"""X6 (defined 2026-09-12; script written the same evening, NOT RUN — needs PySCF in WSL, after the anchor job) — how much of the
correlation curvature along benzene's probed modes lives in the π space alone? (direction S3: quasi-1D π systems / DMRG as an anchor route)

Design that keeps plan 05's seal: the sealed objects are the canonical and LNO CC energies of probe M1. X6 therefore compares
  E_CAS(6,6) − E_HF      (the π-valence complete active space, chosen by AVAS on the carbon 2pz functions)
against
  E_MP2 − E_HF           (the cheapest unsealed proxy for the correlation energy; MP2 is what plan 05 prints per point anyway)
along the same three modes and the same q grid as probe M1 (totally symmetric, first C–C stretch, CH-oop; q ∈ [−1, 1], 9 points;
geometry x = x0 + (L (v/√ω)) ⊙ Minv, the dry run's convention), at cc-pVDZ. Per mode an even polynomial of degree 4 is fitted in q and the
curvature coefficients a2 compared: share = a2(CAS − HF) / a2(MP2 − HF). The comparison with the sealed CC − DFT curvature is done at the
pilot note, when the seal opens, by the same script with --sealed (not implemented here on purpose).

Pre-stated losing condition (Orientation §7, 2026-09-12): a π-CAS share below ½ on the C–C stretch mode closes S3 as an anchor route.
Pre-stated reading of a win: a share above ½ says the ring-mode correction is mostly π correlation, the object DMRG solves for long acenes;
it does not say anything about the σ part or about the C–H modes, which are printed too.

Runs in WSL:  wsl ~/qc05/bin/python plans/06_equivalent-faster-mathematics/experiments/x6_pi_cas_share.py [--basis cc-pvdz] [--npts 9]
              [--threads 8] [--modes auto|i,j,k]
Windows self-test (no PySCF, numpy only):  python x6_pi_cas_share.py --geometries-only
Every number printed comes from the files or the run; constants in CONSTANTS."""
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
DRYRUN = PLAN05 / "probes/results_dryrun/benzene"
HARTREE_TO_CM = 219474.63
CONSTANTS = {"basis_default": "cc-pvdz", "npts_default": 9, "q_range": [-1.0, 1.0], "active_space": [6, 6], "avas_labels": ["C 2pz"],
             "avas_threshold": 0.2, "fit_degree": 4, "losing_condition": "pi-CAS share of the MP2 correlation curvature < 0.5 on the C-C stretch mode"}


def modes_auto(a):
    fam = a["families"]; ts = int(a["totally_symmetric_index"])
    cc_idx = [k for k, f in enumerate(fam) if f == "CC-stretch"]
    return [ts, cc_idx[0] if cc_idx else 20, 6]          # identical to m1_frozen_spaces.py's auto choice


def geometries(modes, npts):
    a = json.load(open(DRYRUN / "stageA.json")); z = np.load(DRYRUN / "stageA_hessians.npz")
    L, omega, Minv, x0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    qs = np.linspace(CONSTANTS["q_range"][0], CONSTANTS["q_range"][1], npts)
    pts = []
    for m in modes:
        for q in qs:
            v = np.zeros(len(omega)); v[m] = q
            x = x0 + ((L @ (v / np.sqrt(omega))) * Minv).reshape(-1, 3)
            pts.append((int(m), float(q), x))
    return a, np.array(a["freq_low_cm"]), pts


