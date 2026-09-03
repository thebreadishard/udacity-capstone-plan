# Frozen ladder and tolerances — Plan 05

**Status.** Frozen 2026-09-03 in *form*; revised the same day after Round-7 Pass A. Carried
from plan 04 with the plan-05 additions marked **[05]**; the pilot-dependent numbers (§4) are
frozen by a dated note **before** any comparison they govern is scored. After that note, no
number may be loosened in either direction. Agrees with
[Overarching_Goal.md](Overarching_Goal.md), which also defines the notation (Δ₂/Δ₃/Δ₄, mode
E/G, K, structural vs learned prior); the Goal file wins on drift. Costs live in
[Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md).

---

## 1. Three sentence types, declared up front

- **Accuracy rungs (A).** Laboratory data exists. The claim is *beat the frozen line per band
  against the lab scoreboard* ([Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) §5).
- **Reach rungs (R).** No per-molecule laboratory spectrum exists. The claim is *the pipeline
  ran end-to-end and produced a spectrum with a stated error budget*; comparisons against the
  lines are **theory-vs-theory and labelled as such**. The word "beat" is forbidden on reach
  rungs.
- **[05] Cost sentences.** Exactly two kinds exist, and this is the only place that defines
  them; every other document conforms to this section.
  - **The cost record** — allowed on any rung once printed, and *promised* for every rung that
    ran: `K = n at rung R, mode E|G, prior = structural|learned, ρ* = …, wall-clock w per
    probe on machine m, printed by probes/<file>`. Nothing else about cost may be written.
  - **The size claim** — allowed **only** after Q8(c) has passed **in mode G with the
    structural prior** at R1, R2 and R3, and then only as the printed numbers: "K_G went
    n₁ → n₂ → n₃ from R1 to R3 while the mode count went M₁ → M₂ → M₃". The adjectives
    "size-independent", "O(1)", "saturates", "does not grow" are forbidden everywhere,
    including the Module 08 paper. If only mode E ran at any of R1–R3, no size claim exists
    and the cost record says "mode E; K = 2M + K_off; no size claim".

## 2. The ladder (rungs and species carried from plan 04; R2 re-read, see the dated note)

