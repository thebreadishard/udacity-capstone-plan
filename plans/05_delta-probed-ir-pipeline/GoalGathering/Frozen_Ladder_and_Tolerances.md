# Frozen ladder and tolerances — Plan 05

**Status.** Frozen 2026-09-03 in *form*, carried from plan 04 with the plan-05 additions marked
**[05]**; the pilot-dependent numbers (§4) are frozen by a dated note **before** any comparison
they govern is scored. After that note, no number may be loosened in either direction. Agrees
with [Overarching_Goal.md](Overarching_Goal.md); the Goal file wins on drift. Costs live in
[Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md).

---

## 1. Two claim types, declared up front (carried)

- **Accuracy rungs (A).** Laboratory data exists. The claim is *beat the frozen line per band
  against the lab scoreboard* ([Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) §5).
- **Reach rungs (R).** No per-molecule laboratory spectrum exists. The claim is *the pipeline
  ran end-to-end and produced a spectrum with a stated error budget*; comparisons against the
  lines are **theory-vs-theory and labelled as such**. The word "beat" is forbidden on reach
  rungs.
- **[05] Cost claims are a third kind of sentence**, allowed on any rung, and only in the form
  "K = n probes at this rung, mode E/G, wall-clock w per probe, printed by `probes/…`". A cost
  sentence without a probe file is forbidden, including in the Module 08 paper.

## 2. The ladder (rungs and species carried verbatim from plan 04)

