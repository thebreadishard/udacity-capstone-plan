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
