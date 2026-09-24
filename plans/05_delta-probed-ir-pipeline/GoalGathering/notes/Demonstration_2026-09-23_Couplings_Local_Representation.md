# Can the network learn what the pipeline needs? The couplings, in one day (23 September 2026)

*A demonstration note for the supervisor conversation of 28 September. Every number traces to a results file named in the text; the tests were
pre-registered with their predictions before they ran (`PreRegistration_2026-09-19_E6_Learning_Curve_in_Data.md`,
`PreRegistration_2026-09-23_E7_Couplings_in_Local_Coordinates.md`). Written by Claude on the student's instruction; the student reads it before it
leaves the repository.*

## The question

The pipeline needs a learned correction from a cheap harmonic calculation (B3LYP/6-31G\*) to a better one. In the mode basis that correction is a
matrix K per molecule: its diagonal is the shift of each band, its off-diagonal elements (the *couplings*) say how the modes re-mix. The diagonal
was learned early (module 05: ring-in-plane shifts to 5 cm⁻¹ against 16 for the best rule that needs no learning). The couplings were not — by any
model, at any data size. The question for this note: is that a limit of the network, or of what we asked it to predict?

## 1. The evidence that data was not the problem

A pre-registered learning curve (E6) trained five models on 45, 100 and 175 molecules of the project's own corpus (224 molecules, two functionals
on identical geometries) and read them on two held-out sets fixed in advance: (a) ten small aromatics of the first layer; (b) all 39 molecules of
two scaffold cores never seen in training (fluoranthene, fluorene). The read-out for the couplings is the ratio of the model's RMS error to the
RMS of the couplings themselves — the "zero rule", 1.00, is a model that predicts no coupling at all.

Every mode-basis model sat on or above the zero rule at every size: the module's own block model at 1.00, 1.00, 1.00; two bilinear embedding
models at 1.9 and 1.3, flat. Slopes of the ratio against data: 0.00, −0.03, −0.04, against a pre-registered threshold of −0.25 for "data-limited".
Four times the data moved nothing (`out/E6_learning_curve_in_data_2026-09-23_excl_imaginary.md`). By the rule set on 19 September, buying more
data for this target was not justified.

## 2. The diagnosis: the target was unlearnable as posed

Three properties of the mode-basis coupling K_ij make it impossible for a model on per-mode descriptors, whatever its size:

- **Sign.** K_ij changes sign when one normal-mode vector is flipped (L_i → −L_i), and every per-mode descriptor is a square of that vector, hence
  blind to the flip. For a sign-blind input and a sign-odd target, the least-squares optimum is exactly zero — which is what the block model
  learned, to two decimals (`E7 T1`: the same model trained on |K_ij| moves off zero; trained on K it cannot).
- **Locality lost.** In internal coordinates (bonds, angles, torsions) a force-constant correction is sparse: an element is non-zero only between
  coordinates that share atoms. The transformation to normal modes smears that sparse object over every pair of modes, molecule by molecule,
  through a rotation the model never sees.
- **Symmetry lost.** Couplings between different irreducible representations are exactly zero; per-mode descriptors carry no irrep.

## 3. Where the correction actually lives (measured, not assumed)

The Cartesian correction ΔH of every molecule was transformed to redundant primitive internal coordinates (geomeTRIC's bonds, angles, dihedrals,
out-of-planes; Bᵀ F B reproduces the Hessians to 10⁻¹⁵ relative). Projecting the internal correction onto three sparsity patterns — no fitting,
no free parameter — and transforming back gives the fraction of ΔH that each pattern carries (`out/E7_T2_ceilings_2026-09-23.md`, rows "mask"):

| pattern of the internal correction | ΔH unexplained (a) / (b) | coupling ratio (a) / (b) |
|---|---|---|
| diagonal of the primitives only | 77 % / 73 % | 0.98 / 0.96 |
| + pairs of primitives sharing an atom | 61 % / 55 % | 0.78 / 0.70 |
| + bond–bond pairs inside the same ring (ortho / meta / para) | **27 % / 19 %** | **0.38 / 0.29** |

