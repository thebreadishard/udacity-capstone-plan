"""E8 — CCSD(T)/cc-pVDZ Hessian of a molecule by central finite differences of analytic gradients, checkpointed (pre-registration
PreRegistration_2026-09-23_E8_CC_Correction_Locality.md, 23 September 2026).

Reference + 2 × 3N displaced geometries (step 0.005 bohr along every Cartesian coordinate); each CCSD(T) gradient is written to
<out>/grad_<k>_<sign>.npy as soon as it exists, so the run resumes after any interruption. The Hessian H_ij = (g_i(+j) − g_i(−j)) / (2δ), symmetrised,
is written to <out>/hessian_ccsd_t.npz with H_raw, H_projected (translations/rotations projected out, mass-weighted projector), freq_cm, the
reference energy and gradient. The two-route checks of the pre-registration (degenerate-pair splits, translational null space) are printed.

Usage: python e8_cc_hessian_fd.py <geometry.json> <out dir> [--threads 16] [--basis cc-pvdz] [--step 0.005] [--frozen N] [--only-reference]
           [--symmetry] [--ks a:b] [--two-route-check inline|separate|only|energy] [--charge 0 --spin 0] [--fast-t-density] [--fast-t-lambda]
"""
import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import e8_hessian_checks as HC
import e8_symmetry as SYM
import numpy as np
from pyscf import cc, gto, lib, scf
from pyscf.grad import ccsd_t as ccsd_t_grad
from qc_common import CORE_ORBITALS, HARTREE2CM
from qc_common import project_tr as project_tr  # re-exported: the gate-1 test reads frequencies through it

LAMBDA_TOL = 1e-8            # ccsd_t_lambda / uccsd_t_lambda convergence (pyscf's default), solved explicitly since the 29 Sep 2026 incident
FAST_T_LIMIT = 1e-10         # largest |kernel − pyscf| over the (T) density intermediates on the reference gradient (water: 4e-18, 29 Sep 2026)
FIRST_PAIR_LIMIT = 1e-4      # a.u.; |mean(g+, g−) − g0| is O(h²) ≈ 1e-5 for h = 0.005 bohr; the frozen-6-of-10 run gave 2–9e-4 in plane
TWO_ROUTE_GRAD_LIMIT = 1e-8  # a.u.; the checked reference gradient must equal the stored one (same code, same machine: 1e-10 observed on water)
TWO_ROUTE_ENERGY_LIMIT = 1e-9  # E_h; idem for the reference energy
ENERGY_GRAD_LIMIT = 2e-5  # a.u.; |g0_k − (E(+h) − E(−h)) / 2h| over the displaced coordinates (6 Oct 2026; the central difference at h = 0.005 bohr with
#                           energies converged to 1e-9 is good to ~1e-6; the 29 Sep incident's CCSD-lambda gradient was wrong by ~1e-3)
SCF_TOL = 1e-11
CC_TOL = 1e-9
CC_TOL_NORMT = 1e-7
UHF_STABILITY_ROUNDS = 3
S2_TOLERANCE = 0.05


# ---- files

def save_atomic(path: str, save) -> None:
    """`save(file handle)` into a temporary file moved over `path`: a run stopped mid-write leaves no half file for the resume to load."""
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        save(fh)
    os.replace(tmp, path)


def write_json(path: str, record: dict) -> None:
    save_atomic(path, lambda fh: fh.write(json.dumps(record, indent=1).encode("utf-8")))


class RunLog:
    """The run's log: every line to stdout and to <out>/e8_fd.log, flushed, the file closed however the run ends."""

    def __init__(self, out_dir: str):
        self.path = os.path.join(out_dir, "e8_fd.log")

    def __enter__(self):
        self.fh = open(self.path, "a")          # closed by __exit__
        return self

    def __exit__(self, *exc):
        self.fh.close()

    def __call__(self, s: str) -> None:
        line = f"[{time.strftime('%F %T')}] {s}"
        print(line, flush=True)
        self.fh.write(line + "\n")
        self.fh.flush()


# ---- checks

def energy_route_gradient_check(out_dir, g0, step):
    """6 Oct 2026: the reference gradient against central differences of the stored displaced energies (ener_kk_p/m.npy), coordinate by coordinate —
    a second route to the gradient itself (lambda, density and contraction together) that needs no slow pyscf route. Used where pyscf's (T) density
    route does not fit (benzene/cc-pVTZ: OOM at 20 GB) or does not end (anthracene/cc-pVDZ: > 28 h). The displaced gradients are covered by the
    assembly's H_kk energy route (e8_hessian_checks, negative control on water, 30 Sep 2026)."""
    g0 = np.asarray(g0, float).ravel()
    rows = {}
    for f in sorted(os.listdir(out_dir)):
        if f.startswith("ener_") and f.endswith("_p.npy"):
            k = int(f[5:7])
            fm = os.path.join(out_dir, f"ener_{k:02d}_m.npy")
            if os.path.exists(fm):
                fd = (float(np.load(os.path.join(out_dir, f))) - float(np.load(fm))) / (2 * step)
                rows[k] = dict(fd=fd, g0=float(g0[k]), diff=abs(fd - float(g0[k])))
    if not rows:
        raise SystemExit("--two-route-check energy: no displaced energy pairs (ener_kk_p/m.npy) in the run directory")
    worst = max(rows, key=lambda k: rows[k]["diff"])
    return dict(passed=bool(rows[worst]["diff"] <= ENERGY_GRAD_LIMIT), max_grad_diff=rows[worst]["diff"], worst_coordinate=worst, n_coordinates=len(rows),
                max_abs_g0=float(np.abs(g0).max()), per_coordinate={str(k): v for k, v in rows.items()})


