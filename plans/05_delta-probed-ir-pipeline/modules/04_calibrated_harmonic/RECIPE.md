# Module 04 — the calibrated-harmonic baseline: recipe candidate (written 2026-09-12, before any model was trained)

This note fixes, before the first training run, what the in-house calibrated-harmonic baseline is:
the per-band machine-learning correction to scaled-harmonic DFT that the pipeline must beat
(Capstone_Mapping §M04; proposal §7 row "in-house"; Distilled Q4 exception). The pilot note's item 6
("the M04 baseline recipe: features, tuning budget, seeds", Ladder §4) adopts this note or amends it by
a dated note that names the reason; after the pilot note the baseline is never weakened
(Distilled §"Weakening the M04 baseline after the pilot note").

## Problem

Supervised **regression**. Target per band: **y = ν_lab − ν_scaled**, the error of the PAHdb
scaled-harmonic position (library as served, decision 30) against the laboratory position, in cm⁻¹.
A model that predicts y corrects line A; a perfect model would make the harmonic library exact. The
comparison the plan needs is: does the pipeline's anharmonic correction beat *corrected* harmonic
positions (Distilled, Ethereal-AI row), evaluated with the molecule held out.

## Dataset (the paired theory↔lab band table)

- **Sources, both already parsed by Module 02:** computed bands of the PAHdb theoretical library v4.00
  (`out/theoretical_4.00/bands.csv.gz`, stored = scaled positions, unscaled recovered as stored/scale)
  and the laboratory bands of the PAHdb experimental library v3.10 (`out/experimental_3.10/`, argon
  matrix). Species are joined on the PAHdb `uid` (83 of the 84 experimental entries exist in the
  theoretical library with the same formula and charge; uid 548 does not and is dropped).
- **Join rule (fixed):** matrix bands of one species are taken in descending laboratory intensity; for
  each, the candidates are the computed bands of the same species with intensity ≥ 1 km/mol whose scaled
  position lies within ±30 cm⁻¹ and that are not yet taken; the nearest candidate is paired (one-to-one,
  no second choice); a matrix band without a candidate stays unmatched and is counted.
- **Reading 1 (user decision 2026-09-02, carried):** this paired table is Module 04's dataset and is to be
  published as its own versioned release (Zenodo DOI) **before the module starts**, with a provenance
  paragraph on its distinctness from the Module 02 and 03 datasets (computed library; laboratory
  scoreboard). The release is the student's action; until it exists the table is "pre-release".
- **What the lab side is:** argon-matrix positions, not gas-phase. Module 03 measured the matrix–gas
  offset (+3.3 to +5.9 cm⁻¹ per family against hot vapour, 2026-09-11); the baseline is therefore a
  *matrix-calibrated* harmonic line, and scoring against gas-phase data passes through the Ladder §2
  matrix gate like every other matrix quantity.

## Features (fixed)

Per band: unscaled harmonic frequency; log₁₀ of the computed intensity (km/mol, floored at 10⁻³);
computed relative intensity within the molecule; the scale-factor region as stored (three regions);
the family label by the Module 02 frequency-range rule on the scaled position. Per molecule: carbon
count, hydrogen count, charge, hydrogen-adjacency counts (solo, duo, trio, quartet) from the PAHdb
record, and whether the molecule contains nitrogen. No laboratory quantity is a feature. No symmetry
irrep (labels differ per point group and are not comparable across molecules).

## Models (fixed; scikit-learn)

0. **Zero model** — the library as served (y = 0). This is line A.
1. **Per-family constant** — the mean y of the family in the training fold (the "refit the scale
   factor per family" opponent, the honest simplest calibration).
2. **Ridge regression** on standardised numeric features plus one-hot family and region (α = 1.0).
3. **Gradient-boosted trees** — `HistGradientBoostingRegressor` with library defaults, `random_state = 0`.

**Tuning budget: none.** Hyper-parameters are the library defaults named above; no search. Seed 0
everywhere. The baseline is meant to be strong and *reproducible*, not maximal.

## Evaluation (fixed)

- **Leave-one-molecule-out**: `LeaveOneGroupOut` with the PAHdb uid as the group (83 folds). Bands of
  one molecule never sit on both sides of a split — an instance-level split would leak the molecule's
  own systematic error into its own test score (the leakage Bos et al. 2025's 80/20 instance split does
  not exclude; the SI carries no species identifier, so it cannot be checked there).
- **Metrics:** MAE and RMSE of the corrected position against the lab position (equivalently of the
  residual y − ŷ), R² of ŷ against y, and the share of bands within 5 cm⁻¹ — overall and per family;
  reported for all four models side by side. MAE is the primary metric (the plan's per-band |error|,
  P2).
- **Ladder molecules:** the held-out predictions for naphthalene (330), anthracene (265), pyrene (334),
  tetracene (282), chrysene (291) and coronene (18) are written out as the opponent column (P2), each
  from the fold in which that molecule was held out.
- **Uncertainty layer (P5):** the per-family 68 % and 95 % quantiles of |y − ŷ| over all held-out
  predictions of the chosen model, written out as the empirical per-band uncertainty attached to R4–R6
  reach spectra, labelled an extrapolation from molecules of ≤ 50 carbon atoms.

## Q4 exception (declared, carried)

The baseline trains on laboratory residuals by design. The pipeline itself never does. No
scoreboard value of a ladder molecule is reachable from the fold that predicts that molecule.

## What is not decided here

Which of models 1–3 is *the* baseline column is decided by the pilot note on these leave-one-molecule-
out numbers, with the rule fixed now: the model with the lowest overall held-out MAE, ties to the
simpler model. The margins τ_F are the pilot note's.
