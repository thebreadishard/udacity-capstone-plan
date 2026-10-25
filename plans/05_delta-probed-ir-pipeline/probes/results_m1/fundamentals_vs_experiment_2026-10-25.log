# Benzene and naphthalene mode by mode against experiment (TASKS 111, reading 3)

Pre-registration: `GoalGathering/notes/PreRegistration_2026-10-25_Scale_Factor_Residuals.md`. Experiment: benzene Goodman et al. 1991 and Miani et al. 2000 (`probes/data/benzene_benchmark_goodman1991_miani2000.json`); naphthalene Martin, El-Yazal & François 1996 via NIST CCCBDB (`probes/data/naphthalene_fundamentals_martin1996.json`). Mai et al. 2026 enter as statistics only (CC BY-NC-SA 4.0). Our CC anchors are Hessians at the B3LYP/6-31G* geometry of the corpus, the project's convention.

### benzene: mean / rms (cm⁻¹) per family

| comparison | CH-stretch (n) | CH-oop (n) | ring-ip (n) | other (n) | all (n) |
|---|---|---|---|---|---|
| Mai 2026 scaled − exp. fundamental | -14.5 / 18.3 (4) | -9.6 / 13.9 (4) | -24.6 / 28.9 (9) | +4.2 / 12.6 (3) | -15.3 / 22.5 (20) |
| our B3LYP/6-31G* × PAHdb factors − exp. | +1.1 / 7.2 (4) | -23.4 / 25.9 (4) | -24.3 / 25.0 (9) | -11.7 / 14.3 (3) | -17.2 / 21.3 (20) |
| our CC harmonic − exp. fundamental | +90.0 / 90.5 (4) | +14.7 / 22.5 (4) | +21.5 / 24.0 (9) | -9.0 / 19.4 (3) | +29.3 / 45.4 (20) |
| our CC harmonic − exp. harmonic (Miani) | -38.5 / 38.5 (4) | -2.3 / 19.1 (4) | +2.1 / 5.5 (9) | -13.2 / 20.4 (3) | -9.2 / 21.1 (20) |

Anchor `probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/hessian_ccsd_t.npz` (CCSD(T)/cc-pVTZ); Mai entry hc_c6h6_0pent_1, its modes paired with our B3LYP by sorted order: 0 pairs more than 50 cm⁻¹ apart (largest 39.0); smallest overlap of a CC mode with its B3LYP partner 0.99; 0 pairs flagged as possible crossings. Symmetry, b3lyp: mixed A1g+B1u resolved by projector weights (mode 11: A1g 0.00, B1u 1.00; mode 12: A1g 1.00, B1u 0.00).

#### benzene, per mode (Mai's values are not shown: licence)

