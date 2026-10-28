#!/usr/bin/env python3
"""Install the packaged skill locally for Codex/compatible Agent Skills hosts."""
from pathlib import Path
import argparse, shutil, sys

HERE=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description='Install God Prompt skill locally (requires user filesystem permissions)')
    mx=ap.add_mutually_exclusive_group(required=True)
    mx.add_argument('--user',action='store_true',help='Install to ~/.agents/skills/god-prompt')
    mx.add_argument('--repo',help='Install to <repository>/.agents/skills/god-prompt')
    ap.add_argument('--replace',action='store_true',help='Allow replacement of an existing skill folder')
    a=ap.parse_args()
    target=(Path.home()/'.agents'/'skills'/'god-prompt') if a.user else (Path(a.repo).expanduser().resolve()/'.agents'/'skills'/'god-prompt')
    if target.resolve()==HERE.resolve():raise SystemExit('Source is already the install target')
    if target.exists() and not a.replace:raise SystemExit(f'Already exists: {target}; use --replace explicitly')
    if not (HERE/'SKILL.md').is_file():raise SystemExit('Missing SKILL.md')
    if target.exists():shutil.rmtree(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(HERE,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git','output','.env','.env.*','*.key','*.secret','*.pem','*.log','*.skill','*.zip','SHA256_RELEASE.txt'))
    print('Installed:',target)
    print('Codex can detect skills automatically; if this one does not appear, restart the host.')
if __name__=='__main__':main()
