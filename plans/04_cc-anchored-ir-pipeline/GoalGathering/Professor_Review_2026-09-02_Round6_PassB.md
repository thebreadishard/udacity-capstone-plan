# Professor review — Round 6, Pass B (adversarial domain)

**Date.** 2026-09-02.
**Role.** Hostile examiner (computational vibrational spectroscopy / local CC / scientific ML).
Not trying to help. Trying to find the month-fourteen failure.
**Corpus.** Pass A file (patched freeze claimed same day in the plan README); then
Overarching_Goal, Frozen_Lines, Frozen_Ladder, Compute_Budget, Capstone_Mapping, Distilled,
Relevant_Scientific_Papers, probes/README, grok_chat_4, plan README / tree banners.
**Literature verified this pass (not recall).** Mulas et al. arXiv:1809.05669 / JCP **149**,
144102 (2018); Tang et al. arXiv:2504.11898 / JCP **163**, 044304 (2025); Mai et al.
arXiv:2503.05120 / MNRAS **541**, 3073 (2025); Sylvetsky, Banerjee, Alonso & Martin
arXiv:2001.08641 / JCTC **16**, 3641–3653 (2020) — identifier pinned this pass against
[Papers/30_Sylvetsky2020_LocalCC_Porphyrins.pdf](../../../Papers/30_Sylvetsky2020_LocalCC_Porphyrins.pdf)
and the arXiv abstract (HTML 404; abstract + local PDF filename used); Kumar, Neese & Valeev
arXiv:2008.03237 / JCP **153**, 094105 (2020); Käser, Boittier, Upadhyay & Meuwly
arXiv:2103.05491 (2021). grok_chat_4 is a source conversation, labelled as such, never as a
budget. Hudgins & Sandford 1998 (bib item 8) was **not** re-read this pass.

Plans 01–03 stay dead. Nothing below reopens them.

---

**Verdict: no green light for the promised set (R0–R3 scored “beat” + R6 “reached” +
Modules 02–09 inside 840 h).**

Plan 04 is not a mistake as a *laptop pipeline idea*. It is a mistake as currently promised.
The accuracy/reach split is honest governance; the promised accuracy rungs R2–R3 are not
decidable on the scoreboard the plan actually owns, the anharmonic method is unnamed where
PAHs break VPT2, the DLPNO factory that would have to buy the improvement is a B3 object
without an allocation, and R6 cannot be wrong in a way anyone could detect. A legitimate
continuation is a **cut promise**: R0–R1 NIST gas-phase, fail-closed if the R1 license or a
timed factory does not fit B2, R2–R3 only as pre-declared inconclusive or as same-charge
IRMPD, R6 dropped from Module 08. Until that cut is written into the Goal/Ladder/Distilled
claim ladder, Module 08 is defending a criterion the literature will not support.

---

## Blocking findings

### 1. The R2–R3 “beat” is scored on a matrix scoreboard that cannot resolve it

**Where:** Frozen_Lines §5–§6; Frozen_Ladder §2 R2–R3 and §3 matrix tolerance;
Overarching “What is scored”; Distilled §7 P2 and §9 steps 2–4.

**What:** Promised accuracy rungs R2 (pyrene/tetracene/chrysene) and R3 (coronene) are typed
**A** and scored against PAHdb experimental v3.10 (Ar matrix, ~5–15 K). The plan’s own
measured floor is scaled-harmonic quartet mean |error| **7.1 cm⁻¹** vs that same Ar matrix
(commit `800f3aa`), with working matrix tolerance **15 cm⁻¹** until Module 03 measures a
binding value. Anharmonic corrections of a few cm⁻¹ cannot beat a 7 cm⁻¹ floor inside a
15 cm⁻¹ systematic and still be a verdict. Inconclusive is allowed in Ladder §3; it is **not**
what Distilled §9.4 promises (“P2 at R2–R3 → …and it holds where PAHdb’s anharmonic front
ends”).

**Evidence (verified this pass):**
- Frozen_Lines §6: quartet 7.1 / solo −36 / duo −49 cm⁻¹ vs Ar matrix; lab quartet spread
  60.2 cm⁻¹.
