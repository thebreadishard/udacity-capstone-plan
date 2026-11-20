# The low-mode repair's change of a label mode, against frequency and force constant (TASKS 218)

**Exploratory read; it decides nothing.** These are the by-product points of the repairs of 13 and 15 November, and they were looked at before this read was written. Every molecule here was selected for a label mode below 20 cm⁻¹, so the sample is biased, and it holds no B3LYP mode between 20 and 60 cm⁻¹.

128 points (re-measured label mode × functional) on 60 molecules; 11 flagged for a coverage or overlap below 0.9 and 0 for two steps more than 0.15 cm⁻¹ apart (0 points have a step check; 0 check point(s) set aside for their own overlap); flagged points are in points.csv and in no statistic. A molecule is 'biased' when a label mode of it lies below 20 cm⁻¹, which is why the repair selected it. 1 point(s) turned imaginary under the patch. 'Noise' is the frequency noise the finite difference makes of 1e-07 hartree/bohr of gradient noise on that mode (see `noise_sensitivity_cm`); the gradient noise itself is not measured here.

## b3lyp, unbiased sample: 0 unflagged points in 20–100 cm⁻¹

| label frequency (cm⁻¹) | n | median abs Δ (cm⁻¹) | max abs Δ | > 0.5 | fraction | 1 SE | median noise per 1e-07 |
|---|---|---|---|---|---|---|---|
| 20–30 | 0 | undefined | undefined | 0 | undefined | undefined | undefined |
| 30–40 | 0 | undefined | undefined | 0 | undefined | undefined | undefined |
| 40–50 | 0 | undefined | undefined | 0 | undefined | undefined | undefined |
| 50–60 | 0 | undefined | undefined | 0 | undefined | undefined | undefined |
| 60–80 | 0 | undefined | undefined | 0 | undefined | undefined | undefined |
| 80–100 | 0 | undefined | undefined | 0 | undefined | undefined | undefined |

Force-constant quartiles: fewer than four points, no split.

Spearman of abs Δ against the label frequency: undefined (n = 0); against log k: undefined (n = 0). Frequency against log k on the same points: undefined; as far as these two are one ordering the points cannot tell a frequency trigger from a force-constant trigger, and the read names none. Rms of the signed change: undefined cm⁻¹.

The rule's arithmetic on this group's points in 20–60 cm⁻¹ (the registered population; its outcome is in the section below): n = 0, 0 moved more than 0.5 cm⁻¹: fewer than the 16 points the rule needs, so it reads nothing from them. Outcome 3: undecided.

## wb97x, biased sample: 52 unflagged points in 20–100 cm⁻¹

| label frequency (cm⁻¹) | n | median abs Δ (cm⁻¹) | max abs Δ | > 0.5 | fraction | 1 SE | median noise per 1e-07 |
|---|---|---|---|---|---|---|---|
| 20–30 | 1 | 2.81 | 2.81 | 1 | 1.00 | 0.00 | 0.19 |
| 30–40 | 1 | 1.67 | 1.67 | 1 | 1.00 | 0.00 | 0.14 |
| 40–50 | 4 | 2.51 | 4.01 | 3 | 0.75 | 0.22 | 0.38 |
| 50–60 | 35 | 0.70 | 4.43 | 24 | 0.69 | 0.08 | 0.06 |
| 60–80 | 11 | 0.89 | 6.72 | 9 | 0.82 | 0.12 | 0.08 |
| 80–100 | 0 | undefined | undefined | 0 | undefined | undefined | undefined |

| force constant quartile (hartree/bohr²) | n | median abs Δ (cm⁻¹) | max abs Δ | > 0.5 | fraction | 1 SE | median noise per 1e-07 |
|---|---|---|---|---|---|---|---|
| Q1: 1.68e-04 to 9.59e-04 | 13 | 2.76 | 6.72 | 11 | 0.85 | 0.10 | 0.19 |
| Q2: 1.00e-03 to 1.39e-03 | 13 | 0.54 | 2.60 | 9 | 0.69 | 0.13 | 0.06 |
| Q3: 1.39e-03 to 1.63e-03 | 13 | 0.71 | 1.61 | 8 | 0.62 | 0.13 | 0.06 |
| Q4: 1.64e-03 to 2.81e-03 | 13 | 0.89 | 1.67 | 10 | 0.77 | 0.12 | 0.05 |

