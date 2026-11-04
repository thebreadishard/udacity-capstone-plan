# S2 read — 14 molecules in 9 scaffolds, excluded 6 — labels GVPT2, scope no-large-amplitude

| k (training scaffolds) | (b) rms ± SE | (c) rms ± SE | unseen-family modes |
|---|---|---|---|
| 4 | 4.46 ± 0.03 | 8.12 ± 0.01 | 0 |
| 6 | 4.40 ± 0.01 | 8.10 ± 0.01 | 0 |
| all (8) | 4.37 ± 0.00 | 8.09 ± 0.00 | 0 |

| family | modes | (b) k=4 | (b) k=6 | (b) all | (c) all |
|---|---|---|---|---|---|
| CH-stretch | 0 | nan ± nan | nan ± nan | nan | nan |
| CH-oop | 74 | 5.81 ± 0.08 | 5.73 ± 0.04 | 5.67 | 5.89 |
| ring-ip | 251 | 3.88 ± 0.02 | 3.82 ± 0.01 | 3.81 | 9.38 |
| other | 93 | 4.68 ± 0.05 | 4.62 ± 0.03 | 4.60 | 5.39 |

*8 training scaffolds per held-out scaffold: k ≥ 8 is the full set, so the curve ends at k = 6 → all.*

**line 2 missed, route b still descending but its fitted asymptote is at or above 3.0 cm⁻¹: read as flat — the search (model class × features) first**

- excluded A_8f6ed7c002: NOISY (noise rule)
- excluded B_190a33a33e: NOISY (noise rule)
- excluded B_151c8ce719: NOISY (noise rule)
- excluded B_16194573ac: NOISY (noise rule)
- excluded B_17f1611949: NOISY (noise rule)
- excluded B_0040149ee1: no qff_report.npz (STOPPED or FAILED)