- Frozen_Lines §5: PAHdb gas-phase library v1.00 = **5 spectra, CN-substituted**. That is not
  an R2–R3 gas set. NIST is named for R0/R1. R3 lab cell is uid 18 (matrix).
- Mulas 2018 (arXiv:1809.05669): pyrene/coronene QFF compared mostly to **Ne matrix 4 K**
  (Joblin 1994). “Matrix effect expected weak for neon.” Positions excluding CH stretch
  “accurate on average to better than 0.8%.” 0.8% of a 1600 cm⁻¹ CC mode is ~13 cm⁻¹; of a
  3000 cm⁻¹ CH stretch is ~24 cm⁻¹. The paper’s own honesty sentence: conclusions “might
  slightly change if/when full high-res low-T gas-phase spectra become available.” CH stretch
  is less resolved in Ne than in low-T gas (Maltseva). The plan scores **Ar**, not Ne; Ar
  shifts are not the “expected weak” neon case. Hudgins & Sandford 1998 (the Ar-matrix source
  behind many PAHdb uids) was **not re-read this pass** — no per-band Ar-vs-gas table is
  verified here.
- Mai 2025 (arXiv:2503.05120): experimental comparison is matrix isolation
  (Hudgins/Allamandola/Sandford) at 50 K MLMD vs matrix, and 300 K vs NIST gas (assumed
  ~300 K). The field’s own large-PAH “anharmonic vs lab” papers already mix T, matrix, and
  gas without a cm⁻¹-class isolation of method error.
- Tang 2025 (arXiv:2504.11898): the modern R2 **gas** standard is IRMPD of **cations**,
  600–1800 cm⁻¹, 3 cm⁻¹ FELIX steps, 0.4% bandwidth. Ladder charge rule (verified in freeze):
  a cation measurement never scores a neutral spectrum. So the one gas dataset that could
  resolve R2 is declared out of scope.

**Why it matters:** This attack does not kill the pipeline. It kills the *criterion* at the
rungs Distilled uses to say the method “holds where PAHdb’s anharmonic front ends.” A P2
“beat” against Ar-matrix data whose own systematic is larger than the plan-02 floor, and
larger than any honest anharmonic increment, is not a defence sentence. R0–R1 with NIST gas
remain decidable. R2–R3 as promised are not.

**What would close it:**
- *In spec:* Distilled §9.4 and the promised-set sentence in the plan README / Ladder §2
  reword R2–R3 to **pre-declared inconclusive on matrix**, with “beat” allowed only on
  families that have gas-phase coverage (R0–R1 NIST; same-charge IRMPD if the pilot note
  names a cation). Module 03 must print a measured matrix-vs-gas delta **before** any R2 P2
  language is used.
- *As science:* an M03 table of per-band Ar-matrix minus gas (or Ne minus gas) for every
  promised R2–R3 uid. If that delta ≳ the beat margin, P2 on those uids is forbidden, not
  optional.

---

### 2. The R1 canonical-vs-DLPNO “license” does not license coronene π curvatures

**Where:** Frozen_Ladder §2 R1, §5 stop 4, §6 “no gold rung”; Distilled §3 anchors;
Overarching method skeleton; bib item 15; grok_chat_4.

**What:** DLPNO-CCSD(T) is a locality truncation for **energies**. The plan then trains an ML
surface on those energies (optionally forces) and differentiates it into anharmonic
frequencies. One canonical check at naphthalene (itself **conditional**: if canonical (T)
fails on the new machine, the license **downgrades to R0-only**) is then used at C₁₆–C₂₄.
That is a fig leaf, not a license. Stop 4 (“roughness is a measured result”) does not say
what observable trips it, so it will not trip.

