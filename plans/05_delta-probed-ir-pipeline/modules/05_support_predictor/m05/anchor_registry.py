"""Anchor registry (7 Oct 2026; the user: "kan het plan uitgevoerd worden zonder oude berekeningen te verliezen … en dat een berekening de 'beste' is?").

Every coupled-cluster Hessian the project has computed is one entry: molecule, file, level of theory, tier, kind, status, date, the checks it passed
and why it has its status. Nothing is deleted or overwritten: a better version is a new entry and the old one becomes `superseded`. Exactly one
entry per molecule may be `carried` — the best version we have — and every read that uses anchors (T3, the Atlas, training) takes the carried file
or refuses (`require_carried_anchor`, override `--allow-any-anchor`, named in the record). The anchors of one read must share one tier
(`require_one_tier`): chain 33 of 7 Oct mixed four cc-pVDZ blocks with one repaired block and its out-of-plane numbers moved both ways.

Statuses: `carried` (the best version, used by reads), `superseded` (valid, replaced by a better level; kept for comparison), `imaginary` (computed
correctly, not a minimum — the small-basis arene artefact), `invalid` (a known error; kept and labelled), `experimental` (valid but not yet judged).
Tiers: `TZ` (CCSD(T)/cc-pVTZ, or a composite that stands in for it: CC/DZ + [MP2/TZ − MP2/DZ] over the whole Hessian), `DZ` (CCSD(T)/cc-pVDZ),
`DZ+oop` (CC/DZ with only the out-of-plane block corrected — test 3).

    python m05/anchor_registry.py --check            # every entry: file present, hash unchanged, keys, status rules; one carried per molecule
    python m05/anchor_registry.py --write-overview   # modules/ANCHORS.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[3]
STATUS_FILE = PLAN / "modules" / "05_support_predictor" / "out" / "ANCHORS_STATUS.json"
OVERVIEW = PLAN / "modules" / "ANCHORS.md"
STATUSES = ("carried", "superseded", "imaginary", "invalid", "experimental")
TIERS = ("TZ", "DZ", "DZ+oop")
KINDS = ("full", "composite", "composite-oop")
FIELDS = ("mol_id", "name", "path", "level", "tier", "kind", "status", "date", "sha16", "checks", "note")


def sha16(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def load(status_file: Path = STATUS_FILE) -> list[dict]:
    if not status_file.exists():
        raise SystemExit(f"anchor registry missing: {status_file}")
    return json.loads(status_file.read_text(encoding="utf-8"))["anchors"]


def save(entries: list[dict], status_file: Path = STATUS_FILE) -> None:
    status_file.write_text(json.dumps({"about": "anchor registry — m05/anchor_registry.py; one carried entry per molecule", "anchors": entries},
                                      indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def check_entry(e: dict, root: Path = PLAN) -> list[str]:
    """Problems of one entry (empty list = fine)."""
    p = []
    missing = [f for f in FIELDS if f not in e]
    if missing:
        return [f"{e.get('path', '?')}: fields missing {missing}"]
    if e["status"] not in STATUSES:
        p.append(f"{e['path']}: status {e['status']!r} not in {STATUSES}")
    if e["tier"] not in TIERS:
        p.append(f"{e['path']}: tier {e['tier']!r} not in {TIERS}")
    if e["kind"] not in KINDS:
        p.append(f"{e['path']}: kind {e['kind']!r} not in {KINDS}")
    f = root / e["path"]
    if not f.exists():
        return p + [f"{e['path']}: file missing"]
    if sha16(f) != e["sha16"]:
        p.append(f"{e['path']}: file changed since it was registered (sha {sha16(f)} vs {e['sha16']})")
    if e["status"] == "carried":
        z = np.load(f)
        if not {"H_raw", "H_projected"} <= set(z.files):
            p.append(f"{e['path']}: carried but H_raw/H_projected missing")
        st = str(z["status"]) if "status" in z.files else "VALID"
        if st != "VALID" or "IMAGINARY" in f.name or "INVALID" in f.name:
            p.append(f"{e['path']}: carried but the file's own verdict is {st} ({f.name})")
    return p


def check_all(entries: list[dict], root: Path = PLAN) -> list[str]:
    problems = [q for e in entries for q in check_entry(e, root)]
    carried = {}
    for e in entries:
        if e.get("status") == "carried":
            carried.setdefault(e["mol_id"], []).append(e["path"])
    problems += [f"{m}: {len(v)} carried entries {v} — exactly one allowed" for m, v in carried.items() if len(v) > 1]
    paths = [e.get("path") for e in entries]
    problems += [f"{q}: registered twice" for q in {x for x in paths if paths.count(x) > 1}]
    return problems


def carried(mol_id: str, entries: list[dict] | None = None) -> dict | None:
    for e in entries if entries is not None else load():
        if e["mol_id"] == mol_id and e["status"] == "carried":
            return e
    return None


def _rel(path: Path, root: Path) -> str:
    p = Path(path).resolve()
    try:
        return p.relative_to(root.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def require_carried_anchor(mol_id: str, path: Path, allow: bool = False, entries: list[dict] | None = None, root: Path = PLAN) -> dict | None:
    """The file must be the molecule's carried entry (decision of 7 Oct 2026); `allow` lets another registered or unregistered file through and
    returns None so the caller can name it. Refuses a file whose content changed since it was registered."""
    entries = entries if entries is not None else load()
    rel = _rel(path, root)
    hit = next((e for e in entries if e["path"] == rel), None)
    best = carried(mol_id, entries)
    if hit is not None and hit["mol_id"] != mol_id:
        raise SystemExit(f"{rel} is registered for {hit['mol_id']}, not {mol_id}")
    if hit is not None and hit["status"] == "carried":
        if sha16(root / rel) != hit["sha16"]:
            raise SystemExit(f"{rel}: carried anchor changed since it was registered — re-register it")
        return hit
    if allow:
        return None
    why = f"registered as {hit['status']}" if hit else "not registered"
    raise SystemExit(f"anchor {mol_id}: {rel} is {why}; the carried version is "
                     + (f"{best['path']} ({best['level']})" if best else "none") + " — pass --allow-any-anchor to use it anyway (named in the record)")


def require_one_tier(found: dict[str, dict | None], allow: bool = False) -> str | None:
    """All anchors of one read on one tier; returns the tier (None when an anchor is unregistered and allowed through)."""
    tiers = {e["tier"] for e in found.values() if e is not None}
    if len(tiers) > 1 and not allow:
        raise SystemExit(f"anchors on several tiers {sorted(tiers)}: " + ", ".join(f"{m} {e['tier']}" for m, e in found.items() if e)
                         + " — one read uses one tier (chain 33, 7 Oct 2026); pass --allow-mixed-tiers to override")
    return tiers.pop() if len(tiers) == 1 and all(found.values()) else None


def register(entry: dict, promote: bool = False, entries: list[dict] | None = None, root: Path = PLAN, status_file: Path = STATUS_FILE) -> list[dict]:
    """Add one entry (sha computed here). promote=True: the entry becomes carried and the molecule's previous carried entry superseded, with a note.
    Refuses a path that is already registered and anything that breaks check_all; writes the status file only when everything passes."""
    entries = [dict(e) for e in (entries if entries is not None else load(status_file))]
    rel = _rel(root / entry["path"], root) if not Path(entry["path"]).is_absolute() else _rel(Path(entry["path"]), root)
    if any(e["path"] == rel for e in entries):
        raise SystemExit(f"{rel} is already registered")
    new = {**entry, "path": rel, "sha16": sha16(root / rel)}
    if promote:
        new["status"] = "carried"
        for e in entries:
            if e["mol_id"] == new["mol_id"] and e["status"] == "carried":
                e["status"] = "superseded"
                e["note"] = f"{e['note']}; superseded {new['date']} by {rel} ({new['level']})"
    entries.append(new)
    problems = check_all(entries, root)
    if problems:
        raise SystemExit("registry not written: " + "; ".join(problems))
    save(entries, status_file)
    return entries


def render_overview(entries: list[dict]) -> str:
    out = ["# Anchors — every coupled-cluster Hessian of the project and which one is used", "",
           "Generated by `modules/05_support_predictor/m05/anchor_registry.py --write-overview` from `modules/05_support_predictor/out/ANCHORS_STATUS.json`. "
           "Nothing is deleted: a better version is a new row and the old one becomes *superseded*. Exactly one *carried* row per molecule; reads use it "
           "or refuse. One read uses one tier.", ""]
    for mol in sorted({e["mol_id"] for e in entries}, key=lambda m: next(e["name"] for e in entries if e["mol_id"] == m)):
        rows = sorted((e for e in entries if e["mol_id"] == mol), key=lambda e: (e["status"] != "carried", e["date"]), reverse=False)
        out += [f"## {rows[0]['name']} ({mol})", "", "| status | level | tier | date | file | checks | note |", "|---|---|---|---|---|---|---|"]
        for e in rows:
            st = f"**{e['status']}**" if e["status"] == "carried" else e["status"]
            out.append(f"| {st} | {e['level']} | {e['tier']} | {e['date']} | `{e['path']}` | {e['checks']} | {e['note']} |")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write-overview", action="store_true")
    ap.add_argument("--register", metavar="PATH", help="add PATH as a new entry (with --mol, --name, --level, --tier, --kind, --status, --date, --checks, --note)")
    ap.add_argument("--promote", action="store_true", help="with --register: the new entry becomes carried, the previous carried one superseded")
    for f in ("mol", "name", "level", "tier", "kind", "status", "date", "checks", "note"):
        ap.add_argument(f"--{f}", default="experimental" if f == "status" else "—")
    a = ap.parse_args(argv)
    if a.register:
        register(dict(mol_id=a.mol, name=a.name, path=a.register, level=a.level, tier=a.tier, kind=a.kind, status=a.status, date=a.date,
                      checks=a.checks, note=a.note), promote=a.promote)
        print(f"registered {a.register} for {a.mol} ({'carried' if a.promote else a.status})")
    entries = load()
    problems = check_all(entries)
    for q in problems:
        print("PROBLEM:", q)
    if a.write_overview:
        OVERVIEW.write_text(render_overview(entries) + "\n", encoding="utf-8")
        print(f"wrote {OVERVIEW.relative_to(PLAN)}")
    n_c = sum(e["status"] == "carried" for e in entries)
    print(f"{len(entries)} anchor entries, {n_c} carried, {len(problems)} problems")
    return 1 if (a.check and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
