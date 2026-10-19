# Pre-registration — the composite TZ step by density-fitted MP2 (19 October 2026, 22:3x, before any DF-MP2 number)

*The user, 19 Oct ≈ 22:20: 'Ja, goed idee. Doe stap 1 t/m 4 zelfstandig, want ik ga zo slapen.'*

## Why

The composite anchor level (decision 62; `Design_2026-10-04_Composite_Anchor_Level_DZ_TZ.md`) is CC/DZ + [MP2/TZ − MP2/DZ]. Its MP2 rows come
from pyscf's conventional MP2 gradient (`probes/cc_composite_basis_check.gradient`), which held 26 GB per worker on 7 Oct. Anchor set
three's five carried candidates (waves 1–2) need that step: 98 worker-hours priced from the 7 Oct rows, on a server only — and server
spending is paused (the user, 19 Oct 20:5x). pyscf has no density-fitted MP2 gradient (`NotImplementedError` in `pyscf/mp/dfmp2_native.py`
and `pyscf/mp/dfmp2.py`, worktree f09223488; the docs say the same). psi4 has one (`gradient('mp2')` with `scf_type df`, `mp2_type df`),
and psi4 1.10.2 is installed in WSL (env `vpt2`). If the DF basis step equals the conventional one closely enough, the step may fit the
laptop and anchor set three's read stops waiting for a server.

**Upstream tests that make the same call** (CLAUDE.md, a new library call): psi4 `tests/dfmp2-grad1` (`gradient('mp2')`, RHF water,
`scf_type df`, `mp2_type df`, reference gradient to 1e-5) and `tests/dfmp2-grad5` (the analytic DF-MP2 gradient against 5-point finite
differences of the energy, to 1e-7).

## Steps and lines (fixed now)

1. **Route.** `probes/dfmp2_rows.py`: the MP2 Hessian rows of a molecule's symmetry-unique displacements by central differences of psi4's
   analytic DF-MP2 gradient, at exactly the geometry, step, basis, frozen-core count and spherical/Cartesian choice stored in an existing
   conventional row file (`--like`), written in the same file format so `cc_composite_full_check.py` assembles it unchanged. Fitting basis
   sets `<basis>-jkfit` (SCF) and `<basis>-ri` (MP2); frozen core set as the stored count (`num_frozen_docc`); C1, no reorientation.
   psi4's own output file is kept beside the rows (the library log rule).
2. **W — two routes on water.** The analytic DF-MP2 gradient (frozen 1s) against 5-point finite differences of the DF-MP2 energy, cc-pVDZ
   and cc-pVTZ, at a non-equilibrium geometry. **Line: max |Δg| ≤ 1e-6 Eh/bohr on both** → the route's gradient is valid; otherwise stop.
3. **S — the swap on pyridine and naphthalene** (the molecules whose conventional DZ and TZ rows exist, 7 Oct queue). With the same
   conventional MP2/DZ Hessian as base, the vibrational frequencies of M_DZ + Δ_DF against M_DZ + Δ_conv (= the conventional MP2/TZ
   Hessian), Δ = M_TZ − M_DZ, all modes (`probes/dfmp2_swap_check.py`). **Lines, per molecule:** max |Δω| ≤ 0.5 cm⁻¹ on both → the DF route
   is adopted for anchor set three's composite step; ≤ 2.0 → noted, adopted only with the difference carried as a named error of the
   composite; > 2.0 on either → refused, the conventional route stays. Reported beside: rms(Δ_DF − Δ_conv) / rms(Δ_conv), the symmetry
   spread of the DF rows. The CC anchor is not needed: the swap changes only the basis step, in one frame.
4. **P — price.** Seconds per DF row at DZ and TZ measured on pyridine and naphthalene (psi4 at 6 threads, 4 GB, under
   `probes/wsl_capped.sh`, peak RSS logged); a power law in atoms through the measured rows predicts the five anchors' worker-hours, and the
   peak RSS says whether they fit the laptop's 13 GB budget beside its other runs. Stated, not launched: the launch of the five is the user's
   read of this.

**Prediction (before any number):** W passes by a wide margin (≤ 1e-7); S passes, max |Δω| < 0.3 cm⁻¹ on both (the fitting error is
nearly the same in DZ and TZ and cancels in the difference) — three in four; DF rows are ≥ 5× faster than the conventional ones.

## Outcome

*(appended after the reads)*
