# Decision rule 2026-09-13 — when plan 06 closes a branch, transfers a result, or stops (dated, before the numbers) — **adopted by the user on 13 September 2026 ("Akkoord met de beslisregel, neem hem over")**

*Plan 05 has a kill criterion for its side project and a calendar for its rungs; plan 06 so far has only its protocol ("a direction lives while it has a falsification test"). After the evening of 12 September the plan has thirteen experiments, two conjectures, a draft proposal and a pre-registered measurement — enough that "alive" needs a date. This note fixes, before the pending numbers arrive, what each outcome does to plan 06. Written by the assistant on the morning of 13 September; adopted by the user the same morning, unchanged.*

## 1. The two branches, restated as the user stated them (12 September)

- **Branch M (mathematics):** solve the electronic problem of a many-atom molecule a new way, equivalent to the gold standard within plan 05's error budget (levels E1/E2/E3 of the Orientation).
- **Branch C (cost):** make plan 05 cheap enough that conclusions come sooner, the pipeline runs many times, and the data for the supervisor's network exist.

## 2. The pending numbers and their dates

| number | from | expected | decides |
|---|---|---|---|
| g (gradient-to-energy cost ratio, shipped LNO) | M2a, cells 0–4 | the first free evening after the naphthalene timing (this week) | branch C's gradient route: g ≤ 20 build M2; 20–26 marginal; > 26 no (M2 design note §6, X14's bar) |
| P25's naphthalene licence | X10 repeated on the naphthalene tensor | after the BHHLYP Hessian (machine queue item 5; days) | branch C's energies-only route: licensed → proposal to plan 05; not → withdrawn |
| π share of the ring correction (X6) | X6 | after the run (minutes) | branch M's S3: share < ½ on the C–C stretch closes S3 as an anchor route |
| λ·gap across benzene, naphthalene, pyrene (X7) | X7 | after the run (minutes) | branch M's S1 rate claim (T3): factor > 2 falsifies "rate ∝ gap" |
| the correction's profile beyond one ring (X9 on naphthalene) | after the BHHLYP Hessian | days | whether any real-space route survives at all |
| T1d built | Lean build after the run | this week | the Lean route's second theorem; no branch depends on it |
| ODLR of far blocks at 0.5 cm⁻¹ (X15) | plan 02's Hessians | **done 13 September: fails** (r\*/dim 0.30–0.83) | branch M: T3's ODLR form is norm-level only; branch C: no lever beyond the symmetry prior from low rank |


### 2b. Outcomes (added 16 September 2026; the table above keeps the expectations as written on 13 September — a cold read found the g cell overwritten with its result, which defeated the purpose of a rule "before the numbers")

| number | outcome | date | what it decided |
|---|---|---|---|
| g | 2.84 at RHF, 3.20 at MP2 (plan 05 `probes/results_m2a/m2a_cc-pvdz.md`); the anchor-level cells (canonical and local CCSD(T)) do not fit the laptop's 25 GB in PySCFAD's eager implementation (21 GB RSS + 6.8 GB swap at the energy step; host below 1 GB free twice) | 14 Sep | the closing arm "unmeasurable on the laptop at cc-pVDZ" is live; the gradient route waits for a larger machine |
| P25's naphthalene licence | **LOSE** (X16 on the symmetrised naphthalene stage A, 16 Sep 09:03): the DFT-only ranking needs 76 of 141 eligible pairs for 0.5 cm⁻¹ (rule: ≤ 70.5 and ≤ 1.5 × the oracle's 33); `X16_2026-09-16_Naphthalene_Battery_P25_Licence.md` | 16 Sep | P25 withdrawn; lever B leaves the affordability tables; **both closing conditions of branch C now hold** — closure at the 15 October review |
| π share (X6) | 9 % on the C–C stretch, −48 % on the C–H out-of-plane mode → **S3 closed** | 14 Sep | branch M loses its π-space anchor route |
| λ·gap (X7) | factor 1.57 (under the pre-stated 2), but λ rises 12 % where rate ∝ gap predicts 77 % — the threshold was lenient; T3 alive without support | 14 Sep | T3 to the 1 December review; closing observation named in the annex |
| X9 on naphthalene | run 16 Sep on the symmetrised stand-in: ratio Δ/H_low rises 0.035 → 0.21 with distance; blocks to d = 5 of 7 needed for 0.5 cm⁻¹; the far correction is in the C–C pair blocks (`X9_2026-09-16_Naphthalene_Range_Profile.md`) | 16 Sep | T3′ stays closed; no real-space truncation route; the ring-skeleton families are the non-local ones (as X18) |
| T1d built | built 14 Sep, no `sorry` (`symmValid_iff`) | 14 Sep | the Lean route's second theorem |
| ODLR (X15) | fails at 0.5 cm⁻¹ (r*/dim 0.30–0.83) | 13 Sep | no lever from low rank |
| X18 (added: type transfer, lead D) | C–H stretch 0.27 cm⁻¹ RMS, C–C stretch 17.8 of 41.2 → LOSE as a whole-correction route, per-family win | 16 Sep | lead D folded into plan 05's per-family design |

