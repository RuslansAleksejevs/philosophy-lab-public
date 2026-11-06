"""Synthetic panel provenance tests; no manuscript or real transcript is read."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import judges20_panel as panel
from research_archive import Archive, ArchiveError, canonical, sha


class PanelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='synthetic-panel-')
        self.root = Path(self.tmp.name).resolve()
        self.archive = Archive(self.root / 'research/archive')
        self.archive.init()
        self.write('LAB_PROFILE.json', '{"lab":{"kind":"PHILOSOPHY_PROGRAM"}}')
        self.write('methods/synthetic.json', json.dumps({'id':'synthetic', 'stages':panel.rounds.STAGES}))
        for name in ('AGENTS.md','AGENT_POLICY.md','USER_PREFERENCES.md','workflows/ROUND.md',
                     '.codex/config.toml','input.txt'):
            self.write(name, 'Synthetic neutral fixture')
        self.write('.lab/philosophy.json', json.dumps({'schema_version':1,'kernel':'philosophy.v1',
                                                      'archive_format':'research-archive.v1'}))
        self.write('research/judges/20260912/registry.json', json.dumps({'judges':[{'judge_id':'synthetic'}]}))
        with self.archive.writer() as w:
            self.start = panel.rounds.start(self.root,w,panel.RUN,'synthetic-coordinator','research',
                                           'methods/synthetic.json',['input.txt'],selection_round_id='JUDGES20_PANEL')
            files=[]
            for name in ('A.md','B.md','C.md','profile.md','task.txt','rules.md'):
                body=('Synthetic '+name+'\n').encode()
                self.write(panel.BASE/'synthetic'/name, body.decode())
                files.append({'path':name,'sha256':w.put(body)})
            manifest={'run_id':panel.RUN,'judge_id':'synthetic','display_order':['A','B','C'],'files':files}
            data=canonical(manifest)
            self.write(panel.BASE/'synthetic'/'packet.json',data.decode())
            event=panel.rounds.envelope(self.start,'round.panel_packet',payload={'judge_id':'synthetic','manifest_sha256':sha(data)})
            event['outputs']=[w.put(data)]+[f['sha256'] for f in files]
            self.prepared=w.append(event,'synthetic-packet')
        self.source=self.root/'synthetic-native.jsonl'
        self.identity={'session_id':'synthetic-panelist','source_path':str(self.source),
                       'source_cwd':str(self.root),'agent_path':'/root/panel_synthetic'}

    def tearDown(self):
        self.tmp.cleanup()

    def write(self,path,body):
        dest=self.root/path; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(body)
        return dest

    def marker(self,stage,digest):
        meta={'type':'session_meta','payload':{'id':self.identity['session_id'],'cwd':str(self.root)}}
        message={'type':'response_item','timestamp':'2026-09-12T00:00:00Z','payload':{
            'type':'message','role':'assistant','phase':'commentary','content':[{'type':'output_text',
            'text':f'[JUDGES20:panel-synthetic:{stage} sha256={digest}]'}]}}
        if not self.source.exists():
            self.source.write_text(json.dumps(meta)+'\n')
        with self.source.open('a') as stream: stream.write(json.dumps(message)+'\n')

    def invoke(self,command,file):
        args=argparse.Namespace(command=command,judge='synthetic',agent_path='/root/panel_synthetic',file=file)
        with patch.object(panel.essay_tools,'discover',return_value=self.identity):
            with self.archive.writer() as writer:
                return panel.process(self.root,args,writer)

    def review(self):
        body=b'Synthetic independent review; A and B tied, C unresolved.\n'
        self.write(panel.BASE/'synthetic'/'review.md',body.decode())
        self.marker('review',sha(body))
        return self.invoke('review','review.md')

    def test_sealed_review_exact_capture_and_retry_then_input_drift(self):
        first=self.review()
        self.assertEqual(first,self.invoke('review','review.md'))
        events={e['id']:e for e in self.archive.events()}
        event=events[first['review_event_id']]
        self.assertIn(self.prepared['id'],event['parents'])
        self.assertEqual(events[event['payload']['coverage_event_id']]['payload']['status'],'BOUNDED_COMPLETE')
        self.assertTrue(event['payload']['raw_event_ids'])
        self.assertTrue(self.archive.validate()['ok'])
        self.write(panel.BASE/'synthetic'/'A.md','Changed manuscript')
        with self.assertRaisesRegex(ArchiveError,'input bytes changed'):
            self.invoke('review','review.md')

    def test_missing_marker_and_coordinator_session_are_rejected(self):
        self.write(panel.BASE/'synthetic'/'review.md','Synthetic unattested text')
        self.marker('review','a'*64)
        with self.assertRaisesRegex(ArchiveError,'visible commentary marker'):
            self.invoke('review','review.md')
        self.identity['session_id']='synthetic-coordinator'
        with self.assertRaisesRegex(ArchiveError,'fresh non-author session'):
            self.invoke('review','review.md')

    def test_sources_are_archived_before_review_and_cross_packet_paths_fail(self):
        self.write(panel.BASE/'synthetic'/'sources'/'excerpt.txt','Synthetic primary-source excerpt')
        data=canonical([{'path':'sources/excerpt.txt','url':'https://example.invalid/fixture',
                         'read_status':'excerpt','title':'Synthetic evidence','locators':'Fixture only'}])
        self.write(panel.BASE/'synthetic'/'extra.json',data.decode())
        self.marker('sources_extra',sha(data))
        source=self.invoke('sources-extra','extra.json')
        review=self.review()
        event=next(e for e in self.archive.events() if e['id']==review['review_event_id'])
        self.assertIn(source['source_event_id'],event['parents'])
        with self.assertRaisesRegex(ArchiveError,'review is sealed'):
            self.invoke('sources-extra','extra.json')
        for path in ('../another/review.md','/tmp/escape','../../essay-51/final.md'):
            with self.assertRaises(ArchiveError): panel.own(self.root,'synthetic',path)


if __name__=='__main__': unittest.main()
