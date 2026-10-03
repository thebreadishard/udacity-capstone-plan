# Standout module — the pattern proposer (which measurement next?)

**Status (3 October 2026).** Built 26 September on the user's word, pre-registered before the first run (`../../GoalGathering/notes/PreRegistration_2026-09-26_Standout_Pattern_Proposer.md`, dated amendments and a running outcome record), and read through to its CC-level test. On the proxy: E1 (band pool) and E2 (all pairs) read; the fair-chance search for the learned representation through stage 3; the adaptive ordering on the band pool (27 Sep) and on the wide pool (28 Sep 08:4x, `out/sim/all_p2s1A_*`): feedback alone helps the blind order on the parents only, and on top of a scorer it adds nothing. The wide-deck stop rule failed both readings (28–30 Sep: W1 40 %, W2 28 % false stops; the band-free prior changes nothing); the user dropped the band deck on 29 Sep — the wide deck is the only focus. At CC level (`PreRegistration_2026-09-28_Standout_CC_Level_Test.md`, `cc_level_test.py --use-analytic`): benzene's corpus psi4 row proved noise (29 Sep) and the first CC response came from the wrong lambda (the lambda incident, 29 Sep); on the corrected Hessian (29 Sep 23:4x) the registered band deck fails C1/C2 as before, while the wide pool with the open prior passes C1 and C2 (P1 0.54 of P0's cost, oracle 124 of 806) — 'confirmed on this molecule (CC)'. The notebook's section 4f carries that read beside the invalid 4c/4d, kept and labelled (30 Sep); report rebuilt. Next read: the same test on naphthalene's CC Hessian (2 Oct) and, after it, on anthracene's — the molecule decides whether the wide deck's CC claim travels beyond benzene. Design note: `DESIGN_2026-09-27.md`.

## The question

Every molecule of plan 05 has a coupling table Δ₂ we can only afford to know in part: each entry costs an expensive energy. The recovery (banded ℓ₁,
FISTA, warm-started) reconstructs the table from pattern responses R_s = ½ aᵀ Δ a and stops when the held-out residual ρ_off is low enough. The
deck fixes *which* patterns exist and in *which order* they are measured. This module asks whether a network that has only seen other molecules can
choose a better order — and, since 27 September, whether the deck should reach every pair at all.

## Data (no new quantum chemistry)

`run_export.py` turns the corpus's DFT-against-DFT Hessians (ωB97X − B3LYP; layers A, A2, B) into one export per molecule: modes, frequencies, atomic
participations, the low-level Hessian, the full Δ₂ (the "answer", used only for the oracle and the read-out), the probe deck's patterns (built by
`probes/dryrun_dft_delta_recovery.py build_deck`) and their exact responses. 289 molecules on 26 September. Splits are hashed: the parents (unsubstituted
aromatics, larger than any training molecule) are evaluation only; A2/B molecules 70/10/20 train/validation/evaluation → 97 evaluation molecules
(41 parents, 56 substituted), 21 validation, the rest training.

## Orderings

| name | what decides the order | learns from |
|---|---|---|
| P0 | the deck's hashed order (the plan's fixed recipe) | nothing |
| P1 | an MLP on 21 hand-made pair features (frequencies, band flag, atom-sharing overlaps, low-level Hessian projections) → log₁₀\|Δ_ij\| | training molecules |
| P2 | the learned embedding: the rung-C equivariant body (`../05_support_predictor/m05/rungC_equivariant.py`) → per-mode embedding → pair head | training molecules |
| P12 | z-score average of P1 and P2 | — |
| P3 | the oracle: the true \|Δ_ij\| (an upper bound, never available in practice) | the answer |
| P0+A, P1+A, P2+A | the same priors, re-ranked after every checkpoint by the current reconstruction (optimism for untouched pairs) | feedback during measurement |

A pattern's score is the *mean* over the pairs it touches (dated amendment of 26 Sep; the sum favoured broad random patterns on the planted test).

## Read-outs (all from the stored curves; `readout.py`)

