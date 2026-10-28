#!/usr/bin/env python3
"""Check release SHA-256 hashes; hashes are change detection, not a signature."""
from pathlib import Path
import argparse
from package_integrity import read_verified


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    try:
        files=read_verified(args.root)
    except (OSError,ValueError,UnicodeError) as error:
        print('PACKAGE INVALID:',error)
        return 1
    print('Package hashes verified:',len(files)-1)
    return 0


if __name__=='__main__':raise SystemExit(main())
