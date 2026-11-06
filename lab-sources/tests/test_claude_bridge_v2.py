"""Adversarial synthetic workflows; never contacts Claude or edits real projects."""
import copy
import json
from pathlib import Path
from unittest import mock
from test_philosophy_bridge import BridgeFixture
import philosophy_bridge as b
import claude_export as ex
import claude_project as project
import claude_intake as intake
from research_archive import ArchiveError, canonical


class ExportTests(BridgeFixture):
    def setUp(self):
        super().setUp()
        self.write('claude-export-policy.json', {'private_terms': ['Private Person']})

    def review(self, request=None):
        request = request or self.request
        review = b.prepare(self.root, request, preview=True)
        review.update(status='REVIEWED', reviewer='synthetic-reviewer', reviewed_at='2026-09-13T00:00:00Z')
        for v in review['files']:
            v.update(classification='public_source' if v['path'].endswith('.pdf') else 'neutral_instruction',
                     content_and_metadata_reviewed=True, personal_context_absent=True,
                     notes='Synthetic fixture explicitly inspected including metadata; public attribution allowed.')
        self.write('review.json', review)
        return {**request, 'export_review': 'review.json'}

    def test_gate_preview_no_publish_and_stale_policy_and_bytes(self):
        with self.assertRaisesRegex(ArchiveError, 'review required'): b.prepare(self.root, self.request)
        reviewed = self.review()
        self.assertFalse((self.root/'research/bridge/jobs/synthetic-job').exists())
        with self.assertRaisesRegex(ArchiveError, 'changed'):
            b.prepare(self.root, {**reviewed, 'prompt': 'changed'})
        self.write('claude-export-policy.json', {'private_terms': ['Private Person', 'New name']})
        with self.assertRaisesRegex(ArchiveError, 'policy'): b.prepare(self.root, reviewed)

    def test_personal_name_in_filename_copied_notes_and_local_path_blocked(self):
        for source,label,body in [('a.md','notes.md','Private Person said this'),
                                  ('a.md','Private Person.md','neutral'),
                                  ('a.md','notes.md','/Users/private-person/secret'),
                                  ('a.md','notes.md','Bearer abcdefghijklmnopqrstuvwxyz')]:
            with self.subTest(label=label, body=body):
                self.write(source, body)
                req={**self.request, 'selected_inputs':[{'source':source,'label':label}]}
                with self.assertRaisesRegex(ArchiveError,'private context'): b.prepare(self.root,self.review(req))

    def test_binary_unreviewed_and_public_names_and_email(self):
        self.write('paper.pdf',b'%PDF- synthetic public author Public Scientist public@example.org')
        req={**self.request,'selected_inputs':[{'source':'paper.pdf','label':'paper.pdf'}]}
        reviewed=self.review(req);v=json.loads((self.root/'review.json').read_text())
        entry=next(x for x in v['files'] if x['path'].endswith('.pdf'));entry['content_and_metadata_reviewed']=False
        self.write('review.json',v)
        with self.assertRaisesRegex(ArchiveError,'unreviewed'):b.prepare(self.root,reviewed)
        result=b.prepare(self.root,self.review(req));self.assertEqual(result['status'],'PREPARED')
        self.write('claude-export-policy.json',{'private_terms':['Public Scientist']})
        with self.assertRaises(ArchiveError):b.activate(self.root,'synthetic-job',self.workspace)

    def test_omitted_file_duplicate_or_tampered_findings_blocked(self):
        reviewed=self.review();original=json.loads((self.root/'review.json').read_text())
        for mutation in ('omit','duplicate','findings'):
            v=copy.deepcopy(original)
            if mutation=='omit':v['files'].pop()
            elif mutation=='duplicate':v['files'][1]=v['files'][0]
            else:v['files'][0]['findings']=[{'rule':'ignored'}]
            self.write('review.json',v)
            with self.assertRaises(ArchiveError):b.prepare(self.root,reviewed)


