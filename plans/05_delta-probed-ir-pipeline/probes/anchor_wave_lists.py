"""Split the anchor plan's molecules over rented anchor servers (21 Nov 2026; the user rented five CPX62s: 'Servers gehuurd. Maak nieuwe ankers.').

The plan is `out/anchor_plan/count_<n>.json` (`probes/anchor_plan.py count`): per ring context, the cheapest neutral molecules. Here:

- a molecule that already has a carried anchor in the registry (`out/ANCHORS_STATUS.json`) is left out — it is not computed twice;
- a molecule an earlier wave dealt to a server (`--earlier <that wave's output folder>`, repeatable) is left out too: it is being
  computed, or waits in that server's list, and has no carried anchor yet;
- a molecule is ready only when its manifest row is `done` and its corpus geometry exists (`corpus/molecules/<id>/geometry.json`, the
  B3LYP/6-31G* minimum every label is computed at): a geometry left by an interrupted DFT run is not a finished one. The others are
  listed under 'needs its DFT row first' and in `needs_dft.txt`, never guessed;
- the ready molecules are dealt largest first (by the plan's own hour rule, `anchor_plan.anchor_hours`) to the server with the fewest hours
  so far, which brings the servers' totals close; then each server's list is put cheapest first, so every server still begins with its
  cheapest molecules. The hours are the rule's, which prices symmetric molecules high.

Output, per server, the folder `<out>/<host>/` with `wave.txt` in the format `probes/anchor_wave.sh` reads
(`name|geometry|workers|threads|mem_mb`, the geometry under `/root/dpir/geoms/<id>/`) and `geoms/<id>/geometry.json`; beside them `plan.md`
and `needs_dft.txt`. The folder is built beside the target and renamed into place at the end, so a failure leaves no half list; an existing
output folder is refused, so a list a server is already working on is never rewritten. Each `<out>/<host>/` is copied to `/root/dpir/`.

    python probes/anchor_wave_lists.py --hosts anc1,anc2,anc3,anc4,anc5 --out probes/results_m1/anchor_waves_2026-11-21
    python probes/anchor_wave_lists.py --hosts … --out <wave 2's folder> --earlier probes/results_m1/anchor_waves_2026-11-21
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import anchor_plan as A

PLAN_FILE = A.OUT / "count_n167.json"
REGISTRY = A.M05 / "out" / "ANCHORS_STATUS.json"
REMOTE_GEOMS = "/root/dpir/geoms"
WORKERS, THREADS, MEM_MB = 2, 8, 10000      # two partial runs of 8 threads: the CPX62 setting anchor set three measured (12 Oct 2026)


@dataclass(frozen=True)
class Candidate:
    mol_id: str
    context: str
    n_atoms: int
    basis_functions: int
    hours: float


def carried_ids(registry: Path = REGISTRY) -> set[str]:
    """Molecules with a carried anchor."""
    entries = json.loads(registry.read_text(encoding="utf-8"))["anchors"]
    return {e["mol_id"] for e in entries if e["status"] == "carried"}


def earlier_wave_ids(folders: list[Path]) -> set[str]:
    """Molecules an earlier wave dealt to a server: the first field of every line of `<folder>/<host>/wave.txt`. A folder without
    such a list is refused, so that a mistyped path does not read as 'nothing was dealt'."""
    ids: set[str] = set()
    for folder in folders:
        waves = sorted(folder.glob("*/wave.txt"))
        if not waves:
            raise SystemExit(f"--earlier {folder}: no <host>/wave.txt in it")
        for wave in waves:
            ids.update(line.split("|", 1)[0] for line in wave.read_text(encoding="utf-8").splitlines() if line.strip())
    return ids


def cheapest_first(items: list[Candidate]) -> list[Candidate]:
    """Rule hours ascending; ties: fewer atoms, then the id."""
    return sorted(items, key=lambda c: (c.hours, c.n_atoms, c.mol_id))


def candidates(plan: dict, smiles_of: dict[str, str]) -> list[Candidate]:
    """Every molecule of the plan with its rule hours, cheapest first; a plan id the corpus rows do not hold is refused by name."""
    missing = sorted(i for ids in plan["chosen"].values() for i in ids if i not in smiles_of)
    if missing:
        raise SystemExit(f"{len(missing)} plan ids are not among the corpus rows in the domain (manifest changed since the plan?): {missing}")
    out = []
    for context, ids in plan["chosen"].items():
        for mol_id in ids:
            smiles = smiles_of[mol_id]
            n_atoms = A.Chem.AddHs(A.Chem.MolFromSmiles(smiles)).GetNumAtoms()
            n_functions = A.basis_functions(smiles)
            out.append(Candidate(mol_id, context, n_atoms, n_functions, A.anchor_hours(n_atoms, n_functions)))
    return cheapest_first(out)


def deal(items: list[Candidate], hosts: list[str]) -> dict[str, list[Candidate]]:
    """Largest first to the host with the fewest hours so far (ties: the host listed first); each host's list then cheapest first."""
    if not hosts:
        raise ValueError("no hosts")
    lists: dict[str, list[Candidate]] = {h: [] for h in hosts}
    load = dict.fromkeys(hosts, 0.0)
    for c in reversed(cheapest_first(items)):
        host = min(hosts, key=lambda h: (load[h], hosts.index(h)))
        lists[host].append(c)
        load[host] += c.hours
    return {h: cheapest_first(items_h) for h, items_h in lists.items()}