| Rung | Molecule(s) | Type | Why this rung | Opponents | Lab scoreboard | **[05] what it licenses** |
|---|---|---|---|---|---|---|
| **R0** | benzene C₆H₆ | A | End-to-end laptop pilot; canonical CCSD(T) affordable (plan-02 measured ~20 s/point, old machine) | A, B | NIST gas; PAHdb experimental | **Q7 probing licence**: recovered Δ₂ vs a directly computed reference Δ₂ (full numerical canonical/local-CC Hessian minus DFT Hessian); also the zero-CC dry run of the recovery code |
| **R1** | naphthalene C₁₀H₈ | A | The canonical-vs-local-CC licence molecule, conditional exactly as in plan 04 (first R1 probe measures whether canonical (T) runs on the new machine; else R0-only + declared cross-basis protocol, stated in every anchor claim) | A, B | NIST; PAHdb experimental | Q6 anchor licence; Q7 at a second size; first **Q8 locality-decay** read; first mode-E vs mode-G timing |
| **R2** | pyrene C₁₆H₁₀; tetracene, chrysene C₁₈H₁₂ (A-scored set); triphenylene computed and reported, not scored | A | First territory beyond PAHdb's anharmonic front | A, B | PAHdb experimental (uids 334, 282, 291); IRMPD = context only | Q8 second read; K must be printed; Δ₃/Δ₄ probing on the promised families for the first time |
| **R3** | coronene C₂₄H₁₂ | A | Mulas 2018's molecule; largest PAH with a usable matrix spectrum (uid 18) | A, B (Mulas), C | PAHdb experimental (uid 18) | Q8 third read; **the saturation test**: K(R3) vs K(R2) vs K(R1) printed side by side |
| **R4** | circumcoronene-class, C₅₄H₁₈ → ~C₉₆ | R | First rung with no per-molecule lab truth | A, C (theory-vs-theory) | — | expert-judgment datum (Goal, tier 3); fragment-probing bonus arm **only if** the user decides it in |
| **R5** | ~C₂₁₆ (top of Mai's set) | R | Meet line C at its own ceiling | A, C | — | — |
| **R6** | C₃₈₄H₄₈-class | R | Only line A exists here, at 4-31G | A (theory-vs-theory) | — | the reach certificate; **K(R6) reported against K(R3)** in the same sentence as the spectrum |

**Promised:** R0–R1 scored as accuracy rungs against gas-phase data. R2–R3 scored as accuracy
rungs **conditional on the M03 matrix–gas gate** (plan-04 decision, 2026-09-02): a family whose
|matrix−gas| delta is ≳ its beat margin is scored **"pre-declared inconclusive on matrix"**.
R6 reached as a reach rung, **conditional on B3**; if the allocation never exists, R6 is
reported fail-closed. **[05]** In addition, the promised set includes the **cost record**:
K, mode and wall-clock per probe at every rung that ran, in one table.
**Bonus:** R4, R5, anything beyond R6, the learned-prior arm (P3), and fragment probing.

**Charge.** All rungs are **neutral species** unless a rung's pilot note names a charge state.

**Ordering.** R0 before anything. R1 before any local-CC-based accuracy claim. **[05]** Q7 must
pass at R0 and R1 before any Δ enters a scored spectrum; Q8 must be printed at R1, R2 and R3
before K(R6) is estimated. Reach rungs may not start before R3 has been **scored** (scored
includes lost and pre-declared inconclusive).

## 3. Frozen now (not pilot-dependent)

- **Reporting unit:** cm⁻¹ per band; families = CH-stretch (~3.3 µm), CC modes (6.2 / 7.7 /
  8.6 µm), CH-oop by adjacency class (solo / duo / trio / quartet, 10–15 µm).
- **Resolution floor:** no claim finer than **10 cm⁻¹** in any astronomical framing; a
  lab-facing claim may be finer only if the measurement uncertainty *and* the declared controls
  (recovery residual, local-CC noise floor, threshold sensitivity) support it, printed by the
  comparison probe — never finer than the scoreboard's own uncertainty (~1 cm⁻¹ bind).
- **Matrix tolerance:** working convention **15 cm⁻¹**; binding value = the Module-03 measured
  one, frozen in the pilot note (§4 item 4). Gas-phase preferred over matrix wherever both exist.
- **Comparison form (pre-registered):** paired per-band absolute error, pipeline vs line, on
  identical lab bands; per family; mean ± spread. ≥3 seeds for every ML component.
  **Inconclusive is a publishable outcome.** The scoreboard is never a training or validation
  input of the pipeline (Distilled Q4; the M04 baseline is the declared exception).
- **No lab band may be scored twice under different windows.**
- **[05] Frozen domains:** every local-CC probe evaluation at a displaced geometry uses
  correlation domains and pair lists frozen at the reference geometry. A code that cannot do
  this at the anchor level is reported under stop condition 1, not worked around silently.
- **[05] Probe patterns are hashed** in the Q0 deck before the first probe runs; adding
  patterns after the recovery residual is known is a §4 deviation (Distilled).
- **[05] The promised route uses the uninformed prior.** The learned Δ-prior (M05) may reduce
  K only on rungs where the P3 saving was demonstrated on held-out probes at the previous
  rung, and never on a promised accuracy rung's scored spectrum.

## 4. Frozen at the pilot note (form fixed now, numbers then)

Written into a dated pilot note after (a) the **R0 pilot** — geometry, Hessian, harmonic
bands, timings, the zero-CC dry run and the Q7 reference comparison, **no pipeline-vs-lab
number** — and (b) the **scoreboard re-read probe**. Committed **before any pipeline-vs-lab
number exists for any molecule**; inputs are the lab side, the opponent side and the
probe-machinery side only, never a pipeline spectrum.

1. The exact band list per molecule (uid / NIST CAS, window, class); every §3 family with lab
   data for a promised molecule must appear.
2. The "beat" margin per family; the list of promised families closed in the same note.
3. The P-gate numbers (0 imaginary frequencies tolerance; scale-factor policy: **none** on
   anharmonic output; a harmonic fallback declares its factor and fit set).
4. The **matrix shift tolerance** as measured by Module 03.
5. The **P3 effect size** — **[05] redefined**: the probe-count saving (or recovery-residual
   reduction at fixed K) that the learned prior must deliver to count, declared before either
   arm is scored.
6. The **M04 baseline recipe** (features, tuning budget, seeds).
7. **Resonance handling per rung** (carried): GVPT2 with named r₃/r₄ thresholds and a polyad
   cap; or MD-ACF with CH-stretch labelled classical; or CH-stretch unscored.
8. **[05] K per rung and per mode** (E and G): the probe count at which the recovery is
   declared converged, with its justification (held-out residual curve from R0–R1), so the
   B2/B3 **classification rule** (`wall_clock_per_probe × K`) is arithmetic. Replaces plan
   04's N_min.
9. **[05] r_c, the locality length**, and the **Q8 decay criterion** (the functional form and
   threshold below which a Δ₂ element is treated as zero), from the R1 read; re-printed at R2
   and R3, never loosened.
10. **[05] The Q7 tolerance** per family: how close the recovered Δ₂ must come to the reference
    Δ₂ at R0–R1, in cm⁻¹ of harmonic frequency, before Δ is licensed to enter a scored
    spectrum — no larger than the smallest beat margin.
11. **[05] The held-out fraction f_h** of probes kept out of the recovery for the residual.

## 5. Stop conditions and escalation (declared in advance)

1. **Local-CC code unavailable at the anchor level, or unable to freeze domains, or the new
   laptop underperforms:** the rung stops; the missing binary, option or measurement is named.
   Do not substitute a different level, or unfrozen domains, and keep the rung's name.
2. **A rung crosses a machine checkpoint:** a dated decision note is mandatory — continue
   knowingly, reroute to B3, or stop. Silent overrun is forbidden, and so is ducking under a
   checkpoint by coarsening the basis, loosening thresholds, shrinking K below the frozen
   value, or dropping patterns. **Human hours are never a stop condition.**
3. **Cluster or rented-GPU access not formalised when first needed:** reach rungs stop and the
   stop is reported.
4. **A licence probe breaches its frozen threshold** — Q6 (local-CC vs canonical, TightPNO vs
   NormalPNO, smoothness with frozen domains), **Q7 (recovered vs reference Δ₂ at R0–R1)**,
   or **Q8 (no locality decay, or K not saturating between R1, R2 and R3)**: a measured result,
   reported as such. Q6/Q7 breach: Δ does not license "beat" language on the affected families;
   the pre-declared fallback (best-level harmonic + declared-provenance correction, labelled)
   competes under the same protocol. **Q8 breach: the size claim is withdrawn** — R6 is
   reported as "not reachable at a saturating cost; Δ locality measured thus", and the plan
   does not fall back to a point factory it has already shown it cannot afford.
5. **A promised accuracy rung loses to a line:** published with the paired table.

## 6. What this ladder refuses (carried, with one addition)

- No global QFF of a huge molecule as a deliverable.
- No whole-molecule "gold rung" language above R1; anchors are "local-CC, R1-checked".
- No motif-transfer claim: every molecule gets its own probed Δ; transfer, if ever observed,
  is a bonus observation. **[05]** The learned prior is not a transfer claim: it is scored by
  what it saves, and the probes remain the answer.
- No editing this ladder after a rung it governs has been scored, except by dated deviation
  note committed before the affected number is known.
- **[05]** No cost sentence ("size-independent", "O(1)", "a few hundred points") outside the
  form of §1's third sentence type.
