"""Provider isolation regression; synthetic metadata only, no native files."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from collector import codex_raw_index


class ProviderIndexTests(unittest.TestCase):
    def test_other_provider_and_legacy_fragments_cannot_poison_codex_cursor(self):
        codex = {'kind': 'capture.raw_record', 'session_id': 'same-id',
                 'payload': {'format': 'codex-visible-selection.v1', 'source_line': 9}}
        claude = {'kind': 'capture.raw_record', 'session_id': 'same-id',
                  'payload': {'format': 'claude-visible-fragments.v1',
                              'source_line': 9, 'source_fragment': 1}}
        legacy = {'kind': 'capture.raw_record', 'session_id': 'legacy-claude',
                  'payload': {'line': 9, 'ordinal': 0}}
        coverage = {'kind': 'capture.coverage', 'session_id': 'same-id', 'payload': {}}
        self.assertEqual(codex_raw_index([codex, claude, legacy, coverage]),
                         {('same-id', 9): codex})
        self.assertEqual(legacy['payload'], {'line': 9, 'ordinal': 0})

    def test_declared_codex_missing_line_is_not_silently_accepted(self):
        malformed = {'kind': 'capture.raw_record', 'session_id': 'bad-codex',
                     'payload': {'format': 'codex-visible-selection.v1'}}
        with self.assertRaises(KeyError):
            codex_raw_index([malformed])


if __name__ == '__main__':
    unittest.main()
