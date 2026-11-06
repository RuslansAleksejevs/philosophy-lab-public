"""Synthetic launchd preparation/control tests; launchctl is always mocked."""
import contextlib
import io
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import collector_service as module
from research_archive import ArchiveError


class CollectorServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-collector-service-")
        self.base = Path(self.temp.name).resolve()
        # Spaces and shell metacharacters must remain literal argv components.
        self.root = self.base / "Synthetic Lab $VARIABLE; literal"
        self.home = self.base / "Synthetic Home"
        (self.root / "collector").mkdir(parents=True)
        (self.root / "scripts").mkdir()
        self.home.mkdir()
        self.staged = self.root / "collector" / (module.LABEL + ".plist")
        self.target = self.home / "Library/LaunchAgents" / (module.LABEL + ".plist")
        self.domain = "gui/501"
        self.service = self.domain + "/" + module.LABEL
        self.patches = contextlib.ExitStack()
        self.patches.enter_context(mock.patch.object(module, "__file__", str(self.root / "scripts/collector_service.py")))
        self.patches.enter_context(mock.patch.object(module.Path, "home", return_value=self.home))
        self.patches.enter_context(mock.patch.object(module.os, "getuid", return_value=501))
        self.patches.enter_context(mock.patch.object(module.os, "umask", return_value=0o022))
        self.run = self.patches.enter_context(mock.patch.object(module.subprocess, "run"))
        self.run.return_value = subprocess.CompletedProcess([], 0)

    def tearDown(self):
        self.patches.close()
        self.temp.cleanup()

    def invoke(self, command):
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["collector_service.py", command]), contextlib.redirect_stdout(output):
            result = module.main()
        return result, output.getvalue()

    def expected(self):
        return plistlib.dumps(module.plist(self.root), sort_keys=True)

    def install_fixture(self):
        self.target.parent.mkdir(parents=True, exist_ok=True)
        self.target.write_bytes(self.expected())

    def assert_commands(self, expected):
        self.assertEqual([call.args[0] for call in self.run.call_args_list], expected)
        for call in self.run.call_args_list:
            self.assertFalse(call.kwargs.get("shell", False))

    def test_plist_is_stable_and_uses_literal_arguments_without_shell_environment(self):
        value = module.plist(self.root)
        self.assertEqual(value, module.plist(self.root))
        self.assertEqual(value["Label"], module.LABEL)
        self.assertEqual(value["ProgramArguments"][1:],
                         ["-B", str(self.root / "scripts/collector.py"), "--root", str(self.root), "watch"])
        self.assertTrue(Path(value["ProgramArguments"][0]).is_absolute())
        self.assertEqual(value["WorkingDirectory"], str(self.root))
        self.assertNotIn("EnvironmentVariables", value)
        self.assertNotIn("Program", value)
        self.assertTrue(value["RunAtLoad"])
        self.assertTrue(value["KeepAlive"])
        self.assertEqual(value["ThrottleInterval"], 30)
        self.assertEqual(value["Umask"], 0o077)
        self.assertEqual(value["StandardErrorPath"], str(self.root / "collector/runtime/service-error.log"))
        self.run.assert_not_called()

    def test_interpreter_falls_back_to_current_python_as_one_argument(self):
        synthetic_python = str(self.base / "Python With Spaces/bin/python3")
        with mock.patch.object(module.Path, "is_file", return_value=False), \
                mock.patch.object(module.sys, "executable", synthetic_python):
            self.assertEqual(module.plist(self.root)["ProgramArguments"][0], synthetic_python)

    def test_prepare_writes_exact_private_plist_without_installing(self):
        result, output = self.invoke("prepare")
        self.assertEqual(result, 0)
        self.assertEqual(self.staged.read_bytes(), self.expected())
        self.assertEqual(self.staged.stat().st_mode & 0o777, 0o600)
        self.assertIn(str(self.staged), output)
        self.assertFalse(self.target.exists())
        self.run.assert_not_called()

    def test_install_rejects_changed_staged_configuration_before_any_launchctl(self):
        self.staged.write_bytes(b"synthetic differing staged configuration")
        with self.assertRaisesRegex(ValueError, "staged"):
            self.invoke("install")
        self.assertFalse(self.target.exists())
        self.run.assert_not_called()

    def test_install_preserves_differing_existing_configuration(self):
        self.invoke("prepare")
        self.target.parent.mkdir(parents=True)
        self.target.write_bytes(b"synthetic preexisting other service")
        with self.assertRaisesRegex(ValueError, "existing launch agent differs"):
            self.invoke("install")
        self.assertEqual(self.target.read_bytes(), b"synthetic preexisting other service")
        self.run.assert_not_called()

    def test_install_rejects_symlink_target_without_touching_destination(self):
        self.invoke("prepare")
        self.target.parent.mkdir(parents=True)
        destination = self.base / "synthetic symlink destination"
        destination.write_bytes(self.expected())
        self.target.symlink_to(destination)
        with self.assertRaises(ArchiveError):
            self.invoke("install")
        self.assertEqual(destination.read_bytes(), self.expected())
        self.run.assert_not_called()

    def test_install_writes_exact_config_and_bootstraps_unloaded_service(self):
        self.invoke("prepare")
        self.run.side_effect = [subprocess.CompletedProcess([], 113), subprocess.CompletedProcess([], 0)]
        result, _ = self.invoke("install")
        self.assertEqual(result, 0)
        self.assertEqual(self.target.read_bytes(), self.expected())
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)
        self.assert_commands([["/bin/launchctl", "print", self.service],
                              ["/bin/launchctl", "bootstrap", self.domain, str(self.target)]])
        self.assertTrue(self.run.call_args_list[-1].kwargs["check"])

    def test_install_loaded_exact_service_is_idempotent(self):
        self.invoke("prepare")
        self.install_fixture()
        original = self.target.read_bytes(), self.target.stat().st_mtime_ns
        result, _ = self.invoke("install")
        self.assertEqual(result, 0)
        self.assertEqual((self.target.read_bytes(), self.target.stat().st_mtime_ns), original)
        self.assert_commands([["/bin/launchctl", "print", self.service]])

    def test_start_missing_or_changed_installation_refuses_launch(self):
        with self.assertRaisesRegex(ValueError, "install exact"):
            self.invoke("start")
        self.install_fixture()
        self.target.write_bytes(b"synthetic changed configuration")
        with self.assertRaisesRegex(ValueError, "install exact"):
            self.invoke("start")
        self.run.assert_not_called()

    def test_stop_then_start_bootstraps_before_kickstart(self):
        self.install_fixture()
        original = self.target.read_bytes()
        self.assertEqual(self.invoke("stop")[0], 0)
        self.assertEqual(self.target.read_bytes(), original)
        status = json.loads((self.root / "collector/runtime/status.json").read_text())
        self.assertEqual(status["status"], "STOPPED")
        self.assertIn("checked_at", status)
        self.assert_commands([["/bin/launchctl", "bootout", self.service]])
        self.run.reset_mock()
        self.run.side_effect = [subprocess.CompletedProcess([], 113), subprocess.CompletedProcess([], 0),
                                subprocess.CompletedProcess([], 0)]
        self.assertEqual(self.invoke("start")[0], 0)
        self.assert_commands([["/bin/launchctl", "print", self.service],
                              ["/bin/launchctl", "bootstrap", self.domain, str(self.target)],
                              ["/bin/launchctl", "kickstart", self.service]])
        self.assertTrue(all(call.kwargs["check"] for call in self.run.call_args_list[1:]))

    def test_start_loaded_service_kickstarts_without_bootstrap(self):
        self.install_fixture()
        self.assertEqual(self.invoke("start")[0], 0)
        self.assert_commands([["/bin/launchctl", "print", self.service],
                              ["/bin/launchctl", "kickstart", self.service]])

    def test_failed_bootstrap_propagates_failure_and_never_kickstarts(self):
        self.install_fixture()
        failure = subprocess.CalledProcessError(5, ["/bin/launchctl", "bootstrap"])
        self.run.side_effect = [subprocess.CompletedProcess([], 113), failure]
        with self.assertRaises(subprocess.CalledProcessError):
            self.invoke("start")
        self.assertEqual(len(self.run.call_args_list), 2)

    def test_failed_stop_does_not_falsely_write_stopped_status(self):
        runtime = self.root / "collector/runtime"
        runtime.mkdir()
        status = runtime / "status.json"
        original = b'{"status":"RUNNING"}\n'
        status.write_bytes(original)
        self.run.side_effect = subprocess.CalledProcessError(5, ["/bin/launchctl", "bootout"])
        with self.assertRaises(subprocess.CalledProcessError):
            self.invoke("stop")
        self.assertEqual(status.read_bytes(), original)

    def test_status_reports_loaded_and_unloaded_without_mutation(self):
        import collector
        with mock.patch.object(collector, "status", return_value={"status": "RUNNING", "fresh": True, "sessions": []}):
            code, output = self.invoke("status")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output)["healthy"], True)
            self.run.return_value = subprocess.CompletedProcess([], 113)
            code, output = self.invoke("status")
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(output)["loaded"], False)
            self.assertEqual(json.loads(output)["healthy"], False)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.staged.exists())
        self.assertTrue(all(call.args[0][1] == "print" for call in self.run.call_args_list))

    def test_loaded_service_with_stale_or_missing_collector_state_is_not_healthy(self):
        import collector
        with mock.patch.object(collector, "status", return_value={"status": "STALE", "fresh": False}):
            code, output = self.invoke("status")
            self.assertEqual(code, 1)
            self.assertTrue(json.loads(output)["loaded"])
            self.assertFalse(json.loads(output)["healthy"])
        code, output = self.invoke("status")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["collector"]["status"], "UNKNOWN")

    def test_running_service_with_coverage_gaps_is_not_reported_fully_healthy(self):
        import collector
        report={'status':'RUNNING','fresh':True,'sessions':[{'session_id':'synthetic',
                'gaps':[{'source_line':2,'reason':'unknown_payload_fields','surface':'tools'}]}]}
        with mock.patch.object(collector,'status',return_value=report):
            code,output=self.invoke('status');result=json.loads(output)
        self.assertEqual(code,1)
        self.assertTrue(result['service_healthy'])
        self.assertFalse(result['coverage_healthy'])
        self.assertFalse(result['healthy'])

    def test_report_without_session_inventory_has_unknown_coverage(self):
        import collector
        for status in ('ERROR','RUNNING'):
            report={'status':status,'fresh':True,'error':'Synthetic missing inventory'}
            with mock.patch.object(collector,'status',return_value=report):
                code,output=self.invoke('status');result=json.loads(output)
            self.assertEqual(code,1)
            self.assertIsNone(result['coverage_healthy'])
            self.assertFalse(result['healthy'])
        report=collector.add_coverage_status({'status':'ERROR'})
        self.assertIsNone(report['coverage_summary']['unresolved_gap_count'])
        self.assertIsNone(report['coverage_summary']['pending_tool_records'])
        self.assertTrue(collector.coverage_summary([])['coverage_healthy'])


if __name__ == "__main__":
    unittest.main()
