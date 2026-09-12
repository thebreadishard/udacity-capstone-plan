# Decision memo P13 (2026-09-12): where the naphthalene rung and everything above it is computed

*For the user's decision. Written while the naphthalene cc-pVTZ xtight timing runs (relaunched 16:50, expected
to finish Monday 14 September between ≈ 11:00 and ≈ 23:00); the memo pre-computes both outcomes of that
measurement so that P13 can be taken the moment the number is in. Every number below is either measured (marked
**m**) with its file, or an estimate (marked *e*) with its arithmetic shown. Nothing here is a decision.*

## 1. What P13 decides, and by when

P13 = the machine for the R1 probe batch (naphthalene, the first real coupled-cluster correction) and, by
extension, for R2–R3. Three routes: the laptop (excluded by the measurement below), the desktop of the
hardware note (a priced configuration on the Alternate wishlist, €4,556.80 with the UPS, not bought), and
Snellius through a cluster-time request the supervisor would sponsor (proposal §13 item 5). The calendar
(proposal §12) has R1 scored on **4 December 2026** and the cluster request submitted on **11 December 2026**
— an order that the arithmetic of §3 does not allow for R1 at the anchor's thresholds; the calendar
consequence is in §6.

## 2. The measured facts (all on the laptop, 8 threads, WSL)

| quantity | value | source |
|---|---|---|
| benzene, cc-pVTZ, tight, arm A per energy | 2,160 s = 36 min **m** | `probes/results_m1/benzene_ccpvtz_tight.log` line 10 |
| benzene, cc-pVTZ, xtight, arm A per energy | 4,576 s = 76 min **m**; factor xtight/tight = 2.1 | `probes/results_m1/XTIGHT_READIN.md` |
| naphthalene, cc-pVTZ, tight, one energy | 41,375 s = 11.5 h, peak RSS 19.8 GB **m** | `probes/results_timing/naphthalene_cc-pvtz_tight.json` |
| naphthalene, cc-pVTZ, xtight, one energy | **running**; fragments 1 and 2 of 24: ≈ 110 and ≈ 70 min **m** (attempt 2, log archived); whole energy *e* 42–54 h, i.e. factor 3.6–4.7 over tight (a v⁴ cost model on the tight run's fragment sizes, calibrated on the two measured fragments; Budget dated note) | `naphthalene_ccpvtz_xtight_failed_attempt2.log`; this memo §2 |
| memory at xtight with the three levers | RSS 3–12 GB **m**, scratch up to 29 GB **m**; the VM died once at 21.9 GB when 8 GB of Windows-side work was added (event 2004) | Budget dated notes 2026-09-12 |
| R1 deck without a prior | 96 + 96 + 282 = **474 energies** (proposal §3.2) | proposal |
| R1 deck under the symmetry prior | K ≈ 220–380 energies *e* (96 + 0.9…2.0 × 141; proposal §3.2) | proposal |
| plan 06's substitution route at benzene | 6 products at plan 05's noise (X1c/X1d) — not a plan-05 object yet; needs the engine-side product cost | plan 06 result notes |

**Why xtight matters for P13.** Decision 20 made xtight the anchor's thresholds (composite bias 0.11/0.01/0.23
cm⁻¹ against 0.47/0.03/0.79 at tight). Every R1 energy is therefore an xtight energy. The factor between tight
and xtight is 2.1 at benzene and, by the model, 3.6–4.7 at naphthalene — the LNO spaces grow faster with the
threshold at the larger molecule (fragment 1: 220 → 310 virtuals). Monday's number replaces the model.

## 3. The routes, priced with the facts of §2 (per energy → deck → calendar)

Per-energy times: laptop **m**/​*e* as above; desktop *e* = 3–5 h at tight "from the core count" (Budget desktop
paragraph; 16 cores at desktop clocks, no swap) — an estimate, never timed; Snellius thin node *e* = 1.5–2.5 h wall
and 200–300 SBU at tight (Budget Snellius note). The xtight column multiplies each by the naphthalene factor
3.6–4.7 (model) and, for comparison, by 2.1 (the benzene factor, the best case).

| route | per energy, tight | per energy, xtight (factor 2.1 / 3.6–4.7) | R1 deck 474 energies at xtight | R1 deck ≈ 300 energies (prior) at xtight |
|---|---|---|---|---|
| laptop (**m** base) | 11.5 h | 24 h / 42–54 h | 474 × 24–54 h = **1.3–3.0 years** | 300 × 24–54 h = 300–675 days |
| desktop (*e* base 3–5 h) | 3–5 h | 6–10 h / 11–24 h | 474 × 6–24 h = **120–470 days = 4–16 months** | 300 × 6–24 h = 75–300 days = 2.5–10 months |
| Snellius, one thin node (*e* base) | 1.5–2.5 h wall | 3–5 h / 5–12 h | 474 × 3–12 h = 60–240 node-days; **on four nodes 15–60 days**; SBU 474 × (420–1,400) = **200,000–660,000** | 300 × 3–12 h; SBU 125,000–420,000 |

