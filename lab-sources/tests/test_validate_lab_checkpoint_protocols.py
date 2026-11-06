"""Keep the lab validator compatible with bound checkpoint protocols."""
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate_lab


class CheckpointProtocolTests(unittest.TestCase):
    def test_accepts_known_philosophy_and_hundred_checkpoint_headers(self):
        for protocol in (
            'philosophy-checkpoint.v1',
            'hundred-artifacts.v1',
            'hundred-artifacts.v2',
            'hundred-checkpoint-alias.v3',
        ):
            with self.subTest(protocol=protocol):
                self.assertTrue(validate_lab.valid_checkpoint_header({
                    'protocol': protocol,
                    'research_date': '2026-09-28',
                }))

    def test_rejects_unknown_protocol_and_malformed_date(self):
        self.assertFalse(validate_lab.valid_checkpoint_header({
            'protocol': 'unreviewed-checkpoint.v99',
            'research_date': '2026-09-28',
        }))
        self.assertFalse(validate_lab.valid_checkpoint_header({
            'protocol': 'hundred-checkpoint-alias.v3',
            'research_date': '2026-9-28',
        }))
        self.assertFalse(validate_lab.valid_checkpoint_header(None))


if __name__ == '__main__':
    unittest.main()
