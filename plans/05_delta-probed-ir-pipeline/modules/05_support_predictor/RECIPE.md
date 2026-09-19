# Module 05 — the Δ₂-support predictor: recipe candidate (written 2026-09-12, before any corpus or model exists)

This note fixes, before the corpus is built and before any network is trained, what Module 05 is
under the plan (Capstone_Mapping §M05, decided by the user 2026-09-04; Distilled §5; Ladder §3). It is
the pre-registration the pilot note's item 5 (the P3 effect size) and the module's own report will point
to. What the plan leaves open on purpose — the size of the recomputed subset — stays open here and is
fixed by a dated note after the timing that the plan names.

## Task type and model family (rubric, declared)

- **Domain: sequence.** A molecule is a sequence of M tokens, one per DFT normal mode; the target is a
  label per token *pair*.
- **Model: Transformer** (self-attention over mode tokens; a pairwise head on the attended token pairs).
  Nothing outside CNN/RNN/Transformer is used; a change of family goes back to the user before training.
- **Framework: PyTorch**, CPU (the laptop has no CUDA GPU; Compute_Budget B2).

## What is predicted

The **support of Δ₂ in the low-level DFT normal-mode basis**: which off-diagonal blocks between which
DFT modes are large. Δ₂ is the difference of two DFT Hessians projected on the low-level modes
(dimensionless-q form, as `probes/dryrun_dft_delta_recovery.py` stage A prints it: `D2_direct_Q`).

- **Label (candidate, pilot-note item 5 fixes it):** s_ij = 1 if |Δ₂,ij| ≥ θ · max_k |Δ₂,kk| with
  θ = 0.1, for i ≠ j; the diagonal is not predicted (it is always taken). θ is printed with every table.
- **Loss:** binary cross-entropy on the pairs, class-weighted by the label prevalence of the training
  fold; **metrics:** precision, recall, F1 and average precision (area under the precision–recall
  curve) on the held-out pairs, and — the quantity the plan actually consumes — **the pattern count K
  the prior implies at a recall of 0.9**, compared with the free-element count the symmetry prior
  leaves on the same molecule (decisions 11 and 13).

## Corpus (the plan's, unchanged)

1. **Hessian QM9** — Williams, Kabalan, Stojanovic, Zolyomi & Pyzer-Knapp, *Scientific Data* 12 (2025),
   DOI 10.1038/s41597-024-04361-2; data on figshare, DOI 10.6084/m9.figshare.26363959 (v4, 6.29 GB;
   41,645 QM9 molecules, ωB97x/6-31G* Hessians in vacuum and three implicit solvents). Public since
   2024, verified in Crossref and DataCite on 2026-09-12. **The download needs the user's permission
   (size) and has not been made.**
2. **B3LYP/6-31G* Hessians recomputed** on an aromatic-heavy QM9 subset with the plan's psi4 deck
   (`probes/dryrun_dft_delta_recovery.py` stage A, low functional B3LYP; the high side for the corpus is
   Hessian QM9's ωB97x, so the dry-run's BHHLYP high side is *not* reused). **Subset size: not here** —
   fixed by a dated note from the measured per-molecule Hessian time (benzene 388 s B3LYP on the laptop,
   dry run 2026-09-05) and the compute available after the xtight/QZ work.
3. Δ₂ per molecule = H(ωB97x) − H(B3LYP) in the B3LYP mode basis, dimensionless q; support labels by
   the rule above; **split by molecule** with a hash of the QM9 index (80/10/10), no lab data anywhere.
4. **Held-out PAH test set only:** the benzene dry-run tensor (fixture in `probes/results_dryrun/`;
   note it is B3LYP→BHHLYP, labelled as such) and later the naphthalene dry run and the probed rung
   tensors. QM9 has at most nine heavy atoms, so every PAH is off-distribution; reported separately.
5. Published as its own release (Zenodo DOI, deck hashes) **before the module starts** — the user's action.

Reading 1 of the reuse clause (decision 7) and the reading-2 fallback (another public Hessian source,
not yet named) are carried from the mapping unchanged.

## Baseline and the one controlled change (rubric + Distilled §5)

- **Baseline network:** 2 encoder layers, 4 heads, width 64, dropout 0.1; tokens = [ω_i, family one-hot,
  atomic-composition fractions of the mode (C/H/N/O mass-weighted participation), mode-localisation
  index]; pair head = MLP on [h_i, h_j, |h_i − h_j|, h_i ⊙ h_j, |ω_i − ω_j|]; AdamW, lr 10⁻³, batch 32
  molecules, 30 epochs, early stopping on validation average precision, **seeds 0, 1, 2**.
- **The one change (frozen in the plan, Distilled §5): the prior.** Learned prior vs structural
  (symmetry) prior at matched K on the dry-run corpus — same patterns, same held-out set, same solver,
  ≥ 3 seeds; what changed = the prior, what stayed the same = everything else. Metric ρ_off at fixed K
  and K to reach ρ* = max(1.1·ρ_dry, c·ρ_noise). This is a comparison of a network-as-prior against a
  prior without a network; it satisfies the rubric's "exactly one aspect" and is the comparison the
  pipeline needs.
- **Rubric-side second configuration (also declared, so the report has a network-vs-network pair):**
  the baseline with **depth 2 → 4** (everything else identical). Reported beside the plan's comparison,
  never in its place.

