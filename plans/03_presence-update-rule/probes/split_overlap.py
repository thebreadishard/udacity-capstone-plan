#!/usr/bin/env python3
"""Q4 / Q5. Print 0 if two hash lists are disjoint.

Each file is one hash per line (hex SHA256 or any token). Blank lines
and # comments are ignored.

Q4: train hashes vs test hashes.
Q5: H2 train hashes vs water geometry hashes.

  python split_overlap.py train.txt test.txt
  python split_overlap.py train.txt water.txt --label q5
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cube_io import die_not_run, print_kv  # noqa: E402


def read_hashes(path: Path) -> set[str]:
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.add(s.split()[0])
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("left", nargs="?", default=None, help="train hash list")
    p.add_argument("right", nargs="?", default=None, help="test or water hash list")
    p.add_argument("--label", default="q4", help="q4 (time split) or q5 (no water in H2 train)")
    args = p.parse_args()
    if args.left is None or args.right is None:
        die_not_run("need two hash-list files; splits are cut after Q0")
    left_p = Path(args.left)
    right_p = Path(args.right)
    if not left_p.is_file() or not right_p.is_file():
        die_not_run(f"missing {left_p} or {right_p}")
    a = read_hashes(left_p)
    b = read_hashes(right_p)
    inter = a & b
    n_overlap = len(inter)
    print_kv(
        label=args.label,
        n_left=len(a),
        n_right=len(b),
        n_overlap=n_overlap,
        disjoint=int(n_overlap == 0),
        left=str(left_p),
        right=str(right_p),
    )
    print(n_overlap)
    raise SystemExit(0 if n_overlap == 0 else 1)


if __name__ == "__main__":
    main()