**Evidence (verified this pass):**
- Sylvetsky, Banerjee, Alonso & Martin, JCTC **16**, 3641 (2020), arXiv:2001.08641.
  **Identifier pinned this pass** (bib item 15 was an unpaid debt; this is labelled
  verified-this-pass, not a scored Module 03–09 cite). Expanded porphyrins: Möbius-like
  structures have much stronger static correlation; this “causes significant errors in
  DLPNO-CCSD(T) and even DLPNO-CCSD(T1) approaches, **unless TightPNO cutoffs are employed**.”
  Sub-kcal/mol vs canonical on Möbius required Nagy & Kállay LNO-CCSD(T) with tight settings,
  “at much greater computational expense.” The POLYPYR21 set is a benchmark for **relative
  energies** under varying static correlation — **not Hessian eigenvalues, not PAH IR
  curvatures.** Treating TightPNO-on-porphyrin-energies as a naphthalene-IR license is a
  category error the bibliography itself invited and did not pay.
- grok_chat_4 (source conversation, not a paper): locality thresholds make the surface uneven;
  “Daardoor krijg je voor coroneen geen chemisch nauwkeurig, volledig anharmonisch spectrum
  op die manier.” The freeze carries roughness as stop 4 and forbids “gold” language. It does
  not carry a curvature-delta gate.
- Distilled §3: the R1 check is already allowed to fail and become “R0-only plus a declared
  cross-basis protocol.” After that downgrade, every R2–R3 DLPNO point is an unlicensed local
  approximation on a larger, more delocalized π system than the license molecule.
- Kumar, Neese & Valeev, arXiv:2008.03237: TightPNO recovers ~99.86% of canonical correlation
  energy on the trityl radical; absolute error on a ~3 Eh correlation energy is still
  ~2.7 kcal/mol. Relative energies are the selling point. **Nothing in that paper is a
  frequency or a Hessian.** Chemical accuracy on heats of formation is not ~1 cm⁻¹ on a
  curvature.

**Why it matters:** If DLPNO curvature noise at R2–R3 exceeds the anharmonic signal, the Δ-arm
of the controlled comparison **is** the DFT baseline plus fitted noise. P3 “the anchor buys X”
then prints a number. Whether that number is ~0 (honest) or a fit-to-noise win (dishonest)
depends on a smoothness probe the plan does not specify. Stop 4 as written is a press
release for a failure, not a trigger.

**What would close it:**
- *In spec:* a real license, frozen in the Q0 deck: (i) TightPNO vs NormalPNO **harmonic
  frequency** delta at R1, not just energy; (ii) the same delta on a per-size spot check at
  R2 (even one pyrene mode family); (iii) a smoothness probe along each promised normal mode
  (energy and force continuity, second-difference noise vs step size) that **is** stop 4.
  If canonical (T) fails at R1, R2–R3 lose “beat” language automatically — not “state the
  limitation and proceed.”
- *As science:* print TightPNO−NormalPNO and DLPNO−canonical frequency deltas at naphthalene
  **and** one C₁₆ point. If those deltas ≳ the P2 beat margin, DLPNO is not the thing that
  beats line B.

---

### 3. “VPT2 or MD-ACF” never names Fermi resonances; at PAH sizes that is the method

**Where:** Distilled §3 “Anharmonic machinery”; Overarching method skeleton step 2;
Frozen_Ladder §3 families (CH-stretch is a reporting unit that “must appear”);
probes/README (R0 stops at harmonic).

**What:** The freeze says “VPT2 or MD-ACF spectra; declared per rung” and never writes Fermi,
GVPT2, Darling–Dennison, or polyad. That is not a method choice. It is a deferred decision
disguised as one. For PAHs, VPT2 without taking resonances out of the perturbative treatment
is the known failure mode in the CH-stretch family the ladder promises. MD-ACF is the
affordable remaining path, and the literature that uses it says it misses Fermi.

**Evidence (verified this pass):**
- Mulas 2018: PAH modes cluster; near-degeneracies unavoidable especially CH stretch and CH
  bends. “VPT2 … breaks down in the case of near degeneracy.” “Resonances must therefore be
  taken out of the perturbation treatment … GVPT2.” Fermi if |V/ΔE| ≥ r₃; Darling–Dennison if
  ≥ r₄. Pyrene CH polyads grow to ~36 000 states at r = 0.05. CH stretch “very sensitive …
  more difficult to get to converge.” QFF cost 36N² Hessians; coronene used **6-31G\***, not
  TZ2P. Main limit = DFT QFF accuracy. Scaled harmonic “not much less accurate” for
  fundamentals but misses combination/overtone/Fermi-active bands. That last sentence is the
  honest scope of anharmonicity on these molecules — and it is **not** a few-cm⁻¹ move of the
  fundamentals the P2 table will score.
