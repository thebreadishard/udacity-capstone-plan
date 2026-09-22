"""Keep ARCHITECTURE.md's mermaid fences identical to the sheet files (22 September 2026).

Every section heading names its sheet in backticks (`40_data_creation_labels.mmd`); the fence that follows must be that file's
content verbatim. Run after editing a sheet:  python tools/sync_architecture_md.py [--check]
--check exits 1 if any fence differs (for the pre-commit hook / CI) without writing.
"""
import re
import sys
from pathlib import Path

ARCH = Path(__file__).resolve().parents[1] / "GoalGathering" / "architecture"
MD = ARCH / "ARCHITECTURE.md"


def main(check=False):
    text = MD.read_text(encoding="utf-8")
    out, pos, changed = [], 0, []
    for m in re.finditer(r"^## .*?`([0-9]{2}_[A-Za-z0-9_]+\.mmd)`.*?$\n\n```mermaid\n(.*?)\n```", text, flags=re.S | re.M):
        name, body = m.group(1), m.group(2)
        src = (ARCH / name).read_text(encoding="utf-8").rstrip("\n")
        if src != body:
            changed.append(name)
        out.append(text[pos:m.start(2)])
        out.append(src)
        pos = m.end(2)
    out.append(text[pos:])
    new = "".join(out)
    if check:
        print("fences differ from the sheets:" if changed else "fences identical to the sheets", changed)
        return 1 if changed else 0
    if changed:
        MD.write_text(new, encoding="utf-8", newline="\n")
    print("synced", changed if changed else "(nothing to do)")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
