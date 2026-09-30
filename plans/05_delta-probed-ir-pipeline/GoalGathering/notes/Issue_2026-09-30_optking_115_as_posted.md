## Summary

`psi4.optimize` (psi4 1.11 / optking 0.5.0) hung indefinitely — one core at 100 %, no output for five hours, no exception — on a B3LYP/6-31G* optimisation of 1-ethynyl-naphthalene-8-carboxylic acid. The log ends right after an `AlgError` in which a "bend" with the **terminal ethynyl hydrogen as vertex** (interior angle 0.7°) was reported as a linear bend. Reading the source, the most likely place of the silent loop is the collinear-segment torsion search in `addIntcos.add_intcos_from_connectivity`, which walks along LINEAR bends without a visited set or a bound. A second run of the same input did not hang but failed loudly with 19 `AlgError`s on the same bend and `Could not converge geometry optimization in 50 iterations`.

## Environment

- psi4 1.11, optking 0.5.0, qcelemental 0.51.2 (conda-forge, Linux x86-64, Ubuntu 24.04, 16 threads)
- B3LYP/6-31G*, `scf_type df`, `e_convergence 1e-8`, `d_convergence 1e-8`, DFT grid 75/302, `reference rhf`, `symmetry c1`, `no_reorient`, `no_com`; all optimiser options at their defaults

## Reproducer

Start geometry (RDKit ETKDG + MMFF, Å), SMILES `C#Cc1cccc2cccc(C(=O)O)c12`:

```
0 1
C      2.56326953    -2.35221594    -0.72316320
C      1.47236587    -1.89836199    -0.50583171
C      0.15113558    -1.40482602    -0.23273813
C     -0.86895438    -2.36948045    -0.24719718
C     -2.17830185    -2.01803310     0.04582650
C     -2.47684498    -0.69918318     0.36646176
C     -1.48026255     0.28909084     0.38928968
C     -1.84648032     1.60144711     0.73775625
C     -0.91026152     2.62955372     0.78751668
C      0.41128801     2.36060043     0.47116909
C      0.79260697     1.05933810     0.10623660
C      2.21002444     0.92157512    -0.25353471
O      3.15468906     0.91675863     0.51039185
O      2.34837893     0.91070170    -1.59093694
C     -0.13030105    -0.03267181     0.07193291
H      3.53342135    -2.75228558    -0.90458608
H     -0.63874567    -3.40716872    -0.48191833
H     -2.96258120    -2.77015296     0.03446008
H     -3.50912607    -0.44689979     0.60432542
H     -2.88159408     1.83570576     0.98325445
H     -1.21494978     3.63504321     1.06553226
H      1.14748373     3.16114922     0.49703777
H      3.31373999     0.83031571    -1.73128500
units angstrom
symmetry c1
no_reorient
no_com
```

```python
psi4.set_options({"basis": "6-31G*", "scf_type": "df", "e_convergence": 1e-8, "d_convergence": 1e-8,
                  "dft_radial_points": 75, "dft_spherical_points": 302, "reference": "rhf"})
psi4.optimize("b3lyp", molecule=mol)
```

Run 1 (machine A) hung after the 15th SCF; run 2 (machine B, identical input and thread count) took 50 iterations and failed. Both logs, the full `psi4.out` excerpt and the input are in our public repository:
`https://github.com/thebreadishard/udacity-capstone-plan/tree/master/plans/05_delta-probed-ir-pipeline/probes/results_m1/optking_stall_2026-09-30`
(`hung_hel1-14_worker_stdout.txt`, `repro_hel1-23_worker.log`, `psi4_out_excerpt.txt`, `job.json`).

## What the logs show

Run 1: at step 14 optking replaced the ordinary bend of the ring–C≡C angle (170.5°) by the linear pair `L(3,1,16)` / `l(3,1,16)` (1-based); in the next step the complement `l(3,1,16)` moved −9.41° at once while every other coordinate moved < 0.2°. The SCF after that converged, optking printed the new coordinate values — and the last lines of the optking log are

