"""Pre-commit hook for shell scripts under plan 05 (code-quality review of 28 Sep 2026: ten chain scripts ran without `set -e`, so a failed
step let the chain continue): every staged .sh must parse (`bash -n`) and must either enable fail-fast (`set -e`, `set -euo pipefail`, …) in its
first 30 lines or state why not on a line `# no-set-e: <reason>` (polling and diagnostic scripts, where an empty grep/pgrep is normal).

    python tools/check_shell.py a.sh b.sh …      → exit 1 with one line per offending file
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

SET_E = re.compile(r"^\s*set\s+-[a-zA-Z]*e[a-zA-Z]*\b|^\s*set\s+-o\s+errexit\b", re.M)
REASON = re.compile(r"^#\s*no-set-e:\s*\S", re.M)


def check(path: Path, bash: str | None) -> list[str]:
    problems = []
    text = path.read_text(encoding="utf-8", errors="replace")
    head = "\n".join(text.split("\n")[:30])
    if not SET_E.search(head) and not REASON.search(text):
        problems.append(f"{path}: no `set -e` in the first 30 lines and no `# no-set-e: <reason>` line")
    if bash:
        r = subprocess.run([bash, "-n", str(path)], capture_output=True, text=True, check=False)
        if r.returncode:
            problems.append(f"{path}: bash -n failed: {r.stderr.strip()[:200]}")
    return problems


def main(argv: list[str]) -> int:
    bash = shutil.which("bash")
    problems = [p for f in argv for p in check(Path(f), bash)]
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
