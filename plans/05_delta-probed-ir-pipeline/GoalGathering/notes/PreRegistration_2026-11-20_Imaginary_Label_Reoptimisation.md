# The corpus molecules with an imaginary label mode, re-optimised at the label settings — registered before the run

**Written 20 November 2026, before any of these molecules is re-optimised.** TASKS 215. Nothing here writes into the corpus,
swaps a label or retrains a network; section 7 lists what is not decided.

## 1. The question

A corpus molecule whose analytic label has an imaginary mode never trains: `m05/build_release.py` skips it. The decision of
TASKS 215 is to repair these at the source: re-optimise each molecule at the label route's own settings and compute both analytic
Hessians again at the new geometry. The question this run answers, per molecule: **does one re-optimisation at the label settings
give two labels without an imaginary mode, for the same molecule?**

## 2. The list, recomputed from the corpus today

`probes/low_mode_coverage.py --out probes/results_m1/imaginary_reopt_2026-11-20/coverage_before` read the 1,154 corpus folders
that carry both analytic labels on 20 November: **42 molecules have a lowest projected vibrational mode below zero in at least
one label** (20 below −50 cm⁻¹, 18 between −50 and −20, 4 between −20 and 0; 11 in both labels). The list with atoms, formula
and both lowest modes is `probes/results_m1/imaginary_reopt_2026-11-20/ids_imaginary.tsv`. In 41 of them the B3LYP label is
imaginary, in 12 the ωB97X label. Sizes: 10 to 38 atoms; 32 molecules have at most 25 atoms.

- **One molecule is not run: P3c_0028cdfd85**, the only cation of the list (charge 1 in its `job.json`; B3LYP lowest +32.54,
  ωB97X −482.64 cm⁻¹). `probes/reoptimise_at_label_settings.py` builds a neutral closed-shell molecule and has no charge
  option, and this molecule's B3LYP label, the one the script optimises on, has no imaginary mode. It stays out and keeps its
  own line on TASKS 215.
- **The four between −20 and 0** (B_1e0fa2d7f0 −11.95, A2_187a20beab −8.11, B_04f049ae58 −7.17, B_84485091e3 −3.53) carry
  the low-mode repair of 13–14 November already and stayed negative after it.

## 3. What is known, and how far it goes

One molecule has been through this script: D_ac28161d06 (38 atoms), on 11 November. Its re-optimisation converged in 14 steps
and **left the B3LYP mode where it was** (−7.48 before, −9.5 after; ledger, 11 Nov 23:4x). What made the mode positive was the
low-mode repair on 13 November (−7.48 → +7.05 cm⁻¹ at the corpus geometry; ledger, 13 Nov 20:5x): that mode was an artefact
of the missing grid-weight derivative, not a saddle. So the one done case is not evidence that re-optimising removes an
imaginary mode. For the 38 molecules below −20 cm⁻¹ the artefact is too small to be the cause (it moves a mode by a few
cm⁻¹); the likely cause there is a geometry that psi4 (density fitting, grid 75,302) left on or near a saddle of the label
settings, which a push along the mode and an optimisation at those settings can leave. That is an expectation, not a
measurement; this run is the measurement.

## 4. What is run

Per molecule, the two steps of `probes/reoptimise_label_settings.sh` (the laptop wrapper of 11 November), through
`probes/imaginary_reopt_lane.sh`, which calls them without WSL and into a folder outside the corpus:

1. `python probes/reoptimise_at_label_settings.py <corpus folder> <out>/<id> --threads 8 --max-memory 24000` with the script's
   defaults: the start geometry pushed 0.05 bohr (largest atom) along the lowest B3LYP label mode when that mode is negative;
   geomeTRIC at the labels' SCF (B3LYP/6-31G*, Cartesian d, no density fitting, grid (99,590)), energy 1e-7, gradient rms 1e-5
   and max 2e-5, displacement rms 1e-4 and max 2e-4, at most 100 steps; an optimisation that does not converge raises and
   writes no geometry.
2. `python modules/05_support_predictor/corpus/analytic_hessians.py <out>/<id> --threads 8 --max-memory 24000 --reuse-existing`:
   both analytic Hessians, the APT with its residual check, and the route's own low-mode repair for any mode below 20 cm⁻¹.

**The environment is `qc215` for both steps: pyscf 2.15.0, geomeTRIC 1.1.1, the laptop `qc215`'s pins.** Two reasons. The
label route's low-mode repair needs pyscf 2.15.0 (`analytic_hessians.py`, `REPAIR_MIN_PYSCF`), and a molecule that leaves a
saddle is likely to have a soft mode. And the optimiser needs geomeTRIC, which the servers' `qc05` recipe
(`tools/bootstrap_qc05_env.sh`) does not install. The corpus's other labels were made with pyscf 2.14.0; the two versions'
analytic Hessians were compared on three molecules: benzene and B_0f06474656 (ledger, 12 Nov 19:5x; at most 0.24 cm⁻¹ on one
mode at 1187.9 cm⁻¹, 0.013 on the lowest) and D_ac28161d06 (every mode within 0.018 cm⁻¹; ledger, 13 Nov 08:5x). A label
made here differs from a 2.14.0 label by that much and carries its versions in its `software` field.

