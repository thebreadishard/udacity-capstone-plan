# Pre-registration E-series — can a separately trained network *learn* what is transferable between PAHs? (19 September 2026, 18:2x, before any run; the user: "een beetje zoals een netwerk dat woord embeddings leert … test al je ideeën autonoom; de enige restrictie: de ankerrun niet schaden")

## Question

Today's two learning curves left the ring-in-plane family at 12.4 cm⁻¹ on the proxy target (ωB97X − B3LYP first-order shift per B3LYP mode, 45 molecules, 12 held out by hash), unchanged when hand-made environment descriptors were added while the training error halved. The user's framing: as word embeddings capture what is transferable between contexts without a human naming it, a network trained on a pretext task might learn a per-mode representation that captures what is transferable between PAHs. This series tests that on the data that exist tonight, on the laptop at one thread and lowest priority, with the same held-out molecules and the same target as the two passes today.

## The raw input a network can learn from

A mode is represented as a *set of atoms*, each with: element one-hot (C, H, N, O, S), position in the molecule's principal-axis frame (Å / 5), the mass-weighted displacement vector of that atom in the mode (normalised so the mode has unit norm), its amplitude and its participation. Nothing derived (no families, no environment classes, no frequency except as a separate scalar for the probe). Planar PAHs make the principal frame well defined; in-plane rotations and reflections are used as augmentations.

## Experiments (all: 3 seeds; held-out RMS per family in cm⁻¹ on the fixed 12 molecules; n_train = 30 unless a curve is stated)

