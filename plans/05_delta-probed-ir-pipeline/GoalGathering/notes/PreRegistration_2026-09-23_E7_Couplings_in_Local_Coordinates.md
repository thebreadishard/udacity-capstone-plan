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

**Post-hoc (i)–(iii), 10:5x — not pre-registered; `m05/e7_t2_posthoc.py`, `out/E7_T2_posthoc_2026-09-23.*`.**

| hold-out | variant | ring diag | ring coupling ratio | corrected ω RMS (zero rule) | ΔH residual ratio |
|---|---|---|---|---|---|
| (a) | (i) own-fit ceiling of the multiplicative form | 17.47 | **0.93** | 12.15 (24.87) | 0.71 |
| (a) | (ii) per-type factors, K-space objective | 17.10 | **0.97** | 11.37 (24.31) | 0.73 |
| (a) | (iii) + additive diagonal per type, K-space | 14.31 | **0.93** | 10.54 (24.31) | 0.62 |
| (b) | (i) own-fit ceiling of the multiplicative form | 12.97 | **0.94** | 9.61 (23.10) | 0.71 |
| (b) | (ii) per-type factors, K-space objective | 12.55 | **0.93** | 9.04 (23.09) | 0.70 |
| (b) | (iii) + additive diagonal per type, K-space | 9.85 | **0.90** | 7.36 (23.09) | 0.66 |

