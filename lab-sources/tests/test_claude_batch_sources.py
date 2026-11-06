"""Mechanical source capture: no live network calls in the suite."""
import importlib.util
import json
from pathlib import Path
import types
import unittest
from unittest.mock import patch
from test_claude_batch import ROOT,request
import test_claude_batch_text as text_fixture
import claude_batch

spec=importlib.util.spec_from_file_location('source_capture',ROOT/'templates/philosophy_claude/batch/source_capture.py')
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)

class SourceTests(unittest.TestCase):
    def setUp(self):
        self.fx=text_fixture.TextTransportTests();self.fx.setUp()
        self.fx.b.manifest['source_capture']=True
        self.fx.b.tasks['first']['public_web']=True
        self.fx.b.source_module=types.SimpleNamespace(fetch=lambda url:(b'<p>Whole source &amp; ending.</p>','text/html','utf-8',{'requested_url':url}),extract=source.extract)
        self.fx.spawn()
    def tearDown(self):self.fx.tearDown()
    def fetch(self):
        f=self.fx
        f.call('PreToolUse',agent_id='child',tool_name='WebFetch',tool_use_id='web',tool_input={'url':'https://example.org/source','prompt':'full text'})
        return f.call('PostToolUse',agent_id='child',tool_name='WebFetch',tool_use_id='web',tool_response={'result':'Short provider summary'})
    def test_raw_and_full_text_separately_saved_and_readable(self):
        f=self.fx;r=self.fetch();mapping=f.b.state()['sources']['first']
        raw=next(p for p in mapping if p.endswith('.original.html'));text=next(p for p in mapping if p.endswith('.txt'))
        self.assertEqual((f.base/raw).read_bytes(),b'<p>Whole source &amp; ending.</p>')
        self.assertIn('Whole source & ending.',(f.base/text).read_text())
        self.assertIn(str(f.base/text),r['hookSpecificOutput']['additionalContext'])
        f.b.scoped(str(f.base/text),f.b.tasks['first'],f.b.state())
        with self.assertRaises(ValueError):f.b.scoped(str(f.base/text),f.b.tasks['second'],f.b.state())
        f.finish(f.envelope());f.result()
        f.b.scoped(str(f.base/text),f.b.tasks['second'],f.b.state())
    def test_pdf_extraction_failure_preserves_original(self):
        f=self.fx
        def fail(*args):raise ValueError('No PDF extractor')
        f.b.source_module=types.SimpleNamespace(fetch=lambda url:(b'%PDF-original','application/pdf',None,{'requested_url':url}),extract=fail)
        self.fetch();mapping=f.b.state()['sources']['first']
        self.assertTrue(any(p.endswith('.original.pdf') for p in mapping))
        self.assertFalse(any(p.endswith('.txt') for p in mapping));self.assertFalse(f.b.state().get('halt'))
    def test_plain_text_original_not_overwritten_by_utf8_conversion(self):
        f=self.fx;f.b.source_module.fetch=lambda url:(b'caf\xe9','text/plain','latin-1',{'requested_url':url})
        self.fetch();mapping=f.b.state()['sources']['first']
        raw=next(p for p in mapping if p.endswith('.original.txt'));text=next(p for p in mapping if p.endswith('.txt') and '.original.' not in p)
        self.assertEqual((f.base/raw).read_bytes(),b'caf\xe9');self.assertEqual((f.base/text).read_text(),'café')
    def test_download_unavailable_does_not_halt_batch(self):
        def fail(url):raise OSError('HTTP 404')
        self.fx.b.source_module.fetch=fail
        r=self.fetch();self.assertIn('unavailable',str(r));self.assertFalse(self.fx.b.state().get('halt'))
    def test_source_tampering_detected(self):
        self.fetch();mapping=self.fx.b.state()['sources']['first'];p=next(iter(mapping))
        (self.fx.base/p).write_text('changed')
        with self.assertRaisesRegex(ValueError,'source changed'):self.fx.b.verify_done(self.fx.b.state())
    def test_compiler_binds_helper_only_when_requested(self):
        q=request();plain=claude_batch.compile_packet(ROOT,q);self.assertFalse(any(p.endswith('source_capture.py') for p in plain))
        q['source_capture']=True;files=claude_batch.compile_packet(ROOT,q)
        manifest=json.loads(files['batches/synthetic-batch/manifest.json'])
        self.assertIn('batches/synthetic-batch/source_capture.py',manifest['controls'])
    def test_local_redirect_target_rejected(self):
        with patch.object(source.socket,'getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaisesRegex(ValueError,'not public'):source.public_url('https://example.org/')
    def test_html_scripts_are_not_source_prose(self):
        text,_,_=source.extract(b'<head><title>T</title></head><p>A &amp; B</p><script>hidden()</script>','text/html')
        self.assertIn(b'A & B',text);self.assertNotIn(b'hidden',text)

class PdfCacheAliasTests(SourceTests):
    def test_identical_provider_pdf_routed_to_owned_original(self):
        f=self.fx
        f.b.source_module.fetch=lambda url:(b'%PDF-owned','application/pdf',None,{'requested_url':url})
        self.fetch();mapping=f.b.state()['sources']['first']
        original=next(p for p in mapping if p.endswith('.original.pdf'))
        cache=f.parent.parent/'parent/tool-results/webfetch-123-abc.pdf';cache.parent.mkdir(parents=True);cache.write_bytes(b'%PDF-owned')
        r=f.call('PreToolUse',agent_id='child',tool_name='Read',tool_use_id='pdf-read',tool_input={'file_path':str(cache),'pages':'1-8'})
        self.assertEqual(r['hookSpecificOutput']['updatedInput'],{'file_path':str(f.base/original),'pages':'1-8'})
        self.assertFalse(f.b.state().get('halt'))
    def test_foreign_pdf_is_not_blessed_by_cache_location(self):
        f=self.fx;self.fetch()
        cache=f.parent.parent/'parent/tool-results/webfetch-123-foreign.pdf';cache.parent.mkdir(parents=True);cache.write_bytes(b'%PDF-not-assigned')
        r=f.call('PreToolUse',agent_id='child',tool_name='Read',tool_use_id='foreign',tool_input={'file_path':str(cache)})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'deny')
