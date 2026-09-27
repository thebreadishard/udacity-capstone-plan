# Decision memo, 27 September 2026 — rung C: train tonight on the free laptop, or after the 28th?

*For the Sunday-evening decision named in the weekend plan. One page. Plan of record: `PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md`
(read-outs R1–R5, predictions, the "nothing before 28 September" guard, build status of 25 Sep 23:1x). Nothing in this memo changes that
pre-registration; it only asks when its test run happens.*

## What the test is

The equivariant Δ-Hessian model (`m05/rungC_equivariant.py`: registered inputs only, PaiNN-type body, tensor head, 171,554 parameters; equivariance
checked to 1.5e-15, five tests) is trained on the same 175-molecule pool, sizes 45 / 100 / 175, seeds 0–2, as the pair model whose numbers are the floor
(`out/E7_rungB_2026-09-23_analytic.json`). Read-outs: R1 ratio at 175 on both hold-outs (pass ≤ 0.35 / 0.38; fail ≥ 0.43 / 0.47), R2 slope, R3 corrected ω,
R4 within-orbit spread (a bug check), R5 the class breakdown. Two variants were registered: **C1** (train from scratch) and **C2** (body pretrained on the
41,645 Hessian-QM9 molecules, 2–4 CPU-hours once, then fine-tuned). Predictions on record: C1 0.40 / 0.43 (a small gain from directions), C2 0.34 / 0.37.

## Why the question is open tonight

The pre-registration's guard was "nothing runs on the laptop while an anchor-class run is on it; nothing before 28 September". The anchor and its
densification finished on 27 September 01:51; the laptop is free for the first time since 20 September. The guard's reason has lapsed; its date has not.
Changing the date is the user's call, which is why this memo exists.

## Option A — C1 tonight on the laptop (recommended)

- **Cost:** minutes per seed at 8 threads; 3 sizes × 3 seeds ≈ 1–2 hours in total, after the 20:00 layer-B reading (which needs the laptop for ≈ 30 min).
  No server, no money, no new data.
- **What it buys for Monday:** a measured number for the one architectural question the supervisor is most likely to ask ("why a pair model and not an
  equivariant one?"): R1 pass, fail, or between — read against predictions written on 25 September.
- **Risks:** (i) a *fail* at 08:00 Monday with no time to digest — but the verdict rule already says what a fail means (directions do not help at 175;
  re-test at 600 molecules), so it is a scheduling outcome, not a verdict on the idea; (ii) a between — reported with R5, no change of plan; (iii) a bug
  found under time pressure — the smoke and the five tests make this unlikely, and the run is a probe, not a promotion.
- **Guard kept:** nothing else starts on the laptop; the run is logged hourly; the read-out is written into the pre-registration's outcome section before
  anything is said about it.

## Option B — C1 and C2 after the 28th

- **Cost:** none tonight; C2 needs the QM9 Hessian set downloaded and a 2–4 CPU-hour pretraining, which is better done unhurried.
- **What it buys:** the two variants read together, as the pre-registration frames them (the prediction says the pretraining is what carries).
- **What it loses:** Monday's conversation has the pair-model floor and the layer-B curve, but no equivariant number; the architectural question is
  answered with "built, tested, registered, runs this week".

## Option C — C1 tonight on hel1-14 instead of the laptop

Not available without cost: hel1-14 runs layer-B shard 3 on all 16 threads since 08:37; a second 16-thread job would slow both. The laptop is the free
machine.

## Recommendation

**A tonight for C1, C2 after the 28th** — the cheap half of the registered test, on the machine that is free, read by the registered rule. If the
20:00 reading shows the layer-B curve flat on the parents, A becomes more valuable, not less: the equivariant model is the registered next lever for
exactly that case. If the user prefers B, nothing is lost but one number on Monday.

## What must exist before option A can run (status 10:0x)

The model, loader and loss exist and are tested; **the training-and-read-out driver does not yet** (`rungC_equivariant.py` has `--smoke` only). It is being built today as desk work (`m05/rungC_train.py`: the pair model's pool, sizes, seeds and hold-outs from `e7_rungB_pairs.py`; training with `loss_terms`; the same read-outs R1–R5 through the pair model's projection code), smoke-tested on water and one corpus molecule, and *not run* on the pool before the user's word. **Update 10:0x: the driver exists and is smoked** (`m05/rungC_train.py`; 12 epochs on 5 molecules learn — Cartesian residual ratio 0.95, corrected ω 20 vs the zero rule's 24 — mechanics only). Two build notes, recorded in the pre-registration: the output is scaled by the training set's RMS ΔH (as the pair model scales its targets per class), and the internal-ΔF auxiliary term is taken relative to the target's own mean square (the raw term is ~10⁹ in a.u.). The A + A2 pool is exactly the registered floor's 175 molecules today (`--pool-layers A,A2`), so R1–R3 compare like with like; the pair model can be re-run on it in minutes for a same-night floor. Full C1 run (3 sizes × 3 seeds × 60 epochs) ≈ 20–30 minutes on the laptop. Option A is available.

## What I need from the user tonight

One word: "A" or "B". With "A" I launch after the 20:00 reading with `launch_detached.sh` (hourly heartbeat, alarm file), read R1–R5 in the morning, and
put the outcome in the pre-registration and the reading copy's §3.5 note before the conversation.
