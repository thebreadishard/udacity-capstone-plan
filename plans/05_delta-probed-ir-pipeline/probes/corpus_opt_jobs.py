"""psi4_worker jobs that optimise corpus molecules from their start geometry, and batches of them for servers (21 Nov 2026).

A job is the corpus deck's B3LYP/6-31G* optimisation without the finite-difference Hessians ("hessians": false); the molecule's labels then
come from `corpus/analytic_hessians.py`, which `probes/labels_batch_ccx53.sh` runs after the optimisation. The start geometry is the
corpus's own (`corpus/run_corpus.start_geometry`: RDKit ETKDG + MMFF from the SMILES, seed 0). `opt_job` is the one implementation;
`probes/rung4_jobs.py` builds its jobs with it.

The batch command takes an id list of manifest rows (one id per line, '#' comments allowed), deals the molecules over hosts with the anchor
lists' rule (`anchor_wave_lists.deal`: largest first to the least loaded host, each host's list then cheapest first, by
`anchor_plan.anchor_hours` as the size weight) and writes, per host, `<out>/<host>/molecules/<id>/job.json` with `out_dir` already the
server's folder, and `<out>/<host>/ids.txt` cheapest first, so each server's first molecules can become anchors soonest. An existing output
folder is refused; the folder is built beside it and renamed into place.

    python probes/corpus_opt_jobs.py --ids probes/results_m1/anchor_waves_2026-11-21/needs_dft.txt --hosts anc1,anc2,anc3,anc4,anc5 \
        --server-root /root/dft1/molecules --threads 4 --memory-gb 6 --out probes/results_m1/anchor_dft_2026-11-21
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus"
sys.path.insert(0, str(CORPUS))
DECK = CORPUS / "decks" / "deck_v1.json"


NEUTRAL_SINGLET_LAYERS = {"A", "A2", "B", "G", "P3", "R4"}   # deck v1's charge 0, singlet; cations (P3c) take their own deck and parent geometry


def opt_job(row: dict, deck: dict, out_dir: str, source: dict) -> dict:
    """One psi4_worker job: optimise from the corpus start geometry at the deck's low functional, no Hessians."""
    from run_corpus import start_geometry
    if row["layer"] not in NEUTRAL_SINGLET_LAYERS:
        raise ValueError(f"{row['id']}: layer {row['layer']} is not a neutral singlet layer; opt_job builds deck v1 jobs only")
    xyz, optimise = start_geometry({**row, "qm9_label": ""})
    if not optimise:
        raise ValueError(f"{row['id']}: start_geometry would not optimise this row")
    return {"id": row["id"], "layer": row["layer"], "xyz_angstrom": [[s, float(x), float(y), float(z)] for s, x, y, z in xyz], "deck": deck,
            "out_dir": out_dir, "optimise": True, "grid_check": False, "hessians": False, "source": source}


def read_ids(path: Path) -> list[str]:
    """The ids of a list file, in order; a repeated id is refused."""
    ids = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    repeated = sorted({i for i in ids if ids.count(i) > 1})
    if repeated:
        raise SystemExit(f"{path}: ids listed twice: {repeated}")
    return ids


def write_batches(out: Path, lists: dict, rows: dict, deck: dict, server_root: str, list_name: str) -> None:
    """Per host: the job files and ids.txt (cheapest first), under out."""
    for host, items in lists.items():
        folder = out / host
        (folder / "molecules").mkdir(parents=True)
        for c in items:
            row = {**rows[c.mol_id], "id": c.mol_id}
            job = opt_job(row, deck, f"{server_root}/{c.mol_id}", {"list": list_name, "name": row["name"], "smiles": row["smiles"]})
            if len(job["xyz_angstrom"]) != c.n_atoms:
                raise ValueError(f"{c.mol_id}: {len(job['xyz_angstrom'])} atoms embedded, the SMILES has {c.n_atoms}")
            (folder / "molecules" / c.mol_id).mkdir()
            (folder / "molecules" / c.mol_id / "job.json").write_text(json.dumps(job, indent=1), encoding="utf-8", newline="\n")
        (folder / "ids.txt").write_text(f"# {list_name}, {host}, cheapest first\n" + "".join(c.mol_id + "\n" for c in items),
                                        encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    import anchor_plan as A
    import anchor_wave_lists as W

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ids", required=True, type=Path, help="id list of manifest rows")
    ap.add_argument("--hosts", required=True, help="comma-separated host names from tools/hosts.tsv")
    ap.add_argument("--server-root", required=True, help="absolute folder on the servers that will hold <id>/ (the jobs' out_dir)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--threads", type=int, required=True)
    ap.add_argument("--memory-gb", type=int, required=True)
    args = ap.parse_args(argv)
    hosts = [h for h in args.hosts.split(",") if h]
    if len(set(hosts)) != len(hosts):
        raise SystemExit(f"a host is named twice: {hosts}")
    if not args.server_root.startswith("/"):
        raise SystemExit(f"--server-root must be absolute on the server, not {args.server_root!r}")
    if args.threads < 1 or args.memory_gb < 1:
        raise SystemExit("--threads and --memory-gb must be positive")
    if args.out.exists():
        raise SystemExit(f"{args.out} exists — a batch a server may be working on is not rewritten")
    ids = read_ids(args.ids)
    rows = A.corpus_cells()
    candidates = W.candidates({"chosen": {"batch": ids}}, {i: r["smiles"] for i, r in rows.items()})
    done = sorted(c.mol_id for c in candidates if rows[c.mol_id]["status"] == "done")
    if done:
        raise SystemExit(f"rows already done in the manifest, not optimised again: {done}")
    deck = dict(json.loads(DECK.read_text(encoding="utf-8")), threads=args.threads, memory_gb=args.memory_gb)
    lists = W.deal(candidates, hosts)
    staging = args.out.with_name(args.out.name + ".partial")
    if staging.exists():
        raise SystemExit(f"{staging} exists — a failed earlier run left it; look at it and remove it by hand")
    write_batches(staging, lists, rows, deck, args.server_root, args.ids.name)
    os.replace(staging, args.out)
    for host, items in lists.items():
        print(f"{host}: {len(items)} jobs, rule hours {sum(c.hours for c in items):,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