def even_fit(qs, e):
    """Least-squares fit e(q) ≈ a0 + a2 q² + a4 q⁴ (even part only, as M1's comparison does for the bias)."""
    A = np.vstack([np.ones_like(qs), qs ** 2, qs ** 4]).T
    coef, *_ = np.linalg.lstsq(A, e, rcond=None)
    return coef, float(np.sqrt(np.mean((A @ coef - e) ** 2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", default=CONSTANTS["basis_default"]); ap.add_argument("--npts", type=int, default=CONSTANTS["npts_default"])
    ap.add_argument("--threads", type=int, default=8); ap.add_argument("--modes", default="auto"); ap.add_argument("--geometries-only", action="store_true")
    args = ap.parse_args()
    a0 = json.load(open(DRYRUN / "stageA.json"))
    modes = modes_auto(a0) if args.modes == "auto" else [int(t) for t in args.modes.split(",")]
    a, freq, pts = geometries(modes, args.npts)
    sym = a["symbols"]; fam = a["families"]
    x0 = np.load(DRYRUN / "stageA_hessians.npz")["coords"]
    if args.geometries_only:
        for m in modes:
            disp = max(np.abs(x - x0).max() for mm, q, x in pts if mm == m)
            print(f"mode {m} ({freq[m]:.0f} cm-1, {fam[m]}): {sum(1 for mm, *_ in pts if mm == m)} points, max atomic displacement {disp:.4f} bohr")
        print("geometries OK (numpy only; PySCF not touched)")
        return
    os.environ.setdefault("OMP_NUM_THREADS", str(args.threads))
    from pyscf import gto, scf, mp, mcscf
    from pyscf.mcscf import avas
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "basis": args.basis, "modes": modes, "points": []}
    t0 = time.time()
    for m, q, x in pts:
        mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(sym, x)], unit="Bohr", basis=args.basis, verbose=0, symmetry=False)
        mf = scf.RHF(mol); mf.conv_tol = 1e-10; mf.kernel()
        if not mf.converged:
            raise RuntimeError(f"SCF not converged at mode {m} q {q}")
        emp2 = mp.MP2(mf).kernel()[0]
        ncas, nelecas, mo = avas.avas(mf, CONSTANTS["avas_labels"], threshold=CONSTANTS["avas_threshold"], canonicalize=True)
        if (ncas, nelecas) != tuple(CONSTANTS["active_space"]) and not (ncas == CONSTANTS["active_space"][1] and sum(np.atleast_1d(nelecas)) == CONSTANTS["active_space"][0]):
            print(f"warning: AVAS gave ncas {ncas}, nelecas {nelecas} at mode {m} q {q:+.3f}")
        mc = mcscf.CASCI(mf, CONSTANTS["active_space"][1], CONSTANTS["active_space"][0]); mc.verbose = 0
        ecas = mc.kernel(mo)[0]
        out["points"].append({"mode": m, "q": q, "e_hf": float(mf.e_tot), "e_corr_mp2": float(emp2), "e_corr_cas": float(ecas - mf.e_tot),
                              "avas_ncas": int(ncas), "avas_nelecas": int(sum(np.atleast_1d(nelecas)))})
        print(f"mode {m} q {q:+.3f}: HF {mf.e_tot:.8f}  MP2 corr {emp2*1e3:.3f} mEh  CAS corr {(ecas-mf.e_tot)*1e3:.3f} mEh  [{time.time()-t0:.0f} s]", flush=True)
    rows = []
    for m in modes:
        P = [p for p in out["points"] if p["mode"] == m]; qs = np.array([p["q"] for p in P])
        cm, sm = even_fit(qs, np.array([p["e_corr_mp2"] for p in P])); cc, sc = even_fit(qs, np.array([p["e_corr_cas"] for p in P]))
        rows.append({"mode": m, "family": fam[m], "omega_cm": float(freq[m]), "a2_mp2_uEh": cm[1] * 1e6, "a2_cas_uEh": cc[1] * 1e6, "share_cas_over_mp2": cc[1] / cm[1],
                     "rms_fit_mp2_uEh": sm * 1e6, "rms_fit_cas_uEh": sc * 1e6, "dw_mp2_cm": cm[1] * HARTREE_TO_CM, "dw_cas_cm": cc[1] * HARTREE_TO_CM})
    out["rows"] = rows
    json.dump(out, open(HERE / f"x6_pi_cas_share_{args.basis}.json", "w"), indent=1)
    L = [f"# X6 — π-CAS(6,6) share of the correlation curvature along the probed benzene modes ({args.basis}, {out['date']})", "",
         "Even degree-4 fits in q of E_corr(MP2) and E_corr(CAS(6,6) via AVAS on C 2pz) − both relative to the same RHF; a2 is the curvature coefficient (µE_h per q²), "
         "Δω = a2 in cm⁻¹ the frequency shift it implies (M1's convention). Share = a2(CAS)/a2(MP2).", "",
         "| mode | family | ω (cm⁻¹) | a2 MP2 (µE_h) | a2 π-CAS (µE_h) | **share** | Δω MP2 / π-CAS (cm⁻¹) | rms fit MP2 / CAS (µE_h) |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['mode']} | {r['family']} | {r['omega_cm']:.0f} | {r['a2_mp2_uEh']:.2f} | {r['a2_cas_uEh']:.2f} | **{r['share_cas_over_mp2']:.2f}** | {r['dw_mp2_cm']:.2f} / {r['dw_cas_cm']:.2f} | {r['rms_fit_mp2_uEh']:.3f} / {r['rms_fit_cas_uEh']:.3f} |")
    L += ["", f"Losing condition (pre-stated): {CONSTANTS['losing_condition']}. The sealed CC − DFT comparison waits for the pilot note.", "", "Constants: " + json.dumps(CONSTANTS)]
    (HERE / f"x6_pi_cas_share_{args.basis}.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
