"""Sparse recovery of benzene's coupled-cluster correction from a subset of its finite-difference probes (24 September 2026; pre-registration
PreRegistration_2026-09-24_Sparse_Probe_Count.md, section "Reconstruction test").

Data: the 72 CCSD(T)/cc-pVDZ gradients of E8 (36 axis probes k, each ± a 0.005 bohr step) and the B3LYP/cc-pVDZ Hessian recomputed by
e8_cc_locality (not saved) — here the low-level Hessian is replaced by the *full* FD ΔH target as follows: ΔH_true = H_CC(full 72) − H_B3LYP is not
needed; the test is whether ΔF on a compact local basis reproduces the CC Hessian's *columns* from few probes, so the target is H_CC itself minus
its own reference-free part … no: the object recovered is H_CC − H_B3LYP, and H_B3LYP at cc-pVDZ is obtained from the saved E8 read-out only through
its frequencies. To keep the test honest and self-contained, the recovered object is **ΔH = H_CC − H_B3LYP(6-31G*)** where H_B3LYP(6-31G*) is the
corpus Hessian at the same geometry (deck v1). Its basis differs from the CC one, so ΔH carries a basis term too; that does not matter for the
question asked — is a local ΔF recoverable from few probes — but it is stated.

Compact local basis: bonds, angles, one out-of-plane wag per trigonal centre, the ring torsions (benzene: 12 + 18 + 6 + 6 = 42 primitives; the
non-redundant count is 30). Wilson B by numerical differentiation of the coordinate values. Pattern (d) mask on these primitives. Unknowns: the
free entries of symmetric ΔF on the mask. Equations: for each probe k in the subset, ΔH e_k = Bᵀ ΔF B e_k (36 equations). Solve by least squares
(minimum norm when underdetermined). Read-outs against the full-probe ΔH: residual ratio of ΔH, RMS error of the harmonic frequencies of
H_B3LYP + ΔH_rec against those of H_B3LYP + ΔH_true, split in-plane / out-of-plane; as a function of the number of probes, for (i) the first p
axis probes in symmetry order (one atom per orbit first), (ii) random subsets (10 draws).

Usage: python e8_sparse_recovery_benzene.py  (reads results_m1/e8_benzene_ccpvdz and the corpus benzene directory; writes *_recovery_2026-09-24.*)
"""
import itertools
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RCOND = float(os.environ.get("E8_RCOND", "1e-6"))   # relative singular-value cut-off of the least squares; the underdetermined systems need it (24 Sep: rcond=None blew up)
BOHR = 0.529177210903


def bond_graph(symbols, x):
    cov = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "S": 1.05}
    n = len(symbols); adj = [set() for _ in range(n)]; xa = x * BOHR
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(xa[i] - xa[j]) < 1.2 * (cov.get(symbols[i], 0.75) + cov.get(symbols[j], 0.75)):
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
                    found.add(tuple(path))
                elif w not in path and len(path) < max_len and w > start:
                    stack.append((w, path + [w]))
    out = {}
    for r in found:
        if 5 <= len(r) <= max_len:
            out.setdefault(frozenset(r), r)
    return list(out.values())


def coordinates(symbols, x):
    """Compact local basis: (kind, atoms) list and a function value(xflat) -> vector of coordinate values."""
    adj = bond_graph(symbols, x); R = rings(adj); n = len(symbols)
    prims = []
    for i in range(n):
        for j in sorted(adj[i]):
            if i < j:
                prims.append(("bond", (i, j)))
    for j in range(n):
        for i, k in itertools.combinations(sorted(adj[j]), 2):
            prims.append(("angle", (i, j, k)))
    for j in range(n):
        if len(adj[j]) == 3:
            a, b, c = sorted(adj[j]); prims.append(("wag", (j, a, b, c)))
    for ring in R:                                   # ring torsions i-j-k-l along the ring
        L = len(ring)
        for s in range(L):
            i, j, k, l = ring[s], ring[(s + 1) % L], ring[(s + 2) % L], ring[(s + 3) % L]; prims.append(("torsion", (i, j, k, l)))

    def value(xf):
        X = xf.reshape(-1, 3); v = []
        for kind, at in prims:
            if kind == "bond":
                v.append(np.linalg.norm(X[at[0]] - X[at[1]]))
            elif kind == "angle":
                u = X[at[0]] - X[at[1]]; w = X[at[2]] - X[at[1]]
                v.append(np.arccos(np.clip(u @ w / np.linalg.norm(u) / np.linalg.norm(w), -1, 1)))
            elif kind == "wag":
                j, a, b, c = at; nrm = np.cross(X[b] - X[a], X[c] - X[a]); nrm /= np.linalg.norm(nrm)
                v.append(float(nrm @ (X[j] - (X[a] + X[b] + X[c]) / 3)))
            else:
                i, j, k, l = at; b1, b2, b3 = X[j] - X[i], X[k] - X[j], X[l] - X[k]
                n1, n2 = np.cross(b1, b2), np.cross(b2, b3); m1 = np.cross(n1, b2 / np.linalg.norm(b2))
                v.append(np.arctan2(m1 @ n2, n1 @ n2))
        return np.array(v)
    return prims, adj, R, value