**No library call is new.** The optimisation call is `geometric_solver.kernel` as pyscf's own
`pyscf/geomopt/test/test_geometric_solver.py` (`test_optimize_with_hessian`) makes it, through `probes/geomopt_verdict.py`;
the Hessian and the repair are the label route's.

**Where it runs and writes.** On the rented CCX53 `night20` (`tools/hosts.tsv`), from a `git archive` of the branch commit
that holds the lane script, into `/root/night20_215/out/<id>/`; the corpus inputs are copied there and only read. Fetched to
`probes/results_m1/imaginary_reopt_2026-11-20/`. The corpus on the laptop is not touched: the training search reads it.

## 5. The acceptance rule, per molecule, decided now

`probes/imaginary_reopt_read.py` reads each re-optimised folder beside its corpus folder. A molecule is **accepted** when all
four hold, and **stays out** with the first reason that fails:

1. **The optimisation converged** by the criteria of section 4: the folder holds `geometry.json`, which the optimiser writes
   last and only then.
2. **The labels are complete**: both label files exist, neither is marked `low_mode_pending`, and the APT file exists.
3. **No imaginary mode in either label**, after the label route's own soft-mode repair: the lowest projected vibrational
   frequency of both is above zero by `vibrations.vibrational_modes` (the route section 2 counted with), and the label
   route's own counts in `result.json` are both zero. A frequency of exactly zero is not accepted.
4. **It is still the same molecule**: the atoms are the corpus folder's in its order, and the bond graph is unchanged
   (`e8_cc_locality.bond_graph`, the existing geometry-based check: bonded below 1.2 times the sum of the covalent radii).

Reported beside the verdict and not deciding: the rms distance from the corpus geometry after a rigid rotation
(`frame_match.kabsch`), over all atoms and over the heavy atoms. A heavy-atom distance above 0.5 bohr is **flagged as another
conformer**. A flagged molecule that passes the four conditions is accepted by this rule; whether a label at another conformer
replaces the corpus row is put to the author at the swap, with the list.

A molecule that stays out is listed with its reason and gets no second attempt in this run (chain 42's rule: one
re-optimisation). The eleven molecules whose ωB97X label is imaginary too can fail on that label alone: the corpus computes
both Hessians at the B3LYP geometry, and the optimisation follows B3LYP only.

The read ran on synthetic records before this note was committed (`tests/test_imaginary_reopt_read.py`, 17 tests, on a bent
triatomic held by springs and a four-carbon chain): an accepted folder; a rotated and shifted copy is the same geometry; no
folder and no geometry; still imaginary, with its frequency; a lowest mode of exactly zero; a pending label; a missing label
file; a missing APT; the route's count disagreeing or absent; a broken and a made bond, named; another atom order; upper-case
symbols; another conformer flagged and not refused; one row per molecule; a repeated id refused.

## 6. Cost and order

Priced from each molecule's own label: the seconds of its two analytic Hessians in its `analytic_check.json` (made at 8
threads on a CCX53 with four lanes), times 1.3 for the optimisation and a possible repair (D_ac28161d06's optimisation was
5,036 s beside 54,850 s of Hessians, a factor 1.09; taken wider because a molecule that leaves a saddle needs more steps).
The 41 molecules come to **152 lane-hours** at 8 threads; four lanes for one night give about 55 to 60. So the list does
not finish in one night, and the order is chosen for that:

- **First the 30 molecules priced at 4.2 hours or less** (54 lane-hours), in four lanes of 13.5 to 13.7 hours, largest first.
- **Then the eleven larger ones, smallest first**, as far as the night goes: A2_197913eb9c, A2_2c22216564, B_663eaca2f1,
  A2_2a0b78bd2b, A2_20e59f3897, A2_220d2c107b, A2_0420908ebe, A2_187a20beab, A2_20747fd501 (4.6 to 8.3 hours each), and last
  P3_2aa4adcc95 (34 atoms, 19 hours) and P3_086e85b2d7 (38 atoms, 27 hours), which one night cannot finish.

The lane lists are `probes/results_m1/imaginary_reopt_2026-11-20/lanes/ids_lane{0,1,2,3}.txt`. A molecule the night does not
finish is reported as not run or unfinished, not as failed; its optimised geometry, if written, is kept and the lane script
resumes from it. The first two lanes start beside TASKS 211's force field, the other two when that has ended, so that the
server never runs more than 32 threads.

