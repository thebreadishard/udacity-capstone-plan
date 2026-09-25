# Note 2026-09-25, 06:3x — the growing asset, the two horizons, and the proof that the network learns

*Written on the user's word ("Schrijf het, en laten we ons daar ook richten, meer en meer … het bewijs dát het netwerk leert is het allerbelangrijkste").
For the proposal package of 28 September; dated additions below as evidence arrives.*

## 1. The framing (the user, 25 September morning)

A coupled-cluster label is not a cost that evaporates when a project ends; it is a permanent measurement that makes every later network
better. The system we build — the corpus, the frozen decks, the second route, the ΔH network — improves with each expensive calculation that
enters it. ΔH-v1 is usable after the first few hundred labels while the machines keep going; ΔH-v2 replaces it when the queue is further; each
version is a release with a DOI and a per-family statement of what it is worth. After a decade the network is an asset that everyone who
predicts aromatic spectra profits from. Under this view the right measure of a label is not "hours per molecule" but "what the network learns
per machine-hour", and slow is acceptable where informative.

## 2. The two horizons, and how the odds relate to them

- **Capstone horizon (2027; the mandate sentence of 13 September):** a trained network for large PAHs with a desktop and a small Snellius
  allocation. Here the price per label counts, the per-family licensing of the anchor is the honest form of "usable now", and the levers
  (symmetry 6× on cores, E9 neighbourhood 4×, E10 environment-once ≈ 2.7×, a cheaper correlation tier) decide what v1 can contain.
- **Asset horizon (a decade):** the price per label hardly counts; what counts is that the system keeps learning. L2's reading (one
  LNO-CCSD(T)/cc-pVDZ energy of a 25-atom molecule > 8 h on eight threads) is a fail on the first horizon and a factory rate on the second:
  twelve energies a day per CCX53, a 240-energy neighbourhood label in three weeks, the ≈ 30 environment types of the A2 layer in a year and a
  half on one machine or a month on a small allocation.

Both horizons go into the proposal: a v1 that exists inside the capstone and says per family what it is worth, and a growing asset in which every
expensive calculation stays. The odds lines of the PI assessment keep their 2027 meaning; this note is the reason they are not the whole story.

## 3. What such a system needs — and what already exists

| requirement | why | status 25 September |
|---|---|---|
| a target that is local and learnable | otherwise more data does not help | shown on the proxy: E7 (pattern (vi) carries ¾ of ΔH; pair model learns couplings), E8 (CC correction local, one bond further), E9 (neighbourhood columns), E10 (environment blocks transplant for 11 of 15 types); E6 showed the mode basis is *not* learnable — the contrast is part of the evidence |
| labels quieter than the signal | else v5 learns the noise of v1 | the noise principle (21 Sep): frozen deck v1 with hash, second route (analytic Hessians) that already corrected two releases |
| a label definition that does not drift over ten years | else old measurements become worthless | decks are frozen files with hashes; releases are dated with manifests; a new deck is a new version, never an edit |
| a queue ordered by information, not by list position | the asset grows fastest on the most informative labels | partly: E10 says small rigid hosts first; a formal acquisition rule is not written |
| the price of every label on record | value per euro must stay visible | the corpus ledger records timings per molecule and stage; L2/L3 record seconds per energy |
| versioned releases with a DOI and a per-family worth | the "usable after 200, better after 400" cycle | release layerA2_2026-09-24 exists; Zenodo deposits prepared (24 Sep); the per-family licence of M3 is the first "worth" statement |

## 4. The proof that the network learns — what we have and what we do not

The user's criterion: the design is a success when it is fully shown that the network learns. Honest status, all numbers from the files named.

**Shown (proxy, DFT–DFT ΔH, corpus of 24 September):**
- *The diagonal is learned, strongly.* Module 05's baseline retrained on the 229-molecule release, held-out test set of 20: per-family diagonal
  RMS 2.6 / 3.9 / 5.4 / 8.5 cm⁻¹ (C–H stretch / C–H out-of-plane / ring in-plane / other) against 44 / 24 / 20 / 19 for no correction
  (`notebook/results_followup2.json`, `test_rms_diag_229`).
- *The couplings are learned in the local representation, and the curve rises with data — on one of the two hold-outs.* E7 rung B
  (`out/E7_rungB_2026-09-23.md`), MLP on pair features, hold-out (b) = two scaffold cores never seen: ring coupling ratio to the zero rule
  0.51 → 0.50 → 0.47 and corrected-frequency RMS 5.99 → 5.40 → 5.14 cm⁻¹ at 45 → 100 → 175 training molecules (no correction 23.1); the
  gradient-boosted check agrees to a few tenths. ΔH residual 0.34 → 0.31.
- *In the wrong basis it does not learn* (E6, 23 September: coupling ratio flat at 1.0 / 1.9 / 1.3 over the same sizes). That the same data
  learns in one representation and not in the other is what turns "a curve went down" into "the representation is right".

**Not shown, and what it would take:**
1. *Hold-out (a) — the bare parent skeletons — barely improves:* ratio 0.82 → 0.82 → 0.81, corrected RMS 9.96 → 9.47 → 9.34 at 45 → 100 → 175.
   The model trained on substituted molecules transfers its diagonal to bare cores but not yet their couplings. This is the mandate's own
   direction (large bare PAHs), so it is the gap that matters most.
