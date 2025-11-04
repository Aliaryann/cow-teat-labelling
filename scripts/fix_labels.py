#!/usr/bin/env python
import glob, os, sys
from pathlib import Path

# Remap 1->0, 2->1, 3->2, 4->3. Any 0 stays 0 (will warn). Lines with wrong length skipped.
# Usage: python scripts/fix_labels.py --root datasets/labels --in-place

import argparse

def process(root, dry_run=True):
    root_p = Path(root)
    if not root_p.exists():
        print(f"Root {root} does not exist", file=sys.stderr)
        sys.exit(1)
    mapping = {1:0, 2:1, 3:2, 4:3}
    total=0; changed=0; skipped=0; malformed=0; warnings=0
    for f in root_p.glob('*.txt'):
        lines_in = f.read_text().strip().splitlines()
        out_lines=[]; file_changed=False
        for ln in lines_in:
            if not ln.strip():
                continue
            parts = ln.split()
            if len(parts) != 5:
                malformed+=1
                continue
            try:
                cid = int(parts[0])
            except ValueError:
                malformed+=1
                continue
            if cid in mapping:
                new_cid = mapping[cid]
            elif cid == 0:
                new_cid = 0
                warnings+=1
            else:
                # unexpected class id; skip line
                skipped+=1
                continue
            if new_cid != cid:
                parts[0] = str(new_cid)
                file_changed=True
            out_lines.append(' '.join(parts))
            total+=1
        if file_changed and not dry_run:
            f.write_text('\n'.join(out_lines)+'\n')
            changed+=1
    print(f"Processed labels in {root}")
    print(f"Total valid lines kept: {total}")
    print(f"Files changed: {changed}")
    print(f"Malformed lines skipped: {malformed}")
    print(f"Unexpected class id lines skipped: {skipped}")
    if warnings:
        print(f"Warnings: {warnings} lines already had class id 0")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='datasets/labels')
    ap.add_argument('--apply', action='store_true', help='Actually modify files')
    args = ap.parse_args()
    process(args.root, dry_run=not args.apply)