# the Hessian self-check and its limits live in e8_hessian_checks.py (split into INVALID / IMAGINARY / VALID on 30 Sep 2026)
def pair_consistency(gp, gm, g0) -> float:
    """max |mean(g(+k), g(−k)) − g0|: zero to O(h²) when both displaced calculations sit on the same surface as the reference."""
    return float(np.abs(0.5 * (np.asarray(gp).ravel() + np.asarray(gm).ravel()) - np.asarray(g0).ravel()).max())


def core_orbital_count(symbols) -> int:
    """Number of core orbitals to freeze for a frozen-core CCSD(T): one 1s per first-row atom, five per second-row atom (incident of 27 Sep 2026:
    naphthalene ran with benzene's 6 instead of its 10; six of ten quasi-degenerate carbon 1s orbitals gave inconsistent in-plane gradients)."""
    return sum(CORE_ORBITALS[s.capitalize()] for s in symbols)


def select_displacements(ks, spec):
    """The subset of the displacement list `ks` named by --ks: 'a:b' slices it, 'i,j,k' picks positions in it (both index the displacement list; before
    28 Sep 2026 the comma form was read as raw coordinate indices — the E8 incident's two 'extra' runs)."""
    if not spec:
        return list(ks)
    if ":" in spec:
        lo, hi = (int(v) if v else None for v in spec.split(":"))
        return list(ks[lo:hi])
    return [ks[int(v)] for v in spec.split(",")]


# ---- the CCSD(T) gradient

@dataclass(frozen=True)
class CCSettings:
    """How every CCSD(T) gradient of a run is computed: basis, frozen core, charge and 2S, pyscf's memory per process, and the (T) C kernels
    (`t_density_fast`, or None for pyscf's routes)."""
    basis: str
    frozen: int
    charge: int = 0
    spin: int = 0
    max_memory: int = 26000
    fast: Any = None


def _kernel_check(label: str, run, refusal: str, log) -> None:
    """A C kernel against pyscf's Python route on this run's reference gradient; the run stops if they differ."""
    t1 = time.time()
    diffs = run()
    worst = max(diffs, key=diffs.get)
    log(f"{label} two-route check: max |kernel − pyscf| = {diffs[worst]:.1e} ({worst}; limit {FAST_T_LIMIT:.0e}; {time.time() - t1:.0f} s)")
    if diffs[worst] > FAST_T_LIMIT:
        raise SystemExit(refusal)


def _rhf_gradient(mol, s: CCSettings, log, check_fast: bool):
    """RHF-CCSD(T), the path validated on benzene (24 Sep 2026)."""
    mf = scf.RHF(mol)
    mf.conv_tol = SCF_TOL
    e_hf = mf.kernel()
    mycc = cc.CCSD(mf, frozen=s.frozen)
    mycc.conv_tol = CC_TOL
    mycc.conv_tol_normt = CC_TOL_NORMT
    e_corr = mycc.kernel()[0]
    if not mycc.converged:
        log("WARNING: CCSD not converged")
    et = mycc.ccsd_t()
    # The (T) lambda is solved explicitly (29 Sep 2026 incident): Gradients(mycc).kernel() without l1, l2 falls back to mycc.solve_lambda, the
    # CCSD lambda, and the result is not dE/dx of the CCSD(T) energy (water: 1.5e-3 a.u.; pyscf's own test passes ccsd_t_lambda's l1, l2).
    from pyscf.cc import ccsd_t_lambda
    eris = mycc.ao2mo()
    fast = s.fast if check_fast else None
    if fast is not None and fast.lambda_installed():
        # two-route check of the (T)-lambda C kernel (30 Sep 2026): pyscf's Python make_intermediates versus ours on the reference gradient
        _kernel_check("fast (T) lambda", lambda: fast.check_lambda_against_pyscf(mycc, mycc.t1, mycc.t2, eris),
                      "the fast (T) lambda kernel disagrees with pyscf on the reference gradient — refusing to continue", log)
    t0 = time.time()
    conv, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=LAMBDA_TOL)
    if not conv:
        log("WARNING: CCSD(T) lambda not converged")
    if fast is not None and fast.density_installed():
        # two-route check of the C kernel (29 Sep 2026): pyscf's Python (T) densities versus ours on this run's reference gradient
        _kernel_check("fast (T) density", lambda: fast.check_against_pyscf(mycc, mycc.t1, mycc.t2, l1, l2, eris),
                      "the fast (T) density kernel disagrees with pyscf on the reference gradient — refusing to continue", log)
    t1 = time.time()
    g, mu = gradient_with_dipole(mol, mf, mycc, l1, l2, eris)
    log(f"(T) lambda {t1 - t0:.0f} s, gradient {time.time() - t1:.0f} s")
    return float(e_hf + e_corr + et), np.asarray(g), mu