## Success criterion

**The licence, not accuracy** (Uitleg ch. 10 §7): does the prior save patterns on the corpus (P3
effect size), and does the prior-assisted recovery on a real rung (R2, R3) agree with the prior-free
check within τ₇ / η₈·S? Both outcomes are publishable; the report is written for either.

## What is scaffolded now (2026-09-12) and what is not

Now: the corpus builder in fixture mode (reads the dry-run `stageA_hessians.npz`, writes tokens,
labels and a manifest), the Transformer and pair head in PyTorch, and a smoke test that trains on the
fixture for a few steps to prove the code path. Not now: the download, the recomputed subset, any
result. No number printed by the smoke test is a result.

## Dated amendment 2026-09-13 (P26, proposed; adopted only with P26) — the target object changes, the discipline does not

Written before any corpus is recomputed or any model is trained, so it is still a recipe change and not a post-hoc one.

- **What is predicted (replaces "the support of Δ₂").** Two heads on the same per-mode sequence: (1) a **regression head** for the per-mode
  correction — the first-order band shift δν_i = Δ₂,ii/(2ω_i) in cm⁻¹, or equivalently the relative shift δν_i/ν_i — of every DFT mode; (2) the
  **pair head as before**, now with the resonance-denominator ordering of P25 as its declared baseline (a pair's prior is 1/|ω_i² − ω_j²| within an
  irrep; plan 06 X10: Spearman 0.75 against the measured effect at benzene, 19 of 47 pairs for 0.5 cm⁻¹), so the learned pair head must beat the free
  rule, not the zero rule. The support label s_ij of the original recipe stays as the pair head's label.
- **Why per mode and not per family.** `probes/t1_transfer_test.py` (13 September): within benzene the C–C stretch corrections span −36 to +65 cm⁻¹
  and the C–H out-of-plane ones 36 to 84, so a family scalar cannot be the label (RMS 33 and 13 cm⁻¹ inside one molecule); C–H stretch is tight (0.17).
  The per-family band correction remains the *scoreable aggregate* (P19, decision 32's licence), not the model output.
- **Inputs.** As before (mode descriptors from the low-level Hessian: frequency, family, atom-projected displacement shares, irrep) **plus charge and
  spin multiplicity as tokens on the molecule**, so that cations can enter the training set later without an architecture change (P26 §4); until
  cation labels exist the model is licensed for neutrals only.
- **Corpus and pre-training.** Unchanged: the DFT–DFT corpus (ωB97X − B3LYP on Hessian QM9 subsets, 11,321 candidates) for pre-training; fine-tuning
  on the coupled-cluster labels pipeline B produces (thin decks: diagonal + P25 couplings, or gradients), per P26 §4; the stand-in is labelled as such.
- **Metrics.** Regression head: RMS error of δν per family on held-out molecules against (a) the zero rule and (b) the family-median rule of T-1,
  reported in cm⁻¹ beside the family's laboratory margin (Module 03's u_band). Pair head: as before, plus precision at the P25 count.
- **Success criterion (the licence).** Unchanged in kind: transfer, not fit — the held-out per-family error within τ_F on a rung the pipeline
  measured (R1 first, thin R2 hold-outs after); P26 §6's T-2 is the first such test. Both outcomes are publishable; the report is written for either.
- **What does not change.** The frozen splits, several seeds, tuning parity, the declared effect size, "inconclusive" as an allowed outcome, and the
  rule that the recipe is committed before the data it judges.

## Dated pointer 2026-09-18

The architecture above is restated in one paragraph, with the label-count reasoning per family (expectations fixed before any learning curve) and the training practices we hold to, in `GoalGathering/notes/Desk_2026-09-18_Network_Architecture_and_Label_Count.md`. Read the layer-A learning curve of 19 September and the first coupled-cluster labels against that note's §4 table.

## Dated amendment 2026-09-19, 21:3x (proposed from E4; adopted by the user: "Laten we dat goed onthouden en meenemen naar de volgende stappen") — the target object becomes the family block

E4 (`GoalGathering/notes/PreRegistration_2026-09-19_E_Series_Learned_Mode_Embeddings.md`, outcome section) showed on the proxy that the per-mode first-order shift is ill-posed for the ring-in-plane family: two legitimate definitions of one mode's shift differ by 9.2 cm⁻¹ RMS because the mode mixes with its family neighbours, while the mixing-invariant family mean transfers across molecules to 3.6 cm⁻¹. From this date the regression target of the P26 amendment is stated **per family block**: the block of the mode-basis correction matrix K_ij = L_iᵀ ΔH L_j / (2√(ω_i ω_j)) (cm⁻¹) restricted to the family's modes — its diagonal (the per-mode shifts) *and* its couplings together, so that the loss and the licence are invariant to how the correction is distributed inside the block. The per-mode shift remains a printed read-out (it is what a band position needs once the block is known), the per-family band correction remains the scoreable aggregate (P19), and the pair head's support label stays. The encoder architecture is open: the mode-token Transformer, the E5 encoder + bilinear form (word2vec analogue on K), or the atom-level ΔH model of `Design_Note_2026-09-19_Learned_Features_Hessian_Difference_Network.md`, decided by pre-registered tests on the same held-out molecules.

