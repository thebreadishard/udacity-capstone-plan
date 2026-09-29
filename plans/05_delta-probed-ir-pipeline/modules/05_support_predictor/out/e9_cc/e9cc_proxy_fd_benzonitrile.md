# E9 at CC level — proxy psi4 FD (2026-09-29 05:16): core benzene → benzonitrile

Low level: B3LYP psi4 FD (grid 75/302). High level: core wB97X (proxy, psi4 FD); molecule wB97X (proxy, psi4 FD). Mode substituent; 11 of 12 core atoms mapped onto the 13-atom molecule.

**R2 at r = 2, transfer + probe: FAIL** — corrected ω RMS 21.88 cm⁻¹ (line ≤ 3.3), ring coupling ratio 3.70 (line ≤ 0.5); zero rule 24.48 cm⁻¹.

| r | variant | columns probed | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) | overlap median |
|---|---|---|---|---|---|---|---|
| 0 | transfer_probe | 0.15 | 0.793 | **4.55** | 66.78 | **27.27** (24.48) | 0.972 |
| 0 | probe_only | 0.15 | 0.805 | **0.99** | 18.43 | **22.30** (24.48) | 1.000 |
| 0 | transfer_only | 0.15 | 0.990 | **4.56** | 66.59 | **28.92** (24.48) | 0.984 |
| 1 | transfer_probe | 0.23 | 0.737 | **4.35** | 67.65 | **27.77** (24.48) | 0.979 |
| 1 | probe_only | 0.23 | 0.670 | **0.76** | 12.53 | **20.39** (24.48) | 1.000 |
| 1 | transfer_only | 0.23 | 1.047 | **4.51** | 65.91 | **29.81** (24.48) | 0.981 |
| 2 | transfer_probe | 0.38 | 0.513 | **3.70** | 53.22 | **21.88** (24.48) | 0.972 |
| 2 | probe_only | 0.38 | 0.439 | **0.51** | 5.53 | **17.36** (24.48) | 0.999 |
| 2 | transfer_only | 0.38 | 1.035 | **3.90** | 53.89 | **25.65** (24.48) | 0.987 |
| 3 | transfer_probe | 0.69 | 0.275 | **2.14** | 8.32 | **6.31** (24.48) | 0.990 |
| 3 | probe_only | 0.69 | 0.213 | **0.16** | 1.96 | **11.41** (24.48) | 1.000 |
| 3 | transfer_only | 0.69 | 1.015 | **2.37** | 20.05 | **18.80** (24.48) | 0.989 |
| 4 | transfer_probe | 0.92 | 0.041 | **0.84** | 9.03 | **5.48** (24.48) | 1.000 |
| 4 | probe_only | 0.92 | 0.056 | **0.07** | 1.00 | **5.09** (24.48) | 1.000 |
| 4 | transfer_only | 0.92 | 0.999 | **1.28** | 20.77 | **23.12** (24.48) | 0.997 |
| — | exact | 1.00 | 0 | 0.00 | 0.00 | 0.00 | 1.000 |
