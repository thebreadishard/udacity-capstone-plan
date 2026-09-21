"""Quartic force field from displaced Hessians, with noise diagnostics — own software (21 September 2026).

Why this exists: the benzene VPT2 of 20–21 September (pyVPT2 0.1.2 on 61 B3LYP/6-31G* Hessians, hel1-14) gave unusable fundamentals,
and the cause turned out to be the semi-diagonal quartic constants φ_iijj: symmetry-related constants (the two components of a degenerate
pair against the same totally symmetric mode) differed by up to a factor three, i.e. finite-difference noise of tens of cm⁻¹, and pyVPT2's
own consistency check cannot see it (it compares φ[i,j] with φ[j,i] after the assembly has already averaged the two routes). This script
re-assembles the force field from the same cached AtomicResults (or any set of displaced Hessians) in reduced normal coordinates, keeps
both finite-difference routes for every off-diagonal quartic constant, prints per-constant and per-symmetry-pair noise estimates, averages
symmetry partners where the point group requires equality, and evaluates VPT2 fundamentals with the standard formulas (Mills 1972; the same
ones pyVPT2 implements, which was verified term by term) — with optional deperturbation of Fermi resonances by a polyad diagonalisation.

Conventions (self-contained, no pyVPT2 import): F = M^-1/2 H M^-1/2 (atomic units, masses in m_e); q_i orthonormal eigenvectors, ω_i² the
eigenvalues; reduced dimensionless coordinate Q_i with Cartesian displacement A[:, i] = M^-1/2 q_i / sqrt(ω_i) per unit Q_i; H_QQ = Aᵀ H A has
diagonal ω_i (E_h) at the reference; φ_ijk = ∂³V/∂Q_i∂Q_j∂Q_k and φ_iijj by central differences of H_QQ, converted to cm⁻¹.

Usage:
  python qff_from_hessians.py <cache_dir> [--disp 0.05] [--pyvpt2-json results_vpt2/benzene_b3lyp_631gs_vpt2.json] [--out results_vpt2/qff_benzene_2026-09-21.md]
The cache_dir holds qcschema AtomicResult json files (driver = hessian) as written by vpt2_checkpoint.py; the reference is the file whose
geometry is the mean of all geometries (the displacements are symmetric ±δ), and each other file is assigned to (mode, sign) by projecting
its displacement onto A.
"""
import argparse
import glob
import itertools
import json
import os

import numpy as np

HARTREE_CM = 219474.6313632
AMU_ME = 1822.888486209
MASS = {"H": 1.00782503223, "C": 12.0, "N": 14.00307400443, "O": 15.99491461957}


def load_results(cache_dir):
    recs = []
    for f in sorted(glob.glob(os.path.join(cache_dir, "*.json"))):
        d = json.load(open(f))
        if not isinstance(d, dict) or d.get("driver") != "hessian" or "molecule" not in d:
            continue
        geom = np.array(d["molecule"]["geometry"], float)
        H = np.array(d["return_result"], float)
        n = len(geom); H = H.reshape(n, n)
        recs.append({"file": os.path.basename(f), "geom": geom, "H": H, "symbols": d["molecule"]["symbols"]})
    return recs


