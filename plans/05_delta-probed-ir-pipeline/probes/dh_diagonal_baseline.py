"""Lead A, first test (reflection of 2026-09-13 §3 A, amended by the literature check the same day; the user adopted it on
13 September: "double-hybrid Hessians as lead A's first test, after the run") — the off-the-shelf better functional before any fit.

QUESTION. How much of the per-mode coupled-cluster correction to the B3LYP harmonic frequencies does a double-hybrid functional
already remove, at zero fitting cost? Kesharwani, Brauer & Martin (J. Phys. Chem. A 119, 1701 (2015), DOI 10.1021/jp508422u, abstract)
report harmonic RMSD 10-12 cm-1 for B2PLYP-class functionals against 5 cm-1 at the CCSD(T) basis-set limit, so a double hybrid is the
established "better functional for frequencies"; if it captures most of R0's probed correction, lead A collapses into "use a double
hybrid as the DFT half" and no range-separation parameter needs fitting.

WHAT IS COMPUTED. The diagonal of the double-hybrid Hessian in the B3LYP normal-mode basis, by central finite differences of ENERGIES
along each B3LYP mode (psi4 1.11 has B2PLYP energies only: no gradients, no Hessians), i.e. the same first-order quantity as stage A's
dfreq_first_order_cm:  delta_nu_i = (k_i[F] - k_i[B3LYP]) / (2 omega_i)  with k_i the curvature along mode i. Three functionals at the
same displaced points: B2PLYP (the test), BHHLYP (the DFT-DFT stand-in used in every desk experiment, for continuity), B3LYP (a
finite-difference check against the analytic frequencies: |nu_FD - nu_analytic| must be < FD_CHECK_CM or the run is flagged).
Five-point stencil, step chosen per mode so that the harmonic energy change at +-h is E_STEP (anharmonic contamination O(h^4);
energy noise 1e-9 E_h against 1e-4 E_h of curvature signal -> ~1e-5 relative). Every energy is checkpointed (energies.json) so the
run resumes after an interruption. Basis 6-31G* = the dry-run's basis (the comparison is per mode against the dry-run tensor).

READING (pre-registered here, before any CC number is read; thresholds proposed by the student on 13 September, to be confirmed by
the user before R0's probed diagonal is joined): with R0's per-mode correction delta_nu_i^CC available (pilot), the score is
  r = RMS_i(delta_nu_i^DH - delta_nu_i^CC) / RMS_i(delta_nu_i^CC)   over the IR-active + Raman modes of the deck;
  r <= 1/3 : the double hybrid removes >= 2/3 of the correction -> lead A becomes "double hybrid as the DFT half", no fit;
  r >= 2/3 : the double hybrid does not help -> the omega fit (lead A proper) is worth trying, with the Korzdorfer 2011 drift reported;
  between  : mode-resolved discussion, per family.
Until R0 exists the script only reports delta_nu^DH beside the stand-in delta_nu^BHHLYP per mode and family - no verdict.

INPUTS. benzene: results_dryrun/benzene/stageA_hessians.npz (H_low = B3LYP/6-31G* Cartesian Hessian, coords) + stageA.json (symbols,
freq_low_cm, families). naphthalene: plan 02's results_dft_locality/naphthalene.npz (B3LYP/6-31G* Hessian, coordinates, masses; the
same molecule as results_dryrun/naphthalene/geometry.json — sorted interatomic distances agree to 5e-4 bohr — but in a rotated frame
and another atom order, so the npz geometry is used as the reference and rotated with its Hessian into the plane frame; the 48 modes
agree with Module 03's naphthalene mode table to 0.05 cm-1, checked 13 September). Self-test 13 September: benzene modes exact
(max deviation 0.000 cm-1), one B2PLYP/6-31G* energy 35.5 s at 2 threads / 800 MB.
OUTPUTS. results_dryrun/<molecule>/dh_diagonal_baseline.{json,md}, energies.json checkpoint, a log line per mode (timestamped).
RUN. after the naphthalene timing run (one anchor job at a time; nothing above ~1 GB on the Windows side beside it):
  conda run -n qc python probes/dh_diagonal_baseline.py --molecule benzene --threads 8 --memory 8GB
  --self-test: rebuild the modes from the Hessian and compare with the dry-run's frequencies (no psi4), then ONE B2PLYP energy at the
  reference geometry with 2 threads / 800 MB to time the run (this part is allowed beside the anchor job)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
from dryrun_dft_delta_recovery import assign_families  # noqa: E402  (light import; psi4 is passed in, not imported at module level)

CONSTANTS = {
    "basis": "6-31g*", "functionals": ["b2plyp", "bhhlyp", "b3lyp"], "target": "b2plyp", "reference": "b3lyp", "stand_in": "bhhlyp",
    "E_STEP_hartree": 1e-4, "stencil": "5-point central: k = (-E(2h) + 16E(h) - 30E(0) + 16E(-h) - E(-2h)) / (12 h^2)",
    "FD_CHECK_CM": 1.0, "scf_conv": 1e-10, "d_conv": 1e-10,
    "reading_thresholds_r": {"collapse_no_fit": 1/3, "fit_worth_trying": 2/3}, "reading_status": "proposed 2026-09-13; confirm before R0's diagonal is joined",
}
AMU_TO_ME = 1822.888486209
HARTREE_TO_CM = 219474.6313632


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def load_inputs(molecule):
    out = HERE / "results_dryrun" / molecule
    if molecule == "benzene":
        z = np.load(out / "stageA_hessians.npz"); a = json.load(open(out / "stageA.json"))
        H = z["H_low"]; coords = z["coords"]; symbols = a["symbols"]; masses = np.array(a["masses_amu"]); ref_freq = np.array(a["freq_low_cm"]); ref_fam = a["families"]
    elif molecule == "naphthalene":
        # plan 02's Hessian belongs to plan 02's frame and atom order (same molecule as geometry.json: the sorted interatomic-distance
        # sets agree to 5e-4 bohr, checked 13 September, but the frame is rotated and the atoms ordered differently) -> use the npz
        # geometry itself, symbols from its masses, and rotate coordinates + Hessian into the plane frame (normal = z) that
        # assign_families assumes.
        z = np.load(REPO / "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/naphthalene.npz")
        masses = np.array(z["masses_amu"]); symbols = ["H" if m_ < 2 else "C" for m_ in masses]
        c0 = np.array(z["coords_bohr"]); A = c0 - c0.mean(0); _, _, Vt = np.linalg.svd(A); coords = A @ Vt.T
        Rbig = np.kron(np.eye(len(masses)), Vt); H = Rbig @ z["hessian_au"] @ Rbig.T; ref_freq = None; ref_fam = None
        assert np.abs(coords[:, 2]).max() < 0.05, "naphthalene not planar after rotation"
        g = json.load(open(out / "geometry.json")); dj = np.array(g["coords_bohr"])
        dist = lambda x: np.sort(np.linalg.norm(x[:, None] - x[None], axis=2).ravel())
        assert np.abs(dist(coords) - dist(dj)).max() < 1e-3, "plan 02 geometry is not the dry-run geometry"
    else:
        raise SystemExit("molecule must be benzene or naphthalene")
    return out, np.asarray(H, float), np.asarray(coords, float), list(symbols), masses, ref_freq, ref_fam


def normal_modes(H, masses_amu):
    """Mass-weighted Hessian in atomic units -> (omega_au[M], L[3N,M] mass-weighted orthonormal modes, Minv[3N]); the six
    smallest |omega| (translations, rotations) dropped after projecting them out explicitly."""
    m = np.repeat(masses_amu * AMU_TO_ME, 3); Minv = 1 / np.sqrt(m)
    Hm = H * np.outer(Minv, Minv)
    n = len(masses_amu); coords = None
    w, v = np.linalg.eigh((Hm + Hm.T) / 2)
    idx = np.argsort(np.abs(w))[6:]; idx = idx[np.argsort(w[idx])]
    omega = np.sqrt(np.abs(w[idx])) * np.sign(w[idx])
    return omega, v[:, idx], Minv


def psi4_setup(threads, memory, outfile):
    import psi4
    psi4.core.set_output_file(str(outfile), True); psi4.set_num_threads(threads); psi4.set_memory(memory)
    psi4.set_options({"basis": CONSTANTS["basis"], "scf_type": "df", "mp2_type": "df", "e_convergence": CONSTANTS["scf_conv"], "d_convergence": CONSTANTS["d_conv"], "dft_radial_points": 99, "dft_spherical_points": 590})
    return psi4


def energy(psi4, symbols, coords_bohr, functional):
    import psi4 as p4
    geom = "\n".join(f"{s} {x:.10f} {y:.10f} {z:.10f}" for s, (x, y, z) in zip(symbols, coords_bohr))
    mol = p4.geometry(f"units bohr\nsymmetry c1\nno_reorient\nno_com\n0 1\n{geom}\n")
    return float(p4.energy(f"{functional}/{CONSTANTS['basis']}", molecule=mol))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--molecule", default="benzene"); ap.add_argument("--threads", type=int, default=8); ap.add_argument("--memory", default="8GB")
    ap.add_argument("--functionals", default=",".join(CONSTANTS["functionals"])); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--modes", default="", help="comma list of mode indices (0-based) to restrict")
    args = ap.parse_args()
    out, H, coords, symbols, masses, ref_freq, ref_fam = load_inputs(args.molecule)
    omega, L, Minv = normal_modes(H, masses); freq = omega * HARTREE_TO_CM; M = len(omega)
    fams = ref_fam if ref_fam else assign_families(freq, L, symbols, Minv, coords)
    log(f"{args.molecule}: {M} modes from the B3LYP Hessian; {freq.min():.1f}..{freq.max():.1f} cm-1")
    if ref_freq is not None:
        dev = np.abs(freq - ref_freq).max(); log(f"self-test modes vs stageA freq_low_cm: max |dev| = {dev:.3f} cm-1 ({'PASS' if dev < 0.5 else 'FAIL'})")
        if dev >= 0.5: raise SystemExit("mode reconstruction does not match the dry run")
    if args.self_test:
        psi4 = psi4_setup(2, "800MB", out / "dh_selftest_psi4.out"); t = time.time(); e = energy(psi4, symbols, coords, CONSTANTS["target"]); dt = time.time() - t
        n_pts = 4 * M; log(f"one {CONSTANTS['target']}/{CONSTANTS['basis']} energy: {dt:.1f} s (2 threads, 800 MB) -> full run ~ {n_pts} points x 3 functionals; target part alone ~ {n_pts*dt/3600:.1f} h at this speed")
        json.dump({"date": f"{datetime.now():%Y-%m-%d %H:%M}", "molecule": args.molecule, "modes": M, "mode_check_max_dev_cm": float(dev) if ref_freq is not None else None, "e_target_ref": e, "t_one_energy_s": dt, "threads": 2, "memory": "800MB"}, open(out / "dh_selftest.json", "w"), indent=1)
        return
    functionals = args.functionals.split(","); modes = [int(x) for x in args.modes.split(",")] if args.modes else list(range(M))
    ck = out / "dh_energies.json"; E = json.load(open(ck)) if ck.exists() else {}
    psi4 = psi4_setup(args.threads, args.memory, out / "dh_psi4.out")
    def get(key, xyz, f):
        k = f"{f}|{key}"
        if k not in E:
            E[k] = energy(psi4, symbols, xyz, f); json.dump(E, open(ck, "w"), indent=0)
        return E[k]
    t0 = time.time(); rows = []
    for f in functionals: get("ref", coords, f)
    for i in modes:
        h = np.sqrt(2 * CONSTANTS["E_STEP_hartree"]) / abs(omega[i]); disp = (L[:, i] * Minv).reshape(-1, 3)  # Cartesian displacement per unit mass-weighted Q
        k = {}
        for f in functionals:
            e = {s: get(f"m{i}_{s:+d}", coords + s * h * disp, f) for s in (-2, -1, 1, 2)}; e0 = get("ref", coords, f)
            k[f] = (-e[2] + 16 * e[1] - 30 * e0 + 16 * e[-1] - e[-2]) / (12 * h * h)
        row = {"mode": i, "family": fams[i], "nu_b3lyp_analytic_cm": float(freq[i]), "h_massweighted_au": float(h)}
        if "b3lyp" in k:
            nu_fd = np.sqrt(abs(k["b3lyp"])) * HARTREE_TO_CM; row["nu_b3lyp_fd_cm"] = float(nu_fd); row["fd_check_pass"] = bool(abs(nu_fd - freq[i]) < CONSTANTS["FD_CHECK_CM"])
        kref = k.get("b3lyp", omega[i] ** 2)
        for f in functionals:
            if f != "b3lyp": row[f"dnu_{f}_minus_b3lyp_cm"] = float((k[f] - kref) / (2 * omega[i]) * HARTREE_TO_CM)
        rows.append(row); log(f"mode {i:2d} {fams[i]:12s} nu={freq[i]:7.1f}  " + "  ".join(f"d{f}={row.get(f'dnu_{f}_minus_b3lyp_cm', float('nan')):+7.2f}" for f in functionals if f != "b3lyp") + (f"  fd_check={row.get('nu_b3lyp_fd_cm', float('nan')):.2f}" if 'b3lyp' in k else "") + f"  elapsed {(time.time()-t0)/60:.1f} min")
    res = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "molecule": args.molecule, "constants": CONSTANTS, "functionals": functionals, "threads": args.threads, "rows": rows, "verdict": "NOT_READ (R0's probed diagonal not joined; reading thresholds proposed, not confirmed)"}
    json.dump(res, open(out / "dh_diagonal_baseline.json", "w"), indent=1)
    Lm = [f"# Double-hybrid diagonal baseline — {args.molecule} ({res['date']})", "", f"Per-mode first-order shifts against B3LYP/{CONSTANTS['basis']}, by 5-point finite differences of energies along the B3LYP modes. {res['verdict']}.", "",
          "| mode | family | ν B3LYP | FD check | δν B2PLYP−B3LYP | δν BHHLYP−B3LYP (stand-in) |", "|---|---|---|---|---|---|"]
    for r in rows:
        Lm.append(f"| {r['mode']} | {r['family']} | {r['nu_b3lyp_analytic_cm']:.1f} | {r.get('nu_b3lyp_fd_cm', float('nan')):.2f} | {r.get('dnu_b2plyp_minus_b3lyp_cm', float('nan')):+.2f} | {r.get('dnu_bhhlyp_minus_b3lyp_cm', float('nan')):+.2f} |")
    (out / "dh_diagonal_baseline.md").write_text("\n".join(Lm), encoding="utf-8"); log("written " + str(out / "dh_diagonal_baseline.md"))


if __name__ == "__main__":
    main()
