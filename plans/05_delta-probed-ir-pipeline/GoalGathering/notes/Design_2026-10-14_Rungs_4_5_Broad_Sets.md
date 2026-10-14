# Design note, 14 October 2026, 19:4x — rungs 4 and 5 as broad sets (proposal; nothing launched, spending on the user's word)

*The user, 14 Oct evening: the ladder is climbed slowly, small to large (decision 39, 14 Sep: 'Laten we traag doen, met ionen'), and 'een
trede is niet 1 molecuul … het is een zo groot mogelijke set van moleculen van die orde van grootte'. Then 'Ja oké' to a proposal: which
scaffolds, how many per scaffold (decision 52), what it costs and where it runs, registered first with the learning-curve clause.*

## 1. Where the rungs stand (counted 14 Oct 19:4x)

Corpus manifest, rows `done`, by ring count (five-membered rings included); pool 3 is not merged yet and is counted from its shards.

| rung (rings) | done | scaffolds | atoms | notes |
|---|---|---|---|---|
| 1 | 239 | 8 | 8–20 | |
| 2 | 538 | 18 | 15–26 | |
| 3 | 185 | 13 | 20–28 | |
| 4 | 84 | **2** | 26–30 | fluoranthene family 51, pyrene family 33 (layers A/A2); pool 3 shard b adds 15 aza-pyrenes/aza-fluoranthenes |
| 5 | 0 | — | — | pool 3 shard b: 16 done over six scaffolds (perylene, benzo[a]pyrene, benzo[e]pyrene, picene, two more), ≈ 5 per scaffold |

**The benzenoid core of rung 4 is missing.** Of the six closed-shell four-ring benzenoids (enumerated 14 Oct: tetracene, chrysene,
benz[a]anthracene, benzo[c]phenanthrene, triphenylene, pyrene), only pyrene has a family; the other five exist only as one pending parent row
each (layer G). Tetracene is the mandate's S3 molecule and the acene stress branch of decision 39. By decision 52 (≈ 30 mixed children cover
a scaffold family, ≈ 60 finish it), rung 4 is two families wide and rung 5 has no covered family.

## 2. Proposal

**Step 0 — no new cost (the user's word on pool 3's free threads, open since this morning).** Pool 3's runner b finished and its 8
threads idle on the paid `pool3` CPX62. The 29 pending neutral P3 rows (aza-four-rings and five-rings — rungs 4 and 5) move to b; runner a
keeps the cations. Needs: runner a's queue told to skip those 29 ids (`run_corpus.py` has no such switch yet: one exclude file with a test), and a dry run on a manifest copy.

**Step 1 — rung 4 covered (registered first).** The five missing benzenoid families, each parent + 29 mixed mono-substituted children
(layer B's substituent scheme through `probes/pool3_candidates.children`, round-robin over substituents, n_atoms ≤ 40, no duplicate of the
manifest): **150 molecules**, 30–34 atoms. One family is held out whole as the rung's transfer test (proposed: **tetracene**, the acene branch
and S3's molecule — its 30 rows are test rows, never trained); the other four train. Labels by the analytic route (`analytic_hessians.py`,
both functionals, route C APT), as every new layer since 5 Oct.

**Step 2 — rung 5, only after rung 4 holds (decision 39).** Breadth first over the five-ring families with ≤ 40 atoms (15 benzenoids by the
enumeration, plus benzo[b/j/k]fluoranthene and cyclopenta[cd]pyrene): pool 3's six scaffolds topped up to 30 each first, then new families.
Priced now as an outlook only; registered and decided after step 1's read.

## 3. Price (labels server lane fit, measured)

`probes/price_large_labels.py`'s fit on the labels server's 387 lane times (t ∝ nbas^3.40–3.45, + 10 % optimisation allowance; one lane = 8
threads on the CCX53, €0.855/h ÷ 4 lanes = €0.214 per lane-hour). The largest measured molecules are 30 atoms / 307 basis functions at
6.4–7.0 h; rung 4's children (313–324 functions) sit just beyond the data, rung 5's (343–388) further out.

| | atoms | lane-hours per molecule |
|---|---|---|
| rung 4 parent C18H12 | 30 | 5.8–5.9 |
| rung 4 child (methyl / ethynyl) | 32–33 | 7.2–8.3 |
| rung 5 child C21H14 … C24H14 | 35–38 | 9.8–15.4 |

- **Step 1:** 150 × ≈ 7.5 ≈ **1,125 lane-hours** → on the CCX53 (4 lanes) ≈ **12 days, ≈ €240**, after lever 5 (TASKS 49, ≈ 22–26 Oct) →
  ≈ 7 Nov. Alternative: two more CPX62 (the shared-vCPU limit leaves room for two), 2 lanes each, €0.104 per lane-hour if a CPX62 lane matches
  a CCX53 lane — **not measured**: the first molecule on a CPX62 prices it (time and peak memory at 16 GB per lane; memory beyond 307
  functions is unmeasured, lever 5's caveat). If it matches: ≈ 12 days, ≈ €120, and it starts as soon as the servers exist.
- **Step 2 (outlook, not proposed now):** ten five-ring families × 30 ≈ 300 molecules × ≈ 12 lane-h ≈ 3,600 lane-hours ≈ €770 on the CCX53
  rate (≈ 37 CCX53-days) — the size at which the PC question (TASKS 58) returns with a number.

## 4. Registration (to be written before step 1 launches)

- **Read:** the rung-3 → rung-4 transfer per family (decision 39's go/no-go: the held-out family within 2.5 cm⁻¹ per band family, the
  carried rung-C recipe, the proxy target), and the size penalty q as chain 39 read it, with and without rung 4 in training.
- **Learning curve:** the four training families at 0 / 10 / 20 / 30 children each (nested subsets of the frozen list, `curve_rank` as pool 3),
  three seeds; 'still learning' = error at 30 below error at 10 by more than twice the combined SE and the last step still down → that family
  goes to 60 (decision 52's 'finish'), priced; a flat curve → the search first (features, model class), never a verdict at 30.
- **No scope-reducing fallback:** a family that cannot be computed (noise, cost) is re-priced and the read waits; the held-out family is not
  swapped after the fact.

## 5. Decisions for the user

1. Step 0 now (no new cost): the 29 pending P3 neutrals onto runner b's free threads.
2. Step 1's place: the CCX53 after lever 5 (≈ €240, ≈ 7 Nov), or two new CPX62 priced on their first molecule (≈ €120 if a lane matches,
   earlier start).
3. Tetracene as rung 4's held-out family (or another, chosen now, before any number).