def _uhf_gradient(mol, s: CCSettings, log):
    """UHF with up to three internal-stability rounds (a cation at a near-degenerate geometry may first land on a saddle, as the cation price probe
    found), <S²> logged, UCCSD(T) and its analytic gradient (pyscf 2.14); the anchor set of 29 Sep 2026: benzene cation."""
    from pyscf.cc import uccsd_t_lambda
    from pyscf.grad import uccsd_t as uccsd_t_grad
    install_uccsd_t_dvvvv_fix()   # pyscf#3305 / #3387, not in v2.14.0 (gate 1, 30 Sep 2026)
    mf = scf.UHF(mol)
    mf.conv_tol = SCF_TOL
    e_hf = mf.kernel()
    for _ in range(UHF_STABILITY_ROUNDS):
        mo_i, _, stable_i, _ = mf.stability(return_status=True)
        if stable_i:
            break
        e_hf = mf.kernel(dm0=mf.make_rdm1(mo_i, mf.mo_occ))
    else:
        log("WARNING: UHF still internally unstable after three rounds")
    s2 = float(mf.spin_square()[0])
    if abs(s2 - s.spin / 2 * (s.spin / 2 + 1)) > S2_TOLERANCE:
        log(f"WARNING: UHF <S²> = {s2:.4f} (expected {s.spin / 2 * (s.spin / 2 + 1):.2f})")
    mycc = cc.UCCSD(mf, frozen=s.frozen)
    mycc.conv_tol = CC_TOL
    mycc.conv_tol_normt = CC_TOL_NORMT
    e_corr = mycc.kernel()[0]
    if not mycc.converged:
        log("WARNING: UCCSD not converged")
    et = mycc.ccsd_t()
    eris = mycc.ao2mo()
    t0 = time.time()
    conv, l1, l2 = uccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=LAMBDA_TOL)   # explicit (T) lambda, as on the RHF path
    if not conv:
        log("WARNING: UCCSD(T) lambda not converged")
    t1 = time.time()
    g = uccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris)
    log(f"(T) lambda {t1 - t0:.0f} s, gradient {time.time() - t1:.0f} s (no dipole on the UHF path)")
    return float(e_hf + e_corr + et), np.asarray(g), None


def gradient(symbols, coords_bohr, s: CCSettings, log, check_fast: bool = False):
    """CCSD(T) energy, gradient and (closed shell) relaxed dipole at one geometry: RHF-CCSD(T) for spin 0, UHF-UCCSD(T) otherwise. `check_fast`
    runs the C kernels' two-route checks (the reference gradient)."""
    mol = gto.M(atom=[(sym.capitalize(), tuple(c)) for sym, c in zip(symbols, coords_bohr, strict=True)], unit="Bohr", basis=s.basis, symmetry=False,
                verbose=0, max_memory=s.max_memory, charge=s.charge, spin=s.spin)
    if s.spin == 0:
        return _rhf_gradient(mol, s, log, check_fast)
    return _uhf_gradient(mol, s, log)


def gradient_with_dipole(mol, mf, mycc, l1, l2, eris):
    """The CCSD(T) gradient and the relaxed dipole from one gradient evaluation (odds lever 4, 3 Oct 2026). pyscf's grad_elec builds the fully relaxed
    one-particle density and calls `mf.get_veff(mol, dm1 + dm1.T)` with its correlation part once, last among the get_veff calls of the gradient (the
    Z-vector solve calls it first; pyscf 2.14.0 grad/ccsd.py lines 148 and 169); a wrapper records that argument. μ = Σ Z_A R_A − Tr[(D_corr + D_HF) r].
    Validated on water against the finite-field derivative: 6.1e-8 a.u. (probes/cc_dipole_capture.py)."""
    captured = []
    orig = mf.get_veff

    def get_veff_recording(mol_, dm=None, *args, **kwargs):
        if dm is not None and np.ndim(dm) == 2 and dm.shape == (mol.nao, mol.nao):
            captured.append(np.array(dm))
        return orig(mol_, dm, *args, **kwargs)

    mf.get_veff = get_veff_recording
    try:
        g = ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris)
    finally:
        mf.get_veff = orig
    if not captured:
        raise RuntimeError("no get_veff call with an AO density during the gradient — pyscf's grad_elec changed; the dipole capture needs re-validation")
    d_total = 0.5 * captured[-1] + mf.make_rdm1()
    r = mol.intor("int1e_r", comp=3)
    mu = -np.einsum("xij,ji->x", r, d_total) + np.einsum("a,ax->x", mol.atom_charges(), mol.atom_coords())
    return g, mu