def wave_line(c: Candidate) -> str:
    return f"{c.mol_id}|{REMOTE_GEOMS}/{c.mol_id}/geometry.json|{WORKERS}|{THREADS}|{MEM_MB}"


def report(lists: dict[str, list[Candidate]], skipped_carried: list[str], needs_dft: list[Candidate],
           in_earlier: list[str] | None = None) -> str:
    lines = ["# Anchor waves — molecules per server", "",
             f"Plan: `{PLAN_FILE.relative_to(A.PLAN).as_posix()}`. Hours by `anchor_plan.anchor_hours` (CPX62, plane symmetry only).", "",
             "| server | molecules | rule hours | first | last |", "|---|---|---|---|---|"]
    for host, items in lists.items():
        if items:
            lines.append(f"| {host} | {len(items)} | {sum(c.hours for c in items):,.0f} | {items[0].mol_id} | {items[-1].mol_id} |")
        else:
            lines.append(f"| {host} | 0 | 0 | — | — |")
    lines += ["", f"Left out, carried anchor already: {len(skipped_carried)} ({', '.join(skipped_carried) or 'none'}).",
              f"Left out, dealt in an earlier wave and not carried yet: {len(in_earlier or [])} "
              f"({', '.join(in_earlier or []) or 'none'}).",
              f"Needs its DFT row first (no corpus geometry): {len(needs_dft)}, rule hours {sum(c.hours for c in needs_dft):,.0f}."]
    return "\n".join(lines) + "\n"


def write_lists(out: Path, lists: dict[str, list[Candidate]], corpus_molecules: Path) -> None:
    for host, items in lists.items():
        folder = out / host
        (folder / "geoms").mkdir(parents=True)
        for c in items:
            target = folder / "geoms" / c.mol_id
            target.mkdir()
            shutil.copy2(corpus_molecules / c.mol_id / "geometry.json", target / "geometry.json")
        (folder / "wave.txt").write_text("".join(wave_line(c) + "\n" for c in items), encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--hosts", required=True, help="comma-separated host names from tools/hosts.tsv")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--plan", type=Path, default=PLAN_FILE)
    ap.add_argument("--earlier", type=Path, action="append", default=[],
                    help="the output folder of an earlier wave (repeatable): its molecules are not dealt again")
    args = ap.parse_args(argv)
    hosts = [h for h in args.hosts.split(",") if h]
    if len(set(hosts)) != len(hosts):
        raise SystemExit(f"a host is named twice: {hosts}")
    if args.out.exists():
        raise SystemExit(f"{args.out} exists — a list a server may be working on is not rewritten")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    rows = A.corpus_cells()
    carried = carried_ids()
    earlier = earlier_wave_ids(args.earlier)
    corpus_molecules = A.CORPUS / "molecules"
    all_candidates = candidates(plan, {i: r["smiles"] for i, r in rows.items()})
    skipped = [c.mol_id for c in all_candidates if c.mol_id in carried]
    in_earlier = [c.mol_id for c in all_candidates if c.mol_id in earlier and c.mol_id not in carried]
    open_ = [c for c in all_candidates if c.mol_id not in carried and c.mol_id not in earlier]
    ready = [c for c in open_ if is_ready(rows[c.mol_id]["status"], corpus_molecules / c.mol_id)]
    ready_ids = {c.mol_id for c in ready}
    needs_dft = [c for c in open_ if c.mol_id not in ready_ids]
    lists = deal(ready, hosts)
    text = report(lists, skipped, needs_dft, in_earlier)
    staging = args.out.with_name(args.out.name + ".partial")
    if staging.exists():
        raise SystemExit(f"{staging} exists — a failed earlier run left it; look at it and remove it by hand")
    staging.mkdir(parents=True)
    write_lists(staging, lists, corpus_molecules)
    (staging / "needs_dft.txt").write_text("".join(c.mol_id + "\n" for c in needs_dft), encoding="utf-8", newline="\n")
    (staging / "plan.md").write_text(text, encoding="utf-8", newline="\n")
    staging.rename(args.out)
    sys.stdout.write(text)
    return 0


def is_ready(manifest_status: str, molecule_folder: Path) -> bool:
    """A finished DFT row: manifest status done and the geometry on disk."""
    return manifest_status == "done" and (molecule_folder / "geometry.json").exists()


if __name__ == "__main__":
    sys.exit(main())
