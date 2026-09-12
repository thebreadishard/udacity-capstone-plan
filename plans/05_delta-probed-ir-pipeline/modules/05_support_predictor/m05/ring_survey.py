#!/usr/bin/env python
"""Module 05 — ring survey of the Hessian QM9 vacuum split from geometry alone (no SMILES download needed).
Bonds are perceived from interatomic distances (covalent radii, tolerance 0.45 A); rings from the cycle basis of the
bond graph; an 'aromatic six-ring' is a six-membered ring of carbon atoms each with exactly three bonded neighbours
(sp2 proxy) and ring atoms coplanar within 0.1 A (RMS distance to the best plane). Prints, per molecule class, counts
and writes the label list of molecules with at least one aromatic six-ring (the candidate pool for the recomputed
B3LYP subset; the RECIPE fixes the size later by dated note). Run:  python ring_survey.py"""
import collections, json
from datetime import datetime
from pathlib import Path
import numpy as np
import pyarrow as pa, pyarrow.ipc as ipc

HERE = Path(__file__).resolve().parent
D = HERE.parent / "data" / "hessian_qm9" / "hessian_qm9_DatasetDict" / "vacuum"
OUT = HERE.parent / "out"
COV = {1: 0.31, 6: 0.76, 7: 0.71, 8: 0.66, 9: 0.57}   # covalent radii, Angstrom (Cordero et al. 2008 values as commonly tabulated)
TOL = 0.45; PLANAR_RMS = 0.10
BOHR = 0.529177210903


def bonds(Z, X):
    n = len(Z); d = np.linalg.norm(X[:, None] - X[None], axis=-1)
    r = np.array([COV[z] for z in Z]); cut = r[:, None] + r[None] + TOL
    A = (d < cut) & ~np.eye(n, dtype=bool)
    return A


def cycle_basis(A):
    """Fundamental cycles of an undirected graph from a recursive DFS: every back edge (u, v) with v an ancestor of u
    on the current DFS path closes one cycle = the path slice from v to u. Returns a list of node lists (deduplicated)."""
    n = A.shape[0]; nbrs = [list(map(int, np.nonzero(A[u])[0])) for u in range(n)]
    visited = [False] * n; on_path = [-1] * n; path = []; found = {}

    def dfs(u, parent):
        visited[u] = True; on_path[u] = len(path); path.append(u)
        for v in nbrs[u]:
            if v == parent:
                continue
            if on_path[v] >= 0:                      # back edge to an ancestor: close the cycle
                cyc = path[on_path[v]:]
                found.setdefault(frozenset(cyc), list(cyc))
            elif not visited[v]:
                dfs(v, u)
        path.pop(); on_path[u] = -1

    for r in range(n):
        if not visited[r]:
            dfs(r, -1)
    return list(found.values())


def planar_rms(P):
    c = P - P.mean(0); _, s, vt = np.linalg.svd(c, full_matrices=False)
    return float(np.sqrt(np.mean((c @ vt[2]) ** 2)))


