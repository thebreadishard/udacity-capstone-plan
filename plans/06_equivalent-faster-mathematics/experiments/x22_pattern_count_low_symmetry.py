"""X22 — does the gradient count 2k+1 stay linear for molecules without D2h symmetry? (19 September 2026)

X14/X21 counted the symmetry-blocked products k for eight high-symmetry PAHs (D6h, D2h, C2v): k = 6…23
against 52…682 pairs, linear in the mode count M. The corpus, the substituted PAHs and the cations have
less symmetry. This script takes the corpus's DFT Hessians (B3LYP/6-31G*, `molecules/<id>/`), finds the
abelian symmetry operations the optimised geometry actually has (C2 about the principal axes, mirror
planes through them, inversion), classifies every normal mode by its sign pattern under those
operations (a coarsening of the true irreps: valid as a prior, never finer than the truth), builds the
block-diagonal coupling pattern, and counts the products k with X1c's substitution colouring exactly as
X21 does. It also reports the two limiting cases per molecule: no symmetry (one block, k ≈ M/2 by
substitution) and the found symmetry.

Reading, fixed before the run: the count is linear in M in every case (a dense symmetric M×M matrix needs
at most M gradient directions); what X22 measures is the CONSTANT — how much the symmetry prior still
saves at C2v/Cs/C1 — and whether 2k+1 stays below the energies deck (2 × allowed pairs + M + 1).

Usage: python x22_pattern_count_low_symmetry.py <corpus/molecules dir> [out prefix]
Pure numpy; seconds per molecule.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from x1c_triangular_substitution import (smallest_last_order, lower_pattern, intersection_graph,  # noqa: E402
                                         sequential_colouring, is_proper, recover_by_substitution)

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705
TOL_BOHR = 0.10          # atom-mapping tolerance for a symmetry operation
DEG_CM = 15.0            # modes within this window are symmetry-adapted together (harmless for non-degenerate ones; catches pairs split by a slightly distorted geometry)
CHAR_ONE = 0.90          # |character| above this counts as ±1


def products(P, seed=0):
    """X21's counting, verbatim: substitution colouring of the block pattern, recovery error on a random symmetric matrix."""
    M = P.shape[0]
    H = P.copy(); np.fill_diagonal(H, False)
    pos = smallest_last_order(H)
    Lp = lower_pattern(P, pos)
    Gu = intersection_graph(Lp)
    pos_gu = smallest_last_order(Gu)
    cands = []
    for c, nm in ((sequential_colouring(Gu, list(np.argsort(-Gu.sum(1)))), "largest-first"),
                  (sequential_colouring(Gu, sorted(range(M), key=lambda v: pos_gu[v])), "smallest-last")):
        if is_proper(Gu, c):
            cands.append((int(c.max() + 1), nm, c))
    k, nm, colour = min(cands, key=lambda t: t[0])
    rng = np.random.default_rng(seed)
    R = rng.standard_normal((M, M)); R = (R + R.T) / 2; R[~P] = 0.0
    probes = [R @ (colour == q).astype(float) for q in range(k)]
    err = float(np.abs(recover_by_substitution(P, pos, colour, probes) - R).max())
    return k, nm, err


def normal_modes(H, masses_amu):
    """Mass-weighted eigenvectors of a TR-projected Cartesian Hessian; drops the six (five if linear) lowest |ω|."""
    m = np.repeat(np.asarray(masses_amu) * AMU2AU, 3)
    Hm = H / np.sqrt(np.outer(m, m))
    w, V = np.linalg.eigh(Hm)
    freq = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    order = np.argsort(np.abs(freq))
    n_tr = 6
    keep = np.sort(order[n_tr:])
    return freq[keep], V[:, keep]          # (M,), (3N, M) mass-weighted, orthonormal


def principal_frame(coords, masses):
    com = (coords * masses[:, None]).sum(0) / masses.sum()
    x = coords - com
    I = np.zeros((3, 3))
    for r, mm in zip(x, masses):
        I += mm * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
    w, R = np.linalg.eigh(I)
    return x @ R, w      # rotated coordinates, principal moments


OPS = {
    "C2z": np.diag([-1., -1., 1.]), "C2y": np.diag([-1., 1., -1.]), "C2x": np.diag([1., -1., -1.]),
    "s_xy": np.diag([1., 1., -1.]), "s_xz": np.diag([1., -1., 1.]), "s_yz": np.diag([-1., 1., 1.]),
    "i": -np.eye(3),
}