def install_uccsd_t_dvvvv_fix():
    """pyscf <= 2.14.0: uccsd_t_rdm._gamma2_intermediates(compress_vvvv=True), the gradient's call, omits the 1/2 on the mixed-spin dvvVV block, so
    the UCCSD(T) gradient is 4.9e-3 a.u. off dE/dx on H2O+ (gate 1, 30 Sep 2026). Upstream: issue pyscf#3305, fixed by PR #3387 (commit aa2ad208,
    9 Aug 2026, after v2.14.0), test pyscf/grad/test/test_uccsd_t.py. The wrapper takes the uncompressed blocks and compresses them itself with the
    1/2, so it is right on fixed and unfixed pyscf alike; idempotent."""
    from pyscf.cc import uccsd_t_rdm
    if getattr(uccsd_t_rdm._gamma2_intermediates, "_dpir_fixed", False):
        return
    orig = uccsd_t_rdm._gamma2_intermediates

    def fixed(mycc, t1, t2, l1, l2, eris=None, compress_vvvv=False):  # noqa: PLR0913  (pyscf's signature, which it replaces)
        d2 = orig(mycc, t1, t2, l1, l2, eris, False)
        if not compress_vvvv:
            return d2
        nvira, nvirb = t2[1].shape[2:]
        ia = np.tril_indices(nvira)
        ia = ia[0] * nvira + ia[1]
        ib = np.tril_indices(nvirb)
        ib = ib[0] * nvirb + ib[1]

        def compress(x, na, nb, i1, i2):
            x = x + x.transpose(1, 0, 2, 3)
            return lib.take_2d(x.reshape(na**2, nb**2), i1, i2) * .5
        dvvvv, dvvVV, dVVvv, dVVVV = d2[1]
        vv = (compress(dvvvv, nvira, nvira, ia, ia), compress(dvvVV, nvira, nvirb, ia, ib), dVVvv, compress(dVVVV, nvirb, nvirb, ib, ib))
        return (d2[0], vv, *d2[2:])
    fixed._dpir_fixed = True
    uccsd_t_rdm._gamma2_intermediates = fixed


def frequencies(Hmw_projected):
    w = np.linalg.eigvalsh(Hmw_projected)
    return np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM


# ---- gate 1

GATE1_STAMP = os.path.expanduser("~/.dpir_gate1.json")   # written by tests/test_acceptance_water.py when gate 1 passes (30 Sep 2026)
_HERE = os.path.dirname(os.path.abspath(__file__))
GATE1_FILES = (os.path.join(_HERE, "e8_cc_hessian_fd.py"), os.path.join(_HERE, "e8_hessian_checks.py"),
               os.path.join(_HERE, "t_density_kernel", "t_density_fast.py"), os.path.join(_HERE, "t_density_kernel", "ccsd_t_rdm_kernel.so"),
               os.path.join(_HERE, "..", "tests", "test_acceptance_water.py"))


def gate1_fingerprint() -> dict:
    """sha256 of the files gate 1 vouches for (a file absent on this machine hashes as 'absent'); any edit invalidates the stamp."""
    return {os.path.basename(p): (hashlib.sha256(Path(p).read_bytes()).hexdigest() if os.path.exists(p) else "absent") for p in GATE1_FILES}


def gate1_problem(fast_used: bool, open_shell: bool = False, fast_lambda_used: bool = False):  # noqa: PLR0911  (one answer per gate condition)
    """None when a gate-1 stamp from this host, this pyscf and these exact files exists (and covers the C kernel if it is used), else why not.
    Lambda incident of 29 Sep 2026: six days of CCSD-lambda Hessians passed every pair check; only a second route saw it."""
    import socket

    import pyscf
    if not os.path.exists(GATE1_STAMP):
        return f"no gate-1 stamp ({GATE1_STAMP})"
    s = json.loads(Path(GATE1_STAMP).read_text())
    if s.get("host") != socket.gethostname() or s.get("pyscf") != pyscf.__version__:
        return f"stamp is from {s.get('host')} / pyscf {s.get('pyscf')}, this is {socket.gethostname()} / pyscf {pyscf.__version__}"
    changed = sorted(k for k, v in gate1_fingerprint().items() if s.get("fingerprint", {}).get(k) != v)
    if changed:
        return f"changed since the stamp of {s.get('time')}: {', '.join(changed)}"
    if fast_used and not s.get("results", {}).get("fast_kernel"):
        return "the stamp does not cover the (T) density C kernel"
    if fast_lambda_used and not s.get("results", {}).get("fast_lambda"):
        return "the stamp does not cover the (T) lambda C kernel"
    if open_shell and not s.get("paths", {}).get("uhf"):
        return "the UHF-CCSD(T) gradient failed gate 1 on this machine (before the dvvVV fix of 30 Sep 2026 it was 4.9e-3 a.u. off on H2O⁺)"
    return None


