# TASKS 44, third route for the band heights — registration (11 October 2026, 14:1x, before any run on a corpus molecule)

**Question.** Does pyscf-properties' infrared module (`pyscf/prop/infrared`, commit 4eee5a43, loaded by `probes/upstream_infrared.py`) give the
same atomic polar tensors (APT) and band heights as ours, closed shell and open shell? Our closed-shell APT comes from two routes that share
pyscf's CPHF solver (route B: a second solve, `probes/dipole_derivs_cphf.py`; route C: the Hessian's own response, `corpus/apt.py`) and is checked
against finite differences of the dipole (`probes/dipole_derivs_fd.py`). The upstream module also uses pyscf's solver, but its own contraction
(core-Hamiltonian dipole derivative `int1e_irp` contracted with the density, then the response term), its own normal modes
(`hessian.thermo.harmonic_analysis`) and its own unit constant (CODATA via scipy). For open shells we have no route at all; upstream has a UKS
module, checked by upstream against Q-Chem (NH3⁺, PBE0, rtol 1e-3).

**Smoke, done before this registration (14:0x):** upstream's own test file `pyscf/prop/infrared/test/test_ir_inten.py` passes in our qc05
environment (pyscf 2.14.0) through the loader: 4 of 4 (RHF, UHF, RKS, UKS against Q-Chem), 8.5 s, 0.49 GB.

**Molecules and settings.** The labels route's settings (`corpus/analytic_hessians.py`): B3LYP/6-31G* Cartesian, grid (99, 590) unpruned, SCF
conv_tol 1e-11, 4 threads at nice 19 beside the five-ring runner (8 threads; 12 of 16 cores in use). Normal modes with the corpus's masses
(`geometry.json`, the main isotopes; upstream's default would be isotope averages), passed to upstream as its `vib_dict`.
- closed shell: water (`probes/results_m1/water_dipole_fd_2026-10-02`), benzene (`corpus/molecules/A_8448043181`) — both with route B and FD files;
- open shell: 3-hydroxypyridine⁺ (`corpus/shards_pool3/a/molecules/P3c_02d75f732a`, charge 1, 2S = 1, a pool 3 cation with a saved UKS analytic
  Hessian), with an FD APT from `dipole_derivs_fd.py --charge 1 --spin 1` (h = 0.005 bohr, written to this folder, not to the corpus).

**Lines (fixed now; the limits are those of routes B and C).**
- L1 closed: upstream APT vs route B's saved APT, max |Δ| ≤ 1e-4 e.
- L2 every molecule: upstream's Hessian vs the saved analytic Hessian (`H_raw`), max |Δ| ≤ 1e-5 Eh/bohr².
- L3 every molecule: heights — upstream's `kernel_ir` vs `corpus/apt.intensities` on the same APT, Hessian and masses: frequencies within
  0.1 cm⁻¹; intensities summed over (near-)degenerate groups (frequencies within 1 cm⁻¹), relative difference ≤ 1e-3 on every group of ≥ 1 km/mol.
- L4 every molecule: translation sum rule of the upstream APT, max |Σ_A P_A − q·I| ≤ 5e-4 e.
- L5 every molecule: upstream APT vs the FD APT, max |Δ| ≤ 1e-3 e (closed shell: the saved FD files; the cation: the new FD run, which must
  pass its own sum rule, 1e-4 e).
- Peak memory and seconds are recorded per molecule.

**Reading.** L1–L5 pass on water and benzene → pyscf-properties is a third implementation that agrees with routes B and C (written with its
numbers). L2–L5 pass on the cation → the UKS module gives cation heights we can trust at the labels route's settings, and a UKS branch for
the labels route (route C's pattern on the unrestricted Hessian) gets its own design note and the user's word before any production change.
A failed line stops the reading at that line: diagnose, record, no adoption.

## Outcome, 11 October 2026 16:3x

Files: `water.json/.log`, `benzene.json/.log`, `P3c_02d75f732a.json/.log` (the registered run), `P3c_02d75f732a_fd.npz/.log` (the FD APT),
`P3c_02d75f732a_diag.json/.log` (a rerun with two diagnostic fields, not registered lines), `diagnose_l3.py/.json`.

| | L1 vs route B (e) | L2 Hessian vs saved | L3 freq (cm⁻¹) / heights (rel.) | L4 sum rule (e) | L5 vs FD (e) | seconds, peak |
|---|---|---|---|---|---|---|
| water | 1.2e-7 | — (no saved analytic Hessian in that folder) | 4.3e-6 / 9.5e-8 | 4.6e-7 | 1.2e-5 | 3, 0.38 GB |
| benzene | 4.8e-7 | 3.3e-12 | 8.0e-4 / 1.5e-6 | 1.1e-4 | 4.4e-4 | 473, 1.51 GB |
| 3-hydroxypyridine⁺ (UKS, ⟨S²⟩ 0.7656) | — | 1.8e-11 | 3.1e-2 / **3.2e-3 FAIL** | 3.0e-6 | 9.0e-4 | 1273, 2.06 GB |

The cation's FD APT (`dipole_derivs_fd.py --charge 1 --spin 1`, h = 0.005 bohr) passed its own sum rule, 3.9e-5 e (limit 1e-4), in 88 min.

**Reading.** Closed shell: L1–L5 pass on water and benzene; pyscf-properties' infrared module is a third implementation that agrees with routes
B and C — its APT against route B's on benzene 4.8e-7 e, its heights against ours 1.5e-6 relative. Open shell: L2, L4 and L5 pass, **L3 fails**
(3.2e-3 against 1e-3), so the reading stops there as registered: upstream's heights are not adopted.

**Diagnosis of L3** (the rerun's diagnostic fields; `diagnose_l3.py` first showed that on the saved, already symmetrised Hessian upstream's modes
and ours agree to 2e-13): the analytic UKS Hessian as pyscf returns it is asymmetric, max |H − Hᵀ| = 6.2e-5 Eh/bohr²; pyscf's
`hessian.thermo.harmonic_analysis` passes it to `numpy.linalg.eigh`, which reads one triangle; the labels route symmetrises first
(`analytic_hessians.py`). On the symmetrised Hessian upstream's heights equal ours to 9.3e-8 relative and the frequencies to 3.8e-6 cm⁻¹. The L3
difference is in pyscf's normal-mode step, not in the APT and not in our heights. pyscf master's `harmonic_analysis` still does not symmetrise
(checked 11 Oct, last change #3491 on 9 Oct): software ledger row 43.

**What follows.** The UKS module's APT passes the sum rule and FD (L4, L5) on a pool 3 cation, so cation heights from it with our own normal modes
on the symmetrised Hessian are within reach; L5's margin is small (9.0e-4 against 1e-3 — the DFT terms carry no grid response; the same order on
NH3⁺ in the pull-request measurement, 2.8e-4), and a design note for a UKS branch of the labels route must settle that limit before the user's word.
