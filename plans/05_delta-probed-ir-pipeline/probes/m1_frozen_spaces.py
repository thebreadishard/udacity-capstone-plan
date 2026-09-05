#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Probe M1 — frozen spaces (plan 05, Ladder §3 "Frozen spaces — the object, written once";
probes/README item 2; Ladder stop 1).

Can the anchor code (pyscf-forge LNO-CCSD(T)) store its spaces at the reference geometry and
evaluate the correlation energy at displaced geometries in spaces transported by projection —
and is the resulting energy a smooth function of the nuclei?

Arms (Ladder §3):
  A  frozen–frozen : the stored active-occupied set and every fragment's stored LNO spaces,
                     transported to the displaced geometry by projection onto the displaced
                     occupied / virtual space and Löwdin-orthonormalised; no localiser, no
                     LNO construction, no assignment.  (A small override of make_las.)
  B  transported occupied set, fresh LNO spaces built on it (the released code, lo_coeff input).
  C  fresh localiser, fresh LNO spaces (the production energy).

Printed, per point, without a verdict: the continuity diagnostics (smallest singular value of
the occupied overlap C_occ(0)ᵀ S(x) C_occ(x); the largest pre-Löwdin off-diagonal, both halves;
arm C's Pipek–Mezey functional and its overlap with the transported set), E(A) − E(B) and
E(A) − E(C) in µE_h, and wall-clock. The raw energies are NOT printed: they go to a hashed,
sealed JSON (they would make three benzene Δ₂ diagonal elements readable before the note).

Stage 0 is the round trip: at the reference geometry, arm A with reloaded spaces must reproduce
arm C to 10⁻⁹ E_h.

Runs in WSL:  wsl ~/qc05/bin/python plans/05_delta-probed-ir-pipeline/probes/m1_frozen_spaces.py
              [--basis cc-pvdz] [--thresh normal|tight] [--npts 9] [--modes 12,20,6] [--threads 8]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import time
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DRYRUN = os.path.join(HERE, "results_dryrun", "benzene")
OUT = os.path.join(HERE, "results_m1")
THRESH = {"normal": [1e-5, 1e-6], "tight": [1e-6, 1e-7]}
FROZEN_CORE = 6   # benzene: six carbon 1s


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2


# ----------------------------------------------------------------------------- linear algebra
def lowdin(V, S):
    """Symmetric orthonormalisation of the columns of V in the metric S; returns (V_orth, O_pre)."""
    O = V.T @ S @ V
    w, U = np.linalg.eigh(O)
    w = np.maximum(w, 1e-14)
    return V @ (U * (1.0 / np.sqrt(w))) @ U.T, O


def transport(C0, Cspace_x, S_x):
    """Project stored vectors C0 onto span(Cspace_x) (S-metric) and Löwdin-orthonormalise.
    Returns the transported set, the singular values of the overlap M = Cspace_xᵀ S_x C0, and the
    pre-Löwdin overlap matrix O = VᵀSV of the projected set."""
    M = Cspace_x.T @ S_x @ C0
    V = Cspace_x @ M
    Vt, O = lowdin(V, S_x)
    sv = np.linalg.svd(M, compute_uv=False)
    return Vt, sv, O


def complement_within(Cspace_x, Vt, S_x, n_keep):
    """Orthonormal complement of span(Vt) inside span(Cspace_x): n_keep vectors."""
    P_perp = Cspace_x - Vt @ (Vt.T @ S_x @ Cspace_x)
    O = P_perp.T @ S_x @ P_perp
    w, U = np.linalg.eigh(O)
    order = np.argsort(w)[::-1][:n_keep]
    W = P_perp @ U[:, order]
    Wt, _ = lowdin(W, S_x)
    return Wt


def offdiag_max(O):
    A = np.abs(O - np.diag(np.diag(O)))
    return float(A.max()) if A.size else 0.0


# ----------------------------------------------------------------------------- pyscf pieces
def make_mol(symbols, coords_bohr, basis):
    from pyscf import gto
    return gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, coords_bohr)], unit="Bohr", basis=basis,
                 verbose=0, max_memory=24000, symmetry=False)


