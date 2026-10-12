# Design note — a residual-checked response for route C's dipole derivatives (12 October 2026)

*Status: proposal; the user decides before any change to the labels server's code. Written on the user's word ('Ja, doe beide maar', 12 Oct).*

## Why

Route C (`corpus/apt.py`, in production on the labels server since 11 Oct) contracts the CPHF response that pyscf's analytic Hessian solves into
the atomic polar tensor (APT), from which the band heights follow. On 12 Oct (`probes/results_m1/uks_apt_margin_2026-10-11/REGISTRATION.md`,
addendum) that response was found off its own linear system: pyscf 2.14.0's `lib.krylov`, which solves all 3N right-hand sides of the Hessian at
once, returns a solution 7e-5 to 1e-4 off the system for DFT, whatever `tol` and `max_cycle` say, without a warning (pyscf issue #2702; master's
fix #3334 does not change this case: 5.6e-5 with master's solver files laid over 2.14.0). The Hessian is insensitive at this level (benzene: 0.06
cm⁻¹ against the frozen-grid finite difference of the gradient), so the **labels are not affected**. The APT is first order in the response and
is: benzene B3LYP 4.3e-4 e against the field route (which agrees with finite differences of the dipole to 3.9e-5), heights ≤ 0.6 % per band.

## Measured options (benzene, B3LYP/6-31G* Cartesian, grid 99/590 — the labels route's settings; `probes/results_m1/krylov_report_2026-10-12/`)

| option | APT against the field route | extra time (Hessian 780 s) | notes |
|---|---|---|---|
| as now | 4.3e-4 e | 0 | the production state |
| GMRES per direction, from pyscf's solution | 3.75e-5 | 1,171 s (408 one-vector operator calls) | `refine_timing.py`; too dear |
| **one round of batched defect correction** | **3.75e-5** | **≈ 120 s** (one residual call ≈ 50 s, then 7 batched calls) | `refine_batched.py`; residual 1.3e-4 → 7.8e-8 |
| the field route instead of route C | (the reference) | ≈ 440 s (6 SCFs, 12 gradients) | `probes/apt_field_route.py`; independent, dearer |

## Proposal

1. **`corpus/apt.py`: `refine_response(mf, hobj, mo1, h1ao)`** — forms the residual of all 3N directions in the solver's own system in one batched
   operator call, solves the correction equation with the same multi-root `lib.krylov` and adds it; repeats at most three rounds until the
   residual is ≤ 1e-6 (the bound: 3.75e-5 e on the APT was reached at 7.8e-8; 1e-6 keeps a margin of two orders over what the heights need).
   Returns the refined response and the residual reached. The Hessian is computed from pyscf's own response as now — the labels stay
   bit-identical; only the APT uses the refined response.
2. **`analytic_hessians.py`** writes the residual before and after into `dipole_b3lyp_cphf.npz` (`cphf_residual_before/after`) beside the
   `software` stamp; an APT whose residual stays above the bound is written with `passed=False` and the molecule exits 3, as a failed sum rule
   does now.
3. **Tests:** on water at a small grid, the refined APT against the field route within 5e-5 (the field route's O(F²) error is 9e-6 at F = 1e-3);
   the residual reported falls below the bound; a test that a too-tight bound marks the APT failed.
4. **Second route on a sample:** the field route on five molecules of the labels list after the install (≈ 8 min each at 4 threads on the laptop),
   max |ΔAPT| ≤ 1e-4 e as the line.
5. **Install:** as route C was — water smoke in `staging_apt`, atomic replace between molecules, `install.log`. Cost on the server ≈ +15 % per
   molecule's B3LYP pass (the ωB97X pass is untouched): ≈ +1 day on the ≈ 470 remaining molecules at 0.44 per lane-hour.

## Decisions for the user

- **(a)** Install the refined response on the labels server, as above?
- **(b)** The route-C APTs written since 11 Oct 10:49 (45 files on the server at 11:0x, 12 Oct): recompute their APTs (SCF + make_h1 + response + refinement, no Hessian;
  ≈ 5 min each, on the laptop when it is free), or keep them with their error marked (heights ≤ 0.6 %)?
- **(c)** When pyscf fixes #2702 in a release, the refinement stays as a guard (one cheap residual check), per the upgrade checklist.
