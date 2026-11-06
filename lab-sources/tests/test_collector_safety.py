import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collector_safety import contains_credential, redact_value
from test_collector import CollectorTests, message
from collector import Collector


class CredentialProjectionTests(unittest.TestCase):
    def test_nested_json_quoted_secret(self):
        value={'arguments':json.dumps({'cmd':'password = "'+('x'*32)+'"'})}
        self.assertTrue(contains_credential(value))
        self.assertNotIn('x'*32,str(redact_value(value)))
        for value in ({'output':json.dumps({'password':'x'*32})},{'password':'x'*32}):
            self.assertTrue(contains_credential(value))
            self.assertNotIn('x'*32,str(redact_value(value)))

    def test_pem_and_token_patterns(self):
        for text in ('sk-'+('x'*32),'ghp_'+('x'*36),'-----BEGIN PRIVATE KEY-----\nsynthetic\n-----END PRIVATE KEY-----'):
            self.assertTrue(contains_credential({'text':text}))
            self.assertNotIn(text,str(redact_value({'text':text})))

    def test_ordinary_text_unchanged(self):
        text={'text':'A philosophical argument about private knowledge. API_KEY is unspecified.'}
        self.assertFalse(contains_credential(text)); self.assertEqual(redact_value(text),text)


class CredentialCollectorTests(CollectorTests):
    # Inherit fixtures but run only this subclass's extra cases (loader below).
    def test_credential_prompt_projected_without_original(self):
        secret='x'*32
        self.source.write_bytes(self.source.read_bytes()+message('user','password = "'+secret+'"'))
        report=Collector(self.root).collect()
        events=self.archive.events()
        selected=[e for e in events if e['kind']=='collector.message']
        self.assertEqual(len(selected),1)
        self.assertNotIn(secret,selected[0]['payload']['text'])
        self.assertFalse(any(e['kind']=='capture.raw_record' for e in events))
        self.assertEqual(report['sessions'][0]['coverage'],'GAPS')
        for path in (self.archive.root/'objects').iterdir(): self.assertNotIn(secret.encode(),path.read_bytes())


def load_tests(loader,tests,pattern):
    suite=loader.loadTestsFromTestCase(CredentialProjectionTests)
    suite.addTest(CredentialCollectorTests('test_credential_prompt_projected_without_original'))
    return suite
