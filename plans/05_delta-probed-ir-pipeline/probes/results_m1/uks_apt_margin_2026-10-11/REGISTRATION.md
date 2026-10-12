# The cation heights' margin: finite-difference truncation or an error in the analytic UKS APT? — registration (11 October 2026, 22:2x, before the run)

**Why.** The third route (`../apt_route_props_2026-10-11/REGISTRATION.md`) found the analytic UKS APT of 3-hydroxypyridine⁺ 9.0e-4 e from the
finite-difference APT (h = 0.005 bohr), against a limit of 1e-3, while its translation sum rule held to 3.0e-6. A UKS branch of the labels route
(heights for the 60 pool 3 cations) needs a limit with a reason. Two causes are possible: the FD step's truncation error (O(h²)), or an error in
the analytic UKS terms — pyscf 2.14's UKS Hessian has no grid response (`hessian/uks.py` sets `grid_response = False` and never reads it; the RKS
code carries a grid-response path, `hessian/rks.py` near line 1292). A Richardson pair separates the two.

**Molecule and settings.** A second pool 3 cation, `corpus/shards_pool3/a/molecules/P3c_00e041576d` (12 atoms, with sulphur; charge 1, 2S = 1;
saved UKS analytic Hessian), at the labels route's settings (B3LYP/6-31G* Cartesian, grid (99, 590) unpruned, conv_tol 1e-11), 4 threads at
nice 19 beside the five-ring runner (8 threads). FD: `probes/dipole_derivs_fd.py --charge 1 --spin 1`, h = 0.005 and h/2 (145 UKS SCFs,
≈ 3 h from the 72 s per SCF measured on the first cation), then `probes/apt_route_props_probe.py --fd` (the upstream UKS APT, ≈ 21 min, ≤ 2.1 GB).

**Lines (fixed now).**
- M1: the FD route's own sum rule at h/2 ≤ 1e-4 e (else the FD data are not used).
- M2: the analytic APT's sum rule ≤ 5e-4 e; its Hessian against the saved one ≤ 1e-5 (as L2, L4 of the third route).
- M3, the reading. g(h), g(h/2): max |P_analytic − P_FD| at each step; g(R): against the Richardson value P* = (4 P(h/2) − P(h)) / 3.
  - **FD truncation** if g(R) ≤ 1e-4 e and g(h/2) < g(h): the analytic UKS APT stands; for cations the FD check uses P* (or h/2) with the
    limit 1e-4 e, and that limit goes into the UKS design note.
  - **An analytic error** if g(R) > 3e-4 e: the analytic UKS APT carries an error of that size (grid response the first suspect); the design note
    carries it as an error bar on cation heights, or waits for a grid-response route.
  - Between the two: recorded as undecided; the first cation gets the same Richardson pair before the design note.

The result does not change any production file; it decides the limit a later UKS branch registers.

## Outcome, 12 October 2026 03:4x

Files here: `P3c_00e041576d_fd.{npz,log}` (the FD pair), `P3c_00e041576d.{json,log}` (the registered probe run), `chain.log`; the diagnosis below:
`*_field.{npz,log}` (`probes/apt_field_route.py`), `P3c_00e041576d_upstream_apt.npz` (the analytic APT saved), `diagnose_cphf.{py,json,log}`,
`diagnose_xc.{py,json,log}`, `water_field.npz`, `benzene_field.{npz,log}`.

**M1** passes: the FD sum rule at h/2 is 3.0e-5 e (limit 1e-4). **M2** passes: the analytic sum rule 4.1e-6 e, the Hessian against the saved one
7.5e-11. **M3: an analytic error.** g(h) = 3.59e-3, g(h/2) = 3.61e-3, g(R) = 3.62e-3 e (line 3e-4), while the FD pair itself differs by 5.7e-5 e:
the FD route has converged in its step and the analytic UKS APT does not agree with it. (As on the first cation, the heights' L3 also fails, 1.2e-3,
from the asymmetric UKS Hessian, 5.0e-5; on the symmetrised Hessian 9e-8.)

**Diagnosis (not registered lines; each step recorded as it ran).** A third route was built: the APT as minus the field derivative of pyscf's analytic
nuclear gradient in a uniform field (`probes/apt_field_route.py`, F = 1e-3 a.u., with and without the gradient's grid response; test
`tests/test_apt_field_route.py`). On water it agrees with route B's CPHF APT to 7.4e-6 and with FD to 5.5e-6; at HF it converges to route C as F²
(3.6e-5, 9.1e-6, 2.4e-6 e at F = 2e-3, 1e-3, 5e-4).
- *Grid response is not the cause:* the field route with and without it differs by 8e-6 (this cation), 5e-6 (the first), 4e-5 (benzene), 3e-7
  (water); with it the sum rule is exact (1e-10).
- *The field route and FD agree:* 2.8e-4 e on this cation (against FD's Richardson value), 9.9e-5 on 3-hydroxypyridine⁺, 3.9e-5 on benzene.
- *The CPHF-based analytic APT disagrees with both:* upstream's UKS APT against the field route 3.3e-3 e here, spread over the heavy atoms (per
  atom 0.4–3.6e-3); and — the larger news — our closed-shell route B/C on benzene against the field route 4.0e-4 e (against FD 4.4e-4, the gap
  recorded on 11 Oct and then put down to FD).
