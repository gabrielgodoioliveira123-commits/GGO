"""Offline integrity and behavior tests for the portable God Prompt skill."""
import importlib.util, json, tempfile, unittest
from unittest.mock import patch
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('god_prompt',ROOT/'scripts'/'god_prompt.py')
gp=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gp)

class TestGodPrompt(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest=Path(self.tmp.name)/'project'
        class Args:pass
        a=Args();a.request=str(ROOT/'examples'/'request.json');a.out=str(self.dest)
        gp.init(a)
    def build(self):
        class Args:pass
        a=Args();a.project=str(self.dest)
        gp.build(a)
    def test_standard_skill_manifest(self):
        s=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(s.startswith('---\nname: god-prompt\n'))
        self.assertIn('description:',s)
        self.assertIn('THREE',s)
    def test_catalog_count_and_verified_headers(self):
        c=gp.load(gp.CATALOG)
        self.assertEqual(len(c['prompt_patterns']),25)
        self.assertGreaterEqual(len(c['skill_candidates']),25)
        self.assertEqual(c['verified_skill_headers'],26)
    def test_300_variants_and_full_graph(self):
        self.build()
        cs=gp.load(self.dest/'candidates_300.json')
        self.assertEqual(len(cs['ranked']),300)
        self.assertEqual(len(set(x['id'] for x in cs['ranked'])),300)
        self.assertTrue(cs['not_an_empirical_benchmark'])
        gr=gp.load(self.dest/'interaction_graph.json')
        n=gr['node_count']
        self.assertEqual(gr['logical_edge_count'],n*(n-1))
        self.assertEqual(sum(map(sum,gr['adjacency'])),n*(n-1))
        self.assertEqual(sum(gr['adjacency'][0]),n-1)
        self.assertFalse((self.dest/'GOD_PROMPT_COMPLETE_OR_PARTIAL.txt').exists())
    def test_seed_is_apl_not_runtime_author_promo(self):
        self.build()
        s=(self.dest/'GOD_PROMPT_SEED.txt').read_text(encoding='utf-8')
        self.assertIn("GP.CONNECT_ALL←1",s)
        self.assertIn('GP.S37←',s)
        self.assertIn('GP.P24←',s)
        self.assertNotIn('Gabriel Godoi de Oliveira',s)
        self.assertIn('⎕IO←0',s)
    def test_local_provenance_and_dedup(self):
        p=Path(self.tmp.name)/'note.md';p.write_text('Original authorized notes about an RPG.',encoding='utf-8')
        class Args:pass
        a=Args();a.project=str(self.dest);a.paths=[str(p),str(p)]
        gp.ingest(a)
        m=gp.load(self.dest/'manifest.json')
        self.assertEqual(len(m['sources']),1)
        self.assertEqual(len(m['sources'][0]['sha256']),64)
    def test_full_local_text_preservation(self):
        local=Path(self.tmp.name)/'all.md'
        original='First line\nSecond line with café content\nThird line'
        local.write_text(original,encoding='utf-8')
        class Args: pass
        a=Args();a.project=str(self.dest);a.paths=[str(local)]
        gp.ingest(a)
        self.build()
        corpus=(self.dest/'GOD_PROMPT_SOURCE_CORPUS.txt').read_text(encoding='utf-8')
        for line in original.splitlines():self.assertIn('⍝ '+line,corpus)

    def test_mock_does_not_credit_pages(self):
        self.build()
        class Args:pass
        a=Args();a.project=str(self.dest);a.pages=5;a.mock=True;a.provider='openai';a.model=None
        gp.expand(a)
        m=gp.load(self.dest/'manifest.json')
        self.assertEqual(m['state'],'SEED_READY')
        self.assertEqual(len(m['completed_pages']),0)
        self.assertTrue((self.dest/'MOCK_DEMONSTRATION_NOT_A_PAGE.txt').exists())
    def test_no_credentials(self):
        self.build()
        m=gp.load(self.dest/'manifest.json')
        self.assertNotIn('OPENAI_API_KEY',json.dumps(m))
    def test_apl_quoting_and_comment_escape(self):
        self.assertEqual(gp.aplstr("don't\nrun"),"'don''t run'")
        self.assertEqual(gp.aplcomment('one\ntwo'),'⍝ one\n⍝ two\n')

# Supplemental volume and open-target verification suite.
class TestVolumesAndOpenTargets(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name)/'project'
        class A:pass
        self.A=A
        a=A();a.request=str(ROOT/'examples'/'request_small.json');a.out=str(self.project);gp.init(a)
        a=A();a.project=str(self.project);gp.build(a)
    def new_page(self,topic):
        # substantive distinct natural-language APL instruction, no fake page credit
        path=Path(self.tmp.name)/f'input_{topic}.txt'
        sentences=[f'The {topic} module requires complete requirements and validation based on original documents with a provenance trail, independent analysis, measurable coverage criteria, and explicit acceptance tests for each component.' for _ in range(6)]
        path.write_text(' '.join(sentences),encoding='utf-8')
        a=self.A();a.project=str(self.project);a.file=str(path);gp.add_page(a)
    def test_10000_target_and_100_volume_plan(self):
        a=self.A();a.project=str(self.project);a.pages=10000;a.pages_per_txt=100;a.words_per_page=None
        gp.set_target(a)
        m=gp.load(self.project/'manifest.json')
        self.assertEqual(m['target_pages'],10000)
        self.assertEqual(m['pages_per_txt'],100)
        self.assertEqual(m['target_words'],1000000) # small example 100 words/page
        self.assertEqual(len(m['completed_pages']),0)
        self.assertFalse((self.project/'volumes'/'VOLUME_00001.txt').exists())
    def test_custom_future_target_has_no_fixed_limit(self):
        a=self.A();a.project=str(self.project);a.pages=25000;a.pages_per_txt=50;a.words_per_page=None
        gp.set_target(a)
        m=gp.load(self.project/'manifest.json')
        self.assertEqual(m['target_pages'],25000)
        self.assertEqual(m['pages_per_txt'],50)
    def test_host_page_export_and_hash_audit(self):
        self.new_page('ALPHA')
        a=self.A();a.project=str(self.project);a.pages_per_txt=1;a.assemble=True
        gp.export_volumes(a)
        m=gp.load(self.project/'manifest.json')
        index=gp.load(self.project/'volumes'/'INDEX.json')
        self.assertEqual(len(m['completed_pages']),1)
        self.assertEqual(index['planned_txt_volumes'],3)
        self.assertEqual(index['actual_txt_volumes_created'],1)
        self.assertFalse(index['all_pages_delivered'])
        self.assertTrue((self.project/'GOD_PROMPT_COMPLETE_OR_PARTIAL.txt').exists())
        self.assertNotIn('javascript', (self.project/'volumes'/'VOLUME_00001.txt').read_text(encoding='utf-8').lower())
    def test_empty_export_does_not_create_fictional_volumes(self):
        a=self.A();a.project=str(self.project);a.pages_per_txt=None;a.assemble=False
        gp.export_volumes(a)
        index=gp.load(self.project/'volumes'/'INDEX.json')
        self.assertEqual(index['planned_txt_volumes'],2)
        self.assertEqual(index['actual_txt_volumes_created'],0)
    def test_tampering_blocks_export(self):
        self.new_page('TEST')
        path=self.project/'pages'/'page_000001.txt'
        path.write_text('⍝ tampered content',encoding='utf-8')
        a=self.A();a.project=str(self.project);a.pages_per_txt=None;a.assemble=False
        with self.assertRaises(RuntimeError):gp.export_volumes(a)
    def test_reject_short_host_page(self):
        path=Path(self.tmp.name)/'short.txt';path.write_text('insufficient content',encoding='utf-8')
        a=self.A();a.project=str(self.project);a.file=str(path)
        with self.assertRaisesRegex(ValueError,'Insufficient'):gp.add_page(a)
        self.assertEqual(len(gp.load(self.project/'manifest.json')['completed_pages']),0)
    def test_reject_js_in_generated_apl(self):
        path=Path(self.tmp.name)/'js.txt';path.write_text('```javascript\nconst x = 1\n```',encoding='utf-8')
        a=self.A();a.project=str(self.project);a.file=str(path)
        with self.assertRaisesRegex(ValueError,'JavaScript'):gp.add_page(a)
    def test_seed_keeps_page_size_and_density(self):
        data=(self.project/'GOD_PROMPT_SEED.txt').read_text(encoding='utf-8')
        self.assertIn('GP.PAGES_PER_TXT←2',data)
        self.assertIn("GP.DENSITY←'dense'",data)

class TestUserSelectedLanguage(unittest.TestCase):
    def test_non_apl_requested_language_still_txt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);request=gp.load(ROOT/'examples/request_small.json')
            request['format']='PYTHON'
            reqfile=root/'request.json';gp.save(reqfile,request)
            class A:pass
            a=A();a.request=str(reqfile);a.out=str(root/'project');gp.init(a)
            a=A();a.project=str(root/'project');gp.build(a)
            output=root/'project'/'GOD_PROMPT_SEED.txt'
            self.assertTrue(output.exists())
            content=output.read_text(encoding='utf-8')
            self.assertIn('OUTPUT FORMAT: PYTHON',content)
            self.assertNotIn('original_apl_blueprint',content)
    def test_default_is_apl_with_txt(self):
        request=gp.load(ROOT/'examples/request.json')
        self.assertEqual(request['format'],'APL')
        self.assertEqual(request['target_pages'],10000)
        self.assertEqual(request['words_per_page'],500)
        self.assertEqual(request['pages_per_txt'],100)


