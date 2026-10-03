"""Gate 1 (30 Sep 2026, after the lambda incident of 29 Sep): acceptance tests on water for the production CCSD(T) gradient of
probes/e8_cc_hessian_fd.py, run on the machine that will compute. Every earlier incident was found by a second route, never by lint or unit
tests, so each check here compares the production path with an independent counterpart:

1. energy (RHF and UHF, the paths of neutral molecules and of benzene⁺) against psi4 1.11 sealed on hel1-23 (30 Sep 2026, 06:4x;
   probes/results_m1/gate1_water_2026-09-30/psi4_water_seal.out), same bohr geometry, frozen core, conventional CC;
2. the analytic CCSD(T) gradient (explicit (T) lambda) against central finite differences of the CCSD(T) energy — the check that caught
   the lambda incident (the bare Gradients(mycc).kernel() is 1.5e-3 a.u. off; limit 1e-6);
3. geometry optimised with that gradient and its FD Hessian frequencies (the probe's own step, projector and pair check) against CCCBDB
   Release 22, CCSD(T)/cc-pVDZ frozen core: r 0.9664 Å, ∠ 101.964°, ω 1690/3820/3926 cm⁻¹ (all-electron: 1691/3824/3930; the
   CCSD-lambda Hessian was 2.5–7.7 cm⁻¹ off);
4. where the C kernels are built ((T) density; (T) lambda since 30 Sep 2026): their intermediates against pyscf's Python (≤ 1e-10) and the
   gradient through both (≤ 1e-8).

Script mode (no pytest needed on a server): `python tests/test_acceptance_water.py` runs all of them; when the RHF checks pass it writes the stamp
~/.dpir_gate1.json that e8_cc_hessian_fd.py requires (host, pyscf version and the hashes of the probe, the kernel and this file must match)
with a verdict per path; exit 0 = both paths pass, 2 = RHF only (--spin > 0 refused), 1 = no stamp.
probes/launch_detached.sh runs it before every E8 launch. 30 s on the laptop (8 threads). On a server whose probes live elsewhere, put this
file in <probes>/../tests and run it with DPIR_PROBES=<probes>."""
import json
import os
import socket
import sys
import time

import numpy as np

PLAN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DPIR_PROBES: the probe directory on a server that keeps the probes outside the repo layout (hel1-23: /root/e8, this file at /root/tests)
PROBES = os.environ.get("DPIR_PROBES", os.path.join(PLAN, "probes"))
sys.path.insert(0, PROBES)
sys.path.insert(0, os.path.join(PROBES, "t_density_kernel"))

try:
    import pytest
    pyscf = pytest.importorskip("pyscf")
    pytestmark = pytest.mark.slow
except ImportError:           # script mode on a server without pytest
    pytest = None
    import pyscf

import e8_cc_hessian_fd as E  # noqa: E402
import e8_hessian_checks as HC  # noqa: E402
import t_density_fast as F  # noqa: E402

SYMBOLS = ["O", "H", "H"]
MASSES = np.array([15.99491462, 1.00782503, 1.00782503])
# CCCBDB CCSD(T)/cc-pVDZ Cartesians (Å) divided by pyscf's BOHR 0.52917721092, rounded to 1e-6; psi4 got these numbers with `units bohr`
X_REF = np.array([[0.0, 0.0, 0.229980], [0.0, 1.418995, -0.919730], [0.0, -1.418995, -0.919730]])
FROZEN = 1
PSI4_SEALED = {(0, 0): -76.2413048758, (1, 1): -75.8024945203}   # (charge, 2S): psi4 1.11 CCSD(T) total energy, E_h
# CCCBDB Release 22, H2O CCSD(T)/cc-pVDZ (frozen core; =FULL is 0.9658 Å, 101.970°, 1691/3824/3930 cm⁻¹, all-electron), read 30 Sep 2026
CCCBDB = {"energy": -76.241305, "r_angstrom": 0.9664, "angle_deg": 101.964, "omega_cm": (1690.0, 3820.0, 3926.0)}
BOHR = 0.52917721092

