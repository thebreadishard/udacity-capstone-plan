# Pre-registration E7 — the couplings in local coordinates, not in the mode basis (written 23 September 2026, 10:3x, before either test ran; the user: "Goed idee, onthoud het, schrijf T1 en T2 uit als pre-registratie en draai zodra het kan")

## What we want to know

E6 (`PreRegistration_2026-09-19_E6_Learning_Curve_in_Data.md`, outcome of today) showed that the within-family couplings K_ij of the
correction matrix (K = Lᵀ ΔH_mw L / (2√(ω_i ω_j)), ΔH = H(ωB97X) − H(B3LYP) at the B3LYP/6-31G* geometry) are not learned by any model
on mode tokens, and that four times the data moves nothing (coupling ratio to the zero rule 1.00 / 1.9 / 1.3, slopes −0.04…0.00). The
diagnosis of today's proposal: (1) every mode token is a square of the mode vector, hence invariant under L_i → −L_i, while K_ij is odd
under it — the MSE optimum of any such model is 0; (2) the normal-mode transform smears a sparse, local force-constant correction over all
pairs; (3) irreps are invisible. Stakes measured on the release of 224 molecules: the couplings move corrected frequencies by RMS 3.4 cm⁻¹
(max 66) but change the composition of 10 % of the modes by more than 25 %; only 13 % of Σ K_ij² sits in pairs closer than 30 cm⁻¹.

Two tests decide whether the representation, not the data, is the obstacle.

## T1 — the sign test