So the correction between the two functionals is, to three quarters, a change of the **bond–bond interaction constants inside the rings** — the
ortho/meta/para interaction constants of Pulay's benzene force field, the place where B3LYP's delocalisation error lives — plus atom-sharing pair
terms. That is a local, sign-consistent, rotation-invariant object with a chemical name. The classical multiplicative correction (SQM scale
factors, one per coordinate type, Pulay 1983 / Rauhut & Pulay 1995) cannot express it: fitted on the held-out molecule itself it still leaves 71 %
of ΔH (`out/E7_T2_posthoc_2026-09-23.md`).

## 4. The network learns it once it is asked for that

Rung B (`m05/e7_rungB_pairs.py`): the target is the internal correction on that pattern — thousands of labelled pairs per molecule instead of one
matrix — with 66 features per pair built from the two primitives (class, elements, ring membership, value, low-level force constant, the twelve
environment classes of their atoms) and from the pair (shared atoms, same-ring flag, ring-path distance, the low-level interaction constant). Two
learners: an MLP (2 × 128, three seeds) and gradient-boosted trees as the non-neural check. Prediction: ΔF → ΔH = Bᵀ ΔF B → projected onto the
cheap modes → the same read-outs as before, plus the quantity the pipeline consumes: the RMS error of the corrected frequencies after
diagonalisation (`out/E7_rungB_2026-09-23.md`).

