# Desk note 2026-09-18 — pipeline A's network: what it is, how many labels it should need, and where the training wisdom sits (written 18 September 2026, late evening, before any learning curve exists; the user: "sla de architectuur en deze inzichten op in het plan")

*Purpose: one place that says what the network looks like, what the reasoning about its label count is, and which training practices we intend to hold to — so that when the first learning curves arrive (layer A on 19 September; the coupled-cluster labels later) they are read against expectations written before them. The architecture itself is fixed in `modules/05_support_predictor/RECIPE.md` (12 September, amended 13 September for P26); this note restates it in a paragraph and adds the reasoning. Nothing here changes the recipe.*

## 1. The network, in one paragraph

A molecule is a **sequence of tokens, one per DFT normal mode** (30 for benzene, 48 for naphthalene, 102 for pentacene). Each token carries the mode's harmonic frequency, its band family, its irrep, the mass-weighted participation of C/H/N/O in the motion and a localisation index; charge and spin multiplicity are molecule-level tokens so that cations can enter later without an architecture change. A **Transformer encoder** — two layers, four heads, width 64, dropout 0.1, of the order of 10⁵ parameters — attends over the modes. Two heads: a **regression head** per token for the correction to that mode's band position (δν_i = Δ₂,ii / 2ω_i, in cm⁻¹ or relative), and a **pair head** on [h_i, h_j, |h_i − h_j|, h_i ⊙ h_j, |ω_i − ω_j|] for the couplings, whose declared baseline to beat is P25's resonance-denominator rule. Training: AdamW, lr 10⁻³, batch 32 molecules, early stopping on validation, **seeds 0, 1, 2**. **Pre-training** on the DFT–DFT proxy correction (ωB97X − B3LYP, the Hessian-QM9-derived corpus of 11,321 candidates, layers A/A2/B/C); **fine-tuning** on the coupled-cluster labels that pipeline B produces (diagonal from energies, couplings from gradients — the 18 September route). Output per band family is scored against that family's laboratory margin and the family is **licensed or refused**; a refused family returns DFT with the refusal printed (decision 36). Code: `modules/05_support_predictor/m05/model.py` (`SupportTransformer`).

## 2. The unit of counting is the mode, not the molecule

A "label" in plan 05's language is one molecule's coupled-cluster deck. To the network it is 30–100 per-mode regression targets and hundreds of pair targets, correlated within the molecule but distinct in their descriptors. Twenty labelled molecules are therefore ≈ 1,000 mode-level examples. Every estimate below is per band family, because the learning problem decomposes that way and the licence is granted that way.

## 3. What is already measured about the target's difficulty

