# The out-of-plane block on the six-anchor baseline (exploratory, 13 Oct 2026)

Saved λ = 1 folds of 10 Oct; ω matched by eigenvector per kind (not the registered sorted-family read).

## R-C: the strongest out-of-plane mode and its nearest partner of the same species

| anchor | pair (cm⁻¹, truth) | θ zero rule | θ λ = 1 (seeds) | κ λ = 1 (cm⁻¹) | κ zero (cm⁻¹) | gap λ = 1 (cm⁻¹) | captured λ = 1 |
|---|---|---|---|---|---|---|---|
| pyridine | 717.7 / 757.8 | -15.7° | -19.5° / -18.9° / -21.1° | +15.42 | +11.49 | -37.1 | 0.999 |
| fluorobenzene | 669.7 / 768.6 | -5.5° | -9.1° / -8.7° / -8.8° | +10.39 | +6.73 | -65.2 | 0.995 |
| benzonitrile | 682.9 / 770.9 | -10.7° | -15.4° / -14.0° / -14.0° | +19.09 | +13.32 | -69.2 | 0.984 |

## The arms: out-of-plane couplings from B3LYP; the out-of-plane block from the model

| anchor | read | zero rule | λ = 1 | λ = 1, oop couplings from B3LYP | B3LYP + model diagonal | λ = 1, oop block from the model |
|---|---|---|---|---|---|---|
| benzene | ω rms CH-str (cm⁻¹) | 38.64 | 4.95 | 4.95 | 38.64 | 4.95 |
| benzene | ω rms ip (cm⁻¹) | 13.99 | 4.74 | 4.74 | 13.99 | 4.74 |
| benzene | ω rms oop (cm⁻¹) | 19.67 | 19.62 | 19.67 | 13.26 | 13.26 |
| benzene | intensity rel. rms, matched (CC APT) | 0.003 | 0.007 | 0.007 | 0.003 | 0.007 |
| naphthalene | ω rms CH-str (cm⁻¹) | 33.24 | 2.47 | 2.47 | 33.24 | 2.47 |
| naphthalene | ω rms ip (cm⁻¹) | 15.40 | 4.50 | 4.50 | 15.40 | 4.50 |
| naphthalene | ω rms oop (cm⁻¹) | 22.45 | 19.67 | 19.70 | 9.75 | 9.75 |
| pyridine | ω rms CH-str (cm⁻¹) | 35.56 | 2.16 | 2.16 | 35.56 | 2.16 |
| pyridine | ω rms ip (cm⁻¹) | 14.73 | 4.20 | 4.20 | 14.73 | 4.20 |
| pyridine | ω rms oop (cm⁻¹) | 7.88 | 10.97 | 10.95 | 15.52 | 15.52 |
| pyridine | intensity rel. rms, matched (CC APT) | 0.262 | 0.310 | 0.262 | 0.262 | 0.262 |
| fluorobenzene | ω rms CH-str (cm⁻¹) | 34.70 | 1.27 | 1.27 | 34.70 | 1.27 |
| fluorobenzene | ω rms ip (cm⁻¹) | 15.13 | 2.90 | 2.90 | 15.13 | 2.90 |
| fluorobenzene | ω rms oop (cm⁻¹) | 11.52 | 10.06 | 10.13 | 10.26 | 10.26 |
| fluorobenzene | intensity rel. rms, matched (CC APT) | 0.104 | 0.172 | 0.107 | 0.104 | 0.107 |
| benzonitrile | ω rms CH-str (cm⁻¹) | 35.40 | 1.89 | 1.89 | 35.40 | 1.89 |
| benzonitrile | ω rms ip (cm⁻¹) | 21.22 | 19.44 | 19.45 | 21.22 | 19.45 |
| benzonitrile | ω rms oop (cm⁻¹) | 16.50 | 24.61 | 25.38 | 6.97 | 6.97 |
| benzonitrile | intensity rel. rms, matched (CC APT) | 0.258 | 0.443 | 0.258 | 0.258 | 0.258 |
| anthracene | ω rms CH-str (cm⁻¹) | 32.88 | 2.81 | 2.81 | 32.88 | 2.81 |
| anthracene | ω rms ip (cm⁻¹) | 15.53 | 7.54 | 7.54 | 15.53 | 7.54 |
| anthracene | ω rms oop (cm⁻¹) | 25.78 | 21.89 | 21.94 | 13.51 | 13.51 |

## The out-of-plane diagonal: first-order shifts ΔH_kk / 2ω_k (cm⁻¹), predicted (λ = 1) against true

| anchor | oop modes | true shift rms | error rms (seeds) | slope pred/true (seeds) | correlation (seeds) |
|---|---|---|---|---|---|
| benzene | 9 | 18.8 | 18.6 / 18.8 / 18.9 | 0.03 / 0.04 / 0.02 | -0.16 / -0.19 / -0.08 |
| naphthalene | 15 | 21.4 | 19.7 / 18.9 / 18.3 | 0.11 / 0.15 / 0.19 | 0.20 / 0.12 / 0.20 |
| pyridine | 8 | 8.0 | 10.8 / 11.7 / 11.0 | 0.17 / 0.13 / 0.11 | -0.43 / -0.49 / -0.43 |
| fluorobenzene | 9 | 11.2 | 9.8 / 9.8 / 9.9 | 0.16 / 0.18 / 0.17 | 0.24 / 0.28 / 0.16 |
| benzonitrile | 10 | 16.0 | 25.3 / 26.4 / 24.0 | -0.42 / -0.50 / -0.34 | -0.44 / -0.41 / -0.39 |
| anthracene | 21 | 24.8 | 22.2 / 20.9 / 20.8 | 0.14 / 0.19 / 0.19 | 0.20 / 0.31 / 0.32 |

