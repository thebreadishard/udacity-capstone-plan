# Dry run — naphthalene — 2026-09-16 15:45 — machine Asus18, 8 threads, psi4 1.11

## Timing (B2 laptop, this run)
- optimize_s: 0.00 min
- hessian_b3lyp_s: 29.50 min
- hessian_bhhlyp_s: 28.85 min

## Modes: M = 48; families: CC-stretch×9, CH-ip-bend×9, CH-oop×15, CH-stretch×8, ring-ip×7
- totally symmetric mode used by the Q6 scan: index 11 (776 cm⁻¹)

## Deck: hash 8a6a9d52423cd870…, 664 ± pairs in K (48 single-mode + 616 off-diagonal), 123 held out (f_h = 0.2), q_s = 1.0, q₂ = 0.5; 1425 energies evaluated per arm (gradients too)

## Reference constant c₀ = -0.022 ± 0.128 µE_h (two-amplitude read over all modes)
## Δ₁ (∂ΔE/∂q at the B3LYP geometry, dimensionless q), |Δ₁| max = 2930.5 µE_h per unit q

## The w rule: w = 25.0 cm⁻¹ (λ = 1e-07); table:
- w = 25: hold-out ρ = 0.034, worst family RMS = 3.37 cm⁻¹
- w = 50: hold-out ρ = 0.034, worst family RMS = 3.36 cm⁻¹
- w = 100: hold-out ρ = 0.034, worst family RMS = 3.36 cm⁻¹
- w = 200: hold-out ρ = 0.040, worst family RMS = 3.36 cm⁻¹
- w = 400: hold-out ρ = 0.048, worst family RMS = 0.82 cm⁻¹

## Mode E: ρ with all training pairs = 0.034; RMS held-out response = 198.22 µE_h. (Legacy: at the retired declared ρ = 0.1 the raw curve would stop at 98 energies, K_off = 2 — the blindness of decision 8/12; K is read in the noise column below.)
- recovered-vs-direct RMS frequency error per family (cm⁻¹), full recovery (re-diagonalised) / diagonal-only (CMA-0):
  - CC-stretch (n=9): full 2.33 / diag-only 4.10
  - CH-ip-bend (n=9): full 3.37 / diag-only 5.97
  - CH-oop (n=15): full 0.36 / diag-only 1.10
  - CH-stretch (n=8): full 2.89 / diag-only 0.03
  - ring-ip (n=7): full 0.44 / diag-only 0.45
- ρ(n) curve (energies, ρ): (98,0.035), (180,0.036), (262,0.034), (344,0.042), (426,0.057), (508,0.054), (590,0.048), (672,0.046), (754,0.044), (836,0.044), (918,0.039), (1000,0.039), (1082,0.034)
- **model floor** ρ_dry = 0.0340 (noiseless responses, all training pairs): the quartic contamination of the quadratic model at q_s = 1.0
- **off-diagonal view**: RMS of the off-diagonal part of the held-out responses = 7.00 µE_h (vs 198.22 raw); ρ_off(n) curve: (98,1.000), (180,1.033), (262,0.966), (344,1.198), (426,1.628), (508,1.537), (590,1.363), (672,1.296), (754,1.244), (836,1.242), (918,1.103), (1000,1.091), (1082,0.961); K at declared ρ_off = None; **K_off at ρ_off ≤ 0.3 = None energies**
- **diagonal-anchored recovery** (diagonal from the single block, off-diagonals fitted to the residual): ρ_off = 0.960; family RMS (cm⁻¹): CC-stretch 2.30, CH-ip-bend 3.37, CH-oop 0.37, CH-stretch 2.87, ring-ip 0.44
- **quartic-corrected, diagonal-anchored recovery** (Δ_ii and Δ₄,iiii from the two amplitudes; Σ Δ₄ a⁴/24 subtracted): off-diagonal RMS after subtraction = 7.01 µE_h; ρ_off = 0.962; family RMS (cm⁻¹): CC-stretch 2.40, CH-ip-bend 3.37, CH-oop 0.32, CH-stretch 2.86, ring-ip 0.42; two-amplitude diagonal alone: CC-stretch 4.19, CH-ip-bend 5.97, CH-oop 1.06, CH-stretch 0.04, ring-ip 0.44

## Mode G: K at declared ρ: 96 gradients; model floor ρ_dry(G) = 0.0019; family error (full):
  - CC-stretch: 0.08 cm⁻¹
  - CH-ip-bend: 0.11 cm⁻¹
  - CH-oop: 0.21 cm⁻¹
  - CH-stretch: 0.05 cm⁻¹
  - ring-ip: 0.13 cm⁻¹

## Off-diagonal blocks flagged large in the direct Δ₂ (|Δ_ij| > 0.2 × RMS diagonal); (i, j, ratio, ω_i, ω_j):
- (26, 31, +1.14, 1184, 1410)
- (26, 28, -0.53, 1184, 1244)
- (28, 31, +0.48, 1244, 1410)
- (0, 13, +0.40, 175, 804)
- (25, 39, +0.38, 1181, 1688)
- (12, 16, -0.38, 785, 900)
- (5, 13, -0.38, 492, 804)
- (27, 37, +0.38, 1194, 1630)
- (24, 38, -0.37, 1157, 1659)
- (22, 28, +0.37, 1045, 1244)
- (23, 35, -0.35, 1056, 1509)
- (1, 15, -0.34, 190, 852)
- (28, 36, +0.33, 1244, 1567)
- (29, 34, +0.29, 1278, 1506)
- (25, 34, -0.29, 1181, 1506)