| | mode-basis block model | local pairs, MLP (175 molecules) |
|---|---|---|
| ring coupling ratio, unseen cores (b) | 1.00 | **0.47** |
| ring coupling ratio, layer-A set (a) | 1.00 | 0.81 as pre-registered (nine of ten molecules 0.29–0.58; benzene 0.99 on its corrupted target) — **0.43** with benzene's second-route target |
| ring band-shift RMS, (b) | 6.5 cm⁻¹ | 4.8 cm⁻¹ |
| ring-block mean shift vs the median rule, (b) | 1.83 vs 1.14 | **1.09 vs 1.14** (first model to beat it) |
| corrected-frequency RMS, (b) / (a) | 23.1 / 24.3 cm⁻¹ (= zero rule) | **5.1 / 9.3 cm⁻¹** (9.3 → **4.8** with benzene's second-route target) |
| Duschinsky overlap of corrected modes, (b) | — | 0.993 (median) |

The MLP and the trees agree on the coupling ratio to two decimals at every size, so the number is a property of the representation, not of a
learner. With benzene's second-route target the full curve is (a) 45: 0.47, 100: 0.45, 175: 0.43 and (b) 45: 0.51, 100: 0.50, 175: 0.47 — under the pre-registered win line (0.6) at
every size, both slopes negative, corrected frequencies (a) 4.7 / (b) 5.1 cm⁻¹ at 175 (`out/E7_rungB_2026-09-23_analytic.md`). On the 39 molecules of two cores never seen in training the couplings are learned to less than half the zero rule, the band shifts are as
good as the best previous model, and the corrected frequencies land within 5 cm⁻¹ — from the same 175 molecules on which every mode-basis model
learned nothing. Figure: `figures/E7_couplings_representation_2026-09-23.png`.

## 5. What is not solved, stated plainly

- **Benzene — a corrupted target, not a learning failure.** The layer-A hold-out's aggregate (0.81) is one molecule: benzene alone sits at 0.99; the
  other nine — biphenyl, fluorene, phenanthrene, fluoranthene, 2-naphthoic acid, benzophenone, benzonitrile, phenanthridine, biphenylene — are at
  0.29–0.58 with corrected frequencies within 5–7 cm⁻¹ (`out/E7_rungB_diag_a_2026-09-23.log`). The two-route check then showed why: benzene's corpus
  ωB97X Hessian (psi4 finite differences of gradients) is wrong by up to 133 cm⁻¹ at a geometry that is D6h to 10⁻⁴ Å — degenerate pairs split to
  563/605 and 1223/1343 where the analytic pyscf Hessian at the same geometry gives 625/625 and 1210/1210 (`corpus/analytic_hessians.py`,
  `corpus/molecules/A_8448043181/analytic_check.json`). The "+151 cm⁻¹ ring shift" that no model could learn was an artefact of the target. A screen of
  all 244 molecules on the sorted-pair functional shift finds benzene as the only molecule above 100 cm⁻¹ (median 48); the corpus is sound apart from
  it. The screen is now part of the corpus check. Re-read with benzene's analytic target and nothing else changed (`out/E7_rungB_reread_2026-09-23.md`):
  benzene 0.99 → **0.25**, corrected frequencies 34 → 5.4 cm⁻¹; hold-out (a) as a whole 0.81 → **0.43**, corrected frequencies 9.3 → **4.8 cm⁻¹**.
  Both hold-outs are then inside the pre-registered win criterion. *(Added 24 September 04:3x: E8 read the coupled-cluster correction of benzene the
  same way — 92 % of it lives in the pairwise pattern (c) and 98 % in pattern (d), which adds pairs two bonds apart; the ring couplings need (d):
  coupling ratio 0.34 against 0.80 with (c). The CC correction is local like the proxy, one bond further. Pre-registration E8, outcome sections.)*
  The mechanism was pinned the same afternoon: the corpus deck's finite differences with
  psi4's default grid (75/302) reproduce the wrong Hessian exactly, and the same run with a 99/590 grid agrees with the analytic one to 8 cm⁻¹ — grid noise
  in the gradients divided by a 0.005 bohr step, worst for the range-separated functional on a high-symmetry molecule. Our setting, not the program; new
  corpus layers use analytic Hessians. This is the noise principle of 21 September doing its job a second time: every derived quantity gets a second route.
- **The curve is shallow**, now at a good level ((a) 45: 0.47, 100: 0.45, 175: 0.43; (b) 45: 0.51, 100: 0.50, 175: 0.47; slopes -0.06 / -0.06): what remains (ΔH residual 0.25 / 0.31) is the part of the correction outside the pairwise pattern and the missing gradient term, not data volume. The next
  step is representation once more, not volume: the full local Hessian on atom-pair blocks with an equivariant network (rung C), trained with
  displaced-geometry gradients as cheap extra labels and pre-trained on Hessian QM9 — or, cheaper first, the missing 27 % of ΔH outside the
  present pattern.
- **The gradient term.** The high-level gradient at the low-level geometry (decision 48's geometry term) is not in the corpus and sits in the
  residual; it is exact and cheap to add.
- **This is the DFT–DFT proxy.** The coupled-cluster correction the pipeline ultimately carries has the same chemistry (a bond-type-dependent change
  of stiffness and of the ring interaction constants); it has two real points so far, not a curve.

## 6. What this shows about the method

The learning-curve rule of 19 September ("no verdict on tiny data; keep training until the curve answers") did its job twice in one day: it said
*flat* for the mode basis, and it will say whether rung C is worth its cost. The network was never the limit. When the target was a basis-dependent,
sign-ambiguous object it learned the only thing consistent with its inputs — zero. When the target was the local, chemically named object that the
correction actually is, the same corpus taught it the couplings on unseen scaffolds in four minutes of CPU. That is the argument for the pipeline's
learned layer: choose the representation by measuring where the physics lives, then the network learns what it needs.

## Provenance

E6 clean curve: `modules/05_support_predictor/out/E6_learning_curve_in_data_2026-09-23_excl_imaginary.{json,md,log}`. E7: `out/E7_T1_2026-09-23.*`
(sign test), `out/E7_T2_2026-09-23.*` (SQM), `out/E7_T2_posthoc_2026-09-23.*`, `out/E7_T2_ceilings_2026-09-23.*` (where ΔH lives),
`out/E7_rungB_2026-09-23.*` (rung B), `out/E7_rungB_diag_a_2026-09-23.log` (benzene). Scripts in `modules/05_support_predictor/m05/`:
`e6_learning_curve.py`, `e7_t1_sign_test.py`, `e7_t2_sqm.py`, `e7_t2_posthoc.py`, `e7_t2_ceilings.py`, `e7_rungB_pairs.py`, `e7_rungB_diag_a.py`.
All runs on the rented CCX53 (Hetzner, Helsinki), 23 September 2026; the corpus is the project's own (224 molecules, B3LYP/6-31G\* and ωB97X/6-31G\*
Hessians on identical B3LYP geometries; the twenty molecules with an imaginary mode excluded after the split).
