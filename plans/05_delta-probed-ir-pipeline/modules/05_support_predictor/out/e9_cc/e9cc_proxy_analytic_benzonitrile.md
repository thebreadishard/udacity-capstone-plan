# E9 at CC level — proxy pyscf analytic (2026-09-29 05:17): core benzene → benzonitrile

Low level: B3LYP pyscf analytic (grid 99/590). High level: core wB97X (proxy, pyscf analytic); molecule wB97X (proxy, pyscf analytic). Mode substituent; 11 of 12 core atoms mapped onto the 13-atom molecule.

**R2 at r = 2, transfer + probe: PASS** — corrected ω RMS 0.88 cm⁻¹ (line ≤ 3.3), ring coupling ratio 0.06 (line ≤ 0.5); zero rule 24.22 cm⁻¹.

| r | variant | columns probed | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) | overlap median |
|---|---|---|---|---|---|---|---|
| 0 | transfer_probe | 0.15 | 0.127 | **0.22** | 2.52 | **1.96** (24.22) | 1.000 |
| 0 | probe_only | 0.15 | 0.817 | **0.98** | 18.71 | **22.05** (24.22) | 1.000 |
| 0 | transfer_only | 0.15 | 0.590 | **0.25** | 3.05 | **9.38** (24.22) | 1.000 |
| 1 | transfer_probe | 0.23 | 0.029 | **0.07** | 1.07 | **1.03** (24.22) | 1.000 |
| 1 | probe_only | 0.23 | 0.679 | **0.76** | 12.66 | **20.09** (24.22) | 1.000 |
| 1 | transfer_only | 0.23 | 0.735 | **0.79** | 8.12 | **9.93** (24.22) | 0.999 |
| 2 | transfer_probe | 0.38 | 0.015 | **0.06** | 0.77 | **0.88** (24.22) | 1.000 |
| 2 | probe_only | 0.38 | 0.445 | **0.50** | 5.76 | **17.10** (24.22) | 0.999 |
| 2 | transfer_only | 0.38 | 0.895 | **0.96** | 15.28 | **13.11** (24.22) | 0.997 |
| 3 | transfer_probe | 0.69 | 0.006 | **0.01** | 0.10 | **0.31** (24.22) | 1.000 |
| 3 | probe_only | 0.69 | 0.218 | **0.14** | 2.13 | **11.40** (24.22) | 1.000 |
| 3 | transfer_only | 0.69 | 0.976 | **1.00** | 18.00 | **17.53** (24.22) | 0.998 |
| 4 | transfer_probe | 0.92 | 0.001 | **0.00** | 0.03 | **0.16** (24.22) | 1.000 |
| 4 | probe_only | 0.92 | 0.057 | **0.07** | 0.99 | **5.17** (24.22) | 1.000 |
| 4 | transfer_only | 0.92 | 0.998 | **1.00** | 18.66 | **22.04** (24.22) | 0.999 |
| — | exact | 1.00 | 0 | 0.00 | 0.00 | 0.00 | 1.000 |
