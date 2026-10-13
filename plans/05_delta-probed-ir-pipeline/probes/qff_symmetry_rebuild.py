"""Rebuild a quartic force field's displaced Hessians from the symmetry-minimal set (13 Oct 2026, S1 registration amendment 2, step 4).

A complete set (reference + ±δ along every normal mode, as probes/make_qff_displacements.py writes it) is read; the files the two symmetry
savings would not compute are replaced by what the group gives, and the result is written as a new set for `python -m dpir.qff`:
  * a non-degenerate mode that is not totally symmetric: H(−δq) = D(g) H(+δq) D(g)ᵀ, for the operation g with D(g)d = −d (d the Cartesian
    displacement of +δq);
  * a degenerate pair (a, b): every image D(g)d_a lies in the pair's plane, D(g)d_a = c_g d_a + s_g d_b, and H(x₀ + D(g)d) = D(g) H(x₀ + d)
    D(g)ᵀ. From the images of H(±δa): the odd parts (c ∂_a + s ∂_b)H by least squares give the first derivatives, the even parts
    (c² Q_aa + 2cs Q_ab + s² Q_bb)/2 the second; H(±δb) = H₀ ± ∂_bH + Q_bb/2 replaces the two files of b.
Totally symmetric modes keep both files. The rebuilt set then goes through dpir.qff unchanged, and `s1_anharmonic_level.py compare` reads
it against the direct one. In production only +δa of each pair would be computed, with a chosen so that −a is an image; here the measured
H(−δa) stands for that image (same information), so the test isolates the new step: b from a by the group.

    python probes/qff_symmetry_rebuild.py <hess_dir> <out_hess_dir> [--disp 0.10] [--kinds pm,pairs]
    python probes/qff_symmetry_rebuild.py <hess_dir> --image-errors     the measured H(−δq) against every symmetry image of H(+δq),
        split by whether the operation maps the integration grid onto itself (R a signed permutation: Lebedev grids are octahedral)
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from e8_symmetry import point_group_ops  # noqa: E402

from dpir.qff import align_degenerate_subspaces, degenerate_groups, harmonic, load_results, reference_index  # noqa: E402

REL_TOL = 1e-2      # a displacement maps onto ±itself or into its pair's plane within this relative residual


def rep(R, perm, n):
    D = np.zeros((3 * n, 3 * n))
    for i in range(n):
        D[3 * perm[i]:3 * perm[i] + 3, 3 * i:3 * i + 3] = R
    return D


def grid_compatible(R) -> bool:
    """R maps an atom-centred Lebedev grid in the laboratory frame onto itself: a signed permutation matrix (the octahedral group)."""
    return bool(np.allclose(np.abs(R), np.round(np.abs(R)), atol=1e-6))


def image_errors(hess_dir: str, disp: float = 0.10) -> dict:
    """For every non-degenerate mode that is not totally symmetric: max |D H(+δq) Dᵀ − H(−δq)| / max |H(+δq) − H₀| over the operations
    with D d = −d, split by grid compatibility. Grid-compatible images show the noise floor of a DFT Hessian difference; the others add the
    grid's lack of the molecule's symmetry (13 Oct 2026: on the 21 Sep benzene set 3.0e-3 against 2.4e-2, medians)."""
    recs = load_results(hess_dir)
    i0 = reference_index(recs)
    ref = recs[i0]
    n = len(ref.symbols)
    ops = point_group_ops(ref.symbols, ref.geom.reshape(n, 3))
    harm = harmonic(ref.H, ref.symbols, ref.geom)
    harm, asg, _ = align_degenerate_subspaces(harm, recs, i0, disp)
    f = {(i, int(s)): k for k, (i, s, _dq, _res) in asg.items()}
    out = {"compatible": [], "other": []}
    for grp in degenerate_groups(harm.omega_cm):
        if len(grp) != 1:
            continue
        i = grp[0]
        dp = recs[f[(i, 1)]].geom - ref.geom
        Hp, Hm = recs[f[(i, 1)]].H, recs[f[(i, -1)]].H
        sig = np.abs(Hp - ref.H).max()
        for R, p in ops:
            D = rep(R, p, n)
            if np.linalg.norm(D @ dp + dp) / np.linalg.norm(dp) < REL_TOL:
                out["compatible" if grid_compatible(R) else "other"].append(float(np.abs(D @ Hp @ D.T - Hm).max() / sig))
    return {k: {"images": len(v), "median": float(np.median(v)) if v else None, "max": max(v) if v else None} for k, v in out.items()}


def rebuild(hess_dir: str, out_dir: str, disp: float = 0.10, kinds=("pm", "pairs")) -> dict:
    recs = load_results(hess_dir)
    i0 = reference_index(recs)
    ref = recs[i0]
    n = len(ref.symbols)
    x0 = ref.geom.reshape(n, 3)
    ops = point_group_ops(ref.symbols, x0)
    Ds = [rep(R, p, n) for R, p in ops]
    harm = harmonic(ref.H, ref.symbols, ref.geom)
    harm, asg, _ = align_degenerate_subspaces(harm, recs, i0, disp)
    files = {}                                              # (mode, sign) -> record index
    for k, (i, s, _dq, _res) in asg.items():
        files[(i, int(s))] = k
    d = {key: recs[k].geom - ref.geom for key, k in files.items()}
    H = {key: recs[k].H for key, k in files.items()}
    new = {}                                                # record index -> rebuilt Hessian
    log = {"group_order": len(ops), "totally_symmetric": [], "pm_rebuilt": [], "pairs_rebuilt": [], "max_rel_change": {}}
    for grp in degenerate_groups(harm.omega_cm):
        if len(grp) == 1:
            i = grp[0]
            dp = d[(i, 1)]
            res_same = min(np.linalg.norm(D @ dp - dp) for D in Ds) / np.linalg.norm(dp)
            if all(np.linalg.norm(D @ dp - dp) / np.linalg.norm(dp) < REL_TOL for D in Ds):
                log["totally_symmetric"].append(i); continue
            g = int(np.argmin([np.linalg.norm(D @ dp + dp) for D in Ds]))
            r = np.linalg.norm(Ds[g] @ dp + dp) / np.linalg.norm(dp)
            if r > REL_TOL:
                raise ValueError(f"mode {i}: no operation maps its displacement onto its negative (best {r:.1e}; identity residual {res_same:.1e})")
            if "pm" in kinds:
                new[files[(i, -1)]] = Ds[g] @ H[(i, 1)] @ Ds[g].T
                log["pm_rebuilt"].append(i)
            continue
        if len(grp) != 2:
            raise ValueError(f"degenerate group {grp}: only pairs are handled")
        a, b = grp
        if "pairs" not in kinds:
            continue
        P = np.c_[d[(a, 1)], d[(b, 1)]]
        cs, odd, even = [], [], []
        H0 = ref.H
        for D in Ds:
            v = D @ d[(a, 1)]
            c, *_ = np.linalg.lstsq(P, v, rcond=None)
            if np.linalg.norm(P @ c - v) / np.linalg.norm(v) > REL_TOL:
                raise ValueError(f"pair {grp}: an image of the displacement leaves the pair's plane")
            Hp, Hm = D @ H[(a, 1)] @ D.T, D @ H[(a, -1)] @ D.T
            cs.append(c); odd.append((Hp - Hm) / 2); even.append((Hp + Hm) / 2 - H0)
        cs = np.array(cs)
        Xo = cs                                              # odd part = c·∂_a + s·∂_b
        Xe = np.c_[cs[:, 0] ** 2, 2 * cs[:, 0] * cs[:, 1], cs[:, 1] ** 2]   # even part = c²·Q_aa/2 + 2cs·Q_ab/2 + s²·Q_bb/2
        if np.linalg.matrix_rank(Xe, tol=1e-6) < 3:
            raise ValueError(f"pair {grp}: the images span fewer than three lines")
        O = np.array(odd).reshape(len(Ds), -1); E = np.array(even).reshape(len(Ds), -1)
        G = np.linalg.lstsq(Xo, O, rcond=None)[0]
        Q = np.linalg.lstsq(Xe, E, rcond=None)[0]
        Gb, Qbb = G[1].reshape(3 * n, 3 * n), Q[2].reshape(3 * n, 3 * n)
        new[files[(b, 1)]] = H0 + Gb + Qbb
        new[files[(b, -1)]] = H0 - Gb + Qbb
        log["pairs_rebuilt"].append([a, b])
    for k, Hn in new.items():
        Hn = 0.5 * (Hn + Hn.T)
        signal = np.abs(recs[k].H - ref.H).max()
        log["max_rel_change"][recs[k].file] = float(np.abs(Hn - recs[k].H).max() / signal)
        new[k] = Hn
    os.makedirs(out_dir, exist_ok=False)
    for k, r in enumerate(recs):
        src = os.path.join(hess_dir, r.file)
        if k not in new:
            shutil.copy2(src, os.path.join(out_dir, r.file)); continue
        dj = json.load(open(src, encoding="utf-8"))
        dj["return_result"] = new[k].ravel().tolist()
        dj["symmetry_rebuild"] = "probes/qff_symmetry_rebuild.py: replaced by the group's image (13 Oct 2026, S1 amendment 2)"
        json.dump(dj, open(os.path.join(out_dir, r.file), "w", encoding="utf-8"))
    vals = list(log["max_rel_change"].values())
    log["summary"] = {"files": len(recs), "replaced": len(new), "max_rel_change_max": max(vals) if vals else 0.0,
                      "max_rel_change_median": float(np.median(vals)) if vals else 0.0}
    return log


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hess_dir")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--image-errors", action="store_true")
    ap.add_argument("--disp", type=float, default=0.10)
    ap.add_argument("--kinds", default="pm,pairs", help="which savings to rebuild: pm, pairs or both (the default)")
    a = ap.parse_args(argv)
    if a.image_errors:
        print(json.dumps(image_errors(a.hess_dir, a.disp), indent=1))
        return
    if not a.out_dir:
        ap.error("out_dir is required for a rebuild")
    log = rebuild(a.hess_dir, a.out_dir, a.disp, tuple(a.kinds.split(",")))
    json.dump(log, open(os.path.join(a.out_dir, "..", "symmetry_rebuild.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in log.items() if k != "max_rel_change"}, indent=1))


if __name__ == "__main__":
    main()
