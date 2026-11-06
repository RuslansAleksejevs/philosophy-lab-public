import unittest
import test_claude_gradual as helpers

class QuotaRaceTests(unittest.TestCase):
    setUp=helpers.GradualTests.setUp
    tearDown=helpers.GradualTests.tearDown
    call=helpers.GradualTests.call
    spawn=helpers.GradualTests.spawn
    row=helpers.GradualTests.row
    native=helpers.GradualTests.native
    envelope=helpers.GradualTests.envelope
    finish=helpers.GradualTests.finish
    result=helpers.GradualTests.result

    def limit_result(self):
        return {'status':'completed','agentId':'child','content':[{'type':'text','text':"Agent terminated early due to an API error: You've hit your session limit (error type rate_limit, HTTP 429)"}]}

    def test_agent_success_wrapper_with_api_failure_is_quota(self):
        self.spawn();self.call('PostToolUse',tool_name='Agent',tool_use_id='launch',tool_response=self.limit_result())
        s=self.b.state();self.assertFalse(s.get('halt'));self.assertFalse(s['pending']);self.assertFalse(s['done']);self.assertTrue(s['quota_wait'])
        self.call('StopFailure',error='rate_limit')
        self.call('UserPromptSubmit',prompt='Continue after reset')
        s=self.b.state();self.assertFalse(s.get('quota_wait'));self.assertFalse(s.get('halt'));self.assertEqual(s['checkpoints']['first']['agent_id'],'child')
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child'});self.result('resume','SendMessage');self.finish(self.envelope())
        self.assertIn('first',self.b.state()['done'])

    def test_quota_before_agent_callback_stays_resumable(self):
        self.spawn();self.call('StopFailure',error='rate_limit');self.call('PostToolUse',tool_name='Agent',tool_use_id='launch',tool_response=self.limit_result())
        self.call('UserPromptSubmit',prompt='Continue');self.assertFalse(self.b.state().get('halt'));self.assertIn('first',self.b.state()['checkpoints'])

    def test_legacy_missing_result_halt_then_quota_is_superseded(self):
        self.spawn();self.result();self.assertTrue(self.b.state()['halt'])
        self.call('StopFailure',error='rate_limit');self.assertFalse(self.b.state().get('halt'))
        self.call('UserPromptSubmit',prompt='Continue');self.assertFalse(self.b.state().get('quota_wait'));self.assertIn('first',self.b.state()['checkpoints'])

    def test_existing_double_state_repaired_on_human_prompt(self):
        self.spawn();self.result();s=self.b.state();s['quota_wait']={'evidence':'synthetic','reset_at':'UNKNOWN'};self.b.save(s)
        self.call('UserPromptSubmit',prompt='Continue');self.assertFalse(self.b.state().get('halt'));self.assertFalse(self.b.state().get('quota_wait'))
        self.assertEqual(self.b.state()['checkpoints']['first']['agent_id'],'child')

    def test_integrity_block_not_hidden_or_cleared_by_quota(self):
        self.spawn();s=self.b.state();self.b.halt(s,'sealed output changed','first');self.call('StopFailure',error='rate_limit')
        self.assertEqual(self.b.summary(self.b.state())['state'],'BLOCKED')
        r=self.call('UserPromptSubmit',prompt='Continue');self.assertIn('further human prompt',str(r));self.assertEqual(self.b.state()['halt']['reason'],'sealed output changed')

    def test_ordinary_content_cannot_claim_provider_quota(self):
        for result in [{'content':[{'type':'text','text':'An essay discussing usage limits'}]}, {'prompt':'rate_limit','content':[]}, {'content':[{'type':'text','text':'Normal result'},{'type':'text','text':'Agent terminated early due to an API error: rate_limit'}]}]:
            self.assertFalse(self.b.agent_quota_error(result))

    def test_repeated_quota_preserves_original_agent(self):
        self.spawn();self.result();self.call('StopFailure',error='rate_limit')
        for i in range(3):
            self.call('UserPromptSubmit',prompt='Continue');self.call('StopFailure',error='rate_limit')
        self.assertFalse(self.b.state().get('halt'));self.assertEqual(self.b.state()['agents'],{'child':'first'})
