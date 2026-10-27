# Pre-registration — the anchor price under the change the anchors measured (arm (c)); a covering selection against random draws

27 October 2026, 12:5x. Written before any run of arm (c). TASKS 82 (the anchor price), TASKS 84 step 4 (the covering selection),
TASKS 140 claim 3 (the count of anchors per accuracy, with prices) for the supervisor meeting of 25 November 2026. Code:
`probes/anchor_price_plan.py`, `rungC_train.py --distortion-file` (branch measured-distortion); tests `tests/test_anchor_price_plan.py`
(11, synthetic records with the regime's edge cases) and `tests/test_rungC_distortion_file.py` (15).

## Why

The proxy check's arm (a) (21–22 Oct; `Design_2026-10-21_Few_Anchor_Proxy_Check.md`) gave the curve the anchor count rests on: the
whole head reaches 3 cm⁻¹ CH-oop at k ≈ 139 molecules (log-linear between 3.17 at 100 and 2.82 at 200). Its base was trained on a label
distorted by **one factor per family for every molecule**. Two facts measured today say that is not the change the anchors show:

1. **The CC correction's CH-oop mean shift follows the ring context.** On the nine anchors with a CC/DZ Hessian (the TZ composite, ratio
   of the CC mean first-order shift to the proxy's): single rings +0.05, −0.06, +0.02 (benzene, fluorobenzene, pyridine); fused rings
   −0.29 to −0.71 (quinoxaline, isoquinoline, quinoline, naphthalene); with a five-membered ring −0.70 and −1.09 (acenaphthylene,
   azulene). The other families' ratios are nearly uniform (other −1.2 to −1.9, ring-ip −1.2 to −2.1, CH-stretch −0.75 to −0.89; azulene's
   other and ring-ip ratios are meaningless because its proxy mean there is near zero, and medians ignore them).
2. **Under arm (a)'s distortion a fine-tune molecule's cells cannot matter.** Exploratory, on arm (a)'s own records: the same read
   molecule's CH-oop error in draws whose molecules held its cells minus in draws that did not, whole head, −0.41, +0.28, −0.22, −0.05
   cm⁻¹ at k = 5, 10, 20, 50 — no sign, against errors of 4–7 cm⁻¹. A family-wide factor is learned from any molecule of the family.

## The design

**Base (c).** Chain 34's recipe, pool and exclusions exactly as arm (a) (`a_exclude.txt`, 750 molecules, seeds 0–2), the training label
distorted by `--distortion-file`: per family, the block in the low level's mode basis is split into its mean part (carrying exactly the
family's mean first-order shift) and the rest, each with its own factor (`rungC_train.distort_blocks`). Factors from `set3_decompose`'s
nine anchors by `anchor_price_plan.family_factors` (medians; the preview of 27 Oct on the stored decomposition, slopes unchanged):

| family | mean factor | rest factor | arm (a), both parts |
|---|---|---|---|
| CH-oop | single 0.02, fused −0.45, five −0.90 | −0.52 | −0.43 |
| other | −1.45 | −0.30 | −1.16 |
| ring-ip | −1.39 | +0.12 | −0.34 |
| CH-stretch | −0.79 | −0.79 (its centred proxy shifts are noise) | −0.79 |

A molecule's context (`anchor_plan.fusion_context`): five when any ring has five members, else fused when a ring atom is shared, else
single (biphenyl is single). Reservoir 89 fused / 67 single / 44 five; read set 168 / 110 / 65.

**Fine-tunes.** The proxy check's reservoir (200), read set (343, analytic labels) and fine-tune protocol (3000 steps, `head_all` = every
head layer + α, the carried transfer mode). (i) Random draws: k = 5, 10, 20, 50, 100, 200, the same three draws per k as arm (a)
(`draw_subsets`, one at 200), three seeds; whole head only (scratch does not depend on the base and arm (a) read it on the same draws).
(ii) Covering selections by the anchor plan's cells (adjacency class × ring context × aza × charge): k = 5, 10, 20, three draws each
(`balanced_cover`: the most weight on cells still thin, ties by a seeded order), three seeds; whole head and scratch. The covers hold
15 / 25–26 / 31 of the reservoir's 38 cells against the random draws' 5–8 / 8–13 / 16–20. **The k = 5 covers hold no single-ring
molecule** (fused 3–4, five 1–2): single rings carry few cells, so the cell rule reaches them last; the k = 10 and 20 covers hold two.

## Lines (read by `anchor_price_plan.py read`; mean ± se over seeds × draws; 'below' = lower by more than twice the combined se)

- **C1 — the cover pays:** the covers' whole-head CH-oop below the random draws' at two of k = 5, 10, 20.
- **C2 — the count:** per family the k at which arm (c)'s random whole-head curve reaches 3 cm⁻¹ (log-linear between the neighbouring k;
  None if not by 200), beside arm (a)'s from its own records (ring-ip 19, CH-stretch 17, CH-oop 139, other None — 3.32 at 200).

## Predictions

- **C1 does not hold.** At k = 5 the covers miss the single rings (a third of the read set), at 10 and 20 the random draws already hold
  all three contexts, and the cells beyond the context carry nothing in this proxy by construction. Expected: cover ≈ random at 10 and 20,
  not below at 5.
- **C2, CH-oop: the crossing stays at k ≥ 100** (arm (a) 139): the per-context change is no smaller on average than arm (a)'s uniform one
  (the change of the mean shift is 0.98, 1.45, 1.90 times the proxy's by context against 1.43 everywhere) and the head has to learn it per
  context. **C2, ring-ip: ≤ 50** (a larger but uniform mean change, a milder rest). **C2, other: reached by 200, and below arm (a) by
  two se at k = 50, 100 and 200** (the rest factor −0.30 against −1.16). **C2, CH-stretch: within a factor two of arm (a)'s 17** (the
  same factor: a control).

## What each outcome means for claim 3

- CH-oop ≥ 100 → the anchor count of 100–200 for the 3 cm⁻¹ line stands under the measured change; the anchor plan prices that count.
  CH-oop < 100 → the count falls with the measured change; the plan prices the new number.
- C1 does not hold → the anchor plan chooses the cheapest molecules with every context present, not a cell cover (cheaper: single rings
  are the cheapest anchors). C1 holds → the cell cover is kept and its price stands.
- Limits stated now: nine anchors (three single, four fused, two five); the proxy carries only the structure we measured, so a cell
  dependence of the real CC correction beyond the context would not show here; the anchors' scatter around the trend (1 − corr²) is left
  out; the base is chain 34's 750-molecule recipe, as arm (a)'s, not the carried version.

## Order and cost

After the branch is merged (it sits on v14-search-code, merged after chain 35): `set3_decompose.py` again on the set-three folder (adds the
mean and the centred slope; the stored slopes unchanged, checked 27 Oct), then `anchor_price_plan.py distortion`, `cover`, `plan`, a
runspec on the proxy check's (memory 7.7 GB, nothing beside it), dry run, launch when the laptop is free. Measured on arm (a): base
3.5 h for three seeds, fine-tunes 6.0 h with four modes → arm (c) ≈ 3.5 + 2.7 (random, whole head) + 1.5 (covers) ≈ 7.7 laptop hours.
The read by 18 Nov at the latest (TASKS 140).