# ---- the run

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("geometry")
    ap.add_argument("out")
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--step", type=float, default=0.005)
    ap.add_argument("--frozen", type=int, default=None, help="core orbitals to freeze; default: derived from the elements (all 1s of first-row atoms); "
                    "a stated value that differs from the derived one refuses to start unless --allow-frozen-mismatch")
    ap.add_argument("--allow-frozen-mismatch", action="store_true")
    ap.add_argument("--only-reference", action="store_true")
    ap.add_argument("--two-route-check", default="inline", choices=["inline", "separate", "only", "energy"],
                    help="2 Oct 2026: where the (T)-kernel two-route checks against pyscf's slow route run — 'inline' with the reference gradient "
                         "(registered); 'separate' = the reference skips them and is marked unchecked; 'only' = recompute the reference with the checks, "
                         "compare with reference.npz and write two_route_check.json (the assembly refuses an unchecked reference without a passing file); "
                         "'energy' (6 Oct 2026) = the stored reference gradient against central differences of the stored displaced energies, no quantum "
                         "chemistry — the second route where pyscf's slow (T) route does not fit in memory")
    ap.add_argument("--charge", type=int, default=0)
    ap.add_argument("--spin", type=int, default=0, help="2S (1 = doublet); > 0 selects UHF-UCCSD(T), 29 Sep 2026")
    ap.add_argument("--max-memory", type=int, default=26000, help="pyscf max_memory in MB per process (default the former hard-coded 26000); "
                    "partial runs sharing one box take less (29 Sep 2026: 3 x 8000 on a 31 GB CPX62)")
    ap.add_argument("--fast-t-density", action="store_true", help="use the C kernel for the (T) density intermediates (probes/t_density_kernel, 29 Sep "
                    "2026); the reference gradient is also computed through pyscf's Python route and the run refuses to continue if they differ; RHF only")
    ap.add_argument("--fast-t-lambda", action="store_true", help="use the C kernel for the (T) part of the CCSD(T) lambda intermediates (same "
                    "library, 30 Sep 2026); two-route check against pyscf's make_intermediates on the reference gradient; RHF only")
    ap.add_argument("--symmetry", action="store_true", help="displace only one atom per symmetry orbit and reconstruct the Hessian with e8_symmetry "
                    "(validated 24 Sep 2026)")
    ap.add_argument("--ks", default="", help="compute only these displacement indices (comma list or a:b slice of the displacement list, e.g. 0:15) and "
                    "stop before the Hessian — for splitting a run over machines; merge the grad_*.npy files and rerun without --ks to assemble")
    return ap


def load_fast(a):
    """The (T) C kernels when asked for (RHF only), installed; None otherwise."""
    if not (a.fast_t_density or a.fast_t_lambda):
        return None
    if a.spin:
        raise SystemExit("--fast-t-density and --fast-t-lambda are RHF only (the UHF gradient has its own (T) code)")
    sys.path.insert(0, os.path.join(_HERE, "t_density_kernel"))
    import t_density_fast as fast
    if not fast.available():
        raise SystemExit("ccsd_t_rdm_kernel.so is not built on this machine: bash probes/t_density_kernel/build.sh <python>")
    if a.fast_t_density:
        fast.install()
    if a.fast_t_lambda:
        fast.install_lambda()
    return fast


def resolve_frozen(a, symbols) -> tuple[int, int]:
    """(the frozen core the run uses, the one the elements give); a stated value that differs is refused unless allowed on purpose."""
    derived = core_orbital_count(symbols)
    if a.frozen is None:
        return derived, derived
    if a.frozen != derived and not a.allow_frozen_mismatch:
        raise SystemExit(f"--frozen {a.frozen} but the elements give {derived} core orbitals — refusing (guard of 27 Sep 2026: naphthalene ran with "
                         "benzene's 6 of its 10 carbon cores and produced an invalid Hessian); pass --allow-frozen-mismatch to override on purpose")
    return a.frozen, derived


@dataclass
class Job:
    """One run: its options, the molecule, the gradient settings, the log and the run folder's two record paths."""
    a: argparse.Namespace
    symbols: list
    x0: np.ndarray
    masses: np.ndarray
    s: CCSettings
    log: RunLog

    @property
    def n(self) -> int:
        return len(self.symbols)

    @property
    def ref_path(self) -> str:
        return os.path.join(self.a.out, "reference.npz")

    @property
    def check_path(self) -> str:
        return os.path.join(self.a.out, "two_route_check.json")


def energy_check(job: Job) -> None:
    """--two-route-check energy: the stored reference gradient against the stored displaced energies; no quantum chemistry."""
    a = job.a
    if not os.path.exists(job.ref_path):
        raise SystemExit("--two-route-check energy needs an existing reference.npz and the displaced energies (ener_kk_p/m.npy)")
    with np.load(job.ref_path) as ref:
        g0 = ref["gradient"]
    res = energy_route_gradient_check(a.out, g0, a.step)
    write_json(job.check_path, dict(route="energy_fd", grad_limit=ENERGY_GRAD_LIMIT, step=a.step, date=time.strftime("%F %T"), **res))
    job.log(f"two-route check (energy route) {'PASSED' if res['passed'] else 'FAILED'}: reference gradient vs (E(+h) − E(−h)) / 2h over "
            f"{res['n_coordinates']} coordinates, max |Δ| {res['max_grad_diff']:.1e} a.u. at coordinate {res['worst_coordinate']} "
            f"(limit {ENERGY_GRAD_LIMIT:.0e}); max |g0| {res['max_abs_g0']:.1e}")
    if not res["passed"]:
        raise SystemExit(5)


