# v1.4 on the data — the promotion read (design note §14)

The new models are the carried recipe (c00_control) trained on the whole pool (seeds 0, 1, 2; best epochs 173, 142, 169 / 300); the carried version is the frozen list's three checkpoints, read again on the same hold-outs.

## The promotion: hold-out (a) on its eight clean molecules (a8), and hold-out (b)

| hold-out | quantity | v1.4 candidate | carried | difference | beyond 2 SE |
|---|---|---|---|---|---|
| (a8) | ring-ip | 1.52 (1.37–1.75) | 1.77 (1.68–1.95) | -0.25 | no |
| (a8) | CH-stretch | 1.21 (1.05–1.34) | 1.19 (0.91–1.74) | +0.03 | no |
| (a8) | CH-oop | 2.43 (1.66–3.42) | 2.17 (1.99–2.47) | +0.26 | no |
| (a8) | other | 2.83 (2.74–2.88) | 3.62 (3.27–4.09) | -0.80 | yes |
| (a8) | coupling_ratio | 0.146 (0.140–0.157) | 0.184 (0.176–0.193) | -0.038 | yes |
| (b) | ring-ip | 1.61 (1.47–1.89) | 2.12 (2.02–2.23) | -0.50 | yes |
| (b) | CH-stretch | 2.35 (2.15–2.58) | 2.51 (1.91–3.54) | -0.16 | no |
| (b) | CH-oop | 1.67 (1.51–1.85) | 2.70 (2.44–2.95) | -1.04 | yes |
| (b) | other | 2.96 (2.75–3.19) | 3.88 (3.52–4.52) | -0.92 | yes |
| (b) | coupling_ratio | 0.169 (0.158–0.180) | 0.263 (0.243–0.281) | -0.094 | yes |

**Promotion: not promoted** — worse on (a8) CH-stretch, (a8) CH-oop, better on 8 of 10 (the registered rule: §5, decision 57). By §14 nothing is carried, and the cause is looked at per molecule before anything else is decided. This read carries nothing itself and changes no registry entry.

## Beside it, deciding nothing: hold-out (a) on all ten molecules

The eight decide (§14's addition of 16 Nov): the carried version trained on twins of two of the ten (2-naphthoic acid and benzonitrile, TASKS 157), so on the ten the comparison favours it on two molecules it has seen.

| hold-out | quantity | v1.4 candidate | carried | difference | beyond 2 SE |
|---|---|---|---|---|---|
| (a) | ring-ip | 1.43 (1.29–1.64) | 1.66 (1.59–1.82) | -0.23 | no |
| (a) | CH-stretch | 1.16 (1.01–1.31) | 1.15 (0.87–1.62) | +0.01 | no |
| (a) | CH-oop | 2.21 (1.63–3.02) | 1.99 (1.86–2.22) | +0.22 | no |
| (a) | other | 2.64 (2.58–2.69) | 3.35 (3.02–3.79) | -0.71 | yes |
| (a) | coupling_ratio | 0.138 (0.132–0.148) | 0.172 (0.164–0.180) | -0.034 | yes |
| (b) | ring-ip | 1.61 (1.47–1.89) | 2.12 (2.02–2.23) | -0.50 | yes |
| (b) | CH-stretch | 2.35 (2.15–2.58) | 2.51 (1.91–3.54) | -0.16 | no |
| (b) | CH-oop | 1.67 (1.51–1.85) | 2.70 (2.44–2.95) | -1.04 | yes |
| (b) | other | 2.96 (2.75–3.19) | 3.88 (3.52–4.52) | -0.92 | yes |
| (b) | coupling_ratio | 0.169 (0.158–0.180) | 0.263 (0.243–0.281) | -0.094 | yes |

On the ten the same rule would read: not promoted, worse on (a) CH-stretch, (a) CH-oop, better on 8 of 10.

## What was stated beforehand

Stated before any whole-pool model existed (§12, §14), as corrected ω rms in cm⁻¹, hold-out (a) on its eight clean molecules. They decide nothing; the promotion does.

- hold-out (b) below the carried version on the mean of three seeds: 2.10 against 2.79 — **PASS**
- hold-out (a) not above the carried version on the mean of three seeds: 2.02 against 2.37 — **PASS**
- biphenylene (A_72b86c2331) on hold-out (a) at most 4.7 on the mean of three seeds: the new models 1.73, 3.29, 1.48 (mean 2.17), the carried version 2.24, 2.27, 1.38 (mean 1.96) — **PASS**

Apart from this read, and deciding nothing in it: the licence's quantity — the band error of the seed-mean ΔH (decision 65 as amended on 16 Nov 2026) — is made by `probes/product_error_read.py` and is not in this read.