def run_scf(mol):
    from pyscf import scf
    mf = scf.RHF(mol).density_fit()
    mf.conv_tol = 1e-11
    mf.kernel()
    if not mf.converged:
        raise RuntimeError("SCF did not converge")
    return mf


def pm_localise(mol, orbocc):
    """Pipek–Mezey with Jacobi stability sweeps (the LNO code's own test recipe)."""
    from pyscf import lo
    mlo = lo.PipekMezey(mol, orbocc)
    lo_coeff = mlo.kernel()
    for _ in range(100):
        lo1, stable = mlo.stability_jacobi(return_status=True)
        if stable:
            break
        mlo = lo.PipekMezey(mol, lo1)
        mlo.init_guess = None
        lo_coeff = mlo.kernel()
    return lo_coeff, float(lo.PipekMezey(mol, lo_coeff).cost_function())   # functional of this set (u = identity)


def full_mp2(mf):
    from pyscf import mp
    m = mp.dfmp2.DFMP2(mf, frozen=FROZEN_CORE) if hasattr(mp, "dfmp2") else mp.MP2(mf, frozen=FROZEN_CORE)
    m.verbose = 0
    m.kernel()
    return float(m.e_corr)


def lno_classes():
    from pyscf.lno import LNOCCSD_T

    class RecordingLNOCCSD_T(LNOCCSD_T):
        """Arm B/C: the released code, but every fragment's LAS (orbfrag, frzfrag) is recorded."""
        def kernel(self, eris=None):
            self.recorded = []
            return super().kernel(eris)

        def make_las(self, eris, orbloc, lno_type, lno_param):
            orbfrag, frzfrag, uocc_loc, msg = super().make_las(eris, orbloc, lno_type, lno_param)
            self.recorded.append((np.array(orbfrag), np.array(frzfrag, dtype=int).ravel() if np.ndim(frzfrag) else np.array([], dtype=int), msg))
            return orbfrag, frzfrag, uocc_loc, msg

    class FrozenLNOCCSD_T(LNOCCSD_T):
        """Arm A: make_las returns the stored, transported LAS of each fragment; nothing is rebuilt."""
        def set_transported(self, frags, s1e):
            self._frags = frags      # list of (orbfrag_x, frzfrag, n_occ_act_slice)
            self._s_x = s1e
            return self

        def kernel(self, eris=None):
            self._ifrag = 0
            return super().kernel(eris)

        def make_las(self, eris, orbloc, lno_type, lno_param):
            orbfrag, frzfrag, occ_act, msg = self._frags[self._ifrag]
            self._ifrag += 1
            uocc_loc = orbfrag[:, occ_act].T @ self._s_x @ orbloc
            return orbfrag, (frzfrag if len(frzfrag) else 0), uocc_loc, msg + " [transported]"

    return RecordingLNOCCSD_T, FrozenLNOCCSD_T


def energies_of(mcc, mf, emp2_full):
    """(E_corr LNO-CCSD(T) uncorrected, E_corr MP2-corrected composite, LNO-MP2)."""
    ecc_t = float(mcc.e_corr_ccsd_t)
    ept2 = float(mcc.e_corr_pt2)
    return {"e_scf": float(mf.e_tot), "e_corr_lno_ccsd_t": ecc_t, "e_corr_lno_mp2": ept2,
            "e_corr_mp2_full": emp2_full, "e_corr_composite": ecc_t - ept2 + emp2_full,
            "e_tot_composite": float(mf.e_tot) + ecc_t - ept2 + emp2_full}


