"""Sparse-probe count under the locality prior of E8 (24 September 2026; pre-registration PreRegistration_2026-09-24_Sparse_Probe_Count.md).

E8 read the coupled-cluster correction ΔH as a force-constant correction ΔF supported on pattern (d): diagonal, pairs of primitives sharing an atom,
bond–bond pairs in the same ring, and pairs two bonds apart. If ΔF has m_d free entries, then each probe (one displacement direction, two gradients)
gives 3N linear equations for them, and p = ceil(m_d / 3N) probes determine ΔF by count (conditioning aside — plan 06's recovery theorems are the
rigorous side). This script counts, for every corpus molecule with a geometry: N, 3N, the number of primitives (bonds, angles, dihedrals from the
bond graph, as geomeTRIC builds them, minus nothing — an over-count of the non-redundant set, so p is an upper bound), m_c and m_d, p_c and p_d,
and the saving 3N / p against the plain finite-difference count 3N (X22's 2M + 1 without symmetry). No compute beyond seconds of numpy; no run is
touched.

Usage: python e8_sparse_probe_count.py [--corpus <molecules dir>] [--out <prefix>]
"""
import argparse
import glob
import itertools
import json
import math
import os

import numpy as np

BOHR = 0.529177210903
COV = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "S": 1.05, "F": 0.57, "Cl": 1.02, "Br": 1.20}


def bond_graph(symbols, coords_bohr):
    x = np.asarray(coords_bohr) * BOHR; n = len(symbols); adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(x[i] - x[j]) < 1.2 * (COV.get(symbols[i], 0.75) + COV.get(symbols[j], 0.75)):
                adj[i].add(j); adj[j].add(i)
    return adj


def rings(adj, max_len=7):
    found = set(); n = len(adj)
    for start in range(n):
        stack = [(start, [start])]
        while stack:
            v, path = stack.pop()
            for w in adj[v]:
                if w == start and len(path) >= 3:
                    found.add(frozenset(path))
                elif w not in path and len(path) < max_len and w > start:
                    stack.append((w, path + [w]))
    return [r for r in found if 5 <= len(r) <= max_len]


def primitives(adj, dihedrals=True):
    """Bonds, angles, dihedrals of the bond graph: atom sets (frozensets) and a kind tag."""
    prims = []
    n = len(adj)
    for i in range(n):
        for j in adj[i]:
            if i < j:
                prims.append(("bond", frozenset((i, j))))
    for j in range(n):
        for i, k in itertools.combinations(sorted(adj[j]), 2):
            prims.append(("angle", frozenset((i, j, k))))
    for j in (range(n) if dihedrals else ()):
        for k in adj[j]:
            if j < k:
                for i in adj[j] - {k}:
                    for l in adj[k] - {j}:
                        if i != l:
                            prims.append(("dihedral", frozenset((i, j, k, l))))
    return prims