def atom_map(x, symbols, R, tol=TOL_BOHR):
    """Permutation p with R x[a] == x[p[a]] within tol, same symbol; None if the operation is not a symmetry."""
    y = x @ R.T
    p = np.full(len(x), -1)
    for a in range(len(x)):
        d = np.linalg.norm(x - y[a], axis=1)
        b = int(np.argmin(d))
        if d[b] > tol or symbols[b] != symbols[a] or b in p:
            return None
        p[a] = b
    return p


def rot_z(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0.], [s, c, 0.], [0., 0., 1.]])


def find_ops(coords, symbols, masses):
    """Abelian operations of the geometry in its principal frame. If two principal moments are degenerate the
    in-plane orientation is free: scan it and keep the orientation with the most operations."""
    x, mom = principal_frame(coords, masses)
    frames = [("principal", np.eye(3))]
    rel = np.abs(np.diff(np.sort(mom))) / max(mom.max(), 1e-9)
    if rel.min() < 1e-3:                       # symmetric top (benzene, triphenylene, coronene…)
        # put the unique axis on z, then scan the in-plane angle
        order = np.argsort(mom)
        uniq = 2 if rel[0] < rel[1] else 0     # index (in sorted order) of the unique moment
        perm = [i for i in range(3) if i != order[uniq]] + [order[uniq]]
        Rz = np.eye(3)[:, perm]
        frames = [(f"scan{deg}", Rz @ rot_z(np.deg2rad(deg))) for deg in np.arange(0, 180, 0.5)]
    best = None
    for name, F in frames:
        xf = x @ F
        ops = {}
        for on, R in OPS.items():
            p = atom_map(xf, symbols, R)
            if p is not None:
                ops[on] = (R, p)
        if best is None or len(ops) > len(best[1]):
            best = (xf, ops, F)
    return best


def characters(V, ops, natom):
    """Sign of each mode under each operation: <L_i, Op L_i> with atoms permuted and vectors rotated."""
    M = V.shape[1]
    chars = np.zeros((M, len(ops)))
    for j, (on, (R, p)) in enumerate(ops.items()):
        for i in range(M):
            L = V[:, i].reshape(natom, 3)
            Lt = np.zeros_like(L); Lt[p] = L @ R.T
            chars[i, j] = float(np.dot(L.ravel(), Lt.ravel()))
    return chars


def symmetry_adapt(freq, V, ops, natom):
    """Within each cluster of near-degenerate modes (|Δω| < DEG_CM, chained) rotate the eigenvectors so that
    every abelian operation is diagonal on the cluster: eigh of a random combination of the operation
    matrices C_op = V_cᵀ (Op V_c), which commute. Removes the arbitrary mixing eigh returns inside
    degenerate or accidentally near-degenerate pairs; characters become ±1 where the operations are true."""
    if not ops:
        return V
    M = V.shape[1]
    V = V.copy()
    i = 0
    rng = np.random.default_rng(0)
    while i < M:
        j = i + 1
        while j < M and abs(freq[j] - freq[j - 1]) < DEG_CM:
            j += 1
        if j - i > 1:
            Vc = V[:, i:j]
            A = np.zeros((j - i, j - i))
            for (on, (R, p)) in ops.items():
                OpV = np.zeros_like(Vc)
                for c in range(j - i):
                    L = Vc[:, c].reshape(natom, 3)
                    Lt = np.zeros_like(L); Lt[p] = L @ R.T
                    OpV[:, c] = Lt.ravel()
                C = Vc.T @ OpV
                A += rng.uniform(0.5, 1.5) * (C + C.T) / 2
            _, U = np.linalg.eigh(A)
            V[:, i:j] = Vc @ U
        i = j
    return V


def block_labels(freq, chars):
    """Label per mode: the sign tuple; modes whose character is not ±1 (degenerate) are grouped with their
    frequency-neighbours into one block, which is the coarser but still valid prior."""
    M = len(freq)
    labels = [None] * M
    clean = np.all(np.abs(np.abs(chars) - 1) < (1 - CHAR_ONE), axis=1) if chars.shape[1] else np.ones(M, bool)
    for i in range(M):
        if clean[i]:
            labels[i] = "sgn" + "".join("+" if c > 0 else "-" for c in chars[i])
    # unresolved after symmetry adaptation: the mode may couple with anything (label "any" -> full row in P).
    # Never a block of its own: that would be a prior FINER than the symmetry allows.
    for i in range(M):
        if labels[i] is None:
            labels[i] = "any"
    return labels