- Tang 2025: GVPT2 includes resonances “important for 3.3 µm”; largest GVPT2 DFT molecule
  cited is protonated C₇₀. Harmonic + 0.9671 **already fits** pyrene-cation IRMPD band
  profiles. MD is mandatory for fully superhydrogenated PHP. The paper the plan cites as a
  warning is a warning that anharmonicity often does not pay on the scored fundamentals.
- Mai 2025 conclusions: MLMD “does not account for quantum-specific phenomena such as Fermi
  resonance”; VPT2 typically N_C < 25. Mai applies scale factor 0.9578 (Bauschlicher &
  Langhoff 1997). This plan **forbids** a scale factor on anharmonic output, so a P2 “beat
  teacher” vs Mai is not apples-to-apples unless that is labelled.
- Käser et al., arXiv:2103.05491: the ML-PES + VPT2 precedent the bibliography owns uses
  **Gaussian GVPT2** (default resonance thresholds). Fermi 1:2 in formic acid (OH bend vs
  torsion overtone) is why they reassign the experimental band. MD “unable to capture the
  full anharmonic behaviour … especially for high-frequency modes.” Largest molecule in that
  paper: 9 atoms (acetamide). Coronene is 36 atoms / 102 modes. The precedent does not scale
  to R3 as a one-person GVPT2 implementation.
- Distilled §3 still has no Fermi/GVPT2 row. Pilot note inventory (Ladder §4) freezes band
  lists, margins, P-gates, matrix tolerance, P3, M04 recipe — **not** resonance handling.

**Why it matters:** One person at ~10 h/week will not implement AnharmoniCaOs-class GVPT2
with 36 000-state CH polyads. If the rung declares VPT2, the CH-stretch family — which
Ladder §4.1 says must appear if lab data exist — is garbage, and P2 can still “win” on
CH-oop. If the rung declares MD-ACF, Mai already did that at DFT cost to C₂₁₆ and told you
Fermi is missing. Either way the Distilled §9.4 sentence is undefended in the 3.3 µm family.

**What would close it:**
- *In spec:* the pilot note freezes, **before R2**, one of: (a) GVPT2 with named r₃/r₄ and a
  polyad cap, and CH-stretch is dropped from promised families if the cap is exceeded; (b)
  MD-ACF only, CH-stretch labelled classical, Fermi not claimed; (c) CH-stretch never scored.
  “Declared per rung” without those words is not a freeze.
- *As science:* a pyrene GVPT2-vs-raw-VPT2-vs-MD-ACF table on the CH-stretch polyad, even at
  DFT, before any CC surface is fitted. If raw VPT2 moves the band by more than the beat
  margin relative to GVPT2, raw VPT2 is forbidden on that family.

---

### 4. R2–R3 are promised accuracy rungs whose point factory is a B3 object that does not exist

**Where:** Compute_Budget §1–§3; Frozen_Ladder §2 “Promised: R0–R3 scored”; Distilled §9.4;
grok_chat_4; probes/README.

**What:** The plan never states a minimum point count for a usable surface. That omission is
itself a finding (brief attack 4). R2–R3 require a DLPNO factory. B3 has **no number** and
starts only after access + timed probe + dated cap. B2 is 168 h laptop per rung pilot. If the
factory does not fit B2, the promised set silently depends on an allocation that does not
exist. The first timed probe that should force the stop is not named as a stop.

**Evidence (verified this pass):**
- grok_chat_4 assertion (labelled assertion, not budget): one coronene DLPNO-CCSD(T)/TZ point
  “tientallen minuten tot een paar uur”; 10⁴ points “duizenden node-uren.”
- Käser 2021 sampling formula, verified: (3N−6)·600 + 1 geometries for a from-scratch PES.
  Coronene: N = 36, 3N−6 = 102 → **61 201** points — *above* the chat’s 10⁴. Transfer learning
  used ~5% CC points for 9-atom molecules (262–632 CC geometries). The paper’s own sentence:
  “for the largest molecules and at the highest levels of theory … a sufficient number of
  energies and forces (estimated to be around 10⁴ or larger) at … CCSD(T) is usually not
  feasible.” Those “largest molecules” are acetamide, not pyrene.