Primary: K_off(0.3) — energies beyond the single-mode block until the held-out ρ_off ≤ 0.3, as a ratio to P0 per molecule (median, fraction improved).
Fallback registered before reading (band pool: P0 rarely reaches 0.3): n_half (energies to the midpoint between the single block and P0's end point) and
the AUC of ρ_off over P0's checkpoint grid; the in-band Frobenius error beside them. `stage_readout.py` reads scorer recipes on the validation split
(MSE, Spearman, top-decile precision in and out of band). `deck_cost_readout.py` compares the band deck and the all-pairs candidate set.

## Results so far (outcome sections of the pre-registration; read-outs in `out/sim/*_readout.md`)

- **E1, band pool:** the learned order reaches the halfway point with ≈ one fifth of the fixed order's energies (n_half ratio 0.17–0.20 on 95–98 % of
  molecules, the same on parents and substituted; oracle 0.06–0.07). S1 pass, S4 (transfer to size) holds.
- **E2, all pairs:** the pool matters more than the order. The band deck consumed in full ends at ρ_off 0.53 / 0.47; a candidate set with a pattern for
  every pair ends at 0.08 / 0.14. On that set ordering still pays: K_off(0.3) ratio P12 0.70 / 0.76, oracle 0.25 / 0.38 (`out/sim/deck_cost_2026-09-27.md`).
- **P2, the fair-chance search (rule of 26 Sep 12:1x):** stages 1–3 read on validation (recipe +0.03 Spearman; loss and capacity within the registered
  margins, the largest variant consistently ahead); stage 4 at 300 molecules with a paired per-molecule test; stage 5 (QM9 pretraining) after the 28th.
  No sentence about the embedding before stage 5.
- **Adaptive ordering, band pool:** feedback helps the blind order (P0+A 0.8× P0) and improves the whole curve on top of a scorer (6–10 %) without moving
  the halfway point — the oracle gap is knowledge, not feedback (S5 fails on n_half, passes on AUC).
- **Adaptive ordering, wide pool (follow-up 28 Sep, section 4b):** on the all-pairs candidate set feedback helps the blind order early in the curve
  (n_half: P0+A 0.73× P0 on both splits; at K_off(0.3): 0.92× parents, 1.08× substituted) and adds nothing on top of a scorer (P1+A = P1 at the median, strictly better on 37–50 %; the
  band pool's AUC gain is gone); S5 fails, the prediction "feedback closes a third of the log-gap to the oracle" fails (9–12 %, by read-out). Lever: a better scorer.

## How to run

```
python run_export.py ../05_support_predictor/corpus/molecules out/exports          # exports + index.json
python -m pp.scorer fit out/exports out/p1 --seed 0                                 # P1 (three seeds)
python -m pp.embed_scorer fit out/exports out/p2s1_lr1e-3_w128 --seed 0 --lr 1e-3 --n-embed 128 --patience 20 --epochs 300   # P2, stage-1 recipe
python run_simulation.py out/exports out/p1 out/sim/band --pool band --embed-prefix out/p2s1_lr1e-3_w128 [--adaptive] [--shard k/n]
python merge_shards.py out/sim/band_merged out/sim/band_shard*.json
python readout.py out/sim/band_merged.json out/sim/band_readout.md
python stage_readout.py out/exports out/stageN_readout.md <recipe prefixes…>
python deck_cost_readout.py out/sim/band_p2_merged.json out/sim/all_p2_merged.json out/sim/deck_cost_<date>.md
```
Tests: `python -m pytest ../../tests/test_pp_planted.py -q` (7 planted-block tests, seconds). Interpreter: the system Python with torch and rdkit
(`../../REPRODUCE.md`, header). Pools ran on hel1-23 (CPX62, 8 shards × 2 threads, `nice 10`); fits on one laptop thread.

## Files

`pp/core.py` (export, recovery, orderings, adaptive rule) · `pp/scorer.py` (P1) · `pp/embed_scorer.py` (P2) · `run_export.py` · `run_simulation.py` ·
`merge_shards.py` · `readout.py` · `stage_readout.py` · `deck_cost_readout.py` · `out/sim/*_readout.{md,json}` (committed read-outs; merged JSONs local) ·
`out/*_seed*.json` (fit records) · `out/inband_share_2026-09-26.json` · `requirements.txt` · `DESIGN_2026-09-27.md`.

## What this is not

A proxy-level result: the tables are DFT against DFT, not DFT against coupled cluster. The test on real responses (the anchor's naphthalene deck) comes
after the 28th, as does the deck change it motivates (`../../GoalGathering/notes/PreRegistration_2026-09-27_Wide_Candidate_Deck_Stop_Rule.md`).
