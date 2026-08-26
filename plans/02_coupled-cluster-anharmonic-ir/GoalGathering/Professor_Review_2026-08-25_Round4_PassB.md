# Professor Review — 2026-08-25/26, Round 4, Pass B (adversarial domain review)

**Reviewer:** Grok, given [the Pass B brief](Review_Brief_2026-08-25_Round4_PassB.md) after Pass A's
findings were written down.

**Verdict:** *Conditional — green light only for a neutrals-first ladder that stops at the first
measured cost or accuracy wall, with option F (small-molecule excellence) elevated from safety net to
the default deliverable. **No green light for the full neutral+cation pyrene claim** under the stated
10 h/week constraint.*

**Outcome: both recommendations accepted.** This review did not find that the plan was wrong. It
found that the plan was **more expensive than it needed to be, aimed at the wrong derivative, and
promising more than the calendar allows**. All three are now fixed. The resulting scope reduction is
recorded in [Frozen_Ladder_and_Tolerances_2026-08-26.md](Frozen_Ladder_and_Tolerances_2026-08-26.md),
which supersedes the 2026-08-25 freeze.

---

## Blocking findings

### Issue 1 — the core hypothesis may be oriented the wrong way

**Where:** Distilled §2; Overarching_Goal §2.

The plan asserted that the dominant error in large-PAH IR is electronic-structure error rather than
nuclear-motion error. The reviewer produced verified evidence pointing the other way for the 6–9 μm
region: electron correlation is critical for **quadratic** constants and geometry, while its effect on
**cubic/quartic** constants is substantially smaller; a 2025 DFT survey over seven PAHs and 182
fundamentals found hybrid GGAs already the best practical performers.

**Response, in two parts.**

*The reviewer overreached once, and accepted the correction.* "Climbing Jacob's ladder does not
improve anharmonic frequencies" concerns the **DFT functional hierarchy**. Coupled cluster is not on
that ladder. The survey therefore does not show that CCSD(T) adds nothing.

*But the underlying argument holds, and it is worth more than the objection.* A fundamental is
\(\nu=\omega+\delta_{\mathrm{anh}}\); \(\omega\) is the overwhelming majority of the number and is
where a systematic electronic-structure error lands. If correlation matters for \(\omega\) and much
less for \(\delta_{\mathrm{anh}}\), then **the plan was spending its expensive labels on the wrong
derivative** — building a coupled-cluster-quality surface in order to differentiate it four times,
when the fourth derivative did not need that quality.

**Status: CLOSED by restructure.** The hybrid quartic force field is now the **primary** architecture
(Distilled §6.4): \(\omega\) from the measured gold rung, \(\delta_{\mathrm{anh}}\) from a frozen
cheaper level. The hypothesis is restated in a sharper, cheaper, falsifiable form — *coupled cluster
improves \(\omega\), not \(\delta_{\mathrm{anh}}\)* — and a front-loaded pilot at gate **G1b** now
tests it on benzene before any production spend.

**Not closed as science.** The pilot may find the hybrid loses. Tang et al. (2025) already report
scaled harmonic sufficient for pristine pyrene cations, so "it did not pay for itself" remains a
pre-registered, publishable outcome.

### Issue 2 — the cost arithmetic was missing

**Where:** Distilled §5.1–§5.3, §5.7; Restructure §10.

The plan cited Kumar, Neese & Valeev (2020) — DLPNO-CCSD(T)-F12 on 550+ atoms in under three days —
for a campaign requiring hundreds of geometries with gradients. That citation is a **single-point
energy**.

Two facts the reviewer verified that the plan did not contain:

- **ORCA does not provide analytic gradients for full DLPNO-CCSD(T).** Numerical gradients cost ~6N
  single points each.
- Open-shell carries roughly 1.5× overhead, and TightPNO — required for delocalized π per Sylvetsky
  & Martin — is substantially more expensive than default settings.

**Status: CLOSED in spec, and the finding got worse before it got better.** The reviewer then noted
that ORCA has **no analytic DLPNO-CCSD(T) Hessian either**, so the hybrid restructure does not escape
by itself. Distilled §5.9 now carries the multiplication, per rung, for Hessians rather than for
hundreds of gradients — and that table is what forced the ladder to shrink.

**Not closed as science** until the G1a pilot replaces the estimates with measurements.

### Issue 3 — semidiagonal GVPT2 at pyrene-scale congestion is optimistic

**Where:** Distilled §2.1, §6.4; Frozen ladder.

Feasibility rested on 21-atom aspirin. Pyrene has 72 modes and a dense 6–9 μm region where plain VPT2
diverges and selected VCI is the standard escalation. The families most likely to end UNRESOLVED are
precisely the diagnostic ones.

**Status: CLOSED by scope reduction.** Pyrene is no longer a promise (see issue 6). The escalation
ladder is unchanged, but the reviewer's requirement is adopted: the **fraction of 6–9 μm modes left
UNRESOLVED must be reported for benzene and naphthalene** before any larger species is attempted.

### Issue 4 — no published evidence that a fine-tuned foundation MLIP carries CC-quality third derivatives