- Tang 2025: 18k–30k **DFT** points for PaiNN per cation; PHP 55 ps MLMD ~1 h GPU vs 305 days
  DFT-MD. DFT points are not DLPNO points.
- Mai 2025: 17 175 B3LYP/4-31G configurations for a **transferable** NN. This plan forbids
  motif-transfer (Ladder §6); every molecule gets its own surface.
- Kumar 2020 timings (**not** a C₁₆H₁₀/TZ laptop bracket — state that clearly): 4 CPU cores,
  **512 GB** nodes. Medium-molecule UHF-DLPNO-CCSD(T)-F12 wall times (Table 2): Vitamin E
  (80 atoms) 60 724 s ≈ 17 h; Cochineal (55 atoms) 130 252 s ≈ 36 h; CL20 (36 atoms) 234 992 s
  ≈ 65 h. Bicarbonate F12-only ~26 h at >500 atoms, NormalPNO, no (T). n-alkane C₁₆₀H₃₂₂ is
  the locality **best case** (measured exponent ~1.2). **These numbers do not bracket a
  pyrene DLPNO-CCSD(T)/TZ point on a student workstation.** They do show that even
  insulator-like DLPNO-(T) on 4 cores is hours, not seconds, once F12/TightPNO/(T) are on.
  A delocalized PAH at TightPNO (finding 2) is worse, not better.
- Plan-02 provenance (Compute_Budget §4): coronene **B3LYP** frequency job 176 min. That is
  the Hessian, not the factory.
- B2 = 168 h. Even a charitable 20 min/point × 1 000 points = 333 h > B2, and 1 000 is
  below every published count cited above. TightPNO × C₁₆ × TZ on a laptop is not a number
  anyone has printed. Until the probe exists, promising R2 as an accuracy rung is promising
  B3.

**Why it matters:** Accuracy rungs that do not run are fail-closed (Ladder). Distilled §9.4
is written as if they will. The calendar failure mode is: R0–R1 consume the 200 h
infrastructure bucket (finding 8), UvA allocation never appears, R2 is reported “did not
run: B3 precondition” in month fourteen, and Module 08 still has a claim ladder that
required R2–R3.

**What would close it:**
- *In spec:* freeze N_min (even a small-N QFF-like 36N² vs an MD-sample 10³–10⁴) in the Q0
  deck. The **first** timed DLPNO probe is: one pyrene (or naphthalene, if R2 is too dear)
  DLPNO-CCSD(T) energy+gradient at the frozen basis/thresholds, on the laptop, printed by
  `probes/`. Stop rule, not a hope: if `wall_clock × N_min > 168 h`, R2–R3 are **not
  promised**. They become bonus/B3, same status as R4–R5 today.
- *As science:* that probe. No literature timing substitutes for it. Kumar’s 512 GB / 4-core
  enzyme times are a warning, not a quote for the defence.

---

### 5. R6 “reached” is either unaffordable or unfalsifiable; Distilled still sells it as the first beyond-scaled-harmonic spectrum there

**Where:** Frozen_Ladder §2 R6; Distilled §9.5; Overarching Size and compute; Compute_Budget
§3.3 (reach rungs B3-only, blocked); Frozen_Lines debt 6.

**What:** C₃₈₄H₄₈-class: 432 atoms if that formula, 3N−6 = 1290 modes. No lab. No CC check.
P5 error budget is extrapolated from R0–R3 via an M04 uncertainty layer. Nothing at R6 can
contradict it. PAHdb already did the cheap Hessian at 4-31G above 200 C; the plan’s “first
beyond-scaled-harmonic spectrum there” is anharmonic colouring of an uncheckable object, and
the anharmonic colouring is the factory from finding 4, blocked on B3.

