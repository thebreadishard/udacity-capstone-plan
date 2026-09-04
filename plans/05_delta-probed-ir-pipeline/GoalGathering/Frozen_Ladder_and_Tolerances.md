# Frozen ladder and tolerances — Plan 05

**Status.** Frozen 2026-09-03 in *form*; revised the same day after Round-7 Pass A and Pass B.
Carried from plan 04 with the plan-05 additions marked **[05]**; the pilot-dependent numbers
(§4) are frozen by a dated note **before** any comparison they govern is scored. After that
note, no number may be loosened in either direction. Agrees with
[Overarching_Goal.md](Overarching_Goal.md), which defines the notation; the Goal file wins on
drift. Costs live in [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md).

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
    ran: `K = n (of which 2M = … diagonal, K_off = … off-diagonal) at rung R, mode E|G, prior =
    structural|learned, ρ* = …, PNO extrapolation = none|CPS, wall-clock w per probe on machine
    m, printed by probes/<file>`. Nothing else about cost may be written.
  - **The size sentence** — numeric only, in one of two forms, each allowed only after Q8(c)
    has passed for that quantity at R1→R2 and R2→R3 with the structural prior at the same ρ\*:
    *mode-E form* (the promised route): "K_off went n₁ → n₂ → n₃ from R1 to R3 while the mode
    count went M₁ → M₂ → M₃"; *mode-G form* (bonus, only if the gradient probe printed "yes" at
    all three rungs): the same for K. The adjectives "size-independent", "O(1)", "saturates",
    "does not grow" are forbidden everywhere, including the Module 08 paper. A rung where mode
    E's Q6 noise gate did not pass carries a cost record but no "beat" language.

## 2. The ladder (rungs and species carried from plan 04; R2 re-read, see the dated note)

