# What a scale factor leaves per family on the proxy task (TASKS 112, reading 1)

Pre-registration: `GoalGathering/notes/PreRegistration_2026-10-25_Scale_Factor_Residuals.md`. Quantity: `diag_rms`, the rms error of the first-order frequency shift B3LYP/6-31G* → ωB97X/6-31G* per mode family (cm⁻¹), read by `E6.readout`. Factors fitted by least squares on all 1073 pool molecules; network = carried chain 34 (v1.1), seed mean of its three analytic records.

Fitted factors: S1 1.0132; S3 1.0191, 1.0101, 1.0135; SF 1.0135, 1.0252, 1.0102, 1.0191 (S3 regions: below 1111, 1111–2500, above 2500 cm⁻¹; SF in the order CH-stretch, CH-oop, ring-ip, other).

| hold-out | read | CH-stretch | CH-oop | ring-ip | other |
|---|---|---|---|---|---|
| (a), 10 molecules | S1 | 2.46 | 13.44 | 16.09 | 8.63 |
| (a), 10 molecules | S3 | 2.02 | 9.21 | 15.47 | 8.58 |
| (a), 10 molecules | SF | 2.04 | 6.61 | 15.31 | 8.46 |
| (a), 10 molecules | network | 1.25 | 2.36 | 1.82 | 3.35 |
| (a) | share of S3's residual the network removes | 38 % | 74 % | 88 % | 61 % |
| (b), 39 molecules | S1 | 4.26 | 14.27 | 14.67 | 15.00 |
| (b), 39 molecules | S3 | 3.86 | 9.96 | 14.19 | 14.63 |
| (b), 39 molecules | SF | 3.88 | 6.93 | 14.21 | 14.56 |
| (b), 39 molecules | network | 2.57 | 3.81 | 2.62 | 6.03 |
| (b) | share of S3's residual the network removes | 33 % | 62 % | 82 % | 59 % |

Registered lines:

- L1: (a) network < S3 in every family: **PASS** (CH-stretch yes, CH-oop yes, ring-ip yes, other yes)
- L2: (a) network < SF in every family: **PASS** (CH-stretch yes, CH-oop yes, ring-ip yes, other yes)
- L3: (b) network < S3 in every family: **PASS** (CH-stretch yes, CH-oop yes, ring-ip yes, other yes)

Record molecules equal to the current loader's hold-out: (a) yes, (b) no, read on the records ids

This is the proxy task at one basis. A scale factor's real use, B3LYP → experimental fundamentals with the anharmonicity folded in, is reading 3 (`probes/fundamentals_vs_experiment.py`).