- **E0 — ridge on the first-pass tokens** (closed form, no network). Separates variance from bias: if ridge matches the Transformer (12.4 ± 20 % on ring-ip) the plateau is the representation's; if ridge is clearly better, today's model overfits; if clearly worse, its nonlinearity matters.
- **E1 — self-supervised mode embedding (the word-embedding analogue).** A permutation-invariant atom-set encoder (attention pooling, width 64, ≈ 3·10⁴ parameters) → 32-d embedding, trained with a contrastive objective: two augmented views of the same mode (in-plane rotation/reflection, coordinate noise 0.02 Å, 15 % atom dropout) are positives, all other modes in the batch negatives (InfoNCE). **No target enters the training.** Then the frozen embedding is probed with ridge to the target. Curve at 5/10/20/30 training molecules for the probe (the encoder is trained on all 45 molecules' modes — targets unseen, molecules seen; the leak is geometric only and is stated).
- **E1b — the same encoder trained supervised** on the proxy target of the 33 training molecules (the fallback of the design note: a mode-conditioned atom network). Its penultimate layer is the embedding; probed likewise.
- **E2 — molecule-level tokens** (ring count, longest linear acene run, heavy-atom count, heteroatom count) appended to the first-pass tokens, ridge and Transformer: the conjugation-length hypothesis of this afternoon's addition.

## Readings, fixed now (ring-in-plane family at n = 30, held-out; other families reported)

| reading | E0 | E1 | E1b | E2 |
|---|---|---|---|---|
| **win** | — | < 10 cm⁻¹ (and better than E0 by ≥ 20 %): the self-supervised embedding carries transferable structure our tokens lack; < 7 is a strong win | < 10 | improvement ≥ 1 cm⁻¹ over 12.4 |
| **lose** | — | ≥ 11.5: contrastive structure of displacement fields is not what governs the proxy ring correction | ≥ 11.5 | < 0.5 |
| **diagnostic** | within 20 % of 12.4 ⇒ representation-limited; ≤ 9 ⇒ the Transformer overfits; ≥ 15 ⇒ nonlinearity needed | training error vs held-out error reported | idem | idem |

Any E1 win is followed (later, not tonight) by the design note's Stage 1 (the full correction-Hessian object) with the E1 encoder as its atom backbone. Any loss across E0–E2 strengthens the reading that the *proxy's* ring correction is non-local, and the next experiment is a different proxy (BHHLYP − B3LYP from stage A), not a different network.

## What this does not decide

Anything about the coupled-cluster correction (X18 and T-1 remain the only two real points); anything at more than 45 molecules (layer A2 needs a machine); whether an equivariant pair-block model (design note §3) does better than an atom-set encoder — that is Stage 1, a week of work.

## Cost and safety

`modules/05_support_predictor/m05/embedding_experiments_E.py`; one thread, `nice -n 19`, ≈ 20–40 min of laptop CPU in total; the anchor run keeps its eight threads and is not touched. Results to `modules/05_support_predictor/out/embedding_experiments_E_2026-09-19.{json,md}`; outcome section appended here.

## Outcome — 19 September 2026, 20:0x (laptop, one thread at nice 19, 1,500 steps, about 50 min; `out/embedding_experiments_E_2026-09-19.{json,md}`)

Held-out RMS in cm⁻¹ on the same 12 molecules, n_train = 30. Reference: first-pass Transformer 1.78 / 4.31 / 12.41 / 26.6; family-median rule ring-ip 18.5; zero rule 21.9.

| experiment | C–H stretch | C–H oop | ring-ip | other |
|---|---|---|---|---|
| E0 ridge, first-pass tokens | 2.28 | 7.98 | 17.62 | 11.40 |
| E2 ridge, + molecule-level tokens | 2.70 | 8.11 | 17.64 | 11.23 |
| E2 Transformer, + molecule-level tokens | 1.85 | 3.93 | 12.37 | 24.50 |
| E1 contrastive embedding, ridge probe (mean of 3 seeds) | 12.21 | 9.18 | 19.30 | 13.30 |
| E1 embedding + tokens, ridge probe | 4.40 | 7.16 | 17.28 | 11.37 |
| E1b supervised atom-set encoder, direct (mean of 3 seeds) | 10.35 | 7.21 | 19.04 | 12.82 |
| E1b embedding, ridge probe | 12.19 | 7.39 | 18.95 | 12.54 |

**Readings by the rule fixed above.** E0: ridge on the tokens gives ring-ip 17.6 against the Transformer's 12.4 — above the 15 threshold: *the nonlinearity is needed*; the Transformer is not merely overfitting the ring family (its overfitting shows in 'other', not here). E2: **lose** — the molecule-level conjugation tokens change nothing (ridge 17.6, Transformer 12.4); the conjugation-length hypothesis in this crude form does not hold. E1: **lose** — the contrastive embedding probes to 19.3 on ring-ip and is worse than the hand tokens on every family (C–H stretch 12.2 against 1.8): the pretext task 'tell modes apart under augmentation' does not force chemistry into the embedding; adding the tokens back (17.3) recovers only the tokens' own information. E1b: **lose** — the same encoder trained on the target reaches 19.0 direct and 18.9 probed; from raw atom sets, 33 molecules are too few for this encoder to learn even what the tokens state outright.

**What was learned tonight, in one sentence each.** (1) The mode-token Transformer is the best model on the proxy and its ring-family plateau is not variance: neither a linear model nor more inputs nor a model on raw fields improves it. (2) A word-embedding analogue lives or dies by its pretext task; 'distinguish augmented views of a mode' is not aligned with vibrational chemistry the way 'predict the context' is aligned with word meaning. The next pretext, stated now and cheap: **predict DFT-only quantities from the raw field** — the mode's B3LYP frequency, its family, the *sign* of its ωB97X shift — supervision that exists for every corpus molecule whose Hessians are computed, so the encoder can be trained at scale before coupled-cluster labels exist (E3, to pre-register). (3) With 45 molecules every raw-input model is data-starved; the design note's Stage 1 (the correction-Hessian object, thousands of full matrices from the corpus) is the version of this idea that has enough data, and it is unchanged by tonight. (4) The proxy's ring correction may simply be non-local; the BHHLYP − B3LYP proxy on benzene and naphthalene (stage A) is the cheap check of that, before any more architecture.

## E4 — added 19 September, 20:4x, before the run: is the *target* the problem? (the user: "Blijf doordenken … er moet iets te vinden zijn")

Every model tonight predicts the per-mode first-order shift δν_i = (L_iᵀ H_high L_i − ω_i²)/(2ω_i), the projection of the high-level Hessian on the *low-level* mode. Where two modes of the same family lie close, the low-level eigenvector is a nearly arbitrary rotation inside the pair, and the projection inherits that arbitrariness: the same physics gives a different δν_i for a slightly different mixing. If the ring family — the densest family, 987 modes in 45 molecules — is the one where this happens, its plateau is a property of the label, not of the network, and no embedding can remove it. Two diagnostics, numpy only, seconds:

- **E4a — two definitions of the same shift.** For every mode: (1) the first-order shift above; (2) the *matched-eigenvalue* shift ω_high,j − ω_low,i where j is the high-level normal mode with the largest overlap |⟨L_i, L'_j⟩|. Per family: RMS of (1) − (2), the median best overlap, and the fraction of modes with best overlap < 0.9. **Reading:** if the ring family's RMS difference is of the order of the plateau (≥ 8 cm⁻¹) while the C–H stretch's is < 2, the label's mixing sensitivity explains the plateau; if it is < 3, the label is clean and the fault is elsewhere.
- **E4b — a mixing-invariant target.** Per molecule and family F: the mean shift of the family subspace, Tr(P_F ΔH_mw P_F)/(2 Σ ω) in the same units — invariant to rotations inside the family. Learning curve of the family-mean shift across molecules with ridge on molecule-level tokens (ring count, heavy atoms, heteroatoms, longest fused run, H-class counts). **Reading:** if the family-mean ring shift is predictable to < 5 cm⁻¹ across held-out molecules while per-mode shifts are not, the transferable quantity is the family block, not the mode — which is the design note's ΔH object read at the family level, and the recipe's regression head should predict blocks, not modes.

Script: `m05/target_diagnostics_E4.py`; results `out/target_diagnostics_E4_2026-09-19.{json,md}`. No training beyond closed-form ridge; the anchor is untouched.

### E4 outcome — 19 September, 20:5x (`out/target_diagnostics_E4_2026-09-19.md`)

| family | modes | RMS(first-order − matched) | median best overlap | overlap < 0.9 | sd of per-mode shift | sd of family mean across molecules | held-out family mean: median rule / ridge / zero | within-molecule per-mode spread |
|---|---|---|---|---|---|---|---|---|
| C–H stretch | 379 | 1.43 | 0.998 | 6 % | 2.2 | 0.86 | 0.74 / 0.61 / 43.6 | 2.0 |
| C–H out-of-plane | 271 | 1.52 | 0.997 | 4 % | 8.7 | 2.40 | 2.05 / 2.91 / 23.1 | 8.4 |
| ring in-plane | 987 | **9.19** | 0.989 | **17 %** | 18.0 | 2.78 | **3.56** / 4.58 / 13.6 | **17.7** |
| other | 826 | 24.4 | 0.999 | 6 % | 17.2 | 4.95 | 6.08 / 6.24 / 11.7 | 16.6 |

**Reading, by the rule above: the label is the problem.** (E4a) For the ring family the two legitimate definitions of "the shift of mode i" differ by 9.2 cm⁻¹ RMS — three quarters of the 12.4 plateau — because 17 % of ring modes have no clean partner in the high-level Hessian; for the two C–H families they differ by 1.4–1.5, exactly the level those families were learned to. (E4b) The mixing-invariant family mean of the ring shift varies across molecules by only 2.8 cm⁻¹ and is predicted on held-out molecules to 3.6 by the median rule alone, while the per-mode shifts inside one molecule spread by 17.7 around that mean. **What transfers between PAHs is the family block; what does not transfer is how the correction is distributed among the modes inside the block — and that distribution is the coupling structure, which a per-mode label cannot carry.** Consequences: (1) the recipe's per-mode regression target is ill-posed for the ring family and should become the family block (diagonal *and* couplings) — the design note's ΔH object at family level; (2) the licence question for the fingerprint is not "can the network predict each mode's shift" but "can it predict the block", which the shape test already said is what the spectrum needs; (3) E1's failure is partly explained: it was asked to predict a number that is not a function of the mode alone.

## E5 — added 19 September, 21:0x, before the run: the word-embedding analogy taken literally (the user: "Hoe leert een computer de embeddings van woorden. Laat je inspireren. Gebruik de analogie.")

Word2vec learns a word's vector by predicting its *context*; the trained skip-gram is an implicit factorisation of the word–context co-occurrence matrix (Levy & Goldberg 2014): u_wᵀ v_c ≈ PMI(w, c). Meaning is never labelled; it emerges because words that keep the same company get the same vector. The analogue: a molecule is a sentence, its modes are the words, and the company a mode keeps is **its coupling with the other modes under the correction**, K_ij = L_iᵀ ΔH L_j / (2√(ω_i ω_j)) in cm⁻¹ — the mode-basis correction matrix, whose diagonal is the per-mode shift and whose off-diagonal block is what E4 says does not transfer per mode but does as a block. K is on disk for every corpus molecule (≈ 60,000 pairs in 45 molecules against 2,463 per-mode targets: the pair supervision is twenty times richer, as context is richer than the word). **E5:** an encoder e(mode) → ℝ³² (E5-tok from the first-pass tokens + environment tokens through an MLP; E5-atoms from the raw atom set through the E1 encoder), a learned symmetric bilinear form W, trained so that e_iᵀ W e_j ≈ K_ij over *all pairs of every training molecule* (the diagonal included; symmetry-forbidden zero pairs are the negatives). Three seeds; the same 12 held-out molecules.

**Readings, fixed now (held-out molecules).** (a) Diagonal: e_iᵀ W e_i per family — ring-in-plane **win < 10 cm⁻¹**, lose ≥ 11.5 (the E1 rule). (b) Couplings: RMS of predicted K_ij against true K_ij over within-family ring pairs (i ≠ j), as a ratio to the zero rule — **win ≤ 0.7**, lose ≥ 0.9; this is the quantity no model so far was asked for. (c) Family block: the ring family's block trace on held-out molecules against the median rule's 3.6. (d) The frozen embedding probed with ridge to the first-order shift, for comparability with E0–E1b. Script `m05/embedding_skipgram_E5.py`; one thread at nice 19; results `out/embedding_skipgram_E5_2026-09-19.{json,md}`.

