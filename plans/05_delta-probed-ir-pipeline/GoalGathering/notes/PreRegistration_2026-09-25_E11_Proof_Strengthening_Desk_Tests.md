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
