from pathlib import Path
import importlib.util,unittest
spec=importlib.util.spec_from_file_location('tool_followup',Path(__file__).with_name('audit.py'));a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
SID='00000000-1111-2222-3333-444444444444'
class Tests(unittest.TestCase):
 def fixture(self,count=1):
  payload={'type':'function_call_output','call_id':'call-test','output':'Complete retained text, opaque to the audit.'};native={}
  for i in range(count):
   key=(SID,i+1,str(i)*64);raw=payload['output'].encode();native[key]={'session_id':SID,'source_line':i+1,'source_record_sha256':key[2],'tool_type':payload['type'],'call_id_sha256':a.sha(payload['call_id'].encode()),'payload_core_sha256':a.sha(a.canonical(payload)),'string_bodies':[{'field':'output','sha256':a.sha(raw),'bytes':len(raw)}]}
  return a.Matcher(native,set()),payload
 def test_explicit_unique_identity_and_complete_payload_required(self):
  m,p=self.fixture();m.walk({'session_id':SID,'visible_tool':p},{'member':'fixture'})
  self.assertEqual(len(m.exact),1)
  m,p=self.fixture();m.walk({'session_id':SID,'visible_tool':dict(p,output='changed')},{'member':'fixture'})
  self.assertFalse(m.exact)
 def test_repeated_native_call_tuple_is_ambiguous(self):
  m,p=self.fixture(2);m.walk({'session_id':SID,'visible_tool':p},{'member':'fixture'})
  self.assertFalse(m.exact);self.assertEqual(len(m.ambiguous),2)
 def test_equal_text_without_identity_is_content_only(self):
  m,p=self.fixture();m.walk({'text':p['output']},{'member':'fixture'})
  self.assertFalse(m.exact);self.assertEqual(len(m.content),1)
 def test_no_substring_or_fuzzy_matching(self):
  m,p=self.fixture();m.walk({'text':'prefix '+p['output']},{'member':'fixture'})
  self.assertFalse(m.content)
 def test_other_provider_cannot_become_exact_codex_identity(self):
  m,p=self.fixture();m.walk({'session_id':SID,'visible_tool':p},{'member':'fixture'},provider='claude')
  self.assertFalse(m.exact);self.assertTrue(m.content)
 def test_hidden_contexts_are_not_searched(self):
  m,p=self.fixture();m.walk({'phase':'analysis','text':p['output']},{'member':'fixture'})
  m.walk({'reasoning':{'text':p['output']}},{'member':'fixture'})
  m.walk({'role':'developer','content':p['output']},{'member':'fixture'})
  self.assertFalse(m.content)
 def test_nonrecord_schema_objects_are_not_treated_as_tools(self):
  m,p=self.fixture();m.walk({'type':{'type':'string'},'role':['assistant'],'phase':{}},{'member':'schema'})
  self.assertFalse(m.exact);self.assertFalse(m.content)
if __name__=='__main__':unittest.main()