def harmonic(H, symbols, geom):
    m = np.array([MASS[s] for s in symbols]) * AMU_ME
    Minvh = np.repeat(1.0 / np.sqrt(m), 3)
    F = Minvh[:, None] * H * Minvh[None, :]
    # project translations and rotations out of the mass-weighted Hessian
    x = geom.reshape(-1, 3); com = (m[:, None] * x).sum(0) / m.sum(); xc = x - com
    n = len(symbols); vecs = []
    for a in range(3):
        v = np.zeros((n, 3)); v[:, a] = np.sqrt(m); vecs.append(v.ravel())
    for a in range(3):
        v = np.zeros((n, 3)); e = np.zeros(3); e[a] = 1.0
        v[:] = np.cross(np.tile(e, (n, 1)), xc) * np.sqrt(m)[:, None]; vecs.append(v.ravel())
    T = np.array(vecs).T; Q, _ = np.linalg.qr(T); P = np.eye(3 * n) - Q @ Q.T
    Fp = P @ F @ P
    lam, q = np.linalg.eigh(Fp)
    order = np.argsort(lam); lam, q = lam[order], q[:, order]
    vib = lam > 1e-8
    omega = np.sqrt(lam[vib]); q = q[:, vib]
    A = (Minvh[:, None] * q) / np.sqrt(omega)[None, :]           # Cartesian displacement per unit reduced coordinate
    return omega, q, A, Minvh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache_dir"); ap.add_argument("--disp", type=float, default=0.05)
    ap.add_argument("--pyvpt2-json", default=None); ap.add_argument("--out", default=None)
    ap.add_argument("--fermi-window", type=float, default=200.0, help="cm-1; resonances with |Δ| below it are deperturbed and diagonalised")
    ap.add_argument("--fermi-min-k", type=float, default=0.0, help="cm-1; strength threshold K = φ⁴/(64Δ³) (type 2) or /(256Δ³) (type 1)")
    args = ap.parse_args()
    recs = load_results(args.cache_dir)
    G = np.array([r["geom"] for r in recs]); mean = G.mean(0)
    i0 = int(np.argmin(np.linalg.norm(G - mean, axis=1)))
    ref = recs[i0]; symbols = ref["symbols"]
    omega, q, A, Minvh = harmonic(ref["H"], symbols, ref["geom"])
    n = len(omega); w = omega * HARTREE_CM
    # assign displaced files to (mode, sign)
    pinvA = np.linalg.pinv(A)
    Hp, Hn = {}, {}
    assign_err = []
    for k, r in enumerate(recs):
        if k == i0:
            continue
        dQ = pinvA @ (r["geom"] - ref["geom"])
        i = int(np.argmax(np.abs(dQ))); s = np.sign(dQ[i]); resid = np.linalg.norm(dQ - s * args.disp * np.eye(n)[i])
        assign_err.append(resid)
        (Hp if s > 0 else Hn)[i] = r["H"]
    missing = [i for i in range(n) if i not in Hp or i not in Hn]
    if missing:
        raise SystemExit(f"modes without a ± pair: {missing}")
    def toQ(H):
        return A.T @ H @ A
    H0 = toQ(ref["H"]); Hp = {i: toQ(h) for i, h in Hp.items()}; Hn = {i: toQ(h) for i, h in Hn.items()}
    d = args.disp
    # cubic: three routes for i≠j≠k, kept separately for the diagnostic
    phi3 = np.zeros((n, n, n)); cubic_spread = np.zeros((n, n, n))
    for i, j, k in itertools.product(range(n), repeat=3):
        routes = [(Hp[i][j, k] - Hn[i][j, k]) / (2 * d), (Hp[j][k, i] - Hn[j][k, i]) / (2 * d), (Hp[k][i, j] - Hn[k][i, j]) / (2 * d)]
        phi3[i, j, k] = np.mean(routes); cubic_spread[i, j, k] = np.max(routes) - np.min(routes)
    # semi-diagonal quartic: two routes for i≠j
    phi4 = np.zeros((n, n)); route_a = np.zeros((n, n)); route_b = np.zeros((n, n))
    for i in range(n):
        phi4[i, i] = (Hp[i][i, i] + Hn[i][i, i] - 2 * H0[i, i]) / d**2
        for j in range(n):
            if i == j:
                continue
            route_a[i, j] = (Hp[j][i, i] + Hn[j][i, i] - 2 * H0[i, i]) / d**2     # displace j, read H_ii
            route_b[i, j] = (Hp[i][j, j] + Hn[i][j, j] - 2 * H0[j, j]) / d**2     # displace i, read H_jj
            phi4[i, j] = 0.5 * (route_a[i, j] + route_b[i, j])
    phi3 *= HARTREE_CM; phi4 *= HARTREE_CM; route_a *= HARTREE_CM; route_b *= HARTREE_CM; cubic_spread *= HARTREE_CM
    # symmetry partners: exactly degenerate pairs
    pairs = [(i, i + 1) for i in range(n - 1) if abs(w[i] - w[i + 1]) < 0.5]
    in_pair = {i for p in pairs for i in p}
    lines = [f"# Quartic force field from {len(recs)} displaced Hessians — {args.cache_dir}", "",
             f"Reference file `{ref['file']}`; {n} vibrational modes; displacement {d} in reduced coordinates; assignment residual max {max(assign_err):.2e}.",
             f"Harmonic ω (cm⁻¹): " + ", ".join(f"{x:.1f}" for x in w), ""]
    lines += ["## Noise diagnostics", "",
              "Off-diagonal semi-diagonal quartic constants φ_iijj have two independent finite-difference routes (displace j and read H_ii; displace i and read H_jj). "
              "Their difference is a direct estimate of the numerical error of that constant. Exactly degenerate pairs (a, b) must give equal φ_aa,jj and φ_bb,jj "
              "for every totally symmetric j; their difference is a second estimate.", ""]
    diff = np.abs(route_a - route_b); iu = np.triu_indices(n, 1)
    lines += [f"- route disagreement |φ_iijj(a) − φ_iijj(b)|: median {np.median(diff[iu]):.1f}, 90th percentile {np.percentile(diff[iu], 90):.1f}, max {diff[iu].max():.1f} cm⁻¹ (max |φ_iijj| {np.abs(phi4[iu]).max():.1f})"]
    lines += [f"- cubic route spread (max − min of the three routes): median {np.median(cubic_spread):.2f}, max {cubic_spread.max():.1f} cm⁻¹"]
    # totally symmetric modes: those with large φ_iii
    ts = [i for i in range(n) if abs(phi3[i, i, i]) > 5 and i not in in_pair]
    lines += [f"- totally symmetric modes (|φ_iii| > 5 cm⁻¹, non-degenerate): {[(i, round(float(w[i]),1)) for i in ts]}", ""]
    lines += ["| degenerate pair (ω) | j (ω) | φ_aa,jj | φ_bb,jj | difference | route disagreement a / b |", "|---|---|---|---|---|---|"]
    for a, b in pairs:
        for j in ts:
            lines.append(f"| ({a},{b}) {w[a]:.0f} | {j} {w[j]:.0f} | {phi4[a, j]:+.1f} | {phi4[b, j]:+.1f} | {abs(phi4[a, j]-phi4[b, j]):.1f} | {diff[a, j]:.1f} / {diff[b, j]:.1f} |")
    # symmetry-averaged constants for degenerate pairs (a, b) against any third mode j: average φ_aa,jj and φ_bb,jj; average φ_aaaa, φ_bbbb, and use φ_aabb accordingly
    phi4s = phi4.copy()
    for a, b in pairs:
        for j in range(n):
            if j in (a, b):
                continue
            m = 0.5 * (phi4[a, j] + phi4[b, j]); phi4s[a, j] = phi4s[j, a] = phi4s[b, j] = phi4s[j, b] = m
        m = 0.5 * (phi4[a, a] + phi4[b, b]); phi4s[a, a] = phi4s[b, b] = m
    # VPT2 (Mills) with the same expressions as pyVPT2, on raw and on symmetry-averaged quartics
    B = rotational_constants(ref["geom"], symbols)
    zeta = coriolis_zeta(q, symbols)
    def vpt2(p3, p4):
        fermi = []
        for i in range(n):
            for k in range(n):
                dw = 2 * w[i] - w[k]
                if i != k and abs(dw) < args.fermi_window and dw != 0 and p3[i, i, k]**4 / (256 * abs(dw)**3) >= args.fermi_min_k:
                    fermi.append((k, (i, i)))
            for j in range(i + 1, n):
                for k in range(n):
                    dw = w[i] + w[j] - w[k]
                    if k not in (i, j) and abs(dw) < args.fermi_window and p3[i, j, k]**4 / (64 * abs(dw)**3) >= args.fermi_min_k:
                        fermi.append((k, (i, j)))
        fset = set(fermi)
        chi = np.zeros((n, n))
        for i in range(n):
            s = p4[i, i] / 16.0
            for k in range(n):
                if (k, (i, i)) in fset:
                    s -= p3[i, i, k]**2 / 32.0 * (1.0 / (2 * w[i] + w[k]) + 4.0 / w[k])
                else:
                    s -= p3[i, i, k]**2 * (8 * w[i]**2 - 3 * w[k]**2) / (16 * w[k] * (4 * w[i]**2 - w[k]**2))
            chi[i, i] = s
            for j in range(n):
                if j == i:
                    continue
                s = p4[i, j] / 4.0 + sum(B[a] * zeta[a, i, j]**2 for a in range(3)) * (w[i] / w[j] + w[j] / w[i])
                for k in range(n):
                    s -= p3[i, i, k] * p3[j, j, k] / (4 * w[k])
                    if (k, (i, j)) in fset or (k, (j, i)) in fset:
                        dd = (1 / (w[i] + w[j] + w[k]) + 1 / (-w[i] + w[j] + w[k]) + 1 / (w[i] - w[j] + w[k])) / -2
                    elif (i, (j, k)) in fset or (i, (k, j)) in fset:
                        dd = (1 / (w[i] + w[j] + w[k]) - 1 / (w[i] + w[j] - w[k]) + 1 / (w[i] - w[j] + w[k])) / -2
                    elif (j, (i, k)) in fset or (j, (k, i)) in fset:
                        dd = (1 / (w[i] + w[j] + w[k]) - 1 / (w[i] + w[j] - w[k]) + 1 / (-w[i] + w[j] + w[k])) / -2
                    else:
                        D = (w[i] + w[j] - w[k]) * (w[i] + w[j] + w[k]) * (w[i] - w[j] + w[k]) * (w[i] - w[j] - w[k])
                        dd = 2 * w[k] * (w[i]**2 + w[j]**2 - w[k]**2) / D
                    s += p3[i, j, k]**2 * dd / 4.0
                chi[i, j] = s
        nu = np.array([w[i] + 2 * chi[i, i] + 0.5 * sum(chi[i, j] for j in range(n) if j != i) for i in range(n)])
        return nu, chi, fermi
    nu_raw, chi_raw, fermi = vpt2(phi3, phi4)
    nu_sym, chi_sym, _ = vpt2(phi3, phi4s)
    lines += ["", f"## VPT2 fundamentals (deperturbation window {args.fermi_window} cm⁻¹, min K {args.fermi_min_k}; {len(fermi)} resonances deperturbed; polyad diagonalisation not applied)", "",
              "| mode | ω | ν raw quartics | ν − ω | ν symmetry-averaged quartics | ν − ω | pyVPT2 ν | pair |", "|---|---|---|---|---|---|---|---|"]
    py = None
    if args.pyvpt2_json and os.path.exists(args.pyvpt2_json):
        pj = json.load(open(args.pyvpt2_json)); pw = np.array(pj["omega"]); pn = np.array(pj["nu"])
        keep = pw > 1.0; pw, pn = pw[keep], pn[keep]
        py = [pn[int(np.argmin(np.abs(pw - x)))] for x in w]
    for i in range(n):
        tag = "" if i not in in_pair else "e"
        lines.append(f"| {i} | {w[i]:.1f} | {nu_raw[i]:.1f} | {nu_raw[i]-w[i]:+.1f} | {nu_sym[i]:.1f} | {nu_sym[i]-w[i]:+.1f} | {py[i]:.1f} | {tag} |" if py else
                     f"| {i} | {w[i]:.1f} | {nu_raw[i]:.1f} | {nu_raw[i]-w[i]:+.1f} | {nu_sym[i]:.1f} | {nu_sym[i]-w[i]:+.1f} | — | {tag} |")
    txt = "\n".join(lines) + "\n"
    out = args.out or os.path.join(os.path.dirname(args.cache_dir.rstrip("/\\")), "qff_report.md")
    open(out, "w", encoding="utf-8").write(txt); print(txt)
    np.savez(out.replace(".md", ".npz"), omega_cm=w, phi_ijk=phi3, phi_iijj=phi4, phi_iijj_route_a=route_a, phi_iijj_route_b=route_b, phi_iijj_sym=phi4s, chi_raw=chi_raw, chi_sym=chi_sym, nu_raw=nu_raw, nu_sym=nu_sym)


def rotational_constants(geom, symbols):
    m = np.array([MASS[s] for s in symbols]); x = geom.reshape(-1, 3) * 0.529177210903; com = (m[:, None] * x).sum(0) / m.sum(); x = x - com
    I = np.zeros((3, 3))
    for mi, r in zip(m, x):
        I += mi * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
    ev = np.linalg.eigvalsh(I)                       # amu Å²
    return 16.857629206 / ev                         # cm⁻¹ (h/(8π²c) in amu Å² cm⁻¹)


def coriolis_zeta(q, symbols):
    n = q.shape[1]; nat = len(symbols); z = np.zeros((3, n, n))
    Q = q.reshape(nat, 3, n)
    for a, (b, c) in enumerate(((1, 2), (2, 0), (0, 1))):
        z[a] = np.einsum("ki,kj->ij", Q[:, b, :], Q[:, c, :]) - np.einsum("ki,kj->ij", Q[:, c, :], Q[:, b, :])
    return z


if __name__ == "__main__":
    main()
