# Pre-registration — one engine for the product: pyscf + geomeTRIC geometries against the corpus's psi4 geometries (TASKS 73)

1 November 2026, 10:4x. Written before any computation for this check. The user's decision of 1 November (`docs/product_repo_design.md`,
'Three design points', point 1, and 'Decisions'): pyscf + geomeTRIC becomes the product's one required engine, after this check; the
line is 0.3 cm⁻¹, with the user's condition that above the line the new value must be the less true one, not only a different one. The read:
`probes/engine_check_read.py`, tested on synthetic route files (`tests/test_engine_check_read.py`: equal routes, a family on the line and
just beyond it, a better pyscf route, and every inconsistency refused). The run script is written after this registration and before
any run, and is checked by check 0 below.

## Why

The corpus's geometries come from psi4 1.11 (deck v1: B3LYP/6-31G*, DFT grid 75/302, optking's default convergence), because psi4 was the
engine on the laptop on 5 September; its Hessians and APTs come from pyscf since 23 September. The network was trained on B3LYP Hessians
at those psi4 geometries. A public package needs one engine that installs with pip, and pyscf with geomeTRIC is that engine. A geometry
from another optimiser sits slightly elsewhere, so the network's input changes; what matters is whether its answer is then less true.

## The design

**Molecules:** the clean hold-out (a), the licence's set `a8` (`modules/05_support_predictor/out/holdout_a_clean_2026-10-30.txt`), never
trained under any id: benzophenone, fluoranthene, phenanthrene, biphenylene, benzene, phenanthridine, fluorene, biphenyl (12–26 atoms, 174
in all). The corpus holds, for each, the psi4 geometry and the analytic B3LYP and ωB97X Hessians there (grid 99/590).

**psi4 route (exists):** the corpus folder as it is: geometry from psi4 (optking 0.5.0, `g_convergence` QCHEM: max force 3e-4 E_h/bohr,
ΔE 1e-6, max displacement 1.2e-3), `hessian_b3lyp_analytic.npz` as the network's input, `hessian_wb97x_analytic.npz` as the truth.

**pyscf route (new, per molecule, in WSL pyscf 2.14.0, `~/qc05`):**
1. the same start geometry the corpus's psi4 run started from (`corpus/run_corpus.start_geometry` of the manifest row: RDKit ETKDG +
   MMFF, seed 0), checked against the folder's recorded start as `m08/reuse.py` checks it;
2. a B3LYP/6-31G* optimisation with geomeTRIC through `pyscf.geomopt.geometric_solver.optimize`, at the Hessian's grid (99/590, unpruned,
   as `corpus/analytic_hessians.py` builds it), SCF `conv_tol` 1e-11, convergence set GAU_TIGHT (max force 1.5e-5 E_h/bohr); the call
   is the one in pyscf's own `examples/geomopt/01-geomeTRIC.py` and in our `probes/route2_optimise.py` (22 Sep 2026); 100 steps at most;
3. at the optimised geometry, `corpus/analytic_hessians.py --functionals b3lyp,wb97x --no-apt --grid 99,590`: the network's input and the
   truth, by the same code as the corpus's.

The convergence is tighter than psi4's: the product's route is meant to be the better-converged one, and a frequency calculation wants a
small residual force. The check therefore measures the product's whole route against the corpus's, engine and convergence together; the
residual force of both geometries at grid 99/590 is reported beside the result (one B3LYP gradient at each psi4 geometry).

## The measure and the line

Per route, the network's error per mode family on the eight molecules, per seed, by the licence's read-out (the per-family error of
`probes/rungC_eval_saved.py` that `m08/accuracy.py` and `m08/licence.py` read; families ring-ip, CH-stretch, CH-oop, other), each route
against the ωB97X Hessian at its own geometry. The line (`engine_check_read.py`):

- **E — not less true:** in every family, the pyscf route's seed-mean error is at most **0.3 cm⁻¹** above the psi4 route's
  (difference pyscf − psi4 ≤ 0.3; lower is allowed and reported).

