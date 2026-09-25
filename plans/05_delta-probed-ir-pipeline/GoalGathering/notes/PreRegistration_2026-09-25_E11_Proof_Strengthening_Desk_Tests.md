# Pre-registration 2026-09-25, 08:5x — E11: seven desk tests that sharpen the proof that the network learns (the user: "Doe alles maar")

**Why.** The proof-of-learning pre-registration of this morning fixes *the* learning curve (layer B). Independently of compute, seven cheaper
tests say whether what the pair model learns is the physics of the correction and not an artefact of the read-out, the split or the data
size. All run on files that exist (the 229-molecule release and the E7 machinery); the retrainings are minutes on the CCX53's free threads.
Model, features, seeds and read-outs are E7 rung B's unless stated (`m05/e7_rungB_pairs.py`).

## E11.1 Shuffled labels (the control that the read-out measures learning)

Train the pair model exactly as in E7 rung B (E6 hold-outs, full pool) with the **target vectors permuted between molecules of the pool**
(molecule i receives molecule π(i)'s ΔF entries where the pair lists have equal length, otherwise a random draw from the pool's pair pool of
the same pair class; seed 0 for π). **Reading:** the shuffled model's ring coupling ratio must be ≥ 0.9 on both hold-outs and its corrected-
frequency RMS no better than the zero rule by more than 10 %; if the shuffled model "learns" (ratio < 0.8), the read-out is not measuring
learning and every curve of E6/E7 is re-read.

## E11.2 Symmetry consistency (learned physics, not memorised data)

For every hold-out molecule, group the pattern pairs into symmetry classes by RDKit's canonical atom ranks (`CanonicalRankAtoms`, breakTies
False): two primitives are equivalent when their atom tuples have the same rank tuple (up to reversal); two pairs are equivalent when their
primitives are equivalent pairwise. Nothing of this is in the features. **Read-out:** the RMS spread of the model's prediction within a class
divided by the RMS of the predictions over all classed pairs (per molecule, pooled). **Reading:** ≤ 0.10 → the model respects symmetry it was
never told; > 0.30 → it does not, and the equivariant model is not optional; between → reported.

## E11.3 The learned pair terms against chemistry (descriptive, not judged)

For benzene (a training molecule) and naphthalene: the model's predicted ΔF for the ring C–C bond–bond pairs at ring-path distance 1, 2, 3
(ortho, meta, para) against the data's minimum-norm ΔF for the same pairs, and, for orientation, the sign pattern of the *full* B3LYP force
field's interaction constants F_ij for the same pairs (the Kekulé pattern of Pulay's SQM literature: ortho positive, meta negative, para positive,
which is a statement about F, not ΔF — the comparison is printed for the reader, not scored).

## E11.4 The label noise floor (the number the proof standard refers to)

On the molecules that carry both the finite-difference deck-v1 Hessians and the analytic second-route Hessians (23 on 25 September): per
functional, the RMS over vibrational modes of the frequency difference FD − analytic, and the RMS difference of the mode-basis K diagonal
(the correction's diagonal) between the two routes. **Read-out:** two numbers per functional and one for K; **use:** the plateau bound of the
proof-of-learning pre-registration ("no higher than three times the second-route noise") is this K number × 3.

## E11.5 Power-law prediction of the layer-B curve (fixed before the 300-table)

Fit log(ring coupling ratio) and log(corrected-frequency RMS) against log(n) on the existing points (E7 rung B: 45, 100, 175 on hold-outs a and
b; the size split: 45, 100, 161 on the size hold-out) by least squares with a seed bootstrap; **predict** the values at 300, 600 and 1,200 with
a 68 % band. **Use:** the layer-B tables are read against these predictions as well as against the bars; a table below the band is better than
expected, above it worse. (Not a pass/fail; the pass/fail lives in the proof-of-learning pre-registration.)

## E11.6 Error growth with molecule size (the additivity argument, checked)

If ΔH is a sum of local blocks with independent errors, the corrected-frequency RMS per molecule grows with √N_atoms at most; if the errors are
correlated across the molecule, linearly. **Read-out:** on the size-split run's per-molecule errors (hold-out > 26 atoms and the pool's own
cross-validation is not needed: the hold-out spans 27–34 atoms, the control ≤ 26), the slope of log(RMS per molecule) against log(N_atoms).
**Reading:** slope ≤ 0.6 → consistent with additive local blocks (good for large PAHs); ≥ 0.9 → correlated errors, extrapolation to large PAHs will
be hard; between → reported.

## E11.7 Where the bare-parent error sits (diagnostic)

