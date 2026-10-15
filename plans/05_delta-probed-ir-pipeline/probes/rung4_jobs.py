"""Rung 4 step 1 (TASKS 61, 15 Oct 2026; the user: 'Trede 4 draait op de CCX53 na hefboom 5'): psi4_worker jobs for the 150 rows of the frozen
list `modules/05_support_predictor/out/rung4_candidates_2026-10-14.csv`, in the form of `probes/large_pah_jobs.py`: the corpus deck's B3LYP/6-31G*
optimisation without the finite-difference Hessians ("hessians": false), whose labels then come from `corpus/analytic_hessians.py`. The start
geometry is the corpus's own (`corpus/run_corpus.start_geometry`: RDKit ETKDG + MMFF from the SMILES, seed 0). Jobs are written into a local
staging folder, with `out_dir` already the server's folder, and copied to the labels server by the deploy step.

    python probes/rung4_jobs.py <staging_dir> [--server-root /root/labels/rung4/molecules] [--threads 8] [--memory-gb 24]
        → <staging_dir>/<id>/job.json, <staging_dir>/ids.txt (all 150), <staging_dir>/test_ids.txt (the tetracene family)
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.dirname(HERE)
M05 = os.path.join(PLAN, "modules", "05_support_predictor")
sys.path.insert(0, os.path.join(M05, "corpus"))
CSV = os.path.join(M05, "out", "rung4_candidates_2026-10-14.csv")
DECK = os.path.join(M05, "corpus", "decks", "deck_v1.json")
SERVER_ROOT = "/root/labels/rung4/molecules"


def job(row: dict, deck: dict, server_root: str) -> dict:
    """One psi4_worker job: optimise from the corpus start geometry at the deck's low functional, no Hessians."""
    from run_corpus import start_geometry
    xyz, optimise = start_geometry({**row, "qm9_label": ""})
    if not optimise:
        raise ValueError(f"{row['id']}: start_geometry would not optimise this row")
    return {"id": row["id"], "layer": row["layer"], "xyz_angstrom": [[s, float(x), float(y), float(z)] for s, x, y, z in xyz], "deck": deck,
            "out_dir": f"{server_root}/{row['id']}", "optimise": True, "grid_check": False, "hessians": False,
            "source": {"list": os.path.basename(CSV), "family": row["family"], "name": row["name"], "smiles": row["smiles"],
                       "test_family": int(row["test_family"]), "curve_rank": int(row["curve_rank"])}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("staging_dir")
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--server-root", default=SERVER_ROOT)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--memory-gb", type=int, default=24)
    ap.add_argument("--deck", default=DECK)
    a = ap.parse_args()
    deck = dict(json.load(open(a.deck, encoding="utf-8")), threads=a.threads, memory_gb=a.memory_gb)
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8")))
    ids, test = [], []
    for r in rows:
        j = job(r, deck, a.server_root)
        if len(j["xyz_angstrom"]) != int(r["n_atoms"]):
            raise ValueError(f"{r['id']}: {len(j['xyz_angstrom'])} atoms embedded, the list says {r['n_atoms']}")
        os.makedirs(os.path.join(a.staging_dir, r["id"]), exist_ok=True)
        json.dump(j, open(os.path.join(a.staging_dir, r["id"], "job.json"), "w", encoding="utf-8"), indent=1)
        ids.append(r["id"])
        if r["test_family"] == "1":
            test.append(r["id"])
    for name, lst in (("ids.txt", ids), ("test_ids.txt", test)):
        with open(os.path.join(a.staging_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"# rung 4 (TASKS 61), from {os.path.basename(a.csv)}\n" + "".join(i + "\n" for i in lst))
    print(f"{len(ids)} jobs ({len(test)} test family) in {a.staging_dir}; out_dir under {a.server_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