**The deciding read uses v1.5** (TASKS 149: canonical primitives, cos dihedrals), the first carried version without the dihedral wrap:
under v1.3 a 1e-4 bohr geometry difference moved phenanthrene's bands by 1.21 cm⁻¹ (30 Oct), so v1.3 would measure the network's defect,
not the engine. Until v1.5 is carried, a read with v1.3 is made for information only, never as the verdict. If v1.5 is not carried, the
deciding read waits; it is not moved to another version without an amendment written before that read.

**Information, not deciding:** per molecule the largest coordinate difference between the two geometries (after a rigid fit), the B3LYP
frequency differences, the corrected band shift between the routes, the residual forces, the optimisation's steps and seconds.

**Check 0, before any read:** the run's own evaluation, applied to the corpus folders with the deciding models, reproduces those models'
recorded `a8` read per family and seed to 1e-9 cm⁻¹ (`check0.max_abs_difference` in the psi4 route file); the read refuses otherwise. This
proves that the pyscf numbers come out of the same read-out as the licence's.

## Outcomes

- **E holds →** pyscf + geomeTRIC is the product's one required engine; psi4 stays an optional route that reproduces the corpus deck.
- **E fails →** the family or families beyond the line are named, and the user and I choose between psi4 staying required and training
  on pyscf geometries. No line moves after the read.

## Prediction

**E holds.** The truth moves with the geometry, and both routes reach the same minimum within the looser route's tolerance; the
differences should sit in the soft modes of biphenyl and benzophenone (their ring torsions), where the 'other' family is already the
weakest, by a few tenths of a cm⁻¹ at most.

## Order and cost

Water first as the smoke (the run script end to end, numbers not read), then benzene timed, then the other seven in the order of the
list, in the first free laptop slot (the laptop runs geometry_term today). Estimate: two analytic Hessians a molecule (pipeline 0.4's
phenanthrene B3LYP Hessian took about an hour at six threads) plus an optimisation of 10–30 gradients, so about 2–3 h for a molecule of
20–26 atoms and 15–22 laptop hours for the eight; benzene's timing replaces this estimate before the others start. Through
`tools/runspec.py launch` with the memory budget of 13 GB for all laptop runs together.

## Amendment (1 November 2026, 11:4x, before any computation of the pyscf route)

Written with the run script `probes/engine_check.py` (`prepare`, `optimise`, `evaluate`), before the first pyscf optimisation.

1. **The compared psi4 route is an analytic-only folder per molecule** (the corpus geometry and its two analytic Hessians, result.json
   labelled analytic-only), as the pyscf route's folders are. The licence's recorded read loaded the corpus folders with psi4's FD pair
   and substituted the analytic one, keeping the mode-family labels from the FD pair (`e7_rungB_reread_analytic.substitute`); a
   pyscf folder has no FD pair and is labelled from its analytic Hessian. Both compared routes now go through the same loader path.
   **Check 0** runs on exact copies of the eight corpus folders (`check0/`, the recorded read's path). Measured with v1.3's three seeds
   (only as the mechanics' test; the deciding models are v1.5's): check 0 = 0.0 cm⁻¹ at four threads, and the analytic-only psi4 route
   gives the same seed means to 1e-4 (ring-ip 1.7733, CH-stretch 1.1857, CH-oop 2.1729, other 3.6240), so the family labels agree for
   these eight molecules (`probes/results_m1/engine_check_2026-11-01/psi4.json`).
2. **torch runs at four threads** in `evaluate`, as the recorded reads ran (`probes/holdout_a_clean.sh`): at the default count check 0
   was 3.1e-8 cm⁻¹, float32 sums following the thread count; at four it is 0.
3. **geomeTRIC is not installed in the laptop's WSL `qc05`** (nor networkx, which it needs); the servers' qc05 has it. The water smoke
   stopped at the import. It is installed (geomeTRIC 1.1.1, as CI pins it) after geometry_term ends — that run uses the same
   environment, and software changes only between runs — and the smoke runs then, before benzene.