## 3. The rule

1. **Branch C closes** if, by **15 October 2026**, g > 26 (or unmeasurable on the laptop at cc-pVDZ) **and** P25 is not licensed at naphthalene. Closing means: the cost question returns to plan 05 (P13, thresholds, machines); plan 06 keeps only branch M; the cost ladder is filed as the record. Either one surviving (g ≤ 26, or P25 licensed) keeps the branch open with that lever alone.
   **Dated amendment, 17 September 2026 (the user, from the train: "pas de beslisregel t.z.t. maar aan"; applied once the eight-thread control was in).** Rule 1 as written would close branch C on 15 October on the letter of "cc-pVDZ": P25 lost at naphthalene on 16 September (X16: 76 of 141 pairs against a licence of 70.5 and 49.5), and g at cc-pVDZ is still unmeasurable on this laptop (M2a, 14 September; the WSL ceiling is 20 GB since 16 September). But g **is** now measured for the method the plan uses: **LNO-CCSD(T), benzene, 6-31G, three repeats — 6.04 at eight threads (the production setting) on the full LNO-CCSD(T) energy** — *dated correction, 22:31 the same evening: the first reading of this amendment quoted 5.71 (eight threads) and 7.19 (four), measured on `e_corr_ccsd_t`, which in PySCFAD is the (T) increment alone; the corrected eight-thread value is 6.04 (`results_m2a/m2a_631g_lno_8threads_ecorr_2026-09-17.log`), and 7.6 (the four-thread datum scaled by 6.04/5.71) is an inference kept as a conservative bound, not a measurement* — (M2a cell 3, 17 September, `results_m2a/m2a_631g_lno_8threads_2026-09-17.log` and `..._3rep_...`). RHF and MP2 at the same basis give 3.41 and 3.73 against 2.84 and 3.20 at cc-pVDZ (14 September), so the small basis reads *higher*, not lower — with the caveat that those pairs also differ in thread count and are not yet a clean basis comparison. Against the break-even of 16.2 at naphthalene and 29.9 at pentacene (X21), every measured value is a factor two to five inside. **In force from this date:** the closing arm of rule 1 reads "g > 26, measured for LNO-CCSD(T) at the largest basis that fits the machine in use, the basis and thread count stated"; the 6-31G measurement satisfies it with g ≤ 7.2, and **branch C stays open on g alone**, as the rule's own last sentence provides. The transfer gate of rule 2 is unchanged: M2 (in-house frozen-space gradients) still transfers only through M2a's rule, whose g ≤ 20 gate is now met; what M2a has *not* settled is whether PySCFAD's shipped LNO (IAO auto-fragments) can stand in for plan 05's Pipek–Mezey frozen spaces, which is the next pre-registered question before any gradient enters a plan-05 deck. *Answered the same night (M2b, 23:27): it cannot — 5.5 / 8.2 / 26.4 µE_h against a bar of 6 on benzene's three probe modes at arm A's thresholds, and half the C–C response at PySCFAD's defaults. Branch C therefore transfers only through **M2** (in-house frozen-space gradients), whose own g is unmeasured; the 6.04 above is the borrowed engine's. The rule text is unchanged: M2 transfers through M2a's gate as written, and that gate (g ≤ 20) is met by the only g that exists, with the engine caveat stated.* Nothing in this amendment changes the 1 December review of branch M.

2. **Branch C transfers** — a result becomes a plan-05 dated proposal — only through the existing gates: P25 after its licence test (the user agreed on 13 September); M2 after M2a's rule; nothing else transfers without its own pre-registered test.
3. **Branch M closes a direction** by its own pre-stated test (S3 by X6; S1's rate claim by X7; S2 already unlikely; S5's algebra is proved and needs no further mathematics) and **the branch as a whole is reviewed on 1 December 2026**: if by then no direction has an E1 or E2 statement with a measured first data point *and* a written proof plan beyond what T3's plan holds, branch M becomes a reading list rather than an active plan — kept, dated, not pursued.
4. **The Lean route continues as long as it costs machine time only when no anchor job runs** and each theorem is one of a named list (T1d, T3a–T3c, the resolvent lemma); it has no closing date because it produces certificates, not claims.
5. **Plan 06 as a folder never closes**; what closes are branches and directions, each with the sentence that closed it. A closed branch reopens only by a new measured fact, recorded as a dated addition.

## 4. What this protects against

Two failure modes the plan is now large enough to fall into: running experiments because they are cheap rather than because a decision hangs on them, and keeping a direction "alive" past the point where its test has been failed. Every experiment after this note names, in its first paragraph, which row of §2 or which direction of §3 it serves; one that names none is not run.

## 5. Bookkeeping if adopted

Orientation §6 (protocol) gains a pointer to this note; the ledger's status column uses "closed (date, test)" for closed directions; plan 05's README owed list gains the 15 October and 1 December dates. Nothing in plan 05's frozen text changes.
