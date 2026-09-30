# External review received, 30 September 2026 22:2x — Grok on the Δ-Hessian model design (answer to `Review_Prompt_2026-09-30_RungC_Model_Design.md`)

*The reviewer did not have the files on disk; it reasoned from the prompt. Its text is kept in the student's chat; this note records what it claimed,
what was verified against the code the same evening, and what was adopted. Decisions are ours; the review is a source.*

## Claims and verification

| claim (Grok) | verified against the code | verdict |
|---|---|---|
| The three block invariants discard the principal axes off r̂ and the relative orientation of blocks sharing an atom; this is the dominant cause of the 2× gap to the pair model, which sees F_low of the element it corrects | `rungC_equivariant.py` header and `pair_scalars`: trace, r̂ᵀBr̂, ‖B‖_F per block, trace and norm per diagonal block — nothing else | **accepted; the first lever** |
| The head a I + b r̂r̂ᵀ + Σ c (u uᵀ + u uᵀ) is low-rank for coupling blocks unless the vector channels assemble the directions; 3 blocks, mean pooling, 5 Å may not | as designed (N_TENSOR 16, 3 blocks, mean); not measurable without the tests below | plausible; tested by the "overfit one molecule" and hybrid-head runs |
| ΔH_ii = −Σ_j ΔH_ij redistributes error onto the diagonal | as designed (line 229); the constraint is exact translational invariance | kept (reviewer agrees: keep, do not let it dominate) |
| Mass-weighted Cartesian MSE may be raw Cartesian and explain 11 vs 5 cm⁻¹ | `loss_terms`: (ΔH · M^{-1/2}⊗M^{-1/2} · 1e4)², i.e. M^{-1/2} ΔH M^{-1/2} | **not the case** |
| "Aux weight 1.0 may be a no-op if the Cartesian term is 10× larger" | log of tonight's run: main ≈ 1e-6, aux ≈ 0.2–0.3 → the internal ΔF term dominates by ≈ 1e5; the model trains almost entirely on it | **reverse of the claim**; the loss is already the internal quantity |
| The internal term is on all redundant primitives (minimum norm), not on the scored pattern, and not class-standardised | `loss_terms` aux = MSE over the full B⁺ᵀ ΔH B⁺; `--scale class` exists for the target scale, not for the aux term | **accepted**; cheap change |
| Inner validation must split by molecule; standardisation fit on training only | `inner_split(tr, seed, frac)` returns molecule ids; class scale from the training pool | verified, no leak |
| Early stopping on a random 15 % may cherry-pick; pre-register a fixed inner-val list | seeded split, ids recorded in the JSON (`inner_val_ids`) | acceptable; the list is reproducible per seed |
| Pairs beyond 5 Å are unlearnable; count ring–ring primitives with supporting atoms > 5 Å | the scored pattern is bond–bond pairs inside one ring and pairs sharing an atom: supporting atoms ≤ 3 Å apart | **not a cause**; rank 4 (cutoff/topology edges) stays low |
| Undirected edges stored once would break the diagonal constraint | `edges_within` returns both directions; equivariance/translation unit tests exist (`tests/test_rungC_equivariance.py`) | verified |
| Element rows for S/Cl after QM9 pretraining | reset to the trained mean at load (28 Sep amendment), `design_check.py` probes the heaviest element | verified (design check PASS on Cl tonight) |
| Layer B is the wrong support for hold-outs (a)/(b); more of it will not help | proof-of-learning outcome 30 Sep 21:1x | agreed, measured |
| QM9 pretraining ≈ 0 is expected (wrong graphs, wrong residual) | measured 0.00–0.03 | agreed |
| Predicting H_high and subtracting: worse; curriculum: neutral; sum pooling: keep mean | consistent with our records | agreed |
| Literature: HIP (ℓ = 2 content identifies a 3×3 block), Dral's RIC-element learning (= rung B), Δ-learning, class-balanced curvature losses; do not copy AD-Hessians of energy models or foundation-model widths | to be cited in the pre-registration | adopted as references |

## Adopted plan (each item pre-registered with prediction and pass line before it runs; laptop, hours; three seeds where a number is claimed)

1. **Diagnostics first (cheap):** (i) zero the H_low input channels → the ratio must collapse towards 1.0 (the model uses the only cheap signal);
   (ii) overfit benzene alone → must reach a small residual (else the head/constraint is too tight). Add both as tests.
2. **Rank 1 + rank 2 together at 175:** inject the B3LYP 3×3 blocks as rank-2 equivariant edge features (contractions with r̂ and with the vector
   channels; no CG library) and put the internal term on the rung-B pattern with per-class standardisation. Prediction (Grok): (a) 0.55–0.70,
   ω 6–8 cm⁻¹. Pass: (a) ≤ 0.75. Miss: unchanged head is not the bottleneck → go to 3 anyway.
3. **Rank 3, the hybrid:** PaiNN encoder, one scalar per rung-B primitive with F_low as an explicit input, ΔH = Bᵀ ΔF B. Pass: (a) ≤ 0.55 to say
   "the Cartesian head was the problem"; near rung B (0.45–0.55) expected if the encoder is not harmful.
4. **Data, with rung B (minutes):** the 39 two-scaffold molecules held *in* the training; 40 PAH-like against 200 layer-B molecules on the same
   hold-outs; ratio against PAH-likeness of the pool. Decides what is computed next (PAH-like A2, not B; anchors that share the PAH coupling graph).
5. Not first: cutoff/topology edges (rank 4), head width (rank 5), self-supervised pretraining on our own H_low, cross products.

Tonight's data-scaling run (449 / 750, C1 and C2) reads first; its result and the diagnostics above go into the rung-C pre-registration as dated sections.
