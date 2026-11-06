"""Synthetic bounded service-error logs; canonical research files stay untouched."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import collector
from research_archive import ArchiveError


class CollectorOperationalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-collector-operations-")
        self.root = Path(self.temp.name).resolve()
        self.runtime = self.root / "collector/runtime"
        self.runtime.mkdir(parents=True)
        self.log = self.runtime / "operational.log"
        self.older = self.runtime / "operational.log.1"

    def tearDown(self):
        self.temp.cleanup()

    def test_error_has_timestamp_and_bounded_message_length(self):
        with mock.patch.object(collector, "now", return_value="2026-09-08T00:00:00Z"):
            collector.log_error(self.root, "synthetic error " + "x" * 10000)
        self.assertEqual(self.log.read_text(), "2026-09-08T00:00:00Z " + ("synthetic error " + "x" * 10000)[:2000] + "\n")

    def test_rotation_preserves_one_previous_segment_and_does_not_touch_archive(self):
        canonical = self.root / "research/archive/objects/synthetic-canary"
        canonical.parent.mkdir(parents=True)
        canonical.write_bytes(b"synthetic canonical bytes never rotate")
        first = b"a" * (256 * 1024)
        self.log.write_bytes(first)
        self.older.write_bytes(b"synthetic older operational segment")
        collector.log_error(self.root, "synthetic first rotation")
        self.assertEqual(self.older.read_bytes(), first)
        self.assertIn("synthetic first rotation", self.log.read_text())
        second = b"b" * (256 * 1024)
        self.log.write_bytes(second)
        collector.log_error(self.root, "synthetic second rotation")
        self.assertEqual(self.older.read_bytes(), second)
        self.assertIn("synthetic second rotation", self.log.read_text())
        self.assertEqual({p.name for p in self.runtime.iterdir()}, {"operational.log", "operational.log.1"})
        self.assertEqual(canonical.read_bytes(), b"synthetic canonical bytes never rotate")

    def test_repeated_errors_remain_bounded_in_two_files(self):
        for number in range(300):
            collector.log_error(self.root, "synthetic %d " % number + "x" * 3000)
        paths = list(self.runtime.iterdir())
        self.assertEqual({p.name for p in paths}, {"operational.log", "operational.log.1"})
        # Rotation happens before the next append; allow one bounded ASCII entry
        # beyond the threshold in either operational segment.
        self.assertTrue(all(p.stat().st_size <= 256 * 1024 + 2100 for p in paths))

    def test_symlink_log_cannot_redirect_operational_writes(self):
        target = self.root / "synthetic untouched target"
        target.write_bytes(b"synthetic untouched")
        self.log.symlink_to(target)
        with self.assertRaises(ArchiveError):
            collector.log_error(self.root, "synthetic blocked write")
        self.assertEqual(target.read_bytes(), b"synthetic untouched")


if __name__ == "__main__":
    unittest.main()
