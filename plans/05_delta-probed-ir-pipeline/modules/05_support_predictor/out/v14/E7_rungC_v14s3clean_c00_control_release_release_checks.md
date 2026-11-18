# Release checks (2026-11-18 07:16) — PASSED

Release networks: E7_rungC_v14s3clean_c00_control_release_model_n1132_seed0.pt, E7_rungC_v14s3clean_c00_control_release_model_n1132_seed1.pt, E7_rungC_v14s3clean_c00_control_release_model_n1132_seed2.pt. Measurement networks: E7_rungC_v14s3clean_c00_control_model_n1082_seed0.pt, E7_rungC_v14s3clean_c00_control_model_n1082_seed1.pt, E7_rungC_v14s3clean_c00_control_model_n1082_seed2.pt. Decision 66, design note of 17 Nov 2026, §4.

| check | passed | refusal |
|---|---|---|
| 1 same_recipe | yes |  |
| 2 pool_agreement | yes |  |
| 3 holdouts_learnt | yes |  |
| 4 early_stopping | yes |  |
| 5 benzene | yes |  |

## 2 Pool sample (40 of 1041 molecules; cm⁻¹)

| family | release − measurement, seed means | among the measurement seeds | bands |
|---|---|---|---|
| ring-ip | 2.852 | 2.862 | 853 |
| CH-stretch | 0.888 | 1.567 | 293 |
| CH-oop | 0.898 | 1.777 | 99 |
| other | 1.454 | 3.662 | 981 |

## 3 Hold-out (a8): 8 of 8 listed molecules (cm⁻¹)

| family | release, in-sample | measurement, held out | bands |
|---|---|---|---|
| ring-ip | 0.718 | 1.169 | 199 |
| CH-stretch | 0.614 | 0.801 | 73 |
| CH-oop | 1.122 | 1.861 | 46 |
| other | 1.724 | 2.378 | 156 |

## 3 Hold-out (b): 40 of 41 listed molecules (cm⁻¹)

| family | release, in-sample | measurement, held out | bands |
|---|---|---|---|
| ring-ip | 0.534 | 1.224 | 1194 |
| CH-stretch | 0.690 | 1.665 | 410 |
| CH-oop | 0.811 | 1.264 | 84 |
| other | 1.207 | 2.100 | 1258 |

## 5 Benzene (A_8448043181), cm⁻¹

Fitted by 2 of 3 release networks (the others stopped on it); previous version's release networks: none.

| B3LYP | family | ωB97X | measurement | release |
|---|---|---|---|---|
| 415.40 | other | 425.87 | 425.31 | 425.88 |
| 415.42 | other | 425.54 | 425.42 | 426.01 |
| 621.86 | other | 625.54 | 625.45 | 625.74 |
| 621.88 | other | 625.58 | 625.47 | 625.76 |
| 694.85 | CH-oop | 699.77 | 701.12 | 702.46 |
| 717.88 | other | 734.14 | 733.51 | 735.39 |
| 864.85 | CH-oop | 883.58 | 891.00 | 884.69 |
| 864.85 | CH-oop | 883.32 | 888.34 | 885.67 |
| 969.35 | CH-oop | 1001.50 | 998.14 | 1000.12 |
| 969.35 | CH-oop | 1001.70 | 997.59 | 1000.19 |
| 1010.99 | CH-oop | 1036.65 | 1038.87 | 1036.97 |
| 1019.81 | ring-ip | 1024.81 | 1024.56 | 1024.76 |
| 1019.96 | ring-ip | 1032.62 | 1031.88 | 1033.05 |
| 1068.79 | ring-ip | 1078.72 | 1078.51 | 1078.83 |
| 1068.84 | ring-ip | 1078.41 | 1078.56 | 1078.87 |
| 1185.54 | ring-ip | 1174.93 | 1175.50 | 1175.80 |
| 1207.69 | ring-ip | 1210.16 | 1210.05 | 1210.76 |
| 1207.72 | ring-ip | 1210.54 | 1210.08 | 1210.79 |
| 1355.60 | ring-ip | 1324.62 | 1324.14 | 1323.89 |
| 1387.15 | ring-ip | 1390.79 | 1388.50 | 1390.27 |
| 1531.04 | ring-ip | 1540.80 | 1541.32 | 1541.48 |
| 1531.08 | ring-ip | 1540.91 | 1541.35 | 1541.51 |
| 1655.29 | ring-ip | 1689.10 | 1688.94 | 1688.98 |
| 1655.33 | ring-ip | 1689.18 | 1688.99 | 1689.02 |
| 3174.02 | CH-stretch | 3217.19 | 3216.59 | 3215.13 |
| 3183.65 | CH-stretch | 3226.68 | 3226.43 | 3225.17 |
| 3183.65 | CH-stretch | 3226.69 | 3226.43 | 3225.17 |
| 3199.41 | CH-stretch | 3242.24 | 3242.32 | 3240.84 |
| 3199.42 | CH-stretch | 3242.25 | 3242.33 | 3240.85 |
| 3210.07 | CH-stretch | 3252.69 | 3252.42 | 3251.21 |