| Rung | Molecule(s) | Type | Why this rung | Opponents | Lab scoreboard | **[05] what it licenses** |
|---|---|---|---|---|---|---|
| **R0** | benzene C₆H₆ (12 atoms, 30 modes) | A | End-to-end laptop pilot; canonical CCSD(T) affordable (plan-02 measured 19.6 s/point on the old machine, provenance only) | A, B | NIST gas; PAHdb experimental | **Q7 probing licence for Δ₂** against the frozen-domain local-CC reference *and* the canonical reference — **the canonical arm is the only one that licenses the domain freezing** (Q6 bias); the zero-CC dry run; the Q6 noise grid at R0 |
| **R1** | naphthalene C₁₀H₈ (18 atoms, 48 modes) | A | The canonical-vs-local-CC licence molecule, conditional exactly as in plan 04: the first R1 probe measures whether canonical (T) runs on the B2 laptop at any usable basis; if not, the licence downgrades to **R0-only plus a declared cross-basis protocol**, stated in every anchor claim | A, B | NIST; PAHdb experimental | **The Q6 smoothness probe** (three modes, nine points, frozen data — the first rung with truncated pairs); Q6 anchor licence; Q7 at a second size, printed for diagonal-only and full recovery; first **Q8(a/b)** on the reference Hessian; the gradient probe with memory; expected-effect line printed |
| **R2** | pyrene C₁₆H₁₀ (26 atoms, 72 modes); chrysene C₁₈H₁₂; triphenylene C₁₈H₁₂; tetracene C₁₈H₁₂ (each 30 atoms, 84 modes) | A | First territory beyond PAHdb's anharmonic front | A, B | **Gas (NIST WebBook, grids ~4 cm⁻¹ per the plan-04 coverage probe, re-measured under this plan's hash):** pyrene, chrysene, triphenylene. **Matrix (PAHdb experimental uids 334, 282, 291 as recorded in plan-02 probes):** pyrene, tetracene, chrysene. Tetracene has no gas-phase IR (solid-only) and is scored on matrix data only, every family M03-gated. IRMPD = context only | Q6 at R2 size: the **canonical diagonal check at pyrene** (two energies per mode, one mode per family) and the TightPNO/NormalPNO column; **prior-free direct-block probe** for Q8(a/b); K and K_off printed; Q8(c) first ratio (R1→R2) |
| **R3** | coronene C₂₄H₁₂ (36 atoms, 102 modes) | A | Mulas 2018's molecule (B97-1 QFF, item 6); largest PAH with a usable matrix spectrum (uid 18); no gas-phase IR in the WebBook | A, B (Mulas), C | PAHdb experimental (uid 18), every family M03-gated | direct-block probe; Q8(c) second ratio (R2→R3); the size sentence is decided here |
| **R4** | circumcoronene-class, C₅₄H₁₈ → ~C₉₆ | R | First rung with no per-molecule lab truth | A, C (theory-vs-theory) | — | expert-judgment datum (Goal, expectations tier 3); the learned-prior arm (P3) may run here, labelled; **fragment probing exercised here first**, its certificate compared with whole-molecule probing where the size still allows both; the R6 DFT-Hessian timing probe |
| **R5** | ~C₂₁₆ (top of Mai's set) | R | Meet line C at its own ceiling | A, C | — | as R4 |
| **R6** | C₃₈₄H₄₈-class (for C₃₈₄H₄₈ itself: 432 atoms, 1,290 modes) | R | Only line A exists here, at 4-31G | A (theory-vs-theory) | — | **fragment-probed Δ₂ only** (decided 2026-09-04, licensed by Q8 at R2–R3); the reach certificate; cost record in the same table as R3's, same mode, same prior. **Whole-molecule probing is not promised**: mode E would be ≥ 2,580 energies of a 432-atom molecule |

**Dated note, 2026-09-03 (R2 re-read).** Plan 04's R2 row excluded triphenylene as having "no
laboratory spectrum" and was written before plan 04's own NIST coverage probe completed. That
probe (plan 04 `probes/nist_gas_coverage.py`, raw evidence in its `nist_cache/`) found gas-phase
IR for pyrene, chrysene **and triphenylene**, none for tetracene (solid-only), none for
coronene. Plan 05 therefore scores triphenylene on its gas families and gates tetracene fully.
**Confirmed by the user on 2026-09-04** (open decision 3 closed); the R2 A-scored set is
pyrene, chrysene, triphenylene (gas families) and tetracene (matrix, M03-gated).

**Dated note, 2026-09-03 (R6 form, after Round-7 Pass B), closed 2026-09-04.** R6's promised
form depended on the user's open decision 1. **Decided 2026-09-04: in, subject to measurement**
(Goal, "The goal binds; methods are means"). R6 is promised as **fragment-probed Δ₂**,
conditional on Q8(a/b) passing on direct blocks at R2 and R3 for the scored families and on B3;
families that fail Q8 are withdrawn from the R6 certificate with their measured long-range
share. Whole-molecule R6 is not promised.

**Decidability per family (frozen form).** A family is scored against gas-phase data wherever
gas data exists for that molecule and family; it is **decidable** if the measured gas grid
(scoreboard re-read) is smaller than the family's beat margin. A family with matrix data only
passes through the **M03 matrix–gas gate**: if the M03-measured |matrix−gas| delta for that
family is not smaller than its beat margin, it is scored **"pre-declared inconclusive on
matrix"** — not "beat", not "lost". R0–R1 are gas-scored throughout and therefore unconditional.

**Promised:** R0–R1 scored as accuracy rungs against gas-phase data. R2–R3 scored as accuracy
rungs per family under the decidability rule above — **"beat" language on a mode-E rung
requires the Q6 noise gate to have passed at that rung's size class.** R6 per the dated note
above. **[05]** The **cost record** (§1) for every rung that ran.
**Bonus:** R4, R5, anything beyond R6, the learned-prior arm (P3), the diagonal-cubic probe
(Δ₃ along scored modes), the anthracene locality probe, the mode-G size sentence, the size
sentence itself (it is earned or not; its absence is not a failure), and the whole-molecule vs
fragment comparison at R4.

**Charge.** All rungs are **neutral species** unless a rung's pilot note names a charge state.

**Ordering.** R0 before anything. R1 before any local-CC-based accuracy claim. **[05]** Q7 must
pass at R0 and R1 before any Δ₂ enters a scored spectrum at any rung; the R0–R1 scored spectra
themselves are produced only after Q7 has printed. The Q6 smoothness probe at R1 must print
under the line before any mode-E "beat" sentence anywhere. Q8(a/b) must be printed at R1 (on
the reference), R2 and R3 (on direct blocks) and Q8(c) at R1→R2 and R2→R3 before any size
sentence is worded. Reach rungs may not start before R3 has been **scored** (scored includes
lost and pre-declared inconclusive). Open decision 1 was made on 2026-09-04 (in, subject to Q8)
and is recorded in the pilot note.

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
- **[05] The promised correction is Δ₂ only.** No CC correction to cubic or quartic constants
  is promised; the diagonal-cubic probe is a bonus number. DFT anharmonic constants are computed
  for a family set closed under the resonance search.
- **[05] K is a measurement, not a choice.** Patterns are consumed in the hashed order of the
  Q0 deck; K is the smallest count at which the held-out residual ρ (Distilled §3 defines it)
  first satisfies ρ ≤ ρ\*, the target frozen in the pilot note; K_off = K − 2M in mode E. K is
  never written down before the rung runs. The pilot note freezes instead a **cap K_cap**
  (item 9) for the classification rule; if ρ has not reached ρ\* by K_cap, the rung's Δ₂ is
  "not recovered at cap" (§5.4), and the cap is never raised to rescue it.
- **[05] Hold-out membership is decided before any response exists:** by a seeded rule in the
  Q0 deck (deck seed + pattern index), fraction f_h (item 10).
- **[05] Frozen domains:** every local-CC probe evaluation at a displaced geometry uses
  correlation domains, pair lists and per-pair PNO counts frozen at the reference geometry. A
  code that cannot do this at the anchor level is reported under stop condition 1 (as of
  2026-09-03: ORCA documents it for DLPNO-MP2 only; Psi4 documents no domain reuse).
- **[05] The structural prior is frequency-banded** (Distilled §3): off-diagonal Δ₂ elements
  between DFT modes closer than a band width w are unpenalised; outside the band they carry the
  ℓ₁ penalty; plus a low-rank term. w and the regularisation weights are deck numbers fixed from
  the dry run, and the dry-run pair is **B3LYP against a functional with markedly more exact
  exchange** (BHLYP-class or Hartree–Fock), never two functionals of one family.
- **[05] Pattern amplitudes come from the Q6 step grid**: the largest step at which the R1
  smoothness probe printed under the noise line; never chosen to make a recovery converge.
- **[05] Probe patterns are hashed** in the Q0 deck before the first probe runs; off-diagonal
  blocks the dry run flags as large receive explicit two-mode patterns in that deck; adding,
  removing or re-weighting patterns after any residual is known is a Distilled §4 deviation.
- **[05] Order of the pilot inputs.** The pilot note is written with the lab side, the opponent
  side, the **zero-CC dry run**, the gradient-availability probe (with memory), the **R1
  smoothness probe** and single-point timings in hand — **and nothing else**. The R0 local-CC
  probe batch and the Q7 references are computed **after** the note is committed. No local-CC
  Δ₂ number exists when ρ\*, K_cap, the Q7 tolerance or the beat margins are written; the
  smoothness probe is second differences along single modes, not a Δ₂ recovery, and its use
  is confined to item 13 and the amplitude rule.
- **[05] The promised route uses the structural prior by default;** the learned prior may enter a promised rung only under a **licence**: (i) P3 has
  demonstrated its saving on the dry-run corpus at matched K; (ii) at that rung the reference
  check — Q7 at R0–R1, the direct-block Q8 check at R2–R3 — is computed prior-free and the
  prior-assisted recovery agrees with it within τ₇ / ε₈; (iii) the cost record says
  `prior = learned`, and a size sentence compares like with like (same prior at both rungs).
  Unlicensed, the learned prior runs on the dry-run corpus and R4–R5 as a labelled bonus arm
  only (user directive 2026-09-04: inheritance is not authority — a transfer that a gate shows
  to serve the goal is allowed).
- **[05] Q8 has a fixed form** (Distilled Q8) and is computed on **directly measured blocks**
  wherever it decides anything: (a) per atom pair, the Frobenius norm of the 3×3 Δ₂ block
  against interatomic distance, fitted to A·exp(−r/r_c) — r_c is a measured output — with the
  pass test that pairs beyond r_max carry no more than a fraction ε₈ of Σ‖block‖²; at R0–R1
  the blocks come from the reference Hessian, at R2–R3 from the prior-free direct-block probe
  (a deck-chosen set of atom pairs in the π system at near, mid and far distances, each block
  measured by four-point finite differences of ΔE along paired atomic displacements); the
  recovered Δ₂'s blocks are printed beside them and a disagreement larger than ε₈ is a
  Q7-class breach; (b) per scored family, the share of the family's Δ-shift carried by pairs
  beyond r_max is ≤ ε₈, computed with the direct far blocks substituted into the recovered Δ₂;
  (c) saturation, **same mode and same prior at both rungs, at the same ρ\***: in mode E on
  K_off — K_off(R_{n+1}) ≤ γ·K_off(R_n) for R1→R2 and R2→R3 — and in mode G on K, only if the
  gradient probe printed "yes" at all three rungs. If the modes differ between two rungs, Q8(c)
  for that pair reads NOT_RUN. r_max, ε₈ and γ are pilot-note item 12.
- **[05] Q6 has thresholds** (item 13), each a formula frozen now with its numbers filled at
  the pilot note: the noise line σ_E(q_s) ≤ 0.82·τ·q_s² (σ_E the second-difference scatter of
  frozen-domain ΔE along a mode at dimensionless step q_s, τ the smallest beat margin of item
  2 in cm⁻¹, both sides in the same energy unit), measured on the grid q_s ∈ {0.25, 0.5, 1.0}
  at R1 and at the R2-size family; the bias line |Δ₂(frozen) − Δ₂(canonical)| ≤ τ per R0 mode
  and, diagonal-only, per pyrene family mode; the threshold line: TightPNO−NormalPNO
  frequency delta ≤ τ, else CPS extrapolation is mandatory and every probe counts double in
  the classification rule.
- **[05] The cost-sentence rule of §1** binds every document.

## 4. Frozen at the pilot note (form fixed now, numbers then)

Written into a dated pilot note after (a) the **R0 pilot** — geometry, DFT Hessian, harmonic
bands, timings, the zero-CC dry run at R0 and at the largest sizes the laptop affords, **no
local-CC Δ₂ and no pipeline-vs-lab number** — (b) the **scoreboard re-read probe**, (c) the
gradient-availability probe and (d) the R1 smoothness probe. Committed **before any local-CC
Δ₂ response and before any pipeline-vs-lab number exists for any molecule**. The 2026-09-04
fragment-probing decision is recorded in it.

1. The exact band list per molecule (uid / NIST CAS, window, class); every §3 family with lab
   data for a promised molecule must appear; per family, whether it is gas-scored or
   matrix-scored.
2. The "beat" margin per family, from the lab and opponent side only; the list of promised
   families closed in the same note; and the **expected-effect line**: "the literature scale of
   Δ₂ at R1 is ≈ 5 cm⁻¹ mean absolute harmonic difference (item 45, snippet, verify-on-use);
   the P2 hypothesis is that the per-family scatter of Δ₂ exceeds the margin after the
   opponents' fitted factors absorb its mean."
3. The P-gate numbers (0 imaginary frequencies tolerance; scale-factor policy: **none** on
   anharmonic output; a harmonic fallback declares its factor and fit set).
4. The **matrix shift tolerance** as measured by Module 03.
5. The **P3 effect size** — **[05] redefined**: the reduction in K, or in ρ at fixed K, that
   the learned prior must deliver on the dry-run corpus or a bonus rung to count.
6. The **M04 baseline recipe** (features, tuning budget, seeds).
7. **Resonance handling per rung** (carried): GVPT2 with named r₃/r₄ thresholds and a polyad
   cap; or MD-ACF on the defined DFT-plus-Δ potential (only if the deck names one); or
   CH-stretch unscored — and the **resonance-closed family set** (partner modes included in
   the DFT cubic/quartic differencing).
8. **[05] The residual target ρ\***, one number per mode (E, G), and the response type the
   residual is computed on in each mode (Distilled §3). Derived from the dry run by the rule
   stated in the note.
9. **[05] K_cap per rung and per mode**, derived from the dry-run K at that rung's molecule
   (or the largest dry-run size available) by a factor stated in the note. K_cap(G) reads
   NOT_RUN for any rung where the gradient-availability probe printed "no".
10. **[05] The hold-out fraction f_h and the hold-out seed.**
11. **[05] The Q7 tolerance τ₇** (recovered vs reference Δ₂, as per-family RMS harmonic
    frequency difference, cm⁻¹), **no larger than the smallest beat margin of item 2**; and the
    **discriminability factor** d₇ (Distilled Q7). No Q7 result exists when they are written.
12. **[05] The Q8 numbers**: r_max, ε₈, γ, and the direct-block pair list per rung (which
    atom pairs, at which distances). Written before R1's Q8 read; never loosened.
13. **[05] The Q6 numbers**: τ inserted into the noise, bias and threshold formulas of §3; the
    pattern amplitude q_s chosen from the R1 smoothness grid; the CPS decision; the band width
    w and regularisation weights of the structural prior (from the dry run).

## 5. Stop conditions and escalation (declared in advance)

1. **Local-CC code unavailable at the anchor level, or unable to freeze domains, pair lists
   and PNO counts, or the new laptop underperforms:** the rung stops; the missing binary,
   option or measurement is named. Do not substitute a different level, or unfrozen domains,
   and keep the rung's name.
2. **A rung crosses a machine checkpoint:** a dated decision note is mandatory — continue
   knowingly, reroute to B3, or stop. Silent overrun is forbidden, and so is ducking under a
   checkpoint by coarsening the basis, loosening thresholds, dropping CPS once mandatory,
   raising ρ\*, raising K_cap, enlarging q_s beyond the Q6 line, or dropping patterns. **Human
   hours are never a stop condition.**
3. **Cluster or rented-GPU access not formalised when first needed:** reach rungs stop and the
   stop is reported.
4. **A licence probe breaches its frozen threshold** — Q6 (noise line at the rung's size class;
   bias line; threshold line without CPS), **Q7** (Δ₂ outside τ₇, or the discriminability
   clause failed, or the shuffled-probe null passed, or recovered and direct blocks disagree),
   **Q8(a/b)** on direct blocks (no locality, or a family's correction carried by long-range
   pairs), **Q8(c)** (no saturation of K_off), or **ρ not reaching ρ\* by K_cap**: a measured
   result, reported as such. Q6-noise breach at a size class: mode E carries no "beat" language
   there; the rung continues as a cost record and, if mode G or CPS exists, under that. Q6-bias
   or Q7 or K_cap breach: Δ₂ does not enter a scored spectrum on the affected families at that
   rung; the pre-declared fallback is **DFT harmonic + DFT anharmonic, with Δ₂ applied only on
   families where Q7 passed, labelled per family** — it competes under the same protocol and
   may lose. Q8(a/b) breach on a family: that family's Δ₂ is reported with its long-range share
   and carries no accuracy claim finer than that share; if the breach is at R2–R3 on the
   scored families, fragment probing is invalid for those families and R6 loses them from its
   certificate. **Q8(c) breach: no size sentence** — the plan does not fall
   back to a point factory whose affordability no plan has measured.
5. **A promised accuracy rung loses to a line:** published with the paired table.

## 6. What this ladder refuses (carried, with additions)

- No global QFF of a huge molecule as a deliverable.
- No whole-molecule "gold rung" language above R1; anchors are "local-CC, R1-checked".
- No motif-transfer claim: every molecule gets its own probed Δ₂ — or, at R4–R6, a
  fragment-probed Δ₂ whose locality was measured on direct blocks at R2–R3 and is labelled as
  such (user directive 2026-09-04: a method decided by measurement, not a transfer of spectra). **[05]** The learned prior is not a transfer claim: it is scored by what it saves on
  bonus material, and the probes remain the answer.
- No CC correction to anharmonic constants as a promise; no "coupled-cluster anharmonic"
  language.
- No editing this ladder after a rung it governs has been scored, except by dated deviation
  note committed before the affected number is known.
- **[05]** No cost sentence outside the two forms of §1; no K written before it is measured;
  no Q8 ratio across mixed modes or mixed priors; no Q8 verdict computed on recovered blocks
  alone above R1.
