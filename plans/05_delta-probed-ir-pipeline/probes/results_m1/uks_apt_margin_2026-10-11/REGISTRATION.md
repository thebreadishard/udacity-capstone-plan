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
