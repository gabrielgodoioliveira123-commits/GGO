"""Offline privacy boundaries for distributable source archives."""
import importlib.util
import io
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('build_release', ROOT/'scripts/build_release.py')
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)
PRIVATE_MARKER = b'PRIVATE_FIXTURE_SENTINEL_DO_NOT_DISTRIBUTE'


class TestReleasePackaging(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name).resolve()
        self.root = self.parent/'checkout'
        self.root.mkdir()
        for relative in release.SOURCE_FILES:
            (self.root/relative).write_text('Public source fixture\n', encoding='utf-8')
        for directory in release.SOURCE_DIRS:
            (self.root/directory).mkdir()
        self.root_patch = patch.object(release, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def write(self, relative, content=PRIVATE_MARKER):
        path = self.root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def archive_files(self):
        artifacts = release.release_contents()
        with zipfile.ZipFile(io.BytesIO(artifacts[release.ARCHIVE])) as archive:
            return {name: archive.read(name) for name in archive.namelist()}

    def directory_link(self, target, link):
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as error:
            if os.name != 'nt':
                self.skipTest('Directory symlink is unavailable: '+str(error))
            # Windows junctions work without Developer Mode or symlink privilege.
            import _winapi
            try:
                _winapi.CreateJunction(str(target), str(link))
            except OSError as junction_error:
                self.skipTest('Directory links are unavailable: '+str(junction_error))

    def test_archive_keeps_public_sources_and_excludes_private_artifacts(self):
        public = {
            '.github/workflows/ci.yml': b'name: Offline tests\n',
            'agents/openai.yaml': b'display_name: Public fixture\n',
            'engine/core.apl': b'PUBLIC_CORE\n',
            'examples/request.json': b'{"goal":"Public example"}\n',
            'references/guide.md': b'# Public guide\n',
            'scripts/example.py': b'print("public fixture")\n',
            'tests/test_example.py': b'# Public test\n',
        }
        for relative, content in public.items():
            self.write(relative, content)
        private = (
            'personal-notes.txt', 'output/personal-notes.txt',
            'examples/.env', 'examples/.env.local', 'examples/credentials.json',
            'examples/CREDENTIALS.backup.JSON', 'references/secrets.local.yaml',
            'examples/secrets.yaml', 'examples/token.json',
            'references/client_secret_fixture.json', 'references/service-account.json',
            'references/private/notes.md', 'references/personal/notes.txt',
            'references/.private/notes.md', 'examples/private.key',
            'examples/private.pem', 'examples/private.secret', 'examples/private.log',
            'examples/photo.jpg', 'examples/archive.zip', 'scripts/debug.log',
            'scripts/__pycache__/cached.py', 'scripts/cache/copied.py',
            'scripts/.venv/copied.py', 'scripts/node_modules/copied.py',
        )
        for relative in private:
            self.write(relative)
        files = self.archive_files()
        for relative, content in public.items():
            self.assertEqual(files['god-prompt/'+relative], content)
        for relative in private:
            self.assertNotIn('god-prompt/'+relative, files)
        self.assertFalse(any(PRIVATE_MARKER in content for content in files.values()))

    def test_nested_directory_link_never_imports_external_source_text(self):
        external = self.parent/'outside'
        external.mkdir()
        (external/'notes.md').write_bytes(PRIVATE_MARKER)
        self.directory_link(external, self.root/'references'/'linked')
        self.write('references/public.md', b'Public documentation\n')
        files = self.archive_files()
        self.assertIn('god-prompt/references/public.md', files)
        self.assertNotIn('god-prompt/references/linked/notes.md', files)
        self.assertFalse(any(PRIVATE_MARKER in content for content in files.values()))

    def test_linked_required_source_directory_fails_closed(self):
        external = self.parent/'outside'
        external.mkdir()
        (external/'notes.md').write_bytes(PRIVATE_MARKER)
        source_root = self.root/'references'
        source_root.rmdir()
        self.directory_link(external, source_root)
        with self.assertRaisesRegex(ValueError, 'symlink or reparse point'):
            release.release_contents()

    def test_linked_checkout_root_fails_closed(self):
        alias = self.parent/'alias'
        self.directory_link(self.root, alias)
        with patch.object(release, 'ROOT', alias):
            with self.assertRaisesRegex(ValueError, 'symlink or reparse point'):
                release.release_contents()

    def test_linked_checkout_ancestor_fails_closed(self):
        ancestor = self.parent/'real'
        ancestor.mkdir()
        nested = ancestor/'checkout'
        self.root.rename(nested)
        alias = self.parent/'alias'
        self.directory_link(ancestor, alias)
        with patch.object(release, 'ROOT', alias/'checkout'):
            with self.assertRaisesRegex(ValueError, 'symlink or reparse point'):
                release.release_contents()

    def test_windows_reparse_attribute_is_rejected_without_symlink_mode(self):
        info = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_file_attributes=0x400)
        self.assertTrue(release.is_link_or_reparse(info))
        self.assertFalse(release.is_link_or_reparse(
            SimpleNamespace(st_mode=stat.S_IFREG | 0o644, st_file_attributes=0)))

    def test_file_symlink_does_not_enter_archive(self):
        external = self.parent/'outside.md'
        external.write_bytes(PRIVATE_MARKER)
        link = self.root/'references'/'linked.md'
        try:
            link.symlink_to(external)
        except OSError as error:
            self.skipTest('File symlink privilege is unavailable: '+str(error))
        files = self.archive_files()
        self.assertNotIn('god-prompt/references/linked.md', files)
        self.assertFalse(any(PRIVATE_MARKER in content for content in files.values()))


if __name__ == '__main__':
    unittest.main()