Reading: (i) the laptop is out for R1 at any threshold; (ii) the desktop reaches R1 at xtight in 4–16 months
— the whole spread is the unknown factor, and even the best case (benzene's 2.1) is four months for the full
deck; (iii) Snellius does R1 in weeks and within one Small Compute application (1,000,000 SBU) at any factor,
but R2 (order 1–2 M SBU at tight, more at xtight) then needs its own application. The Budget's "two to three
months on the desktop" (R1 row of §12) was a tight-threshold sentence; at the anchor's thresholds it does not
hold.

## 4. What the desktop measures that the cluster does not (the case for "both")

- **The DFT side and the corpus factory.** 11,321 candidate molecules at 3–7 min per B3LYP Hessian (Module 05
  timing) = 24–55 desktop-days of DFT that can run *beside* nothing on the laptop (the anchor job owns it) and
  that a cluster application would not be spent on. The learned prior of Module 05 needs this corpus.
- **R0 and the pilot deck at the anchor's thresholds** in days instead of weeks (benzene xtight 76 min per
  energy on the laptop, ≈ 20–40 min on the desktop by the same core-count estimate).
- **Memory facts for R2/R3** (pyrene at cc-pVTZ needs ≈ 220 GB canonical, unmeasured for LNO) with 128 GB in
  the box — the numbers the cluster request should carry instead of estimates.
- **Development without the one-job rule**: the frozen-space chain, the checkpoint layer, Module 05 training,
  Lean builds — all of which today wait for the anchor job.
What it does not do: R1 in the calendar's time frame at xtight, nor R2/R3 at all.

## 5. Decision rule for Monday's number (factor f = t_xtight / t_tight at naphthalene)

| if f is … | desktop R1 (474 energies) | consequence |
|---|---|---|
| ≤ 2.5 (benzene-like) | 4–6 months | desktop-only R1 is *possible* with the calendar moved to spring 2027; cluster still needed for R2 |
| 3.5–5 (model) | 7–16 months | R1 is cluster work; the desktop's case rests on §4 alone |
| > 5, or memory does not fit | > 16 months | cluster for everything from R1; the xtight timing itself becomes the cluster's first job |

## 6. The calendar under each route (proposal §12 has R1 on 4 Dec 2026, cluster request 11 Dec 2026)

- **Cluster route:** the request must precede R1 by the allocation lead time (unknown; a question for the
  supervisor and SURF — neither the review cadence of Small Compute applications nor the time from grant to
  first job is recorded in our notes). Realistic: request in **October**, first
  job the naphthalene xtight timing on Snellius, R1 in **January–February 2027**. The R0 pilot and the DFT work
  stay on schedule (laptop or desktop).
- **Desktop route:** R1 at xtight in spring–autumn 2027 (§3); the 4 December date moves by 4–16 months; R2/R3
  still need the cluster later.
- **Both:** as the cluster route for R1, with §4's work on the desktop from October.
- **Neither (laptop only):** R0 only; R1 becomes a partial deck (the prior's ≈ 300 energies) at ≈ 2 years, i.e.
  the plan stops at R0 in practice.

## 7. Recommendation (mine; the decision is the user's)

Take the two halves of P13 separately and at different times.

1. **The cluster request: decide now, submit in October.** In every scenario except "f ≤ 2.5 *and* the prior
   halves the deck" R1 is cluster work at the anchor's thresholds, and R2–R3 are cluster work in all of them.
   Waiting for Monday's number changes the size of the request (200,000–660,000 SBU for R1 alone), not the
   need. Pulling the request forward from 11 December to October is the one calendar change that keeps R1 in
   the first quarter of 2027; the proposal's §13 item 5 already asks the supervisor for the sponsorship and
   says the request is sized by the timings — Monday's number completes that sizing.
2. **The desktop: decide after two more facts, not before.** (a) Monday's factor f, which fixes whether the
   desktop is an R1 machine or a §4 machine; (b) the corpus-factory timing (five molecules, `run_corpus.py
   --grid-check`, after the anchor job), which prices the DFT side the desktop would carry. If the desktop is
   bought, it is bought for §4, and §4 is worth €4,557 only if Module 05's corpus and the R0 pilot are going to
   be run — which the plan says they are. The wishlist keeps the configuration for six months.
3. **The calendar row for R1** is repriced either way once f is known; the proposal already carries "the
   desktop … in two to three months — an estimate from the core count" with the caveat, and P13 "open". If
   the user agrees with 1, the §12 rows "R1" and "Cluster request" swap order in a dated edit after Monday.

## 8. What is still missing for a fully measured decision

- Monday's xtight naphthalene time and peak memory (running).
- The Snellius per-energy figures are estimates from core counts; the first job on any allocation is the timed
  naphthalene energy, as the Budget note already says.
- The desktop's 3–5 h is an estimate too; only a bought desktop measures it — the circularity the user named.
- The corpus-factory timing (Module 05) for the DFT side of §4.
- SURF's lead time from application to first job (ask the supervisor; item for the first meeting).
