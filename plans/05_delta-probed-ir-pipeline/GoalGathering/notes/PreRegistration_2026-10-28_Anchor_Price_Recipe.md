# Pre-registration — the anchor price's recipe follow-up: is arm (c)'s count the data's or the fine-tune's?

28 October 2026, 22:2x. Written before any run of the follow-up, after arm (c)'s read (ledger 28 Oct 20:5x and its two notes). TASKS 82;
the user, 28 Oct: 'Oké' to the design, 'voorzichtig met 1.3' (v1.3's weights are not loaded; they are mirrored and read-only, ledger 21:4x).
Code: `probes/anchor_recipe_plan.py`; `m05/proxy_transfer_check.py` modes `head_all_es` and `body1_es`; `m05/rungC_cc_transfer.py`
`finetune_early_stopped` and mode `head_all_body1` (branch anchor-recipe). Tests: `tests/test_anchor_recipe_plan.py` (9, synthetic
records with every outcome), the new tests in `tests/test_rungC_cc_transfer.py` and `tests/test_proxy_transfer_check.py`, and the
regression pin `tests/test_proxy_transfer_check_regression.py` (the existing modes unchanged to the bit).

## Why

Arm (c)'s registered read (`out/anchor_price_2026-10-28/anchor_price_read.md`): the whole-head CH-oop does not reach 3 cm⁻¹ by k = 200
(3.39 ± 0.15 at 100, 3.33 ± 0.03 at 200; arm (a) 3.17 and 2.82), and the CH-stretch control failed (crossing 56 against arm (a)'s 17).
Outside the registration, three things point at the fine-tune rather than the count:

1. Arm (c)'s fine-tunes end at about twice arm (a)'s training loss at every k (k = 100: 0.037–0.052 against 0.021–0.029; k = 200:
   0.046–0.085 against 0.031–0.032), on the very molecules they are fitted to.
2. The recipe is a fixed budget of 3000 optimiser steps whatever k: 15 epochs at k = 200, 150 at k = 20. Only the head and α move; the
   body is frozen. Arm (c)'s change depends on the ring context, which the head can only follow if the frozen body already separates it.
3. The two arms' bases differ in more than the distortion: arm (a)'s base (21 Oct) had analytic labels for 601 molecules, arm (c)'s
   (28 Oct) for 862. The read targets are the same (the zero rule is identical).

## The design

**Arms.** (c): arm (c)'s base as it is (`base_c_model_n750_seed{0,1,2}.pt`). (a2): arm (a)'s base again — chain 34's recipe, arm (a)'s
pool and exclusions, arm (a)'s family scales from the proxy check's manifest (ring-ip −0.34, CH-stretch −0.79, CH-oop −0.43, other −1.16)
— trained now, so on the same 862 analytic labels as (c). The distortion is then the only difference between the arms. Neither base is
v1.3's file: v1.3 has seen the reservoir and the read set, and has learned the undistorted correction the fine-tunes must reach.

**Recipes.** R0 = `head_all`, 3000 steps (arm (c)'s; arm (c)'s own R0 records are read again, arm (a2) runs it). R1 = `head_all_es`:
the whole head and α, fitted on 85 % of the k molecules (`inner_split`, per seed), the loss on the other 15 % after every epoch, the best
epoch's weights restored, stopped 10 epochs after the best or at 60 epochs (four times R0's 15 at k = 200). R2 = `body1_es`: R1 with the
body's last interaction block free as well. Learning rate 1e-3 throughout.

**Draws.** The proxy check's reservoir (200) and read set (343, analytic labels); k = 100 (the same three draws as arms (a) and (c)) and
k = 200 (the whole reservoir); seeds 0–2. Chain AR, 14 steps: base (a2), its registry entries, arm (c)'s R1/R2, arm (a2)'s R0/R1/R2.

## Lines (read by `anchor_recipe_plan.py read`; mean ± se over seeds × draws; 'below' = lower by more than twice the combined se)

Per recipe:

- **G — the control:** arm (c)'s CH-stretch not above arm (a2)'s at k = 100 and at k = 200 (CH-stretch has the same factor in both arms).
- **F — the fit:** arm (c)'s training loss at k = 200 within a factor 1.5 of arm (a2)'s.
- **Cap:** the cap binds when more than a third of arm (c)'s runs at a k keep an epoch within 10 % of the cap (decision 51).
- **P — the price:** arm (c)'s CH-oop at k = 200 at or below 3 cm⁻¹ ('at the line'), and below R0's ('below R0').

**Outcome**, over R1 and R2 where G holds: **recipe-limited** (one is at the line and below R0); **partly recipe** (one is below R0, none
at the line); **undecided: the cap binds** (none below R0, the cap binds in one); **data-limited** (none below R0, no cap); **no
reading** (G fails for both). Reported beside the lines, not judged: every family, both arms, all three recipes at both k; arm (a2)'s R0
against arm (a)'s published R0 (what the 261 extra analytic labels did).

## Predictions

- **G fails under R0 and holds under R1 and R2.** Arm (c)'s R0 control failed on the same draws, and the a2 base changes only the labels.
- **F fails under R0 and holds under R1 or R2.** Fifteen epochs at k = 200 do not reach the fit; up to sixty do.
- **Outcome: partly recipe or recipe-limited; CH-oop (c) at 200 near 3.0 under R2, about 3.1 under R1.** The flat stretch from 100 to
  200 (3.39 → 3.33) is what an under-fit looks like; a freed body block lets the ring context reach the head.
- Arm (a2)'s R0 within 0.2 cm⁻¹ of arm (a)'s on every family at both k (the extra labels are a small change of the base).

## What each outcome means for claim 3

- recipe-limited → the count is not arm (c)'s 'above 200'. The winning recipe (the lower mean validation loss of R1 and R2 at k = 200,
  never the read set) is re-run on arm (c)'s whole curve (k = 5 … 200, a registration of its own) and the anchor plan waits for that
  count. The recipe also replaces 'head_all, 3000 steps' as the fine-tune of the CC step.
- partly recipe → the count stays above 200 under the measured change, the better recipe is carried into the anchor plan's curve.
- data-limited → arm (c)'s count stands: more than 200 anchors for 3 cm⁻¹ CH-oop under the measured change; the anchor plan prices it.
- undecided: the cap binds → the follow-up runs again with a higher cap before anything is priced.
- no reading → the arms differ by more than the distortion; the difference is found before any price is read.
- Limits stated now: one reservoir and read set; k = 100 and 200 only; the 15 % validation share costs the fit 30 of 200 molecules,
  as it would cost a real anchor set; the proxy carries only the change measured on nine anchors.

## Order and cost

Laptop only, after the merge of branch anchor-recipe. Base (a2) ≈ 2 h (base (c) took 1 h 58 min); the fine-tunes ≈ 4 h by arm (c)'s
step times (a k = 100 run of three draws took ≈ 6.5 min at 3000 steps; R1 and R2 take up to 60 epochs, R2 more per step) — about 6 h
in all, measured by a smoke on the real corpus before the launch. Memory: arm (c)'s runspec bound, 7.7 GB. Read by 18 Nov.
