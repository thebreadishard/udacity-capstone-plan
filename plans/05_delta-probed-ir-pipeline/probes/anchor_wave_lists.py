"""Split the anchor plan's molecules over rented anchor servers (21 Nov 2026; the user rented five CPX62s: 'Servers gehuurd. Maak nieuwe ankers.').

The plan is `out/anchor_plan/count_<n>.json` (`probes/anchor_plan.py count`): per ring context, the cheapest neutral molecules. Here:

- a molecule that already has a carried anchor in the registry (`out/ANCHORS_STATUS.json`) is left out — it is not computed twice;
- a molecule an earlier wave dealt to a server (`--earlier <that wave's output folder>`, repeatable) is left out too: it is being
  computed, waits in that server's list, or ended there without a carried anchor — the report gives the registry's status beside
  such a molecule, and it is dealt again only through a list of its own. An earlier id that this plan does not hold is refused;
- a molecule is ready only when its manifest row is `done` and its corpus geometry exists (`corpus/molecules/<id>/geometry.json`, the
  B3LYP/6-31G* minimum every label is computed at): a geometry left by an interrupted DFT run is not a finished one. The others are
  listed under 'needs its DFT row first' and in `needs_dft.txt`, never guessed;
- the ready molecules are dealt largest first (by the plan's own hour rule, `anchor_plan.anchor_hours`) to the server with the fewest hours
  so far, which brings the servers' totals close; then each server's list is put cheapest first, so every server still begins with its
  cheapest molecules. The hours are the rule's, which prices symmetric molecules high.

Output, per server, the folder `<out>/<host>/` with `wave.txt` in the format `probes/anchor_wave.sh` reads
(`name|geometry|workers|threads|mem_mb`, the geometry under `/root/dpir/geoms/<id>/`) and `geoms/<id>/geometry.json`; beside them `plan.md`
and `needs_dft.txt`. The folder is built beside the target and renamed into place at the end, so a failure leaves no half list; an existing
output folder is refused, so a list a server is already working on is never rewritten. Each `<out>/<host>/` is copied to `/root/dpir/`,
where a running wave reads its own list: a later wave therefore takes a list name of its own (`--list-name wave2.txt`), and the name
of an earlier wave's list is refused. The dealing starts every server at zero hours: what a server still has to do of an earlier
wave is not counted.
With `--home <a DFT batch's folder>` nothing is dealt by hours: every molecule goes to the server whose `<folder>/<host>/ids.txt`
lists it — the server that optimised it and computes its MP2 rows, so that `probes/collect_anchor.sh <host> <id>` finds the CC run
and the rows together. A molecule no such list holds is refused.

    python probes/anchor_wave_lists.py --hosts anc1,anc2,anc3,anc4,anc5 --out probes/results_m1/anchor_waves_2026-11-21
    python probes/anchor_wave_lists.py --hosts … --out <wave 2's folder> --earlier probes/results_m1/anchor_waves_2026-11-21 \
        --list-name wave2.txt
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import anchor_plan as A

PLAN_FILE = A.OUT / "count_n167.json"
REGISTRY = A.M05 / "out" / "ANCHORS_STATUS.json"
REMOTE_GEOMS = "/root/dpir/geoms"
LIST_NAME = "wave.txt"
LIST_NAME_PATTERN = re.compile(r"wave[A-Za-z0-9_-]*\.txt")
WORKERS, THREADS, MEM_MB = 2, 8, 10000      # two partial runs of 8 threads: the CPX62 setting anchor set three measured (12 Oct 2026)


@dataclass(frozen=True)
class Candidate:
    mol_id: str
    context: str
    n_atoms: int
    basis_functions: int
    hours: float


def registry_statuses(registry: Path = REGISTRY) -> dict[str, list[str]]:
    """Every status the anchor registry holds per molecule, in the registry's order."""
    out: dict[str, list[str]] = {}
    for entry in json.loads(registry.read_text(encoding="utf-8"))["anchors"]:
        out.setdefault(entry["mol_id"], []).append(entry["status"])
    return out


