# Pre-registration — C1 read again with the early-stopped fine-tune (TASKS 145)

30 October 2026, 20:5x. Written before any run of this re-read; the run waits for the user's word. TASKS 145 (the fine-tunes outside
decision 51), TASKS 82 (the anchor price), TASKS 140 claim 3. Code: `probes/c1_reread_plan.py` (plan and read); tests
`tests/test_c1_reread_plan.py` (synthetic records: two sizes below holds, one does not, a difference just inside two se does not count, a
missing record is refused; the chain's modes, bases and reservoirs).

## Why

Arm (c)'s C1 (`PreRegistration_2026-10-27_Anchor_Price_Arm_C.md`) asked whether a covering selection of anchors — chosen to hold the anchor
plan's cells (adjacency class × ring context × aza × charge) — teaches the network more than random draws of the same size. It was read on
28 Oct with the fine-tune of that day, head_all for a fixed 3000 steps, and did not hold: CH-oop, covers against random draws, 5.84 ± 0.11
against 6.74 ± 0.17 at k = 5 (below), 5.00 ± 0.16 against 5.26 ± 0.10 at k = 10 (inside two se), 4.50 ± 0.10 against 3.99 ± 0.08 at
k = 20 (above) (`out/anchor_price_2026-10-28/anchor_price_read.md`). The anchor plan has since been priced with the reservoir's mix, not a
cover, and the blog post of 30 Oct says the cover did no better.

The recipe follow-up of 29 Oct then found that the fixed budget under-fits (R0 3.33 against R1 2.73 at k = 200), and the anchor count
adopted the early-stopped recipe R2 (body1_es, early stopping on an inner validation split, cap 120 epochs) as the CC step's fine-tune
(`Note_2026-10-30_Fixed_Step_Fine_Tunes.md`). C1 is one of two results that still rest on the fixed budget and carry a decision.

## The design

Everything as arm (c) but the fine-tune. Base (c) (`out/anchor_price_2026-10-28/base_c_model_n750_seed{0,1,2}.pt`, the label distorted by
the anchors' measured change of correction), the proxy check's reservoir (200) and read set (343, analytic labels). (i) Random draws:
k = 5, 10, 20, the same three draws per k as arm (c) (`proxy_transfer_check.py --k --subsets 3`, seeded), seeds 0–2. (ii) Covers: arm (c)'s
nine cover files (`cover_k{5,10,20}_d{0,1,2}.txt`), one draw each, seeds 0–2. Every fine-tune is R2: `--modes body1_es --es-max-epochs
120`, as the anchor count's. 9 + 27 runs of `proxy_transfer_check.py`, chain C1R (`probes/runs/c1_reread.json`, written by `plan`).

## The line (read by `c1_reread_plan.py read`; mean ± se over seeds × draws)

- **C1 on R2 — the cover pays:** the covers' CH-oop below the random draws' by more than two combined standard errors at two of k = 5,
  10, 20 — the registered rule of 27 Oct, unchanged; only the fine-tune differs. The fixed-step reading is printed beside it.

## Prediction

**C1 does not hold on R2 either.** Early stopping changes how well each fine-tune fits its molecules, not which molecules carry
information. At k = 5 the covers hold no single-ring molecule, a third of the read set, while three random molecules of the reservoir's mix
usually include one; at 10 and 20 the random draws already hold all three ring contexts. In this proxy the change of correction follows
the ring context alone, so cells beyond the context carry nothing by construction. Expected: cover ≈ random at 10 and 20; at 5 the cover
may again be lower (it was, 0.90 cm⁻¹, under the fixed budget), which is one size, not two.

## What each outcome means

- **Does not hold** → C1 stands under the early-stopped fine-tune; the anchor plan keeps the reservoir's mix (the cheapest molecules with
  every ring context present), the price bracket of 29 Oct (€729–3,026) and the blog post stand, and TASKS 145 keeps only the fit mode,
  which waits for November's decision.
- **Holds** → a cover does teach more under the CC step's own fine-tune: the anchor plan is priced again with a cover rule before
  November's decision (TASKS 82), and the blog post of 30 Oct gets a dated addendum.
- **Limits, stated now:** the proxy carries only the ring-context structure measured on nine anchors, so a dependence of the real CC
  correction on cells beyond the context cannot show here, in either reading; three seeds × three draws per size; the base is chain 34's
  750-molecule recipe (arm (c)'s), not the carried version.

## Order and cost

`python probes/c1_reread_plan.py plan modules/05_support_predictor/out/c1_reread_2026-10-30`, the run spec `probes/runspecs/c1_reread.json`
(chain_runner, memory bound 7.7 GB as the count's, nothing beside it), its dry run, then the launch on the user's word. Measured on arm (c)
(28 Oct): its random fine-tunes at k = 5–20 took ≈ 7 min per run of three draws, its covers ≈ 5 min per run with two modes → ≈ 1 h + ≈ 2 h,
about three laptop hours. The read follows the chain's end.

## Read (30 October 2026, 23:1x)

Chain C1R ran 21:07–23:03, 36 of 36 outputs; `out/c1_reread_2026-10-30/c1_reread.md`. CH-oop, random draws against covers (mean ± se over seeds × draws): k = 5 7.51 ± 0.27 against 6.51 ± 0.13 (below), k = 10 5.92 ± 0.14 against 6.19 ± 0.34, k = 20 4.75 ± 0.24 against 4.72 ± 0.08 — below at one size, the rule asks two. **C1 does not hold on R2**, as predicted, and as under the fixed budget. One fine-tune of 54 reached its best epoch near the cap (rd_k5_seed1, 115 of 120); more epochs could only lower the random draws at k = 5, so the verdict does not depend on it. The anchor plan keeps the reservoir's mix.
