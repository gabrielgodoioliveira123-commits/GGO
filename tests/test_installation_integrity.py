"""Installer rollback and complete-package verification regressions."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from package_integrity import REQUIRED_FILES,read_verified,canonical_path
from install_skill import install
from validate_skill import validate


class TestInstallationIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve();self.source=self.base/'source';self.source.mkdir()
        self.target=self.base/'host/.agents/skills/god-prompt'
        self.files=sorted(REQUIRED_FILES)
        for relative in self.files:
            path=self.source/relative;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((ROOT/relative).read_bytes())
        self.inventory()

    def inventory(self):
        manifest={'project':'Fixture','version':'1.2.1','files_excluding_checksum_and_manifest':self.files}
        (self.source/'package_manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        listing=''.join(hashlib.sha256((self.source/path).read_bytes()).hexdigest()+'  '+path+'\n'
                        for path in self.files+['package_manifest.json'])
        (self.source/'SHA256SUMS').write_text(listing,encoding='utf-8',newline='\n')

    def existing(self):
        self.target.mkdir(parents=True)
        (self.target/'user-note.txt').write_text('Preserve this existing installation',encoding='utf-8')

    def test_installs_only_verified_inventory(self):
        (self.source/'.env.local').write_text('PRIVATE_FIXTURE',encoding='utf-8')
        (self.source/'scripts/customer-note.json').write_text('{}',encoding='utf-8')
        self.assertIsNone(install(self.source,self.target))
        self.assertFalse((self.target/'.env.local').exists())
        self.assertFalse((self.target/'scripts/customer-note.json').exists())
        self.assertEqual(len(read_verified(self.target)),len(self.files)+2)
        self.assertEqual(validate(self.target,True),[])

    def test_replacement_keeps_original_backup(self):
        self.existing();backup=install(self.source,self.target,True)
        self.assertEqual((backup/'user-note.txt').read_text(),'Preserve this existing installation')
        self.assertTrue((self.target/'SKILL.md').is_file())

    def test_failed_staging_leaves_existing_installation_untouched(self):
        self.existing();original=Path.write_bytes
        def fail(path,data):
            if '.god-prompt-install-' in str(path) and path.name=='README.md':raise OSError('fixture write failure')
            return original(path,data)
        with patch.object(Path,'write_bytes',fail):
            with self.assertRaises(OSError):install(self.source,self.target,True)
        self.assertTrue((self.target/'user-note.txt').is_file())

    def test_failed_final_rename_restores_original(self):
        self.existing();original=Path.replace
        def fail(path,dest):
            if path.name.startswith('.god-prompt-install-') and Path(dest)==self.target:raise OSError('fixture rename failure')
            return original(path,dest)
        with patch.object(Path,'replace',fail):
            with self.assertRaises(OSError):install(self.source,self.target,True)
        self.assertTrue((self.target/'user-note.txt').is_file())

    def test_corrupt_source_does_not_replace_target(self):
        self.existing();(self.source/'README.md').write_text('changed',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'mismatch'):install(self.source,self.target,True)
        self.assertTrue((self.target/'user-note.txt').is_file())

    def test_blank_malformed_duplicate_and_incomplete_checksum_lists_fail(self):
        valid=(self.source/'SHA256SUMS').read_text()
        cases=['','\n','bad line\n',valid+valid.splitlines()[0]+'\n',valid.splitlines()[0]+'\n']
        for data in cases:
            with self.subTest(data=data[:20]):
                (self.source/'SHA256SUMS').write_text(data,encoding='utf-8')
                with self.assertRaises(ValueError):read_verified(self.source)

    def test_noncanonical_paths_fail_without_reading_outside(self):
        for value in ('../outside.txt','/absolute','C:/private.txt','scripts\\x.py','a:stream','.','a//b','./file'):
            with self.subTest(path=value):
                with self.assertRaises(ValueError):canonical_path(value)

    def test_invalid_json_containers_get_validator_diagnostics(self):
        for value in (None,[],{'prompt_patterns':'x'*25,'skill_candidates':'y'*25}):
            (self.source/'references/catalog.json').write_text(json.dumps(value),encoding='utf-8')
            self.assertTrue(any('catalog:' in item for item in validate(self.source)))

    def test_empty_description_cannot_borrow_next_line(self):
        path=self.source/'SKILL.md';text=path.read_text(encoding='utf-8')
        import re
        path.write_text(re.sub(r'^description:.*$','description:',text,flags=re.M),encoding='utf-8')
        self.assertTrue(any('description' in item for item in validate(self.source)))

    def test_unreadable_or_invalid_utf8_files_get_diagnostics(self):
        (self.source/'SKILL.md').write_bytes(b'\xff')
        (self.source/'examples/request.json').unlink()
        errors=validate(self.source)
        self.assertTrue(any('SKILL.md' in item for item in errors))
        self.assertTrue(any('examples/request.json' in item for item in errors))


if __name__=='__main__':unittest.main()
