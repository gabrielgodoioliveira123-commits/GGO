"""Data preservation, validation, and complete-skill workflow regressions."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace as A
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime_under_test',ROOT/'scripts/god_prompt.py')
gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)


class TestRuntimeRecovery(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve()
        self.stdout=io.StringIO()
        self.quiet=contextlib.redirect_stdout(self.stdout);self.quiet.__enter__()
        self.addCleanup(self.quiet.__exit__,None,None,None)

    def project(self,fmt='APL',pages=3):
        request=gp.load(ROOT/'examples/request_small.json');request.update(format=fmt,target_pages=pages)
        source=self.base/'request.json';gp.save(source,request)
        project=self.base/'project';gp.init(A(request=str(source),out=str(project)))
        gp.build(A(project=str(project)))
        return project

    def payload(self,prefix):return ' '.join(prefix+str(i) for i in range(120))

    def add(self,project,prefix):
        path=self.base/(prefix+'.txt');path.write_text(self.payload(prefix),encoding='utf-8')
        gp.add_page(A(project=str(project),file=str(path)))

    def export(self,project,assemble=True):
        gp.export_volumes(A(project=str(project),pages_per_txt=1,assemble=assemble))

    def test_non_apl_adjacent_duplicates_are_rejected(self):
        project=self.project('MARKDOWN');self.add(project,'alpha')
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.add(project,'alpha')
        self.assertEqual(len(gp.load(project/'manifest.json')['completed_pages']),1)

    def test_nonadjacent_apl_duplicates_are_rejected(self):
        project=self.project();self.add(project,'alpha');self.add(project,'beta')
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.add(project,'alpha')

    def test_invalid_complete_project_never_reports_complete(self):
        project=self.project(pages=1);self.add(project,'alpha')
        (project/'pages/page_000001.txt').unlink()
        with self.assertRaises(SystemExit):gp.audit(A(project=str(project)))
        report=gp.load(project/'audit.json')
        self.assertEqual(report['state'],'INVALID');self.assertFalse(report['complete'])
        self.assertEqual(gp.load(project/'manifest.json')['state'],'INVALID')

    def test_external_manifest_page_is_rejected(self):
        project=self.project('MARKDOWN',1)
        external=self.base/'outside.txt';data=self.payload('outside')+'\n';external.write_text(data,encoding='utf-8')
        manifest=gp.load(project/'manifest.json')
        manifest.update(state='COMPLETE',completed_pages=[{'index':1,'path':'../outside.txt','sha256':gp.sha(data),'word_count':120}])
        gp.save(project/'manifest.json',manifest)
        with self.assertRaises(RuntimeError):self.export(project)
        self.assertFalse((project/'volumes/VOLUME_00001.txt').exists())

    def test_unrecorded_page_is_not_overwritten(self):
        project=self.project();path=project/'pages/page_000001.txt';path.write_text('Preserve unrecorded result')
        with self.assertRaisesRegex(ValueError,'Unrecorded'):self.add(project,'alpha')
        self.assertEqual(path.read_text(),'Preserve unrecorded result')

    def test_short_page_with_matching_hash_is_not_exported(self):
        project=self.project('MARKDOWN',1);self.add(project,'alpha')
        data='short page\n';(project/'pages/page_000001.txt').write_text(data,encoding='utf-8')
        manifest=gp.load(project/'manifest.json');manifest['completed_pages'][0].update(sha256=gp.sha(data),word_count=2)
        gp.save(project/'manifest.json',manifest)
        with self.assertRaisesRegex(RuntimeError,'short page'):self.export(project)

    def test_foreign_files_matching_old_glob_are_preserved(self):
        project=self.project();(project/'volumes').mkdir()
        foreign=project/'volumes/VOLUME_personal_notes.txt';foreign.write_text('Preserve unrelated file')
        self.export(project,False)
        self.assertEqual(foreign.read_text(),'Preserve unrelated file')

    def test_page_manifest_write_failure_rolls_back(self):
        project=self.project();before=(project/'manifest.json').read_bytes();original=Path.replace
        def fail(path,dest):
            if 'new' in path.parts and Path(dest)==project/'manifest.json':raise OSError('fixture manifest failure')
            return original(path,dest)
        with patch.object(Path,'replace',fail):
            with self.assertRaises(OSError):self.add(project,'alpha')
        self.assertEqual((project/'manifest.json').read_bytes(),before)
        self.assertFalse((project/'pages/page_000001.txt').exists())
        self.assertFalse(list(project.glob('.ggo-stage-*')))

    def test_export_write_failure_preserves_previous_exports(self):
        project=self.project();self.add(project,'alpha');self.export(project)
        files=['volumes/VOLUME_00001.txt','volumes/INDEX.json','GOD_PROMPT_COMPLETE_OR_PARTIAL.txt']
        before={p:(project/p).read_bytes() for p in files};self.add(project,'beta');original=Path.replace
        def fail(path,dest):
            if 'new' in path.parts and Path(dest)==project/'volumes/INDEX.json':raise OSError('fixture export failure')
            return original(path,dest)
        with patch.object(Path,'replace',fail):
            with self.assertRaises(OSError):self.export(project)
        self.assertEqual({p:(project/p).read_bytes() for p in files},before)
        self.assertFalse((project/'volumes/VOLUME_00002.txt').exists())

    def test_edited_export_is_preserved(self):
        project=self.project();self.add(project,'alpha');self.export(project)
        path=project/'volumes/VOLUME_00001.txt';path.write_text('Preserve user edit')
        with self.assertRaisesRegex(RuntimeError,'edited'):self.export(project)
        self.assertEqual(path.read_text(),'Preserve user edit')

    def test_non_apl_target_updates_seed(self):
        project=self.project('MARKDOWN')
        gp.set_target(A(project=str(project),pages=8,words_per_page=None,pages_per_txt=1))
        self.assertIn('PAGES REQUESTED: 8',(project/'GOD_PROMPT_SEED.txt').read_text(encoding='utf-8'))

    def test_modified_source_is_detected_before_build(self):
        project=self.project();source=self.base/'source.txt';source.write_text('Original source')
        gp.ingest(A(project=str(project),paths=[str(source)]))
        record=gp.load(project/'manifest.json')['sources'][0]
        (project/record['stored_as']).write_text('Changed source')
        with self.assertRaisesRegex(RuntimeError,'source SHA'):gp.build(A(project=str(project)))

    def test_new_sources_require_rebuild_even_after_audit(self):
        project=self.project();source=self.base/'source.txt';source.write_text('Original source')
        gp.ingest(A(project=str(project),paths=[str(source)]));gp.audit(A(project=str(project)))
        self.assertEqual(gp.load(project/'manifest.json')['state'],'PLAN_ONLY')
        with self.assertRaisesRegex(ValueError,'Build'):self.add(project,'alpha')

    def test_rust_format_allows_let_instructions(self):
        project=self.project('RUST');path=self.base/'rust.txt'
        path.write_text('let example = 1;\n// '+self.payload('rust'),encoding='utf-8')
        gp.add_page(A(project=str(project),file=str(path)))
        gp.audit(A(project=str(project)))

    def test_invalid_requests_do_not_create_output(self):
        base=gp.load(ROOT/'examples/request_small.json')
        for index,change in enumerate(({'goal':3},{'target_pages':True},{'words_per_page':3001},{'constraints':'bad'},{'content_language':None})):
            request=dict(base);request.update(change);source=self.base/f'invalid{index}.json';gp.save(source,request)
            output=self.base/f'invalid{index}'
            with self.assertRaises(ValueError):gp.init(A(request=str(source),out=str(output)))
            self.assertFalse(output.exists())

    def test_nonempty_destination_is_preserved(self):
        output=self.base/'occupied';output.mkdir();note=output/'note.txt';note.write_text('Preserve')
        with self.assertRaises(ValueError):gp.init(A(request=str(ROOT/'examples/request_small.json'),out=str(output)))
        self.assertEqual(note.read_text(),'Preserve')

    def test_estimate_bounds_are_consistent_and_large_targets_do_not_overflow(self):
        with self.assertRaises(ValueError):gp.estimate(A(pages=1,words_per_page=3001,pages_per_txt=1))
        gp.estimate(A(pages=10**400,words_per_page=100,pages_per_txt=100))

    def test_apl_strings_normalize_all_line_separators(self):
        encoded=gp.aplstr('one\rtwo\u2028three')
        self.assertNotIn('\r',encoded);self.assertNotIn('\u2028',encoded)

    def test_complete_contracts_are_in_seed(self):
        project=self.project();seed=(project/'GOD_PROMPT_SEED.txt').read_text(encoding='utf-8')
        self.assertIn('GPN.SECURITY00',seed);self.assertIn('GPN.QUALITY07',seed)
        self.assertIn('FULL PACKAGED SKILL WORKFLOW',seed)

    def test_seed_tampering_is_detected(self):
        project=self.project();seed=project/'GOD_PROMPT_SEED.txt';seed.write_text('Changed instructions')
        with self.assertRaisesRegex(RuntimeError,'seed SHA'):self.add(project,'alpha')

    def test_modified_assembled_export_is_detected(self):
        project=self.project(pages=1);self.add(project,'alpha');self.export(project)
        (project/'GOD_PROMPT_COMPLETE_OR_PARTIAL.txt').write_text('Changed combined file',encoding='utf-8')
        with self.assertRaises(SystemExit):gp.audit(A(project=str(project)))
        self.assertIn('Assembled export SHA mismatch',gp.load(project/'audit.json')['export_issues'])

    def test_unrefreshed_assembled_export_is_reported_stale(self):
        project=self.project(pages=1);self.add(project,'alpha');self.export(project)
        self.export(project,False)
        with self.assertRaises(SystemExit):gp.audit(A(project=str(project)))
        self.assertTrue(any('Assembled export is stale' in issue for issue in gp.load(project/'audit.json')['export_issues']))


if __name__=='__main__':unittest.main()
