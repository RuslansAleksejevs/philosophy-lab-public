import json
import sqlite3
import contextlib
from unittest import mock, TestSuite
from test_collector import CollectorTests, Collector, SESSION, message
from test_collector_views import CollectorViewTests, refresh
import collector as module


class InternalCollectorTests(CollectorTests):
    def test_internal_source_never_opened_and_prior_record_corrected(self):
        self.add_bytes(message('assistant','Synthetic visible result','final'))
        collector=Collector(self.root); collector.collect()
        before=self.events('capture.raw_record')
        with contextlib.closing(sqlite3.connect(self.db)) as db:
            db.execute('UPDATE threads SET source=? WHERE id=?',(json.dumps({'subagent':{'other':'guardian'}}),SESSION))
            db.commit()
        with mock.patch.object(module,'regular_file',side_effect=AssertionError('internal body opened')):
            result=collector.collect()
        self.assertEqual(result['chat_sessions'],0)
        self.assertEqual(result['internal_excluded_sessions'],1)
        self.assertEqual(result['sessions'][0]['status'],'EXCLUDED')
        self.assertEqual(self.events('capture.raw_record'),before)
        self.assertEqual(self.events('collector.session_excluded')[0]['payload']['prior_raw_records_count'],1)


class InternalViewTests(CollectorViewTests):
    def test_internal_corrected_identity_suppresses_body_without_reading_it(self):
        self.message('assistant','Synthetic internal final',2,phase='final')
        self.append('capture.session_identified',{'session_kind':'internal_runtime',
                    'collection_policy':'EXCLUDED_INTERNAL_RUNTIME','native_source_subtype':'guardian'})
        events=self.archive.events()
        with mock.patch.object(self.archive,'get',side_effect=AssertionError('internal body opened')):
            result=refresh(self.root,self.archive,events=events)
        self.assertEqual(result['session_count'],0)
        self.assertEqual(result['internal_excluded_session_count'],1)
        self.assertEqual(self.load('conversation.json')['status'],'EXCLUDED_INTERNAL_RUNTIME')


def load_tests(loader,tests,pattern):
    return TestSuite([InternalCollectorTests('test_internal_source_never_opened_and_prior_record_corrected'),
                      InternalViewTests('test_internal_corrected_identity_suppresses_body_without_reading_it')])
