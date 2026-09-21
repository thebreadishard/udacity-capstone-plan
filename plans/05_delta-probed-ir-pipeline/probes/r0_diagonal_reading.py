"""Reader for a diagonal deck of frozen-space energies (21 September 2026): per mode the curvature k and quartic term c₄ of the
composite (and canonical, if present) energy along the B3LYP normal mode, and the coupled-cluster-corrected harmonic frequency
ω′ = ω_B3LYP · sqrt(k / k_B3LYP), with k_B3LYP = ω in atomic units (the displacement is L q / sqrt(ω)).

Works with the symmetric --npts grids of M1/M3 and with the --qlist grids of the R0 diagonal deck: for a mode with points on one side
only, the even part is E(q) − E(0) (exact when the mode is not totally symmetric, decision 37 / I14); with both sides it is the mean of
E(±q) minus E(0). Two positive |q| values give k and c₄ exactly (even(q) = ½ k q² + ¼ c₄ q⁴); one value gives k with c₄ = 0 and says so.

Usage: python r0_diagonal_reading.py <run_dir> [--stagea results_dryrun/benzene_r0/stageA.json] [--exp expfile.json] [--out file.md]
"""
import argparse
import json
import os

import numpy as np

HARTREE_CM = 219474.6313632


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir"); ap.add_argument("--stagea", default=None); ap.add_argument("--exp", default=None, help="json {mode_index: experimental fundamental cm-1}")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    sealed = json.load(open(os.path.join(a.run_dir, "m1_sealed_energies.json")))
    rows = json.load(open(os.path.join(a.run_dir, "m1_rows.json")))["rows"]
    fam = {r["mode"]: (r["family"], r["freq_cm"]) for r in rows}
    keys = [("composite", lambda p: p["A"]["e_tot_composite"]), ("SCF", lambda p: p["A"]["e_scf"]),
            ("LNO-CCSD(T) corr", lambda p: p["A"]["e_corr_lno_ccsd_t"]), ("MP2 corr", lambda p: p["A"]["e_corr_mp2_full"])]
    exp = json.load(open(a.exp)) if a.exp else {}
    lines = [f"# Diagonal deck reading — {a.run_dir}", "",
             "ω′ = ω_B3LYP √(k/ω_au): the harmonic frequency the composite (SCF + LNO-CCSD(T) − LNO-MP2 + full MP2) would give along the B3LYP mode, diagonal only.",
             "", "| mode | family | ω B3LYP | points | k composite (µE_h/q²) | c₄ | ω′ composite | ω′ SCF-only | ω′ − ω | experiment ν | ω′ − ν |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    out = {}
    for m in sorted(fam):
        P = {round(p["q"], 6): p for p in sealed["points"] if p["mode"] == m}
        if 0.0 not in P:
            continue
        qs = sorted(abs(q) for q in P if q != 0.0)
        qpos = sorted(set(qs))
        rec = {}
        for name, key in keys:
            E0 = key(P[0.0]); ev = []
            for q in qpos:
                vals = [key(P[s * q]) - E0 for s in (1, -1) if round(s * q, 6) in P]
                ev.append(np.mean(vals))
            ev = np.array(ev) * 1e6; qa = np.array(qpos)
            if len(qa) >= 2:
                A = np.stack([0.5 * qa**2, 0.25 * qa**4], 1); k, c4 = np.linalg.lstsq(A, ev, rcond=None)[0]
            else:
                k, c4 = 2 * ev[0] / qa[0]**2, float("nan")
            rec[name] = (k, c4)
        w = fam[m][1]; k_dft = w / HARTREE_CM * 1e6
        wc = w * np.sqrt(rec["composite"][0] / k_dft); ws = w * np.sqrt(rec["SCF"][0] / k_dft)
        sides = "±" if any(round(-q, 6) in P for q in qpos) else "+"
        ex = exp.get(str(m)); exs = f"{ex:.0f}" if ex else "—"; dex = f"{wc - ex:+.1f}" if ex else "—"
        c4s = f"{rec['composite'][1]:+.1f}" if not np.isnan(rec["composite"][1]) else "(one |q|: c₄ = 0 assumed)"
        lines.append(f"| {m} | {fam[m][0]} | {w:.1f} | {sides}{','.join(str(q) for q in qpos)} | {rec['composite'][0]:+.1f} | {c4s} | **{wc:.1f}** | {ws:.1f} | {wc - w:+.1f} | {exs} | {dex} |")
        out[m] = {"family": fam[m][0], "omega_b3lyp": w, "k_composite_uEh": rec["composite"][0], "c4_composite_uEh": rec["composite"][1], "omega_cc": wc, "omega_scf": ws, "sides": sides, "q": qpos}
    txt = "\n".join(lines) + "\n"
    dest = a.out or os.path.join(a.run_dir, "DIAGONAL_READING.md")
    open(dest, "w", encoding="utf-8").write(txt); json.dump(out, open(dest.replace(".md", ".json"), "w"), indent=1); print(txt)


if __name__ == "__main__":
    main()