| irrep | family | exp. ν | CC ω | CC − ν | B3LYP×PAHdb − ν | exp. ω | CC − ω_exp | flag |
|---|---|---|---|---|---|---|---|---|
| e2u | other | 398 | 403.4 | +5.4 | -0.9 | 406 | -2.6 |  |
| e2g | other | 608 | 609.0 | +0.9 | -13.6 | 611 | -2.0 |  |
| a2u | CH-oop | 674 | 708.9 | +34.9 | -9.7 | 687 | +21.9 |  |
| b2g | other | 707 | 673.9 | -33.1 | -20.7 | 709 | -35.1 |  |
| e1g | CH-oop | 847 | 873.6 | +26.5 | -20.3 | 865 | +8.6 |  |
| e2u | CH-oop | 967 | 973.1 | +6.1 | -40.3 | 985 | -11.9 |  |
| b2g | CH-oop | 990 | 981.4 | -8.6 | -23.5 | 1009 | -27.6 |  |
| a1g | ring-ip | 993 | 1006.3 | +13.2 | -18.0 | 1003 | +3.3 |  |
| b1u | ring-ip | 1010 | 1010.0 | -0.0 | -35.1 | 1020 | -10.0 |  |
| e1u | ring-ip | 1038 | 1059.4 | +21.1 | -16.5 | 1056 | +3.4 |  |
| b2u | ring-ip | 1150 | 1166.5 | +16.8 | -21.1 | 1163 | +3.5 |  |
| e2g | ring-ip | 1178 | 1197.2 | +19.5 | -28.0 | 1194 | +3.2 |  |
| b2u | ring-ip | 1309 | 1335.6 | +26.2 | -18.9 | 1326 | +9.6 |  |
| a2g | ring-ip | 1350 | 1377.7 | +27.7 | -29.4 | 1380 | -2.3 |  |
| e1u | ring-ip | 1484 | 1512.3 | +28.3 | -26.4 | 1509 | +3.3 |  |
| e2g | ring-ip | 1601 | 1641.7 | +40.8 | -25.1 | 1637 | +4.7 |  |
| e2g | CH-stretch | 3057 | 3144.2 | +87.5 | -0.4 | 3183 | -38.8 |  |
| b1u | CH-stretch | 3057 | 3132.7 | +75.7 | -9.9 | 3173 | -40.3 |  |
| e1u | CH-stretch | 3064 | 3162.1 | +97.8 | +7.1 | 3200 | -37.9 |  |
| a1g | CH-stretch | 3074 | 3173.1 | +99.2 | +7.7 | 3210 | -36.9 |  |

### naphthalene: mean / rms (cm⁻¹) per family

| comparison | CH-stretch (n) | CH-oop (n) | ring-ip (n) | other (n) | all (n) |
|---|---|---|---|---|---|
| Mai 2026 scaled − exp. fundamental | +5.0 / 19.8 (8) | -1.0 / 8.9 (8) | -2.6 / 14.7 (18) | +6.2 / 16.2 (14) | +1.5 / 15.4 (48) |
| our B3LYP/6-31G* × PAHdb factors − exp. | +1.3 / 18.0 (8) | -25.3 / 26.9 (8) | -19.4 / 21.0 (18) | -7.1 / 15.2 (14) | -13.3 / 20.2 (48) |
| our CC harmonic − exp. fundamental | +95.7 / 97.4 (8) | -0.6 / 11.7 (8) | +29.5 / 32.3 (18) | +0.3 / 16.3 (14) | +27.0 / 45.5 (48) |

Anchor `modules/05_support_predictor/out/composite_full_naphthalene_2026-10-07.npz` (CCSD(T)/cc-pVDZ + [MP2/cc-pVTZ − MP2/cc-pVDZ]); Mai entry C2M011912, hc_c10h8_0pent_1, its modes paired with our B3LYP by sorted order: 0 pairs more than 50 cm⁻¹ apart (largest 38.0); smallest overlap of a CC mode with its B3LYP partner 0.92; 2 pairs flagged as possible crossings.

#### naphthalene, per mode (Mai's values are not shown: licence)

