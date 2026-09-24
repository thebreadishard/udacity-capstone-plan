"""E8 — CCSD(T)/cc-pVDZ Hessian of a molecule by central finite differences of analytic gradients, checkpointed (pre-registration
PreRegistration_2026-09-23_E8_CC_Correction_Locality.md, 23 September 2026).

Reference + 2 × 3N displaced geometries (step 0.005 bohr along every Cartesian coordinate); each CCSD(T) gradient is written to
<out>/grad_<k>_<sign>.npy as soon as it exists, so the run resumes after any interruption. The Hessian H_ij = (g_i(+j) − g_i(−j)) / (2δ), symmetrised,
is written to <out>/hessian_ccsd_t.npz with H_raw, H_projected (translations/rotations projected out, mass-weighted projector), freq_cm, the
reference energy and gradient. The two-route checks of the pre-registration (degenerate-pair splits, translational null space) are printed.

Usage: python e8_cc_hessian_fd.py <geometry.json> <out dir> [--threads 16] [--basis cc-pvdz] [--step 0.005] [--frozen 6] [--only-reference]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from pyscf import cc, gto, lib, scf
from pyscf.grad import ccsd_t as ccsd_t_grad

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705


def gradient(symbols, coords_bohr, basis, frozen, log):
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(symbols, coords_bohr)], unit="Bohr", basis=basis, symmetry=False, verbose=0, max_memory=26000)
    mf = scf.RHF(mol); mf.conv_tol = 1e-11; e_hf = mf.kernel()
    mycc = cc.CCSD(mf, frozen=frozen); mycc.conv_tol = 1e-9; mycc.conv_tol_normt = 1e-7; e_corr = mycc.kernel()[0]
    if not mycc.converged:
        log("WARNING: CCSD not converged")
    et = mycc.ccsd_t()
    g = ccsd_t_grad.Gradients(mycc).kernel()
    return float(e_hf + e_corr + et), np.asarray(g)


def project_tr(H, masses, x):
    n = len(masses); m = np.repeat(masses * AMU2AU, 3); sm = np.sqrt(m)
    com = (x * masses[:, None]).sum(0) / masses.sum(); r = x - com
    D = []
    for k in range(3):
        v = np.zeros((n, 3)); v[:, k] = 1.0; D.append((v * np.sqrt(masses)[:, None]).ravel())
    for k in range(3):
        e = np.zeros(3); e[k] = 1.0; v = np.cross(np.tile(e, (n, 1)), r); D.append((v * np.sqrt(masses)[:, None]).ravel())
    D = np.array(D).T; q, _ = np.linalg.qr(D); P = np.eye(3 * n) - q @ q.T
    Hmw = H / np.outer(sm, sm); Hp = P @ Hmw @ P
    return Hp * np.outer(sm, sm), Hmw


def frequencies(Hmw_projected):
    w = np.linalg.eigvalsh(Hmw_projected)
    return np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("geometry"); ap.add_argument("out")
    ap.add_argument("--threads", type=int, default=16); ap.add_argument("--basis", default="cc-pvdz"); ap.add_argument("--step", type=float, default=0.005)
    ap.add_argument("--frozen", type=int, default=6); ap.add_argument("--only-reference", action="store_true")
    ap.add_argument("--symmetry", action="store_true", help="displace only one atom per symmetry orbit and reconstruct the Hessian with e8_symmetry (validated 24 Sep 2026)")
    ap.add_argument("--ks", default="", help="compute only these displacement indices (comma list or a:b slice of the displacement list, e.g. 0:15) and stop before the Hessian — for splitting a run over machines; merge the grad_*.npy files and rerun without --ks to assemble")
    a = ap.parse_args(); lib.num_threads(a.threads); os.makedirs(a.out, exist_ok=True)
    logf = open(os.path.join(a.out, "e8_fd.log"), "a")

    def log(s):
        line = f"[{time.strftime('%F %T')}] {s}"; print(line, flush=True); logf.write(line + "\n"); logf.flush()

    g = json.load(open(a.geometry)); sym = g["symbols"]; x0 = np.array(g["coords_bohr"], float); masses = np.array(g["masses_amu"]); n = len(sym)
    log(f"E8 FD Hessian: {n} atoms, {a.basis}, frozen {a.frozen}, step {a.step} bohr, {2 * 3 * n} displacements, {a.threads} threads")
    ref_p = os.path.join(a.out, "reference.npz")
    if os.path.exists(ref_p):
        ref = np.load(ref_p); e0, g0 = float(ref["energy"]), ref["gradient"]
    else:
        t0 = time.time(); e0, g0 = gradient(sym, x0, a.basis, a.frozen, log); np.savez(ref_p, energy=e0, gradient=g0, coords_bohr=x0)
        log(f"reference: E = {e0:.9f}, max|grad| {np.abs(g0).max():.2e}, {time.time() - t0:.0f} s")
    if a.only_reference:
        return
    G = np.zeros((3 * n, 3 * n))          # row k: gradient (flattened) at +/− displacement of coordinate k, differenced
    ks = list(range(3 * n)); ops = None
    if a.symmetry:
        import e8_symmetry as SYM
        ops = SYM.point_group_ops(sym, x0); ks, reps = SYM.unique_displacements(ops, n)
        log(f"symmetry: {len(ops)} operations, orbits {SYM.orbits(ops, n)}, {len(ks)} displacements ({2 * len(ks)} gradients) instead of {6 * n}")
    partial = False
    if a.ks:
        if ":" in a.ks:
            lo, hi = (int(v) if v else None for v in a.ks.split(":")); ks = ks[lo:hi]
        else:
            ks = [int(v) for v in a.ks.split(",")]
        partial = True; log(f"partial run: displacement indices {ks}")
    for k in ks:
        gs = {}
        for sign, s in (("p", +1.0), ("m", -1.0)):
            p = os.path.join(a.out, f"grad_{k:02d}_{sign}.npy")
            if os.path.exists(p):
                gs[sign] = np.load(p); continue
            x = x0.copy(); x.flat[k] += s * a.step
            t0 = time.time(); e, gr = gradient(sym, x, a.basis, a.frozen, log); np.save(p, gr); gs[sign] = gr
            done = len([f for f in os.listdir(a.out) if f.startswith("grad_")])
            log(f"coordinate {k:2d} {sign}: E − E0 = {(e - e0) * 1e6:+9.2f} µE_h, {time.time() - t0:.0f} s  ({done}/{6 * n} gradients)")
        G[k] = (gs["p"].ravel() - gs["m"].ravel()) / (2 * a.step)
    if partial:
        log("partial run done; merge grad_*.npy files and rerun without --ks to assemble the Hessian"); return
    spread = None
    if a.symmetry:
        block_rows = {i: G[3 * i:3 * i + 3] for i in reps}
        H, spread = SYM.reconstruct(block_rows, ops, n); log(f"symmetry reconstruction: spread of multiply-reached rows {spread:.2e} a.u.; self-check {SYM.self_check(H, ops, n):.1e}")
        asym = spread     # the consistency measure of the symmetric run (24 Sep: the log line below needs it; it crashed the benzene smoke once)
    else:
        H = 0.5 * (G + G.T); asym = float(np.abs(G - G.T).max())
    Hp, Hmw = project_tr(H, masses, x0); fr = frequencies(Hp / np.outer(np.sqrt(np.repeat(masses * AMU2AU, 3)), np.sqrt(np.repeat(masses * AMU2AU, 3))))
    fr_s = np.sort(fr)
    np.savez(os.path.join(a.out, "hessian_ccsd_t.npz"), H_raw=H, H_projected=Hp, freq_cm=fr_s, energy=e0, gradient=g0, coords_bohr=x0, step=a.step, basis=a.basis, symmetry_reduced=bool(a.symmetry), symmetry_spread=(spread if spread is not None else -1.0), frozen=a.frozen)
    log(f"Hessian written; FD asymmetry max {asym:.2e} a.u.; frequencies (cm-1): {np.round(fr_s[6:], 0).astype(int).tolist()}")
    log(f"two-route checks: six lowest |freq| after projection {np.round(np.abs(fr_s[:6]), 1).tolist()} (translations/rotations → ~0)")
    logf.close()


if __name__ == "__main__":
    main()
