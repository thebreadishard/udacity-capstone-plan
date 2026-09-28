# Standout module — provenance

Every number in the notebook and the report traces to a file named here. Dated notes are appended; nothing above them is rewritten.

## Data

- `out/exports/<id>.npz` + `out/exports/index.json` — one export per corpus molecule, written by `run_export.py` on 26 September 2026 (log
  `out/export_2026-09-26.log`, local) from `../05_support_predictor/corpus/molecules/*` (analytic B3LYP and ωB97X Hessians at the corpus deck; the corpus's
  own provenance is in module 05). 289 molecules. The exports are local (≈ 4 MB each is not committed); they rebuild with the same command from the corpus.
- Splits: `pp/core.py: split_of` — parents evaluation only; A2/B by sha1 of the id, 70/10/20. Counts in notebook section 1.
- `out/inband_share_2026-09-26.json` — share of off-diagonal coupling power inside the 200 cm⁻¹ band per molecule (committed).

## Fits (weights local, records committed)

- P1: `out/p1_seed{0,1,2}.json` (recipe, epochs, best validation MSE); weights `out/p1_seed*.pt` + `_norm.npz` (local). Log `out/p1_fit_2026-09-26.log`.
- P2: stage 0 `out/p2_seed*.json`; stage 1 grid `out/p2s1_*_seed*.json` (log `out/p2_stage1_2026-09-26.log`); stage 2 `out/p2s2_{huber,rank}_seed*.json`
  (`out/p2_stage2_2026-09-26.log`); stage 3 `out/p2s3_{b5,b3v,b5v}_seed*.json` (`out/p2_stage3_2026-09-26.log`). Validation reads:
  `out/stage2_readout_2026-09-26.{md,json}`, `out/stage3_readout_2026-09-26.{md,json}` (`stage_readout.py`).

## Pools (hel1-23, CPX62; shards 8 × 2 threads unless stated)

- E1 band pool, P1 + oracle: `band_shard*` → `band_merged.json` (local) → `out/sim/band_readout.{md,json}` (committed), 26 Sep 10:16 UTC.
- E1 band pool, all orderings (P2 = stage 0): `band_p2_*` → `out/sim/band_p2_readout.{md,json}`, 26 Sep 12:19 UTC.
- E2 all pairs, all orderings: `all_p2_*` → `out/sim/all_p2_readout.{md,json}`, 26 Sep 23:22 UTC (68.6 shard-hours).
- Adaptive band pool (3 shards × 2 threads, P2 = stage-1 recipe): `band_p2s1A_*` → `out/sim/band_p2s1A_readout.{md,json}` and the paired statistics
  `out/sim/band_p2s1A_paired.json` (written by the notebook from the merged JSON), 27 Sep 03:19 UTC.
- Deck cost: `out/sim/deck_cost_2026-09-27.{md,json}` from `deck_cost_readout.py` on the band_p2 and all_p2 merged JSONs.
- Wide pool, stage-1 recipe: `all_p2s1` (hel1-23, 5 shards; read 27 Sep 15:2x): `out/sim/all_p2s1_{merged,readout,paired}.md`, `all_p2s1_readout.json`; the
  merged JSON is local (data backup).
- Wide pool, adaptive orderings: `all_p2s1A` (hel1-23, 8 shards, 27 Sep 13:2x → 28 Sep 06:39 UTC; read 28 Sep 08:4x): `out/sim/all_p2s1A_{merged,readout,paired}.md`,
  `all_p2s1A_readout.json`; `out/sim/all_p2s1A_paired.json` written by notebook section 4b (28 Sep); the 16 MB merged JSON is local (data backup).
- Pool chain log on the server: `/root/pp/pool_chain.log` (DONE lines with UTC stamps); launcher scripts `run_pool.sh`, `run_pool_n.sh`,
  `run_band_adaptive.sh`, chains `chain_*.sh` (copies in the session scratchpad).

## Notebook and report

- `notebook/make_notebook.py` → `notebook/pattern_proposer.ipynb` (executed) + `notebook/results.json` + `notebook/figures/*.png`. The only live computation
  is three curves on the smallest evaluation molecule of layer B; everything else is read from the files above.
- `make_summary.py` → `Pattern_Proposer_Report.docx/.pdf` from `notebook/results.json`.

## Plan of record

- `../../GoalGathering/notes/PreRegistration_2026-09-26_Standout_Pattern_Proposer.md` (question, data, read-outs, pass lines, dated amendments, outcomes).
- `../../GoalGathering/notes/PreRegistration_2026-09-27_Wide_Candidate_Deck_Stop_Rule.md`, `PreRegistration_2026-09-27_Cheap_Proxy_Input.md` (after the 28th).
- Tests: `../../tests/test_pp_planted.py` (7). Interpreter: the system Python with torch (`../../REPRODUCE.md`).
- CC-level test (28 Sep 20:3x, pre-registered 20:2x): `cc_level_test.py` → `out/cc/A_8448043181_cc_test.{json,md}` (registered run) and `…_all_band200`, `…_all_band5000` (exploratory, labelled); `pp.core.hi_override` (tests `tests/test_pp_hi_override.py`); notebook section 4c.

## 28 September 2026, 21:4x–21:5x — the wide deck's stop rule (pre-registration 27 Sep, amendment 28 Sep 21:4x)

- `pp/core.py` gains `stop_rule(curve, tau, b_max, M)`; `run_simulation.py` gains `--w-cm` (solver prior width; 0 = band-free l1 on every off-diagonal pair) and `--only`
  (curves for a subset of orderings, P0 always); `stop_rule_readout.py` reads W1/W2 from a wide-pool record and its band record; the probe's `build_deck` gains `pool="all"`
  (`--deck-pool all`). Tests: `tests/test_pp_stop_rule.py` (5), `tests/test_probe_deck_pool.py` (2).
- Reading (i), as registered (band prior, from the record): `python stop_rule_readout.py out/sim/all_p2s1_merged.json out/sim/band_p2s1A_merged.json out/sim/stop_rule_band_prior_2026-09-28`
  -> W1 FAIL (53 % stop within B_max), W2 FAIL (29 % false stops). Outcome in the pre-registration.
- Benzene CC test with the band-free prior: `python cc_level_test.py A_8448043181 ../../probes/results_m1/e8_benzene_ccpvdz/hessian_ccsd_t.npz --pool all --w-cm 0 --tag all_band0`
  -> `out/cc/A_8448043181_cc_test_all_band0.{json,md}` (exploratory, labelled).
- Reading (ii), launched 21:57 on the laptop (8 shards, OMP 2 threads each): `python run_simulation.py out/exports out/p1 out/sim/all_p2s1_w0_shard$k --embed-prefix out/p2s1
  --pool all --w-cm 0 --only P12,P3_oracle --checkpoints 60 --shard $k/8` -> `out/sim/all_p2s1_w0_shard*.{json,md,log}`; merge with `merge_shards.py`, read with `stop_rule_readout.py`.