def only_check(job: Job) -> None:
    """--two-route-check only: the reference recomputed with the kernel checks and compared with the stored one."""
    if not os.path.exists(job.ref_path):
        raise SystemExit("--two-route-check only needs an existing reference.npz (run the reference first)")
    with np.load(job.ref_path) as ref:
        e0, g0 = float(ref["energy"]), ref["gradient"]
    t0 = time.time()
    e1, g1, _ = gradient(job.symbols, job.x0, job.s, job.log, check_fast=True)
    dgrad = float(np.abs(np.asarray(g1) - np.asarray(g0)).max())
    de = abs(e1 - e0)
    passed = bool(dgrad <= TWO_ROUTE_GRAD_LIMIT and de <= TWO_ROUTE_ENERGY_LIMIT)   # the kernel checks inside gradient() raise on failure
    write_json(job.check_path, dict(passed=passed, max_grad_diff=dgrad, energy_diff=de, grad_limit=TWO_ROUTE_GRAD_LIMIT,
                                    energy_limit=TWO_ROUTE_ENERGY_LIMIT, seconds=round(time.time() - t0), date=time.strftime("%F %T")))
    job.log(f"two-route check {'PASSED' if passed else 'FAILED'}: checked reference vs stored reference max |Δgrad| {dgrad:.1e} "
            f"(limit {TWO_ROUTE_GRAD_LIMIT:.0e}), |ΔE| {de:.1e}; {time.time() - t0:.0f} s")
    if not passed:
        raise SystemExit(5)


@dataclass(frozen=True)
class Reference:
    """The reference geometry's energy and gradient, and whether they passed the kernel checks."""
    energy: float
    gradient: np.ndarray
    checked: bool


@dataclass(frozen=True)
class Assembly:
    """The symmetrised Hessian, the symmetry spread (None without --symmetry) and the consistency measure the checks read."""
    H: np.ndarray
    spread: float | None
    asym: float


def reference(job: Job) -> Reference:
    """Read when the run folder has it, else computed and stored."""
    if os.path.exists(job.ref_path):
        with np.load(job.ref_path) as ref:
            checked = bool(ref["two_route_checked"]) if "two_route_checked" in ref.files else True
            return Reference(float(ref["energy"]), ref["gradient"], checked)
    a = job.a
    inline = a.two_route_check == "inline"
    t0 = time.time()
    e0, g0, mu0 = gradient(job.symbols, job.x0, job.s, job.log, check_fast=inline)
    save_atomic(job.ref_path, lambda fh: np.savez(fh, energy=e0, gradient=g0, coords_bohr=job.x0, charge=a.charge, spin=a.spin, two_route_checked=inline,
                                                  **({"dipole": mu0} if mu0 is not None else {})))
    job.log(f"reference: E = {e0:.9f}, max|grad| {np.abs(g0).max():.2e}, {time.time() - t0:.0f} s"
            + ("" if inline else "; two-route checks deferred to a separate run (--two-route-check only)"))
    return Reference(e0, g0, inline)


def require_passed_check(job: Job) -> None:
    ok = os.path.exists(job.check_path) and bool(json.loads(Path(job.check_path).read_text()).get("passed"))
    if not ok:
        raise SystemExit("the reference gradient is unchecked and no passing two_route_check.json exists — run `--two-route-check only` "
                         "before assembling the Hessian (rule: every derived quantity has a second route)")
    job.log("two-route check on file: passed — assembling")


def displacements(job: Job) -> tuple[list[int], list | None, list | None]:
    """(coordinates to displace, symmetry operations, orbit representatives); every coordinate without --symmetry."""
    if not job.a.symmetry:
        return list(range(3 * job.n)), None, None
    ops = SYM.point_group_ops(job.symbols, job.x0)
    ks, reps = SYM.unique_displacements(ops, job.n)
    job.log(f"symmetry: {len(ops)} operations, orbits {SYM.orbits(ops, job.n)}, {len(ks)} displacements ({2 * len(ks)} gradients) instead of {6 * job.n}")
    return ks, ops, reps


def displaced_pair(job: Job, k: int, e0: float) -> dict[str, np.ndarray]:
    """The gradients at ±step along coordinate k, read when stored, else computed and stored with their energy and dipole."""
    a = job.a
    gs = {}
    for sign, s in (("p", +1.0), ("m", -1.0)):
        p = os.path.join(a.out, f"grad_{k:02d}_{sign}.npy")
        if os.path.exists(p):
            gs[sign] = np.load(p)
            continue
        x = job.x0.copy()
        x.flat[k] += s * a.step
        t0 = time.time()
        e, gr, mu = gradient(job.symbols, x, job.s, job.log)
        save_atomic(p, lambda fh, gr=gr: np.save(fh, gr))
        gs[sign] = gr
        save_atomic(os.path.join(a.out, f"ener_{k:02d}_{sign}.npy"), lambda fh, e=e: np.save(fh, np.array(e)))
        if mu is not None:   # 3 Oct 2026: the CC APT by FD over the same displacements
            save_atomic(os.path.join(a.out, f"dip_{k:02d}_{sign}.npy"), lambda fh, mu=mu: np.save(fh, np.asarray(mu)))
        done = len([f for f in os.listdir(a.out) if f.startswith("grad_")])
        job.log(f"coordinate {k:2d} {sign}: E − E0 = {(e - e0) * 1e6:+9.2f} µE_h, {time.time() - t0:.0f} s  ({done}/{6 * job.n} gradients)")
    return gs


