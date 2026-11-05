# MP2 against ωB97X as the stepping stone, on the 11 carried TZ anchors (TASKS 11 (c))

Shifts K_kk in the analytic B3LYP mode basis, pooled per family; 'scaled' = CC − s·candidate with s fitted on the other anchors.

| family | candidate | anchors | modes | corr | slope | rms CC | rms CC − cand | rms scaled |
|---|---|---|---|---|---|---|---|---|
| CH-oop | wb97x | 11 | 79 | -0.26 | -0.51 | 17.78 | 37.22 | 13.73 |
| CH-oop | mp2_dz | 11 | 79 | +0.85 | +0.22 | 17.78 | 53.05 | 10.17 |
| CH-oop | mp2_tz | 11 | 79 | +0.97 | +0.70 | 17.78 | 14.07 | 13.61 |
| CH-oop | mp2_631gs | 11 | 79 | +0.88 | +0.16 | 17.78 | 83.74 | 8.14 |
| other | wb97x | 11 | 131 | -0.25 | -1.09 | 17.56 | 27.12 | 13.10 |
| other | mp2_dz | 11 | 131 | +0.57 | +0.27 | 17.56 | 38.73 | 11.11 |
| other | mp2_tz | 11 | 131 | +0.62 | +0.62 | 17.56 | 15.12 | 14.73 |
| other | mp2_631gs | 11 | 131 | +0.69 | +0.20 | 17.56 | 50.41 | 12.44 |
| ring-ip | wb97x | 11 | 183 | +0.59 | -0.18 | 16.02 | 29.59 | 16.01 |
| ring-ip | mp2_dz | 11 | 183 | -0.18 | -0.14 | 16.02 | 47.91 | 15.07 |
| ring-ip | mp2_tz | 11 | 183 | -0.41 | +0.01 | 16.02 | 32.57 | 16.94 |
| ring-ip | mp2_631gs | 11 | 183 | -0.43 | -0.36 | 16.02 | 46.46 | 10.81 |
| CH-stretch | wb97x | 11 | 75 | +0.35 | -0.79 | 34.38 | 77.73 | 2.52 |
| CH-stretch | mp2_dz | 11 | 75 | +0.06 | -0.31 | 34.38 | 144.62 | 2.27 |
| CH-stretch | mp2_tz | 11 | 75 | +0.60 | +1.52 | 34.38 | 11.90 | 2.16 |
| CH-stretch | mp2_631gs | 11 | 75 | -0.44 | -0.79 | 34.38 | 77.98 | 1.91 |

| family | verdict (MP2/cc-pVDZ against ωB97X, scaled rms) | ratio |
|---|---|---|
| CH-oop | better | 0.74 |
| other | no clear difference | 0.85 |
| ring-ip | no clear difference | 0.94 |
| CH-stretch | no clear difference | 0.90 |

| family | verdict (MP2/6-31G* against ωB97X, scaled rms; amendment 1) | ratio |
|---|---|---|
| CH-oop | better | 0.59 |
| other | no clear difference | 0.95 |
| ring-ip | better | 0.68 |
| CH-stretch | better | 0.76 |