def analyse(mol_dir):
    g = json.load(open(mol_dir / "geometry.json"))
    z = np.load(mol_dir / "hessian_b3lyp.npz")
    coords = np.asarray(g["coords_bohr"]); masses = np.asarray(g["masses_amu"]); symbols = g["symbols"]
    freq, V = normal_modes(z["H_projected"], masses)
    M = len(freq)
    xf, ops, F = find_ops(coords, symbols, masses)
    # rotate mode vectors into the same frame as xf: x_frame = x @ Rtot, so vectors transform with the same matrix
    # (V is mass-weighted; the rotation acts per atom on the 3-vector, mass weighting is per atom so it commutes)
    # the rotation coords -> xf, recovered by least squares (mass weighting is per atom, so it commutes with it)
    com = (coords * masses[:, None]).sum(0) / masses.sum()
    A = coords - com
    Rtot, *_ = np.linalg.lstsq(A, xf, rcond=None)
    Vf = np.stack([(V[:, i].reshape(-1, 3) @ Rtot).ravel() for i in range(M)], axis=1)
    Vf = symmetry_adapt(freq, Vf, ops, len(symbols))
    chars = characters(Vf, ops, len(symbols))
    labels = block_labels(freq, chars)
    uniq = sorted(set(labels) - {'any'}); sizes = [labels.count(u) for u in uniq]
    P = np.array([[i == j or labels[i] == labels[j] or 'any' in (labels[i], labels[j]) for j in range(M)] for i in range(M)])
    n_any = labels.count('any')
    k, nm, err = products(P)
    P1 = np.ones((M, M), bool)
    k1, nm1, err1 = products(P1)
    pairs = M * (M - 1) // 2
    allowed = int((P.sum() - M) // 2)
    return dict(id=mol_dir.name, natom=len(symbols), M=M, ops=sorted(ops), n_ops=len(ops), n_blocks=len(uniq),
                block_sizes=sorted(sizes, reverse=True), pairs=pairs, allowed_pairs=allowed,
                k=k, gradients=2 * k + 1, recovery_err=err, k_nosym=k1, gradients_nosym=2 * k1 + 1,
                energies_deck=2 * allowed + M + 1, energies_deck_nosym=2 * pairs + M + 1,
                n_unresolved=n_any, worst_char=float(np.abs(np.abs(chars) - 1).max()) if chars.size else 0.0)


def main():
    mdir = Path(sys.argv[1]); prefix = sys.argv[2] if len(sys.argv) > 2 else str(HERE / "x22_pattern_count_low_symmetry")
    names = {}
    man = mdir.parent / "manifest.csv"
    if man.exists():
        import csv
        names = {r["id"]: r["name"] for r in csv.DictReader(open(man, newline="", encoding="utf-8"))}
    rows = []
    for d in sorted(p for p in mdir.iterdir() if (p / "hessian_b3lyp.npz").exists() and (p / "geometry.json").exists()):
        try:
            r = analyse(d); r["name"] = names.get(d.name, d.name); rows.append(r)
            print(f"{r['name']:28s} N={r['natom']:3d} M={r['M']:4d} ops={r['n_ops']} blocks={r['n_blocks']:2d} "
                  f"k={r['k']:3d} grads={r['gradients']:4d} (nosym {r['gradients_nosym']:4d})  energies {r['energies_deck']:5d}  unresolved={r['n_unresolved']} worst|c|-1={r['worst_char']:.2f} err={r['recovery_err']:.1e}")
        except Exception as e:
            print(f"{d.name}: FAILED {e!r}")
    rows.sort(key=lambda r: r["M"])
    out = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), tol_bohr=TOL_BOHR, deg_cm=DEG_CM, rows=rows)
    json.dump(out, open(prefix + ".json", "w"), indent=1)
    # linear fit gradients vs M, with and without symmetry
    Ms = np.array([r["M"] for r in rows], float)
    if len(rows) >= 3:
        for key in ("gradients", "gradients_nosym", "energies_deck"):
            y = np.array([r[key] for r in rows], float)
            a, b = np.polyfit(Ms, y, 1)
            print(f"fit {key:16s} ~ {a:.2f}*M {b:+.1f}   (ratio to M at the largest: {y[-1]/Ms[-1]:.2f})")
    md = ["# X22 — pattern count without D2h symmetry (" + out["date"] + ")", "",
          "| molecule | N | M | ops found | blocks | k | gradients 2k+1 | gradients, no symmetry | energies deck | recovery err |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['name']} | {r['natom']} | {r['M']} | {r['n_ops']} ({','.join(r['ops'])}) | {r['n_blocks']} | {r['k']} | {r['gradients']} | {r['gradients_nosym']} | {r['energies_deck']} | {r['recovery_err']:.1e} |")
    open(prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", prefix + ".json/.md")


if __name__ == "__main__":
    main()
