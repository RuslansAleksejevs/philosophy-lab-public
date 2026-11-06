import unittest
import claude_configuration as cfg
from research_archive import canonical,sha

class ConfigurationEvidenceTests(unittest.TestCase):
    def fixture(self):
        native={'agent_id':'child','session_id':'parent','models':[{'model':'claude-opus-5','effort':'xhigh','source_line':7}], 'source_sha256':'native-source'}
        data=canonical(native);ref=sha(data)
        return {'batch_id':'sample','objects':{ref:data},'state':{'parent_session':'parent'},'events':[{'kind':'task.sealed','payload':{'task':'author','native_object':ref}}], 'manifest':{'dispatcher_ui_mode_requested':'Ultracode','tasks':[{'id':'author','essay_id':'essay-01','configuration':{'model':'claude-opus-5','effort':'xhigh','ui_mode':'not_applicable_subagent'}}]}}
    def test_requested_ultracode_and_child_xhigh_do_not_prove_ui_selection(self):
        r=cfg.report(self.fixture())
        self.assertEqual(r['dispatcher_ui_mode_requested'],'Ultracode')
        self.assertEqual(r['dispatcher_ui_mode_observed'],'UNKNOWN_FROM_NATIVE_JOURNAL')
        self.assertEqual(r['workers'][0]['native_observations'][0]['effort'],'xhigh')
        self.assertEqual(r['workers'][0]['ui_mode_observed'],'UNKNOWN')
    def test_no_parent_child_inheritance_or_unlaunched_observations(self):
        x=self.fixture();x['events']=[]
        self.assertEqual(cfg.report(x)['workers'],[])
    def test_modified_evidence_not_accepted(self):
        x=self.fixture();key=next(iter(x['objects']));x['objects'][key]+=b' '
        with self.assertRaisesRegex(ValueError,'hash'):cfg.report(x)
    def test_native_changes_preserved_separately(self):
        x=self.fixture();key=next(iter(x['objects']));import json
        n=json.loads(x['objects'].pop(key));n['models'].append({'model':'claude-opus-5','effort':'max','source_line':8})
        data=canonical(n);x['objects'][sha(data)]=data;x['events'][0]['payload']['native_object']=sha(data)
        self.assertEqual([v['effort'] for v in cfg.report(x)['workers'][0]['native_observations']],['xhigh','max'])

    def test_dated_ui_remains_separate_from_native_effort(self):
        ui={'session_id':'parent','source_kind':'desktop_ui','observed_at':'2026-09-13T20:07:05Z','value':'Ultracode','evidence':'Effort: Ultracode'}
        r=cfg.report(self.fixture(),[ui])
        self.assertEqual(r['separate_ui_observations'],[ui])
        self.assertEqual(r['workers'][0]['native_observations'][0]['effort'],'xhigh')
        ui['session_id']='unrelated'
        self.assertEqual(cfg.report(self.fixture(),[ui])['separate_ui_observations'],[])

    def test_checkpoint_observations_are_not_lost_or_called_complete(self):
        x=self.fixture();x['events'][0]['kind']='task.checkpoint'
        r=cfg.report(x)
        self.assertEqual(r['workers'][0]['stage_outcome'],'task.checkpoint')
        self.assertEqual(r['workers'][0]['native_observations'][0]['effort'],'xhigh')
