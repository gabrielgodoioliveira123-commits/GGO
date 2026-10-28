#!/usr/bin/env python3
"""Install the packaged skill locally for Codex/compatible Agent Skills hosts."""
from pathlib import Path
import argparse, shutil, sys, uuid, stat
from package_integrity import read_verified

HERE=Path(__file__).resolve().parents[1]


def plain_target(target):
    for path in (target,*target.parents):
        if path.exists() or path.is_symlink():
            info=path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                raise ValueError('Installation target contains a link or Windows reparse point: '+str(path))


def install(source,target,replace=False):
    source=Path(source).resolve();target=Path(target).absolute()
    plain_target(target)
    if target.resolve()==source or source.is_relative_to(target.resolve()):
        raise ValueError('Installation target must not replace the source or its ancestor')
    if target.exists() and (not target.is_dir() or not replace):
        raise ValueError('Installation already exists; use --replace to preserve it as a backup and replace it')
    files=read_verified(source)
    if not files['SKILL.md'].startswith(b'---\nname: god-prompt\n'):
        raise ValueError('Source manifest is not the god-prompt skill')
    target.parent.mkdir(parents=True,exist_ok=True)
    stage=target.with_name('.god-prompt-install-'+uuid.uuid4().hex)
    backup=None
    try:
        stage.mkdir()
        for relative,data in files.items():
            destination=stage/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(data)
        if target.exists():
            backup=target.with_name('god-prompt.backup-'+uuid.uuid4().hex)
            target.replace(backup)
        try:stage.replace(target)
        except BaseException:
            if backup is not None:
                try:backup.replace(target)
                except OSError as error:raise RuntimeError('Restore failed; original installation is preserved at '+str(backup)) from error
            raise
    finally:
        if stage.exists() and stage.resolve().parent==target.parent.resolve():shutil.rmtree(stage)
    return backup

def main():
    ap=argparse.ArgumentParser(description='Install God Prompt skill locally (requires user filesystem permissions)')
    mx=ap.add_mutually_exclusive_group(required=True)
    mx.add_argument('--user',action='store_true',help='Install to ~/.agents/skills/god-prompt')
    mx.add_argument('--repo',help='Install to <repository>/.agents/skills/god-prompt')
    ap.add_argument('--replace',action='store_true',help='Allow replacement of an existing skill folder')
    a=ap.parse_args()
    target=(Path.home()/'.agents'/'skills'/'god-prompt') if a.user else (Path(a.repo).expanduser().resolve()/'.agents'/'skills'/'god-prompt')
    try:backup=install(HERE,target,a.replace)
    except (OSError,ValueError,UnicodeError,RuntimeError) as error:
        print('INSTALL FAILED:',error,file=sys.stderr);return 2
    print('Installed:',target)
    if backup is not None:print('Previous installation preserved:',backup)
    print('Codex can detect skills automatically; if this one does not appear, restart the host.')
    return 0
if __name__=='__main__':raise SystemExit(main())
