# E9 at CC level — R2 proxy fluorobenzene, analytic (2026-09-29 05:44): core benzene → benzene+F

Low level: B3LYP pyscf analytic (grid 99/590). High level: core wB97X (proxy, pyscf analytic); molecule wB97X (proxy, pyscf analytic). Mode substituent; 11 of 12 core atoms mapped onto the 12-atom molecule.

**R2 at r = 2, transfer + probe: PASS** — corrected ω RMS 0.76 cm⁻¹ (line ≤ 3.3), ring coupling ratio 0.07 (line ≤ 0.5); zero rule 23.16 cm⁻¹.

| r | variant | columns probed | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) | overlap median |
|---|---|---|---|---|---|---|---|
| 0 | transfer_probe | 0.08 | 0.073 | **0.13** | 1.21 | **1.32** (23.16) | 1.000 |
| 0 | probe_only | 0.08 | 0.993 | **0.99** | 17.99 | **22.98** (23.16) | 1.000 |
| 0 | transfer_only | 0.08 | 0.141 | **0.14** | 1.34 | **2.09** (23.16) | 1.000 |
| 1 | transfer_probe | 0.17 | 0.035 | **0.09** | 0.74 | **0.96** (23.16) | 1.000 |
| 1 | probe_only | 0.17 | 0.853 | **0.84** | 12.45 | **21.23** (23.16) | 0.999 |
| 1 | transfer_only | 0.17 | 0.522 | **0.76** | 6.82 | **5.08** (23.16) | 1.000 |
| 2 | transfer_probe | 0.33 | 0.014 | **0.07** | 0.71 | **0.76** (23.16) | 1.000 |
| 2 | probe_only | 0.33 | 0.571 | **0.59** | 5.52 | **18.41** (23.16) | 0.999 |
| 2 | transfer_only | 0.33 | 0.821 | **0.91** | 15.13 | **9.58** (23.16) | 0.999 |
| 3 | transfer_probe | 0.67 | 0.006 | **0.02** | 0.10 | **0.16** (23.16) | 1.000 |
| 3 | probe_only | 0.67 | 0.281 | **0.17** | 1.97 | **12.51** (23.16) | 1.000 |
| 3 | transfer_only | 0.67 | 0.960 | **0.97** | 17.60 | **15.22** (23.16) | 0.999 |
| 4 | transfer_probe | 0.92 | 0.001 | **0.00** | 0.04 | **0.05** (23.16) | 1.000 |
| 4 | probe_only | 0.92 | 0.073 | **0.09** | 0.98 | **5.08** (23.16) | 1.000 |
| 4 | transfer_only | 0.92 | 0.997 | **0.99** | 17.99 | **20.73** (23.16) | 1.000 |
| — | exact | 1.00 | 0 | 0.00 | 0.00 | 0.00 | 1.000 |
