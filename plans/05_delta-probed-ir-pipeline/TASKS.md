# Open tasks — plan 05 (the working list; the ledger is the record)

*Opened 26 September 2026, 13:4x, on the user's word ("Goed idee, doen"). One row per open task: what, why it exists (the decision or question behind it),
where it lives, the next check and when. Rows are removed when done (the ledger keeps the outcome); rows are edited with the clock's stamp. Read it
with `bash probes/state.sh`; both together are the picture. Rules: nothing here is a plan of record — the pre-registrations and the weekend plan are;
this file only says what is running or waiting and who acts.*

## Running (machines)

| task | why | where | next check | ends |
|---|---|---|---|---|
| Densification, mode 12 (4 points, decision 45) | the anchor's family reading on mode 12 needs the points between the sealed ones | laptop WSL, `probes/results_m1/naphthalene_cc-pvtz_tight_m3/`, `anchor_watch` | heartbeat in `state.sh`; commit `m1_rows.json` when the 4 points are in | point 2 of 4 on 26 Sep 11:0x; ≈ 2 more days |
| Layer-B shards 0/1/2 | the layer-B learning curve (proof of learning; interim reading Sun 20:00, 300-table when all five shards have their first 20) | hel1-16 (shard 2, 46.62.227.91), hel1-18 (2.29.40.182), hel1-21 (2.29.45.10); `corpus/layerB_shard*of5.log` | monitor line every 10 molecules; counts 42/43/44 = 129 at 12:3x | run on; merge with `merge_shards.py` for readings |
| Naphthalene⁺ ULNO-CCSD(T) price (obstacle 9) | the cation cost ratio c at the label level (decision 41's condition) | hel1-14 (89.167.29.36), `/root/cations/price/naphthalene/` | monitor line `PRICE naphthalene DONE`; then `cation_price_readout.py`, pre-registration outcome, reading-copy note | q = 0 done (34,121 s); q+1 running; ≈ Sun 03:00–04:00 |
| E8 naphthalene CC Hessian (three partial runs) | locality one bond further at CC level, on a two-ring molecule | CCX53 (77.42.67.27), `/root/e8/results/naphthalene_ccpvdz/` | monitor line (verdict/finished/Traceback); 20 of 30 gradient files at 12:3x | ≈ Sun evening; then assembly + `e8_cc_locality.py` + `e8_between_extension.py` (in the chain) |
| Module 06 seed 2 training | pre-registration wants three seeds before the 10,000-sample notebook run | CCX53, `/root/m05run/06_generative_candidates/notebook/out/seed2/` | monitor line at epochs 10/15/20 and `ENDED` | ≈ 19:00 Sat; then `M06_REUSE=1 make_notebook.py` on the CCX53 |
| Standout pattern proposer, round 2 (band pool, all orderings) then E2 (all pairs) | is the meetvolgorde a lever, and does the learned embedding add to the scorer (pre-registration 26 Sep) | hel1-23 (157.180.32.149), `/root/pp/plan/modules/standout_pattern_proposer/out/sim/{band_p2,all_p2}_*`, chain `chain_p2` | monitor line `POOL band_p2 DONE` / `POOL all_p2 DONE`; fetch merged JSON, `readout.py`, outcome section | band_p2 done 14:19 (read 14:3x); all_p2 ≈ 17:30–18:00 |
| P2 stage-1 search (lr × width, patience 20; 18 fits) | the learned embedding gets a fair chance before any sentence about it (the user, 12:1x) | laptop, one thread, `modules/standout_pattern_proposer/out/p2s1_*`, log `out/p2_stage1_2026-09-26.log` | `STAGE1_DONE` in the log; pick by validation MSE; ship the chosen recipe's weights to hel1-23 with the new `embed_scorer.py` | ≈ 16:30 |

## Waiting on the user

| task | why | what is needed | when |
|---|---|---|---|
| Extra CPX62 for layer-B shard 3 | five shards for the 300-table; hel1-23 can take it over after the standout pools | the user: keep hel1-23 or create one; I bootstrap with `bootstrap_shardB.sh <ip> 3 5` | this evening |
| Hetzner credit | usage ≈ €1.60/h against €300 (raised 26 Sep 11:xx) | the user raises when I warn; I warn a day ahead | Monday |
| Anthropic Console key for module 07's LLM run | the rubric's own-model run; the deterministic policy is the reference until then | the user sets `ANTHROPIC_API_KEY` (never in chat); then `M07_LLM=1 STEWARD_MODEL=claude-sonnet-5 make_notebook.py` | when convenient |
| Rung C decision | train the equivariant Δ-Hessian model on the pool now or after the 28th (pre-registration 25 Sep; model built and tested 25 Sep 23:1x) | the conversation of Sunday evening | Sun evening |

## Fixed appointments

| when | what | prepared by |
|---|---|---|
| Sat evening | module 06 notebook run with three seeds on the CCX53; delete/reassign hel1-23 | me (run), the user (servers) |
| Sun 20:00 | interim layer-B reading (`e7_rungB_pairs.py … --split layerB --sizes all --seeds 0,1,2`, plain and `--tune --tune-stage2`), read against both prediction sets | me |
| Sun evening | rung C decision; E8 naphthalene read-out if the chain finished | the user + me |
| Mon 28 Sep | supervisor conversation; the Monday package (reading copy, cover note, two-horizon note) current as of Sunday night | me |

## Desk work queue (quiet hours, in order)

1. Standout: outcome sections as pools finish; module artefacts (design note, notebook, report, requirements) once E2 is read.
2. P2 stages 2–5 as registered (ranking loss, capacity, data growth, QM9 pretraining) — only after stage 1 is read; never a negative sentence before stage 5.
3. Cation affordability line in the reading copy once naphthalene⁺ is in (three points).
4. The band-prior finding (≈ 45 % of off-diagonal power in band) — to discuss with the user before the 28th, not to act on.
5. Standout pattern proposer at CC level: a test on the anchor's real responses (naphthalene deck) — after the 28th.

## Guards on this file

Every row names a file or a log; no numbers without a source; stamps from `tools/stamp.py`; the ledger gets the outcome, this file loses the row.