Spearman of abs Δ against the label frequency: -0.26 (n = 52); against log k: -0.29 (n = 52). Frequency against log k on the same points: +0.56; as far as these two are one ordering the points cannot tell a frequency trigger from a force-constant trigger, and the read names none. Rms of the signed change: 1.81 cm⁻¹.

The rule's arithmetic on this group's points in 20–60 cm⁻¹ (description only): n = 41, 29 moved more than 0.5 cm⁻¹: p = 0.71, 1 SE = 0.07. p ≥ 0.50 and p − 1 SE = 0.64 ≥ 0.40. Outcome 2, for this group's molecules: a majority of the labels of their modes in this window stand more than 0.5 cm⁻¹ from the patched value. That says label and patch disagree, not why: the missing grid-weight derivative is one cause, the labels' older CPHF another, and the finite difference corrects both.

## The registered decision rule

Population: b3lyp, unbiased sample, label frequency 20–60 cm⁻¹, unflagged. n = 0, 0 moved more than 0.5 cm⁻¹: fewer than the 16 points the rule needs, so it reads nothing from them. Outcome 3: undecided.

Flagged points in the window: 0. Counted as moved: 0 of 0, outcome undecided; counted as unmoved: 0 of 0, outcome undecided. The registered fraction stays the one on unflagged points.

What orders the moves (descriptive): Spearman of abs Δ against the label frequency: undefined (n = 0); against log k: undefined (n = 0). Frequency against log k on the same points: undefined; as far as these two are one ordering the points cannot tell a frequency trigger from a force-constant trigger, and the read names none.

| registered point | label (cm⁻¹) | patched | Δ | noise per 1e-07 hartree/bohr | other step − this | flags |
|---|---|---|---|---|---|---|

## Flagged points

- A2_29caedd47d wb97x mode 0: label 72.59 → 71.77 cm⁻¹, coverage 0.71, overlap after the patch 1.00, flags overlap
- B_00bee51dac wb97x mode 2: label 60.92 → 61.42 cm⁻¹, coverage 0.68, overlap after the patch 1.00, flags overlap
- B_0e479d2c02 b3lyp mode 0: label 13.00 → 10.98 cm⁻¹, coverage 1.00, overlap after the patch 0.53, flags overlap
- B_0e479d2c02 b3lyp mode 1: label 16.68 → 17.54 cm⁻¹, coverage 1.00, overlap after the patch 0.53, flags overlap
- B_0f33d4114d wb97x mode 0: label 70.88 → 72.81 cm⁻¹, coverage 0.73, overlap after the patch 1.00, flags overlap
- B_1a0c9dbf4c wb97x mode 0: label 58.09 → 59.19 cm⁻¹, coverage 0.87, overlap after the patch 0.91, flags overlap
- B_1f4e104c2d wb97x mode 0: label 88.43 → 88.83 cm⁻¹, coverage 0.88, overlap after the patch 1.00, flags overlap
- B_333dfff155 wb97x mode 0: label 68.39 → 68.61 cm⁻¹, coverage 0.81, overlap after the patch 1.00, flags overlap
- B_53ecda5a90 b3lyp mode 0: label 15.36 → 13.84 cm⁻¹, coverage 1.00, overlap after the patch 0.63, flags overlap
- B_53ecda5a90 b3lyp mode 1: label 18.92 → 15.12 cm⁻¹, coverage 1.00, overlap after the patch 0.63, flags overlap
- P3_082a4af67e wb97x mode 1: label 57.66 → 59.08 cm⁻¹, coverage 0.83, overlap after the patch 0.99, flags overlap