def wilson_b(value, xf, h=1e-5):
    q0 = value(xf); B = np.zeros((len(q0), len(xf)))
    for c in range(len(xf)):
        xp = xf.copy(); xp[c] += h; xm = xf.copy(); xm[c] -= h; B[:, c] = (value(xp) - value(xm)) / (2 * h)
    return B


def pattern_d(prims, adj, R):
    n = len(prims); atoms = [set(p[1]) for p in prims]; ring_sets = [set(r) for r in R]
    ring_of_bond = {k: {ri for ri, r in enumerate(ring_sets) if atoms[k] <= r} for k, p in enumerate(prims) if p[0] == "bond"}
    M = np.eye(n, dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            share = bool(atoms[i] & atoms[j])
            ringp = i in ring_of_bond and j in ring_of_bond and bool(ring_of_bond[i] & ring_of_bond[j])
            two = (not share) and any(b in adj[a] for a in atoms[i] for b in atoms[j])
            if share or ringp or two:
                M[i, j] = M[j, i] = True
    return M


def freqs(H, masses):
    sm = np.sqrt(np.repeat(masses, 3)); w = np.linalg.eigvalsh(H / np.outer(sm, sm))
    f = np.sqrt(np.abs(w) / 1822.888486209) * 219474.6313705
    return np.sort(np.where(w < 0, -f, f))


def oop_mask(H, masses, x):
    """Eigenvectors' out-of-plane share for a planar molecule (normal = smallest inertia-like axis)."""
    n = len(masses); xc = x - x.mean(0); ev, R = np.linalg.eigh(xc.T @ xc); nrm = R[:, 0]
    sm = np.sqrt(np.repeat(masses, 3)); w, V = np.linalg.eigh(H / np.outer(sm, sm))
    share = ((V.reshape(n, 3, -1) * nrm[None, :, None]).sum(1) ** 2).sum(0)
    return share > 0.5, np.argsort(w)


def main():
    d = os.path.join(HERE, "results_m1", "e8_benzene_ccpvdz"); cdir = os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181")
    g = json.load(open(os.path.join(cdir, "geometry.json"))); sym = g["symbols"]; x = np.array(g["coords_bohr"]); m = np.array(g["masses_amu"]); n = len(sym)
    step = float(np.load(os.path.join(d, "hessian_ccsd_t.npz"))["step"])
    cols = np.array([(np.load(os.path.join(d, "grads", f"grad_{k:02d}_p.npy")).ravel() - np.load(os.path.join(d, "grads", f"grad_{k:02d}_m.npy")).ravel()) / (2 * step) for k in range(3 * n)]).T
    Hcc = 0.5 * (cols + cols.T)
    Hlow = np.load(os.path.join(cdir, "hessian_b3lyp.npz"))["H_raw"]
    dH_true = Hcc - Hlow
    prims, adj, R, value = coordinates(sym, x); B = wilson_b(value, x.ravel()); M = pattern_d(prims, adj, R)
    kinds = {k: sum(1 for p in prims if p[0] == k) for k in ("bond", "angle", "wag", "torsion")}
    iu = [(i, j) for i in range(len(prims)) for j in range(i, len(prims)) if M[i, j]]
    print(f"benzene: {len(prims)} primitives {kinds}; pattern (d) free entries {len(iu)}; rank of B {np.linalg.matrix_rank(B)}; 3N = {3 * n}; p by count = {int(np.ceil(len(iu) / (3 * n)))}; rcond {RCOND}")
    # design matrix for all probes: for probe k, ΔH e_k = Bᵀ ΔF B e_k → for entry (i,j): contribution B[i]^T ... build per column
    # column k of Bᵀ ΔF B = Σ_ij ΔF_ij B[i] B[j,k]  (+ symmetric term)
    def design(probe_ks):
        rows = []
        for k in probe_ks:
            A = np.zeros((3 * n, len(iu)))
            for c, (i, j) in enumerate(iu):
                A[:, c] = B[i] * B[j, k] + (B[j] * B[i, k] if i != j else 0.0)
            rows.append(A)
        return np.vstack(rows)
    A_all = design(range(3 * n)); y_all = cols.ravel(order="F")  # not symmetrised columns: use the measured columns directly
    y_all = np.concatenate([cols[:, k] - Hlow[:, k] for k in range(3 * n)])
    # ceiling with all probes
    xall, *_ = np.linalg.lstsq(A_all, y_all, rcond=RCOND)
    def assemble(xv):
        F = np.zeros((len(prims), len(prims)))
        for (i, j), v in zip(iu, xv):
            F[i, j] = v; F[j, i] = v
        return B.T @ F @ B
    def readout(dH):
        ft, fr = freqs(Hlow + dH_true, m), freqs(Hlow + dH, m)
        oop, _ = oop_mask(Hlow + dH_true, m, x); oop = oop[np.argsort(np.linalg.eigvalsh((Hlow + dH_true) / np.outer(np.sqrt(np.repeat(m, 3)), np.sqrt(np.repeat(m, 3)))))]
        e = (fr - ft)[6:]; o = oop[6:]
        return dict(residual=float(np.sqrt(np.mean((dH - dH_true) ** 2) / np.mean(dH_true ** 2))), freq_rms=float(np.sqrt(np.mean(e ** 2))),
                    freq_rms_inplane=float(np.sqrt(np.mean(e[~o] ** 2))) if (~o).any() else None, freq_rms_oop=float(np.sqrt(np.mean(e[o] ** 2))) if o.any() else None)
    res = {"n_prims": len(prims), "kinds": kinds, "free_entries": len(iu), "threeN": 3 * n, "ceiling_all_probes": readout(assemble(xall)), "by_probes": {}}
    print("ceiling (all 36 probes, pattern (d), compact basis):", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res["ceiling_all_probes"].items()})
    # symmetry order: one atom per orbit first (atoms 0 = C, 6 = H), then the rest
    order = [0, 1, 2, 18, 19, 20] + [k for k in range(3 * n) if k not in (0, 1, 2, 18, 19, 20)]
    rng = np.random.default_rng(0)
    for p in (6, 9, 11, 12, 15, 18, 24, 30, 36):
        sub = order[:p]; A = design(sub); y = np.concatenate([cols[:, k] - Hlow[:, k] for k in sub]); xs, *_ = np.linalg.lstsq(A, y, rcond=RCOND)
        r_sym = readout(assemble(xs))
        rr = []
        for _ in range(10):
            sub = sorted(rng.choice(3 * n, p, replace=False)); A = design(sub); y = np.concatenate([cols[:, k] - Hlow[:, k] for k in sub]); xs, *_ = np.linalg.lstsq(A, y, rcond=RCOND)
            rr.append(readout(assemble(xs)))
        res["by_probes"][p] = {"symmetry_order": r_sym, "random_median": {k: float(np.median([r[k] for r in rr])) for k in ("residual", "freq_rms")}}
        print(f"p = {p:2d}: symmetry order residual {r_sym['residual']:.2f}, freq RMS {r_sym['freq_rms']:.1f} (in-plane {r_sym['freq_rms_inplane']:.1f}, oop {r_sym['freq_rms_oop']:.1f}) | random median residual {res['by_probes'][p]['random_median']['residual']:.2f}, freq RMS {res['by_probes'][p]['random_median']['freq_rms']:.1f}")
    out = os.path.join(d, "sparse_recovery_benzene_2026-09-24")
    json.dump(res, open(out + ".json", "w", encoding="utf-8"), indent=1, ensure_ascii=False); print("wrote", out + ".json")


if __name__ == "__main__":
    main()
