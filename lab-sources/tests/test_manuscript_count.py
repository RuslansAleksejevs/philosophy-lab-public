import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from manuscript_count import count

class CountTests(unittest.TestCase):
    def test_boundary_title_notes_and_punctuation(self):
        r=count('# Title\n\nwell-defended claim — yes\n\n## Notes\nA note.\n\n## Bibliography\nExcluded entry')
        self.assertEqual(r['word_units'],7)
        self.assertTrue(r['bibliography_heading_found'])
    def test_ceiling_and_missing_or_ambiguous_boundary(self):
        self.assertEqual(count('word '*6001)['length_status'],'REQUIRES_SHORTENING')
        self.assertEqual(count('word '*6000)['length_status'],'WITHIN_LOCAL_COUNT')
        self.assertFalse(count('plain')['bibliography_heading_found'])
        with self.assertRaises(ValueError):count('## References\na\n## Bibliography\nb')
