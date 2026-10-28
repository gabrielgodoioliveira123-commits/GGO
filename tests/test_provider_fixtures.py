"""Provider response fixtures: no live network, real keys, or model spending."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace as A
import unittest
from unittest.mock import patch
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('provider_runtime',ROOT/'scripts/god_prompt.py')
gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)


class Response:
    def __init__(self,data):self.data=data
    def __enter__(self):return io.BytesIO(json.dumps(self.data).encode('utf-8'))
    def __exit__(self,*args):return False


class TestProviderFixtures(unittest.TestCase):
    def payload(self,prefix='word'):return ' '.join(prefix+str(i) for i in range(120))

    def test_incomplete_response_never_returns_partial_page(self):
        response={'status':'incomplete','incomplete_details':{'reason':'max_output_tokens'},
                  'output':[{'content':[{'type':'output_text','text':self.payload()}]}]}
        with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-test-placeholder'}),patch.object(gp.urllib.request,'urlopen',return_value=Response(response)):
            with self.assertRaisesRegex(RuntimeError,'not completed'):gp.model_output('fixture','offline-model',100)

    def test_completed_output_skips_reasoning_and_disables_response_storage(self):
        response={'status':'completed','output':[{'type':'reasoning','content':None},
            {'type':'message','content':[{'type':'output_text','text':self.payload()}]}]}
        with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-test-placeholder'}),patch.object(gp.urllib.request,'urlopen',return_value=Response(response)) as network:
            self.assertEqual(gp.model_output('fixture','offline-model',100),self.payload())
        request=network.call_args.args[0]
        body=json.loads(request.data)
        self.assertFalse(body['store']);self.assertEqual(request.full_url,'https://api.openai.com/v1/responses')

    def test_malformed_or_empty_completed_outputs_fail_cleanly(self):
        for output in (None,'bad',[],[{'type':'message','content':None}],[{'content':[{'type':'output_text','text':42}]}]):
            with self.subTest(output=output):
                with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-test-placeholder'}),patch.object(gp.urllib.request,'urlopen',return_value=Response({'status':'completed','output':output})):
                    with self.assertRaises(RuntimeError):gp.model_output('fixture','offline-model',100)

    def test_http_errors_do_not_echo_provider_body(self):
        error=urllib.error.HTTPError('https://api.openai.com/v1/responses',401,'PRIVATE_FIXTURE',{},None)
        with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-test-placeholder'}),patch.object(gp.urllib.request,'urlopen',side_effect=error):
            with self.assertRaisesRegex(RuntimeError,'HTTP 401') as caught:gp.model_output('fixture','offline-model',100)
        self.assertNotIn('PRIVATE_FIXTURE',str(caught.exception))

    def test_missing_key_does_not_contact_provider(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':''}),patch.object(gp.urllib.request,'urlopen') as network:
            with self.assertRaisesRegex(RuntimeError,'unset'):gp.model_output('fixture','offline-model',100)
            network.assert_not_called()

    def test_explicit_token_budget_is_sent_without_live_request(self):
        response={'status':'completed','output':[{'content':[{'type':'output_text','text':self.payload()}]}]}
        with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-test-placeholder'}),patch.object(gp.urllib.request,'urlopen',return_value=Response(response)) as network:
            gp.model_output('fixture','offline-model',100,4200)
        self.assertEqual(json.loads(network.call_args.args[0].data)['max_output_tokens'],4200)

    def test_harvest_does_not_verify_truncated_or_empty_headers(self):
        with tempfile.TemporaryDirectory() as directory,contextlib.redirect_stdout(io.StringIO()):
            project=Path(directory)/'project';gp.init(A(request=str(ROOT/'examples/request_small.json'),out=str(project)))
            bodies=[b'---\nname: example\ndescription:\nlicense: MIT\n---\n',b'x'*700001,
                    b'---\nname: example\ndescription: Valid skill metadata\n---\n']
            for body,status in zip(bodies,('not-skill-frontmatter','unavailable','verified')):
                with patch.object(gp.urllib.request,'urlopen',return_value=io.BytesIO(body)):
                    gp.harvest(A(project=str(project),max_files=1,online=True))
                result=gp.load(project/'skill_verifications.json')[0]
                self.assertEqual(result['status'],status)
                if status=='unavailable':self.assertNotIn('sha256',result)

    def test_expansion_carries_full_contracts_and_retries_are_bounded(self):
        with tempfile.TemporaryDirectory() as directory,contextlib.redirect_stdout(io.StringIO()):
            base=Path(directory);project=base/'project'
            gp.init(A(request=str(ROOT/'examples/request_small.json'),out=str(project)))
            gp.build(A(project=str(project)))
            args=A(project=str(project),pages=1,mock=False,provider='openai',model='offline-model')
            with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-test-placeholder'}),patch.object(gp,'model_output',return_value=self.payload()) as model:
                gp.expand(args)
                self.assertIn('GPN.SECURITY00',model.call_args.args[0])
                self.assertIn('FULL SKILL AND CONTRACT SEED',model.call_args.args[0])
                model.reset_mock()
                with self.assertRaisesRegex(RuntimeError,'3 attempts'):gp.expand(args)
                self.assertEqual(model.call_count,3)
            self.assertEqual(len(gp.load(project/'manifest.json')['completed_pages']),1)

    def test_invalid_page_count_does_not_contact_provider(self):
        with tempfile.TemporaryDirectory() as directory,contextlib.redirect_stdout(io.StringIO()):
            project=Path(directory)/'project'
            gp.init(A(request=str(ROOT/'examples/request_small.json'),out=str(project)))
            with patch.object(gp,'model_output') as model:
                with self.assertRaises(ValueError):gp.expand(A(project=str(project),pages=-1,mock=True))
                model.assert_not_called()

    def test_source_context_rotates_and_respects_character_budget(self):
        with tempfile.TemporaryDirectory() as directory,contextlib.redirect_stdout(io.StringIO()):
            base=Path(directory);project=base/'project';sources=base/'inputs';sources.mkdir()
            gp.init(A(request=str(ROOT/'examples/request_small.json'),out=str(project)))
            for i in range(6):(sources/f'source{i}.txt').write_text((f'source{i} ')*800,encoding='utf-8')
            gp.ingest(A(project=str(project),paths=[str(sources)]))
            manifest=gp.load(project/'manifest.json');seen=set()
            for index in range(1,7):
                text=gp.source_context(project,manifest,index,2500)
                self.assertLessEqual(len(text),2500)
                for i in range(6):
                    if f'source{i}.txt' in text:seen.add(i)
            self.assertEqual(seen,set(range(6)))


if __name__=='__main__':unittest.main()