def displaced_rows(job: Job, ks: list[int], ref: Reference) -> tuple[np.ndarray, dict]:
    """G (row k: the differenced gradients of coordinate k) and the energy route to H_kk, with the pair check after every coordinate."""
    a = job.a
    G = np.zeros((3 * job.n, 3 * job.n))
    ediag = {}   # k -> (E+ + E- - 2 E0)/h², the energy route to H_kk (energies stored since 30 Sep 2026)
    for k in ks:
        gs = displaced_pair(job, k, ref.energy)
        G[k] = (gs["p"].ravel() - gs["m"].ravel()) / (2 * a.step)
        e_files = [os.path.join(a.out, f"ener_{k:02d}_{s_}.npy") for s_ in ("p", "m")]
        if all(os.path.exists(f_) for f_ in e_files):
            ediag[k] = (float(np.load(e_files[0])) + float(np.load(e_files[1])) - 2 * ref.energy) / a.step ** 2
        drift = pair_consistency(gs["p"], gs["m"], ref.gradient)
        job.log(f"pair check coordinate {k:2d}: max |mean(g+, g−) − g0| = {drift:.1e} a.u. (limit {FIRST_PAIR_LIMIT:.0e})")
        if drift > FIRST_PAIR_LIMIT:
            job.log(f"PAIR CHECK FAILED at coordinate {k}: the displaced calculations are not on the reference's surface (27 Sep 2026: six of ten cores "
                    "frozen gave 2–9e-4) — stopping before more gradients are bought")
            raise SystemExit(3)
    return G, ediag


def assemble(job: Job, G: np.ndarray, ops, reps) -> Assembly:
    if not job.a.symmetry:
        return Assembly(0.5 * (G + G.T), None, float(np.abs(G - G.T).max()))
    H, spread = SYM.reconstruct({i: G[3 * i:3 * i + 3] for i in reps}, ops, job.n)
    job.log(f"symmetry reconstruction: spread of multiply-reached rows {spread:.2e} a.u.; self-check {SYM.self_check(H, ops, job.n):.1e}")
    return Assembly(H, spread, spread)     # the symmetric run's consistency measure (24 Sep: the Hessian's log line needs it; it crashed a smoke once)


def require_energy_route(job: Job, g0: np.ndarray) -> None:
    """Decision 61 (6 Oct 2026): the energy route to the reference gradient runs in every assembling run — free, end to end."""
    er = energy_route_gradient_check(job.a.out, g0, job.a.step)
    job.log(f"energy route to the reference gradient: max |g0 − (E(+h) − E(−h))/2h| = {er['max_grad_diff']:.1e} a.u. over {er['n_coordinates']} "
            f"coordinates (limit {ENERGY_GRAD_LIMIT:.0e}) — {'PASSED' if er['passed'] else 'FAILED'}")
    if not er["passed"]:
        job.log("ENERGY ROUTE FAILED: the reference gradient disagrees with the displaced energies — no Hessian written")
        raise SystemExit(6)


def write_hessian(job: Job, asm: Assembly, chk: dict, ref: Reference) -> str:
    a = job.a
    out_name = {"VALID": "hessian_ccsd_t.npz", "INVALID": "hessian_ccsd_t_INVALID.npz", "IMAGINARY": "hessian_ccsd_t_IMAGINARY.npz"}[chk["status"]]
    save_atomic(os.path.join(a.out, out_name), lambda fh: np.savez(
        fh, H_raw=asm.H, H_projected=chk["H_projected"], freq_cm=chk["freq_cm"], energy=ref.energy, gradient=ref.gradient, coords_bohr=job.x0,
        step=a.step, basis=a.basis, symmetry_reduced=bool(a.symmetry), symmetry_spread=(asm.spread if asm.spread is not None else -1.0),
        frozen=job.s.frozen, status=chk["status"], vib_cm=chk["vib_cm"], trans_sum_rule=chk["trans_sum_rule"]))
    job.log(f"Hessian written ({chk['status']}); FD asymmetry max {asm.asym:.2e} a.u.; vibrational frequencies (cm-1): "
            f"{np.round(chk['vib_cm'], 0).astype(int).tolist()}")
    job.log(f"two-route checks: translational sum rule {chk['trans_sum_rule']:.1e} E_h/bohr² (limit {HC.TRANS_SUM_LIMIT:.0e}); "
            f"translations/rotations after projection max {chk['tr_max_cm']:.1e} cm⁻¹; energy route max |H_kk − d²E/dx_k²| "
            + (f"{chk['energy_diag_max']:.1e} E_h/bohr² over {chk['energy_diag_n']} coordinates (limit {HC.ENERGY_DIAG_LIMIT:.0e})"
               if chk["energy_diag_n"] else "not available (energies not stored for these displacements)"))
    return out_name


