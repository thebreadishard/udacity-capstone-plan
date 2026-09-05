# Dry run — benzene — 2026-09-05 13:35 — machine Asus18, 8 threads, psi4 1.11

## Timing (B2 laptop, this run)
- optimize_s: 0.18 min
- hessian_b3lyp_s: 6.47 min
- hessian_bhhlyp_s: 7.57 min

## Modes: M = 30; families: CC-stretch×6, CH-ip-bend×7, CH-oop×9, CH-stretch×6, ring-ip×2
- totally symmetric mode used by the Q6 scan: index 12 (1020 cm⁻¹)

## Deck: hash 0158e1306bfdf3c6…, 334 ± pairs in K (30 single-mode + 304 off-diagonal), 61 held out (f_h = 0.2), q_s = 1.0, q₂ = 0.5; 729 energies evaluated per arm (gradients too)

## Reference constant c₀ = 0.196 ± 0.257 µE_h (two-amplitude read over all modes)
## Δ₁ (∂ΔE/∂q at the B3LYP geometry, dimensionless q), |Δ₁| max = 2724.1 µE_h per unit q

## The w rule: w = 25.0 cm⁻¹ (λ = 1e-06); table:
- w = 25: hold-out ρ = 0.005, worst family RMS = 0.43 cm⁻¹
- w = 50: hold-out ρ = 0.005, worst family RMS = 0.43 cm⁻¹
- w = 100: hold-out ρ = 0.005, worst family RMS = 0.43 cm⁻¹
- w = 200: hold-out ρ = 0.006, worst family RMS = 0.42 cm⁻¹
- w = 400: hold-out ρ = 0.077, worst family RMS = 2.32 cm⁻¹

## Mode E: K at declared ρ = 0.1: 62 energies (K_off = 2); ρ with all training pairs = 0.005; RMS held-out response = 215.02 µE_h
- recovered-vs-direct RMS frequency error per family (cm⁻¹), full recovery (re-diagonalised) / diagonal-only (CMA-0):
  - CC-stretch (n=6): full 0.36 / diag-only 6.90
  - CH-ip-bend (n=7): full 0.43 / diag-only 7.47
  - CH-oop (n=9): full 0.21 / diag-only 0.62
  - CH-stretch (n=6): full 0.11 / diag-only 0.04
  - ring-ip (n=2): full 0.31 / diag-only 0.37
- ρ(n) curve (energies, ρ): (62,0.024), (102,0.019), (142,0.021), (182,0.021), (222,0.028), (262,0.041), (302,0.036), (342,0.034), (382,0.032), (422,0.031), (462,0.007), (502,0.005), (542,0.005)
- **model floor** ρ_dry = 0.0049 (noiseless responses, all training pairs): the quartic contamination of the quadratic model at q_s = 1.0
- **off-diagonal view**: RMS of the off-diagonal part of the held-out responses = 5.16 µE_h (vs 215.02 raw); ρ_off(n) curve: (62,1.000), (102,0.771), (142,0.878), (182,0.886), (222,1.170), (262,1.705), (302,1.498), (342,1.421), (382,1.315), (422,1.303), (462,0.297), (502,0.212), (542,0.205); K at declared ρ_off = None; **K_off at ρ_off ≤ 0.3 = 388 energies**
- **diagonal-anchored recovery** (diagonal from the single block, off-diagonals fitted to the residual): ρ_off = 0.221; family RMS (cm⁻¹): CC-stretch 0.41, CH-ip-bend 0.45, CH-oop 0.22, CH-stretch 0.05, ring-ip 0.27
- **quartic-corrected, diagonal-anchored recovery** (Δ_ii and Δ₄,iiii from the two amplitudes; Σ Δ₄ a⁴/24 subtracted): off-diagonal RMS after subtraction = 5.18 µE_h; ρ_off = 0.187; family RMS (cm⁻¹): CC-stretch 0.20, CH-ip-bend 0.45, CH-oop 0.20, CH-stretch 0.07, ring-ip 0.21; two-amplitude diagonal alone: CC-stretch 7.26, CH-ip-bend 7.41, CH-oop 0.66, CH-stretch 0.07, ring-ip 0.32

