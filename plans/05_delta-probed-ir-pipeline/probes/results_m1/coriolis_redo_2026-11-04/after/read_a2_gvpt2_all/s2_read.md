# S2 read — 14 molecules in 9 scaffolds, excluded 6 — labels GVPT2, scope all

| k (training scaffolds) | (b) rms ± SE | (c) rms ± SE | unseen-family modes |
|---|---|---|---|
| 4 | 10.15 ± 0.03 | 12.39 ± 0.01 | 0 |
| 6 | 10.06 ± 0.01 | 12.38 ± 0.00 | 0 |
| all (8) | 10.01 ± 0.00 | 12.36 ± 0.00 | 0 |

| family | modes | (b) k=4 | (b) k=6 | (b) all | (c) all |
|---|---|---|---|---|---|
| CH-stretch | 0 | nan ± nan | nan ± nan | nan | nan |
| CH-oop | 74 | 5.79 ± 0.08 | 5.70 ± 0.04 | 5.65 | 5.89 |
| ring-ip | 257 | 4.22 ± 0.03 | 4.11 ± 0.02 | 4.06 | 9.50 |
| other | 101 | 19.26 ± 0.05 | 19.13 ± 0.02 | 19.06 | 19.97 |

*8 training scaffolds per held-out scaffold: k ≥ 8 is the full set, so the curve ends at k = 6 → all.*

**line 2 missed, route b still descending but its fitted asymptote is at or above 3.0 cm⁻¹: read as flat — the search (model class × features) first**
(b) misses line 1 but descends faster than (c): not stopped, repeated after the search

- excluded A_8f6ed7c002: NOISY (noise rule)
- excluded B_190a33a33e: NOISY (noise rule)
- excluded B_151c8ce719: NOISY (noise rule)
- excluded B_16194573ac: NOISY (noise rule)
- excluded B_17f1611949: NOISY (noise rule)
- excluded B_0040149ee1: no qff_report.npz (STOPPED or FAILED)