2. *The curve is shallow and short:* 45 → 175 is less than a factor four; a learning curve that proves learning spans a decade of data with a
   pre-registered slope. The corpus design of 12 September already defines the subsets: layer B's first 300 / 600 / 1,200 molecules in the
   hashed order. They are not computed. Cost: ≈ 1,200 × 1.4 h ≈ 1,700 machine-hours — ten days on the CCX53 plus two CPX62, three weeks on
   three CPX62. **This is the decisive experiment for the user's criterion, and it is a factory job, not a research question.**
3. *Size extrapolation is untested:* train on ≤ 26 atoms, test on 30–34 (layer A2's top) — the form of the mandate's claim. The data exist for
   a first cut (A2 spans 16–30 atoms); the split is not pre-registered yet.
4. *The design's own network is not the one tested:* rung B used an MLP and trees on hand-made pair features; the equivariant ΔH model of
   the 23 September decision (SQM → neural SQM → equivariant ΔH) is not built. The pair model is a floor, not the design. *(12:1x: the pair model
   turned out to carry molecular symmetry in its features — E11.2 amendment — so what the equivariant model must add is directions and context; that
   is now a pre-registered test, rung C, with the pair model's 0.43 / 0.47 as the floor and pass lines fixed before it is built.)*
5. *Nothing is shown on coupled-cluster labels* beyond E8's locality on benzene (and naphthalene on Saturday): a CC-trained instance needs
   CC labels that do not exist yet. Proxy-to-CC transfer is the second horizon's first task.
6. *The noise floor is not reached:* the second route puts the label noise well below 1 cm⁻¹ per mode; the best hold-out sits at 5 cm⁻¹. A
   curve that approaches the floor is the strongest possible proof; one that plateaus above it says the model, not the data, is the limit.

**Proof standard (proposed for pre-registration before the layer-B run):** on hold-outs (a) bare parents, (b) unseen scaffolds, (c) larger
than any training molecule, the corrected-frequency RMS and the ring coupling ratio at 100 / 300 / 600 / 1,200 training molecules; pass =
a monotone decrease on all three hold-outs with the slope on a log scale pre-registered (proposal: at least a factor 1.5 per decade of data on
(a) and (c)), and a plateau, if any, no higher than three times the second-route noise. Fail = flat on (a) or (c). The same table is rerun with
the equivariant model when it exists; the pair model is the floor it must beat.

**Answer to the question "have we shown it?":** in part. The diagonal, yes. The couplings, yes on unseen scaffolds and with a rising curve, and — *corrected 09:0x, see below* — yes on the bare parents too once benzene's target is the second-route one; the slopes are the open point. Fully, no — and the experiment that would settle it is defined, pre-registrable this week, and costs about ten machine-days.

## 5. What this changes in the ordering of work

The levers stay (the user: "Ik vind hefbomen goed, blijf je daar vooral ook op richten"); the proof of learning moves ahead of them in the
queue for the machines. Concretely, in order: (1) pre-register the proof standard above; (2) after route 2 and the cations, hel1-14 starts layer
B's first 300 in the hashed order, and hel1-16 follows after the thirty restarts; the CCX53 after naphthalene E8; (3) the learning-curve table
at 300 as soon as it exists, at 600 and 1,200 as they arrive; (4) the size-extrapolation split on today's data as a desk test this week;
(5) the cheaper correlation tier (L2b) as the lever for the first horizon, pre-registered separately.

## Dated addition, 2026-09-25 07:1x — size extrapolation, first cut

Desk test (`PreRegistration_2026-09-25_Size_Extrapolation_Desk_Test.md`): trained on ≤ 26 atoms only, the pair model predicts the 45 molecules of
27–34 atoms at ring coupling ratio 0.66 → 0.62 → 0.59 and corrected-frequency RMS 6.6 → 6.0 → 5.8 cm⁻¹ (zero rule 22.8) for 45 → 100 → 161 training
molecules — encouraging on the registered bars, at the edge on the ratio, shallow in slope. Item 3 of §4 moves from "untested" to "tested at one
size step, learnable, slower than within-size"; the layer-B curve decides whether the slope holds over a decade of data.

## Dated correction, 2026-09-25 09:0x — hold-out (a) was misquoted this morning

*Correction 09:0x (25 September):* the bare-parent numbers quoted this morning (ratio 0.82 → 0.82 → 0.81, corrected RMS 10.0 → 9.5 → 9.3) are the 23 September run with benzene's corrupted finite-difference target; with the second-route target (E7 rung B `--use-analytic`, recorded in the ledger of 23 September 12:5x) hold-out (a) reads **0.47 → 0.45 → 0.43** and **5.9 → 5.1 → 4.7 cm⁻¹** at 45 → 100 → 175 — learning, not flat. The couplings of the bare parents are learned at the same level as the unseen scaffolds; what remains short is the slope (1.14× per decade on the ratio, 1.49× on the RMS, against the registered 1.5×).

Consequences: item 1 of §4 is withdrawn as written (the gap on bare parents is a slope of 1.14× per decade, not a flat line); the 06:3x and 21:4x odds text and the reading copy's 25 September note carry the same correction by dated line; the E11.5 power-law predictions were refitted on the corrected curve (`out/E11_power_law_2026-09-25b_analytic.md`): bare parents predicted at 1,200 molecules ratio 0.39 [0.38, 0.40], corrected RMS 3.4 [3.2, 3.5] cm⁻¹. Cause: the superseded result file of 23 September 10:0x sat beside the corrected one without a banner; it now has one, and QUALITY_POLICY gains the rule.