## Noise-injection column (K in energies or gradients at ρ* = c·ρ_noise; 'at-noise' if c·ρ_noise ≥ 0.5)
- mode E, σ_E = 0.5 µE_h: ρ_noise = 0.002; c=1.0: K=not-reached; c=1.5: K=not-reached; c=2.0: K=not-reached; c=3.0: K=not-reached  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=98; c=1.5: K=98; c=2.0: K=98; c=3.0: K=98
    P1+P2 reading on ρ_off (decisions 8, 9, 12): ρ_noise,off = 0.050, ρ_dry,off = 0.963; c=1.0: K=at-noise; c=1.5: K=at-noise; c=2.0: K=at-noise; c=3.0: K=at-noise
- mode G, σ_g = 0.5 µE_h per unit q: ρ_noise = 0.005; c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96  | with the floor: c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96
- mode E, σ_E = 1.0 µE_h: ρ_noise = 0.004; c=1.0: K=not-reached; c=1.5: K=not-reached; c=2.0: K=not-reached; c=3.0: K=not-reached  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=98; c=1.5: K=98; c=2.0: K=98; c=3.0: K=98
    P1+P2 reading on ρ_off (decisions 8, 9, 12): ρ_noise,off = 0.101, ρ_dry,off = 0.963; c=1.0: K=at-noise; c=1.5: K=at-noise; c=2.0: K=at-noise; c=3.0: K=at-noise
- mode G, σ_g = 1.0 µE_h per unit q: ρ_noise = 0.011; c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96  | with the floor: c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96
- mode E, σ_E = 2.0 µE_h: ρ_noise = 0.007; c=1.0: K=not-reached; c=1.5: K=not-reached; c=2.0: K=not-reached; c=3.0: K=not-reached  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=98; c=1.5: K=98; c=2.0: K=98; c=3.0: K=98
    P1+P2 reading on ρ_off (decisions 8, 9, 12): ρ_noise,off = 0.202, ρ_dry,off = 0.963; c=1.0: K=at-noise; c=1.5: K=at-noise; c=2.0: K=at-noise; c=3.0: K=at-noise
- mode G, σ_g = 2.0 µE_h per unit q: ρ_noise = 0.021; c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96  | with the floor: c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96
- mode E, σ_E = 5.0 µE_h: ρ_noise = 0.018; c=1.0: K=not-reached; c=1.5: K=not-reached; c=2.0: K=748; c=3.0: K=98  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=674; c=1.5: K=674; c=2.0: K=674; c=3.0: K=98
    P1+P2 reading on ρ_off (decisions 8, 9, 12): ρ_noise,off = 0.505, ρ_dry,off = 0.963; c=1.0: K=at-noise; c=1.5: K=at-noise; c=2.0: K=at-noise; c=3.0: K=at-noise
- mode G, σ_g = 5.0 µE_h per unit q: ρ_noise = 0.054; c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96  | with the floor: c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96
- mode E, σ_E = 10.0 µE_h: ρ_noise = 0.036; c=1.0: K=not-reached; c=1.5: K=98; c=2.0: K=98; c=3.0: K=98  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=not-reached; c=1.5: K=98; c=2.0: K=98; c=3.0: K=98
    P1+P2 reading on ρ_off (decisions 8, 9, 12): ρ_noise,off = 1.010, ρ_dry,off = 0.963; c=1.0: K=at-noise; c=1.5: K=at-noise; c=2.0: K=at-noise; c=3.0: K=at-noise
- mode G, σ_g = 10.0 µE_h per unit q: ρ_noise = 0.107; c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96  | with the floor: c=1.0: K=96; c=1.5: K=96; c=2.0: K=96; c=3.0: K=96
- mode E, σ_E = 20.0 µE_h: ρ_noise = 0.071; c=1.0: K=98; c=1.5: K=98; c=2.0: K=98; c=3.0: K=98  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=98; c=1.5: K=98; c=2.0: K=98; c=3.0: K=98
    P1+P2 reading on ρ_off (decisions 8, 9, 12): ρ_noise,off = 2.020, ρ_dry,off = 0.963; c=1.0: K=at-noise; c=1.5: K=at-noise; c=2.0: K=at-noise; c=3.0: K=at-noise
- mode G, σ_g = 20.0 µE_h per unit q: ρ_noise = 0.214; c=1.0: K=96; c=1.5: K=96; c=2.0: K=88; c=3.0: K=at-noise  | with the floor: c=1.0: K=96; c=1.5: K=96; c=2.0: K=88; c=3.0: K=at-noise

## Deviations from the frozen form (this version)
- low-rank term of the structural prior not implemented (banded l1 only)
- completion patterns are random sparse mode combinations, not O1NumHess

Printed by probes/dryrun_dft_delta_recovery.py. Both arms are DFT; no local-CC number exists here.