| irrep | family | exp. ν | CC ω | CC − ν | B3LYP×PAHdb − ν | exp. ω | CC − ω_exp | flag |
|---|---|---|---|---|---|---|---|---|
| B3u | other | 176 | 167.2 | -8.8 | -8.1 | — | — |  |
| Au | other | 195 | 180.3 | -14.7 | -13.5 | — | — |  |
| B1u | other | 359 | 354.2 | -4.8 | -11.2 | — | — |  |
| B1g | other | 386 | 381.7 | -4.3 | -6.8 | — | — |  |
| B2g | other | 461 | 462.4 | +1.4 | -0.3 | — | — |  |
| B3u | other | 476 | 474.5 | -1.5 | -5.9 | — | — |  |
| B3g | other | 506 | 507.3 | +1.3 | -11.0 | — | — |  |
| Ag | other | 512 | 511.4 | -0.6 | -14.4 | — | — |  |
| Au | other | 581 | 598.3 | +17.3 | +24.6 | — | — |  |
| B2u | other | 618 | 617.0 | -1.0 | -10.3 | — | — |  |
| B1g | CH-oop | 717 | 733.8 | +16.8 | -14.8 | — | — |  |
| B1u | other | 753 | 796.8 | +43.8 | +19.6 | — | — |  |
| Ag | other | 758 | 765.3 | +7.3 | -15.7 | — | — |  |
| B2g | other | 770 | 737.0 | -33.0 | -19.1 | — | — |  |
| B3u | CH-oop | 782 | 797.6 | +15.6 | -13.3 | — | — |  |
| Au | CH-oop | 841 | 843.5 | +2.5 | -26.1 | — | — |  |
| B2g | CH-oop | 876 | 872.3 | -3.7 | -15.4 | — | — |  |
| B3g | other | 935 | 937.1 | +2.1 | -27.3 | — | — |  |
| B1g | CH-oop | 943 | 943.2 | +0.2 | -37.7 | — | — |  |
| B3u | CH-oop | 958 | 954.8 | -3.2 | -37.0 | — | — |  |
| Au | CH-oop | 970 | 954.4 | -15.6 | -28.1 | — | — |  |
| B2g | CH-oop | 980 | 962.9 | -17.1 | -29.7 | — | — |  |
| B2u | ring-ip | 1008 | 1030.7 | +22.7 | -9.1 | — | — |  |
| Ag | ring-ip | 1025 | 1041.6 | +16.6 | -15.7 | — | — |  |
| B1u | ring-ip | 1125 | 1140.7 | +15.7 | -23.6 | — | — |  |
| B2u | ring-ip | 1138 | 1158.2 | +20.2 | -10.7 | — | — |  |
| Ag | ring-ip | 1145 | 1177.9 | +32.9 | -8.4 | — | — |  |
| B3g | ring-ip | 1158 | 1165.7 | +7.7 | -33.5 | — | — |  |
| B2u | ring-ip | 1209 | 1232.2 | +23.2 | -24.9 | — | — |  |
| B3g | ring-ip | 1239 | 1263.0 | +24.0 | -22.7 | — | — |  |
| B1u | ring-ip | 1265 | 1279.6 | +14.6 | -30.3 | — | — |  |
| B2u | ring-ip | 1361 | 1393.2 | +32.2 | -18.7 | — | — |  |
| Ag | ring-ip | 1376 | 1410.2 | +34.2 | -26.9 | — | — |  |
| B1u | ring-ip | 1389 | 1412.2 | +23.2 | -26.8 | — | — |  |
| B3g | ring-ip | 1438 | 1487.2 | +49.2 | -4.3 | — | — |  |
| Ag | ring-ip | 1460 | 1487.8 | +27.8 | -23.0 | — | — |  |
| B2u | ring-ip | 1506 | 1552.9 | +46.9 | -14.0 | — | — |  |
| Ag | ring-ip | 1577 | 1614.3 | +37.3 | -24.9 | — | — |  |
| B1u | ring-ip | 1595 | 1638.6 | +43.6 | -15.9 | — | — |  |
| B3g | ring-ip | 1624 | 1682.9 | +58.9 | -16.8 | — | — |  |
| B2u | CH-stretch | 3027 | 3146.1 | +119.1 | +24.1 | — | — |  |
| Ag | CH-stretch | 3031 | 3148.5 | +117.5 | +23.6 | — | — |  |
| B1u | CH-stretch | 3058 | 3141.4 | +83.4 | -8.4 | — | — | crossing? |
| Ag | CH-stretch | 3060 | 3175.2 | +115.2 | +19.7 | — | — |  |
| B3g | CH-stretch | 3060 | 3140.5 | +80.5 | -12.3 | — | — |  |
| B1u | CH-stretch | 3065 | 3161.9 | +96.9 | +1.9 | — | — | crossing? |
| B2u | CH-stretch | 3090 | 3174.2 | +84.2 | -11.5 | — | — |  |
| B3g | CH-stretch | 3092 | 3160.8 | +68.8 | -26.3 | — | — |  |