**Evidence (verified this pass):**
- Frozen_Lines §1 / Goal: whether C₃₈₄H₄₈ *itself* is in v4.00 is unpaid (debt 6). R6 species
  is “chosen from what the atlas actually contains.” Distilled §9.5 still says “the pipeline
  reaches C₃₈₄H₄₈-class … the first beyond-scaled-harmonic spectrum there.”
- Compute_Budget §3.3: R4–R6 are B3-only and blocked on access+probe+cap. Promised R6 is a
  promised cluster job without a cluster.
- Plan-02 Hessian scaling on file: benzene 3.3 min, naphthalene 12.7 min, coronene frequency
  176 min (B3LYP/6-31G*). No 432-atom timing is on file. PAHdb’s existence of 4-31G Hessians
  at that size is evidence that **NASA’s** production path did it, not that **this** 10 h/week
  student with no allocation will. I am **not** inventing a node-hour cost for a 432-atom
  B3LYP/4-31G Hessian; the honest statement is: unaffordable-until-probed, and the probe is
  forbidden until B3 exists.
- Falsifiability: P5 “stated error budget” with empirical component = M04 layer. M04 is
  trained on small-molecule lab residuals (Distilled §4 exception). Extrapolating that layer
  across two orders of magnitude in N_C, with no lab and no CC, is a number generator. A
  theory-vs-theory table vs line A cannot falsify the budget; line A **is** the scaled
  harmonic the budget is supposed to improve on.

**Why it matters:** Module 08 can print a spectrum, an error bar, and Distilled §9.5, and no
reviewer can prove the error bar wrong. That is not reach. That is a graphics pipeline.
Pass A already forced the C₃₈₄H₄₈-class hedge and debt 6; Pass B finds the remaining
scientific content of R6 is still a promise to generate an unfalsifiable plot.

**What would close it:**
- *In spec:* remove R6 from the promised set. Bonus-only, same as R4/R5. Delete Distilled
  §9.5 from the claim ladder, or rewrite it to “if B3 exists and a species in the atlas
  Hessians, a labelled theory-vs-theory spectrum is shown; no error bar that cannot be
  wrong.”
- *As science:* name one measurement at R6 that could make the budget fail. If none exists,
  do not print a budget. A Hessian-only timed probe on the smallest species actually in the
  101–386 C bin, after B3 exists, is the affordability horn — it does not close
  falsifiability.

---

## Non-blocking findings

### 6. Intensities were demoted in the freeze and are still in the mouth of the claim

**Where:** Overarching prime directive vs “What is scored”; Distilled §1 opening sentence;
Distilled §3 Intensities; Distilled P2.

**What:** Pass A patched the scoring rule: positions scored; intensities reported; scored only
if the pilot note names a **gas-phase** intensity scoreboard; matrix intensities never score;
pairing frozen, never “strongest band in window.” That is the right demotion. It is not
finished. The prime directive still reads “demonstrably more accurate than the best
prediction currently available anywhere for that molecule” with no positions-only qualifier.
Distilled §1 still opens with “band positions (scored) and intensities (reported; scored
only…)” inside the single claim sentence. Line A’s tables include intensities; P2 does not
score them.

**Evidence (verified this pass):** Mulas 2018: Ne matrices lack absolute intensity
calibration; used 570 K gas; pyrene CH stretch ~40% low; coronene some bands factor ~3;
intensities limited by the QFF. Distilled intensities = “dipole derivatives at the declared
level” — one line, no gate, no tolerance, no column.

**Why it matters:** Module 08 can ship a position win and read the prime directive aloud.
Pairing is frozen, so the plan-02 strongest-in-window bug is closed **if** the pilot note
exists before any pipeline-vs-lab number (Ladder §4). Intensities are not scoreable on
matrix; they are barely scoreable on Mulas’s own gas comparison. Leave them out of every
sentence that uses the word “beat.”

**What would close it:** Prime directive and Distilled §1 claim sentence: positions only.
Intensities in a methods paragraph, not the criterion. No intensity P-gate unless a gas
intensity scoreboard is actually named and calibrated.

### 7. Neutral-only is now stated, and that makes finding 1 worse rather than better

**Where:** Frozen_Ladder §2 Charge; R2 lab cell “IRMPD (Tang 2025 class)”; Overarching JWST
sentence.

