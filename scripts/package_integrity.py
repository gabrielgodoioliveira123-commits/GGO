"""Strict, non-executing verification of a complete God Prompt source package."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat

REQUIRED_FILES=frozenset({
    'SKILL.md','README.md','LICENSE','AUTHORS','NOTICE','CITATION.cff',
    'agents/openai.yaml','engine/god_prompt.apl','engine/specialization_contracts.apl',
    'references/catalog.json','examples/request.json','examples/request_small.json',
    'scripts/god_prompt.py','scripts/install_skill.py','scripts/validate_skill.py',
    'scripts/verify_package.py','scripts/build_release.py','scripts/package_integrity.py',
    'tests/test_god_prompt.py',
    '.gitattributes','.gitignore','GITHUB_SETUP.md','CHANGELOG.md','SECURITY.md','CONTRIBUTING.md',
    'references/architecture.md','references/connectors.md','references/page-equivalence.md','references/quality.md',
    'scripts/make_catalog.py','scripts/build_apl_instructions.py',
    '.github/workflows/ci.yml','tests/test_release_packaging.py',
    'references/troubleshooting.md','examples/request_quickstart.json','examples/page_001.txt',
    'tests/test_installation_integrity.py','tests/test_runtime_regressions.py','tests/test_provider_fixtures.py','tests/test_cli_workflow.py',
})


def canonical_path(value):
    if (not isinstance(value,str) or not value or value=='.' or '\\' in value or ':' in value
            or '\x00' in value or '\n' in value or '\r' in value):
        raise ValueError('Package paths must be canonical relative POSIX paths')
    path=PurePosixPath(value)
    if path.is_absolute() or path.as_posix()!=value or any(p in ('.','..') for p in path.parts):
        raise ValueError('Package path escapes or is not canonical: '+value)
    return value


def read_file(root,relative):
    root=Path(root).resolve()
    path=root/canonical_path(relative)
    for part in (path,*path.parents):
        if part==root:break
        info=part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
            raise ValueError('Linked package paths are not allowed: '+relative)
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError('Package source is not a contained regular file: '+relative)
    return path.read_bytes()


def read_verified(root):
    """Return verified immutable bytes; installers copy exactly this inventory."""
    listing=read_file(root,'SHA256SUMS')
    raw_manifest=read_file(root,'package_manifest.json')
    try:manifest=json.loads(raw_manifest.decode('utf-8-sig'))
    except (ValueError,UnicodeError) as error:raise ValueError('Invalid package_manifest.json') from error
    if not isinstance(manifest,dict) or not isinstance(manifest.get('files_excluding_checksum_and_manifest'),list):
        raise ValueError('Package manifest must declare a source file inventory')
    inventory=manifest['files_excluding_checksum_and_manifest']
    folded=set()
    for path in inventory:
        canonical_path(path)
        if path.casefold() in folded:raise ValueError('Duplicate package inventory path: '+path)
        folded.add(path.casefold())
    expected=set(inventory)|{'package_manifest.json'}
    if {'SHA256SUMS','package_manifest.json'}&set(inventory):raise ValueError('Source inventory includes a generated manifest or checksum listing')
    if not REQUIRED_FILES.issubset(expected):raise ValueError('Package inventory is incomplete')
    try:lines=listing.decode('utf-8').splitlines()
    except UnicodeError as error:raise ValueError('SHA256SUMS must be UTF-8') from error
    checks={}
    for line in lines:
        if not line.strip():continue
        match=re.fullmatch(r'([0-9a-fA-F]{64})  (.+)',line)
        if match is None:raise ValueError('Malformed SHA256SUMS line')
        digest,relative=match.groups();canonical_path(relative)
        if relative in checks:raise ValueError('Duplicate checksum path: '+relative)
        checks[relative]=digest.lower()
    if not checks or set(checks)!=expected:raise ValueError('Checksum inventory does not match the complete package manifest')
    result={}
    for relative,digest in checks.items():
        data=raw_manifest if relative=='package_manifest.json' else read_file(root,relative)
        if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Package SHA-256 mismatch: '+relative)
        result[relative]=data
    result['SHA256SUMS']=listing
    return result
