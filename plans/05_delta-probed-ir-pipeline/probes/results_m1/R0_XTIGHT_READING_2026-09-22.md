# Diagonal deck reading — results_m1/benzene_r0_cc-pvtz_xtight_r0diag_xtight

ω′ = ω_B3LYP √(k/ω_au): the harmonic frequency the composite (SCF + LNO-CCSD(T) − LNO-MP2 + full MP2) would give along the B3LYP mode, diagonal only.

| mode | family | Wilson | ω B3LYP | points | k composite (µE_h/q²) | c₄ | ω′ composite | ω′ SCF-only | ω′ SCF+MP2 | ω′ − ω | ω CCSD(T) | ω′ − ω_CC | ω_exp Goodman | ω′ − ω_exp | experiment ν | ω′ − ν |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | CH-oop | ν4 b2g | 717.5 | +0.5,1.0 | +2931.9 | +96.1 | **679.5** | 785.6 | 695.1 | -38.0 | 717 | -37.5 | 707.0 | -27.5 | 707 | -27.5 |
| 29 | CH-stretch | ν2 a1g | 3210.0 | ±0.5,1.0 | +14292.1 | +134.1 | **3173.2** | 3224.8 | 3188.3 | -36.8 | 3218 | -44.8 | 3191.0 | -17.8 | 3074 | +99.2 |

## Against the CCSD(T) harmonics (Miani et al. 2000 Table II, their ref. 26) and Goodman 1991 Table II ω estimates

| group | modes | MAE ω_B3LYP − ω_CC | MAE ω′ − ω_CC | mean ω′ − ω_CC | MAE ω_B3LYP − ω_exp | MAE ω′ − ω_exp |
|---|---|---|---|---|---|---|
| out-of-plane | 1 | 0.5 | 37.5 | -37.5 | 10.5 | 27.5 |
| C–H stretch | 1 | 8.0 | 44.8 | -44.8 | 19.0 | 17.8 |
| all | 2 | 4.2 | 41.2 | -41.2 | 14.8 | 22.7 |

ω′ is diagonal only (the mode is the B3LYP mode; no off-diagonal coupling correction), from the composite SCF + LNO-CCSD(T) − LNO-MP2 + full MP2 at cc-pVTZ along ±q or +q. The CCSD(T) column is a full harmonic calculation from the literature (basis as in Miani's ref. 26); Goodman's ω estimates carry anharmonic corrections for nine modes only.
