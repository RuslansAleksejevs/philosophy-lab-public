import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import hundred_checkpoint_alias_v3 as checkpoint_alias  # noqa: E402
from research_archive import ArchiveError  # noqa: E402


def stage(event_id, name, *, phase, kind="critique", independent=True):
    return {"id": event_id, "payload": {"stage": name, "phase": phase,
                                           "kind": kind, "independent": independent}}


class StageAliasTests(unittest.TestCase):
    def test_exact_name_needs_no_alias(self):
        item = stage("event-1", "critique-001", phase="critique")
        got = checkpoint_alias.resolve_required_stages(["critique-001"], [item], [])
        self.assertEqual(got[0]["resolution"], "exact")
        self.assertEqual(got[0]["event_id"], "event-1")

    def test_documented_critic_name_alias_requires_independent_critique(self):
        item = stage("event-2", "critic-001", phase="critique")
        got = checkpoint_alias.resolve_required_stages(
            ["critique-001"], [item], [checkpoint_alias.ALLOWED_ALIAS])
        self.assertEqual(got[0]["resolution"], "documented-semantic-alias")
        self.assertEqual(got[0]["actual_stage"], "critic-001")

    def test_alias_rejects_wrong_phase_or_nonindependent_stage(self):
        alias = [checkpoint_alias.ALLOWED_ALIAS]
        for item in (stage("event-3", "critic-001", phase="draft"),
                     stage("event-4", "critic-001", phase="critique", independent=False)):
            with self.subTest(item=item), self.assertRaises(ArchiveError):
                checkpoint_alias.resolve_required_stages(["critique-001"], [item], alias)

    def test_alias_rejects_ambiguity_and_unreviewed_aliases(self):
        alias = [checkpoint_alias.ALLOWED_ALIAS]
        items = [stage("event-5", "critic-001", phase="critique"),
                 stage("event-6", "critic-001", phase="critique")]
        with self.assertRaises(ArchiveError):
            checkpoint_alias.resolve_required_stages(["critique-001"], items, alias)
        with self.assertRaises(ArchiveError):
            checkpoint_alias.resolve_required_stages(
                ["critic-002"], [stage("event-7", "critique-002", phase="critique")],
                [{"required_stage": "critic-002", "actual_stage": "critique-002",
                  "phase": "critique", "kind": "critique", "independent": True}])

    def test_all_required_stages_must_resolve(self):
        with self.assertRaises(ArchiveError):
            checkpoint_alias.resolve_required_stages(
                ["sources-001", "critique-001"],
                [stage("event-8", "critic-001", phase="critique")],
                [checkpoint_alias.ALLOWED_ALIAS])


if __name__ == "__main__":
    unittest.main()