Reading. (i) Even with the scale factors fitted on the held-out molecule itself — no transfer at all — the multiplicative form leaves
71 % of the Cartesian ΔH RMS and a ring coupling ratio of 0.93: **the SQM form is the limit, not the transfer.** (ii) The K-space
objective changes nothing (0.97 / 0.93): the a.u. weighting was not the problem. (iii) One additive constant per coordinate type
on the diagonal helps the diagonal (ring 14.3 / 9.9) and the couplings a little (0.93 / 0.90) but still leaves 62 % of ΔH.
So the ωB97X − B3LYP correction is not, to first approximation, a change of the *diagonal* force constants of the primitives: a large part
of it sits in the *interaction* constants between internals — chemically, in how conjugated bonds stiffen each other (bond-alternation /
Kekulé interaction constants, where B3LYP's delocalisation error lives). That is where the mode-basis couplings come from, and it is
exactly what a per-coordinate representation, multiplicative or additive, cannot express. The capacity ceilings of local representations
with pair terms (post-hoc (iv)–(vi): diagonal only; pairs sharing an atom; plus ring bond–bond pairs; each fitted per molecule, no transfer)
are being measured to size rung B (`m05/e7_t2_ceilings.py`); the result is appended when in.

## Outcome T1 — 23 September 2026, 11:3x: LOSE on hold-out (a) by the registered threshold (ratio to the constant rule 0.96); 0.86 on hold-out (b)

Run: `m05/e7_t1_sign_test.py` on the CCX53 (32 threads, 656 s); results `out/E7_T1_2026-09-23.{json,md,log}`. 224 molecules, hold-out (a) 10, (b) 39,
pool 175, seeds [0, 1, 2], 30 epochs; the constant rule is the mean |K| of the training ring pairs (c = 2.75 cm⁻¹).

| n | hold-out | |K| model RMS | zero rule | constant rule | ratio to zero | ratio to constant | signed control (E6 M2) | ring diag |K| / signed |
|---|---|---|---|---|---|---|---|---|
| 45 | (a) | 5.30 | 5.90 | 5.46 | 0.90 | **0.97** | 1.00 | 13.76 / 14.21 |
| 45 | (b) | 2.55 | 3.74 | 2.89 | 0.68 | **0.88** | 1.00 | 7.52 / 7.98 |
| 175 | (a) | 5.26 | 5.90 | 5.46 | 0.89 | **0.96** | 1.00 | 12.50 / 12.74 |
| 175 | (b) | 2.49 | 3.74 | 2.89 | 0.67 | **0.86** | 1.00 | 6.14 / 6.51 |

**Against the prediction.** Predicted: ratio to the constant rule ≤ 0.85 on (a). Measured: 0.96 on (a) — **lose** by the registered threshold (≥ 0.95) —
and 0.86 on (b), which would have counted as a win. The signed control reproduces E6 exactly (1.00 at both n). So the sign is
*an* obstacle (removing it moves the model off zero everywhere: 0.89 to the zero rule on (a), 0.67 on (b)) but not the whole story: on the
ten layer-A molecules the magnitudes carry almost no token-predictable structure beyond their mean, on the 39 scaffold molecules a modest
amount. Read together with T2 and its post-hoc checks, the two tests point the same way: the couplings are not a per-mode or per-coordinate
property at all — they come from the interaction constants between internals, which neither mode tokens nor per-coordinate scale factors
see. The representation has to carry pairs of local coordinates (rung B with pair terms) or the full local Hessian (rung C). The diagonal is
unaffected by the target change (12.5 vs 12.7 on ring), as it should be.

**Post-hoc (iv)–(ix), 11:5x — where ΔH lives; `m05/e7_t2_ceilings.py`, `out/E7_T2_ceilings_2026-09-23.*`.** Per held-out molecule, no transfer.
(iv)–(vi) are least-squares fits of ΔF on a sparsity pattern; (v)/(vi) have more parameters than Cartesian elements and prove nothing (residual 0.07 by
construction) — they are kept only as the record. (vii)–(ix) are parameter-free: the minimum-norm internal ΔF = B⁺ᵀ ΔH B⁺, zeroed outside the pattern,
transformed back — the fair measure of how much of ΔH sits on each pattern.

| hold-out | pattern (projection, no fit) | ΔH residual ratio | ring diag | ring coupling ratio | corrected ω RMS (zero rule) |
|---|---|---|---|---|---|
| (a) | diagonal of the primitives only | 0.77 | 19.54 | **0.98** | 13.36 (24.87) |
| (a) | + pairs sharing an atom | 0.61 | 15.60 | **0.78** | 8.21 (24.87) |
| (a) | + bond–bond pairs in the same ring | 0.27 | 8.30 | **0.38** | 4.98 (24.87) |
| (b) | diagonal of the primitives only | 0.73 | 14.89 | **0.96** | 10.57 (23.10) |
| (b) | + pairs sharing an atom | 0.55 | 10.96 | **0.70** | 6.48 (23.10) |
| (b) | + bond–bond pairs in the same ring | 0.19 | 2.62 | **0.29** | 2.11 (23.10) |

Reading. The diagonal of the primitives carries almost nothing of the couplings (ratio 0.98); pairs of internals sharing an atom carry
about 40 %; adding the **bond–bond interaction constants inside a ring** (bonds one, two and three bonds apart — the ortho/meta/para
interaction constants of Pulay's benzene force field) takes the residual to 0.27 / 0.19, the ring coupling ratio to
0.38 / 0.29 and the corrected-frequency error to 5.0 / 2.1 cm⁻¹ (zero rule 24 / 23). **The ωB97X − B3LYP correction is, to three quarters, a
change of the ring bond–bond interaction constants plus atom-sharing pair terms — a local, transferable object with a chemical name.** This
fixes the representation for rung B.

## Rung B, pre-registered 11:5x (written before the run; the user, 11:1x: "Doe wat nodig is om aan de supervisor aan te tonen dat ons idee werkt, dat het netwerk alles kan leren wat het nodig heeft")

**Target.** The minimum-norm internal correction ΔF = B⁺ᵀ ΔH B⁺ on the pattern of post-hoc (ix): diagonal, pairs sharing an atom, bond–bond
pairs in the same ring. Every element is a rotation-invariant, sign-consistent number in atomic units (geomeTRIC builds the primitives
deterministically from the geometry), so the sign and basis problems of the mode basis do not exist here; a molecule contributes thousands
of labelled pairs instead of one matrix.

**Features per element (i, j).** For each primitive: class (bond / angle / dihedral / out-of-plane / linear), elements involved, ring membership,
its value (length or angle), F_low,kk, the environment classes of its atoms (the 12 atom classes of the second-pass descriptors) and their
ring counts. For the pair: the two primitives' features in canonical order, the number of shared atoms, same-ring flag, ring-path distance for
bond–bond pairs (1 = adjacent, 2, 3 = across), F_low,ij and F_low,ii F_low,jj.

**Models.** (B1) a network: MLP 2 × 128 GELU on standardised features, targets scaled per class, AdamW, 3 seeds; (B2) gradient-boosted trees
(sklearn HistGradientBoosting) as the non-neural check. Prediction: ΔH_pred = Bᵀ ΔF_pred B, mass-weighted, projected onto the B3LYP modes →
K_pred; E6 read-outs plus the basis-free ones. Same hold-outs (a) and (b), same pool, imaginary-mode molecules excluded; **sizes 45, 100, 175**
(three seeds) so that the curve itself is an exhibit.

**Predictions.** Ring coupling ratio ≤ 0.6 on (a) and (b) at 175 (the projection ceiling is 0.38 / 0.29); corrected-frequency RMS ≤ 8 cm⁻¹ against
24 for the zero rule; ring diagonal ≤ 10 cm⁻¹; and — the point for the supervisor — the coupling ratio *descends with data* (slope steeper than
−0.15 over 45 → 175), where every mode-basis model was flat. **Win:** ratio ≤ 0.6 on both hold-outs at 175 and a negative slope. **Lose:** ratio
≥ 0.9 at 175 → the pairwise local target is still not learnable from these features and rung C (equivariant Δ-Hessian) is the next test.
**Between:** 0.6–0.9 → more expressive features or rung C, decided by whether the curve descends.

Script `m05/e7_rungB_pairs.py`; results `out/E7_rungB_2026-09-23.*`; CCX53 only.

## Outcome rung B — 23 September 2026, 12:0x: BETWEEN on hold-out (a) (ratio 0.81), WIN-level on hold-out (b) (ratio 0.47); the first model that learns the couplings

Run: `m05/e7_rungB_pairs.py` on the CCX53 (32 threads, 251 s); results `out/E7_rungB_2026-09-23.{json,md,log}`. 224 molecules; 66 pair features;
pool 175; sizes [45, 100, 175]; MLP seeds [0, 1, 2], 60 epochs; GBT 400 iterations. RMS in cm⁻¹; MLP = mean over seeds.

| n | hold-out | model | diag ring-ip | diag CH-oop | ring coupling RMS / zero | **ratio** | ring block / median | corrected ω RMS (zero) | overlap | ΔH residual |
|---|---|---|---|---|---|---|---|---|---|---|
| 45 | (a) | B1 MLP | 11.63 | 9.97 | 4.83 / 5.90 | **0.82** | 5.70 / 4.14 | 9.96 (24.31) | 0.998 | 0.43 |
| 45 | (a) | B2 GBT | 11.46 | 6.99 | 4.84 / 5.90 | **0.82** | 5.39 / 4.14 | 9.63 (24.31) | 0.998 | 0.45 |
| 45 | (b) | B1 MLP | 6.04 | 10.64 | 1.91 / 3.74 | **0.51** | 1.35 / 1.09 | 5.99 (23.09) | 0.992 | 0.34 |
| 45 | (b) | B2 GBT | 5.96 | 7.78 | 1.81 / 3.74 | **0.48** | 1.71 / 1.09 | 6.32 (23.09) | 0.994 | 0.35 |
| 100 | (a) | B1 MLP | 11.22 | 6.79 | 4.82 / 5.90 | **0.82** | 5.16 / 4.12 | 9.47 (24.31) | 0.997 | 0.42 |
| 100 | (a) | B2 GBT | 11.70 | 7.75 | 4.84 / 5.90 | **0.82** | 5.55 / 4.12 | 9.83 (24.31) | 0.998 | 0.45 |
| 100 | (b) | B1 MLP | 4.96 | 7.24 | 1.87 / 3.74 | **0.50** | 1.17 / 1.16 | 5.40 (23.09) | 0.992 | 0.34 |
| 100 | (b) | B2 GBT | 6.25 | 8.55 | 1.83 / 3.74 | **0.49** | 2.17 / 1.16 | 6.73 (23.09) | 0.994 | 0.36 |
| 175 | (a) | B1 MLP | 11.23 | 5.19 | 4.80 / 5.90 | **0.81** | 5.18 / 4.12 | 9.34 (24.31) | 0.998 | 0.41 |
| 175 | (a) | B2 GBT | 11.76 | 8.74 | 4.85 / 5.90 | **0.82** | 5.70 / 4.12 | 9.99 (24.31) | 0.998 | 0.46 |
| 175 | (b) | B1 MLP | 4.83 | 6.01 | 1.76 / 3.74 | **0.47** | 1.09 / 1.14 | 5.14 (23.09) | 0.993 | 0.31 |
| 175 | (b) | B2 GBT | 6.44 | 9.65 | 1.84 / 3.74 | **0.49** | 2.33 / 1.14 | 6.70 (23.09) | 0.994 | 0.37 |

MLP ring coupling ratio per seed at 175: (a) 0.81, 0.82, 0.81; (b) 0.47, 0.46, 0.49. Slopes of the ratio over [45, 100, 175]: (a) -0.01, (b) -0.06.

**Against the predictions.** Predicted ≤ 0.6 on both hold-outs and a descending curve. Measured: **(b), the 39 molecules of two cores never seen in
training, ratio 0.47** (zero-rule 1.00 for every mode-basis model of E6; projection ceiling of the pattern 0.29), ring diagonal 4.8 cm⁻¹ (the module-05
Transformer's best was 5.3 on its own split, without couplings), ring block 1.09 against the median rule's 1.14 — the first model to beat that rule — and the
corrected-frequency error 23.1 → 5.1 cm⁻¹ with a Duschinsky overlap of 0.993. **(a), the ten layer-A molecules, ratio 0.81**: better than any
mode-basis model by a wide margin, but above 0.6, and flat over 45 → 175 (slope -0.01) while (b) descends a little (-0.06). By the registered rule:
**between on (a), win-level on (b)**. The neural model and the trees agree to two decimals on the ratio at every n, so the number is a property
of the representation, not of one learner.

**Reading.** In the local pairwise representation the couplings are learned — from the same 175 molecules on which every mode-basis model sat
at the zero rule at every data size. Cores transfer (hold-out (b) is the harder test in chemistry and the easier one in the numbers). The
layer-A hold-out is a different population (small mono- and bicyclic aromatics with heteroatoms, the corpus is 78 % three- and four-ring
substituted cores); its flat 0.82 says that what is missing there is not data of the same kind but coverage of its chemistry or features that
see it — the per-molecule diagnosis (`out/E7_rungB_diag_a_2026-09-23.log`) says which molecules carry the residual. Rung C (equivariant Δ-Hessian
on atom-pair blocks, displaced-gradient labels) remains the next representation step; before it, the cheaper lever is coverage: layer-A-type
molecules in the training pool.

**Added 12:0x — the layer-A hold-out is one molecule: benzene.** `m05/e7_rungB_diag_a.py`, `out/E7_rungB_diag_a_2026-09-23.log` (GBT of rung B, deterministic).
Per molecule of hold-out (a), trained on the full pool: biphenyl 0.35, fluorene 0.38, phenanthrene 0.50, fluoranthene 0.52, 2-naphthoic acid 0.58,
benzophenone 0.35, benzonitrile 0.29, phenanthridine 0.54, biphenylene 0.41 — nine of ten between 0.29 and 0.58 (corrected-frequency RMS 5.4–7.2 cm⁻¹
against 22–24 for the zero rule) — and **benzene 0.99** (ring diagonal 42 cm⁻¹, ΔH residual 0.71, corrected-frequency RMS 34 against 39). The
aggregate ratio is RMS-weighted and benzene's coupling magnitudes are the largest in the set, so one molecule carries the 0.82. Training on the
32 layer-A molecules of the pool alone gives the same picture (benzene 0.99, aggregate 0.84), so it is not coverage of the layer-A population
either: it is benzene. Benzene's ωB97X − B3LYP correction is the largest of the corpus (zero-rule frequency error 39 cm⁻¹ against 23 elsewhere;
two ring modes near 1200 cm⁻¹ shift by +151 and +58 cm⁻¹ — plausibly the exchange-sensitive bond-alternation motion, assignment to be checked), and no training molecule
carries a bare, unsubstituted, unfused ring with that response. The registered aggregate stays **between**; the per-molecule table says that for
every polycyclic or substituted molecule of the hold-out the local pairwise representation is at win level, and that the single failure is a
chemically identifiable extreme, not the representation. Hold-out (a) is not redefined; benzene enters the next pre-registration as its own row.

**Added 12:4x — benzene was not a learning failure but a corrupted target.** The two-route check (`corpus/analytic_hessians.py`: pyscf analytic Hessians at the
corpus geometry, 6-31G* Cartesian, grid 99/590) against the corpus psi4 finite-difference Hessians: B3LYP agrees to 1 cm⁻¹ except the e2g pair (622/622
analytic vs 630/645 corpus); **ωB97X disagrees by up to 133 cm⁻¹** (analytic 1210/1210, 1324, 1391 vs corpus 1223/1343, 1409, 1450; the 625/625 pair split to
563/605), |ΔH| max 2·10⁻² a.u. — at a geometry that is D6h to 10⁻⁴ Å. The "+151 cm⁻¹ ring shift" that defeated every model on hold-out (a) is an artefact of the
finite-difference Hessian, the same mechanism the noise principle found in the VPT2 quartics on 21 September. A corpus-wide screen on the sorted-pair
functional shift (`check_results.py`, 244 molecules): median max |Δω| 48 cm⁻¹, benzene 137 — the only molecule above 100; five between 80 and 90 (S–H and
methyl torsions, mostly imaginary-mode molecules already excluded). So the corpus is sound apart from benzene; benzene's row is being replaced by the analytic
route (both functionals), after which hold-out (a) is re-read with the same rung-B model. Policy: incident row in `QUALITY_POLICY.md`; the screen is now part of
`check_results.py`.

**Added 12:5x — hold-out (a) re-read with benzene's second-route target: win level on both hold-outs.** `m05/e7_rungB_reread_analytic.py`,
`out/E7_rungB_reread_2026-09-23.*`. Same training pool (175 molecules, untouched), same rung-B models; only benzene's *target* replaced by the analytic
Hessians (pyscf, same geometry). Benzene: ratio 0.99 → **0.25**, ring diagonal 42.5 → 4.1 cm⁻¹, corrected-frequency RMS
34.1 → 5.4 (zero rule 25.0), ΔH residual 0.71 → 0.20; the other nine molecules unchanged to the last digit.
Aggregate (a), MLP: ratio 0.81 → **0.43**, ring diagonal 11.3 → 4.5, corrected-frequency RMS 9.3 → 4.8 cm⁻¹ (zero rule 23.3); GBT 0.82 → 0.46.
Hold-out (b) untouched: 0.47 / 0.49. The registered outcome on the data as pre-registered stands (between on (a), win-level on (b)); with the corrupted
target corrected — nothing else changed — both hold-outs are inside the win criterion (≤ 0.6). The curve with the corrected target
(`out/E7_rungB_2026-09-23_analytic.*`, `--use-analytic`) is appended when in; the three A2 molecules flagged by the screen are being checked by the same second route.

**Added 16:2x — the three screen suspects.** Carbazole+SH (two entries): analytic and corpus agree to 4 and 10 cm⁻¹ (genuine S–H shifts). Biphenylene+CH3: every mode agrees except the softest — the deck's ωB97X finite differences make the methyl torsion imaginary (−37 cm⁻¹) where the analytic route gives +97. That is a second artefact class of the same mechanism: 20 corpus molecules carry an imaginary soft mode, 16 of them in one functional only; all 20 are on the analytic second route tonight (corpus README, dated note). If they heal, the module-05 release rule was dropping good molecules and E6/E7 gain up to 20 rows; the E6 hold-out (a) pathology of 2-phenylpyridine (imaginary −37 cm⁻¹, first-order target ill-defined) is one of them.

**Added 13:1x — the rung-B curve with benzene's second-route target (`--use-analytic`, everything else as pre-registered): WIN by the registered rule.**
`out/E7_rungB_2026-09-23_analytic.*` (1187 s). MLP ring coupling ratio vs n: (a) 45: 0.47, 100: 0.45, 175: 0.43 (slope -0.06); (b) 45: 0.51, 100: 0.50, 175: 0.47 (slope -0.06).
At 175: ring diagonal (a) 4.5 / (b) 4.8 cm⁻¹; ring block (a) 0.86 vs median rule 2.89, (b) 1.09 vs 1.14; corrected-frequency RMS (a) 4.7
(zero rule 23.3), (b) 5.1 (23.1); Duschinsky overlap median 0.998 / 0.993. Both hold-outs ≤ 0.6 at every size and both slopes negative:
**win** on the pre-registered criterion, on the data with one corrupted target replaced by its second route. The record therefore reads: as pre-registered
(corpus FD Hessians) — between on (a) because of benzene's artefact, win-level on (b); with the artefact corrected — win. The curve is shallow
(−0.06): the remaining error (ΔH residual 0.25 / 0.31) is the part of ΔH outside the pairwise pattern and the missing gradient term, not data.

**Added 14:5x — the mechanism of the benzene artefact.** Three psi4 runs on the CCX53 (`corpus/fd_grid_test_benzene.py`): (a) the corpus deck reproduces the
wrong ωB97X Hessian to the last digit (563/605, 1223/1343; deterministic, so it is a property of the settings); (b) the same finite-difference run with grid
99/590 lands within 8 cm⁻¹ of the analytic Hessian (residual pair split 620/633); (c) B3LYP with the deck is off by 23 cm⁻¹ on one pair. So: DFT grid noise
in the gradients, amplified by the 0.005 bohr step, worst for the range-separated functional and for a molecule whose displaced geometries break a
high-symmetry grid. It was our deck's grid (psi4's default 75/302), not the program. Guard recorded in the policy and the corpus README: analytic Hessians
or 99/590 for every new layer; second route for symmetric molecules.

**Added 24 September 11:4x — the twenty imaginary-mode molecules.** Second route done: 5 healed (all four ωB97X-only flips plus fluorene+CF3), 15
genuine (the B3LYP-only flips are torsional saddles of the substituent at the B3LYP geometry, confirmed by the analytic Hessian). The corpus gains five
rows (release `layerA2_2026-09-24`, 229 molecules); the "drop imaginary-mode molecules" rule was right for 15 and wrong for 5. Corpus README, dated note.
