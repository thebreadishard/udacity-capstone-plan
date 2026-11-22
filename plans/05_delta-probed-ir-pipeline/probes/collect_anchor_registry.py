"""What probes/collect_anchor.sh asks of the corpus manifest and the anchor registry (stage 4).

    python probes/collect_anchor_registry.py name <molecule id>
        → the corpus manifest's name for the id; exit 1 when the manifest has no such row or no name
    python probes/collect_anchor_registry.py status <registered path, relative to the plan>
        → the entry's status (carried, experimental, …); exit 1 when the path is not registered or the registry's own check of the
          entry fails (the file changed since it was registered, a carried file whose own verdict is not VALID)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import anchor_registry as AR  # noqa: E402

MANIFEST = PLAN / "modules" / "05_support_predictor" / "corpus" / "manifest.csv"


def name_of(mol_id: str, manifest: Path = MANIFEST) -> str:
    """The manifest's name for the id; refused when the row or its name is missing."""
    with manifest.open(encoding="utf-8", newline="") as handle:
        names = [row["name"].strip() for row in csv.DictReader(handle) if row["id"] == mol_id]
    if len(names) != 1 or not names[0]:
        raise SystemExit(f"{mol_id}: {len(names)} manifest rows with a name in {manifest}")
    return names[0]


def status_of(path: str, entries: list[dict] | None = None, root: Path = PLAN) -> str:
    """The status of the entry registered under this path, after the registry's own check of it."""
    entries = AR.load() if entries is None else entries
    hits = [e for e in entries if e["path"] == Path(path).as_posix()]
    if len(hits) != 1:
        raise SystemExit(f"{path}: {len(hits)} registry entries")
    problems = AR.check_entry(hits[0], root)
    if problems:
        raise SystemExit("; ".join(problems))
    return hits[0]["status"]


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] not in ("name", "status"):
        raise SystemExit(__doc__)
    print(name_of(argv[1]) if argv[0] == "name" else status_of(argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
