import contextlib
import io
import signal
from unittest.mock import patch
from test_claude_runner import FileRunnerTests
import claude_runner as r
import claude_runner_support as s


class RepairTests(FileRunnerTests):
    def test_output_correction_resumes_same_session_and_advances_queue(self):
        self.make(('normal', 'dependency'))
        original = s.validate
        calls = []
        def validate(*args):
            result = original(*args)
            calls.append(args[2]['id'])
            if len(calls) == 1:
                result.update(passed=False, errors=['word_limit:result.txt'])
            return result
        with patch.object(s, 'validate', side_effect=validate):
            self.assertEqual(self.run_fake()['status'], 'done')
        self.assertEqual(calls, ['task-0', 'task-0', 'task-1'])
        records = [r.load(p) for p in (self.packet/'records').glob('*.json')]
        attempts = [x for x in records if x['kind']=='attempt.started' and x['task']=='task-0']
        self.assertEqual(len(attempts), 2)
        self.assertEqual(len({x['session_id'] for x in attempts}), 1)
        correction = next(x for x in attempts if 'OUTPUT CORRECTION REQUIRED' in x['prompt'])
        self.assertIn('--resume', correction['cli_flags'])
        self.assertIn('word_limit:result.txt', correction['prompt'])

    def test_persistent_repair_budget_and_no_mixed_failure_retry(self):
        self.make()
        with patch.object(s, 'validate', return_value={'passed':False, 'errors':['word_limit:result.txt'], 'checks':{}}):
            self.assertEqual(self.run_fake()['status'], 'paused')
            self.assertEqual(r.load(self.packet/'state.json')['task-0']['output_repair_attempts'], 3)
            self.run_fake()
            records = [r.load(p) for p in (self.packet/'records').glob('*.json')]
            self.assertEqual(sum(x['kind']=='attempt.started' for x in records), 4)
        state = r.load(self.packet/'state.json')['task-0']
        state['validation_errors'] = ['word_limit:result.txt', 'source_changed:receipt.json']
        state['output_repair_attempts'] = 0
        with patch.object(r, 'execute') as execute:
            s.execute_with_repairs(r, execute, self.packet, {'id':'task-0'}, state, self.packet/'work/task-0', str(self.fake))
            execute.assert_not_called()

    def test_quota_during_correction_is_not_retried(self):
        self.make()
        self.run_fake()
        state = r.load(self.packet/'state.json')['task-0']
        state.update(status='paused', reason='validation_failed', validation_errors=['word_limit:result.txt'])
        def quota(*args):
            args[2].update(status='paused', reason='quota')
            return args[2]
        with patch.object(r, 'execute', side_effect=quota) as execute:
            result = s.execute_with_repairs(r, execute, self.packet, {'id':'task-0'}, state, self.packet/'work/task-0', str(self.fake))
            self.assertEqual(result['reason'], 'quota')
            self.assertEqual(execute.call_count, 1)

    def test_stop_before_correction_prevents_dispatch(self):
        self.make()
        self.run_fake()
        state = r.load(self.packet/'state.json')['task-0']
        state.update(status='paused', reason='validation_failed', validation_errors=['word_limit:result.txt'])
        r.atomic(self.packet/'STOP.json', b'{}')
        with patch.object(r, 'execute') as execute:
            s.execute_with_repairs(r, execute, self.packet, {'id':'task-0'}, state, self.packet/'work/task-0', str(self.fake))
            execute.assert_not_called()

    def test_manual_quota_resume_repeats_correction_without_spending_budget(self):
        self.make()
        self.run_fake()
        state = r.load(self.packet/'state.json')['task-0']
        state.update(status='paused', reason='quota', output_repair_attempts=3,
                     validation_errors=['word_limit:result.txt'])
        def success(*args):
            self.assertIn('OUTPUT CORRECTION REQUIRED', r.POLICY)
            self.assertIn('word_limit:result.txt', r.POLICY)
            args[2].update(status='done', reason='accepted_files')
            return args[2]
        with patch.object(r, 'execute', side_effect=success) as execute:
            result = s.execute_with_repairs(r, execute, self.packet, {'id':'task-0'}, state, self.packet/'work/task-0', str(self.fake))
            self.assertEqual(result['output_repair_attempts'], 3)
            self.assertEqual(execute.call_count, 1)

    def test_stop_between_stages_prevents_next_spawn(self):
        self.make(('normal','dependency'))
        original=r.execute
        def execute(*args):
            result=original(*args)
            signal.raise_signal(signal.SIGINT)
            return result
        with patch.object(r,'execute',side_effect=execute):
            self.assertEqual(self.run_fake()['reason'],'batch_stop_latched')
        self.assertFalse((self.packet/'work/task-1').exists())

    def test_source_raw_bytes_survive_extraction_failure_and_relay(self):
        self.make(('normal','dependency'))
        self.run_fake()
        with patch.object(s.sources,'fetch',return_value=(b'%PDF-test','application/pdf',None,{'http_status':200})),patch.object(s.sources,'extract',side_effect=ValueError()):
            s.source_capture(r,self.packet,'task-0','https://example.com/a.pdf')
        r.atomic(self.packet/'work/task-0/output/source-notes/excerpt.md',b'an excerpt')
        r.atomic(self.packet/'work/task-0/output/source-status.json',b'{"sources":[]}')
        outputs=r.snapshot(self.packet,'task-0');states=r.load(self.packet/'state.json');states['task-0']['outputs']=outputs
        task={'id':'new-task','source_dependencies':['task-0']}
        (self.packet/'inputs/new-task').mkdir();r.atomic(self.packet/'inputs/new-task/task.md',b'test')
        work=r.stage(self.packet,task,states)
        files=list((work/'input/source-archives/task-0/sources').glob('*.pdf'))
        self.assertEqual(len(files),1);self.assertEqual(files[0].read_bytes(),b'%PDF-test')
        self.assertEqual((work/'input/source-archives/task-0/source-notes/excerpt.md').read_bytes(),b'an excerpt')
        self.assertTrue((work/'input/source-archives/task-0/source-status.json').exists())
        self.assertTrue(any('source-archives' in n for n in r.load(work/'input/FILES.json')['sources']))

    def test_path_allowed_secret_rejected(self):
        self.assertFalse(s.relay_screen(b'/Users/example/.claude/projects/test/file.pdf','report.md'))
        self.assertTrue(s.relay_screen(b'-----BEGIN PRIVATE KEY-----','report.md'))

    def test_manuscript_limit_and_invalid_source_record_rejected(self):
        self.make();self.run_fake();out=self.packet/'work/task-0/output'
        (out/'final.md').write_text('word '*6001+'\n# Bibliography\nreference')
        task={'id':'task-0','required_outputs':['result.txt'],'manuscripts':['final.md'],'research_checks':True,'model':'fixture','effort':'low'}
        result=s.validate(r,self.packet,task,{}, {'observations':[{'model':'fixture','effort':'low'}]})
        self.assertIn('word_limit:final.md',result['errors']);self.assertIn('source_status_missing_or_invalid',result['errors'])

    def test_configuration_mismatch_blocks_research(self):
        self.make();self.run_fake()
        task={'id':'task-0','required_outputs':['result.txt'],'research_checks':True,'model':'opus','effort':'xhigh'}
        result=s.validate(r,self.packet,task,{}, {'observations':[{'model':'sonnet','effort':'low'}]})
        self.assertIn('native_configuration_unverified_or_changed',result['errors'])

    def test_support_tampering_blocks_run(self):
        self.make();(self.packet/'claude_runner_support.py').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Support code differs'):self.run_fake()

    def test_usage_is_retained_without_thinking(self):
        result=r.visible({'type':'result','subtype':'success','usage':{'input_tokens':12,'output_tokens':3},'total_cost_usd':.03,'thinking':'hidden'})
        self.assertEqual(result['usage']['input_tokens'],12);self.assertNotIn('thinking',result)
