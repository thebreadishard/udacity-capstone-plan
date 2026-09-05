# Dry run — benzene — 2026-09-05 10:57 — machine Asus18, 8 threads, psi4 1.11 — QUICK (reduced deck)

## Timing (B2 laptop, this run)
- optimize_s: 0.18 min
- hessian_b3lyp_s: 6.47 min
- hessian_bhhlyp_s: 7.57 min

## Modes: M = 30; families: CC-stretch×6, CH-ip-bend×7, CH-oop×9, CH-stretch×6, ring-ip×2
- totally symmetric mode used by the Q6 scan: index 12 (1020 cm⁻¹)

## Deck: hash 372dac7254fcdca6…, 126 ± pairs in K (30 single-mode + 96 off-diagonal), 19 held out (f_h = 0.2), q_s = 1.0, q₂ = 0.5; 313 energies evaluated per arm (gradients too)

## Reference constant c₀ = 0.196 ± 0.257 µE_h (two-amplitude read over all modes)
## Δ₁ (∂ΔE/∂q at the B3LYP geometry, dimensionless q), |Δ₁| max = 2724.1 µE_h per unit q

## The w rule: w = 50.0 cm⁻¹ (λ = 1e-07); table:
- w = 25: hold-out ρ = 0.014, worst family RMS = 7.43 cm⁻¹
- w = 50: hold-out ρ = 0.014, worst family RMS = 7.43 cm⁻¹
- w = 100: hold-out ρ = 0.005, worst family RMS = 7.43 cm⁻¹
- w = 200: hold-out ρ = 0.006, worst family RMS = 7.43 cm⁻¹
- w = 400: hold-out ρ = 0.012, worst family RMS = 7.43 cm⁻¹

## Mode E: K at declared ρ = 0.1: 62 energies (K_off = 2); ρ with all training pairs = 0.014; RMS held-out response = 209.54 µE_h
- recovered-vs-direct RMS frequency error per family (cm⁻¹), full recovery (re-diagonalised) / diagonal-only (CMA-0):
  - CC-stretch (n=6): full 6.90 / diag-only 6.90
  - CH-ip-bend (n=7): full 7.43 / diag-only 7.47
  - CH-oop (n=9): full 0.22 / diag-only 0.62
  - CH-stretch (n=6): full 0.05 / diag-only 0.04
  - ring-ip (n=2): full 0.37 / diag-only 0.37
- ρ(n) curve (energies, ρ): (62,0.016), (74,0.016), (86,0.016), (98,0.016), (110,0.016), (122,0.016), (134,0.016), (146,0.015), (158,0.015), (170,0.016), (182,0.014), (194,0.014), (206,0.015)
- **model floor** ρ_dry = 0.0143 (noiseless responses, all training pairs): the quartic contamination of the quadratic model at q_s = 1.0
- **off-diagonal view**: RMS of the off-diagonal part of the held-out responses = 3.31 µE_h (vs 209.54 raw); ρ_off(n) curve: (62,0.999), (74,1.000), (86,1.001), (98,0.997), (110,1.015), (122,1.022), (134,1.024), (146,0.944), (158,0.944), (170,0.996), (182,0.894), (194,0.893), (206,0.937); K at declared ρ_off = None
- **diagonal-anchored recovery** (diagonal from the single block, off-diagonals fitted to the residual): ρ_off = 0.910; family RMS (cm⁻¹): CC-stretch 6.90, CH-ip-bend 7.44, CH-oop 0.22, CH-stretch 0.04, ring-ip 0.38
- **quartic-corrected, diagonal-anchored recovery** (Δ_ii and Δ₄,iiii from the two amplitudes; Σ Δ₄ a⁴/24 subtracted): off-diagonal RMS after subtraction = 3.29 µE_h; ρ_off = 0.900; family RMS (cm⁻¹): CC-stretch 7.26, CH-ip-bend 7.40, CH-oop 0.18, CH-stretch 0.07, ring-ip 0.33; two-amplitude diagonal alone: CC-stretch 7.26, CH-ip-bend 7.41, CH-oop 0.66, CH-stretch 0.07, ring-ip 0.32

## Mode G: K at declared ρ: 60 gradients; family error (full):
  - CC-stretch: 0.47 cm⁻¹
  - CH-ip-bend: 0.17 cm⁻¹
  - CH-oop: 0.27 cm⁻¹
  - CH-stretch: 0.05 cm⁻¹
  - ring-ip: 0.11 cm⁻¹

## Off-diagonal blocks flagged large in the direct Δ₂ (|Δ_ij| > 0.2 × RMS diagonal); (i, j, ratio, ω_i, ω_j):
- (15, 18, +0.95, 1186, 1357)
- (17, 22, -0.41, 1208, 1656)
- (16, 23, +0.40, 1208, 1656)
- (13, 20, +0.34, 1069, 1531)
- (14, 21, +0.34, 1069, 1532)

## DFT-arm noise floor (nine-point degree-4 estimator): pooled σ_E = 0.147 µE_h (ν = 16)
- CC-stretch (1532 cm⁻¹): σ_E = 0.229 µE_h, max |studentised residual| = 1.49
- CH-stretch (3199 cm⁻¹): σ_E = 0.064 µE_h, max |studentised residual| = 1.14
- CH-oop (865 cm⁻¹): σ_E = 0.002 µE_h, max |studentised residual| = 1.48
- totally-symmetric (1020 cm⁻¹): σ_E = 0.174 µE_h, max |studentised residual| = 1.16

## Noise-injection column (K in energies or gradients at ρ* = c·ρ_noise; 'at-noise' if c·ρ_noise ≥ 0.5)
- mode E, σ_E = 1.0 µE_h: ρ_noise = 0.003; c=1.0: K=not-reached; c=1.5: K=not-reached; c=2.0: K=not-reached; c=3.0: K=not-reached  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=62; c=1.5: K=62; c=2.0: K=62; c=3.0: K=62
- mode G, σ_g = 1.0 µE_h/bohr: ρ_noise = 0.008; c=1.0: K=not-reached; c=1.5: K=not-reached; c=2.0: K=not-reached; c=3.0: K=not-reached
- mode E, σ_E = 5.0 µE_h: ρ_noise = 0.017; c=1.0: K=not-reached; c=1.5: K=62; c=2.0: K=62; c=3.0: K=62  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=not-reached; c=1.5: K=62; c=2.0: K=62; c=3.0: K=62
- mode G, σ_g = 5.0 µE_h/bohr: ρ_noise = 0.041; c=1.0: K=not-reached; c=1.5: K=not-reached; c=2.0: K=not-reached; c=3.0: K=not-reached

## Deviations from the frozen form (this version)
- low-rank term of the structural prior not implemented (banded l1 only)
- completion patterns are random sparse mode combinations, not O1NumHess

Printed by probes/dryrun_dft_delta_recovery.py. Both arms are DFT; no local-CC number exists here.