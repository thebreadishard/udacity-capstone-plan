# X19a — IP-tuned LRC-ωPBEh against B3LYP on benzene's three probe modes, truth canonical CCSD(T)/cc-pvtz (2026-09-19 10:41)

ω* = 0.24 bohr⁻¹ (J bracket (0.2, 0.25)); grid [99, 590]; 16 threads.

| functional | mode 6 Δω (cm⁻¹) | mode 12 Δω (cm⁻¹) | mode 18 Δω (cm⁻¹) | RMS |
|---|---|---|---|---|
| B3LYP | -12.30 | +5.71 | +26.72 | 17.30 |
| LRC-ωPBEh ω=0.2 (default) | -9.31 | -3.90 | +30.73 | 18.68 |
| LRC-ωPBEh ω*=0.24 | -17.37 | -5.77 | +42.41 | 26.67 |

Ratio tuned/B3LYP = 1.54; sign flips: [12]; **LOSE** (pre-registered: WIN ≤ 0.5 without flip, LOSE ≥ 0.8 or flip).