ENERGY_LIMIT = 1e-7          # E_h, pyscf versus psi4 (CCSD conv_tol 1e-9 in the probe)
GRADIENT_LIMIT = 1e-6        # a.u., analytic versus FD of the energy (the CCSD-lambda error was 1.5e-3)
FD_ENERGY_STEP = 1e-3        # bohr; truncation O(h²) ≈ 1e-7, noise 1e-11 / 1e-3
FD_HESSIAN_STEP = 0.005      # bohr, the probe's --step default
CCCBDB_ENERGY_LIMIT = 1e-6   # E_h, CCCBDB prints 6 decimals (laptop 30 Sep: 1.2e-7)
GAUSSIAN_MAX_FORCE = 4.5e-4  # a.u., Gaussian's default optimisation threshold: CCCBDB's geometry is stationary only to this (ours there: 2.2e-4)
R_LIMIT = 5e-4               # Å; that residual force moves our minimum by 1.2e-4 Å and 0.05° (0.96628 Å, 101.913°, laptop 30 Sep)
ANGLE_LIMIT = 0.1            # degrees
OMEGA_LIMIT = 2.0            # cm⁻¹, CCCBDB prints integers; frozen core versus all-electron differs by 1–4
KERNEL_LIMIT = E.FAST_T_LIMIT
KERNEL_GRADIENT_LIMIT = 1e-8

_cache = {}


def _quiet(_):
    pass


DIPOLE_LIMIT = 1e-5          # a.u.; the captured relaxed CCSD(T) dipole against the finite-field derivative (laptop 3 Oct 2026: 6.1e-8)


def production_gradient(x, charge=0, spin=0, fast=None, check_fast=False):
    """The probe's own gradient() — the production path, not a re-implementation; (energy, gradient). check_dipole_capture reads the third value."""
    return E.gradient(SYMBOLS, x, "cc-pvdz", FROZEN, _quiet, charge, spin, 4000, fast, check_fast)[:2]


def check_dipole_capture():
    """3 Oct 2026 (odds lever 4): the relaxed dipole the probe captures from the gradient code's density equals −dE/dF of the CCSD(T) energy (water,
    F = 1e-4 a.u. per component; the finite-field route of probes/cc_dipole_capture.py)."""
    import cc_dipole_capture as DC
    from pyscf import gto
    _, _, mu = E.gradient(SYMBOLS, X_REF, "cc-pvdz", FROZEN, _quiet, 0, 0, 4000, None, False)
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(SYMBOLS, X_REF, strict=True)], unit="Bohr", basis="cc-pvdz", symmetry=False, verbose=0)
    mol.set_common_orig((0.0, 0.0, 0.0))
    mu_ff = DC.finite_field_dipole(mol, FROZEN, 1e-4)
    d = float(np.abs(np.asarray(mu) - mu_ff).max())
    assert d <= DIPOLE_LIMIT, f"captured dipole {mu} vs finite field {mu_ff}: {d:.1e} > {DIPOLE_LIMIT:.0e}"
    return {"dmu_finite_field": d}


def reference(charge, spin):
    if (charge, spin) not in _cache:
        _cache[(charge, spin)] = production_gradient(X_REF, charge, spin)
    return _cache[(charge, spin)]


def ccsd_t_energy(x, charge, spin):
    """Independent energy route with tighter tolerances than the probe."""
    from pyscf import cc, gto, scf
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(SYMBOLS, x, strict=True)], unit="Bohr", basis="cc-pvdz", charge=charge, spin=spin,
                symmetry=False, verbose=0)
    mf = (scf.RHF(mol) if spin == 0 else scf.UHF(mol)).run(conv_tol=1e-12)
    mycc = (cc.CCSD if spin == 0 else cc.UCCSD)(mf, frozen=FROZEN)
    mycc.conv_tol, mycc.conv_tol_normt = 1e-11, 1e-9
    mycc.kernel()
    return float(mycc.e_tot + mycc.ccsd_t())


def check_energy_vs_psi4():
    out = {}
    for (charge, spin), e_psi4 in PSI4_SEALED.items():
        e, _ = reference(charge, spin)
        out[f"dE_psi4_charge{charge}"] = d = abs(e - e_psi4)
        assert d <= ENERGY_LIMIT, f"charge {charge}: pyscf {e:.10f} vs psi4 {e_psi4:.10f} ({d:.1e} > {ENERGY_LIMIT:.0e})"
    return out


