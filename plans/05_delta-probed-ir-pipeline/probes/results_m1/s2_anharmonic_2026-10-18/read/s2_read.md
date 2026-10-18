# S2 read — 14 molecules in 9 scaffolds, excluded 6

| k (training scaffolds) | (b) rms ± SE | (c) rms ± SE | unseen-family modes |
|---|---|---|---|
| 4 | 9.86 ± 0.02 | 11.98 ± 0.01 | 0 |
| 6 | 9.77 ± 0.01 | 11.98 ± 0.00 | 0 |
| 8 | 9.72 ± 0.00 | 11.96 ± 0.00 | 0 |
| 10 | 9.72 ± 0.00 | 11.96 ± 0.00 | 0 |
| all (8) | 9.72 ± 0.00 | 11.96 ± 0.00 | 0 |

| family | modes | (b) | (c) |
|---|---|---|---|
| CH-stretch | 0 | nan | nan |
| CH-oop | 74 | 5.67 | 5.92 |
| ring-ip | 257 | 3.15 | 8.77 |
| other | 101 | 18.85 | 19.76 |

*Only 8 training scaffolds per held-out scaffold: the curve's k ≥ 8 rows equal 'all', and 'still learning' cannot be read as registered.*

**line 2 missed, route b still learning: not failed — data-limited; next S2b, sized by the extrapolation**
(b) misses line 1 but descends faster than (c): not stopped, repeated at S2b's size

- excluded A_8f6ed7c002: NOISY (noise rule)
- excluded B_190a33a33e: NOISY (noise rule)
- excluded B_151c8ce719: NOISY (noise rule)
- excluded B_16194573ac: NOISY (noise rule)
- excluded B_17f1611949: NOISY (noise rule)
- excluded B_0040149ee1: no qff_report.npz (STOPPED or FAILED)
