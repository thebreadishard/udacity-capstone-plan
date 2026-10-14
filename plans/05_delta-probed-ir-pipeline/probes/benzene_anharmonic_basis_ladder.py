"""Benzene's anharmonic shift Δ_anh = ν − ω along the basis sets we already have (15 Oct 2026; desk work before S1-TZ, TASKS 60; exploratory,
it changes no line and no prediction of `PreRegistration_2026-10-14_TZ_Anharmonic_Basis.md`).

Per fundamental, matched to Boese & Martin's tables with the hybrid check's own matching (`hybrid_check_benzene.match_to_table`): B3LYP/6-31G
(S1's B setting) and B3LYP/6-31G* (G) from our dpir.qff reports, B3LYP/TZ2P (Miani et al. 2000's finite-difference force field, as tabulated by
Boese & Martin 2004 — one calculation, not two), and the semi-experimental ν_MCP − ω_CCSD(T). Reported: G − TZ2P and B − G per mode, and their
rms over the hybrid check's window (ω 550–2,000 cm⁻¹, Fermi-flagged modes out) for degenerate (e) and non-degenerate modes and for the
out-of-plane modes (a2u, b2g, e1g, e2u) against the in-plane ones.

    python probes/benzene_anharmonic_basis_ladder.py [--out probes/results_m1/benzene_basis_ladder_2026-10-15]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hybrid_check_benzene as hb  # noqa: E402

OUT_OF_PLANE = ("a2u", "b2g", "e1g", "e2u")


def ladder() -> list[dict]:
    modes = {s: hb.our_modes(os.path.join(hb.RUN, s)) for s in ("B", "G")}
    out = []
    for r, m in hb.match_to_table(hb.load_table(), modes):
        out.append({"mode": r["mode"], "irrep": r["irrep"], "omega_ccsdt": r["omega_ccsdt"], "d_631g": m["B"]["d_anh"], "d_631gs": m["G"]["d_anh"],
                    "d_tz2p": r["nu_b3lyp"] - r["omega_b3lyp"], "d_semi": r["nu_mcp"] - r["omega_ccsdt"], "fermi": bool(r["fermi"]),
                    "in_window": bool(hb.WINDOW[0] <= r["omega_ccsdt"] <= hb.WINDOW[1])})
    return sorted(out, key=lambda x: x["mode"])


def groups(rows: list[dict]) -> dict:
    use = [x for x in rows if x["in_window"] and not x["fermi"]]
    sel = {"degenerate (e)": lambda x: x["irrep"].startswith("e"), "non-degenerate": lambda x: not x["irrep"].startswith("e"),
           "out of plane": lambda x: x["irrep"] in OUT_OF_PLANE, "in plane": lambda x: x["irrep"] not in OUT_OF_PLANE}
    out = {}
    for name, f in sel.items():
        s = [x for x in use if f(x)]
        gt = np.array([x["d_631gs"] - x["d_tz2p"] for x in s])
        bg = np.array([x["d_631g"] - x["d_631gs"] for x in s])
        out[name] = {"n": len(s), "rms_631gs_minus_tz2p": float(np.sqrt((gt ** 2).mean())), "mean_631gs_minus_tz2p": float(gt.mean()),
                     "rms_631g_minus_631gs": float(np.sqrt((bg ** 2).mean()))}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = ladder()
    res = {"modes": rows, "groups": groups(rows)}
    lines = ["# Benzene: Δ_anh along the basis (exploratory, before S1-TZ)", "",
             "| mode | irrep | ω CCSD(T) | 6-31G | 6-31G* | TZ2P | semi-exp. | Fermi | 6-31G* − TZ2P | 6-31G − 6-31G* |", "|---|---|---|---|---|---|---|---|---|---|"]
    lines += [f"| ν{x['mode']} | {x['irrep']} | {x['omega_ccsdt']} | {x['d_631g']:+.1f} | {x['d_631gs']:+.1f} | {x['d_tz2p']:+d} | {x['d_semi']:+d} | "
              f"{'yes' if x['fermi'] else ''} | {x['d_631gs'] - x['d_tz2p']:+.1f} | {x['d_631g'] - x['d_631gs']:+.1f} |" for x in rows]
    lines += ["", "| modes (window, no Fermi) | n | rms 6-31G* − TZ2P | mean | rms 6-31G − 6-31G* |", "|---|---|---|---|---|"]
    lines += [f"| {k} | {v['n']} | {v['rms_631gs_minus_tz2p']:.1f} | {v['mean_631gs_minus_tz2p']:+.1f} | {v['rms_631g_minus_631gs']:.1f} |" for k, v in res["groups"].items()]
    print("\n".join(lines))
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        json.dump(res, open(os.path.join(a.out, "ladder.json"), "w", encoding="utf-8"), indent=1)
        open(os.path.join(a.out, "ladder.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
