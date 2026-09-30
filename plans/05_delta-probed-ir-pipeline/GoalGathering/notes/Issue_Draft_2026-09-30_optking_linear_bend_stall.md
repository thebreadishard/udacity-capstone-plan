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

## Where the code points (optking 0.5.0, read 30 Sep)

The last line the hung run wrote to its log (its `worker_stdout.txt`, attached) was ` Caught AlgError exception`, preceded by
`Interior angle of   0.7 for bend B((0, 15, 2)) can't work in good torsion`, `Could not compute T((0, 15, 2, 3))`, `Tors.q: unable to compute torsion
value`, and the linear bends ` L(1,16,3)` / ` l(1,16,3)` to be added. Atom 15 (0-based) is the ethynyl hydrogen: a *terminal* atom as the vertex of a
bend whose "interior angle" is 0.7°, i.e. atoms 0 and 2 lie on the same side of the hydrogen (H–C≡C), not a linear bend at all.

1. `v3d.py`, `linear_torsion_check` (line 246 ff.): `phi_bad = not phi_lim < phi < up_lim` treats an interior angle near 0° the same as one near 180°,
   and then appends "all combinations to be safe" — `old_bends.append([a, b, c]); old_bends.append([a, c, b]); …` — and `linear_bends.append(indices[:-1])`.
   A near-zero interior angle means the torsion's second atom is a terminal atom (a connectivity artefact), and the "linear bend" that is added has the
   terminal atom as its vertex.
2. `optimize.py`, `alg_error_handler` (line 427 ff.; the call at line 481), branch `elif error.linear_bends:`: removes the old bends, appends the new LINEAR/COMPLEMENT bends,
   then calls `frag.add_intcos_from_connectivity(ignore_coords=error.old_bends)` for the affected fragments.
3. `addIntcos.py`, the "additional torsions around collinear segments" search (lines 306–360; the walks at 325 and 336): for a collinear j–m–k it walks outward along LINEAR bends
   with

   ```python
   J = j; i = 0
   while i < Natom:
       if C[i, J] and i != m:
           b = bend.Bend(i, J, k, bend_type="LINEAR")
           if b in intcos:      # i,J,k is collinear
               J = i; i = 0; continue
   ```
   (and the same pattern for `K`/`l` at line 336). There is no visited set and no step bound. As soon as the LINEAR bends in `intcos` form a cycle among a
   few atoms — which the permuted "safety" bends of step 1 make possible (`L(1,16,3)` next to `L(3,1,16)`/`L(2,1,16)` in our run, 1-based) — the walk
   reassigns `J` back and forth and never returns. Nothing inside the loop logs, which matches the silence at 100 % of one core. (The other `while` loops
   in the package are bounded or log.)

We could not confirm the cycle with a stack trace (the second run failed loudly instead of hanging); a `py-spy dump` is now taken automatically before
our runner terminates a stalled worker, and we will attach it when the next stall occurs.

## Suggested fix

- In `linear_torsion_check`, distinguish `phi < phi_lim` (near 0°: a connectivity/geometry problem — raise the reset path, `back_transformation=True`, or
  drop the offending torsion) from `phi > up_lim` (a genuine linear bend); only the latter should add LINEAR/COMPLEMENT bends, and only for the bend
  as found, not for its permutations with a terminal vertex.
- In the collinear-segment walk of `add_intcos_from_connectivity`, keep a visited set (or bound the walk by `Natom` reassignments) and raise
  `AlgError` when a LINEAR-bend cycle is detected, so a pathological coordinate set fails in the open instead of spinning.

We are happy to turn this into a pull request with a regression test on this input if the maintainers agree with the reading.

## What we ask

Either a convergence cap with a clear failure in the back-transformation when linear-bend coordinates are introduced mid-optimisation, or a guard that
does not step a complement coordinate by several degrees in one iteration. A `py-spy dump` of the stalled process is attached when the reproduction
delivers one.

---

### Reproduction status (repo-internal, not part of the issue)

- 30 Sep 07:04 (05:04 UTC) started on hel1-23 (`/root/optking_repro/run_repro.sh`, 16 threads, py-spy 0.4 in env `qc`).
- 07:11: worker exited by itself after 50 iterations (no stall, so no py-spy dump); 19 AlgErrors on the ethynyl bend in `worker.log` (back transformation failed, linear bends detected, new linear angles), then the 50-iteration PsiException. The hang is therefore not deterministic on this input; the py-spy dump now waits for the next natural stall (the guard in `run_corpus.py` writes `stall_stack.txt`). Decision for the user: post the issue with the two logs now, or wait for a stack trace.