**What:** Pass A closed the silent charge hole: all rungs neutral unless the pilot note names
a charge. JWST populations are ~half cations (stated as motivation, not a promise). The
strongest modern R2 gas data are cationic IRMPD (Tang). Neutral-only is a legal scope
choice. Combined with finding 1, it means R2 “beat” cannot use the dataset that could have
resolved it.

**Evidence:** Tang 2025, verified this pass (cations, 600–1800 cm⁻¹, IRMPD). Ladder charge
rule, verified in freeze.

**Why it matters:** Scope is honest; the promised R2 accuracy claim is then almost entirely
Ar-matrix neutrals. Do not cite Tang as an R2 scoreboard for a neutral pipeline. A cation
rung, if ever wanted, is a new promised molecule with its own license (open-shell DLPNO is
Kumar 2020’s actual subject — still energies, still 512 GB).

**What would close it:** Either (a) keep neutrals and drop Tang from the R2 lab cell except as
literature context, or (b) add an explicit cation bonus rung that is not in the promised set.

### 8. 840 h still has to buy infrastructure that was the plan-01 failure mode

**Where:** Compute_Budget §2 (160+200+240+160+80 = 840); Capstone_Mapping §6; Distilled
modules 02–09; probes/README (no probes exist).

**What:** T0 is not a date. Caps are caps. The promised set is R0–R3 scored + R6 reached +
modules 02–09. The 200 h infrastructure bucket is Hessians, DLPNO factories, scoreboard
probes — the exact failure mode the budget file warns about (“if pipeline infrastructure
exceeds 200 h, the plan is drifting toward plan 01”). Pass A recorded overlapping module
assignment as non-blocking; the booking rule stops double-counting hours, not
double-assigning work. At 10 h/week, 840 h is 84 weeks if nothing slips. Factories (finding
4) and GVPT2 (finding 3) do not live in the 240 h thesis bucket as currently drawn.

**Evidence:** arithmetic on the B1 table, verified. No timed human-hour log exists. This is
calendar structure, not a runtime prediction.

**Why it matters:** A no-green-light on R2–R3+R6 is also a B1 finding: do not spend the 200 h
building a factory for rungs that should not be promised.

**What would close it:** cut the promised set (findings 1, 4, 5). Re-draw B1 so infrastructure
cannot eat the thesis. Still not a date; still a cap.

### 9. Tier-2 “pre-registered bonus” has no scoreboard to pre-register against

**Where:** Overarching Temperature and emission, tier 2; Frozen_Lines / bib debt 4 (item 20
Joblin-era T-dependence — NOT FETCHED).

**What:** Tier 2 is “measured bonus, pre-registered before it is run.” The Joblin-era
temperature-dependence lab references are an admitted unpaid debt. You cannot pre-register a
comparison to a bibliography row that is empty.

**Why it matters:** Harmless if tier 2 stays unrun. Not harmless if Module 08 shows MD band
shifts “vs experiment” against a paper fetched after the plot exists.

**What would close it:** pin item 20 before any tier-2 protocol sentence, or delete
“pre-registered” until that day.

### 10. M04 reading 1 without mentor pre-approval: the fallback may be non-executable mid-module

**Where:** Capstone_Mapping §3 M04, §5.1, §5.3; Distilled §4 M04 exception.

**What:** User adopted reading 1 (derived pair table + DOI + provenance = distinct). Mentor
pre-approval is explicitly not required in advance. Fallback if a grader applies the
non-reuse rule: “independent public vibrational benchmark found and verified at that moment —
none is named here from recall.” Finding a second public vibrational benchmark **after** M03
has been spent, mid-M04, is not a plan. It is a hope.

**Why it matters:** Distinctness is the M04 landmine. Reading 1 may be fine. If it is not, the
clock does not contain a second M03.

**What would close it:** name the fallback dataset **now** (even as a URL + license + why it
is not PAHdb), or accept that a grader “no” on reading 1 fails M04 closed and Module 08 uses
only line A / line B published tables as opponents, no in-house calibrated harmonic.

### 11. Pass A leftovers that are scientifically load-bearing, not banner nits