**Smoke before the lanes:** the smallest molecule of the list (B_008b0bc366, 10 atoms) through the lane script on the server
into a folder of its own. D_ac28161d06 is not reproduced as a check: its re-optimisation and labels took 17 hours (5,036 s and 54,850 s). That the
server's `qc215` computes the laptop's numbers was shown on a gradient for TASKS 218 (amendment 1 of
`PreRegistration_2026-11-20_Low_Mode_Repair_Threshold.md`: energies within 3.2e-12 hartree, gradients within 1.9e-8
hartree/bohr).

## 7. What this registration does not decide

- Nothing is written into the corpus. Moving accepted folders in is a separate, reviewed step after the training search has
  ended, and the changed labels ride with the one retrain of TASKS 287.
- Nothing about the cation P3c_0028cdfd85, and nothing about a molecule that stays out: whether it gets another start
  geometry, another route or leaves the corpus is the author's decision, with the reasons listed.
- Nothing about whether a flagged conformer is the one the corpus should hold.
- `probes/imaginary_reopt_lane.sh`, `probes/imaginary_reopt_read.py` and its test are on the branch `t215-imaginary-reopt`
  and join the trunk only after the independent review; the run uses the branch commit named in its run specs.

## Amendment 1 (20 November 2026, 14:4x UTC, before any lane is launched) — the smoke, the re-price and the order

**The smoke ran** (section 6; B_008b0bc366, 10 atoms, through `probes/imaginary_reopt_lane.sh` at branch commit b322e94d, env
`qc215`, 8 threads, into `/root/night20_215/smoke`). The optimisation converged in 47 steps and 591 s. The labels: B3LYP lowest
mode −124.65 → +154.2 cm⁻¹, ωB97X +212.88 → +272.2; the route's imaginary counts 0 and 0; the APT's CPHF residual 2.4e-8 with no
refinement round. Whether its bond graph is unchanged is the read's to say, with the others.

**The price was too low.** The smoke took 1,584 s against the 720 s priced: the optimisation 591 s (107 % of the molecule's
stored Hessian seconds, where section 6 assumed 30 %), the B3LYP Hessian 632 s against 241 s stored (pyscf 2.15.0's Krylov
solver reports that it falls back to its per-root solve; 2.6 times the 2.14.0 time), the ωB97X Hessian 360 s against 313 s.
That is 2.86 times a molecule's stored Hessian seconds where section 6 took 1.3, a factor 2.2 on every price of section
6: about 335 lane-hours for the 41 molecules. **This factor comes from one molecule, the smallest; for larger molecules
it is not measured.**

**The order becomes smallest first, over all 41, in four lanes.** The server is rented for one night, about 59 lane-hours until
07:00 UTC on 21 November (two lanes from about 15:45 UTC, two more from about 16:35). In the order of section 6 (largest first
within the night's set) each lane would finish one or two molecules and never reach its small ones; smallest first finishes
the most molecules, and the acceptance rule of section 5 does not depend on the order. The new lists are
`probes/results_m1/imaginary_reopt_2026-11-20/lanes_smallest_first/ids_lane{0,1,2,3}.txt`: all 41 molecules sorted by the
re-priced time, each given to the lane that is free first, so no molecule is in two lists and each list runs from small to
large. The lists of section 6 (`lanes/`) are not run.

**Expected by 07:00 UTC, at the smoke's factor:** 20 molecules finished (6, 6, 4, 4 per lane), the
largest of them 24 atoms; the first not to finish would be A_78896cfe24 (27 atoms). **Every molecule a lane has not
finished when the server is given back is recorded "not run" (or "unfinished", with its optimised geometry kept if it was
written), as section 6 says; that is not a failure and not a verdict.**

Nothing else changes: the call, the settings, the environment, the acceptance rule and what is not decided stand as registered.

## Amendment 2 (20 November 2026, before any re-optimised label was read) — section 5.2, the APT carries passed = True

Section 5.2 says "the
APT file exists". That is too weak: the label route (`corpus/analytic_hessians.py`, `write_apt`) writes `dipole_b3lyp_cphf.npz`
also when the APT fails its sum rule or its CPHF residual, marks it `passed = False`, and then stops with exit 3. The condition
is therefore: the APT file exists and carries `passed = True`. A file with `passed = False` is the label route's own record of
a failed check, and the molecule stays out with that reason; a file without a `passed` mark stays out too, because its checks
are not on record. The independent review of the read script found this on 20 November 2026, before the read ran on any
re-optimised folder; the read (`probes/imaginary_reopt_read.py`) applies the amended condition, and its tests cover a failed, an
unmarked and a cut-off APT file. Nothing else of section 5 changes.
