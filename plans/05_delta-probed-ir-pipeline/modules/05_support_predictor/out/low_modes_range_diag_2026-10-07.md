# TASKS 23 step 0 — is 'other-low' a matter of range? Truncating the TRUE correction — 2026-10-07 07:15

Hold-out (a), analytic ωB97X − analytic B3LYP; off-diagonal blocks between atoms farther apart than r zeroed; 'keep' leaves the diagonal blocks, 'sum' re-makes them from the acoustic sum rule. Errors are corrected-ω rms against the untruncated correction (identity check: max |error| at r = ∞ is 1.9e-06 cm⁻¹). The models' column is chain 34's three seeds on the same targets (5 Oct record).

## Pooled (rms, cm⁻¹)

| truncation | ring-ip | CH-stretch | CH-oop | other-low | other-mid |
|---|---|---|---|---|---|
| keep r = 3.0 Å | 2.24 | 0.06 | 2.77 | 2.38 | 1.79 |
| keep r = 4.0 Å | 1.40 | 0.08 | 1.94 | 3.32 | 1.37 |
| keep r = 5.0 Å | 0.62 | 0.02 | 0.26 | 1.95 | 0.21 |
| keep r = 6.0 Å | 0.26 | 0.01 | 0.14 | 0.75 | 0.07 |
| keep r = 8.0 Å | 0.01 | 0.01 | 0.07 | 0.06 | 0.02 |
| keep r = inf Å | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| sum r = 3.0 Å | 2.39 | 1.81 | 3.08 | 3.20 | 2.54 |
| sum r = 4.0 Å | 1.55 | 0.23 | 3.47 | 5.89 | 2.44 |
| sum r = 5.0 Å | 0.82 | 0.05 | 0.72 | 3.40 | 0.45 |
| sum r = 6.0 Å | 0.33 | 0.04 | 0.37 | 0.92 | 0.19 |
| sum r = 8.0 Å | 0.03 | 0.02 | 0.11 | 0.07 | 0.04 |
| sum r = inf Å | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **models (chain 34)** | 1.80 | 1.26 | 2.29 | 3.21 | 2.76 |

## other-low per molecule (cm⁻¹): truncation at 5 Å (keep / sum) and the models

| molecule | atoms | n low modes | keep 5 Å | sum 5 Å | models |
|---|---|---|---|---|---|
| A_fdc27f1bd1 | 22 | 13 | 1.15 | 0.95 | 4.62 |
| A_8448043181 | 12 | 4 | 0.00 | 0.00 | 1.25 |
| A_e72997e726 | 23 | 14 | 0.77 | 0.62 | 3.66 |
| A_541c53d1a5 | 24 | 15 | 0.91 | 3.08 | 1.87 |
| A_428228e5a5 | 26 | 19 | 3.19 | 5.60 | 3.59 |
| A_07cadc7923 | 21 | 15 | 3.64 | 6.45 | 1.52 |
| A_08dde334d8 | 24 | 17 | 1.26 | 0.81 | 3.62 |
| A_3100da3761 | 13 | 8 | 0.90 | 0.57 | 3.74 |
| A_bce5bae234 | 23 | 15 | 0.81 | 1.99 | 1.49 |
| A_72b86c2331 | 20 | 12 | 1.55 | 2.47 | 3.98 |

Spearman ρ (truncation at 5 Å vs the models, other-low, ten molecules): keep 0.24, sum -0.10.

**Reading rule:** other-low cost of the 5 Å truncation 1.95 (keep) / 3.40 (sum) cm⁻¹ → between the lines — range and the torsion environment both go into the design note.