```
Interior angle of   0.7 for bend B((0, 15, 2)) can't work in good torsion
AlgError: Exception created. Mesg: Could not compute T((0, 15, 2, 3)). Problem computing interior bend.
AlgError: Linear bends detected.
(0, 15, 2)
AlgError: Exception created. Mesg: Tors.q: unable to compute torsion value
AlgError: Linear bends detected.
 L(1,16,3)
 l(1,16,3)
 Caught AlgError exception
```

Atom 15 (0-based) is the terminal ethynyl H. A 0.7° "interior angle" at a terminal atom means the torsion `(0, 15, 2, 3)` runs *through* the hydrogen (atoms 0 and 2 lie on the same side of it, H–C≡C); the "linear bend" `L(1,16,3)` that is then added has that hydrogen as its vertex. After ` Caught AlgError exception` nothing was written for five hours; RSS constant at 3 GB, one core busy. We terminated the process.

Run 2 (`repro_hel1-23_worker.log`): the same coordinate fails in the open — `Back transformation failed. Cartesian Step size too large`, `Could not compute T((3, 2, 0, 15))`, `Could not compute T([0, 15, 2, 3])`, `Could not compute T([0, 15, 2, 14])`, `Tors.q: unable to compute torsion value`, `New linear angles`, 19 `AlgError`s in all, then the 50-iteration `PsiException`.

## Where the code points (0.5.0)

1. `v3d.py`, `linear_torsion_check` (line 246 ff.): `phi_bad = not phi_lim < phi < up_lim` treats an interior angle near 0° like one near 180°, then appends "all combinations to be safe" to `old_bends` (lines 267–282) and the bend to `new_linear_bends`. Near 0° is not a linear bend; it is a torsion through a terminal atom.
2. `optimize.py`, `alg_error_handler` (line 427 ff.), branch `elif error.linear_bends:` adds the LINEAR/COMPLEMENT bends and rebuilds the rest with `frag.add_intcos_from_connectivity(ignore_coords=error.old_bends)` (line 481).
3. `addIntcos.py`, "Search for additional torsions around collinear segments" (line 306 ff.): the walks at lines 325 and 336

   ```python
   J = j; i = 0
   while i < Natom:
       if C[i, J] and i != m:
           b = bend.Bend(i, J, k, bend_type="LINEAR")
           if b in intcos:      # i,J,k is collinear
               J = i; i = 0; continue
   ```
   have no visited set and no bound, and nothing inside them logs. Once the LINEAR bends in `intcos` form a cycle among a few atoms — which the permuted bends of point 1 make possible (`L(1,16,3)` next to `L(3,1,16)` / `L(2,1,16)` in run 1) — `J` is reassigned back and forth forever. That matches the silence at 100 % of one core. The other `while` loops in the package are bounded or log.

We could not confirm this with a stack trace (run 2 failed instead of hanging); our runner now takes a `py-spy dump` before terminating a stalled worker, and we will attach it here when the next stall occurs.

## Suggested fix

- In `linear_torsion_check`, distinguish `phi < phi_lim` (near 0°: a connectivity/geometry problem → the existing reset path, `back_transformation=True`, or drop the torsion) from `phi > up_lim` (a genuine linear bend); only the latter should add LINEAR/COMPLEMENT bends, and only for the bend as found, not for permutations with a terminal vertex.
- In the collinear-segment walk of `add_intcos_from_connectivity`, keep a visited set (or bound the reassignments by `Natom`) and raise `AlgError` on a LINEAR-bend cycle, so an inconsistent coordinate set fails in the open instead of spinning.

We are applying exactly these two changes to our own installation now and will report whether the input then optimises or fails cleanly; if the maintainers agree with the reading we would be glad to open a pull request with a regression test on this input.