def earlier_lists(folders: list[Path]) -> list[Path]:
    """The wave lists of earlier waves: every `<folder>/<host>/wave*.txt`. A folder without one is refused, so that a mistyped path
    does not read as 'nothing was dealt', and so is a `.partial` folder: what a failed run left is not a dealt wave."""
    found: list[Path] = []
    for folder in folders:
        if folder.name.endswith(".partial"):
            raise SystemExit(f"--earlier {folder}: a staging folder of a run that did not finish, not a dealt wave")
        lists = sorted(folder.glob("*/wave*.txt"))
        odd = [p.as_posix() for p in lists if not LIST_NAME_PATTERN.fullmatch(p.name)]
        if odd:
            raise SystemExit(f"--earlier {folder}: not the name of a wave list, so its molecules would be dealt again — rename or "
                             f"remove: {odd}")
        if not lists:
            raise SystemExit(f"--earlier {folder}: no <host>/wave*.txt in it")
        found += lists
    return found


def wave_ids(lists: list[Path]) -> set[str]:
    """The molecules of wave lists: the first field of every line."""
    return {line.split("|", 1)[0] for wave in lists for line in wave.read_text(encoding="utf-8").splitlines() if line.strip()}


@dataclass(frozen=True)
class Partition:
    """The plan's molecules by what happens to them in this wave."""

    carried: list[str]
    in_earlier: list[str]
    ready: list[Candidate]
    needs_dft: list[Candidate]


def partition(all_candidates: list[Candidate], carried: set[str], earlier: set[str], ready_of: Callable[[Candidate], bool]) -> Partition:
    """Carried molecules and those an earlier wave holds are left out (a carried one counts as carried only); the rest is ready or
    needs its DFT row. An earlier id the plan does not hold is refused by name: another plan's wave, or a list that was edited."""
    unknown = sorted(earlier - {c.mol_id for c in all_candidates})
    if unknown:
        raise SystemExit(f"{len(unknown)} ids of an earlier wave are not in this plan (another plan's wave, or an edited list): {unknown}")
    open_ = [c for c in all_candidates if c.mol_id not in carried and c.mol_id not in earlier]
    ready = [c for c in open_ if ready_of(c)]
    ready_ids = {c.mol_id for c in ready}
    return Partition(carried=[c.mol_id for c in all_candidates if c.mol_id in carried],
                     in_earlier=[c.mol_id for c in all_candidates if c.mol_id in earlier and c.mol_id not in carried],
                     ready=ready, needs_dft=[c for c in open_ if c.mol_id not in ready_ids])


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


def home_hosts(folder: Path, hosts: list[str]) -> dict[str, str]:
    """Molecule → the host whose `<folder>/<host>/ids.txt` lists it (first field of a line; `#` lines and empty lines skipped).
    A host without that file and a molecule listed for two hosts are refused."""
    homes: dict[str, str] = {}
    for host in hosts:
        ids = folder / host / "ids.txt"
        if not ids.is_file():
            raise SystemExit(f"--home {folder}: no {host}/ids.txt in it")
        for line in ids.read_text(encoding="utf-8").splitlines():
            mol_id = line.split("|", 1)[0].strip()
            if not mol_id or mol_id.startswith("#"):
                continue
            if mol_id in homes:
                raise SystemExit(f"--home {folder}: {mol_id} is listed for {homes[mol_id]} and for {host}")
            homes[mol_id] = host
    return homes


def stay_home(items: list[Candidate], hosts: list[str], homes: dict[str, str]) -> dict[str, list[Candidate]]:
    """Every molecule on its home host, each host's list cheapest first; a molecule without a home is refused by name."""
    homeless = sorted(c.mol_id for c in items if c.mol_id not in homes)
    if homeless:
        raise SystemExit(f"{len(homeless)} molecules are in no host's ids.txt of --home, so no server holds their MP2 rows: {homeless}")
    return {h: [c for c in cheapest_first(items) if homes[c.mol_id] == h] for h in hosts}


def wave_line(c: Candidate) -> str:
    return f"{c.mol_id}|{REMOTE_GEOMS}/{c.mol_id}/geometry.json|{WORKERS}|{THREADS}|{MEM_MB}"


def report(lists: dict[str, list[Candidate]], part: Partition, statuses: dict[str, list[str]]) -> str:
    lines = ["# Anchor waves — molecules per server", "",
             f"Plan: `{PLAN_FILE.relative_to(A.PLAN).as_posix()}`. Hours by `anchor_plan.anchor_hours` (CPX62, plane symmetry only).", "",
             "| server | molecules | rule hours | first | last |", "|---|---|---|---|---|"]
    for host, items in lists.items():
        if items:
            lines.append(f"| {host} | {len(items)} | {sum(c.hours for c in items):,.0f} | {items[0].mol_id} | {items[-1].mol_id} |")
        else:
            lines.append(f"| {host} | 0 | 0 | — | — |")
    earlier = [f"{i} [{'/'.join(statuses[i])}]" if i in statuses else i for i in part.in_earlier]
    lines += ["", f"Left out, carried anchor already: {len(part.carried)} ({', '.join(part.carried) or 'none'}).",
              f"Left out, dealt in an earlier wave and not carried: {len(earlier)} ({', '.join(earlier) or 'none'}). A status in "
              "brackets is the registry's: that molecule ended there without a carried anchor.",
              f"Needs its DFT row first (no corpus geometry): {len(part.needs_dft)}, rule hours "
              f"{sum(c.hours for c in part.needs_dft):,.0f}."]
    return "\n".join(lines) + "\n"


