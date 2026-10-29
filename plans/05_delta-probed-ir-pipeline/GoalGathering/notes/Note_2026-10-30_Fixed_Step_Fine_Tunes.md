# The results built on a fixed-step fine-tune (TASKS 145, 30 Oct 2026)

Decision 51 asks every training to stop on a validation split. The fine-tune of a trained network onto a few anchors did not: until
28 Oct both of its implementations ran a fixed budget — `m05/rungC_cc_transfer.finetune` for `--epochs` (300 by default) and
`m05/proxy_transfer_check.py`'s modes head_l2, head, head_all and scratch for `--steps` (3000 steps, epochs = ⌈3000 / k⌉). The
early-stopped modes (`finetune_early_stopped`: head_all_es, body1_es) exist since 28 Oct, and the anchor count's registered meaning makes
body1_es the CC step's fine-tune (R2). This note lists what was read with the fixed budget, what each result decided, and where it still
stands. Found by `grep` over the callers of `finetune(` (`rungC_cc_transfer.py` lines 469 and 513, `proxy_transfer_check.py` line 179);
no `--predict` output (the fit on all anchors) exists.

| result | when (ledger) | run | what it decided | where it stands |
|---|---|---|---|---|
| T3, the CC transfer built and read on DZ anchors | 2 Oct | `rungC_cc_transfer.py`, `out/T3_cc_transfer_seed*` | the transfer step exists and is read leave-one-anchor-out | a chain-34 read; recorded, carries no current claim |
| Chain 33: five against four anchors | 7 Oct 05:4x | `out/T3_five_anchors_c34_*`, `T3_four_anchors_c34_*` | naphthalene's in-plane transfer 6.52 → 5.83 cm⁻¹ with a fourth training anchor | chain 34; nine–eleven anchors, no current claim |
| Chain 33c and its follow-ups (A), (B) | 7 Oct 21:0x, 21:4x | `out/T3_tz_anchors_c34_*`, `T3_seed_means_tz_vs_dz_c34_*` | hypothesis H (the out-of-plane error halves on TZ-tier anchors); (A) the TZ-tier standard is head-tuned with λ = 1 | the composite TZ tier stands as the anchor standard (an anchor property, not a fine-tune one); (A)'s choice of fit mode is replaced by R2 |
| T3's band heights on benzene (overlap 0.37) | 9–10 Oct | `out/T3_tz_intensity_matched_c34_*` | the CC-level overlap quoted by module 08's certificate and the Atlas | removed from module 08's certificates on 29 Oct (decision 65 night); **the Atlas's benzene anchor card still shows chain 34's held-out test 0.37** (`spectrum.test_prediction` reads `T3_tz_folds_c34_*`) until the next deploy |
| T3 folds, pyridine and low-symmetry APTs; lever 6b | 10–12 Oct | `out/T3_tz_folds_c34_*`, `T3_tz_pyridine_apt_c34_*`, `T3_tz_lowsym_apt_c34_*` | 6b: the λ = 1 fine-tune costs mode shapes, three of three | chain 34; a property of that fine-tune, recorded |
| Set three's whole-head repeat read (R-A, R-B) | 21 Oct 09:22 | `rungC_cc_transfer.py` | R-A between (CH-oop 7.24 → 6.25), R-B passes 3 of 3 | led to TASKS 130 below |
| The proxy check (PX): L1, L2 | 22 Oct 02:1x | `proxy_transfer_check.py`, `out/proxy_check_2026-10-21/` | L1 holds: λ 1 stays at 8–10 cm⁻¹ CH-oop at every k | the reservoir and read set it built are the anchor count's; its fine-tune reading is superseded by the count |
| TASKS 130: the whole head is the CC transfer's fit mode | 26 Oct 07:2x | `rungC_cc_transfer.py --fit-mode` (default head_all) | the fit mode for a fit on all anchors | **open**: the default is a fixed-step mode; the count's meaning makes it body1_es — set when the anchor decision of November sets the CC step |
| Arm (a): 3 cm⁻¹ CH-oop at k ≈ 139 | 27 Oct 12:5x | `anchor_price_plan.py` (head_all, fixed) | the first anchor price | superseded by the count (167, body1_es) |
| Arm (c): C1 and C2 | 28 Oct 20:5x | `anchor_price_plan.py` (head_all, fixed) | **C1: a cell cover does not beat random draws** — the anchor plan is priced with the reservoir's mix, not a cover (29 Oct 23:5x); C2: CH-oop none by 200 | C2 is superseded by the count; **C1 rests on the fixed-step fine-tune and is used by the price** — its re-read with body1_es is the one open check |
| The recipe follow-up (R0, R1, R2) | 29 Oct 04:4x | `proxy_transfer_check.py` | R0 (fixed) 3.33 against R1 2.73: the fixed budget under-fits | the reason the count uses an early-stopped fine-tune |
| The anchor count | 29 Oct 18:1x | chain AC | count 167 on body1_es (R2) | not affected: its outcome is early-stopped; the head_all row of its table is fixed-step and is shown, not read |

**What follows.** Two results still carry a decision and rest on the fixed budget: arm (c)'s C1, which the anchor price now uses, and the
fit mode of TASKS 130. C1's re-read with body1_es is a proxy run on the laptop (no anchors; the 9–11 existing ones stay untested), cheap
next to the count's seven hours: the cover and random draws of arm (c) at k = 5, 10, 20, fine-tuned with body1_es. The fit mode is set
with the CC step after November's decision. The Atlas's benzene card goes with the next deploy, which waits for the user.
