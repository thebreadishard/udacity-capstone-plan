"""Did an executed notebook run completely? (18 Oct 2026, the standalone check of tools/make_module_repo.sh.)

A notebook counts as run when every code cell carries an execution count and no cell holds an error output. Both are needed: a build that
stops early leaves an unexecuted notebook with zero errors (module 07's rebuild of 17 Oct did exactly that).

    python tools/notebook_ran.py <executed.ipynb>     → exit 0 and one line 'ran: …', or exit 1 and the reason
"""
import json
import sys
from pathlib import Path


def check(path: Path) -> list[str]:
    """Problems of the executed notebook: unexecuted code cells and error outputs, by cell index."""
    with open(path, encoding="utf-8") as f:
        cells = json.load(f)["cells"]
    problems = []
    for i, cell in enumerate(cells):
        if cell.get("cell_type") != "code" or not "".join(cell.get("source", [])).strip():
            continue
        if cell.get("execution_count") is None:
            problems.append(f"cell {i} not executed")
        problems += [f"cell {i}: {o.get('ename')}: {o.get('evalue', '')[:120]}" for o in cell.get("outputs", []) if o.get("output_type") == "error"]
    return problems


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python tools/notebook_ran.py <executed.ipynb>", file=sys.stderr)
        return 2
    problems = check(Path(args[0]))
    if problems:
        print("NOT RUN: " + "; ".join(problems[:5]))
        return 1
    print(f"ran: {args[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
