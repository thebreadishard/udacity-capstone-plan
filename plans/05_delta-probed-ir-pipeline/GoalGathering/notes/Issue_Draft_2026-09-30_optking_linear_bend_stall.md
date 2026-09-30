# Issue draft, 30 September 2026 — optking: optimisation stalls (100 % CPU, no output for hours) after a bend is switched to linear-bend coordinates

*Concept for the user (30 Sep 06:5x: issue and any PR only on the user's word). Target: psi-rking/optking (the optimiser), with a cross-reference on
psi4/psi4 if they prefer. Written in English for GitHub. The reproduction section is filled from `/root/optking_repro/` on hel1-23 (status at the end).*

## Title

`psi4.optimize` hangs indefinitely (single core spinning, no output) after optking introduces linear-bend coordinates for an ethynyl angle

## Environment

- psi4 1.11, optking 0.5.0, qcelemental 0.51.2 (conda-forge, Linux x86-64, Ubuntu 24.04, 16 threads)
- B3LYP/6-31G*, `scf_type df`, `e_convergence 1e-8`, `symmetry c1`, `no_reorient`, `no_com`; optimiser options at their defaults
- Molecule: 1-ethynyl-naphthalene-8-carboxylic acid, SMILES `C#Cc1cccc2cccc(C(=O)O)c12`, 23 atoms, start geometry RDKit ETKDG + MMFF
  (input geometry and full `psi4.out` attached: `probes/results_m1/optking_stall_2026-09-30/`)

## What happened

The optimisation ran 14 normal steps (≈ 2 minutes). At step 14 optking replaced the ordinary bend of the ethynyl angle C(ring)–C≡C, then at
170.5°, by the linear-bend pair `L(3,1,16)` / `l(3,1,16)`; the complement `l` is reported at exactly 180.000000 (its reference axis, not a value of
the geometry). In the step that followed, `l(3,1,16)` was displaced by −9.41° in one step (`psi4.out` line 12409: previous 180.000, force 0.00032,
change −9.41185, new 170.588) while every other coordinate moved by less than 0.2°. The next SCF converged normally (energy −650.5870277), optking
printed the new internal-coordinate values (`L(3,1,16) = 176.92°`, `l(3,1,16) = 180.000°`, `L(2,1,16) = 177.74°`, `l(2,1,16) = 180.000°`, line
13173–13176) — and then nothing more was written for five hours. The process stayed at ≈ 110 % CPU (one core spinning) with 3 GB RSS; no exception,
no `geom_maxiter` exit (default 50 iterations, only 15 taken). We terminated it.

The same molecule with `opt_coordinates cartesian` optimises without incident (our standing workaround since 20 September for near-linear bends;
`geom_maxiter 200`).

## Why we think it is optking

- The last lines written are optking's coordinate report of the new geometry; psi4's next `tstart()` header never appears, so the hang is between
  optking's step and the return to psi4 (or in optking's preparation of the next step: back-transformation / coordinate check of the new linear bends).
- The one-step 9.4° move of a linear-bend complement that is defined at exactly 180° looks like the trigger: the coordinate pair is near-degenerate and
  the back-transformation may not converge, looping without a cap.

## Reproduction

`psi4_worker` with the attached `job.json` (identical geometry, options and thread count), run again on a second machine with `py-spy` attached and a
10-minute no-output detector: **the hang did not recur in this attempt, but the same coordinate failed in the open.** The second run took 50 iterations (7.5 min) and ended with `PsiException: Could not converge geometry optimization in 50 iterations`; on the way optking raised, and internally caught, `AlgError: Back transformation failed. Cartesian Step size too large. Please restart from the most recent geometry` and `AlgError: Could not compute T((3, 2, 0, 15)). Problem computing interior bend.` — 19 AlgErrors in all, among them `Linear bends detected`, `New linear angles`, `Tors.q: unable to compute torsion value` and the interior-bend failures on the atoms around the ethynyl carbon (0-based 3-2-0-15, 0-15-2-3, 0-15-2-14 ≈ the `L(3,1,16)` / `L(2,1,16)` pair of the first run). So the two runs of one input show the two faces of the same problem: a back-transformation that fails loudly and repeatedly (run 2) or spins silently (run 1). Logs of both runs attached (`repro_hel1-23_worker.log`, `psi4_out_excerpt.txt`).

## What we ask

Either a convergence cap with a clear failure in the back-transformation when linear-bend coordinates are introduced mid-optimisation, or a guard that
does not step a complement coordinate by several degrees in one iteration. A `py-spy dump` of the stalled process is attached when the reproduction
delivers one.

---

### Reproduction status (repo-internal, not part of the issue)

- 30 Sep 07:04 (05:04 UTC) started on hel1-23 (`/root/optking_repro/run_repro.sh`, 16 threads, py-spy 0.4 in env `qc`).
- 07:11: worker exited by itself after 50 iterations (no stall, so no py-spy dump); 19 AlgErrors on the ethynyl bend in `worker.log` (back transformation failed, linear bends detected, new linear angles), then the 50-iteration PsiException. The hang is therefore not deterministic on this input; the py-spy dump now waits for the next natural stall (the guard in `run_corpus.py` writes `stall_stack.txt`). Decision for the user: post the issue with the two logs now, or wait for a stack trace.
