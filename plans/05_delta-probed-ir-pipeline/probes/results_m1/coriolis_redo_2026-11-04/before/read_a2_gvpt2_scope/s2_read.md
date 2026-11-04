# S2 read — 14 molecules in 9 scaffolds, excluded 6 — labels GVPT2, scope no-linear-xh

| k (training scaffolds) | (b) rms ± SE | (c) rms ± SE | unseen-family modes |
|---|---|---|---|
| 4 | 7.87 ± 0.03 | 10.13 ± 0.01 | 0 |
| 6 | 7.73 ± 0.01 | 10.11 ± 0.00 | 0 |
| all (8) | 7.68 ± 0.00 | 10.10 ± 0.00 | 0 |

| family | modes | (b) k=4 | (b) k=6 | (b) all | (c) all |
|---|---|---|---|---|---|
| CH-stretch | 0 | nan ± nan | nan ± nan | nan | nan |
| CH-oop | 74 | 5.90 ± 0.09 | 5.82 ± 0.04 | 5.78 | 5.89 |
| ring-ip | 257 | 4.00 ± 0.02 | 3.92 ± 0.01 | 3.90 | 9.50 |
| other | 96 | 14.34 ± 0.07 | 14.10 ± 0.03 | 14.00 | 13.61 |

*8 training scaffolds per held-out scaffold: k ≥ 8 is the full set, so the curve ends at k = 6 → all.*

**line 2 missed, route b still descending but its fitted asymptote is at or above 3.0 cm⁻¹: read as flat — the search (model class × features) first**

- excluded A_8f6ed7c002: NOISY (noise rule)
- excluded B_190a33a33e: NOISY (noise rule)
- excluded B_151c8ce719: NOISY (noise rule)
- excluded B_16194573ac: NOISY (noise rule)
- excluded B_17f1611949: NOISY (noise rule)
- excluded B_0040149ee1: no qff_report.npz (STOPPED or FAILED)
