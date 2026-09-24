"""Obstacle 9 — cation rows for the proxy corpus (24 September 2026; the user: "Zet benzeen⁺ en naftaleen⁺ maar op hel1-14 zodra route 2 klaar is").

Runs psi4_worker.py with the cation deck (deck_v1_cation.json: UKS, charge 1, doublet; numerics of deck v1) from a neutral corpus geometry with a
seeded 0.01 Å distortion (so a Jahn–Teller minimum is reachable in c1), and summarises: UKS-B3LYP geometry, both Hessians, frequencies, imaginary
count, timings. Output directory has the corpus schema (geometry.json, hessian_b3lyp.npz, hessian_wb97x.npz, result.json), so build_release and the
E-series readers can take it as a row (`--include-cations` to be added when the rows are read).

Usage: python cation_rows.py --name benzene --geometry in/benzene/geometry.json --out rows/benzene --worker psi4_worker.py --deck deck_v1_cation.json [--threads 16] [--memory-gb 24]
       python cation_rows.py --smoke --out smoke_rows --worker psi4_worker.py --deck deck_v1_cation.json [--threads 4]     (water cation, seconds to minutes)
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

import numpy as np

BOHR = 0.529177210903


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--name", default="water"); ap.add_argument("--geometry", default=None); ap.add_argument("--out", required=True)
    ap.add_argument("--worker", required=True); ap.add_argument("--deck", required=True); ap.add_argument("--threads", type=int, default=16); ap.add_argument("--memory-gb", type=int, default=24)
    ap.add_argument("--distort", type=float, default=0.01, help="seeded random Cartesian distortion in Å applied to the neutral start geometry"); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(); t0 = time.time()
    deck = json.load(open(a.deck)); deck["threads"] = a.threads; deck["memory_gb"] = a.memory_gb
    if a.smoke:
        xyz = [["O", 0.0, 0.0, 0.1173], ["H", 0.0, 0.7572, -0.4692], ["H", 0.0, -0.7572, -0.4692]]; name = "water"
    else:
        g = json.load(open(a.geometry)); rng = np.random.default_rng(0)
        x = np.asarray(g["coords_bohr"]) * BOHR + rng.normal(0.0, a.distort, (len(g["symbols"]), 3))
        xyz = [[s, *map(float, r)] for s, r in zip(g["symbols"], x)]; name = a.name
    os.makedirs(a.out, exist_ok=True)
    job = {"id": f"{name}_cation", "layer": "A_cation", "xyz_angstrom": xyz, "deck": deck, "out_dir": os.path.abspath(a.out), "optimise": True, "grid_check": False}
    jp = os.path.join(a.out, "job.json"); json.dump(job, open(jp, "w"), indent=1)
    print(f"[{datetime.now():%H:%M:%S}] {name}+ : {len(xyz)} atoms, deck {deck['deck']} ({deck['reference']}, charge {deck['charge']}, mult {deck['multiplicity']}), {a.threads} threads, {a.memory_gb} GB", flush=True)
    p = subprocess.run([sys.executable, a.worker, jp], capture_output=True, text=True)
    open(os.path.join(a.out, "worker_stdout.txt"), "w").write(p.stdout + "\n---stderr---\n" + p.stderr)
    rp = os.path.join(a.out, "result.json")
    if not os.path.exists(rp):
        print(f"[{datetime.now():%H:%M:%S}] {name}+ FAILED: no result.json (worker exit {p.returncode}); stderr tail: {p.stderr[-400:]}", flush=True); sys.exit(1)
    r = json.load(open(rp)); tm = r.get("timings_s", {})
    print(f"[{datetime.now():%H:%M:%S}] {name}+ {r.get('status')}: opt {tm.get('optimise')} s, B3LYP Hessian {tm.get('hessian_b3lyp')} s, wB97X Hessian {tm.get('hessian_wb97x')} s; "
          f"imaginary B3LYP {r.get('n_imaginary_b3lyp')} / wB97X {r.get('n_imaginary_wb97x')}; lowest B3LYP {r.get('freq_b3lyp_cm', [None])[:3]}; total {time.time() - t0:.0f} s", flush=True)
    if r.get("status") != "done": sys.exit(1)


if __name__ == "__main__":
    main()
