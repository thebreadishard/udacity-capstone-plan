# Open tasks — plan 05 (the working list; the ledger is the record)

*Opened 26 September 2026, 13:4x, on the user's word ("Goed idee, doen"). One row per open task: what, why it exists (the decision or question behind it),
where it lives, the next check and when. Rows are removed when done (the ledger keeps the outcome); rows are edited with the clock's stamp. Read it
with `bash probes/state.sh`; both together are the picture. Rules: nothing here is a plan of record — the pre-registrations and the weekend plan are;
this file only says what is running or waiting and who acts.*

## Running (machines)

| task | why | where | next check | ends |
|---|---|---|---|---|
| Layer-B shards 0/1/2/3 | the layer-B learning curve (proof of learning; interim reading Sun 20:00; 300 molecules for stage 4) | hel1-18 (2.29.40.182), hel1-21 (2.29.45.10), hel1-16 (46.62.227.91, shard 2), hel1-14 (89.167.29.36, shard 3 since 27 Sep 08:37); `corpus/layerB_shard*of5.log` | monitor line every 10 molecules; counts 70/74/77/0 = 221 at 06:2x; fetch with `scratchpad/fetch_layerB_shards.sh [merge]` | run on; ≈ 300 in the corpus Mon/Tue |
| E8 naphthalene CC Hessian (three partial runs) | locality one bond further at CC level, on a two-ring molecule | CCX53 (77.42.67.27), `/root/e8/results/naphthalene_ccpvdz/` | monitor line (verdict/finished/Traceback); 20 of 30 gradient files at 12:3x | ≈ Sun evening; then assembly + `e8_cc_locality.py` + `e8_between_extension.py` (in the chain) |
| Standout pattern proposer: wide pool with the stage-1 recipe, then the adaptive variants on the wide pool | does the stage-1 recipe transfer (band: no, read 05:2x); does feedback pay where the blind order has more to gain (band: P0+A 0.8×, P1+A curve-only) | hel1-23: `all_p2s1` 5 shards (12/97 at 04:5x), then `chain_p2s1e` → `all_p2s1A` 8 shards | monitor lines `POOL all_p2s1 DONE`, `POOL all_p2s1A DONE`; fetch, `readout.py`, paired S5 statistics, outcome | all_p2s1 ≈ Sun 13:00; all_p2s1A ≈ Mon 07:00 |
| P2 search, stage 4 (data growth) and 5 (pretraining) | the learned embedding gets a fair chance before any sentence about it (the user, 12:1x); stages 1–3 read 20:3x (recipe helped a little; loss and capacity within the registered margins; largest variant consistently ahead, not decisive) | laptop, one thread, when layer B passes 300 molecules: `run_export.py` → refit incumbent and 5 blocks + ‖v‖, three seeds each → `stage_readout.py`, paired per-molecule test (rule registered 20:3x) | layer-B count (three shards at ≈ 55–57 each on 26 Sep 20:xx; 300 in the corpus ≈ Mon/Tue) | stage 4 early next week; stage 5 (QM9 pretraining) after the 28th |

## Waiting on the user

| task | why | what is needed | when |
|---|---|---|---|
| Hetzner credit | usage ≈ €1.60/h against €300 (raised 26 Sep 11:xx) | the user raises when I warn; I warn a day ahead | Monday |
| Anthropic Console key for module 07's LLM run | the rubric's own-model run; the deterministic policy is the reference until then | the user sets `ANTHROPIC_API_KEY` (never in chat); then `M07_LLM=1 STEWARD_MODEL=claude-sonnet-5 make_notebook.py` | when convenient |
| Rung C decision | train the equivariant Δ-Hessian model on the pool now or after the 28th (pre-registration 25 Sep; model built and tested 25 Sep 23:1x) | the conversation of Sunday evening | Sun evening |

## Fixed appointments

| when | what | prepared by |
|---|---|---|
| Sat evening | module 06 notebook run done 20:0x (6 of 7 read-outs met); hel1-23 stays for the standout chains through Monday (the user, 20:3x) | done |
| Sun 20:00 | interim layer-B reading (`e7_rungB_pairs.py … --split layerB --sizes all --seeds 0,1,2`, plain and `--tune --tune-stage2`), read against both prediction sets | me |
| Sun evening | rung C decision; E8 naphthalene read-out if the chain finished | the user + me |
| Mon 28 Sep | supervisor conversation; the Monday package (reading copy, cover note, two-horizon note) current as of Sunday night | me |

## Desk work queue (quiet hours, in order)

1. Standout module artefacts: README, requirements, DESIGN_2026-09-27 written 08:5x; still to do: `notebook/make_notebook.py` (rebuilds the read-outs from the committed JSONs, one small molecule's curves live), `make_summary.py` report, `PROVENANCE.md`; outcome sections for `all_p2s1` and `all_p2s1A` when they land.
2. P2 stages 2–5 as registered (ranking loss, capacity, data growth, QM9 pretraining) — only after stage 1 is read; never a negative sentence before stage 5.
3. Cation affordability line in the reading copy once naphthalene⁺ is in (three points).
4. The band-prior finding (≈ 45 % of off-diagonal power in band) — to discuss with the user before the 28th, not to act on.
5. Standout pattern proposer at CC level: a test on the anchor's real responses (naphthalene deck) — after the 28th.
6. Standout: adaptive ordering P0+A / P1+A / P2+A — built and dry-run 22:0x (rule corrected: optimism for untouched pairs; 7 tests); queued on hel1-23 as `band_p2s1A` right after `POOL all_p2 DONE` (chain `chain_p2s1c`), then the wide pool with p2s1; read with `readout.py` against S5 and the prediction.
7. Anchor: the noise floor is read (decision 45 outcome, 02:0x); left for the Monday package: quote it in the reading copy's error budget and the pilot-note inventory (f). The laptop's 8 threads are free (the user decides Sunday evening what runs there).
8. After the 28th, on the user's word (27 Sep 08:3x): pre-register and build (a) the wide-candidate deck with the learned order and a stop rule on ρ_off in `probes/dryrun_dft_delta_recovery.py build_deck`; (b) the cheap proxy-of-the-answer input for P2/P1 (small-basis or semi-empirical Δ) and its test on the 300 molecules; (c) stage 5 (QM9 pretraining). Pre-registrations (a) and (b) written 27 Sep 08:4x (`PreRegistration_2026-09-27_Wide_Candidate_Deck_Stop_Rule.md`, `PreRegistration_2026-09-27_Cheap_Proxy_Input.md`).
9. Monday package (the user, 27 Sep: "doe 1 t/m 5"): weekend notes written 08:5x in the reading copy (§3.4 deck, §3.5 weekend), the cover note and the two-horizon note, each with a placeholder for the 20:00 layer-B reading; after 20:00: fill the three placeholders, run `probes/check_reading_copy_numbers.py`, commit. The 20:00 command is rehearsed (`scratchpad/fetch_layerB_shards.sh merge`, then `e7_rungB_pairs.py … --split layerB --use-analytic --sizes all --seeds 0,1,2`, plain and `--tune --tune-stage2`; smoke 08:5x OK on 233 molecules).

## Guards on this file

Every row names a file or a log; no numbers without a source; stamps from `tools/stamp.py`; the ledger gets the outcome, this file loses the row.