def _gradient_vs_energy_fd(charge, spin):
    out = {}
    _, g = reference(charge, spin)
    fd = np.zeros(X_REF.size)
    for k in range(X_REF.size):
        xp, xm = X_REF.copy(), X_REF.copy()
        xp.flat[k] += FD_ENERGY_STEP
        xm.flat[k] -= FD_ENERGY_STEP
        fd[k] = (ccsd_t_energy(xp, charge, spin) - ccsd_t_energy(xm, charge, spin)) / (2 * FD_ENERGY_STEP)
    out[f"dgrad_fd_charge{charge}"] = d = float(np.abs(np.asarray(g).ravel() - fd).max())
    assert d <= GRADIENT_LIMIT, f"charge {charge}: max |analytic − FD(energy)| = {d:.1e} a.u. > {GRADIENT_LIMIT:.0e}"
    return out


def check_rhf_gradient_vs_energy_fd():
    return _gradient_vs_energy_fd(0, 0)


def check_uhf_gradient_vs_energy_fd():
    """Failed on pyscf 2.14.0 as shipped (30 Sep 2026): 4.9e-3 a.u. on H2O⁺ — the missing 1/2 on dvvVV (pyscf#3305, fixed upstream after v2.14.0);
    the probe's install_uccsd_t_dvvvv_fix() brings it to 1.5e-7. The probe refuses --spin > 0 until this passes."""
    return _gradient_vs_energy_fd(1, 1)


def optimised_geometry():
    if "x_opt" not in _cache:
        from scipy.optimize import minimize
        def energy_and_gradient(v):
            e, g = production_gradient(v.reshape(3, 3))
            return e, np.ravel(g)
        res = minimize(energy_and_gradient, X_REF.ravel(), jac=True, method="BFGS", options={"gtol": 1e-6})
        _cache["x_opt"] = res.x.reshape(3, 3)
    return _cache["x_opt"]


def check_geometry_and_frequencies_vs_cccbdb():
    e_ref, g_ref = reference(0, 0)
    out = {"dE_cccbdb": abs(e_ref - CCCBDB["energy"]), "max_force_at_cccbdb_geometry": float(np.abs(g_ref).max())}
    assert out["dE_cccbdb"] <= CCCBDB_ENERGY_LIMIT, f"E {e_ref:.7f} vs CCCBDB {CCCBDB['energy']} at CCCBDB's geometry"
    assert out["max_force_at_cccbdb_geometry"] <= GAUSSIAN_MAX_FORCE, f"max |g| {out['max_force_at_cccbdb_geometry']:.1e} at CCCBDB's geometry"
    x = optimised_geometry()
    r = 0.5 * (np.linalg.norm(x[1] - x[0]) + np.linalg.norm(x[2] - x[0])) * BOHR
    u, v = x[1] - x[0], x[2] - x[0]
    angle = float(np.degrees(np.arccos(u @ v / np.linalg.norm(u) / np.linalg.norm(v))))
    out.update(r_angstrom=float(r), angle_deg=angle)
    assert abs(r - CCCBDB["r_angstrom"]) <= R_LIMIT, f"r {r:.5f} Å vs CCCBDB {CCCBDB['r_angstrom']}"
    assert abs(angle - CCCBDB["angle_deg"]) <= ANGLE_LIMIT, f"angle {angle:.3f}° vs CCCBDB {CCCBDB['angle_deg']}"
    _, g0 = production_gradient(x)
    G = np.zeros((9, 9))
    worst_pair = 0.0
    e_opt = production_gradient(x)[0]
    ediag = {}
    for k in range(9):
        gs = []
        es = []
        for s in (+1.0, -1.0):
            xd = x.copy()
            xd.flat[k] += s * FD_HESSIAN_STEP
            e_d, g_d = production_gradient(xd)
            gs.append(np.asarray(g_d))
            es.append(e_d)
        G[k] = (gs[0].ravel() - gs[1].ravel()) / (2 * FD_HESSIAN_STEP)
        ediag[k] = (es[0] + es[1] - 2 * e_opt) / FD_HESSIAN_STEP ** 2
        worst_pair = max(worst_pair, E.pair_consistency(gs[0], gs[1], g0))
    H = 0.5 * (G + G.T)
    chk = HC.classify_hessian(H, x, MASSES, float(np.abs(G - G.T).max()), ediag)
    Hp, _ = E.project_tr(H, MASSES, x)
    sm = np.sqrt(np.repeat(MASSES * E.AMU2AU, 3))
    fr = np.sort(E.frequencies(Hp / np.outer(sm, sm)))
    omega = sorted(fr[-3:].tolist())
    out.update(pair_check=worst_pair, null_space_cm=float(np.abs(fr[:6]).max()), omega_cm=omega)
    assert worst_pair <= E.FIRST_PAIR_LIMIT, f"pair check {worst_pair:.1e} > {E.FIRST_PAIR_LIMIT:.0e}"
    out.update(selfcheck=chk["status"], trans_sum_rule=chk["trans_sum_rule"], energy_route_max=chk["energy_diag_max"])
    assert chk["status"] == "VALID", f"the probe's self-check calls the water minimum {chk['status']}: {chk['reasons']}"
    assert out["null_space_cm"] <= HC.NULL_SPACE_LIMIT_CM, f"null space {out['null_space_cm']:.1f} cm⁻¹"
    for w, ref in zip(omega, sorted(CCCBDB["omega_cm"]), strict=True):
        assert abs(w - ref) <= OMEGA_LIMIT, f"ω {w:.1f} vs CCCBDB {ref:.0f} cm⁻¹ (limit {OMEGA_LIMIT}); got {np.round(omega, 1).tolist()}"
    return out


