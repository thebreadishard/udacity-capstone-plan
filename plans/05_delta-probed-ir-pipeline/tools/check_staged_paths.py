"""pre-commit path guard: refuse files that are run scratch or live run directories (QUALITY_POLICY.md, "Local hooks").

Usage (pre-commit passes the staged file names): python check_staged_paths.py <path> [<path> ...]
Exit 1 with the offending paths listed; exit 0 otherwise.
"""

import re
import sys

FORBIDDEN = [
    (re.compile(r"(^|/)psi4\.out$"), "psi4 scratch output"),
    (re.compile(r"\.out$"), "electronic-structure output file (75 MB benzene .out, 20 Sep 2026)"),
    (re.compile(r"(^|/)corpus/molecules/"), "live per-molecule run directory of the corpus factory"),
    (re.compile(r"(^|/)psi\.\d+\.clean$"), "psi4 scratch marker"),
    (re.compile(r"(^|/)timer\.dat$"), "psi4 timer file"),
    (re.compile(r"(^|/)corpus\.lock$"), "runner lock"),
]


def main(paths):
    bad = []
    for p in paths:
        q = p.replace("\\", "/")
        for rx, why in FORBIDDEN:
            if rx.search(q):
                bad.append(f"  {p}  ({why})")
                break
    if bad:
        print("refused by plans/05_delta-probed-ir-pipeline/tools/check_staged_paths.py:\n" + "\n".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
