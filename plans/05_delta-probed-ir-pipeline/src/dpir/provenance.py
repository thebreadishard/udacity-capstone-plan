"""Provenance for result files: which code, which command, which machine, when.

Every result file written by tier-2 code ends with ``provenance_block()`` so that a number in a document can be traced
back to the commit and command that produced it (QUALITY_POLICY.md, "Evidence").
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from datetime import datetime, timezone


def git_state(cwd: str | None = None) -> dict[str, str]:
    """Commit hash and dirty flag of the repository containing ``cwd`` (or the current directory); empty if not in git."""
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=cwd, timeout=10).stdout.strip()
        if not head:
            return {}
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True, cwd=cwd, timeout=10).stdout.strip()
        return {"commit": head, "dirty": "yes" if dirty else "no"}
    except (OSError, subprocess.SubprocessError):
        return {}


def provenance() -> dict[str, str]:
    import numpy

    d = {"timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), "host": platform.node(),
         "python": sys.version.split()[0], "numpy": numpy.__version__, "command": " ".join([os.path.basename(sys.argv[0]), *sys.argv[1:]])}
    d.update(git_state(os.path.dirname(os.path.abspath(__file__))))
    return d


def provenance_block() -> str:
    """Markdown section with the provenance fields, one per line."""
    p = provenance()
    return "## Provenance\n\n" + "\n".join(f"- {k}: `{v}`" for k, v in p.items()) + "\n"
