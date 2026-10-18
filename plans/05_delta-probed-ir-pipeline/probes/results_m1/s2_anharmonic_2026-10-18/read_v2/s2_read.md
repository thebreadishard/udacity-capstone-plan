# S2 read — 14 molecules in 9 scaffolds, excluded 6

| k (training scaffolds) | (b) rms ± SE | (c) rms ± SE | unseen-family modes |
|---|---|---|---|
| 4 | 9.86 ± 0.02 | 11.98 ± 0.01 | 0 |
| 6 | 9.77 ± 0.01 | 11.98 ± 0.00 | 0 |
| all (8) | 9.72 ± 0.00 | 11.96 ± 0.00 | 0 |

| family | modes | (b) k=4 | (b) k=6 | (b) all | (c) all |
|---|---|---|---|---|---|
| CH-stretch | 0 | nan ± nan | nan ± nan | nan | nan |
| CH-oop | 74 | 5.81 ± 0.08 | 5.73 ± 0.04 | 5.67 | 5.92 |
| ring-ip | 257 | 3.32 ± 0.03 | 3.20 ± 0.02 | 3.15 | 8.77 |
| other | 101 | 19.04 ± 0.04 | 18.93 ± 0.01 | 18.85 | 19.76 |

*8 training scaffolds per held-out scaffold: k ≥ 8 is the full set, so the curve ends at k = 6 → all.*

**line 2 missed, route b still descending but its fitted asymptote is at or above 3.0 cm⁻¹: read as flat — the search (model class × features) first**
(b) misses line 1 but descends faster than (c): not stopped, repeated after the search

- excluded A_8f6ed7c002: NOISY (noise rule)
- excluded B_190a33a33e: NOISY (noise rule)
- excluded B_151c8ce719: NOISY (noise rule)
- excluded B_16194573ac: NOISY (noise rule)
- excluded B_17f1611949: NOISY (noise rule)
- excluded B_0040149ee1: no qff_report.npz (STOPPED or FAILED)