# ----------------------------------------------------------------------------- the probe
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--thresh", default="normal", choices=list(THRESH))
    ap.add_argument("--npts", type=int, default=9)
    ap.add_argument("--modes", default="auto", help="comma-separated DFT mode indices: totally symmetric, degenerate, non-symmetric")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--tag", default="")
    ap.add_argument("--resume", action="store_true",
                    help="continue an interrupted run: keep the finished points in the output dir (their rows and sealed "
                         "energies), verify the recomputed frozen-space hash against the saved reference, run only the missing points")
    args = ap.parse_args()
    from pyscf import lib
    lib.num_threads(args.threads)
    Recording, Frozen = lno_classes()

    a = json.load(open(os.path.join(DRYRUN, "stageA.json")))
    z = np.load(os.path.join(DRYRUN, "stageA_hessians.npz"))
    L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    symbols, freq, fam = a["symbols"], np.array(a["freq_low_cm"]), a["families"]
    if args.modes == "auto":
        ts = int(a["totally_symmetric_index"])
        # a degenerate mode: the first CC-stretch pair member; a non-symmetric one: the CH-oop scan mode
        cc_idx = [k for k, f in enumerate(fam) if f == "CC-stretch"]
        deg = cc_idx[0] if cc_idx else 20
        nonsym = 6
        modes = [ts, deg, nonsym]
    else:
        modes = [int(t) for t in args.modes.split(",")]
    out = os.path.join(OUT, f"benzene_{args.basis}_{args.thresh}{args.tag}")
    os.makedirs(out, exist_ok=True)
    qs = np.linspace(-1.0, 1.0, args.npts)
    log(f"M1: benzene {args.basis}, thresholds {THRESH[args.thresh]}, modes {modes} "
        f"({', '.join(f'{freq[m]:.0f} cm⁻¹ {fam[m]}' for m in modes)}), {args.npts} points, {args.threads} threads")

    # ---------------- reference geometry: arm C, record the spaces
    t0 = time.time()
    mol0 = make_mol(symbols, coords0, args.basis)
    mf0 = run_scf(mol0)
    S0 = mf0.get_ovlp()
    nocc = int(np.count_nonzero(mf0.mo_occ))
    C_occ_act0 = mf0.mo_coeff[:, FROZEN_CORE:nocc]
    emp2_0 = full_mp2(mf0)
    prior_rows, prior_points, prior_ref, resumed_note = [], [], None, ""
    if args.resume:
        # The reference localisation and LNO construction are not bit-reproducible between runs (thread order),
        # so a resumed run must RELOAD the saved spaces — which is exactly the pipeline's own path for a frozen object.
        zp = np.load(os.path.join(out, "frozen_spaces_reference.npz"))
        assert np.max(np.abs(zp["coords0"] - coords0)) < 1e-12, "saved reference is for another geometry"
        lo0 = zp["lo0"]
        nfrag = len([k for k in zp.files if k.startswith("orbfrag_")])
        recorded = [(zp[f"orbfrag_{i}"], zp[f"frzfrag_{i}"], f"frag {i} [reloaded]") for i in range(nfrag)]
        prior_rows = json.load(open(os.path.join(out, "m1_rows.json")))["rows"]
        prior_sealed = json.load(open(os.path.join(out, "m1_sealed_energies.json")))
        prior_points, prior_ref = prior_sealed["points"], prior_sealed["reference"]
        E_C0 = prior_ref["C"]
        resumed_note = (f"resumed {datetime.now():%Y-%m-%d %H:%M}: reference spaces reloaded from `frozen_spaces_reference.npz`, "
                        f"{len(prior_rows)} finished points kept from the interrupted run")
        log(resumed_note)
    else:
        lo0, pm0 = pm_localise(mol0, C_occ_act0)
        mccC0 = Recording(mf0, lo0, [[i] for i in range(lo0.shape[1])], frozen=FROZEN_CORE)
        mccC0.lno_thresh = THRESH[args.thresh]; mccC0.verbose = 2
        mccC0.kernel()
        E_C0 = energies_of(mccC0, mf0, emp2_0)
        recorded = mccC0.recorded
    frag_lolist = [[i] for i in range(lo0.shape[1])]
    stored = []
    for orbfrag, frzfrag, msg in recorded:
        n_occfrz = int(np.sum(frzfrag < nocc))          # core + frozen occupied LNOs
        n_virfrz = int(np.sum(frzfrag >= nocc))
        nmo = orbfrag.shape[1]
        occ_act = slice(n_occfrz, nocc)
        vir_act = slice(nocc, nmo - n_virfrz)
        stored.append({"orbfrag": orbfrag, "frzfrag": frzfrag, "n_occfrz": n_occfrz, "n_virfrz": n_virfrz,
                       "occ_act": occ_act, "vir_act": vir_act, "msg": msg})
    t_ref = time.time() - t0
    space_blob = np.concatenate([lo0.ravel()] + [s["orbfrag"].ravel() for s in stored]).tobytes()
    frozen_space_hash = hashlib.sha256(space_blob).hexdigest()
    if not args.resume:
      np.savez(os.path.join(out, "frozen_spaces_reference.npz"), lo0=lo0, coords0=coords0,
             **{f"orbfrag_{i}": s["orbfrag"] for i, s in enumerate(stored)},
             **{f"frzfrag_{i}": s["frzfrag"] for i, s in enumerate(stored)})
    log(f"reference: {'reloaded' if args.resume else 'arm C'} {t_ref:.0f} s; {len(stored)} fragments; sizes "
        f"{[(int(s['occ_act'].stop - s['occ_act'].start), int(s['vir_act'].stop - s['vir_act'].start)) for s in stored][:5]}…; "
        f"frozen-space hash {frozen_space_hash[:16]}")

    def arm_A(mf, S, lo_x):
        """Arm A at geometry x: transport every fragment's LAS, run the impurity solves only.

        The transported active blocks are semicanonicalised at x (Fock diagonalised within the occupied-active
        and the virtual-active block, a rotation that leaves the *space* unchanged). pyscf-forge's own make_las
        does the same for fresh LNOs, and the impurity solver relies on it: its MP2 start amplitudes and its
        (T) use diagonal orbital energies. Without this step the first full run (2026-09-05 15:40, tag "")
        gave arm-A LNO-MP2 pieces thousands of µE_h off and a (T) of unknown quality.
        """
        nmo_x = mf.mo_coeff.shape[1]
        F_ao = mf.get_fock()

        def semican(C):
            if C.shape[1] == 0:
                return C
            e, U = np.linalg.eigh(C.T @ F_ao @ C)
            return C @ U
        C_core = mf.mo_coeff[:, :FROZEN_CORE]
        C_occ = mf.mo_coeff[:, FROZEN_CORE:nocc]
        C_vir = mf.mo_coeff[:, nocc:]
        frags, diag_vir_smin, diag_vir_off = [], [], []
        for s in stored:
            of = s["orbfrag"]
            occ_act0, vir_act0 = of[:, s["occ_act"]], of[:, s["vir_act"]]
            occ_act_x, sv_o, O_o = transport(occ_act0, C_occ, S)
            vir_act_x, sv_v, O_v = transport(vir_act0, C_vir, S)
            occ_act_x, vir_act_x = semican(occ_act_x), semican(vir_act_x)
            n_occ_frz_lno = s["n_occfrz"] - FROZEN_CORE
            occ_frz_x = complement_within(C_occ, occ_act_x, S, n_occ_frz_lno) if n_occ_frz_lno > 0 else np.zeros((of.shape[0], 0))
            vir_frz_x = complement_within(C_vir, vir_act_x, S, s["n_virfrz"]) if s["n_virfrz"] > 0 else np.zeros((of.shape[0], 0))
            orbfrag_x = np.hstack([C_core, occ_frz_x, occ_act_x, vir_act_x, vir_frz_x])
            assert orbfrag_x.shape[1] == nmo_x, (orbfrag_x.shape, nmo_x)
            frags.append((orbfrag_x, s["frzfrag"], s["occ_act"], s["msg"]))
            diag_vir_smin.append(float(sv_v.min())); diag_vir_off.append(offdiag_max(O_v))
        mcc = Frozen(mf, lo_x, frag_lolist, frozen=FROZEN_CORE).set_transported(frags, S)
        mcc.lno_thresh = THRESH[args.thresh]; mcc.verbose = 2
        mcc.kernel()
        return mcc, {"vir_smin_min_over_frags": min(diag_vir_smin), "vir_offdiag_max_over_frags": max(diag_vir_off)}

    # ---------------- stage 0: round trip at the reference geometry
    t0 = time.time()
    mccA0, dA0 = arm_A(mf0, S0, lo0)
    E_A0 = energies_of(mccA0, mf0, emp2_0)
    roundtrip = E_A0["e_corr_lno_ccsd_t"] - E_C0["e_corr_lno_ccsd_t"]
    if prior_ref is not None:
        d_ref = (E_A0["e_corr_lno_ccsd_t"] - prior_ref["A"]["e_corr_lno_ccsd_t"]) * 1e6
        log(f"reload test: E_A(0) from the reloaded spaces − E_A(0) of the interrupted run = {d_ref:+.4f} µE_h")
        if abs(d_ref) > 1e-2:
            raise SystemExit("--resume refused: the reloaded spaces do not reproduce E_A(0) to 0.01 µE_h.")
        resumed_note += f"; reload test {d_ref:+.4f} µE_h"
    log(f"stage 0 round trip: E_A(0) − E_C(0) = {roundtrip*1e6:.4f} µE_h (target |·| ≤ 1e-3 µE_h = 1e-9 E_h); arm A {time.time()-t0:.0f} s")

    # ---------------- displaced points
    rows, sealed = list(prior_rows), {"reference": {"C": E_C0, "A": E_A0}, "points": list(prior_points)}
    done = {(r["mode"], round(r["q"], 6)) for r in prior_rows}
    for m in modes:
        for q in qs:
            if (int(m), round(float(q), 6)) in done:
                continue
            t_pt = time.time()
            v = np.zeros(len(omega)); v[m] = q
            x = coords0 + ((L @ (v / np.sqrt(omega))) * Minv).reshape(-1, 3)
            mol = make_mol(symbols, x, args.basis)
            mf = run_scf(mol)
            S = mf.get_ovlp()
            C_occ = mf.mo_coeff[:, FROZEN_CORE:nocc]
            # transported occupied set (arms A and B) and its diagnostics
            lo_x, sv_occ, O_occ = transport(lo0, C_occ, S)
            emp2 = full_mp2(mf)
            # arm C: fresh localiser
            lo_c, pm_c = pm_localise(mol, C_occ)
            pm_t = None
            try:
                from pyscf import lo as _lo
                pm_t = float(_lo.PipekMezey(mol, lo_x).cost_function())
            except Exception:  # noqa: BLE001
                pass
            match = np.abs(lo_c.T @ S @ lo_x)      # fresh × transported
            best_match_min = float(match.max(axis=1).min())
            mccC = Recording(mf, lo_c, frag_lolist, frozen=FROZEN_CORE); mccC.lno_thresh = THRESH[args.thresh]; mccC.verbose = 2
            mccC.kernel(); E_C = energies_of(mccC, mf, emp2)
            mccB = Recording(mf, lo_x, frag_lolist, frozen=FROZEN_CORE); mccB.lno_thresh = THRESH[args.thresh]; mccB.verbose = 2
            mccB.kernel(); E_B = energies_of(mccB, mf, emp2)
            mccA, dA = arm_A(mf, S, lo_x); E_A = energies_of(mccA, mf, emp2)
            row = {"mode": int(m), "freq_cm": float(freq[m]), "family": fam[m], "q": float(q),
                   "occ_smin": float(sv_occ.min()), "occ_offdiag_max": offdiag_max(O_occ),
                   "vir_smin": dA["vir_smin_min_over_frags"], "vir_offdiag_max": dA["vir_offdiag_max_over_frags"],
                   "pm_fresh": pm_c, "pm_transported": pm_t, "fresh_vs_transported_min_best_match": best_match_min,
                   "EA_minus_EB_uEh": (E_A["e_corr_lno_ccsd_t"] - E_B["e_corr_lno_ccsd_t"]) * 1e6,
                   "EA_minus_EC_uEh": (E_A["e_corr_lno_ccsd_t"] - E_C["e_corr_lno_ccsd_t"]) * 1e6,
                   "EB_minus_EC_uEh": (E_B["e_corr_lno_ccsd_t"] - E_C["e_corr_lno_ccsd_t"]) * 1e6,
                   "EA_minus_EC_lnomp2_uEh": (E_A["e_corr_lno_mp2"] - E_C["e_corr_lno_mp2"]) * 1e6,
                   "wall_s": time.time() - t_pt, "peak_rss_gb": rss_gb()}
            rows.append(row)
            sealed["points"].append({"mode": int(m), "q": float(q), "A": E_A, "B": E_B, "C": E_C})
            log(f"mode {m} q={q:+.2f}: s_min occ {row['occ_smin']:.4f} vir {row['vir_smin']:.4f}; "
                f"pre-Löwdin off-diag occ {row['occ_offdiag_max']:.2e} vir {row['vir_offdiag_max']:.2e}; "
                f"A−B {row['EA_minus_EB_uEh']:+.2f} A−C {row['EA_minus_EC_uEh']:+.2f} µE_h (LNO-MP2 piece A−C {row['EA_minus_EC_lnomp2_uEh']:+.1f}); "
                f"PM fresh {pm_c:.4f} transported {pm_t if pm_t is None else round(pm_t,4)}; match {best_match_min:.3f}; {row['wall_s']:.0f} s")
            json.dump({"rows": rows}, open(os.path.join(out, "m1_rows.json"), "w"), indent=1)
            blob = json.dumps(sealed, sort_keys=True).encode()
            json.dump(sealed, open(os.path.join(out, "m1_sealed_energies.json"), "w"))
            open(os.path.join(out, "m1_sealed_energies.sha256"), "w").write(hashlib.sha256(blob).hexdigest())

    # ---------------- report (no verdict)
    seal_hash = open(os.path.join(out, "m1_sealed_energies.sha256")).read()
    lines = [f"# Probe M1 — frozen spaces — benzene {args.basis}, LNO thresholds {THRESH[args.thresh]}, "
             f"{datetime.now():%Y-%m-%d %H:%M}, {platform.node()} (WSL), {args.threads} threads",
             "", f"- reference: {len(stored)} fragments (one per PM LMO); frozen-space hash `{frozen_space_hash[:16]}…`; "
             f"arm C at the reference {t_ref:.0f} s",
             f"- **stage 0 round trip** E_A(0) − E_C(0) = {roundtrip*1e6:.4f} µE_h (the object reloads; target ≤ 1e-3 µE_h)",
             f"- raw energies sealed: `m1_sealed_energies.json`, sha256 `{seal_hash[:16]}…` — not printed",
             *([f"- {resumed_note}"] if resumed_note else []),
             "", "| mode | family | ω (cm⁻¹) | q | s_min occ | off-diag occ | s_min vir | off-diag vir | PM fresh | PM transported | match | A−B (µE_h) | A−C (µE_h) | B−C (µE_h) | s |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['mode']} | {r['family']} | {r['freq_cm']:.0f} | {r['q']:+.2f} | {r['occ_smin']:.4f} | {r['occ_offdiag_max']:.1e} | "
                     f"{r['vir_smin']:.4f} | {r['vir_offdiag_max']:.1e} | {r['pm_fresh']:.3f} | "
                     f"{'—' if r['pm_transported'] is None else f'{r['pm_transported']:.3f}'} | {r['fresh_vs_transported_min_best_match']:.3f} | "
                     f"{r['EA_minus_EB_uEh']:+.2f} | {r['EA_minus_EC_uEh']:+.2f} | {r['EB_minus_EC_uEh']:+.2f} | {r['wall_s']:.0f} |")
    # per-mode smoothness of A−C and A−B: residual about a degree-4 fit in q (the Q6 estimator, informational)
    lines.append("")
    for m in modes:
        rr = [r for r in rows if r["mode"] == m]
        if len(rr) >= 6:
            qq = np.array([r["q"] for r in rr])
            for key in ("EA_minus_EC_uEh", "EA_minus_EB_uEh"):
                y = np.array([r[key] for r in rr]); res = y - np.polyval(np.polyfit(qq, y, 4), qq)
                lines.append(f"- mode {m} ({rr[0]['family']}, {rr[0]['freq_cm']:.0f} cm⁻¹): {key.replace('_uEh','')} residual about a degree-4 fit "
                             f"σ = {np.sqrt(np.sum(res**2)/max(len(qq)-5,1)):.3f} µE_h (ν = {len(qq)-5}); range {y.min():+.2f} … {y.max():+.2f} µE_h")
    lines += ["", "No verdict is printed (the τ it would be judged against does not exist yet). "
              "Printed by probes/m1_frozen_spaces.py."]
    txt = "\n".join(lines)
    open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8").write(txt)
    print("\n" + txt)


if __name__ == "__main__":
    main()
