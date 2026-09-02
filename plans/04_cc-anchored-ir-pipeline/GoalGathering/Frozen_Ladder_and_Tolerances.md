# Frozen ladder and tolerances — Plan 04

**Status.** Frozen 2026-09-02 in *form*; the pilot-dependent numbers (§4) are frozen by a dated
note **before** any comparison they govern is scored. After that note, no number may be loosened
in either direction. Agrees with [Overarching_Goal.md](Overarching_Goal.md); the Goal file wins
on drift. Costs live in [Compute_Budget_2026-09-02.md](Compute_Budget_2026-09-02.md).

---

## 1. Two claim types, declared up front

- **Accuracy rungs (A).** Laboratory data exists. The claim is *beat the frozen line per band
  against the lab scoreboard* ([Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) §5).
- **Reach rungs (R).** No per-molecule laboratory spectrum exists. The claim is *the pipeline
  ran end-to-end and produced a spectrum with a stated error budget*; comparisons against the
  lines are **theory-vs-theory and labelled as such**. The word "beat" is forbidden on reach
  rungs. This split is what keeps "any aromatic in, spectrum out" honest at C₃₈₄H₄₈.

## 2. The ladder

| Rung | Molecule(s) | Type | Why this rung | Opponent line(s) | Lab scoreboard |
|---|---|---|---|---|---|
| **R0** | benzene C₆H₆ | A | End-to-end laptop pilot; canonical CCSD(T) is affordable here (measured, plan 02: single point ~20 s) | A, B | NIST gas-phase; PAHdb experimental |
| **R1** | naphthalene C₁₀H₈ | A | The plan-02 measured canonical-(T) wall (~114 basis functions at 28 GB, old machine) sits **between R0 and R1 at production bases** — so the R1 canonical-vs-DLPNO check is itself conditional: the first R1 probe measures whether canonical (T) runs on the *new* machine at any usable basis. If yes, R1 is the same-molecule license for all DLPNO anchors above it. If no, the license downgrades to **R0-only plus a declared cross-basis protocol**, and every anchor claim above R0 states that limitation | A, B | NIST; PAHdb experimental |
| **R2** | pyrene C₁₆H₁₀, tetracene and chrysene C₁₈H₁₂ (the **A-scored set**); triphenylene C₁₈H₁₂ is computed and **reported, not scored** — it has no laboratory spectrum | A | The PAHdb Anharmonic front ends at C₁₈H₁₂ — first territory where beating line B means beating the *best* small-molecule work; lab uids already recorded in plan-02 probes | A, B | PAHdb experimental (uids 334, 282, 291). IRMPD (Tang 2025 class) is **literature context only** for these neutral rungs — a cation measurement never scores a neutral spectrum |
| **R3** | coronene C₂₄H₁₂ | A | The source conversation's named case; Mulas 2018's molecule; the largest PAH with a usable matrix spectrum in hand (uid 18) | A, B (Mulas), C | PAHdb experimental (uid 18); cluster libraries as context only |
| **R4** | circumcoronene-class, C₅₄H₁₈ → ~C₉₆ | R | PAHdb-only + Mai territory; first rung with no per-molecule lab truth | A, C (theory-vs-theory) | — |
| **R5** | ~C₂₁₆ (top of Mai's set) | R | Meet line C at its own ceiling | A, C (theory-vs-theory) | — |
| **R6** | C₃₈₄H₄₈-class | R | Only line A exists here, at 4-31G; any physics beyond scaled-harmonic is new | A (theory-vs-theory) | — |

**Promised:** R0–R3 scored as accuracy rungs, R6 reached as a reach rung.
**Bonus:** R4, R5, and anything beyond R6. A bonus rung that does not run is not a failure;
a promised rung that does not run is reported fail-closed with the rung and cap named.

**Charge.** All rungs are **neutral species** unless a rung's pilot note names a charge state
explicitly. A laboratory spectrum of one charge state never scores a pipeline spectrum of
another.

**Ordering.** R0 before anything. R1 before any DLPNO-based accuracy claim (the
DLPNO-vs-canonical check at R1 — or its declared R0-only downgrade — is the license for DLPNO
anchors above it). Reach rungs may not
start before R3 has been scored — a pipeline that has not beaten anything has no business
burning node-hours on size.

## 3. Frozen now (not pilot-dependent)

- **Reporting unit:** cm⁻¹ per band; band families = CH-stretch (~3.3 µm), CC modes
  (6.2 / 7.7 / 8.6 µm), CH-oop by adjacency class (solo / duo / trio / quartet, 10–15 µm).
- **Resolution floor:** no claim finer than **10 cm⁻¹** is made in any astronomical framing
  (emission from a T- and charge-distributed ensemble has no sub-10 cm⁻¹ observational
  meaning). A lab-facing claim may be finer **only if** the measurement uncertainty *and* the
  declared controls (test RMSE, DLPNO-threshold sensitivity) both support it, printed by the
  comparison probe — and never finer than the scoreboard's own uncertainty (the source
  conversation's ~1 cm⁻¹ bind, carried).
- **Matrix tolerance:** Ar-matrix comparisons carry a shift tolerance. The **working
  convention is 15 cm⁻¹** (plan-02); the **binding value is the Module-03 measured one**,
  frozen in the pilot note (§4 item 4). This number lives in exactly one bin: the pilot note.
  No matrix-scored comparison may run before that note exists. Gas-phase preferred over matrix
  wherever both exist.
- **Comparison form (pre-registered):** paired per-band absolute error, pipeline vs line, on
  identical lab bands; aggregated per band family; reported as mean ± spread per family.
  ≥3 seeds for every ML component; mean ± SD across seeds. **Inconclusive is a publishable
  outcome.** The scoreboard is never a training or validation input of the pipeline
  (Distilled Q4; the M04 baseline is the declared exception recorded there).
- **No lab band may be scored twice under different windows.** Window and class assignment per
  band are fixed in the pilot note before any pipeline number exists for that molecule.

## 4. Frozen at the pilot note (form fixed now, numbers then)

The following numbers are written into a dated pilot note after (a) the **R0 pilot**, which
produces **no pipeline-vs-lab number** — it stops at geometry, Hessian, harmonic bands and
timings — and (b) the **scoreboard re-read probe**, which is lab-side only. The note is
committed **before any pipeline-vs-lab number exists for any molecule**; its inputs are the
lab side and the opponent side only, never pipeline output. Writing or amending it after a
pipeline-vs-lab number exists is forbidden (Distilled §4) — choosing windows after seeing an
R0 comparison table is the same act as re-windowing and is treated as such.

1. The exact band list per molecule (uid / NIST CAS, window, class). **Every §3 family that
   has laboratory data for a promised molecule must appear**; omitting one requires a dated
   justification inside the pilot note itself.
2. The "beat" margin per family: line beaten only if the pipeline's family mean |error| is
   smaller by at least that margin, and no promised family worsens by more than it. The list
   of promised families is closed in the same note.
3. The P-gate numbers for pipeline sanity (0 imaginary frequencies off-minimum tolerance,
   scale-factor policy: the pipeline uses **no** empirical scale factor on anharmonic output —
   if a harmonic fallback fires, its scale factor and fit set are declared).
4. The **matrix shift tolerance**, as measured by Module 03 (supersedes the 15 cm⁻¹ working
   convention of §3).
5. The **P3 effect size** for the Δ-vs-direct comparison (declared here, per Distilled §7,
   before either arm is scored).
6. The **M04 baseline recipe** (features, tuning budget, seeds), frozen so the baseline cannot
   be weakened after it is known what the pipeline finds hard.
7. **Resonance handling per rung** (Distilled §3): GVPT2 with named r₃/r₄ thresholds and a
   polyad cap; or MD-ACF with CH-stretch labelled classical; or CH-stretch unscored at that
   rung — chosen **before** any anharmonic surface for that rung is fitted.
8. **N_min per rung**: the minimum point count for a usable surface at that rung (with its
   justification), so the B2/B3 kill rule (Compute_Budget §3) is arithmetic, not judgement.

## 5. Stop conditions and escalation (declared in advance)

1. **ORCA/DLPNO unavailable** (license, install, or the new laptop underperforms): the rung
   stops; the missing binary or measurement is named. Do not substitute a different level and
   keep the rung's name.
2. **A rung exceeds its frozen cost cap** (budget doc): stop. Do not coarsen the basis, loosen
   DLPNO thresholds, or drop sampling to stay under the cap silently — that is a §-deviation
   note or a fail-closed report.
3. **Cluster access not formalized when first needed:** reach rungs stop and the stop is
   reported. The plan does not assume UvA access until an account and allocation exist in
   writing (dated note).
4. **The Q6 license/smoothness probes breach their frozen thresholds at R2/R3** (DLPNO
roughness — the source conversation's own named risk, now a *defined trigger*: DLPNO−canonical
or TightPNO−NormalPNO frequency deltas, or normal-mode second-difference noise, ≳ the P2 beat
margin for a family): that is a *measured result*, reported as such, and DLPNO anchors stop
licensing "beat" language on the affected families. Pre-declared fallback: hybrid output —
best-level harmonic + declared-provenance anharmonic correction — clearly labelled; it
competes against the lines under the same protocol and may lose.
5. **A promised accuracy rung loses to a line:** the loss is published with the paired table.
   The criterion is symmetric; losing is a result, not a reason to re-window bands.

## 6. What this ladder refuses

- No global QFF of a huge molecule as a deliverable (plan-02 lesson; grok_chat_3 argument).
- No whole-molecule "gold rung" language above R1: DLPNO locality error on delocalized π is
  not automatically small on curvatures, so DLPNO anchors are named "local-CC anchor,
  R1-checked", never "gold".
- No motif-transfer claim (that was grok_chat_3's thesis, not this one): every molecule gets
  its own surface; transfer, if ever observed, is a bonus observation, not a promise.
- No editing this ladder after a rung it governs has been scored, in either direction, except
  by dated deviation note committed before the affected number is known.
