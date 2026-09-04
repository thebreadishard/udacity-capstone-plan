# Frozen targets, v2: hybrid quartic force field, neutrals-first ladder

**Frozen 2026-08-26.** **Supersedes**
[Frozen_Ladder_and_Tolerances_2026-08-25.md](Frozen_Ladder_and_Tolerances_2026-08-25.md), which
remains in place unedited as the record of what was promised first.

Still committed **before** any gold-rung calculation, model training or comparison against an
experimental standard. Nothing has been computed. This is a change of plan, not a change of story
after seeing data.

## What changed, and why

Two decisions taken 2026-08-26 after Round 4 Pass B
([review record](Professor_Review_2026-08-25_Round4_PassB.md)):

| # | Change | Cause |
|---|---|---|
| **1** | The **hybrid quartic force field** becomes the primary method: \(\omega\) from the measured gold rung, \(\delta_{\mathrm{anh}}\) from a frozen cheaper level | Pass B issue 1. A fundamental is \(\nu=\omega+\delta_{\mathrm{anh}}\); electron correlation lands overwhelmingly in \(\omega\). The v1 plan bought coupled-cluster quality in order to take a *fourth* derivative of it |
| **2** | **Option F is now the primary deliverable.** Benzene and naphthalene, neutral. Cations, anthracene/phenanthrene and pyrene are bonus, not promise | Pass B issues 2 and 6. The Hessian cost table (Distilled §5.9) does not close at 10 h/week for the v1 ladder |

**The scope of this thesis got smaller on 2026-08-26.** That sentence belongs in the thesis, and it
is why v1 is retained rather than overwritten.

---

## 1. The ladder

| Rung | Species | Charge | Status | Named standard |
|---|---|---|---|---|
| **0** | Benzene, C₆H₆ | neutral | **Promised** | One NIST gas-phase FTIR dataset, ID and resolution fixed at G0 |
| **1** | Naphthalene, C₁₀H₈ | neutral | **Promised** | Gas-phase / He-tagged IR where it exists, else PAHdb experimental with the frozen shift model |
| **2** | Naphthalene cation | cation | *Bonus* | As rung 1 |
| **3** | Anthracene **and** phenanthrene | neutral | *Bonus* | PAHdb experimental. The isomer pair, if reached, supplies the degeneracy case |
| **4** | Pyrene | neutral, then cation | *Bonus* | IRMPD action spectroscopy (item 31) |
| **NC** | Negative control, fixed at G5 | — | **Promised if any identification is attempted** | As its nearest rung |

**Promised** means: it appears in the thesis abstract, and failing it is a failure of the thesis.
**Bonus** means: attempted in ladder order if G1a's measured costs allow, reported if reached, and its
absence is a stated limitation rather than a broken promise.

**Cations are a fallback path, not an escalation.** Open-shell local coupled cluster is more expensive
and less reliable, open-shell MLIP fine-tuning is unproven for high-order derivatives, and cation
experimental standards carry their own systematic offsets. Every cation rung is bonus.

**Identification (§5) requires at least two promised rungs to have passed G5.** With fewer, there is
no target list worth pre-registering, and the thesis reports the spectroscopy without the
identification.

H₂O, D₂O and CO₂ remain toolchain regression tests. No claim rests on them.

## 2. Scored band families

Unchanged from v1: **3.3 μm** (aromatic C–H stretch), **6–9 μm** (C–C stretch and C–H in-plane bend),
**11–12 μm** (C–H out-of-plane bend).

Rung 0 is still scored differently: benzene is a single ring, its out-of-plane C–H bend does not sit
in the 11–12 μm window, and it is therefore scored on **all IR-active fundamentals in the chosen NIST
dataset**. Band-family scoring begins at rung 1.

Modes are matched to reference by **displacement-vector overlap, never by index**, and the overlap
value is reported.

## 3. Tolerances

### 3.1 Band centres — both conditions required, unchanged from v1

| | Condition |
|---|---|
| **Absolute** | ≤ **10 cm⁻¹** against gas-phase or action spectroscopy; ≤ **15 cm⁻¹** against matrix data with the frozen shift model |
| **Relative** | Mean absolute error **no worse than the scaled-harmonic baseline** on the same modes |

