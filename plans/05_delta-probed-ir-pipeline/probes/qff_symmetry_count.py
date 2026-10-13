"""How many analytic Hessians a semi-diagonal quartic force field needs when the point group is used (13 Oct 2026, TASKS 53; the user: 'Gaan
met die banaan').

The design note's price (Design_2026-10-13_Spectral_Shape_Anharmonic_Step.md §2) already uses one saving: for a mode that is not totally
symmetric, H(−δq) = D(g) H(+δq) D(g)ᵀ for an operation g with D(g) q = −q, so its −δ Hessian is free. This script adds the second: of a
degenerate pair (a, b) only one Hessian, at +δa, is computed. Every image D(g)a lies in the pair's plane, and H(δ D(g)a) = D(g) H(δa) D(g)ᵀ.
With a chosen as an eigenvector of eigenvalue −1 of some operation restricted to the pair (a reflection in the pair's plane, or −I there),
the images come in ± pairs; when they span at least three lines, the odd parts give ∂H/∂q_a and ∂H/∂q_b and the even parts give the three
second derivatives Q_aa, Q_ab, Q_bb by least squares — everything the semi-diagonal quartic field takes from the pair.

The count needs only the group and the atom permutations: a random Hessian averaged over the group has the molecule's symmetry and no
accidental degeneracy, so its internal eigenvectors classify the modes (non-degenerate totally symmetric, non-degenerate other, pairs).
Counts per molecule:
    full     2M + 1
    pm       1 + 2·n_ts + (M − n_ts)                    (the note's current route)
    pair     1 + 2·n_ts + n_other + n_pairs             (this script's route; every pair must pass the two conditions above)

    python probes/qff_symmetry_count.py [--out probes/results_m1/qff_symmetry_count_2026-10-13]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from e8_symmetry import BOHR, point_group_ops  # noqa: E402
from s1_anharmonic_level import external_basis  # noqa: E402

SELECTION = os.path.join(HERE, "results_m1", "large_labels_price_2026-10-12", "selection.json")
BENZENE = os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181", "geometry.json")
TOL_DEG = 1e-7          # relative eigenvalue gap below which two modes form a pair
# Price inputs. One B3LYP/6-31G* Hessian at the labels settings (R) in CCX53 lane-hours: the design note's §2 table (from
# probes/results_m1/large_labels_price_2026-10-12/; ≥ 34 atoms extrapolated, t ∝ nbas^3.4). € per lane-hour: the same table (≈ 0.21).
LANE_H = {"tetracene (ideal)": 3.2, "coronene": 6.6, "peropyrene": 8.7, "ovalene": 17.0, "hexa-peri-hexabenzocoronene": 42.0}
EUR_PER_LANE_H = 0.21
# Cost of one displaced Hessian relative to R, measured on benzene by S1 (s1, 5 threads per setting, the three settings in parallel; median
# interval between Hessian files at 21:5x on 13 Oct: R 234 s over 22 files, G 112 s over 50, B 162 s over 33). Benzene's ratio, not the
# large molecules': the grid's share of a Hessian falls as the basis grows, so G's saving there is likely smaller — time on the target first.
SETTING_FACTOR = {"R": 1.0, "G": 112 / 234, "B": 162 / 234}


def tetracene_ideal():
    """Tetracene with ideal hexagons (C–C 1.40 Å, C–H 1.08 Å): the count depends only on the group and the permutations, so an ideal
    D2h geometry stands in for an optimised one."""
    r, h = 1.40, 1.08
    cs, hs = [], []
    for ring in range(4):
        cx = (ring - 1.5) * r * np.sqrt(3)
        for k in range(6):
            ang = np.pi / 6 + k * np.pi / 3
            cs.append((cx + r * np.cos(ang), r * np.sin(ang)))
    uniq = []
    for p in cs:
        if all(np.hypot(p[0] - q[0], p[1] - q[1]) > 0.1 for q in uniq):
            uniq.append(p)
    for p in uniq:
        nb = [q for q in uniq if 0.1 < np.hypot(p[0] - q[0], p[1] - q[1]) < 1.5]
        if len(nb) == 2:                                   # a C–H carbon: H along the outward bisector
            v = np.array(p) - 0.5 * (np.array(nb[0]) + np.array(nb[1]))
            hs.append(tuple(np.array(p) + h * v / np.linalg.norm(v)))
    xyz = [(x, y, 0.0) for x, y in uniq] + [(x, y, 0.0) for x, y in hs]
    assert len(uniq) == 18 and len(hs) == 12
    return ["C"] * 18 + ["H"] * 12, np.array(xyz) / BOHR


def rep_matrices(ops, n):
    D = []
    for R, p in ops:
        M = np.zeros((3 * n, 3 * n))
        for i in range(n):
            M[3 * p[i]:3 * p[i] + 3, 3 * i:3 * i + 3] = R
        D.append(M)
    return D


def symmetrize(symbols, x_bohr):
    """The geometry averaged over its group (x_i ← mean_g R_gᵀ x_perm_g(i)): an optimised geometry is symmetric only to its convergence, and
    the classification below needs exact invariance (benzene's corpus geometry gave 0 totally symmetric modes and a split pair without it)."""
    x = np.asarray(x_bohr, float) - np.asarray(x_bohr, float).mean(0)
    ops = point_group_ops(symbols, x)
    return np.mean([np.array([R.T @ x[p[i]] for i in range(len(x))]) for R, p in ops], axis=0)


def count(symbols, x_bohr, seed=0):
    n = len(symbols)
    x_bohr = symmetrize(symbols, x_bohr)
    ops = point_group_ops(symbols, x_bohr, tol=1e-6)
    D = rep_matrices(ops, n)
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((3 * n, 3 * n)); A = A + A.T
    H = sum(d @ A @ d.T for d in D) / len(D)
    E = external_basis(np.asarray(x_bohr, float))
    Q = np.linalg.svd(np.eye(3 * n) - E @ E.T)[0][:, :3 * n - E.shape[1]]     # orthonormal internal basis
    w, U = np.linalg.eigh(Q.T @ H @ Q)
    V = Q @ U
    M = len(w)
    scale = np.abs(w).max()
    groups, i = [], 0
    while i < M:
        j = i + 1
        while j < M and abs(w[j] - w[i]) < TOL_DEG * scale:
            j += 1
        groups.append(list(range(i, j))); i = j
    sizes = [len(g) for g in groups]
    if max(sizes) > 2:
        raise ValueError(f"multiplet of size {max(sizes)}: this count handles groups with irreps of dimension ≤ 2")
    n_ts = n_other = 0
    pair_problems = []
    for g in groups:
        if len(g) == 1:
            v = V[:, g[0]]
            ts = all(np.allclose(d @ v, v, atol=1e-8) for d in D)
            n_ts += ts; n_other += not ts
            continue
        B = V[:, g]                                         # 3n × 2, the pair's plane
        reps2 = [B.T @ d @ B for d in D]                    # the operations restricted to the pair
        a = None
        for r2 in reps2:
            ev, evec = np.linalg.eigh(0.5 * (r2 + r2.T))
            if np.isclose(np.linalg.det(r2), -1) or np.allclose(r2, -np.eye(2), atol=1e-8):
                a = evec[:, np.argmin(ev)]; break
        if a is None:
            pair_problems.append(("no operation with eigenvalue −1 on the pair", g)); continue
        imgs = np.array([r2 @ a for r2 in reps2])
        if not any(np.allclose(im, -a, atol=1e-8) for im in imgs):
            pair_problems.append(("−a not among the images", g)); continue
        lines = []
        for im in imgs:
            ang = np.arctan2(im[1], im[0]) % np.pi
            if all(min(abs(ang - l), np.pi - abs(ang - l)) > 1e-6 for l in lines):
                lines.append(ang)
        if len(lines) < 3:
            pair_problems.append((f"images span {len(lines)} lines (< 3)", g))
    n_pairs = sizes.count(2)
    return {"atoms": n, "order": len(ops), "M": M, "n_ts": int(n_ts), "n_other_nondeg": int(n_other), "n_pairs": n_pairs,
            "full": 2 * M + 1, "pm": 1 + 2 * n_ts + (M - n_ts), "pair": 1 + 2 * n_ts + n_other + n_pairs,
            "pair_problems": [(p, [int(k) for k in g]) for p, g in pair_problems]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(HERE, "results_m1", "qff_symmetry_count_2026-10-13"))
    a = ap.parse_args(argv)
    mols = {}
    b = json.load(open(BENZENE, encoding="utf-8"))
    mols["benzene"] = (b["symbols"], np.array(b["coords_bohr"]))
    mols["tetracene (ideal)"] = tetracene_ideal()
    sel = json.load(open(SELECTION, encoding="utf-8"))
    for name, s in sel["test"].items():
        mols[name] = (s["symbols"], np.array(s["xyz"]) / BOHR)
    res = {name: count(sym, x) for name, (sym, x) in mols.items()}
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "counts.json"), "w", encoding="utf-8"), indent=1)
    lines = ["| molecule | atoms | group order | M | totally symmetric | other non-degenerate | pairs | full 2M+1 | ± symmetry | + pairs | "
             "pairs / ± |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in res.items():
        lines.append(f"| {name} | {r['atoms']} | {r['order']} | {r['M']} | {r['n_ts']} | {r['n_other_nondeg']} | {r['n_pairs']} | "
                     f"{r['full']} | {r['pm']} | {r['pair']} | {r['pair'] / r['pm']:.2f} |")
        if r["pair_problems"]:
            lines.append(f"|   ↳ pairs the second saving cannot use: {r['pair_problems']} |")
    lines += ["", "Price (€, route A, all five large molecules' rows; R-level lane-hours × setting factor × €0.21):", "",
              "| molecule | R, ± | R, + pairs | G, ± | G, + pairs | B, ± | B, + pairs |", "|---|---|---|---|---|---|---|"]
    tot = {}
    for name, lh in LANE_H.items():
        r = res[name]; cells = []
        for s in ("R", "G", "B"):
            for route in ("pm", "pair"):
                eur = r[route] * lh * SETTING_FACTOR[s] * EUR_PER_LANE_H
                tot[(s, route)] = tot.get((s, route), 0) + eur; cells.append(f"{eur:,.0f}")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines.append("| **five** | " + " | ".join(f"**{tot[(s, rt)]:,.0f}**" for s in ("R", "G", "B") for rt in ("pm", "pair")) + " |")
    res["_price_eur"] = {f"{s}_{rt}": round(v, 1) for (s, rt), v in tot.items()}
    json.dump(res, open(os.path.join(a.out, "counts.json"), "w", encoding="utf-8"), indent=1)
    text = "\n".join(lines)
    open(os.path.join(a.out, "counts.md"), "w", encoding="utf-8").write(
        "# Hessians for a semi-diagonal quartic force field, with the point group (probes/qff_symmetry_count.py)\n\n" + text + "\n")
    print(text)


if __name__ == "__main__":
    main()
