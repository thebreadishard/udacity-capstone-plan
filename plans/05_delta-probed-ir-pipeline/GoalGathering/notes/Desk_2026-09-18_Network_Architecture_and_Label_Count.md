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