| family | spread of the true correction | source | what the network must learn |
|---|---|---|---|
| C–H stretch | transfers by local type to 0.27 cm⁻¹ RMS between benzene and naphthalene | plan 06 X18 (16 Sep) | almost nothing beyond the type |
| C–H out-of-plane | 36 to 84 cm⁻¹ inside benzene alone | `probes/t1_transfer_test.py` (13 Sep) | dependence on the H environment (solo/duo/trio/quartet, the PAH literature's own classes) |
| C–C stretch | −36 to +65 cm⁻¹ inside benzene; 17.8 of 41.2 cm⁻¹ left after type transfer | T1, X18 | conjugation and ring-fusion dependence per mode |

A family scalar cannot be the label (RMS 33 and 13 cm⁻¹ inside one molecule); that is why the recipe went per mode on 13 September.

## 4. Reasoning about the label count — expectations fixed before the curves

**Literature anchors.** Käser & Meuwly (2021) lift one molecule's potential-energy surface from MP2 to CCSD(T)-F12 quality with ≈ 188 coupled-cluster points by transfer learning — a whole surface, a harder task than one smooth number per mode, and *per molecule*: it says nothing about crossing molecules. Δ-learning of molecular energies (Ramakrishnan et al. 2015 and its successors) needs thousands of molecules without pre-training and one to two orders of magnitude fewer with it. Learning curves for smooth difference quantities are power laws, error ∝ N^(−0.3 … −0.5): doubling the labels buys a quarter to a third of the error. Hence no estimate is worth anything until the first three points of the curve exist.

**The class is small.** PAHs are built from a dozen local environments (aromatic C–H by neighbour count, C–C by ring fusion and bay/cove geometry). A network does not have to discover these if the descriptors name them; the largest label saving is in the descriptors, not in the count.

**Expectations, per family, for the 5 cm⁻¹ margin of the FEL references (the 0.5 cm⁻¹ of Pirali 2009 is one molecule's reference uncertainty, not a learnable level — desk note of 17 September, §1):**

| family | expected molecules to cross 5 cm⁻¹ on held-out neutrals | the expectation is wrong if |
|---|---|---|
| C–H stretch | 5–10 | the held-out RMS is above 5 cm⁻¹ at 10 molecules |
| C–H out-of-plane | 15–30 | above 5 cm⁻¹ at 30 |
| C–C stretch | 30–100, or refused | the curve is flatter than N^(−0.3) between 10 and 40 |

Overall: **twenty to fifty neutral molecules, chosen to cover the local environments,** for the C–H families; the C–C stretch family is the one likely to demand more or to be refused. At 2–4 laptop-days per label at cc-pVDZ (gradient route, g 3–6) fifty labels are 100–200 laptop-days or some weeks on a cluster; at cc-pVTZ (29–58 laptop-days per label) the count is out of reach without a cluster — which is why the anchor verdict of 20–24 September also sets this number.

**What the proxy learning curve (layer A, 19 September) measures and does not.** It measures the *sample complexity of the task's shape* — how fast a per-mode correction of this form is learned from these descriptors across molecules. It does not measure whether the ωB97X − B3LYP proxy is structurally like the coupled-cluster correction; that is measured only by the first coupled-cluster labels themselves, and X18/T1 are the two points that exist today.

## 5. Where the training wisdom sits (what an engineer who has trained many such networks would insist on)

1. **Per-family learning curves at 5, 10, 20, 40 molecules**, three seeds each, the power-law exponent fitted and printed. The decision number is the label count at which the held-out error crosses the family's margin — nothing else.
2. **Descriptors before capacity.** If a family learns slowly, add the local-type descriptor (neighbour-count classes, fusion class) before adding layers. A 10⁵-parameter model on 10³ examples is already on the generous side.
3. **Pre-train, then fine-tune with a small learning rate and early stopping on held-out molecules, never held-out modes** — modes of one molecule leak into each other; the split is by molecule, and by scaffold where possible (naphthalene-like held out from anthracene-like).
4. **Ensembles over seeds are the uncertainty**, and the uncertainty is the refusal: a family whose ensemble spread exceeds its margin on a held-out molecule is refused for that molecule, not averaged.
5. **Active selection of the next label**: label next the molecule where the ensemble disagrees most, weighted by the family's margin. In practice this halves to thirds the labels a random order needs; it also decides the order of pipeline B's decks, so it belongs in the calendar, not only in the recipe.
6. **Baselines that are hard to beat, always in the table**: the zero rule, the family-median rule of T-1, and the local-type transfer of X18. A network that does not beat X18's type transfer for the C–H stretch has learned nothing there and should not be licensed there.
7. **Report in the family's unit** (cm⁻¹ beside the laboratory margin), never in a loss value.
8. **Do not trust any estimate — including §4 — without the first three points.**

## 6. What would change this note

The first proxy curve (19 September): if the C–H families are not below 5 cm⁻¹ by 20 molecules on the proxy, the descriptors are revisited before any coupled-cluster label is spent. The first three coupled-cluster labels beyond benzene and naphthalene: they replace §4's expectations with measurements. Either event gets a dated addition here, not a rewrite.

### Dated addition, 19 September 2026, 12:4x — the first proxy learning curve (layer A, 45 molecules)

`modules/05_support_predictor/m05/learning_curve_layerA.py`, results in `modules/05_support_predictor/out/learning_curve_layerA_2026-09-19.{json,md}`. Proxy target: the ωB97X − B3LYP first-order shift per B3LYP mode; 12 molecules held out by hash (107 / 71 / 287 / 231 held-out modes in the four families); training sets of 5, 10, 20, 30; three seeds; 600 full-batch AdamW steps; RMS on held-out modes in cm⁻¹.

| family | n = 5 | n = 10 | n = 20 | n = 30 | family-median rule | zero rule | slope of log RMS vs log n | §4 expectation |
|---|---|---|---|---|---|---|---|---|
| C–H stretch | 2.44 | 1.89 | 1.79 | 1.78 | 1.73 | 43.8 | −0.17 | 5–10 molecules for 5 cm⁻¹ → **met at 5**; the median rule is already at 1.7 and the network does not beat it |
| C–H out-of-plane | 5.80 | 5.30 | 4.22 | 4.31 | 8.5 | 23.6 | −0.19 | 15–30 → **met at 20** (4.2); seeds 4.2–4.5 |
| ring in-plane (C–C) | 14.9 | 13.1 | 12.5 | 12.4 | 18.5 | 21.9 | −0.10 | 30–100 or refused → **not met at 30**; the flattest curve; at this slope 5 cm⁻¹ would need ~10⁴ molecules — a descriptor problem, not a count problem |
| other (low-frequency, mixed) | 38.5 | 31.3 | 29.3 | 26.6 | 11.2 | 14.9 | −0.19 | not a licensed family; the network is *worse than zero* here: overfitting (train RMS 3.7–8.3 against held-out 27–38) |

Readings. (1) The two C–H families behave as §4 expected on the proxy, and the C–H stretch confirms §5.6: a family-median (local-type) rule is the baseline to beat, and at 1.7 cm⁻¹ it is not beaten by a 10⁵-parameter model on 30 molecules. (2) The C–C family is the hard one, as predicted, and its slope says more labels alone will not fix it: §5.2 applies — descriptors that name the ring-fusion and conjugation environment before any capacity or any coupled-cluster label is spent on it. (3) The model overfits at every size (train 3.7–9.2 vs held-out 10.7–21.6 over all modes; the seed spread of the all-modes RMS at n = 30 is 10.7 / 20.6 / 21.6, driven by the 'other' bin) — early stopping on held-out molecules and a smaller head are the first two changes for the next pass, not more layers. (4) What this does not say: whether the coupled-cluster correction has the same learnability as the ωB97X − B3LYP proxy; X18 and T-1 are still the only two points on the real object. Consequence for the calendar of §4: unchanged for the C–H families; for the C–C stretch the plan is descriptors first, and the per-family refusal remains the honest outcome if they do not help.

### Dated addition, 19 September 2026, 16:1x — second pass: environment descriptors as the one change (laptop, one thread at nice 19; `m05/learning_curve_layerA_v2_descriptors.py`, `out/learning_curve_layerA_v2_2026-09-19.md`)

Token set B adds per mode the participation shares of H by PAH class (solo/duo/trio/quartet/substituent), of C by ring role (fused/edge-H/edge-substituent/non-ring/sp3) and of heteroatoms (ring/non-ring), from the bond graph; classes verified on five molecules. Same split, sizes, seeds, 600 steps. Held-out RMS, A → B:

| family | n = 5 | n = 10 | n = 20 | n = 30 | slope A → B |
|---|---|---|---|---|---|
| C–H stretch | 2.89 → 1.90 | 1.91 → 1.81 | 1.86 → 1.54 | 1.87 → 1.60 | -0.23 → -0.11 |
| C–H out-of-plane | 5.69 → 4.78 | 5.04 → 4.42 | 4.10 → 4.39 | 4.55 → 5.04 | -0.15 → +0.02 |
| ring in-plane | 14.99 → 15.51 | 12.87 → 12.87 | 12.19 → 12.18 | 12.44 → 12.38 | -0.11 → -0.13 |
| other | 37.5 → 35.8 | 31.9 → 36.2 | 29.0 → 32.5 | 25.4 → 28.5 | -0.21 → -0.12 |
| train, all modes | 3.6 → 1.8 | 4.6 → 2.1 | 7.0 → 5.3 | 7.6 → 5.0 | |

Reading. **The descriptor hypothesis for the ring family is falsified on the proxy**: the environment classes change nothing there (12.4 → 12.4 at 30 molecules, slope −0.10 → −0.12) while the training error halves — the added tokens are memorised, not generalised. The C–H stretch now beats the family-median rule (1.60 against 1.73) and the C–H out-of-plane family gains at 5–10 molecules and loses at 30; neither moves the calendar. Two readings remain open and both are cheap to test before any coupled-cluster label: (a) the ring-mode proxy correction (ωB97X − B3LYP) may be governed by conjugation length and delocalisation — a whole-molecule property the network's per-mode tokens do not carry — rather than by local environment; a molecule-level token (ring count, longest acene run) would test that; (b) the plateau at 12 with training error 2–5 is variance-limited: a ridge regression on the same tokens, and early stopping on held-out molecules, would say whether the 10⁵-parameter model is simply too large for 30 molecules. Rule 2 of §5 stands (descriptors before capacity), but this particular descriptor set was the wrong one for the ring family; the note's §4 expectation for the C–C stretch — '30–100, or refused' — is unchanged, with 'refused' now the more likely reading unless (a) or (b) moves it. What this still does not say: anything about the coupled-cluster correction itself.

### Pointer, 19 September 2026, 17:0x

The route by which the network *learns* its features instead of receiving ours — the correction Hessian ΔH as the output object, the raw probe responses as the labels through their projections, an equivariant atom network with a pair-block head, pre-trained on the proxy ΔH the corpus already holds in full — is designed in `Design_Note_2026-09-19_Learned_Features_Hessian_Difference_Network.md`, with Test 1 (ring-in-plane below 5 cm⁻¹ on the proxy on today's held-out set) as its first pre-registered gate. Guessed descriptors continue in parallel (the user, 19 Sep).