def write_apt(job: Job, ks: list[int], ops, reps, status: str) -> None:
    """3 Oct 2026 (odds lever 4): the CC atomic polar tensor over the same displacements, when every displaced dipole is stored."""
    a = job.a
    dips = {k: [os.path.join(a.out, f"dip_{k:02d}_{s_}.npy") for s_ in ("p", "m")] for k in ks}
    if not all(os.path.exists(f_) for fs in dips.values() for f_ in fs):
        return
    dmu = {k: (np.load(fs[0]) - np.load(fs[1])) / (2 * a.step) for k, fs in dips.items()}
    if a.symmetry:
        P, pspread = SYM.reconstruct_apt({i: np.array([dmu[3 * i + x] for x in range(3)]) for i in reps}, ops, job.n)
        pcheck = SYM.apt_self_check(P, ops, job.n)
    else:
        P = np.array([dmu[k] for k in range(3 * job.n)]).T
        pspread = pcheck = 0.0
    sum_rule = float(np.abs(P.reshape(3, job.n, 3).sum(axis=1) - a.charge * np.eye(3)).max())
    save_atomic(os.path.join(a.out, "apt_ccsd_t.npz"), lambda fh: np.savez(fh, apt=P, step=a.step, symmetry_spread=pspread, self_check=pcheck,
                                                                         sum_rule_max=sum_rule, hessian_status=status, coords_bohr=job.x0, basis=a.basis))
    job.log(f"APT written (apt_ccsd_t.npz): translation sum rule max |Σ_A P_A − qI| = {sum_rule:.1e} e; symmetry spread {pspread:.1e}, "
            f"self-check {pcheck:.1e}")


def stop_on_status(job: Job, chk: dict, out_name: str) -> None:
    if chk["status"] == "INVALID":
        job.log(f"SELF-CHECK FAILED: {'; '.join(chk['reasons'])} — written as {out_name}; no read-out may run on it (guard of 27 Sep 2026)")
        raise SystemExit(2)
    if chk["status"] == "IMAGINARY":
        job.log(f"SELF-CHECK IMAGINARY: {'; '.join(chk['reasons'])} — computed correctly but not a minimum at this geometry; written as "
                f"{out_name}; excluded from every read-out (the user, 30 Sep 2026: only results of correct calculations)")
        raise SystemExit(4)


def header(job: Job, derived: int) -> str:
    a = job.a
    return (f"E8 FD Hessian: {job.n} atoms, {a.basis}, frozen {job.s.frozen} (derived from the elements: {derived}), step {a.step} bohr, "
            f"{2 * 3 * job.n} displacements, {a.threads} threads, max_memory {a.max_memory} MB"
            + (f", charge {a.charge}, spin {a.spin} (UHF-UCCSD(T))" if a.spin else "")
            + ", explicit (T) lambda" + (", fast (T) density kernel" if a.fast_t_density else "") + (", fast (T) lambda kernel" if a.fast_t_lambda else ""))


def run(a, log: RunLog) -> None:
    fast = load_fast(a)
    problem = gate1_problem(a.fast_t_density, a.spin > 0, a.fast_t_lambda)
    if problem:
        raise SystemExit(f"gate 1 not passed on this machine for this code: {problem}. Run: python tests/test_acceptance_water.py "
                         "(≈ 1 min; energy vs psi4, gradient vs FD of the energy, frequencies vs CCCBDB, C kernel vs pyscf)")
    g = json.loads(Path(a.geometry).read_text())
    symbols, x0, masses = g["symbols"], np.array(g["coords_bohr"], float), np.array(g["masses_amu"])
    frozen, derived = resolve_frozen(a, symbols)
    job = Job(a, symbols, x0, masses, CCSettings(a.basis, frozen, a.charge, a.spin, a.max_memory, fast), log)
    log(header(job, derived))
    if a.two_route_check == "energy":
        return energy_check(job)
    if a.two_route_check == "only":
        return only_check(job)
    ref = reference(job)
    if a.only_reference:
        return None
    if not a.ks and not ref.checked:
        require_passed_check(job)
    ks, ops, reps = displacements(job)
    if a.ks:
        ks = select_displacements(ks, a.ks)
        log(f"partial run: displacement indices {ks}")
    G, ediag = displaced_rows(job, ks, ref)
    if a.ks:
        log("partial run done; merge grad_*.npy files and rerun without --ks to assemble the Hessian")
        return None
    asm = assemble(job, G, ops, reps)
    require_energy_route(job, ref.gradient)
    chk = HC.classify_hessian(asm.H, x0, masses, asm.asym, ediag)
    out_name = write_hessian(job, asm, chk, ref)
    write_apt(job, ks, ops, reps, chk["status"])
    stop_on_status(job, chk, out_name)
    return None


def main():
    a = build_parser().parse_args()
    lib.num_threads(a.threads)
    os.makedirs(a.out, exist_ok=True)
    with RunLog(a.out) as log:
        return run(a, log)


if __name__ == "__main__":
    main()
