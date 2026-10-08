"""Odds lever 3 (3 Oct 2026): does local CC reproduce the force constants? LNO-CCSD(T)/cc-pVDZ energies (the L2 probe's recipe: DF-RHF, Pipek–Mezey
fragments, LNO thresholds 'tight', MP2-corrected composite energy) at an anchor's reference geometry and at ±h along stored displacement coordinates;
the diagonal curvature H_kk = (E₊ + E₋ − 2E₀)/h² against the canonical anchor's two routes — the energy route from its stored ener_<k>_<sign>.npy and the
gradient-route Hessian's H_kk. One number per coordinate; the laptop-sized version of the Snellius question (couplings need gradients, which LNO does
not provide — the diagonal is what energies can test).

    python probes/lno_curvature_check.py <anchor dir> <geometry.json> [--ks 0,1,2] [--max-k 6] [--threads 8] [--max-memory 8000] [--xtight] [--reuse-localisation]

--spot (TASKS 36, 8 Oct 2026): spot-check anchors above the top rung — no canonical anchor exists; <anchor dir> is a work directory (created), the
reference geometry is <geometry.json>, --ks is required, --step sets h (default 0.005 bohr, the anchors' step), and each row carries the LNO
curvature only. The MP2 basis step at the same coordinates comes from `probes/cc_composite_full_check.py compute --ks`.

--reuse-localisation (cell (b) of the LNO follow-up, registered 3 Oct 2026 23:3x): the reference point records its Pipek–Mezey orbitals and every
fragment's LNO active space (probes/lno_frozen_spaces.py, saved as lno_spaces_<basis>_<thresh>.npz beside the cached reference energy); the displaced
points carry those spaces instead of localising and truncating afresh, so the curvature is read inside one fixed correlation domain.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l2_lno_price as L2  # noqa: E402
import lno_frozen_spaces as FS  # noqa: E402

FIRST_ROW = {"B", "C", "N", "O", "F"}


def available_ks(anchor):
    ks = sorted({int(f[5:7]) for f in os.listdir(anchor) if f.startswith("ener_") and f.endswith("_p.npy")})
    return [k for k in ks if os.path.exists(os.path.join(anchor, f"ener_{k:02d}_m.npy"))]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("anchor")
    ap.add_argument("geometry")
    ap.add_argument("--ks", default=None, help="comma list of displacement coordinates (default: the first --max-k with stored energies)")
    ap.add_argument("--max-k", type=int, default=2, help="coordinates taken from the stored list when --ks is not given (3 Oct 2026: two — one LNO energy is ≈ 1 h on the laptop)")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=8000)
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--xtight", action="store_true", help="LNO thresholds 1e-7 / 1e-8 instead of 1e-6 / 1e-7")
    ap.add_argument("--reuse-localisation", action="store_true", help="carry the reference's LOs and LNO spaces to the displaced points (cell (b))")
    ap.add_argument("--out", default=None)
    ap.add_argument("--spot", action="store_true", help="TASKS 36: no canonical anchor; <anchor> is a work directory, --ks required")
    ap.add_argument("--step", type=float, default=0.005, help="--spot only: the displacement h in bohr (the anchors' step)")
    a = ap.parse_args()
    from pyscf import lib
    lib.num_threads(a.threads)
    if a.xtight:
        L2.THRESH["tight"] = L2.THRESH["xtight"]
    L2.TIER = "t0"                                                     # tight thresholds, triples on
    g = json.load(open(a.geometry))
    sym = [s.capitalize() for s in g["symbols"]]
    if a.spot:
        if not a.ks:
            raise SystemExit("--spot needs --ks (the coordinates chosen by the registered rule)")
        os.makedirs(a.anchor, exist_ok=True)
        x0 = np.asarray(g["coords_bohr"], float); h = a.step; H = None; e0_can = None
    else:
        ref = np.load(os.path.join(a.anchor, "reference.npz"))
        x0 = np.asarray(ref["coords_bohr"], float)
        if np.abs(x0 - np.asarray(g["coords_bohr"], float)).max() > 1e-8:
            raise SystemExit("geometry.json does not match the anchor's reference coordinates")
        hz = np.load(os.path.join(a.anchor, "hessian_ccsd_t.npz"))
        h = float(hz["step"]); H = hz["H_raw"]; e0_can = float(ref["energy"])
    frozen = sum(1 for s in sym if s in FIRST_ROW)
    ks = [int(k) for k in a.ks.split(",")] if a.ks else available_ks(a.anchor)[: a.max_k]
    tagsp = "_reuse" if a.reuse_localisation else ""
    out = a.out or os.path.join(a.anchor, f"lno_curvature_check{tagsp}_{datetime.now():%Y-%m-%d}.json")
    logp = a.anchor                                                    # L2.log appends to <dir>/l2.log
    xc = x0 - x0.mean(0); normal = np.linalg.eigh(xc.T @ xc)[1][:, 0]  # the molecular plane's normal (smallest principal axis)
    t0 = time.time()
    cache = os.path.join(a.anchor, f"lno_reference_{a.basis}_{'xtight' if a.xtight else 'tight'}.json")   # the reference energy is reused across runs
    spaces_path = cache.replace("lno_reference_", "lno_spaces_").replace(".json", ".npz")
    store = None
    if os.path.exists(cache) and (not a.reuse_localisation or os.path.exists(spaces_path)):
        rec0 = json.load(open(cache))
        print(f"reference LNO energy from {os.path.basename(cache)} ({rec0.get('date', '?')})", flush=True)
        if a.reuse_localisation:
            store = FS.load_store(spaces_path); print(f"reference LNO spaces from {os.path.basename(spaces_path)} ({len(store['frags'])} fragments)", flush=True)
    else:
        store = {} if a.reuse_localisation else None
        rec0 = L2.point(sym, x0, a.basis, "tight", frozen, a.max_memory, logp, "reference", spaces={"mode": "capture", "store": store} if a.reuse_localisation else None)
        rec0["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        json.dump(rec0, open(cache, "w"), indent=1)
        if a.reuse_localisation:
            FS.save_store(spaces_path, store)
    e0 = rec0["e_tot_composite"]
    rows = []
    for k in ks:
        es = {}
        for sgn, s in (("p", 1.0), ("m", -1.0)):
            x = x0.copy(); x.flat[k] += s * h
            es[sgn] = L2.point(sym, x, a.basis, "tight", frozen, a.max_memory, logp, f"k{k:02d}{sgn}{'r' if a.reuse_localisation else ''}",
                               spaces={"mode": "replay", "store": store} if a.reuse_localisation else None)["e_tot_composite"]
        hkk_lno = (es["p"] + es["m"] - 2 * e0) / h ** 2
        if a.spot:
            rows.append(dict(k=k, atom=k // 3, xyz="xyz"[k % 3], element=sym[k // 3], oop_fraction=float(abs(normal[k % 3])), H_kk_lno=hkk_lno,
                             dE_lno_pm=(es["p"] - es["m"])))
            print(f"k {k:2d} ({sym[k // 3]}{k // 3} {'xyz'[k % 3]}, oop {abs(normal[k % 3]):.2f}): H_kk LNO {hkk_lno:.6f}", flush=True)
            continue
        ep, em = float(np.load(os.path.join(a.anchor, f"ener_{k:02d}_p.npy"))), float(np.load(os.path.join(a.anchor, f"ener_{k:02d}_m.npy")))
        hkk_can = (ep + em - 2 * e0_can) / h ** 2
        rows.append(dict(k=k, atom=k // 3, xyz="xyz"[k % 3], element=sym[k // 3], oop_fraction=float(abs(normal[k % 3])), H_kk_hessian=float(H[k, k]),
                         H_kk_energy_route=hkk_can, H_kk_lno=hkk_lno,
                         delta_lno_vs_hessian=hkk_lno - float(H[k, k]), rel=(hkk_lno - float(H[k, k])) / float(H[k, k]),
                         dE_lno_pm=(es["p"] - es["m"]), dE_can_pm=(ep - em)))
        print(f"k {k:2d} ({sym[k // 3]}{k // 3} {'xyz'[k % 3]}, oop {abs(normal[k % 3]):.2f}): H_kk hessian {H[k, k]:.6f} | energy route {hkk_can:.6f} | LNO {hkk_lno:.6f} | Δ {rows[-1]['delta_lno_vs_hessian']:+.2e} "
              f"({100 * rows[-1]['rel']:+.2f} %)", flush=True)
    if a.spot:
        res = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), mode="spot", workdir=a.anchor, geometry=a.geometry, basis=a.basis, frozen=frozen,
                   step=h, thresholds=L2.THRESH["tight"], e0_lno_composite=e0, rows=rows, seconds=round(time.time() - t0), reference_record=rec0)
        json.dump(res, open(out, "w"), indent=1)
        print(f"LNO spot check: {len(rows)} coordinates; {res['seconds']} s → {out}")
        return 0
    worst = max(rows, key=lambda r: abs(r["delta_lno_vs_hessian"]))
    res = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), anchor=a.anchor, basis=a.basis, frozen=frozen, step=h, thresholds=L2.THRESH["tight"],
               spaces="reused (cell b)" if a.reuse_localisation else "fresh per point",
               e0_lno_composite=e0, e0_canonical=e0_can, e0_shift=e0 - e0_can, rows=rows, max_abs_delta=abs(worst["delta_lno_vs_hessian"]),
               max_rel=max(abs(r["rel"]) for r in rows), seconds=round(time.time() - t0), reference_record=rec0)
    json.dump(res, open(out, "w"), indent=1)
    print(f"LNO curvature check: {len(rows)} coordinates; max |H_kk(LNO) − H_kk(Hessian)| = {res['max_abs_delta']:.2e} a.u. (worst k {worst['k']}), max rel {100 * res['max_rel']:.2f} %; "
          f"E0 shift LNO−canonical {res['e0_shift']:+.6f} E_h; {res['seconds']} s → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
