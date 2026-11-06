"""Isolated search checks; no live provider, collector or research files."""
from pathlib import Path
import gzip
import io
import json
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import search_archive as search


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'docs').mkdir()
        (self.root / 'docs/guide.md').write_text('# Evidence\nA remedy protects later inquiry.\n')
        self.message = {'session': {'session_id': 'sample-session', 'title': 'История'},
                        'messages': [{'source_line': 8, 'role': 'user', 'text': 'Сохраняем возражения и историю.'}]}
        raw = json.dumps(self.message, ensure_ascii=False).encode()
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w') as tar:
            member = tarfile.TarInfo('sessions/example.json'); member.size = len(raw)
            tar.addfile(member, io.BytesIO(raw))
        (self.root / 'messages.tar.gz').write_bytes(gzip.compress(buffer.getvalue()))
        with zipfile.ZipFile(self.root / 'records.zip', 'w') as archive:
            archive.writestr('review.txt', 'A distinctive archive-only objection.')
        self.cache = self.root / '.cache/search.sqlite3'

    def db(self):
        db, rebuilt = search.build_index(self.root, self.cache)
        self.addCleanup(db.close)
        return db, rebuilt

    def test_plain_and_archived_text(self):
        db, _ = self.db()
        self.assertEqual(search.search(db, 'remedy')[0]['location'], 'docs/guide.md')
        self.assertEqual(search.search(db, 'distinctive')[0]['location'], 'records.zip::review.txt')
        result = search.search(db, 'возражения', kind='conversation', full=True)[0]
        self.assertEqual(result['excerpt'], self.message['messages'][0]['text'])
        self.assertTrue(result['location'].endswith('#source-line-8'))

    def test_cache_refreshes_after_change(self):
        db, rebuilt = self.db(); self.assertTrue(rebuilt); db.close()
        db, rebuilt = self.db(); self.assertFalse(rebuilt); db.close()
        (self.root / 'docs/guide.md').write_text('# Evidence\nNewly repaired uncertainty.\n')
        db, rebuilt = self.db(); self.assertTrue(rebuilt)
        self.assertTrue(search.search(db, 'uncertainty'))
        self.assertFalse(search.search(db, 'remedy'))

    def test_literal_query_and_phrase(self):
        db, _ = self.db()
        self.assertEqual(search.search(db, 'remedy OR unknown'), [])
        self.assertTrue(search.search(db, 'later inquiry', phrase=True))
        self.assertFalse(search.search(db, 'inquiry later', phrase=True))
        with self.assertRaises(ValueError): search.search(db, '---')

    def test_failed_rebuild_keeps_previous_index(self):
        db, _ = self.db()
        with patch.object(search, 'documents', side_effect=ValueError('bad archive')):
            with self.assertRaises(ValueError):
                search.build_index(self.root, self.cache, rebuild=True)
        self.assertTrue(search.search(db, 'remedy'))

    def test_safe_archives_and_duplicates(self):
        (self.root / 'duplicate.json').write_text(json.dumps(self.message, ensure_ascii=False))
        with zipfile.ZipFile(self.root / 'untrusted.zip', 'w') as archive:
            archive.writestr('../outside.txt', 'Harmless searchable member.')
        db, _ = self.db()
        self.assertEqual(len(search.search(db, 'возражения')), 1)
        self.assertTrue(search.search(db, 'Harmless'))
        self.assertFalse((self.root.parent / 'outside.txt').exists())

    def test_essay_filter_and_readable_copy_preference(self):
        d = self.root / 'essays/final-20261101'; d.mkdir(parents=True)
        (d / 'E012.md').write_text('A distinctive archive-only objection.')
        db, _ = self.db()
        row = search.search(db, 'distinctive', essay='E012', kind='essay')[0]
        self.assertEqual(row['location'], 'essays/final-20261101/E012.md')
        self.assertFalse(search.search(db, 'distinctive', essay='E050'))


if __name__ == '__main__':
    unittest.main()