## Mode G: K at declared ρ: 60 gradients; model floor ρ_dry(G) = 0.0025; family error (full):
  - CC-stretch: 0.30 cm⁻¹
  - CH-ip-bend: 0.16 cm⁻¹
  - CH-oop: 0.21 cm⁻¹
  - CH-stretch: 0.03 cm⁻¹
  - ring-ip: 0.09 cm⁻¹

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
- mode E, σ_E = 0.5 µE_h: ρ_noise = 0.002; c=1.0: K=not-reached; c=1.5: K=not-reached; c=2.0: K=not-reached; c=3.0: K=496  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=490; c=1.5: K=490; c=2.0: K=490; c=3.0: K=490
- mode G, σ_g = 0.5 µE_h per unit q: ρ_noise = 0.004; c=1.0: K=96; c=1.5: K=64; c=2.0: K=64; c=3.0: K=64  | with the floor: c=1.0: K=96; c=1.5: K=64; c=2.0: K=64; c=3.0: K=64
- mode E, σ_E = 1.0 µE_h: ρ_noise = 0.003; c=1.0: K=not-reached; c=1.5: K=538; c=2.0: K=496; c=3.0: K=448  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=498; c=1.5: K=498; c=2.0: K=496; c=3.0: K=448
- mode G, σ_g = 1.0 µE_h per unit q: ρ_noise = 0.008; c=1.0: K=64; c=1.5: K=64; c=2.0: K=64; c=3.0: K=64  | with the floor: c=1.0: K=64; c=1.5: K=64; c=2.0: K=64; c=3.0: K=64
- mode E, σ_E = 2.0 µE_h: ρ_noise = 0.007; c=1.0: K=not-reached; c=1.5: K=496; c=2.0: K=430; c=3.0: K=76  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=not-reached; c=1.5: K=496; c=2.0: K=430; c=3.0: K=76
- mode G, σ_g = 2.0 µE_h per unit q: ρ_noise = 0.016; c=1.0: K=64; c=1.5: K=64; c=2.0: K=64; c=3.0: K=64  | with the floor: c=1.0: K=64; c=1.5: K=64; c=2.0: K=64; c=3.0: K=64
- mode E, σ_E = 5.0 µE_h: ρ_noise = 0.016; c=1.0: K=not-reached; c=1.5: K=76; c=2.0: K=62; c=3.0: K=62  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=not-reached; c=1.5: K=76; c=2.0: K=62; c=3.0: K=62
- mode G, σ_g = 5.0 µE_h per unit q: ρ_noise = 0.039; c=1.0: K=64; c=1.5: K=64; c=2.0: K=64; c=3.0: K=64  | with the floor: c=1.0: K=64; c=1.5: K=64; c=2.0: K=64; c=3.0: K=64
- mode E, σ_E = 10.0 µE_h: ρ_noise = 0.033; c=1.0: K=76; c=1.5: K=62; c=2.0: K=62; c=3.0: K=62  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=76; c=1.5: K=62; c=2.0: K=62; c=3.0: K=62
- mode G, σ_g = 10.0 µE_h per unit q: ρ_noise = 0.078; c=1.0: K=64; c=1.5: K=64; c=2.0: K=64; c=3.0: K=56  | with the floor: c=1.0: K=64; c=1.5: K=64; c=2.0: K=64; c=3.0: K=56
- mode E, σ_E = 20.0 µE_h: ρ_noise = 0.066; c=1.0: K=62; c=1.5: K=62; c=2.0: K=62; c=3.0: K=62  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): c=1.0: K=62; c=1.5: K=62; c=2.0: K=62; c=3.0: K=62
- mode G, σ_g = 20.0 µE_h per unit q: ρ_noise = 0.156; c=1.0: K=64; c=1.5: K=56; c=2.0: K=56; c=3.0: K=56  | with the floor: c=1.0: K=64; c=1.5: K=56; c=2.0: K=56; c=3.0: K=56

## Deviations from the frozen form (this version)
- low-rank term of the structural prior not implemented (banded l1 only)
- completion patterns are random sparse mode combinations, not O1NumHess

Printed by probes/dryrun_dft_delta_recovery.py. Both arms are DFT; no local-CC number exists here.