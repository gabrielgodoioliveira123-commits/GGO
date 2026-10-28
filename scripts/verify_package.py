#!/usr/bin/env python3
"""Check release SHA-256 hashes; hashes are change detection, not a signature."""
from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parents[1]
listing=root/'SHA256SUMS'
if not listing.exists(): raise SystemExit('Missing SHA256SUMS')
errors=[]
for line in listing.read_text(encoding='utf-8').splitlines():
    if not line.strip():continue
    wanted,path=line.split('  ',1)
    p=root/path
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=wanted:
        errors.append(path)
if errors:
    print('FAILED:',errors);sys.exit(1)
print('Package hashes verified:',len(listing.read_text(encoding='utf-8').splitlines()))