| Rung | Molecule(s) | Type | Why this rung | Opponents | Lab scoreboard | **[05] what it licenses** |
|---|---|---|---|---|---|---|
| **R0** | benzene C₆H₆ (12 atoms, 30 modes) | A | End-to-end laptop pilot; canonical CCSD(T) affordable (plan-02 measured 19.6 s/point on the old machine, provenance only) | A, B | NIST gas; PAHdb experimental | **Q7 probing licence, Δ₂ and Δ₃/Δ₄**, against local-CC *and* canonical references — the only rung where the canonical arm is certain; the zero-CC dry run |
| **R1** | naphthalene C₁₀H₈ (18 atoms, 48 modes) | A | The canonical-vs-local-CC licence molecule, conditional exactly as in plan 04: the first R1 probe measures whether canonical (T) runs on the new machine at any usable basis; if not, the licence downgrades to **R0-only plus a declared cross-basis protocol**, stated in every anchor claim | A, B | NIST; PAHdb experimental | Q6 anchor licence; Q7 at a second size (local-CC reference; canonical if it runs); first **Q8(a/b)** read; first mode-E vs mode-G timing |
| **R2** | pyrene C₁₆H₁₀ (26 atoms, 72 modes); chrysene C₁₈H₁₂; triphenylene C₁₈H₁₂; tetracene C₁₈H₁₂ (each 30 atoms, 84 modes) | A | First territory beyond PAHdb's anharmonic front | A, B | **Gas (NIST WebBook, grids ~4 cm⁻¹ per the plan-04 coverage probe, re-measured under this plan's hash):** pyrene, chrysene, triphenylene. **Matrix (PAHdb experimental uids 334, 282, 291 as recorded in plan-02 probes):** pyrene, tetracene, chrysene. Tetracene has no gas-phase IR (solid-only) and is scored on matrix data only, every family M03-gated. IRMPD = context only | Q8(a/b) second read; K printed; Q8(c) first ratio (R1→R2) |
| **R3** | coronene C₂₄H₁₂ (36 atoms, 102 modes) | A | Mulas 2018's molecule; largest PAH with a usable matrix spectrum (uid 18); no gas-phase IR in the WebBook | A, B (Mulas), C | PAHdb experimental (uid 18), every family M03-gated | Q8(a/b) third read; **Q8(c) second ratio (R2→R3)**; the size claim is decided here |
| **R4** | circumcoronene-class, C₅₄H₁₈ → ~C₉₆ | R | First rung with no per-molecule lab truth | A, C (theory-vs-theory) | — | expert-judgment datum (Goal, expectations tier 3); the learned-prior arm (P3) may run here, labelled; fragment probing only if the user decides it in |
| **R5** | ~C₂₁₆ (top of Mai's set) | R | Meet line C at its own ceiling | A, C | — | as R4 |
| **R6** | C₃₈₄H₄₈-class (for C₃₈₄H₄₈ itself: 432 atoms, 1,290 modes) | R | Only line A exists here, at 4-31G | A (theory-vs-theory) | — | the reach certificate, structural prior only; **K(R6) in the same table as K(R3), same mode, same prior** |

**Dated note, 2026-09-03 (R2 re-read).** Plan 04's R2 row excluded triphenylene as having "no
laboratory spectrum" and was written before plan 04's own NIST coverage probe completed. That
probe (plan 04 `probes/nist_gas_coverage.py`, raw evidence in its `nist_cache/`) found gas-phase
IR for pyrene, chrysene **and triphenylene**, none for tetracene (solid-only), none for
coronene. Plan 05 therefore scores triphenylene on its gas families and gates tetracene fully.
The user may veto this by dated note (Goal, open decision 3).

**Decidability per family (frozen form).** A family is scored against gas-phase data wherever
gas data exists for that molecule and family; it is **decidable** if the measured gas grid
(scoreboard re-read) is smaller than the family's beat margin. A family with matrix data only
passes through the **M03 matrix–gas gate**: if the M03-measured |matrix−gas| delta for that
family is not smaller than its beat margin, it is scored **"pre-declared inconclusive on
matrix"** — not "beat", not "lost". R0–R1 are gas-scored throughout and therefore unconditional.

**Promised:** R0–R1 scored as accuracy rungs against gas-phase data. R2–R3 scored as accuracy
rungs per family under the decidability rule above. R6 reached as a reach rung, **conditional
on B3**; if the allocation never exists, R6 is reported fail-closed. **[05]** The **cost
record** (§1) for every rung that ran.
**Bonus:** R4, R5, anything beyond R6, the learned-prior arm (P3), fragment probing, and the
size claim itself (it is earned or not; its absence is not a failure).

**Charge.** All rungs are **neutral species** unless a rung's pilot note names a charge state.

**Ordering.** R0 before anything. R1 before any local-CC-based accuracy claim. **[05]** Q7 must
pass at R0 and R1 — for Δ₂ and for Δ₃/Δ₄ on the promised families — before any Δ enters a
scored spectrum at any rung; the R0–R1 scored spectra themselves are produced only after Q7
has printed. Q8(a/b) must be printed at R1, R2 and R3 and Q8(c) at R1→R2 and R2→R3 before any
size claim is worded. Reach rungs may not start before R3 has been **scored** (scored includes
lost and pre-declared inconclusive).

## 3. Frozen now (not pilot-dependent)

- **Reporting unit:** cm⁻¹ per band; families = CH-stretch (~3.3 µm), CC modes (6.2 / 7.7 /
  8.6 µm), CH-oop by adjacency class (solo / duo / trio / quartet, 10–15 µm).
- **Resolution floor:** no claim finer than **10 cm⁻¹** in any astronomical framing; a
  lab-facing claim may be finer only if the measurement uncertainty *and* the declared controls
  (held-out residual, local-CC noise floor, threshold sensitivity) support it, printed by the
  comparison probe — never finer than the scoreboard's own uncertainty (~1 cm⁻¹ bind).
- **Matrix tolerance:** working convention **15 cm⁻¹**; binding value = the Module-03 measured
  one, frozen in the pilot note (§4 item 4). Gas-phase preferred over matrix wherever both exist.
- **Comparison form (pre-registered):** paired per-band absolute error, pipeline vs line, on
  identical lab bands; per family; mean ± spread. ≥3 seeds for every ML component.
  **Inconclusive is a publishable outcome.** The scoreboard is never a training, validation or
  pattern-design input of the pipeline (Distilled Q4; the M04 baseline is the declared exception).
- **No lab band may be scored twice under different windows.**
- **[05] K is a measurement, not a choice.** Patterns are consumed in the hashed order of the
  Q0 deck; K is the smallest count at which the held-out residual ρ (Distilled §3 defines it)
  first satisfies ρ ≤ ρ\*, the target frozen in the pilot note. K is never written down before
  the rung runs. The pilot note freezes instead a **cap K_cap** (item 9) for the classification
  rule; if ρ has not reached ρ\* by K_cap, the rung's Δ is "not recovered at cap" (§5.4), and
  the cap is never raised to rescue it.
- **[05] Hold-out membership is decided before any response exists:** by a seeded rule in the
  Q0 deck (deck seed + pattern index), fraction f_h (item 10). Choosing held-out probes after
  responses are known is a Distilled §4 deviation.
- **[05] Frozen domains:** every local-CC probe evaluation at a displaced geometry uses
  correlation domains and pair lists frozen at the reference geometry. A code that cannot do
  this at the anchor level is reported under stop condition 1, not worked around silently.
- **[05] Probe patterns are hashed** in the Q0 deck before the first probe runs; adding,
  removing or re-weighting patterns after any residual is known is a Distilled §4 deviation.
- **[05] Order of the pilot inputs.** The pilot note is written with the lab side, the opponent
  side, the **zero-CC dry run** (DFT-vs-DFT Δ; Distilled Q7 dry-run column) and single-point
  timings in hand — **and nothing else**. The R0 local-CC probe batch and the Q7 references
  are computed **after** the note is committed. No local-CC Δ number of any kind exists when
  ρ\*, K_cap, the Q7 tolerances or the beat margins are written.
- **[05] The promised route uses the structural prior.** The learned prior never enters a
  promised rung (R0–R3, R6): not the scored spectrum, not K, not the cost record. It may run on
  R4–R5 as a labelled bonus arm; a prior-assisted K is labelled `prior = learned` and never
  appears in a Q8 ratio or an R6 sentence.
- **[05] Q8 has a fixed form** (Distilled Q8): (a) per atom pair, the Frobenius norm of the
  3×3 Δ₂ block against interatomic distance, fitted to A·exp(−r/r_c) — r_c is a **measured
  output**, printed, never a target; the pass test is that pairs beyond r_max carry no more
  than a fraction ε₈ of Σ‖block‖²; (b) per scored family, the share of the family's Δ-shift
  carried by pairs beyond r_max is ≤ ε₈ (computed by zeroing those blocks and recomputing the
  shift); (c) saturation, **same mode and same prior at both rungs, at the same ρ\***:
  K(R_{n+1}) ≤ γ·K(R_n) for R1→R2 and R2→R3 in mode G; in mode E the test applies to K_off
  only and the 2M part is reported as the mode-E floor. If the modes differ between two rungs,
  Q8(c) for that pair reads NOT_RUN and no size claim exists. r_max, ε₈ and γ are pilot-note
  item 12 — written before R1 runs.
- **[05] The cost-sentence rule of §1** binds every document.

## 4. Frozen at the pilot note (form fixed now, numbers then)

Written into a dated pilot note after (a) the **R0 pilot** — geometry, DFT Hessian, harmonic
bands, timings, the zero-CC dry run at R0 and at the largest sizes the laptop affords, **no
local-CC Δ and no pipeline-vs-lab number** — and (b) the **scoreboard re-read probe**.
Committed **before any local-CC probe response and before any pipeline-vs-lab number exists
for any molecule**; inputs are the lab side, the opponent side, the DFT-only dry run and
single-point timings, never a pipeline spectrum and never a local-CC Δ.

1. The exact band list per molecule (uid / NIST CAS, window, class); every §3 family with lab
   data for a promised molecule must appear; per family, whether it is gas-scored or
   matrix-scored.
2. The "beat" margin per family, from the lab and opponent side only; the list of promised
   families closed in the same note.
3. The P-gate numbers (0 imaginary frequencies tolerance; scale-factor policy: **none** on
   anharmonic output; a harmonic fallback declares its factor and fit set).
4. The **matrix shift tolerance** as measured by Module 03.
5. The **P3 effect size** — **[05] redefined**: the reduction in K, or in ρ at fixed K, that
   the learned prior must deliver on a bonus rung to count, declared before either arm runs.
6. The **M04 baseline recipe** (features, tuning budget, seeds).
7. **Resonance handling per rung** (carried): GVPT2 with named r₃/r₄ thresholds and a polyad
   cap; or MD-ACF on the defined DFT-plus-Δ potential (only if the deck names one); or
   CH-stretch unscored.
8. **[05] The residual target ρ\***, one number per mode (E, G), and the response type the
   residual is computed on in each mode (Distilled §3). Derived from the dry run by the rule
   stated in the note; no local-CC number is available when it is written.
9. **[05] K_cap per rung and per mode**, derived from the dry-run K at that rung's molecule
   (or the largest dry-run size available) by a factor stated in the note. Replaces plan 04's
   N_min. K_cap(G) reads NOT_RUN for any rung where the gradient-availability probe printed
   "no".
10. **[05] The hold-out fraction f_h and the hold-out seed.**
11. **[05] The Q7 tolerances**: τ₇,₂ (recovered vs reference Δ₂, as per-family RMS harmonic
    frequency difference, cm⁻¹) and τ₇,₃ (recovered vs reference Δ₃/Δ₄, as per-family GVPT2
    shift difference, cm⁻¹), each **no larger than the smallest beat margin of item 2**; and
    the **discriminability factor** d₇ (Distilled Q7). No Q7 result exists when they are
    written (§3, order of the pilot inputs).
12. **[05] The Q8 numbers**: r_max, ε₈, γ. Written before R1 runs; never loosened.

## 5. Stop conditions and escalation (declared in advance)

1. **Local-CC code unavailable at the anchor level, or unable to freeze domains, or the new
   laptop underperforms:** the rung stops; the missing binary, option or measurement is named.
   Do not substitute a different level, or unfrozen domains, and keep the rung's name.
2. **A rung crosses a machine checkpoint:** a dated decision note is mandatory — continue
   knowingly, reroute to B3, or stop. Silent overrun is forbidden, and so is ducking under a
   checkpoint by coarsening the basis, loosening thresholds, raising ρ\*, raising K_cap, or
   dropping patterns. **Human hours are never a stop condition.**
3. **Cluster or rented-GPU access not formalised when first needed:** reach rungs stop and the
   stop is reported.
4. **A licence probe breaches its frozen threshold** — Q6 (local CC vs canonical; TightPNO vs
   NormalPNO; smoothness and domain-freezing bias), **Q7** (Δ₂ or Δ₃/Δ₄ outside tolerance, or
   the discriminability clause failed, or the shuffled-probe null passed), **Q8(a/b)** (no
   locality, or a family's correction carried by long-range pairs), **Q8(c)** (no saturation
   in mode G), or **ρ not reaching ρ\* by K_cap**: a measured result, reported as such.
   Q6/Q7/K_cap breach: Δ does not enter a scored spectrum on the affected families at that
   rung; the pre-declared fallback is **DFT harmonic + DFT anharmonic, with Δ₂ applied only on
   families where Q7 passed, labelled per family** — it competes under the same protocol and
   may lose. Q8(a/b) breach on a family: that family's Δ is reported with its long-range share
   and carries no accuracy claim finer than that share. **Q8(c) breach: no size claim** — R6,
   if it runs, is reported with its cost record and the sentence "the probe count did not
   saturate between R1 and R3; this spectrum's cost is not an extrapolable quantity"; the plan
   does not fall back to a point factory whose affordability no plan has measured.
5. **A promised accuracy rung loses to a line:** published with the paired table.

## 6. What this ladder refuses (carried, with additions)

- No global QFF of a huge molecule as a deliverable.
- No whole-molecule "gold rung" language above R1; anchors are "local-CC, R1-checked".
- No motif-transfer claim: every molecule gets its own probed Δ; transfer, if ever observed,
  is a bonus observation. **[05]** The learned prior is not a transfer claim: it is scored by
  what it saves on bonus rungs, and the probes remain the answer.
- No editing this ladder after a rung it governs has been scored, except by dated deviation
  note committed before the affected number is known.
- **[05]** No cost sentence outside the two forms of §1; no K written before it is measured;
  no Q8 ratio across mixed modes or mixed priors.