class ProjectTests(ExportTests):
    def make_job(self, name='synthetic-job'):
        req={**self.request,'job_id':name,'workspace_layout':'persistent','required_outputs':['report.md'],
             'prompt':'Read input/inputs/data.md. Write output/report.md. Synthetic only.',
             'selected_inputs':[{'source':'data.md','label':'data.md'}]}
        self.write('data.md','Synthetic data')
        return b.prepare(self.root,self.review(req))

    def active(self):
        self.make_job();project.initialize(self.root,self.workspace,'synthetic-run');project.publish(self.root,self.workspace,'synthetic-job')
        b.claim(self.root,self.workspace,'synthetic-session','attempt-1')

    def source(self, body='Synthetic report', session='synthetic-session'):
        out=b.output_directory(self.workspace)/'report.md';out.write_text(body)
        def rec(role,content):return {'type':role,'cwd':str(self.workspace),'sessionId':session,'timestamp':'2026-01-01T12:00:00Z','message':{'role':role,'content':content,**({'model':'synthetic-model'} if role=='assistant' else {})}}
        rows=[rec('user','Synthetic neutral job'),rec('assistant',[{'type':'thinking','thinking':'DO_NOT_COPY_THINKING','signature':'hidden'},
             {'type':'tool_use','id':'call-1','name':'Write','input':{'file_path':str(out),'content':body}}]),
             rec('user',[{'type':'tool_result','tool_use_id':'call-1','content':'File created successfully at: '+str(out)}]),
             rec('assistant',[{'type':'text','text':'Synthetic completed.'}])]
        path=self.root.parent/(session+'.jsonl');path.write_bytes(b''.join(canonical(r) for r in rows));return path

    def ingest(self,source,session='synthetic-session'):
        rev=intake.inspect(source,session,self.workspace,1,4);rev.update(reviewer='synthetic-reviewer',reviewed_at='2026-09-13')
        for r in rev['fragments']:r['reviewed']=True
        return intake.ingest(self.root,self.workspace,source,rev,'complete')

    def test_end_to_end_same_folder_new_session_repeat_intake_and_no_hidden_copy(self):
        self.active();source=self.source();r=self.ingest(source);again=self.ingest(source)
        self.assertEqual(r['status'],'ORIGIN_VERIFIED');self.assertEqual(r['event_id'],again['event_id'])
        closed=project.close(self.root,self.workspace,'synthetic-job',r['collection_id'],source)
        self.assertEqual(closed['event_id'],project.close(self.root,self.workspace,'synthetic-job',r['collection_id'],source)['event_id'])
        self.make_job('second-job');project.publish(self.root,self.workspace,'second-job')
        with self.assertRaisesRegex(ArchiveError,'session reuse'):b.claim(self.root,self.workspace,'synthetic-session','attempt-1')
        b.claim(self.root,self.workspace,'second-session','attempt-1')
        r2=self.ingest(self.source('Second report','second-session'),'second-session');self.assertEqual(r2['status'],'ORIGIN_VERIFIED')
        for obj in (self.root/'research/archive/objects').iterdir():self.assertNotIn(b'DO_NOT_COPY_THINKING',obj.read_bytes())
        self.assertTrue(self.archive.validate()['ok'])

    def test_status_distinguishes_queued_returned_collected_and_later_job(self):
        self.active()
        s=project.status(self.root,self.workspace)
        self.assertEqual(s['output_state'],'NO_OUTPUT_OBSERVED')
        self.assertEqual(s['provider_runtime'],'UNKNOWN')
        source=self.source()
        self.assertEqual(project.status(self.root,self.workspace)['output_state'],'OUTPUT_PRESENT_UNCOLLECTED')
        r=self.ingest(source)
        s=project.status(self.root,self.workspace)
        self.assertEqual(s['output_state'],'ALREADY_COLLECTED')
        self.assertEqual(s['matching_collection_id'],r['collection_id'])
        project.close(self.root,self.workspace,'synthetic-job',r['collection_id'],source)
        self.make_job('second-job');project.publish(self.root,self.workspace,'second-job')
        s=project.status(self.root,self.workspace)
        self.assertEqual(s['output_state'],'NO_OUTPUT_OBSERVED')
        self.assertEqual(s['last_collected']['job_id'],'synthetic-job')
        self.assertNotIn('matching_collection_id',s)

    def test_active_switch_and_second_location_rejected(self):
        self.active();self.make_job('second-job')
        with self.assertRaisesRegex(ArchiveError,'active job'):project.publish(self.root,self.workspace,'second-job')
        other=self.workspace.parent/'other';project.initialize(self.root,other,'synthetic-run')
        with self.assertRaisesRegex(ArchiveError,'already activated'):project.publish(self.root,other,'synthetic-job')
        self.assertEqual(project.publish(self.root,self.workspace,'synthetic-job')['state'],'ACTIVE')

    def test_closing_changed_output_uncaptured_tail_and_stale_job_writes(self):
        self.active();src=self.source();r=self.ingest(src);saved=src.read_bytes();src.write_bytes(saved+b'{}\n')
        with self.assertRaises(ArchiveError):project.close(self.root,self.workspace,'synthetic-job',r['collection_id'],src)
        src.write_bytes(saved);out=b.output_directory(self.workspace)/'report.md';out.write_text('changed')
        with self.assertRaisesRegex(ArchiveError,'output changed'):project.close(self.root,self.workspace,'synthetic-job',r['collection_id'],src)
        out.write_text('Synthetic report');project.close(self.root,self.workspace,'synthetic-job',r['collection_id'],src)
        out.write_text('stale chat write');self.make_job('second-job')
        with self.assertRaisesRegex(ArchiveError,'closed job changed'):project.publish(self.root,self.workspace,'second-job')

    def test_recover_committed_controls_but_not_unknown_drift(self):
        self.make_job();project.initialize(self.root,self.workspace,'synthetic-run')
        real=project.replace_control;counter=[0]
        def crash(path,data):
            counter[0]+=1
            if counter[0]==2:raise OSError('synthetic power loss')
            real(path,data)
        with mock.patch.object(project,'replace_control',side_effect=crash),self.assertRaises(OSError):project.publish(self.root,self.workspace,'synthetic-job')
        with self.assertRaises(ArchiveError):project.status(self.root,self.workspace)
        project.recover(self.root,self.workspace);self.assertEqual(project.status(self.root,self.workspace)['state'],'ACTIVE')
        (self.workspace/'CLAUDE.md').write_text('unknown edit')
        with self.assertRaisesRegex(ArchiveError,'unrecognized'):project.recover(self.root,self.workspace)

    def test_wrong_job_output_never_verified_and_review_required(self):
        self.active();src=self.source();v=intake.inspect(src,'synthetic-session',self.workspace,1,4)
        self.assertNotIn('DO_NOT_COPY_THINKING',str(v))
        with self.assertRaisesRegex(ArchiveError,'review'):intake.ingest(self.root,self.workspace,src,v,'complete')
        for item in v['fragments']:item['reviewed']=True
        v.update(reviewer='test',reviewed_at='today');v['source_snapshot_sha256']='0'*64
        with self.assertRaisesRegex(ArchiveError,'changed'):intake.ingest(self.root,self.workspace,src,v,'complete')
        v=intake.inspect(src,'synthetic-session',self.workspace,1,4)
        for item in v['fragments']:item['reviewed']=True
        v.update(reviewer='test',reviewed_at='today');(b.output_directory(self.workspace)/'report.md').write_text('Unattributed bytes')
        r=intake.ingest(self.root,self.workspace,src,v,'complete');self.assertEqual(r['status'],'ARTIFACT_REVIEW_REQUIRED')

    def test_persistent_input_drift_and_local_override(self):
        self.active();p=self.workspace/'work/synthetic-job/input/prompt.md';old=p.read_bytes();p.chmod(0o644);p.write_text('drift')
        with self.assertRaisesRegex(ArchiveError,'input changed'):b.collect(self.root,self.workspace)
        p.write_bytes(old);(self.workspace/'.claude/settings.local.json').write_text('{"bad":true}')
        with self.assertRaisesRegex(ArchiveError,'override'):project.status(self.root,self.workspace)
