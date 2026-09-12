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