**Warning recorded at freeze time.** The closest published precedent for the hybrid scheme —
Lam, Abdul-Al & Allouche (2020), arXiv:1909.12661, quantum-mechanical harmonics plus machine-learned
anharmonic corrections over 37 molecules — reports RMSD **21 cm⁻¹** against its reference level and
**23 cm⁻¹** against experiment. That is **twice our absolute tolerance**.

This is not a reason to loosen the tolerance. It is a reason to expect the G1b pilot to be
informative, and to expect "did not pay for itself" to be a live outcome for some band families. A
tolerance chosen to be comfortably reachable would test nothing.

### 3.2 Relative intensities

Unchanged: ≤ **20 %** on integrated intensity ratios within a band family; neutral-to-cation swap
reproduced qualitatively **wherever both charge states were computed** — which, under decision 2, may
be nowhere. If no cation rung is reached, the swap is reported as untested, not as passed.

### 3.3 Label-level tolerances

Unchanged and still authoritative (Distilled §5.5): relative energy RMSE ≤ 1.0 kcal/mol with max
≤ 2.0; directional derivative RMSE ≤ 1.0 meV/Å; audited harmonic modes ≤ 5 cm⁻¹.

### 3.4 New: the hybrid decision threshold (gate G1b)

On benzene, three treatments are computed against the same frozen experimental standard:

1. \(\omega_{\text{gold}} + \delta_{\text{cheap}}\) — the hybrid
2. a full gold-rung quartic force field — the expensive alternative
3. scaled-harmonic B3LYP — the status quo

**Decision rule, fixed now:**

- If (1) lies within **3 cm⁻¹** MAE of (2), the hybrid is adopted and **gold-rung third and fourth
  derivatives are forbidden for the remainder of the project.**
- If (1) is worse than (2) by more than 3 cm⁻¹ **and** (2) beats (3), the hypothesis that correlation
  matters only for \(\omega\) is **falsified for these families**, and the cost table decides whether
  the full QFF is affordable at rung 0 alone.
- If (2) does not beat (3), the electronic-structure rung is **not the limiting term**, the thesis
  reports that as its finding, and the remaining effort goes to nuclear motion.

All three outcomes are publishable. The third is the one Tang et al. (2025) makes plausible.

## 4. The stop rule

Unchanged in form. Climbing stops at the first rung where any scored band family exceeds its §3.1
absolute tolerance, for any computed charge state. That rung is published as the measured limit.

**Added:** climbing also stops when the measured cost of the next rung's Hessian exceeds the remaining
budget recorded at G1a. A cost stop is reported with the same weight as an accuracy stop, and with the
measured number.

## 5. Identification rule

Unchanged from v1 §5, with one addition: **if fewer than two promised rungs pass G5, no
identification is attempted**, and the thesis says so rather than confronting an observation with one
species.

## 6. Deliberately not frozen

As v1 §6, plus:

| Open | Closes at |
|---|---|
| The specific cheap level for \(\delta_{\mathrm{anh}}\) (B3LYP-family functional and basis, or the MLIP trained at that level) | **G0**, in a dated amendment, before the G1b pilot runs |
| Whether the MLIP is used at all for \(\delta_{\mathrm{anh}}\), or direct cheap-level QFFs suffice | **G1a**, on measured cost |

The GVPT2 resonance criterion remains the item most likely to be fudged, and its rule is unchanged:
fixed at G0 in a dated amendment, **without which no GVPT2 result may be reported**.

## 7. Form of an amendment

As v1 §7, unchanged. `Amendment_<date>_<subject>.md`, stating what is now fixed, the convention it
follows, and that nothing else moves. The commit date is the evidence.

## 8. Checklist for a reviewer

- [ ] Is this document's commit date earlier than the first gold-rung calculation?
- [ ] Do the two G0 amendments exist — cheap level, and resonance criterion — and do they predate the
      results they govern?
- [ ] Was the G1b hybrid decision made by the §3.4 rule, and recorded with all three numbers?
- [ ] Is every reported band centre accompanied by both the absolute **and** the relative condition?
- [ ] Is the four-term error budget present per molecule, charge state and band family — not pooled?
- [ ] Was the stop rung published with the measured error **or cost** that triggered it?
- [ ] Are bonus rungs reported as bonus, and their absence as a limitation rather than a silence?
- [ ] Did the negative control fail?