On hold-out (a) of E7 rung B (the layer-A parents) at the full pool: the prediction error per pair class (diagonal bond / angle / dihedral /
other; off-diagonal bond–bond / other) and per ring-path distance, against the same breakdown on hold-out (b). **Read-out:** which classes carry
the gap; **use:** decides whether layer B (small, many substituents) or bare cores (few, large) fill it — a data-collection decision, not a verdict.

**Cost.** E11.4–E11.6 seconds to a minute on the laptop (existing files); E11.1–E11.3 and E11.7 three retrainings of ≈ 2–5 min each on the CCX53
(`--shuffle-labels`, `--dump`, the symmetry and class breakdowns added to the rung-B script under flags, defaults unchanged so E7's numbers stand).
Outputs `modules/05_support_predictor/out/E11_*_2026-09-25.{json,md}`; outcomes appended below, dated.

## Outcomes — 25 September 2026, 08:5x (E11.4 and E11.5; the retrainings E11.1–3, 6, 7 follow)

**E11.4 noise floor** (`out/E11_noise_floor_2026-09-25.md`, 23 molecules with both routes). The set is *biased*: these molecules were computed
along the second route because they were flagged (imaginary modes, screen suspects, benzene's artefact), so the pooled RMS is the flagged set's
number, not the corpus floor — pooled K-diagonal RMS 9.17 cm⁻¹ (benzene alone 30.1, max 148; the four healed ωB97X flips 21–13), B3LYP frequencies
1.99, ωB97X 24.2. The **median per molecule** is the fair estimate of a typical label's noise: B3LYP frequencies 0.51 cm⁻¹, ωB97X 2.07, **K diagonal
2.09 cm⁻¹**, with the unflagged tail of the set at 1.1–1.4. Choice, recorded now: the plateau bound of the proof-of-learning pre-registration uses
the median → **3 × 2.09 ≈ 6.3 cm⁻¹**; the release already replaces the worst rows by analytic Hessians, so the training labels sit at or below this.

**E11.5 power-law predictions** (`out/E11_power_law_2026-09-25.md`, fixed before any layer-B table), factor per decade of data on the ring
coupling ratio / corrected-frequency RMS, and the extrapolation to 1,200 training molecules:

| curve | factor per decade (ratio / RMS) | predicted at 1,200 (ratio; RMS cm⁻¹) |
|---|---|---|
| E7 hold-out (a) bare parents | 1.01× / 1.12× | 0.81 [0.80, 0.81]; 8.5 [8.4, 8.6] |
| E7 hold-out (b) unseen scaffolds | 1.15× / 1.30× | 0.42 [0.41, 0.44]; 4.1 [3.8, 4.4] |
| size split: > 26 atoms | 1.22× / 1.29× | 0.49 [0.47, 0.51]; 4.6 [4.4, 4.8] |
| size-split control: ≤ 26 scaffolds | 1.16× / 1.55× | 0.32 [0.31, 0.34]; 3.0 [2.8, 3.4] |

Reading: **if nothing changes but the amount of the same kind of data, the layer-B curve is predicted to fail the proof standard on the bare
parents** (1.01× per decade against the registered ≥ 1.5×) and to pass it only on the within-size control's RMS. That is the honest prediction to
put beside the tables when they arrive: a pass on (a) would mean layer B's small heteroaromatic molecules teach the bare cores something the
A2 set did not — a real finding; a fail would confirm this extrapolation and point at the model (equivariant) or the data kind (bare cores in the
pool), not at more of the same. The prediction is on record before the 300-table exists.

### Correction and further outcomes, 09:0x

*Correction 09:0x (25 September):* the bare-parent numbers quoted this morning (ratio 0.82 → 0.82 → 0.81, corrected RMS 10.0 → 9.5 → 9.3) are the 23 September run with benzene's corrupted finite-difference target; with the second-route target (E7 rung B `--use-analytic`, recorded in the ledger of 23 September 12:5x) hold-out (a) reads **0.47 → 0.45 → 0.43** and **5.9 → 5.1 → 4.7 cm⁻¹** at 45 → 100 → 175 — learning, not flat. The couplings of the bare parents are learned at the same level as the unseen scaffolds; what remains short is the slope (1.14× per decade on the ratio, 1.49× on the RMS, against the registered 1.5×).

**E11.5, refitted on the corrected-target curve** (`out/E11_power_law_2026-09-25b_analytic.md`): bare parents 1.14× per decade on the ratio, 1.49× on the RMS (predicted at 1,200: 0.39 [0.38, 0.40]; 3.4 [3.2, 3.5] cm⁻¹); unseen scaffolds unchanged (1.15× / 1.30×). The prediction to read the layer-B tables against is this one; the table of 08:5x above is withdrawn for hold-out (a).

**E11.2 symmetry consistency** (`out/E11_rungB_dump_2026-09-25_dump.md`, seed-0 model at the full pool, 43 hold-out molecules with symmetry classes): pooled spread ratio **0.52** (median per molecule 0.60) — far above the 0.30 line. Reading, as registered: the pair model does **not** respect the molecular symmetry it was never told; the equivariant model of the 23 September decision is not optional. This is the strongest ML-side finding of the day: the current model reaches its numbers by fitting, not by having found the symmetry of the physics.

**E11.6 on the E6 split** (a first look; the registered read-out is the size split's dump, to follow): hold-out (a) slope −0.05 over 12–26 atoms (n = 10), hold-out (b) 1.86 over 23–30 atoms (n = 39, two cores — confounded by core identity, not a size effect).

### E11.7 and E11.3 read, 09:0x (`out/E11_rungB_dump_2026-09-25_dump.md`, seed-0 model, full pool of 175, corrected targets)

**E11.7 — where the error sits** (RMS prediction error / RMS of the true ΔF entries per pair class):

| class | hold-out (a) bare parents | hold-out (b) unseen scaffolds |
|---|---|---|
| diagonal, bonds | 0.11 | 0.15 |
| diagonal, angles | 0.33 | 0.42 |
| diagonal, dihedrals | 0.31 | 0.34 |
| off-diagonal, ring bond–bond | 0.20 | 0.33 |
| off-diagonal, other (pairs sharing an atom) | 0.48 | 0.69 |

Reading: with the corrected targets the bare parents are learned *at least as well* as the unseen scaffolds in every class; the weakest class on both
is the off-diagonal "other" pairs (bond–angle and angle–angle terms sharing an atom), which are also the most numerous. Diagonal bond terms are
essentially learned (0.11–0.15). So the gap is not "bare cores are different"; it is the same class everywhere — a model question (the equivariant
model treats those couplings as tensors, the pair MLP as independent scalars), consistent with E11.2's symmetry finding.

**E11.3 — the ring bond–bond terms of benzene** (a training molecule; mean internal ΔF in hartree/bohr², data vs prediction, with the full B3LYP F for orientation):
ortho +0.0048 (pred +0.0057; F +0.035), meta −0.0064 (pred −0.0072; F −0.017), para +0.0065 (pred +0.0066; F +0.046). The correction's ring
interaction pattern is Kekulé-like (+, −, +), the same sign pattern as the force field itself, and the model reproduces it to within 20 %. Descriptive,
as registered; naphthalene was not in the hold-outs of this run and is read from the size-split dump if present.

### E11.1, E11.2 (size split) and E11.6 read, 09:1x

**E11.1 shuffled labels** (`out/E11_shuffled_2026-09-25.md`, full pool, three seeds, targets permuted within pair class across the pool): ring coupling
ratio **1.12** on hold-out (a) and **1.09** on (b) — ≥ 0.9 as required: a model trained on shuffled couplings does not learn couplings, so the
coupling read-out of E6/E7 measures learning. Corrected-frequency RMS **13.6 / 12.5 cm⁻¹** against the zero rule's 23.3 / 23.1 — *better* than the
registered "no more than 10 %" allowance. Reading, honestly: shuffling within pair class keeps each class's mean, and the diagonal terms have
strong class means (every C–H stretch bond correction is negative and of similar size), so a model that learns only the class means already
halves the corrected-frequency error. The corrected-frequency read-out therefore has a **class-mean floor of ≈ 13 cm⁻¹** for this model form; the
learned models' 4.7–5.2 cm⁻¹ sit far below it, which is the real gain, but any future claim on that read-out is against 13, not 23. The
registered RMS condition was mis-set (it did not anticipate class means); the coupling condition — the one the E6/E7 verdicts rest on — is met.

**E11.2 on the size split** (`out/E11_size26_dump_2026-09-25_dump.md`, 54 molecules): pooled symmetry spread ratio **0.52**, median 0.59 — the same as
on the E6 split. Two independent hold-outs agree: the pair MLP does not respect molecular symmetry.

**E11.6 error growth with size** (registered read-out, the size split's dump): on the 45 hold-out molecules of 27–30 atoms the slope of
log(RMS per molecule) against log(N_atoms) is **0.06**; on the 18 control molecules of 23–26 atoms 0.67. Reading: ≤ 0.6 on the registered hold-out
→ consistent with additive local blocks; the range is narrow (27–30 atoms — the admitted A2 molecules above 26 stop at 30), so this is a first
point, not a law. Layer B's hold-out (c) will span 27–34 against training at ≤ 26.

**Tally of E11 (seven tests):** 1 coupling read-out validated, RMS read-out recalibrated (floor 13); 2 symmetry not respected (0.52, twice) — the
equivariant model is required; 3 Kekulé pattern reproduced on benzene; 4 noise floor 2.1 cm⁻¹ median, plateau bound 6.3; 5 corrected-target
predictions on record (bare parents 1.14× / 1.49× per decade); 6 error grows sub-linearly with size at this range (0.06); 7 the weakest class is
the off-diagonal atom-sharing pairs on every hold-out, bare parents included.

### Amendment 09:4x — E11.2 as registered was not a valid test; its reading is withdrawn; re-registered with pair orbits

**What was wrong.** The registered class key (`pair_symmetry_key`: primitive type plus the canonical atom-rank tuples of each member) puts every bond–bond pair of
the same rank types into one class whatever the two primitives' relative position — benzene's ortho, meta and para bond pairs share a class (28 classes for 978
pairs, where the same-parity pairs form 56 true orbits). The within-class spread therefore measured real physical differences, not asymmetry. The control that
should have been run before reading — the same statistic on the **target** — gives pooled **0.575** (median 0.641; `out/E11_target_symmetry_2026-09-25.json`),
equal to the model's molecule by molecule (benzene 0.750 vs 0.764, biphenyl 0.397 vs 0.396, fluorene 0.294 vs 0.306). **Withdrawn:** the 0.52 reading of 09:0x
and 09:1x above, and the sentence "the pair MLP does not respect molecular symmetry"; nothing is known from E11.2 in either direction.

**Re-registration (before the rerun).** Pair orbits are the orbits of primitive pairs under the graph automorphisms of the hydrogen-explicit molecule (RDKit
self-matches), restricted to same-parity pairs (both sign-even: distance/angle; or both sign-odd: dihedral/out-of-plane), so that an improper operation cannot
flip the sign of a matrix element (`e11_extras.orbit_groups`, `spread_of`). Validation on the target, desk (`out/E11_target_orbit_symmetry_2026-09-25.json`,
44 hold-out molecules): within-orbit spread ratio benzene **0.026**, rigid planar parents 0.07–0.14, fluorene+Cl/F/SH/NO₂ 0.01–0.02; larger where the 3D
geometry has less symmetry than the graph (rotors: CF₃ 0.6, benzophenone 0.5) or where the linear-angle primitives of −C≡N / ethynyl come in perpendicular pairs
the key cannot tell apart (0.6–0.7). Statistics, seed-0 model at the full pool, pooled over the molecules whose *target* within-orbit ratio is below 0.15 ("rigid"):
(i) within-orbit spread ratio of the predictions; (ii) the same for the target (the floor); (iii) the antisymmetric fraction of the error, within-orbit RMS of
(pred − true) over its RMS. Reading: (i) ≤ 0.10 and ≤ 2 × (ii) → the model is as symmetric as its target; (i) ≥ 0.30 → it is not; between → reported with (iii).

**Prediction, and why the test cannot say what it was meant to say.** The pair features are invariant scalars — sums and absolute differences of per-primitive
features, F_low entries, ring distances, shared-atom counts — so two mirror-image pairs present the model with identical inputs up to the geometry's own
numerical asymmetry. Prediction: (i) ≈ (ii). Symmetry is *built into* this model by its features; E11.2 could never have distinguished "learned" from "built in",
and a value of (i) clearly above (ii) would point at a non-invariant feature (an ordering artefact), a bug to find rather than a physics finding. The equivariant
model keeps its design reasons (a Cartesian ΔH is a tensor and needs direction-carrying messages; the pair model's invariance is the right symmetry only for
scalar internal-coordinate targets) but loses the argument E11.2 was said to give it.

**Run.** `m05/e7_rungB_pairs.py corpus/molecules out/E11_orbit_dump_2026-09-25 --use-analytic --dump --sizes all --seeds 0 --threads 4` on the CCX53 beside
naphthalene E8 (as this morning's E11 runs), smoke first through the launch wrapper; the dump now also writes every hold-out molecule's per-pair predictions,
targets and pair classes (`_pairs.npz`) so later desk tests of this kind need no retraining. Cost: one training at the full pool (≈ 1 min) plus the read-outs.
