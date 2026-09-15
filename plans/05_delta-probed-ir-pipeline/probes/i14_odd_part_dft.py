"""I14 confirmation at DFT level (2026-09-15): the odd part ½[E(+q) − E(−q)] along chosen modes, for one or more stage-A sets.

Run for `--sets naphthalene,naphthalene_sym` it gives the A/B that decision 37's prerequisite predicts: the factory modes
(`symmetry c1` Hessian, impure at 1e-4, `MODE_PURITY_2026-09-15.md`) carry a force term of tens of µE_h along a b-mode
at the coupled-cluster level (M3, modes 12 and 31) and must show one at DFT level too; the symmetrised, irrep-projected
modes of `dryrun_dft_delta_recovery.py --symmetrised` must show ≲ 1 µE_h at q = 1. Both functionals of the dry-run pair
are computed. Energies are psi4 single points at 6-31G* (seconds each); no absolute energy is printed.

Usage (Windows, qc env, Library\\bin on PATH):
  python i14_odd_part_dft.py --sets naphthalene,naphthalene_sym --modes 12,22,31 --qs 0.5,1.0 --threads 8
Modes are given as indices of the FIRST set; in the other sets the mode with the nearest frequency is used (printed).
"""
import argparse
import json
import os
import time
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
import sys  # noqa: E402
sys.path.insert(0, HERE)
from dryrun_dft_delta_recovery import BASIS, FUNCTIONALS, make_molecule, psi4_setup  # noqa: E402


def load(name):
    d = os.path.join(HERE, "results_dryrun", name)
    a = json.load(open(os.path.join(d, "stageA.json")))
    z = np.load(os.path.join(d, "stageA_hessians.npz"))
    return a, z["L"], z["omega_au"], z["Minv"], z["coords"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="naphthalene,naphthalene_sym")
    ap.add_argument("--modes", default="12,22,31")
    ap.add_argument("--qs", default="0.5,1.0")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--out", default=os.path.join(HERE, "results_dryrun", "i14_odd_part_dft.json"))
    args = ap.parse_args()
    sets = args.sets.split(",")
    modes0 = [int(t) for t in args.modes.split(",")]
    qs = [float(t) for t in args.qs.split(",")]
    psi4 = psi4_setup(args.threads, os.path.join(HERE, "results_dryrun", "i14_odd_part_dft.psi4.out"))
    rec = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "basis": BASIS, "functionals": FUNCTIONALS, "qs": qs, "sets": {}}
    a0 = load(sets[0])[0]
    lines = [f"# I14 at DFT level — odd and even parts along modes {modes0} (indices of `{sets[0]}`), {rec['date']}", "",
             f"½[E(+q) − E(−q)] and ½[E(+q) + E(−q)] − E(0) in µE_h; {BASIS}; sets: {sets}", ""]
    for name in sets:
        a, L, omega, Minv, x0 = load(name)
        freqs = np.array(a["freq_low_cm"])
        modes = [int(np.argmin(np.abs(freqs - a0["freq_low_cm"][m]))) for m in modes0]
        irreps = a.get("irreps")
        print(f"[{datetime.now():%H:%M:%S}] set {name}: modes {modes} ({', '.join(f'{freqs[m]:.1f}' for m in modes)} cm⁻¹); "
              f"geometry source: {a.get('geometry_source', 'stage A optimisation (pre-2026-09-15)')}", flush=True)
        S = {"modes": modes, "freq_cm": [float(freqs[m]) for m in modes], "irreps": [irreps[m] if irreps else None for m in modes],
             "purity": [a.get("irrep_purity_before_projection", [None] * len(freqs))[m] for m in modes], "rows": []}
        e_ref = {}
        for fn in FUNCTIONALS.values():
            t0 = time.time()
            e_ref[fn] = float(psi4.energy(f"{fn}/{BASIS}", molecule=make_molecule(psi4, a["symbols"], x0)))
            print(f"    reference {fn}: {time.time()-t0:.0f} s", flush=True)
        lines += [f"## {name} — geometry: {a.get('geometry_source', 'stage A optimisation')}", "",
                  "| mode | ω (cm⁻¹) | irrep | 1 − purity | functional | " + " | ".join(f"odd({q:g})" for q in qs) + " | "
                  + " | ".join(f"even({q:g})" for q in qs) + " |", "|---|---|---|---|---|" + "---|" * (2 * len(qs))]
        for m in modes:
            for fn in FUNCTIONALS.values():
                odd, even = [], []
                for q in qs:
                    e = {}
                    for sgn in (+1, -1):
                        v = np.zeros(len(omega)); v[m] = sgn * q
                        x = x0 + ((L @ (v / np.sqrt(omega))) * Minv).reshape(-1, 3)
                        e[sgn] = float(psi4.energy(f"{fn}/{BASIS}", molecule=make_molecule(psi4, a["symbols"], x)))
                    odd.append(0.5 * (e[+1] - e[-1]) * 1e6)
                    even.append((0.5 * (e[+1] + e[-1]) - e_ref[fn]) * 1e6)
                row = {"mode": m, "functional": fn, "odd_uEh": odd, "even_uEh": even}
                S["rows"].append(row)
                pur = a.get("irrep_purity_before_projection")
                lines.append(f"| {m} | {freqs[m]:.1f} | {irreps[m] if irreps else '—'} | "
                             f"{'—' if not pur else f'{1 - pur[m]:.1e}'} | {fn} | "
                             + " | ".join(f"{o:+.3f}" for o in odd) + " | " + " | ".join(f"{v:+.2f}" for v in even) + " |")
                print(f"    mode {m} {fn}: odd " + ", ".join(f"{o:+.3f}" for o in odd) + " µE_h", flush=True)
        lines.append("")
        rec["sets"][name] = S
        json.dump(rec, open(args.out, "w"), indent=1)
    md = args.out.replace(".json", ".md")
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))
    print(f"written {args.out} and {md}")


if __name__ == "__main__":
    main()
