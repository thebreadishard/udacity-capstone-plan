"""Map our 30 benzene normal coordinates to the 20 Wilson modes of the benchmark file and compare (22 September 2026).

Inputs: the QFF arrays of a benzene run (`qff_*.npz` with omega_cm, nu_sym, phi_ijk) and
`data/benzene_benchmark_goodman1991_miani2000.json` (Goodman 1991 Tables I/II, Miani 2000 Tables II/VII).

Mapping rule (tier-1 probe, stated so it can be checked): (1) exactly degenerate pairs (|Δω| < 0.5 cm⁻¹) are e modes,
the rest are non-degenerate; (2) the two a1g modes are the non-degenerate modes with the largest |φ_iii| (the breathing
mode and the symmetric C–H stretch); (3) inside each class (e, a1g, other non-degenerate) our modes and the benchmark's
B3LYP/TZ2P harmonic frequencies are matched by rank — same functional, so the order agrees except at near-crossings, which
the table flags when neighbours in the class lie within 15 cm⁻¹ in either list.

Writes: a markdown table (our ω, ν; Miani's B3LYP/TZ2P ω and calculated ν; Goodman's ω estimate; Miani's ω_exp; the
experimental fundamental) and two json files for `r0_diagonal_reading.py --exp` (mode index → experimental fundamental) and
for a harmonic-against-harmonic reading (mode index → Goodman ω estimate, Miani ω_exp).

Usage: python benzene_benchmark_map.py results_vpt2/qff_benzene_pyscf_analytic_d010_2026-09-21.npz --out results_vpt2/benzene_benchmark_2026-09-22.md
"""
import argparse
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("npz")
    ap.add_argument("--bench", default=os.path.join(HERE, "data", "benzene_benchmark_goodman1991_miani2000.json"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = np.load(a.npz)
    w, nu, phi3 = d["omega_cm"], d["nu_sym"], d["phi_ijk"]
    n = len(w)
    bench = json.load(open(a.bench, encoding="utf-8"))["modes"]

    # classes on our side
    pairs = [(i, i + 1) for i in range(n - 1) if abs(w[i] - w[i + 1]) < 0.5]
    in_pair = {i for p in pairs for i in p}
    nondeg = [i for i in range(n) if i not in in_pair]
    a1g = sorted(sorted(nondeg, key=lambda i: -abs(phi3[i, i, i]))[:2])
    other = [i for i in nondeg if i not in a1g]
    ours = {"e": [p for p in pairs], "a1g": [(i,) for i in a1g], "nd": [(i,) for i in other]}
    # classes on the benchmark side, ordered by B3LYP/TZ2P ω
    key = "b3lyp_tz2p_omega"
    bcls = {"e": sorted([m for m in bench if m["degeneracy"] == 2], key=lambda m: m[key]),
            "a1g": sorted([m for m in bench if m["sym"] == "a1g"], key=lambda m: m[key]),
            "nd": sorted([m for m in bench if m["degeneracy"] == 1 and m["sym"] != "a1g"], key=lambda m: m[key])}
    assert all(len(ours[c]) == len(bcls[c]) for c in ours), {c: (len(ours[c]), len(bcls[c])) for c in ours}
    rows = []
    for c in ("e", "a1g", "nd"):
        for k, (grp, m) in enumerate(zip(ours[c], bcls[c])):
            i = grp[0]
            flag = ""
            for kk in (k - 1, k + 1):
                if 0 <= kk < len(ours[c]):
                    if abs(w[ours[c][kk][0]] - w[i]) < 15 or abs(bcls[c][kk][key] - m[key]) < 15:
                        flag = "near-crossing: rank-assigned"
            rows.append((i, grp, m, flag))
    rows.sort(key=lambda r: r[0])

    lines = [f"# Benzene: our modes against Goodman 1991 / Miani 2000 — {os.path.basename(a.npz)}", "",
             "Mapping by class (e pairs, a1g by |φ_iii|, other non-degenerate) and rank against Miani's B3LYP/TZ2P ω; see the script docstring. "
             "Δν = ν − ω is the anharmonic shift; ours from the two-route QFF, Miani's from their B3LYP/TZ2P force field (Table VII, ε = 0). "
             "ω_exp are experiment-derived harmonics: Goodman's Table II estimate (corrections applied to nine modes only) and Miani's Table II 'this work'.", "",
             "| ours | ω 6-31G* | ν ours | Δν ours | Wilson | sym | ω TZ2P | ν Miani | Δν Miani | ω_exp Goodman | ω_exp Miani | ν exp | ν ours − ν exp | note |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    exp_json, harm_json = {}, {}

    def miani_nu(m):
        """Miani's fundamental with their fullest resonance treatment (ε = 100 where the paper lists it, else ε = 0)."""
        return (m["miani_nu_calc_fermi"] or [m["miani_nu_calc"]])[-1]

    for i, grp, m, flag in rows:
        dn = nu[i] - w[i]
        dm = miani_nu(m) - m["b3lyp_tz2p_omega"]
        idx = "/".join(str(j) for j in grp)
        mn = f"{miani_nu(m)}" + ("†" if m["miani_nu_calc_fermi"] else "")
        lines.append(f"| {idx} | {w[i]:.1f} | {nu[i]:.1f} | {dn:+.1f} | ν{m['wilson']} | {m['sym']} | {m[key]} | {mn} | {dm:+d} | "
                     f"{m['goodman_omega']} | {m['miani_omega_exp']} | {m['exp_nu']}{'*' if m['exp_flag'] == 'estimated' else ''} | {nu[i] - m['exp_nu']:+.1f} | {flag} |")
        for j in grp:
            exp_json[str(j)] = m["exp_nu"]
            harm_json[str(j)] = {"wilson": m["wilson"], "sym": m["sym"], "goodman_omega": m["goodman_omega"], "miani_omega_exp": m["miani_omega_exp"],
                                 "miani_omega_exp_ref29": m["miani_omega_exp_ref29"], "ccsdt_omega": m["ccsdt_omega"], "exp_nu": m["exp_nu"]}
    lines += ["", "\\* estimated from infrared combinations (Goodman Table I, in parentheses there). † Miani's value with Fermi resonances within 100 cm⁻¹ "
              "treated (Table VII, ε = 100); the others are their ε = 0 values, the only ones the paper lists for those modes.", ""]
    # summary statistics on the shifts and on the fundamentals
    dn_all = np.array([nu[i] - w[i] for i, *_ in rows])
    dm_all = np.array([miani_nu(m) - m[key] for _, _, m, _ in rows])
    err = np.array([nu[i] - m["exp_nu"] for i, _, m, _ in rows])
    err_tz = np.array([miani_nu(m) - m["exp_nu"] for _, _, m, _ in rows])
    noch = [k for k, (_, _, m, _) in enumerate(rows) if m["wilson"] not in (2, 7, 13, 20)]
    lines += [f"- anharmonic shifts, ours vs Miani over the 20 modes: median |difference| {np.median(np.abs(dn_all - dm_all)):.1f} cm⁻¹, "
              f"max {np.abs(dn_all - dm_all).max():.1f}; without the four C–H stretches: median {np.median(np.abs((dn_all - dm_all)[noch])):.1f}, max {np.abs((dn_all - dm_all)[noch]).max():.1f}",
              f"- fundamentals against experiment, ours (B3LYP/6-31G*): MAE {np.mean(np.abs(err)):.1f} cm⁻¹ (without C–H stretches {np.mean(np.abs(err[noch])):.1f}); "
              f"Miani's B3LYP/TZ2P: MAE {np.mean(np.abs(err_tz)):.1f} (without C–H stretches {np.mean(np.abs(err_tz[noch])):.1f})"]
    txt = "\n".join(lines) + "\n"
    print(txt)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
        base = a.out[:-3] if a.out.endswith(".md") else a.out
        json.dump(exp_json, open(base + "_exp_nu.json", "w"), indent=1)
        json.dump(harm_json, open(base + "_harmonic_refs.json", "w"), indent=1)
        print("wrote", a.out, base + "_exp_nu.json", base + "_harmonic_refs.json")


if __name__ == "__main__":
    main()