class TestEnglishReleaseBehavior(unittest.TestCase):
    setUp=TestVolumesAndOpenTargets.setUp
    new_page=TestVolumesAndOpenTargets.new_page
    def test_existing_project_is_preserved(self):
        before=(self.project/'manifest.json').read_bytes()
        a=self.A();a.request=str(ROOT/'examples/request_small.json');a.out=str(self.project)
        with self.assertRaisesRegex(ValueError, 'already initialized'):
            gp.init(a)
        self.assertEqual((self.project/'manifest.json').read_bytes(),before)

    def test_seed_preserves_language_and_user_constraints(self):
        seed=(self.project/'GOD_PROMPT_SEED.txt').read_text(encoding='utf-8')
        self.assertIn("GP.CONTENT_LANGUAGE←'English'",seed)
        for constraint in gp.load(ROOT/'examples/request_small.json')['constraints']:
            self.assertIn(constraint,seed)

    def test_expansion_uses_english_and_constraints_without_network(self):
        text=' '.join(f'Testword{i}' for i in range(120))
        a=self.A();a.project=str(self.project);a.pages=1;a.mock=False;a.provider='openai';a.model='offline-fixture'
        with patch.dict(os.environ, {'OPENAI_API_KEY':'offline-test-placeholder'}):
            with patch.object(gp,'model_output',return_value=text) as provider:
                gp.expand(a)
        brief=provider.call_args.args[0]
        self.assertIn('CONTENT LANGUAGE: English',brief)
        self.assertNotIn('Portuguese words',brief)
        for constraint in gp.load(ROOT/'examples/request_small.json')['constraints']:
            self.assertIn(constraint,brief)

    def test_failed_integrity_check_preserves_exported_volumes(self):
        self.new_page('PRESERVATION')
        a=self.A();a.project=str(self.project);a.pages_per_txt=1;a.assemble=True
        gp.export_volumes(a)
        files=[self.project/'volumes/VOLUME_00001.txt', self.project/'volumes/INDEX.json',
               self.project/'GOD_PROMPT_COMPLETE_OR_PARTIAL.txt']
        before={p:p.read_bytes() for p in files}
        (self.project/'pages/page_000001.txt').write_text('tampered input',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'Integrity mismatch'):
            gp.export_volumes(a)
        self.assertEqual({p:p.read_bytes() for p in files},before)


if __name__=='__main__':unittest.main()
