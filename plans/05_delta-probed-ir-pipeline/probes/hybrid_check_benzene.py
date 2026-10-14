"""The registered free check of our DFT anharmonic shift on benzene (14 Oct 2026, TASKS 56;
GoalGathering/notes/PreRegistration_2026-10-14_Hybrid_Check_Benzene.md): Δ_semi = ν_MCP − ω_CCSD(T)/spdf per fundamental (Boese & Martin 2004,
Tables I–II, entered in probes/results_m1/hybrid_check_benzene_2026-10-14/boese_martin_tables.json) against S1's Δ_anh = ν − ω at G and R.

Matching. Each of our modes is classed by symmetry from its own vector: in plane or out of plane (share of the displacement along the ring
normal), g or u (inversion), degenerate or not, and for non-degenerate g in-plane modes totally symmetric or not. The classes are the D6h
irreps of benzene's modes except that b1u and b2u fall into one class (in plane, u, non-degenerate); within a class the table's rows and our
modes are paired in the order of ω. A degenerate pair counts once. Window and exclusions as registered (ω_R in 550–2000 cm⁻¹; ν5, ν12, ν15,
ν16 out).

    python probes/hybrid_check_benzene.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from e8_symmetry import point_group_ops  # noqa: E402
from qff_symmetry_rebuild import rep  # noqa: E402
from s1_anharmonic_level import harmonic_modes  # noqa: E402

RUN = os.path.join(HERE, "results_m1", "s1_anharmonic_benzene_2026-10-13", "s1_benzene")
OUT = os.path.join(HERE, "results_m1", "hybrid_check_benzene_2026-10-14")
WINDOW = (550.0, 2000.0)
LINE = 3.0
TOL_SYM = 2e-2      # |q·D q| within this of 1: the mode maps onto ± itself (G's minimum is symmetric only to its grid)
CLASS_OF_IRREP = {"a1g": ("ip", "g", 1, True), "a2g": ("ip", "g", 1, False), "b1u": ("ip", "u", 1, False), "b2u": ("ip", "u", 1, False),
                  "e2g": ("ip", "g", 2, False), "e1u": ("ip", "u", 2, False), "a2u": ("oop", "u", 1, False), "b2g": ("oop", "g", 1, False),
                  "e1g": ("oop", "g", 2, False), "e2u": ("oop", "u", 2, False)}


def our_modes(setting: str) -> list[dict]:
    """One entry per fundamental of the setting: ω, Δ_anh, symmetry class."""
    ref = json.load(open(os.path.join(RUN, setting, "ref.json"), encoding="utf-8"))
    sym = ref["molecule"]["symbols"]
    x = np.array(ref["molecule"]["geometry"], float).reshape(-1, 3)
    n = len(sym)
    w, q = harmonic_modes(os.path.join(RUN, setting, "ref.json"))
    z = np.load(os.path.join(RUN, setting, "qff_report.npz"))
    d_anh = z["nu_sym"] - z["omega_cm"]
    assert np.allclose(z["omega_cm"], w, atol=0.5), "qff_report and ref.json disagree on ω"
    ops = point_group_ops(sym, x)
    Ds = [rep(R, p, n) for R, p in ops]
    inv = [rep(R, p, n) for R, p in ops if np.allclose(R, -np.eye(3), atol=1e-3)]
    assert len(inv) == 1, "benzene's inversion not found"
    c = x - x.mean(0)
    normal = np.linalg.eigh(c.T @ c)[1][:, 0]
    # degeneracy from symmetry, not from a frequency tolerance: G's coarse grid splits benzene's pairs by more than dpir's tolerance
    # (14 Oct 2026, first run); a mode is one-dimensional when every operation maps it onto ± itself
    one_d = [all(abs(q[:, k] @ D @ q[:, k]) > 1 - TOL_SYM for D in Ds) for k in range(len(w))]
    groups, rest = [[k] for k in range(len(w)) if one_d[k]], [k for k in range(len(w)) if not one_d[k]]
    while rest:
        k = rest.pop(0)
        j = min(rest, key=lambda i: abs(w[i] - w[k]))
        rest.remove(j)
        groups.append([k, j])
    out = []
    for grp in groups:
        V = q[:, grp]                                       # mass-weighted; the classes are the same in Cartesian
        oop = float(np.mean([(V[:, k].reshape(n, 3) @ normal) @ (V[:, k].reshape(n, 3) @ normal) / (V[:, k] @ V[:, k]) for k in range(len(grp))]))
        par = float(np.trace(V.T @ inv[0] @ V)) / len(grp)
        ts = len(grp) == 1 and all(V[:, 0] @ D @ V[:, 0] > 1 - TOL_SYM for D in Ds)
        out.append({"omega": float(w[grp[0]]), "d_anh": float(np.mean(d_anh[grp])), "class": ("oop" if oop > 0.5 else "ip",
                    "g" if par > 0 else "u", len(grp), bool(ts))})
    return out


def main() -> None:
    tab = json.load(open(os.path.join(OUT, "boese_martin_tables.json"), encoding="utf-8"))["rows"]
    modes = {s: our_modes(s) for s in ("R", "G")}
    pairs = []
    for cls in sorted(set(CLASS_OF_IRREP.values())):
        rows = sorted([r for r in tab if CLASS_OF_IRREP[r["irrep"]] == cls], key=lambda r: -r["omega_ccsdt"])
        ours = {s: sorted([m for m in modes[s] if m["class"] == cls], key=lambda m: -m["omega"]) for s in modes}
        if any(len(ours[s]) != len(rows) for s in ours):
            raise SystemExit(f"class {cls}: {len(rows)} table rows, ours R {len(ours['R'])} / G {len(ours['G'])}")
        for r, mr, mg in zip(rows, ours["R"], ours["G"], strict=True):
            pairs.append({"mode": r["mode"], "irrep": r["irrep"], "omega_ccsdt": r["omega_ccsdt"], "omega_R": mr["omega"], "omega_G": mg["omega"],
                          "d_semi": r["nu_mcp"] - r["omega_ccsdt"], "d_R": mr["d_anh"], "d_G": mg["d_anh"],
                          "d_b3lyp_tz2p": r["nu_b3lyp"] - r["omega_b3lyp"], "d_b971_tz2p": r["nu_b971"] - r["omega_b971"], "fermi": r["fermi"], "starred": r["starred_table_ii"]})
    use = [p for p in pairs if WINDOW[0] <= p["omega_R"] <= WINDOW[1] and not p["fermi"]]

    def stats(key):
        diff = np.array([p[key] - p["d_semi"] for p in use])
        return {"rms": float(np.sqrt(np.mean(diff ** 2))), "max": float(np.abs(diff).max()), "mean": float(diff.mean())}
    res = {"n_modes": len(use), "excluded": [p["mode"] for p in pairs if p["fermi"] or not WINDOW[0] <= p["omega_R"] <= WINDOW[1]],
           "G": stats("d_G"), "R": stats("d_R"), "b3lyp_tz2p": stats("d_b3lyp_tz2p"), "b971_tz2p_exploratory": stats("d_b971_tz2p"), "line": LINE, "pairs": pairs}
    res["verdict"] = "passes" if res["G"]["rms"] <= LINE else "misses"
    json.dump(res, open(os.path.join(OUT, "hybrid_check.json"), "w", encoding="utf-8"), indent=1)
    lines = ["# Benzene: our Δ_anh against ν_MCP − ω_CCSD(T)/spdf (registered 14 Oct 2026)", "",
             f"{res['n_modes']} fundamentals in the window, excluded {res['excluded']}.", "",
             f"**G: rms {res['G']['rms']:.2f}, max {res['G']['max']:.2f}, mean {res['G']['mean']:+.2f} cm⁻¹ → {res['verdict']} (line ≤ {LINE})**  ",
             f"R: rms {res['R']['rms']:.2f}, max {res['R']['max']:.2f}; B3LYP/TZ2P (the paper's own ν − ω): rms {res['b3lyp_tz2p']['rms']:.2f}, "
             f"max {res['b3lyp_tz2p']['max']:.2f}; exploratory, not registered — B97-1/TZ2P: rms {res['b971_tz2p_exploratory']['rms']:.2f}, "
             f"max {res['b971_tz2p_exploratory']['max']:.2f}", "",
             "| mode | irrep | ω CCSD(T) | ω R | Δ_semi | Δ G | Δ R | Δ B3LYP/TZ2P | used |", "|---|---|---|---|---|---|---|---|---|"]
    for p in sorted(pairs, key=lambda p: p["mode"]):
        used = "yes" if p in use else ("Fermi" if p["fermi"] else "window")
        lines.append(f"| ν{p['mode']} | {p['irrep']} | {p['omega_ccsdt']} | {p['omega_R']:.0f} | {p['d_semi']:+d} | {p['d_G']:+.1f} | {p['d_R']:+.1f} | "
                     f"{p['d_b3lyp_tz2p']:+d} | {used} |")
    open(os.path.join(OUT, "hybrid_check.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
