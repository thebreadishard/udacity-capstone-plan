# E9 at CC level — R3 proxy, analytic (2026-09-29 05:43): core benzene → pyridine

Low level: B3LYP pyscf analytic (grid 99/590). High level: core wB97X (proxy, pyscf analytic); molecule wB97X (proxy, pyscf analytic). Mode element; 11 of 12 core atoms mapped onto the 11-atom molecule.

| r | variant | columns probed | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) | overlap median |
|---|---|---|---|---|---|---|---|
| 0 | transfer_probe | 0.00 | 0.128 | **0.18** | 1.84 | **2.03** (25.02) | 1.000 |
| 0 | probe_only | 0.00 | 1.000 | **1.00** | 19.84 | **25.02** (25.02) | 0.999 |
| 0 | transfer_only | 0.00 | 0.128 | **0.18** | 1.84 | **2.03** (25.02) | 1.000 |
| — | exact | 1.00 | 0 | 0.00 | 0.00 | 0.00 | 1.000 |

## R3 split, transfer only at r = 0: modes with N participation > 0.3

| modes | n | corrected ω RMS |
|---|---|---|
| N-participating | 2 | 2.83 |
| other | 25 | 1.95 |
| all | 27 | 2.03 |
