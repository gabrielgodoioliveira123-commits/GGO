#!/usr/bin/env python3
"""Build or check a reproducible source manifest, checksums, and skill archive."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import stat
import zipfile

# Keep the lexical path so a symlink or Windows junction cannot disappear
# through resolve() before source-path checks run.
ROOT = Path(__file__).absolute().parents[1]
VERSION = '1.2.1'
ARCHIVE = 'god-prompt.skill'
ZIP_ARCHIVE = 'PromptGod-Go.zip'
SOURCE_FILES = (
    '.gitattributes', '.gitignore', 'AUTHORS', 'CHANGELOG.md', 'CITATION.cff',
    'CONTRIBUTING.md', 'GITHUB_SETUP.md', 'LICENSE', 'NOTICE', 'README.md',
    'SECURITY.md', 'SKILL.md',
)
SOURCE_DIRS = ('.github', 'agents', 'engine', 'examples', 'references', 'scripts', 'tests')
SOURCE_EXTENSIONS = {
    '.github': frozenset({'.md', '.yaml', '.yml'}),
    'agents': frozenset({'.yaml', '.yml'}),
    'engine': frozenset({'.apl'}),
    'examples': frozenset({'.apl', '.json', '.md', '.txt', '.yaml', '.yml'}),
    'references': frozenset({'.apl', '.json', '.md', '.txt', '.yaml', '.yml'}),
    'scripts': frozenset({'.py'}),
    'tests': frozenset({'.py'}),
}
EXCLUDED_DIRECTORIES = frozenset({
    '__pycache__', 'cache', 'caches', 'credentials', 'logs', 'node_modules',
    'output', 'personal', 'private', 'secrets', 'venv',
})
EXCLUDED_FILE_STEMS = frozenset({
    'credentials', 'private-key', 'private_key', 'secrets', 'token', 'tokens',
})
EXCLUDED_FILE_SUFFIXES = frozenset({
    '.key', '.log', '.pem', '.pfx', '.p12', '.pyc', '.secret',
})


def is_link_or_reparse(info):
    """Reject symlinks and every Windows reparse point, including junctions."""
    return (stat.S_ISLNK(info.st_mode)
            or bool(getattr(info, 'st_file_attributes', 0)
                    & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)))


def check_plain_path(path):
    """Fail closed for a required source path or any linked ancestor."""
    for component in (path, *path.parents):
        if is_link_or_reparse(component.lstat()):
            raise ValueError('Release source path uses a symlink or reparse point: '+str(component))


def allowed_source_file(path, directory):
    """Package source formats only; credential names are never exceptions."""
    name = path.name.casefold()
    return (not name.startswith('.')
            and name.split('.', 1)[0] not in EXCLUDED_FILE_STEMS
            and not name.startswith(('client_secret', 'service-account', 'service_account'))
            and path.suffix.casefold() not in EXCLUDED_FILE_SUFFIXES
            and path.suffix.casefold() in SOURCE_EXTENSIONS[directory])


def source_contents():
    root = Path(ROOT).absolute()
    check_plain_path(root)
    paths = []
    # These named root files are deliberate exceptions to the extension and
    # hidden-file rules (LICENSE, AUTHORS, .gitignore, and .gitattributes).
    for relative in SOURCE_FILES:
        path = root/relative
        check_plain_path(path)
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ValueError('Required release source is not a regular file: '+relative)
        paths.append(path)
    for directory in SOURCE_DIRS:
        source_root = root/directory
        check_plain_path(source_root)
        if not stat.S_ISDIR(source_root.lstat().st_mode):
            raise ValueError('Required release source directory is not a directory: '+directory)
        pending = [source_root]
        while pending:
            for path in sorted(pending.pop().iterdir()):
                info = path.lstat()
                if is_link_or_reparse(info):
                    continue
                if stat.S_ISDIR(info.st_mode):
                    if not path.name.startswith('.') and path.name.casefold() not in EXCLUDED_DIRECTORIES:
                        pending.append(path)
                elif stat.S_ISREG(info.st_mode) and allowed_source_file(path, directory):
                    paths.append(path)
    return {path.relative_to(root).as_posix(): path.read_bytes().replace(b'\r\n', b'\n')
            for path in sorted(paths)}


def release_contents():
    source = source_contents()
    paths = sorted(source)
    manifest = {
        'project': 'PromptGod-Go (GGO)', 'version': VERSION,
        'creator': 'Gabriel Godoi de Oliveira',
        'url': 'https://github.com/gabrielgodoioliveira123-commits/GGO',
        'format_default': 'APL', 'content_language_default': 'English',
        'artifact_extension': 'txt', 'javascript_required': False,
        'python_requirement': '>=3.10; standard library only',
        'target_equivalent_pages_default': 10000, 'words_per_equivalent_page_default': 500,
        'pages_per_txt_default': 100, 'planned_txt_files_default': 100,
        'no_fixed_page_limit_for_planning': True, 'pages_written_in_distribution': 0,
        'prompt_patterns': 25, 'skill_candidates': 38,
        'verified_skill_headers': 26, 'header_verification_snapshot': '2026-10-27 (supplied v1.1.0 kit)',
        'candidate_designs_in_runtime': 300,
        'test_command': 'python -m unittest discover -s tests -v',
        'license': 'MIT for original package only',
        'files_excluding_checksum_and_manifest': paths,
    }
    source['package_manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    sums = ''.join(hashlib.sha256(data).hexdigest()+'  '+path+'\n'
                   for path, data in sorted(source.items()))
    source['SHA256SUMS'] = sums.encode('utf-8')
    output = io.BytesIO()
    # Stored entries avoid differences between platform-specific zlib builds.
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path, data in sorted(source.items()):
            info = zipfile.ZipInfo('god-prompt/'+path, date_time=(2026, 10, 27, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    archive_bytes = output.getvalue()
    return {
        'package_manifest.json': source['package_manifest.json'],
        'SHA256SUMS': source['SHA256SUMS'],
        ARCHIVE: archive_bytes,
        ZIP_ARCHIVE: archive_bytes,
        'SHA256_RELEASE.txt': ''.join(hashlib.sha256(archive_bytes).hexdigest()+'  '+name+'\n'
                                     for name in (ARCHIVE, ZIP_ARCHIVE)).encode('ascii'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check committed artifacts without modifying files')
    args = parser.parse_args()
    artifacts = release_contents()
    if args.check:
        stale = [name for name, data in artifacts.items()
                 if not (ROOT/name).is_file() or (ROOT/name).read_bytes() != data]
        if stale:
            raise SystemExit('Release artifacts are missing or stale: '+', '.join(stale))
        print('Release artifacts match the complete source tree:', VERSION)
    else:
        # Git stores these source files with LF on every platform. Normalize
        # generator output before hashing so Windows and Linux verify alike.
        for name, data in source_contents().items():
            if (ROOT/name).read_bytes() != data:
                (ROOT/name).write_bytes(data)
        for name, data in artifacts.items():
            (ROOT/name).write_bytes(data)
        print('Built English release:', ARCHIVE)


if __name__ == '__main__':
    main()