def pattern_counts(symbols, coords_bohr, dihedrals=True):
    adj = bond_graph(symbols, coords_bohr); R = rings(adj); prims = primitives(adj, dihedrals); n_p = len(prims)
    atoms = [p[1] for p in prims]
    ring_of_bond = {}
    for k, (kind, a) in enumerate(prims):
        if kind == "bond":
            for ri, r in enumerate(R):
                if a <= r:
                    ring_of_bond.setdefault(k, set()).add(ri)
    m_a = n_p; m_b = m_c = m_d = n_p          # diagonal counted once
    for i in range(n_p):
        for j in range(i + 1, n_p):
            share = bool(atoms[i] & atoms[j])
            ringp = i in ring_of_bond and j in ring_of_bond and bool(ring_of_bond[i] & ring_of_bond[j])
            two = (not share) and any(b in adj[a] for a in atoms[i] for b in atoms[j])
            if share:
                m_b += 1; m_c += 1; m_d += 1
            elif ringp:
                m_c += 1; m_d += 1
            elif two:
                m_d += 1
    return dict(n_prims=n_p, n_bonds=sum(1 for p in prims if p[0] == "bond"), n_rings=len(R), m_a=m_a, m_b=m_b, m_c=m_c, m_d=m_d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modules", "05_support_predictor", "corpus", "molecules"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_m1", "e8_benzene_ccpvdz", "sparse_probe_count_2026-09-24"))
    a = ap.parse_args()
    import csv
    names = {}
    mp = os.path.join(a.corpus, "..", "manifest.csv")
    if os.path.exists(mp):
        names = {r["id"]: r["name"] for r in csv.DictReader(open(mp, encoding="utf-8"))}
    rows = []
    for gpath in sorted(glob.glob(os.path.join(a.corpus, "*", "geometry.json"))):
        mid = os.path.basename(os.path.dirname(gpath)); g = json.load(open(gpath)); sym = g["symbols"]; x = np.array(g["coords_bohr"]); N = len(sym)
        name = names.get(mid, "?")
        c = pattern_counts(sym, x); tN = 3 * N; entries = tN * (tN + 1) // 2
        p_c = math.ceil(c["m_c"] / tN); p_d = math.ceil(c["m_d"] / tN)
        c2 = pattern_counts(sym, x, dihedrals=False); p_d2 = math.ceil(c2["m_d"] / tN)
        rows.append(dict(id=mid, name=name, N=N, threeN=tN, dH_entries=entries, **c, p_c=p_c, p_d=p_d, saving_c=tN / p_c, saving_d=tN / p_d, saving_full_fd=1.0,
                         m_d_over_entries=c["m_d"] / entries, n_prims_no_dih=c2["n_prims"], m_d_no_dih=c2["m_d"], p_d_no_dih=p_d2, saving_d_no_dih=tN / p_d2))
    N = np.array([r["N"] for r in rows]); md = np.array([r["m_d"] for r in rows]); sd = np.array([r["saving_d"] for r in rows]); sd2 = np.array([r["saving_d_no_dih"] for r in rows])
    fit = np.polyfit(N, md, 1); fit_s = np.polyfit(N, sd, 1); fit_s2 = np.polyfit(N, sd2, 1)
    out = dict(date="2026-09-24", n_molecules=len(rows), fit_m_d_vs_N=dict(slope=float(fit[0]), intercept=float(fit[1])),
               fit_saving_d_vs_N=dict(slope=float(fit_s[0]), intercept=float(fit_s[1])), rows=rows)
    json.dump(out, open(a.out + ".json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    # table: by size class
    md_lines = [f"# Sparse-probe count under the locality prior — {len(rows)} corpus molecules (2026-09-24)", "",
                "m_d = free entries of ΔF on pattern (d) (bond-graph primitives: bonds, angles, dihedrals — an over-count of the non-redundant set, so p is an upper "
                "bound); p_d = ceil(m_d / 3N) probes by count; saving = 3N / p_d against plain finite differences (3N probes).", "",
                "| size class (N atoms) | molecules | m_d / ΔH entries (median) | p_d (median, range) | 3N (median) | saving 3N / p_d (median, range) | bonds+angles only: p_d, saving (median) |", "|---|---|---|---|---|---|---|"]
    for lo, hi in ((10, 15), (16, 20), (21, 25), (26, 30), (31, 40)):
        sel = [r for r in rows if lo <= r["N"] <= hi]
        if not sel:
            continue
        pd_ = [r["p_d"] for r in sel]; sv = [r["saving_d"] for r in sel]
        md_lines.append(f"| {lo}–{hi} | {len(sel)} | {np.median([r['m_d_over_entries'] for r in sel]):.2f} | {int(np.median(pd_))} ({min(pd_)}–{max(pd_)}) | "
                        f"{int(np.median([r['threeN'] for r in sel]))} | {np.median(sv):.1f} ({min(sv):.1f}–{max(sv):.1f}) | {int(np.median([r['p_d_no_dih'] for r in sel]))}, {np.median([r['saving_d_no_dih'] for r in sel]):.1f} |")
    md_lines += ["", f"Linear fits over the {len(rows)} molecules: m_d ≈ {fit[0]:.1f} N {'+' if fit[1] >= 0 else '−'} {abs(fit[1]):.0f}; saving ≈ {fit_s[0]:.3f} N {'+' if fit_s[1] >= 0 else '−'} {abs(fit_s[1]):.2f}.",
                 f"Extrapolation by the fits (count only): N = 50 → saving {np.polyval(fit_s, 50):.1f}; N = 100 → {np.polyval(fit_s, 100):.1f}; N = 200 → {np.polyval(fit_s, 200):.1f}.",
                 f"Bonds + angles only (lower bound of the primitive set): saving ≈ {fit_s2[0]:.3f} N {'+' if fit_s2[1] >= 0 else '−'} {abs(fit_s2[1]):.2f}; N = 50 → {np.polyval(fit_s2, 50):.1f}; N = 100 → {np.polyval(fit_s2, 100):.1f}; N = 200 → {np.polyval(fit_s2, 200):.1f}.", "",
                 "Named molecules:", "", "| molecule | N | 3N | primitives (with / without dihedrals) | m_c | m_d | p_c | p_d | saving_d | p_d, saving without dihedrals |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["name"] in ("benzene", "naphthalene", "anthracene", "pyrene", "phenanthrene", "coronene", "1-naphthol", "2-phenylpyridine", "biphenylene+CH3", "carbazole+SH"):
            md_lines.append(f"| {r['name']} | {r['N']} | {r['threeN']} | {r['n_prims']} / {r['n_prims_no_dih']} | {r['m_c']} | {r['m_d']} | {r['p_c']} | {r['p_d']} | {r['saving_d']:.1f} | {r['p_d_no_dih']}, {r['saving_d_no_dih']:.1f} |")
    open(a.out + ".md", "w", encoding="utf-8").write("\n".join(md_lines) + "\n")
    print("\n".join(md_lines))


if __name__ == "__main__":
    main()
