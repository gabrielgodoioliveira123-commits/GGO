"""Exercise the documented offline workflow through real CLI subprocesses."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT/'scripts/god_prompt.py'
REQUEST = ROOT/'examples/request_quickstart.json'
SAMPLE_PAGE = ROOT/'examples/page_001.txt'

LOCK_HOLDER = r'''
import os
from pathlib import Path
import sys
with Path(sys.argv[1]).open('a+b') as lock:
    if lock.tell() == 0:
        lock.write(b'0')
        lock.flush()
    lock.seek(0)
    if os.name == 'nt':
        import msvcrt
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    Path(sys.argv[2]).write_text('locked', encoding='utf-8')
    sys.stdin.buffer.read()
'''


class TestCLIWorkflow(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        # macOS temporary paths may have /var -> /private/var aliases.
        self.base = Path(self.temporary.name).resolve()
        self.project = self.base/'project'
        self.environment = os.environ.copy()
        self.environment.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
        for name in ('OPENAI_API_KEY', 'GITHUB_TOKEN', 'GOD_PROMPT_MODEL'):
            self.environment.pop(name, None)

    def run_cli(self, *arguments, expected=0):
        result = subprocess.run(
            [sys.executable, str(CLI), *map(str, arguments)], cwd=ROOT,
            env=self.environment, capture_output=True, text=True,
            encoding='utf-8', errors='replace', timeout=30,
        )
        output = result.stdout + result.stderr
        self.assertNotIn('Traceback (most recent call last)', output)
        self.assertEqual(result.returncode, expected, output)
        return result

    def initialize(self, build=False):
        self.run_cli('init', '--request', REQUEST, '--out', self.project)
        if build:
            self.run_cli('build', '--project', self.project)

    def read_json(self, relative):
        return json.loads((self.project/relative).read_text(encoding='utf-8'))

    def test_readme_offline_workflow_exports_a_complete_audited_page(self):
        self.initialize()
        note = ROOT/'examples/EXAMPLE_NOTE.txt'
        self.run_cli('ingest', '--project', self.project, note)
        imported = self.read_json('manifest.json')['sources']
        self.assertEqual(len(imported), 1)
        stored = (self.project/imported[0]['stored_as']).read_text(encoding='utf-8')
        self.assertEqual(stored, note.read_text(encoding='utf-8-sig'))

        self.run_cli('build', '--project', self.project)
        planned = self.read_json('manifest.json')
        self.assertEqual(planned['state'], 'SEED_READY')
        self.assertEqual(planned['completed_pages'], [])
        self.assertEqual(len(self.read_json('candidates_300.json')['ranked']), 300)

        self.run_cli('add-page', '--project', self.project, '--file', SAMPLE_PAGE)
        self.run_cli('export', '--project', self.project, '--assemble')
        self.run_cli('audit', '--project', self.project)
        report = self.read_json('audit.json')
        self.assertEqual(report['state'], 'COMPLETE')
        self.assertTrue(report['complete'])
        self.assertEqual(report['actual_substantive_pages'], 1)
        self.assertEqual(report['generated_txt_volumes'], 1)
        self.assertEqual(report['issues'], [])
        self.assertEqual(report['export_issues'], [])
        index = self.read_json('volumes/INDEX.json')
        self.assertTrue(index['all_pages_delivered'])
        self.assertTrue(index['assembled_current'])
        volume = index['volumes'][0]
        data = (self.project/volume['file']).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), volume['sha256_bytes'])
        self.assertIn('Read the complete supplied passage', data.decode('utf-8'))
        self.assertTrue((self.project/'GOD_PROMPT_COMPLETE_OR_PARTIAL.txt').is_file())

    def test_rejected_page_preserves_state_and_releases_the_command_lock(self):
        self.initialize(build=True)
        manifest = self.project/'manifest.json'
        before = manifest.read_bytes()
        short = self.base/'short.txt'
        short.write_text('This page is too short.', encoding='utf-8')
        result = self.run_cli('add-page', '--project', self.project, '--file', short, expected=2)
        self.assertIn('ERROR:', result.stderr)
        self.assertEqual(manifest.read_bytes(), before)
        self.run_cli('add-page', '--project', self.project, '--file', SAMPLE_PAGE)
        self.run_cli('audit', '--project', self.project)
        self.assertTrue(self.read_json('audit.json')['complete'])

    def test_missing_project_and_malformed_request_fail_without_tracebacks(self):
        result = self.run_cli('build', '--project', self.project, expected=2)
        self.assertIn('ERROR:', result.stderr)
        invalid = self.base/'invalid-request.json'
        invalid.write_text('[]', encoding='utf-8')
        result = self.run_cli('init', '--request', invalid, '--out', self.project, expected=2)
        self.assertIn('ERROR:', result.stderr)
        self.assertFalse((self.project/'manifest.json').exists())
        result = self.run_cli('unknown-command', expected=2)
        self.assertIn('usage:', result.stderr)

    def test_duplicate_init_and_invalid_manifest_preserve_existing_data(self):
        self.initialize()
        manifest = self.project/'manifest.json'
        before = manifest.read_bytes()
        self.run_cli('init', '--request', REQUEST, '--out', self.project, expected=2)
        self.assertEqual(manifest.read_bytes(), before)
        corrupt = b'{"unfinished":'
        manifest.write_bytes(corrupt)
        result = self.run_cli('audit', '--project', self.project, expected=2)
        self.assertIn('ERROR:', result.stderr)
        self.assertEqual(manifest.read_bytes(), corrupt)

    def test_audit_reports_a_tampered_page_as_invalid(self):
        self.initialize(build=True)
        self.run_cli('add-page', '--project', self.project, '--file', SAMPLE_PAGE)
        page = self.project/self.read_json('manifest.json')['completed_pages'][0]['path']
        with page.open('a', encoding='utf-8') as output:
            output.write('\nUnrecorded edit.\n')
        self.run_cli('audit', '--project', self.project, expected=1)
        report = self.read_json('audit.json')
        self.assertEqual(report['state'], 'INVALID')
        self.assertFalse(report['complete'])
        self.assertTrue(report['issues'])
        self.assertIn('Unrecorded edit.', page.read_text(encoding='utf-8'))

    def test_os_lock_excludes_another_process_and_releases_after_process_exit(self):
        self.initialize()
        ready = self.base/'lock-ready.txt'
        holder = subprocess.Popen(
            [sys.executable, '-c', LOCK_HOLDER, str(self.project/'.ggo.lock'), str(ready)],
            cwd=ROOT, env=self.environment, stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
        )

        def stop_holder():
            if holder.poll() is None:
                holder.terminate()
                try:
                    holder.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    holder.kill()
                    holder.wait(timeout=5)
            for stream in (holder.stdin, holder.stderr):
                if stream is not None:
                    stream.close()

        self.addCleanup(stop_holder)
        deadline = time.monotonic() + 5
        while not ready.exists() and holder.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        if not ready.exists():
            stop_holder()
            self.fail('The isolated lock-holder process did not acquire its project lock')
        before = (self.project/'manifest.json').read_bytes()
        result = self.run_cli('build', '--project', self.project, expected=2)
        self.assertIn('Another command is using this project', result.stderr)
        self.assertEqual((self.project/'manifest.json').read_bytes(), before)
        stop_holder()
        self.run_cli('build', '--project', self.project)
        self.assertEqual(self.read_json('manifest.json')['state'], 'SEED_READY')


if __name__ == '__main__':
    unittest.main()