def check_fast_kernel():
    """Both C kernels ((T) density, (T) lambda since 30 Sep 2026) through the production gradient with its two-route checks. Skipped (recorded
    as not built) where the library is absent; the probe then refuses --fast-t-density / --fast-t-lambda anyway."""
    if not F.available():
        return {"fast_kernel": False, "fast_lambda": False}
    _, g_plain = reference(0, 0)
    F.install()
    F.install_lambda()
    try:
        _, g_fast = production_gradient(X_REF, fast=F, check_fast=True)   # raises SystemExit above FAST_T_LIMIT
    finally:
        F.uninstall()
        F.uninstall_lambda()
    d = float(np.abs(np.asarray(g_fast) - np.asarray(g_plain)).max())
    assert d <= KERNEL_GRADIENT_LIMIT, f"gradient through the C kernel differs by {d:.1e} a.u."
    return {"fast_kernel": True, "fast_lambda": True, "dgrad_fast_kernel": d}


# (check, path): 'rhf' checks gate every E8 run, 'uhf' checks gate --spin > 0 runs only
CHECKS = [(check_energy_vs_psi4, "rhf"), (check_rhf_gradient_vs_energy_fd, "rhf"), (check_geometry_and_frequencies_vs_cccbdb, "rhf"),
          (check_fast_kernel, "rhf"), (check_dipole_capture, "rhf"), (check_uhf_gradient_vs_energy_fd, "uhf")]


def test_energy_vs_psi4():
    check_energy_vs_psi4()


def test_rhf_gradient_vs_energy_fd():
    check_rhf_gradient_vs_energy_fd()


def test_uhf_gradient_vs_energy_fd():
    check_uhf_gradient_vs_energy_fd()


def test_geometry_and_frequencies_vs_cccbdb():
    check_geometry_and_frequencies_vs_cccbdb()


def test_fast_kernel():
    check_fast_kernel()


def test_dipole_capture():
    check_dipole_capture()


def main():
    from pyscf import lib
    lib.num_threads(min(8, os.cpu_count() or 1))
    t0 = time.time()
    results, paths = {}, {"rhf": True, "uhf": True}
    for check, path in CHECKS:
        t1 = time.time()
        try:
            r = check()
        except (AssertionError, SystemExit) as exc:
            print(f"GATE 1 FAIL ({path} path) {check.__name__}: {exc}", flush=True)
            paths[path] = False
            continue
        results.update(r)
        print(f"gate 1 pass {check.__name__} ({time.time() - t1:.0f} s): {r}", flush=True)
    paths["uhf"] = paths["uhf"] and paths["rhf"]
    if not paths["rhf"]:
        print("GATE 1 FAIL — no stamp written", flush=True)
        return 1
    stamp = {"paths": paths, "host": socket.gethostname(), "pyscf": pyscf.__version__, "fingerprint": E.gate1_fingerprint(), "time": time.strftime("%F %T"),
             "seconds": round(time.time() - t0), "results": results}
    with open(E.GATE1_STAMP + ".tmp", "w") as f:
        json.dump(stamp, f, indent=1)
    os.replace(E.GATE1_STAMP + ".tmp", E.GATE1_STAMP)
    print(f"GATE 1 PASS ({stamp['seconds']} s) — paths {paths} — stamp {E.GATE1_STAMP}", flush=True)
    return 0 if paths["uhf"] else 2


if __name__ == "__main__":
    sys.exit(main())
