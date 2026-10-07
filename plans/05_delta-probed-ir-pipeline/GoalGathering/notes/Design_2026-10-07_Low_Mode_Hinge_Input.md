# Design note, 7 October 2026 — a hinge input for the low modes (TASKS 23), with its ablation registered before it runs

**The open family.** On clean (analytic) hold-out labels three of the four mode families are under decision 53's line of 3 cm⁻¹; 'other' is not
(3.35), and 77 % of its squared error sits in the modes below 700 cm⁻¹ ('other-low', 3.21 pooled over 132 modes;
`modules/05_support_predictor/out/rungC_low_modes_noise_c34_analytic_2026-10-05.md`). Weighting the loss did not move it (chains 34b and 34c, 4 Oct).
Two causes were registered as candidates: the training labels (finite differences, low-mode floor 4.8 cm⁻¹ — chain 35 on analytic labels tests that,
after the labels server) and the input. This note is the input half.

**Step 0, measured today without training** (`probes/low_modes_range_diag.py`, `out/low_modes_range_diag_2026-10-07.{md,json}`, 41 s). The head
predicts ΔH only for atom pairs within 5 Å. Zeroing the TRUE correction beyond 5 Å costs other-low 1.95 cm⁻¹ pooled (diagonal blocks kept; 3.40 when the
diagonal is re-made from the sum rule as the model does), 0.75 / 0.92 at 6 Å, nothing at 8 Å. But the cost does not follow the models' errors
molecule by molecule (Spearman ρ 0.24 / −0.10): truncation hurts 2-naphthoic acid (3.64) and fluoranthene (3.19) most, where the models do well
(1.52) or average (3.59); the models are worst where truncation costs about 1 — biphenyl 4.62, biphenylene 3.98, benzonitrile 3.74, fluorene 3.66,
benzophenone 3.62. Benzene, phenanthrene, phenanthridine and 2-naphthoic acid sit at 1.3–1.9. The reading rule written before the numbers put this
between its lines (both range and the torsion environment go into the design); the per-molecule pattern says which comes first.

**What the five worst molecules share: a hinge.** Each has a soft motion about a joint that a fused six-ring aromatic does not have: a single bond
between two rings (biphenyl, benzophenone's two ring–carbonyl bonds), a strained small ring (biphenylene's four-ring, fluorene's five-ring with its CH₂),
or a linear group bending against the ring (benzonitrile's C≡N). The body sees elements and positions within 5 Å; a hinge is a property of the bond
graph (ring sizes, which bonds are acyclic, which atoms are linear) that it would have to infer from geometry with few examples.

**The input.** One class per atom from the bond graph, in this priority: `ring4` (in a four-membered ring), `ring5` (in a five-membered ring),
`linear` (two neighbours at > 170°, or a terminal atom triple-bonded to one), `rotor` (a heavy atom of an acyclic bond between two heavy atoms that
both have ≥ 2 heavy neighbours — the inter-ring and ring–substituent single bonds), `sp3` (a carbon with four neighbours), `none`. Bonds from covalent
radii × 1.25; ring membership from shortest cycles through each atom; an acyclic bond is one with no other path between its atoms. The class enters
the body as a learned embedding added to every atom's scalar features, exactly as the charge state does since 3 Oct (`q_emb`): zero-initialised, built
without a random draw (so a run without the feature initialises every other parameter as before, bit for bit), and frozen unless `--hinge-feature`
is given. Old checkpoints load with the embedding at zero and predict exactly as before.

**Ablation (registered here, before any run).** Chain 36 = chain 34's recipe (`probes/night2_1003.sh`: hybrid head, aux both, kring 0.3, kdiag 0.1
family, SQM scale, pair features, pattern f, 200 epochs, patience 20, lr 3e-4, hidden 256, sum aggregation, inner validation 0.15, pool A/A2/B, 750,
seeds 0–2, `--use-analytic`) plus `--hinge-feature`; the control is chain 34 itself (identical code path with the feature off — a test checks that the
initialisation is bit-identical). Read exactly as chain 34 was on 5 Oct: `probes/rungC_eval_saved.py --use-analytic` per seed, `probes/rungC_eval_means.py`,
`probes/rungC_low_modes_noise.py --low 700`.

**Predictions.** other-low pooled 3.21 → 2.5–2.9; the five hinge molecules drop by ≥ 0.8 on average (4.0 → ≤ 3.2); the four hinge-free molecules
move by less than ±0.3; ring-ip, CH-stretch and CH-oop within ±0.2 of chain 34; 'other' 3.35 → 2.8–3.1.

**Lines.** *other-low pooled ≤ 2.9 and the hinge five down by ≥ 0.5 on average* → the hinge input is a cause: chain 36 is a promotion candidate
(decision 57: carried when no family is worse by more than its seed range) and its models replace chain 34's in T3. *The hinge five down by < 0.5* →
the hinge input is not the cause; the remaining candidates are the labels (chain 35) and range (a 6 Å cutoff, which step 0 says can buy up to 1.2 of
the 1.95). *Any family worse by more than 0.3 pooled* → rejected whatever other-low does. Hold-out (b) is reported beside it, not judged.

**Cost and place.** ≈ 3.5 h on the laptop's free 8 threads (chain 34c took 3 h 38 min at 8 threads beside the TZ run), beside the LNO cell (8
threads); nothing else waits for these threads until the CCX53's queue lands (≈ midnight).