def main():
    shards = sorted(D.glob("data-*.arrow"))
    stats = collections.Counter(); arom_labels = []; conj_labels = []; ring_sizes = collections.Counter(); arom_n = collections.Counter(); posunit = None
    for s in shards:
        tab = ipc.open_stream(pa.memory_map(str(s))).read_all()
        cols = {k: tab.column(k).to_pylist() for k in ("atomic_numbers", "positions", "label")}
        for Z, P, lab in zip(cols["atomic_numbers"], cols["positions"], cols["label"]):
            Z = np.array(Z); P = np.array(P, float)
            if posunit is None:   # decide Angstrom vs Bohr from the shortest C-H / heavy-atom distance
                dmin = np.min(np.linalg.norm(P[:, None] - P[None], axis=-1) + np.eye(len(Z)) * 99)
                posunit = "angstrom" if dmin < 1.6 else "bohr"
            if posunit == "bohr": P = P * BOHR
            A = bonds(Z, P); deg = A.sum(1)
            stats["molecules"] += 1
            cyc = cycle_basis(A)
            has_ring = len(cyc) > 0; stats["with_ring"] += has_ring
            n_arom = 0; n_conj = 0
            for c in cyc:
                ring_sizes[len(c)] += 1
                planar = planar_rms(P[c]) < PLANAR_RMS
                if len(c) == 6 and all(Z[i] == 6 and deg[i] == 3 for i in c) and planar:
                    n_arom += 1
                # conjugated-ring proxy: planar 5- or 6-ring of C/N/O in which every carbon has three neighbours (sp2)
                # and every heteroatom at most three (pyridine-, pyrrole-, furan-like); heteroaromatics included
                if len(c) in (5, 6) and planar and all(Z[i] in (6, 7, 8) for i in c) and all(deg[i] == 3 for i in c if Z[i] == 6) and all(deg[i] <= 3 for i in c if Z[i] != 6):
                    n_conj += 1
            if n_arom:
                stats["with_aromatic_six_ring"] += 1; arom_labels.append(lab); arom_n[n_arom] += 1
                if (Z == 6).sum() == 6 and (Z == 1).sum() == 6 and len(Z) == 12: stats["benzene_itself"] += 1
            if n_conj:
                stats["with_conjugated_ring"] += 1; conj_labels.append(lab)
    (HERE.parent / "data" / "hessian_qm9" / "aromatic_sixring_labels.txt").write_text("\n".join(arom_labels), encoding="utf-8")
    (HERE.parent / "data" / "hessian_qm9" / "conjugated_ring_labels.txt").write_text("\n".join(conj_labels), encoding="utf-8")
    out = dict(date=f"{datetime.now():%Y-%m-%d %H:%M}", positions_unit_detected=posunit, covalent_tolerance_A=TOL, planar_rms_A=PLANAR_RMS,
               molecules=stats["molecules"], with_ring=stats["with_ring"], with_aromatic_six_ring=stats["with_aromatic_six_ring"], with_conjugated_ring=stats["with_conjugated_ring"],
               aromatic_rings_per_molecule=dict(sorted(arom_n.items())), ring_size_histogram=dict(sorted(ring_sizes.items())), benzene_itself=stats["benzene_itself"])
    json.dump(out, open(OUT / "HESSIAN_QM9_RINGS.json", "w"), indent=1)
    L = [f"# Hessian QM9 vacuum split — ring survey from geometry — {out['date']}", "",
         f"Positions detected as **{posunit}** (shortest interatomic distance rule). Bonds: covalent radii + {TOL} Å; rings: cycle basis of the bond graph; aromatic six-ring: six carbons, each with three neighbours, coplanar within {PLANAR_RMS} Å RMS.", "",
         f"| molecules | with any ring | with ≥ 1 all-carbon aromatic six-ring | with ≥ 1 planar conjugated 5/6-ring (C/N/O, heteroaromatics included) | benzene itself |", "|---|---|---|---|---|",
         f"| {stats['molecules']:,} | {stats['with_ring']:,} ({stats['with_ring']/stats['molecules']:.1%}) | **{stats['with_aromatic_six_ring']:,} ({stats['with_aromatic_six_ring']/stats['molecules']:.1%})** | **{stats['with_conjugated_ring']:,} ({stats['with_conjugated_ring']/stats['molecules']:.1%})** | {stats['benzene_itself']} |", "",
         "Labels of the conjugated-ring molecules: `data/hessian_qm9/conjugated_ring_labels.txt`.", "",
         "Aromatic six-rings per molecule: " + ", ".join(f"{k}: {v:,}" for k, v in sorted(arom_n.items())) + ".", "",
         "Ring-size histogram (all rings in the cycle basis): " + ", ".join(f"{k}: {v:,}" for k, v in sorted(ring_sizes.items())) + ".", "",
         "Labels of the aromatic-six-ring molecules: `data/hessian_qm9/aromatic_sixring_labels.txt` (the candidate pool; its use and the subset size are the RECIPE's dated note, not this file's)."]
    (OUT / "HESSIAN_QM9_RINGS.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