The module-05 ΔH block model (M2 of E6: `deltah_model.DeltaHModel`, block loss, 30 epochs, batches of 8, seeds 0 1 2) is trained on the
target with the **absolute value of the off-diagonal elements** (diagonal unchanged) and read on the E6 hold-outs (a) and (b), molecules
with an imaginary mode excluded (today's addition to E6), at n = 45 and the full pool. Read-out: ring-in-plane coupling RMS on |K| against
two rules that need no learning — zero, and the best constant (mean |K| of the training pairs, which beats zero on a non-negative target).

- **Prediction:** on |K| the model's ring coupling RMS falls below the constant rule (ratio ≤ 0.85) while the same model on signed K stays at
  1.00 (E6). **Win** = ratio to the constant rule ≤ 0.85 on ring-in-plane at the full pool. **Lose** = ratio ≥ 0.95: the magnitudes are not
  learnable from the tokens either, and the sign is not the (only) obstacle.

## T2 — the chemical null hypothesis: SQM scale factors carry the couplings

Redundant primitive internal coordinates (bonds, angles, dihedrals, out-of-planes; geomeTRIC 1.1.1's `PrimitiveInternalCoordinates`) are
built from each B3LYP geometry. Both Cartesian Hessians (`H_projected`) are transformed to internal force constants F = B⁺ᵀ H B⁺ (the
gradient term Σ g_k ∂B_k/∂x of the high level is **not** available — the corpus stores no ωB97X gradient — and is absorbed into the residual;
this is decision 48's geometry term and is noted as the first refinement). Every primitive gets a **type**: bonds by element pair and ring
membership; angles by centre element, sorted neighbour elements and ring membership; dihedrals by the central bond's elements and ring
membership; out-of-planes by centre element. One scale factor s_t per type is fitted on the training molecules by least squares over all
elements of the internal force-constant matrix, F_high,ij ≈ √(s_i s_j) F_low,ij (Pulay's SQM prescription; start from the diagonal
ratios; types seen fewer than 5 times keep s = 1). Prediction for a held-out molecule: ΔF = (√(s_i s_j) − 1) F_low, ΔH_pred = Bᵀ ΔF B,
projected onto the B3LYP modes → K_pred, then the E6 read-outs (diagonal RMS per family; ring coupling RMS and its ratio to the zero rule;
ring block against the median rule; hold-out (b) for transfer to unseen cores). Training pool and hold-outs exactly as in E6 (imaginary-mode
molecules excluded); sizes 45 and the full pool (the number of parameters is ≈ 30, so a curve is not the point).

- **Prediction:** ring-in-plane coupling ratio to the zero rule **0.6–0.8** at the full pool — the first crossing under 1.0 by any method —
  and CH-out-of-plane ≤ 0.8; diagonal 8–12 cm⁻¹ on ring-in-plane (worse than the Transformer's 5.3 with 136 k parameters, but with ~30).
- **Win:** ring-in-plane coupling ratio ≤ 0.8 on hold-out (a) and ≤ 0.9 on (b). **Lose:** ratio ≥ 1.0 on (a): the couplings are not
  transferable per coordinate type even in local coordinates — the proposal is falsified as stated and the next question is why.
- **Between** (0.8 < ratio < 1.0): the representation helps but per-type constants are too coarse → rung B (per-environment factors and
  pair terms) is the next test, pre-registered separately.

## Read-out that both tests share, basis-free

Besides the K read-outs: RMS of the corrected frequencies after diagonalising Ω² + 2√(ω_i ω_j) K_pred against the same with K_true, and
the Duschinsky overlap of the corrected eigenvectors. These are what the pipeline consumes; K_ij is an intermediate.

## Cost and safety

Both tests run on the CCX53 (`/root/m05run/05_support_predictor`, env `m05` with torch 2.14 and geomeTRIC 1.1.1); T1 ≈ 15 min, T2 minutes;
nothing on the laptop (the anchor run is not touched). Scripts `m05/e7_t1_sign_test.py`, `m05/e7_t2_sqm.py`; results
`out/E7_T1_*.{json,md}`, `out/E7_T2_*.{json,md}`; outcome sections appended here.

## What this does not decide

Rungs B and C of the proposal (neural SQM; equivariant Δ-Hessian with displaced-gradient labels and Hessian-QM9 pretraining); the
coupled-cluster correction (still two real points); anything about intensities beyond the overlap read-out.

## Outcome T2 — 23 September 2026, 10:4x: BETWEEN, at the lose end (ring coupling ratio 0.97 on (a), 0.95 on (b))

Run: `m05/e7_t2_sqm.py` on the CCX53 (9 s); results `out/E7_T2_2026-09-23.{json,md,log}`. 224 molecules; 50 coordinate types fitted at
n = 175 (of 53 seen); Bᵀ F B reproduces every Cartesian Hessian to 3e-15 (median). The Gauss–Newton fit of the scale factors
converged at once (fit RMS 6.62e-04 → 6.60e-04 a.u.; the diagonal-ratio start is already the optimum). Scale factors are all
close to one and chemically sensible (ring C–C bonds 1.028, C–H 1.026, ring C–C–C angles 1.024, ring dihedrals 1.066,
out-of-planes 1.069): ωB97X stiffens everything by 1–9 %, torsions and out-of-planes most.

| hold-out | model | diag CH-stretch | CH-oop | ring-ip | other | ring coupling ratio | ring block / median | corrected ω RMS (zero rule) | overlap median |
|---|---|---|---|---|---|---|---|---|---|
| (a) | sqm_diag_only | 2.58 | 9.51 | 17.56 | 9.02 | **1.00** | 5.54 / 4.12 | 12.23 (24.31) | 0.997 |
| (a) | sqm | 2.58 | 9.51 | 17.56 | 9.02 | **0.97** | 5.54 / 4.12 | 12.21 (24.31) | 0.998 |
| (b) | sqm_diag_only | 4.38 | 8.14 | 13.41 | 14.44 | **1.00** | 3.63 / 1.14 | 10.14 (23.09) | 0.986 |
| (b) | sqm | 4.38 | 8.14 | 13.41 | 14.44 | **0.95** | 3.63 / 1.14 | 10.09 (23.09) | 0.989 |

**Against the predictions.** Predicted: ring coupling ratio 0.6–0.8 and ring diagonal 8–12 cm⁻¹. Measured: ratio 0.97 / 0.95 — the first
reading under 1.0 by any method, but by a hair — and ring diagonal 17.6 on (a), barely better than the family-median rule (18.4) and far from
the Transformer's 11.5 (E6) or 5.3 (module split). The SQM form explains only 28 % of the Cartesian ΔH RMS on (a) (30 % on (b)); it halves the
corrected-frequency error (24.3 → 12.2 cm⁻¹) mostly through the C–H stretches. By the registered rule this is **between**, close to lose:
per-type constants in redundant primitives do not carry the couplings of this correction.

**What it does and does not falsify.** It does not settle the diagnosis of the mode-basis failure (that is T1's job); it says that the coarsest local
representation — one multiplier per coordinate type, fitted on force constants in atomic units — is not enough. Two caveats belong to the method,
not the idea, and are the first post-hoc checks (labelled as such, not pre-registered): (1) in *redundant* primitives F = B⁺ᵀ H B⁺ is one of many
internal representations, and scaling the minimum-norm one is not what Pulay's SQM does in non-redundant natural coordinates; (2) the fit weights
bond force constants (≈ 0.5 a.u.) hundreds of times above bends and torsions, whereas the read-out lives in cm⁻¹ per mode. The post-hoc script
`m05/e7_t2_posthoc.py` measures (i) the upper bound of the SQM form — scale factors fitted on each held-out molecule itself — and (ii) a fit of the
same 50 factors in K-space (cm⁻¹, all families weighted alike). If (i) is also weak, the multiplicative form is the limit and rung B needs
additive per-pair terms; if (ii) is much better than T2, the objective was the problem.
