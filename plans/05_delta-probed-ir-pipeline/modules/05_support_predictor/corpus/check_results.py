"""Mechanical check of the corpus results (23 September 2026, after E6 phase 1).

    python check_results.py [--layer A2]

Per layer: done/failed rows, every done row has result.json with two frequency lists of length 3N (six translations/rotations
included, projected to ~0), the worker's imaginary-mode count (frequencies < -10 cm^-1; such molecules are skipped by
m05/build_release.py), compute hours from the timings. Exit code 1 if a done row lacks a result or has the wrong list length.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", default=None)
    a = ap.parse_args()
    with open(HERE / "manifest.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    layers = [a.layer] if a.layer else sorted({r["layer"] for r in rows if r["status"] in ("done", "failed")})
    bad = 0
    for layer in layers:
        done = [r for r in rows if r["layer"] == layer and r["status"] == "done"]
        failed = [r for r in rows if r["layer"] == layer and r["status"] == "failed"]
        imag, suspect, hours = [], [], 0.0
        for r in done:
            p = HERE / "molecules" / r["id"] / "result.json"
            if not p.exists():
                print(f"MISSING result.json: {r['id']} {r['name']}"); bad += 1; continue
            d = json.loads(p.read_text(encoding="utf-8"))
            n3 = 3 * int(r["n_atoms"])
            if len(d["freq_b3lyp_cm"]) != n3 or len(d["freq_wb97x_cm"]) != n3:
                print(f"WRONG LENGTH: {r['id']} {r['name']} {len(d['freq_b3lyp_cm'])}/{len(d['freq_wb97x_cm'])} vs 3N={n3}"); bad += 1
            if d.get("n_imaginary_b3lyp", 0) or d.get("n_imaginary_wb97x", 0):
                imag.append((r["name"], d["n_imaginary_b3lyp"], d["n_imaginary_wb97x"], round(min(d["freq_b3lyp_cm"]), 1), round(min(d["freq_wb97x_cm"]), 1)))
            # 23 Sep 2026 guard (noise principle): the two functionals' sorted frequency lists should differ by tens of cm^-1, not hundreds;
            # benzene's corpus wB97X finite-difference Hessian was wrong by up to 133 cm^-1 (analytic second route restores the degeneracies).
            fb = np.sort(np.array(d["freq_b3lyp_cm"])); fw = np.sort(np.array(d["freq_wb97x_cm"])); keep = fb > 50
            dif = fw[-int(keep.sum()):] - fb[keep]
            if np.abs(dif).max() > 80:
                suspect.append((r["name"], r["id"], round(float(np.abs(dif).max()), 1), round(float(np.sqrt(np.mean(dif ** 2))), 1)))
            hours += d["timings_s"]["total"] / 3600
        print(f"layer {layer}: done {len(done)}, failed {len(failed)}, with an imaginary mode {len(imag)} (usable {len(done) - len(imag)}), compute {hours:.0f} h")
        for f_ in failed:
            print(f"  failed: {f_['name']} ({f_['id']}) {f_['note'][:80]}")
        for w in imag:
            print(f"  imaginary: {w[0]} n_imag B3LYP {w[1]} wB97X {w[2]}, lowest {w[3]} / {w[4]} cm^-1")
        for s_ in suspect:
            print(f"  SUSPECT Hessian (max sorted-pair |dw| {s_[2]} cm^-1, RMS {s_[3]}): {s_[0]} ({s_[1]}) -> second route: corpus/analytic_hessians.py")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