- *Not the CPHF's convergence:* max_cycle 200 and conv_tol_cpscf 1e-12 change the UKS APT by 3e-10; the Hessian's asymmetry stays 5.0e-5.
- *Not the grid choice:* pyscf's DFT Hessian uses `mf.grids` (`hessian/rks.py`, `uks.py`: `hessobj.grids` falls back to it).
- *In the exchange-correlation part:* route C against the field route on benzene at the same grid — **HF 8.6e-6 (agrees), PBE 2.2e-4, B3LYP
  4.0e-4**. The part every method shares is right; the XC part of pyscf's response (`make_h1`'s XC derivative or the response kernel) is not
  consistent with pyscf's own gradient, already for a GGA without exact exchange.

**What it costs the heights.** On the same Hessian, route C's heights against the field route's: benzene ≤ 0.6 % per band (median 0.2 %, total
0.03 %); this cation ≤ 2.8 % on a 2.6 km/mol band (median 0.08 %, total 0.09 %). The spectra the Atlas draws do not change visibly; the route-C APTs
in production (closed shell) carry an error of this size.

**What follows (open).** (1) Whether pyscf's analytic DFT Hessians — the labels — carry an error from the same XC term: the Hessian uses the same
`make_h1`; a fixed-grid finite-difference check of the analytic gradient on benzene decides it. (2) For the cations' heights the field route is the
validated choice (≈ 15 min per 12-atom cation at 4 threads), not the CPHF APT. (3) A minimal reproduction (benzene PBE, route C against the field
route) for a pyscf report — on the user's word. (4) The 1e-3 limit of route B and of the third route's L5 was wide enough to hide a 4e-4 error;
limits for APTs are set from the field route from now on.

## Addendum, 12 October 2026 09:3x — the cause is pyscf's Krylov solver, not the exchange-correlation terms (correction of the night's attribution)

The night ended with 'the XC part of pyscf's response'. The morning's measurements on benzene, carbon 0, PBE, grid (99, 590), each a script here:
- `diagnose_riddle.py`: on the frozen grid the field route equals FD of the dipole (5e-6, 7e-6, 1e-6 e); route C does not (1.6e-4, 1.1e-4, 2.7e-6);
  `h1` and the density response look close per element, the response's dipole contraction does not (1.7e-4).
- `diagnose_h1.py`: `make_h1` against frozen-grid FD at h = 0.01, 0.005, 0.0025 falls as h² (5e-5, 1.3e-5, 3.3e-6) for HF, PBE and B3LYP — exact.
- `diagnose_kernel.py`: the response function `mf.gen_response(hermi=1)` against FD of Veff: 1.6e-9 (LDA), 8.2e-10 (PBE), 4.6e-10 (B3LYP) — exact.
- `diagnose_rks_cphf.py`: the closed-shell solver at max_cycle 200 / conv_tol_cpscf 1e-12 against the defaults: 7e-11; no 'not converged' line.
- `diagnose_residual.py`: inserted into the CPHF equation built from pyscf's own pieces, the true solution (from frozen-grid FD of the density)
  leaves 3.7e-7, pyscf's solution 1.1e-5 (HF: 4.7e-7 and 3.2e-8).
- `diagnose_krylov.py`: pyscf's solution is off its own solver system by 6.8e-5 (simple fixed-point refinement diverges: the operator's spectral
  radius exceeds 1 — a statement about that refinement, not about the system).
- **`diagnose_gmres.py`, the proof:** the same system solved by GMRES to a residual of 7e-14 gives route C's column against the field route
  **5.9e-6, 2.0e-6, 4.8e-7 e** (from 1.6e-4, 1.0e-4, 2.4e-6).

**Cause.** `pyscf.lib.krylov` (used by `scf/cphf.py solve_withs1` for all 3N right-hand sides of the Hessian at once) stops when the norm of its next,
unnormalised Krylov vector falls below `lindep` (`DSOLVE_LINDEP`, 1e-13) or tol², not on the true residual; for the DFT systems here it returns a
solution 7e-5 off its own equations, the same whatever `tol` and `max_cycle` say, and without a warning. HF converges before that. The functional
mattered only through the solver: the night's 'XC part' attribution is withdrawn. The analytic Hessian, built from the same solution, is
insensitive at this level (benzene 0.06 cm⁻¹ against the frozen-grid FD of the gradient); the dipole derivatives, first order in the response,
are not. The UKS route (`ucphf`, the same `lib.krylov`) is the likely cause of the cations' larger gaps (3.3e-3) — to confirm with the same GMRES test.

**For us.** The route-C APTs in production carry this solver error (benzene ≤ 0.6 % per band height). A fix is cheap and ours to make: solve the
response to a residual we check (GMRES on the solver's own operator, or a refinement of pyscf's solution) inside `corpus/apt.py`, with a test that
the residual is below a stated bound, then the field route as the second route on a sample — a design note and the user's word before the labels
server's code changes.
