# v1.4 on the data, clean arm (no hold-out twin of any charge) — the promotion read (design note §14)

The new models are the carried recipe (c00_control) trained on the whole pool without any hold-out molecule's twin of any charge (--holdout-twins drop-any-charge, TASKS 253: 7 pool molecules left it, P3c_311e979a14, P3c_331729cd47, B_3100da3761, P3c_097651503c, B_07cadc7923, P3c_07cadc7923, P3c_8448043181) (seeds 0, 1, 2; best epochs 144, 120, 186 / 300); the carried version is the frozen list's three checkpoints, read again on the same hold-outs.

## The promotion: hold-out (a) on its eight clean molecules (a8), and hold-out (b)

| hold-out | quantity | v1.4 candidate | carried | difference | beyond 2 SE |
|---|---|---|---|---|---|
| (a8) | ring-ip | 1.55 (1.37–1.77) | 1.77 (1.68–1.95) | -0.22 | no |
| (a8) | CH-stretch | 1.15 (0.92–1.34) | 1.19 (0.91–1.74) | -0.04 | no |
| (a8) | CH-oop | 2.22 (2.10–2.35) | 2.17 (1.99–2.47) | +0.05 | no |
| (a8) | other | 2.91 (2.79–3.10) | 3.62 (3.27–4.09) | -0.71 | yes |
| (a8) | coupling_ratio | 0.147 (0.143–0.150) | 0.184 (0.176–0.193) | -0.037 | yes |
| (b) | ring-ip | 1.64 (1.49–1.89) | 2.12 (2.02–2.23) | -0.48 | yes |
| (b) | CH-stretch | 2.02 (1.55–2.32) | 2.51 (1.91–3.54) | -0.49 | no |
| (b) | CH-oop | 1.72 (1.41–1.96) | 2.70 (2.44–2.95) | -0.98 | yes |
| (b) | other | 3.68 (3.20–4.15) | 3.88 (3.52–4.52) | -0.20 | no |
| (b) | coupling_ratio | 0.170 (0.164–0.177) | 0.263 (0.243–0.281) | -0.093 | yes |

**Promotion: not promoted** — worse on (a8) CH-oop, better on 9 of 10 (the registered rule: §5, decision 57). By §14's addition of 17 November (the clean arm replaces the data arm, whose hold-out (a) was not clean for benzene) nothing is carried, and the cause is looked at per molecule before anything else is decided. This read carries nothing itself and changes no registry entry.

## Beside it, deciding nothing: hold-out (a) on all ten molecules

The eight decide (§14's addition of 16 Nov): the carried version trained on twins of two of the ten (2-naphthoic acid and benzonitrile, TASKS 157), so on the ten the comparison favours it on two molecules it has seen.

| hold-out | quantity | v1.4 candidate | carried | difference | beyond 2 SE |
|---|---|---|---|---|---|
| (a) | ring-ip | 1.46 (1.30–1.66) | 1.66 (1.59–1.82) | -0.20 | no |
| (a) | CH-stretch | 1.12 (0.95–1.25) | 1.15 (0.87–1.62) | -0.03 | no |
| (a) | CH-oop | 2.09 (1.99–2.13) | 1.99 (1.86–2.22) | +0.09 | no |
| (a) | other | 2.76 (2.64–2.95) | 3.35 (3.02–3.79) | -0.59 | yes |
| (a) | coupling_ratio | 0.139 (0.135–0.142) | 0.172 (0.164–0.180) | -0.033 | yes |
| (b) | ring-ip | 1.64 (1.49–1.89) | 2.12 (2.02–2.23) | -0.48 | yes |
| (b) | CH-stretch | 2.02 (1.55–2.32) | 2.51 (1.91–3.54) | -0.49 | no |
| (b) | CH-oop | 1.72 (1.41–1.96) | 2.70 (2.44–2.95) | -0.98 | yes |
| (b) | other | 3.68 (3.20–4.15) | 3.88 (3.52–4.52) | -0.20 | no |
| (b) | coupling_ratio | 0.170 (0.164–0.177) | 0.263 (0.243–0.281) | -0.093 | yes |

On the ten the same rule would read: not promoted, worse on (a) CH-oop, better on 9 of 10.

## What was stated beforehand

Stated before any whole-pool model existed (§12, §14), as corrected ω rms in cm⁻¹, hold-out (a) on its eight clean molecules. They decide nothing; the promotion does.

- hold-out (b) below the carried version on the mean of three seeds: 2.05 against 2.79 — **PASS**
- hold-out (a) not above the carried version on the mean of three seeds: 2.05 against 2.37 — **PASS**
- biphenylene (A_72b86c2331) on hold-out (a) at most 4.7 on the mean of three seeds: the new models 2.04, 2.89, 1.55 (mean 2.16), the carried version 2.24, 2.27, 1.38 (mean 1.96) — **PASS**

Apart from this read, and deciding nothing in it: the licence's quantity — the band error of the seed-mean ΔH (decision 65 as amended on 16 Nov 2026) — is made by `probes/product_error_read.py` and is not in this read.