**Where:** Distilled §5.8, §6.1–§6.2; gate G2.

Verified: searches for MACE + cubic/VPT2/anharmonic force constants return classical MD or harmonic
spectra. Nobody has shown that a hybrid-DFT foundation model fine-tuned on O(10²) coupled-cluster
points recovers CC-quality third and fourth derivatives for a 26-atom aromatic.

**Status: CLOSED by removing the requirement.** Under the hybrid architecture the MLIP no longer
needs to carry coupled-cluster-quality third derivatives. Its role is demoted from *carrier of the
precision* to **accelerator of the cheap half** — it supplies \(\delta_{\mathrm{anh}}\) at a level
where abundant training data exists and where the requirement is a correction, not a gold-standard
derivative. The G2 cubic-stability gate remains, now measured against a **cheap-level** reference QFF
rather than a coupled-cluster one.

The reviewer's caution is recorded: this makes the problem smaller, not absent. Any species without an
affordable Hessian still relies on a differentiated surface.

### Issue 5 — the residual contribution is closer to a rigorous wrapper than a new method

**Where:** Distilled §2.1; Restructure §4.

Verified: Mai et al. (2025) already delivered anharmonic spectra for 1704 PAHdb species to C₂₁₆;
transfer-learning VPT2 pipelines exist. The reviewer found **no prior work** publishing a
per-band-family local-vs-canonical error budget for PAH IR inside a pre-registered, negative-control
identification — so the combination is real, but novelty is field-dependent and thinner than claimed.

**Status: ACCEPTED, no change of substance.** The thesis is framed as *reliability-gated spectral
identification for astrochemistry*, which is already the industry frame in `Overarching_Goal.md` §5.
The chemical contribution is **the measured error budget, not a new method**, and Distilled §2.1 now
says so in those words.

### Issue 6 — the effort table is unmeasured guesses; the calendar does not close

**Where:** Restructure §10.

**Status: CLOSED by scope reduction.** Option F is elevated from fallback to **primary deliverable**.
Benzene and naphthalene, neutral, fully budgeted, both baselines, with the hybrid pilot. Cations,
anthracene/phenanthrene and pyrene become **bonus rather than promise**. Cations are a fallback path,
not an escalation.

---

## Non-blocking findings

| Finding | Status |
|---|---|
| The two-part band tolerance is well designed but stringent; many families may be reported "did not pay for itself" | **Accepted as intended behaviour.** That is the honest outcome the tolerance exists to make visible, and §2 pre-registers it |
| Cations are the weakest link on all three fronts — open-shell local CC, open-shell MLIP, action-spectroscopy standards with their own offsets. Shrink-to-neutrals should be the default, not an escalation | **Adopted.** Recorded in the 2026-08-26 freeze |
| Pass A's status contradictions are real but secondary to the science | **Already closed** in the Pass A record |

## What passed

- The governance machinery — pre-registration, frozen ladder, non-poolable four-term budget,
  independent position/intensity gates, negative control, "inconclusive is publishable", claim
  ladders — *"is unusually strong for a master's and survives the pivot intact."*
- The demotion of classical MD to a diagnostic and of the voxel field to a non-critical leg is
  *"clean and removes the most obvious over-claims of plan 01."*
- Requiring every cm⁻¹ claim to carry the measured local-vs-canonical error is *"scientifically
  correct and a genuine improvement over the unquantified DFT surfaces that dominate the PAH
  literature."*
- The stop rule and UNRESOLVED category *"correctly convert failure into a publishable measured
  limit."*

## Approval conditions

Set by the reviewer, before `Capstone_Mapping.md` or any module document is rewritten:

| # | Condition | Status |
|---|---|---|
| 1 | Execute and commit the G1 cost-pilot table under exact production settings | **Blocked on compute.** Estimates in Distilled §5.9; the pilot replaces them |
| 2 | Commit the G0-dated resonance-criterion amendment | **Blocked on toolchain selection at G0** |
| 3 | Run the electronic-structure vs nuclear-motion pilot (issue 1) | **Now gate G1b**, front-loaded before production spend |
| 4 | Update the three Pass A status statements | ✅ **Done** |
| 5 | Decide in writing whether option F is primary | ✅ **Done** — it is |

**Conditions 1–3 require calculations that have not been run.** Plan 02 is therefore complete as a
plan and **blocked on measurement**, which is the correct terminal state for a document that promised
to measure rather than assert.

---

## Assessment of this review

The most valuable finding was not on the reviewer's list. Issue 1's *evidence* — that correlation
matters for \(\omega\) far more than for \(\delta_{\mathrm{anh}}\) — implied a restructure the
reviewer did not draw, and which he then correctly trimmed when this author overstated it: the three
issues it touches are **moved to a cheaper, testable form, not solved**.

Two corrections went the other way, and both were accepted: the Jacob's-ladder conflation, and the
claim that the hybrid architecture escapes the cost problem. It does not. It escapes *hundreds of
gradients* and lands on *one Hessian per species*, which is smaller but not small — and it is the
Hessian table that finally decided the ladder.

A review that changes the plan is worth more than one that grades it.