## Outcome, 7 October 10:3x — rejected: the hinge input is not the cause

Trained 07:28–10:11 (`out/E7_rungC_chain36_hinge_750_2026-10-07.{json,md,log}`); read as registered on the analytic hold-out (a) targets
(`out/read_chain36_analytic_2026-10-07.md`, `out/rungC_low_modes_noise_c36_analytic_2026-10-07.md`; the first read was refused by decision 55's guard
until the models had a reviewed status — registered as candidates 10:15).

| hold-out (a), seed mean (range) | chain 36 (+ hinge) | chain 34 (5 Oct, same targets) | difference |
|---|---|---|---|
| ring-ip | 1.97 (1.70–2.21) | 1.82 | +0.15 |
| CH-stretch | 1.70 (1.34–2.28) | 1.25 | **+0.45** |
| CH-oop | 2.21 (1.83–2.66) | 2.36 | −0.15 |
| other | 3.73 (3.39–4.31) | 3.35 | **+0.38** |
| other-low, pooled over 132 modes | 3.51 | 3.21 | +0.30 |

The five hinge molecules, other-low: biphenyl 4.62 → 4.89, fluorene 3.66 → 2.74, benzophenone 3.62 → 4.17, benzonitrile 3.74 → 3.95, biphenylene 3.98 →
5.15 — mean 3.92 → 4.18, **up by 0.26** where the prediction said down by ≥ 0.8. The hinge-free four: benzene 1.25 → 0.56, phenanthrene 1.87 → 2.19,
2-naphthoic acid 1.52 → 1.71, phenanthridine 1.49 → 2.40. Hold-out (b) other 6.03 → 6.49.

**Lines:** other-low 3.51 > 2.9 and the hinge five not down → the first line is not met; the hinge five down by less than 0.5 → **the hinge input is
not the cause**; CH-stretch +0.45 and other +0.38 pooled → **rejected** by the third line as well. Chain 36 is superseded (read, not promoted;
chain 34 stays carried, v1.1). Only fluorene moved the predicted way. The per-atom class gave the body more freedom and the low modes did not use it.

**What is left for 'other', in order:** the training labels (chain 35 on analytic labels; the labels server starts when the CCX53's MP2 queue ends,
≈ tonight) — the 4.8 cm⁻¹ finite-difference floor of the low modes in the training targets is now the leading candidate; range (a 6 Å cutoff) only
after chain 35, since step 0 found it does not follow the models' errors.
