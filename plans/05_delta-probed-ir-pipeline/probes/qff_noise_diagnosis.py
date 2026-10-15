"""Which constant tripped dpir.qff's noise guard, which vibrations does it couple, and does it move the fundamentals a read uses? (15 Oct 2026,
styrene in S2: route disagreement 10.7 cm⁻¹ against the guard's 10. Diagnosis only — the registered noise rule stands.)

From a setting directory of `probes/s1_anharmonic_level.sh` (ref.json, qff_report.npz):
- the largest route disagreements |φ_iijj(a) − φ_iijj(b)| (route a displaces i and reads H_jj, route b the reverse) with both modes' ω, their
  substituent share (mass-weighted amplitude on atoms outside every ring) and out-of-plane share (`e8_cc_locality.mode_shares`);
- the sensitivity of the VPT2 fundamentals to the noisy constants: ν with route a's quartics against ν with route b's (dpir.qff.vpt2 with the
  report's own cubic constants, rotational constants and Coriolis ζ, the default deperturbation window), per mode, and its maximum over the
  window 550–2,000 cm⁻¹;
- the literature's remedy for a large-amplitude mode (VPT2 with that mode decoupled, e.g. the V30 benchmark's VPT2+R): every mode below
  --decouple-below cm⁻¹ loses its cubic, quartic and Coriolis couplings, and the shift of the window's fundamentals against the full VPT2
  (symmetry-averaged quartics, as the report's ν) is reported.

    python probes/qff_noise_diagnosis.py <setting_dir> [--top 5] [--decouple-below 100] [--out diagnosis.json]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from e8_cc_locality import bond_graph, mode_shares, rings  # noqa: E402

from dpir.qff import atomic_masses_me, coriolis_zeta, harmonic, rotational_constants, vpt2  # noqa: E402

WINDOW = (550.0, 2000.0)


def decoupled(p3, p4, zeta, modes):
    """Copies of the force-field arrays with every coupling of `modes` removed (their rows and columns set to zero)."""
    p3, p4, zeta = p3.copy(), p4.copy(), zeta.copy()
    for k in modes:
        p3[k, :, :] = p3[:, k, :] = p3[:, :, k] = 0.0
        p4[k, :] = p4[:, k] = 0.0
        zeta[:, k, :] = zeta[:, :, k] = 0.0
    return p3, p4, zeta


def diagnose(setting_dir: str, top: int = 5, decouple_below: float = 100.0) -> dict:
    ref = json.load(open(os.path.join(setting_dir, "ref.json"), encoding="utf-8"))
    sym = ref["molecule"]["symbols"]
    geom = np.asarray(ref["molecule"]["geometry"], float).reshape(-1, 3)
    H = np.asarray(ref["return_result"], float).reshape(3 * len(sym), 3 * len(sym))
    z = np.load(os.path.join(setting_dir, "qff_report.npz"))
    harm = harmonic(H, sym, geom)
    w = np.asarray(z["omega_cm"], float)
    if len(w) != len(harm.omega_cm) or np.abs(w - harm.omega_cm).max() > 1e-3:
        raise SystemExit("the report's ω and ref.json's harmonic analysis disagree")
    n = len(sym)
    ring_sets = rings(bond_graph(sym, geom))
    in_ring = set().union(*ring_sets) if ring_sets else set()
    A = (harm.q.reshape(n, 3, -1) ** 2).sum(1)                         # per atom, per mode
    sub = A[[i for i in range(n) if i not in in_ring]].sum(0) if len(in_ring) < n else np.zeros(len(w))
    _, oop, _ = mode_shares(harm.q, sym, atomic_masses_me(sym), geom)
    a, b = np.asarray(z["phi_iijj_route_a"], float), np.asarray(z["phi_iijj_route_b"], float)
    d = np.abs(a - b)
    order = np.dstack(np.unravel_index(np.argsort(-d, axis=None), d.shape))[0]
    seen, worst = set(), []
    for i, j in order:
        key = (min(i, j), max(i, j))
        if key in seen:
            continue
        seen.add(key)
        worst.append({"i": int(i), "j": int(j), "omega_i": float(w[i]), "omega_j": float(w[j]), "disagreement": float(d[i, j]),
                      "phi_a": float(a[i, j]), "phi_b": float(b[i, j]), "substituent_share_i": float(sub[i]), "substituent_share_j": float(sub[j]),
                      "oop_share_i": float(oop[i]), "oop_share_j": float(oop[j])})
        if len(worst) >= top:
            break
    B = rotational_constants(geom, sym)
    zeta = coriolis_zeta(harm.q, sym)
    p3 = np.asarray(z["phi_ijk"], float)
    nu_a = vpt2(w, p3, a, B, zeta)[0]
    nu_b = vpt2(w, p3, b, B, zeta)[0]
    dnu = nu_a - nu_b
    win = (w >= WINDOW[0]) & (w <= WINDOW[1])
    soft = [int(k) for k in np.where(w < decouple_below)[0]]
    p4s = np.asarray(z["phi_iijj_sym"], float)
    nu_full = vpt2(w, p3, p4s, B, zeta)[0]
    if np.abs(nu_full - np.asarray(z["nu_sym"], float)).max() > 1e-6:
        raise SystemExit("this script's VPT2 does not reproduce the report's ν (nu_sym) — the inputs differ")
    q3, q4, qz = decoupled(p3, p4s, zeta, soft)
    nu_dec = vpt2(w, q3, q4, B, qz)[0]
    shift = nu_dec - nu_full
    decoupling = {"decouple_below_cm": decouple_below, "modes": {str(k): float(w[k]) for k in soft},
                  "window_max_abs_shift": float(np.abs(shift[win]).max()) if soft else 0.0,
                  "window_rms_shift": float(np.sqrt((shift[win] ** 2).mean())) if soft else 0.0,
                  "largest_window_shifts": {f"{k}:{w[k]:.0f}": float(shift[k]) for k in np.argsort(-np.abs(np.where(win, shift, 0)))[:6]}}
    return {"setting_dir": setting_dir, "worst": worst, "lowest_modes": [float(x) for x in w[:4]],
            "dnu_routes_window_max": float(np.abs(dnu[win]).max()), "dnu_routes_window_rms": float(np.sqrt((dnu[win] ** 2).mean())),
            "dnu_routes_all_max": float(np.abs(dnu).max()), "dnu_routes_argmax_mode_omega": float(w[int(np.argmax(np.abs(dnu)))]),
            "dnu_routes_per_mode": {f"{k}:{w[k]:.0f}": float(dnu[k]) for k in np.argsort(-np.abs(dnu))[:8]}, "decoupling": decoupling}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("setting_dir")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--decouple-below", type=float, default=100.0, help="cm-1: modes below are decoupled in the remedy's estimate")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = diagnose(a.setting_dir, a.top, a.decouple_below)
    print(json.dumps(res, indent=1))
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