**Where:** Overarching prime directive (still concatenates “more accurate” without
positions-only — finding 6); Distilled §9.5 (finding 5); bib item 15 still **record** after
this pass pinned the identifier (debt 5 is now half-paid in this review, not in the bib);
probes/README still: R0 geometry→Hessian→harmonic timed, nothing further.

**What:** Pass A’s 19 patches made the freeze internally consistent enough to attack. The
remaining contradictions are the ones this pass is for: a claim ladder that still requires
R2–R3 beat and R6 reach; a method skeleton that still says “VPT2 or MD-based” with no
resonance word; a license that is allowed to downgrade and proceed. Those are not banners.

**Why it matters:** A later author can quote the patched Goal question split and still defend
Distilled §9 steps 4–5. Pass B is the document that says those steps are not earned.

**What would close it:** edit Distilled §9 and Ladder “Promised:” to match findings 1–5. Pin
Sylvetsky as arXiv:2001.08641 / JCTC 16, 3641 (2020) in bib item 15 on the next freeze pass.
Do not treat this review as paying debt 5 for scored modules — verify-on-use still applies.

---

## Attack-by-attack disposition (brief order)

| # | Attack | Lands? | Disposition |
|---|---|---|---|
| 1 | Matrix scoreboard cannot resolve claimed improvement | **Yes, blocking** | Finding 1. Kills R2–R3 *criterion*, not the pipeline. R0–R1 gas remain. |
| 2 | DLPNO curvatures / R1 license vs coronene π | **Yes, blocking** | Finding 2. Sylvetsky is energies + TightPNO on porphyrins; not a curvature license. |
| 3 | VPT2 without Fermi/GVPT2 | **Yes, blocking** | Finding 3. Strongest freeze hole. MD-ACF is the only one-person path and misses Fermi. |
| 4 | Point-factory arithmetic | **Yes, blocking** | Finding 4. No N_min in the plan. Published DLPNO walls do not bracket C₁₆/TZ on a laptop; they make B2 implausible. |
| 5 | Intensities promised then demoted | **Partially** | Finding 6, non-blocking. Scoring rule is patched; criterion sentences still talk like both quantities. |
| 6 | R6 unaffordable or unfalsifiable | **Yes, blocking** | Finding 5. Both horns. Drop from promised set. |

**Also-worth (brief):** charge → finding 7; 840 h → finding 8; tier-2 → finding 9; M04 reading
1 → finding 10; Pass A leftovers → finding 11.

---

## What would settle “is plan 04 a mistake?”

Plan 04 as a **per-molecule laptop pipeline that scores R0–R1 against NIST gas and refuses
everything else** is not a mistake. Plan 04 as **R0–R3 beat + R6 reached in Module 08** is.

Measurements that settle it, in order, all fail-closed if they do not print:

1. **M03 matrix-vs-gas per-band table** for every promised R2–R3 uid. If |matrix−gas| ≳ beat
   margin, R2–R3 P2 is forbidden (finding 1).
2. **R1 canonical-vs-DLPNO and TightPNO-vs-NormalPNO frequency deltas**, plus a normal-mode
   smoothness probe that *is* stop 4 (finding 2).
3. **One timed C₁₆ (or C₁₀) DLPNO-CCSD(T) energy+gradient** at frozen basis/thresholds on the
   laptop × frozen N_min vs 168 h (finding 4). This is the first probe that must be allowed
   to kill the promised set.
4. **Pilot-note resonance freeze** before any R2 surface: GVPT2 / MD-ACF / drop CH-stretch
   (finding 3).
5. **R6 Hessian timed probe after B3 exists**, or R6 dropped now (finding 5). Dropping now is
   the only option that does not wait on a cluster.

Until (3) and (1) exist, writing Distilled §9.4–§9.5 as a defence outline is the month-fourteen
failure. Do not rehabilitate plans 01–03; they died of scope. This one dies of a criterion
the lab data and the factory cannot support.

---

*Pass B complete. Freeze documents were not edited this pass. Identifier pinned here for
Sylvetsky (arXiv:2001.08641, JCTC 16, 3641, 2020) is verified-this-pass, not a scored-module
cite.*