def write_lists(out: Path, lists: dict[str, list[Candidate]], corpus_molecules: Path, list_name: str) -> None:
    for host, items in lists.items():
        folder = out / host
        (folder / "geoms").mkdir(parents=True)
        for c in items:
            target = folder / "geoms" / c.mol_id
            target.mkdir()
            shutil.copy2(corpus_molecules / c.mol_id / "geometry.json", target / "geometry.json")
        (folder / list_name).write_text("".join(wave_line(c) + "\n" for c in items), encoding="utf-8", newline="\n")


def checked_request(args: argparse.Namespace) -> tuple[list[str], list[Path], Path, dict[str, str] | None]:
    """The hosts, the earlier waves' lists, the staging folder and the molecules' home hosts (None without `--home`) of a
    request, each refused here before any data is read."""
    hosts = [h for h in args.hosts.split(",") if h]
    if not hosts:
        raise SystemExit("--hosts names no host")
    if len(set(hosts)) != len(hosts):
        raise SystemExit(f"a host is named twice: {hosts}")
    if args.out.exists():
        raise SystemExit(f"{args.out} exists — a list a server may be working on is not rewritten")
    staging = args.out.with_name(args.out.name + ".partial")
    if staging.exists():
        raise SystemExit(f"{staging} exists — a failed earlier run left it; look at it and remove it by hand")
    if not LIST_NAME_PATTERN.fullmatch(args.list_name):
        raise SystemExit(f"--list-name {args.list_name}: a name like wave.txt or wave2.txt (letters, digits, _ and - after 'wave')")
    earlier = earlier_lists(args.earlier)
    taken = sorted({p.name for p in earlier})
    if args.list_name in taken:
        raise SystemExit(f"--list-name {args.list_name} is the name of an earlier wave's list ({', '.join(taken)}): copied to the "
                         "server it would replace a list a wave is reading — give this wave its own, such as wave2.txt")
    homes = home_hosts(args.home, hosts) if args.home is not None else None
    return hosts, earlier, staging, homes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--hosts", required=True, help="comma-separated host names from tools/hosts.tsv")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--plan", type=Path, default=PLAN_FILE)
    ap.add_argument("--earlier", type=Path, action="append", default=[],
                    help="the output folder of an earlier wave (repeatable): its molecules are not dealt again")
    ap.add_argument("--list-name", default=LIST_NAME, help="the list's file name in every host folder; a later wave needs its own")
    ap.add_argument("--home", type=Path,
                    help="a DFT batch's folder: each molecule goes to the host whose <folder>/<host>/ids.txt lists it, not by hours")
    args = ap.parse_args(argv)
    hosts, earlier, staging, homes = checked_request(args)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    rows = A.corpus_cells()
    statuses = registry_statuses()
    corpus_molecules = A.CORPUS / "molecules"
    all_candidates = candidates(plan, {i: r["smiles"] for i, r in rows.items()})
    part = partition(all_candidates, {i for i, held in statuses.items() if "carried" in held}, wave_ids(earlier),
                     lambda c: is_ready(rows[c.mol_id]["status"], corpus_molecules / c.mol_id))
    lists = deal(part.ready, hosts) if homes is None else stay_home(part.ready, hosts, homes)
    text = report(lists, part, statuses)
    staging.mkdir(parents=True)
    write_lists(staging, lists, corpus_molecules, args.list_name)
    (staging / "needs_dft.txt").write_text("".join(c.mol_id + "\n" for c in part.needs_dft), encoding="utf-8", newline="\n")
    (staging / "plan.md").write_text(text, encoding="utf-8", newline="\n")
    staging.rename(args.out)
    sys.stdout.write(text)
    return 0


def is_ready(manifest_status: str, molecule_folder: Path) -> bool:
    """A finished DFT row: manifest status done and the geometry on disk."""
    return manifest_status == "done" and (molecule_folder / "geometry.json").exists()


if __name__ == "__main__":
    sys.exit(main())
