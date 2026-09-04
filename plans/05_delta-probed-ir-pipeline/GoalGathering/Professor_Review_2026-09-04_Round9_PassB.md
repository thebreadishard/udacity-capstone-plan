# Professor review — Round 9, Pass B (did the Round-8 closures hold?)

**Date.** 2026-09-04.
**Role.** The hostile domain examiner of Rounds 7 and 8 (local coupled cluster, vibrational
spectroscopy, numerical differentiation, sparse recovery), web access allowed. The question is
the brief's: for each of Round-8 Pass B's eighteen findings, closed / re-worded / open with the
deciding sentence; then attacks A–G on what the closures themselves introduced. Round 6 and
Round 7 items are not re-opened unless a Round-8 closure re-broke them.
**Corpus.** Read in full, in this order: the Round-9 Pass B brief; `Professor_Review_2026-09-04_Round9_PassA.md`
(28 findings; each checked briefly against today's text — see the closure-check paragraph);
plan-05 `README.md`; `Overarching_Goal.md` (glossary first); `Why_05_Supersedes_04.md`;
`Research_Note_2026-09-03_Delta_Probing.md` §§8–9; `Frozen_Lines_to_Beat.md`;
`Frozen_Ladder_and_Tolerances.md`; `Compute_Budget_2026-09-03.md`;
`Distilled_Project_Plan_and_Quality_Checks.md`; `Relevant_Scientific_Papers.md`;
`probes/README.md`; `Capstone_Mapping.md`; `Project_Proposal_2026-09-03.md`;
`Side_Project_2026-09-04_ModeG_Gradients.md`; then `Professor_Review_2026-09-04_Round8_PassB.md`
for the eighteen items of Part 1. Plans 01–04 not reviewed. Round-7 and Round-8 Pass A reviews
not opened. Web sources opened are cited inline with the date; anything recalled is marked
*recalled, not opened*. No file other than this one was written.

(Sections are appended below as the read proceeds; if the file ends without the line
"Pass B complete", the review was cut off and what stands is partial.)

**Round-9 Pass A closure check (its 28 findings).** All twenty-eight are in today's text: 1 (σ_g^assumed
= 2.8·τ·q_s in Ladder §4 item 8, glossary, side project §3, Budget §4.5, probes README 3/5; no
pre-note "σ_g where a gradient runs" survives), 2 (ρ_max = 0.5 floor, the 2M single-mode block
consumed first, n_min(G), the cost record's five extra numbers — Ladder §3, Distilled §3 "Patterns"
and "K", Distilled §8 "at noise" sentence), 3 (σ_coupling = σ_E/(2h²) written out in Ladder §3 and
cited from the glossary, Distilled Q8, probes README 12), 4 (two extrapolation targets, "fits" =
≤ 168 h and ≤ 31.3 GB per object, the Q7(i)/(iv) fallback — Ladder §3, Budget §4.1b, probes README
1b, Distilled Q7/§8), 5 (which r_f — Ladder §3 (c), probes README 15; the Goal's item 1 still lacks
the sentence, non-blocking 11 below), 6–28 (fit coefficients sealed; 72 energies; four Q6 modes and
eight energies in M4/M5; 2.8 = 2√2 derived beside 0.82; ρ\* "computed per rung and mode (only c is
frozen)"; 32 ordered rows; "four parts" everywhere; seven pilot-note inputs in Proposal §7; K_cap(G)
"noise-injected"; the Budget's (T) sentence; "snippet grade" in Proposal §5.2 and §11; "u_band" in
Mapping §2/M03/M08 and Proposal §12; Q6 grid not at R0, R1 fallback in cc-pVDZ, M4 in the R2 deck
basis; "a single test at q_s = 1.0"; σ's rung index; S_class with equal counts; K_prior < K_struct;
28 GB explained; supersede rule dropped and probe numbering aligned; "seven decisions"; note §9
extended; glossary terms; Frozen_Lines criterion and §7 trailer; proposal header, §5.3, §11 order).
The patches held. Three of them (the rung-dependent ρ\*, the degree-4 estimator as the single σ,
and the u_band temperature term) are attacked below on what they introduced.

## Literature and software facts opened this pass (how; date 2026-09-04)

- **NIST WebBook, benzene (CAS 71-43-2), IR spectra list** (webbook.nist.gov, `ID=C71432 … Mask=80`):
  a Coblentz Society **gas** spectrum ("DOW KBr FOREPRISM-GRATING", resolution 2 cm⁻¹, "GAS
  (70 mmHg, N2 ADDED, TOTAL PRESSURE 600 mmHg)"); a NIST Mass Spectrometry Data Center gas entry;
  and **twenty NIST Quantitative IR gas-phase spectra** (Chu, Guenther, Rhoderick, Lafferty; Bruker
  IFS66V; resolutions 0.125–1.93 cm⁻¹, several apodizations). Room-temperature cell spectra exist
  for R0.
- **NIST WebBook, naphthalene (CAS 91-20-3), IR spectra list** (`ID=C91203 … Mask=80`): three
  entries — a Coblentz solution spectrum; a Coblentz **gas** spectrum "VAPOR (1.0 MICROLITER AT
  245 C)", Nicolet FTIR, **4 cm⁻¹, digitized from hard copy**; and a NIST Mass Spectrometry Data
  Center gas entry (the same owner line as the R2 GC-IRD entries Round 8 verified). **No
  room-temperature gas-phase spectrum of naphthalene is listed.**
- **PySCF `pyscf/grad/`** (github.com/pyscf/pyscf/tree/master/pyscf/grad, directory listing):
  contains `ccsd_t.py` and `uccsd_t.py` — canonical CCSD(T) analytic nuclear gradients exist in the
  candidate code family, so the feasibility probe's "72 canonical gradients if the chosen code has
  them" branch is live.
- **Pirali, Vervloet, Mulas, Malloci, Joblin, PCCP 11, 3443 (2009), DOI 10.1039/b814037e** —
  Crossref record: "High-resolution infrared absorption spectroscopy of thermally excited
  naphthalene. Measurements and calculations of anharmonic parameters and vibrational
  interactions." Title and venue verified; its numbers not opened.
- **Joblin, Boissel, Léger, d'Hendecourt, Défourneau, A&A 299, 835 (1995)**, "Infrared spectroscopy
  of gas-phase PAH molecules. II. Role of the temperature" — **search-snippet grade** (title and
  reference confirmed by search; one snippet quotes a C–C stretch shift of about −0.020 cm⁻¹ K⁻¹;
  the paper itself was not opened).
- arXiv:2102.06582 (Chakraborty, Mulas, Rapacioli, Joblin, thermally excited pyrene): abstract
  read; qualitative only, no shift rates in the abstract.

*Recalled, not opened:* B3LYP-vs-CCSD(T) equilibrium C–C bond-length differences in benzene of
0.001–0.003 Å; an aromatic C–C stretch force constant ≈ 0.42 E_h/bohr²; cc-pVTZ function counts
(C 30, H 14); the non-uniqueness of Boys/Pipek–Mezey π localisation in D₆h benzene; GC-FTIR
lightpipe temperatures ≈ 200–280 °C; PAH hot-band red-shifts of order 0.01–0.03 cm⁻¹ K⁻¹; the
χ²-distribution quantiles used in A (standard tables). Verify-on-use applies to all of them.

---

**Verdict: conditional — in two scopes.**

- **R0–R1 (and the pre-pilot-note programme): green light once blocking findings 1, 2, 3 and 6
  are written in.** All four are in-spec; none needs a measurement first. They are: the Δ₁·p term
  in mode-E responses (which the noise-aware stopping rule as written does not remove); the
  frozen-space occupied-orbital mapping (re-localise-and-assign is the wrong object on a D₆h
  molecule); the temperature term of u_band, which reaches R1 (naphthalene's only NIST gas spectra
  are hot vapour) and has no floor; and the σ estimator's degrees of freedom.
- **R2–R3: green light under the same four plus finding 5** (Q8(c) at a common ρ, so the size
  sentence compares like with like) — the two Round-8 blocks on R2–R3 (fragment licence,
  decidability) are closed in spec.
- **The promised set beyond R3 (R4 checks, fragment-probed R6): conditional on finding 4** (in
  spec: the admissible fragment radii at coronene are discrete and the fail rule at (b) refuses a
  licence that (b′) could earn; part (c) at R6 must pass the classification rule) **and on B3**,
  which the plan already says. No further re-wording is needed beyond 4; whether the licence can
  be earned is then a measurement, as it should be.

---

## Part 1 — Round-8 closures

1. **Q6 estimator — closed.** Ladder §3: "σ_E is the RMS residual of ΔE(q) about a least-squares
   polynomial of degree 4, and σ_g the RMS residual of g(q) about a polynomial of degree 3";
   identical in Distilled Q6 and probes README 5; the totally symmetric mode is in all three; the
   noise lines are evaluated per grid step from the one σ. (What "RMS" divides by, and what nine
   points buy, is blocking 6 — new, not a re-wording.)
2. **Noise-aware stopping rule — closed.** Ladder §3: "K is the smallest n at which ρ(n) ≤ ρ\* with
   ρ\* = c·ρ_noise, c ≥ 1 the pilot-note constant of item 8 … from the noise-injected dry run …
   never from the noiseless one"; the noise-injection column exists in Budget §4.1 / probes README
   1; the two Round-9 guards are in. The adopted RMS_resp is the rung's own held-out responses
   rather than Round 8's rescaled dry-run responses — a legitimate choice, and the one attack B
   bites on (blocking 1, 5).
3. **Absolute η₈ — closed.** Ladder §3 Q8(a): "the disagreement |recovered − direct| is normalised
   by the coupling scale of the pair's distance class … S_class = √(Σ_class direct²/n_class) …
   A pair whose direct coupling is below 3σ_coupling is reported 'at noise' and enters the fit with
   its uncertainty, never as a pass/fail"; the same object in Distilled Q7(iv)/Q8, the learned-prior
   licence and fragment part (c).
4. **Fragment licence — closed as written.** Ladder §3 (b): "at the smallest fragment radius r_f
   that passes … if no r_f smaller than the molecule passes, that is printed as the result and part
   (b) has failed"; (b′) "promised conditional on B3 classification"; (c) "fragments of radius r_f
   and r_f + one ring carved from the rung's own DFT geometry, agreeing within the absolute η₈".
   Every sentence Round 8 asked for is present. Whether (b) can pass at coronene, and what (c) costs
   at R6, is blocking 4 — a consequence of the closure, not a gap in it.
5. **Frozen-space object — closed.** Ladder §3: "the localized occupied orbitals are mapped to the
   stored ones by maximal overlap and the assignment permutation is printed; the stored
   virtual-space vectors are projected onto the new geometry's virtual space and
   Löwdin-orthonormalised … For mode G the projection is inside the differentiated graph"; M1
   along "one totally symmetric, one degenerate and one non-symmetric benzene mode"; M2's FD
   reference "of the re-projected frozen-space energy" and the third number. Written once, as asked.
   The object's occupied half is attacked in blocking 2.
6. **u_band decidability — closed.** Ladder §2: "decidable if the measured band-centre uncertainty
   u_band … (i) the instrument resolution as stated by the source's documentation (never the JCAMP
   point spacing), (ii) the centroid precision … (iii) a temperature term … is smaller than the
   family's beat margin. M03 prints u_band and the verdict … before the pilot note"; the R2 C–C
   families "expected inconclusive by construction"; Proposal §13.3 "load-bearing". Closed for R2;
   the same term reaches R1 (blocking 3).
7. **Mode E on every rung — closed.** Goal: "Mode E runs on every rung R1–R3 that runs; on every
   rung where the side project's milestone licenses it, mode G runs in addition and the rung carries
   two cost records"; Ladder §1 mode-E form "always earnable"; Q8(c) "per mode over the rungs that
   mode ran". No survivor of "elsewhere mode E runs".
8. **Anchor basis and feasibility probe — closed.** Ladder §3: "cc-pVTZ for R0 and R1 … The
   canonical feasibility probe prints one canonical CCSD(T) energy of benzene at cc-pVTZ on the B2
   laptop and extrapolates … to two counts … 'Fits' means extrapolated wall-clock ≤ the 168 h
   checkpoint and peak memory ≤ 31.3 GB, per object"; fallback written; Distilled §8 sentence
   exists. (Attack G: non-blocking 9.)
9. **M5 both checks — re-worded.** Side project M5: "one gradient at coronene in the R3 deck basis
   … AD-vs-FD along the four Q6 modes (eight re-projected frozen-space energies) and σ_g at the R3
   size class". The correctness check is now real. But σ_g is, by the plan's own estimator, "the
   RMS residual of g(q) about a polynomial of degree 3" over **nine points** per mode — it needs
   nine gradients per Q6 mode (36 at coronene), not one; "one gradient … and σ_g" cannot both be
   true. M4 has the same sentence. A closed version: "nine gradients per Q6 mode (36), the σ_g
   estimator of Ladder §3 pooled over all 3N components (non-blocking 7), classified B3 by the rule".
10. **Closure depth one — closed.** Goal, Ladder §3, item 7 and Distilled §3 all say "closure depth
    one … partners' own diagonal anharmonicity from their 1-D cut only; bounded by the polyad cap;
    size and Hessian count printed".
11. **Learned-prior residuals — closed, not merely acknowledged.** (a) Ladder §3: "the structural
    recovery's own Q8(a/b) on direct couplings must have passed at that rung" — the reference is
    now locality-checked; (b) item 5 "reported on the PAH held-out tensors as well", Distilled §6
    says why (off-distribution corpus), Mapping M05 states QM9's size range with its grade; (c) "the
    certificate … carries the rung's direct-coupling agreement as its prior-independent number".
    The one thing not done — gating the PAH number — is a stated choice with a stated reason
    ("the licence is earned on the probed PAHs themselves"), which I accept.
12. **M05/M06 rubric fit — closed.** Mapping M06 has the display and qualitative-criteria paragraph
    ("displacement arrows on the molecular frame … symmetry consistency, locality, non-redundancy;
    failure cases shown") and "the PAH dry-run tensors … are excluded from M06's training data";
    §4 records it. The reading-2 fallback is left un-named "none is named from recall" — consistent
    with the plan's rule, and decision 7 removed the exposure it insured against.
13. **Inheritance walk — closed.** Goal, "The walk of the other inherited rules": each rule
    classified goal / measurement; neutral species re-justified with three reasons and made a
    per-rung choice; the B3LYP-class reason is in Distilled §3.
14. **Proposal staleness — closed** after the Round-9 Pass A sweep: §5.1 "on the student's
    laptop's CPU"; §7 "seven inputs"; §11 risk 7 "outgrow the pipeline's infrastructure bucket";
    §1 "local coupled-cluster anchor, checked against canonical coupled cluster where affordable".
15. **Engine facts — closed.** Items 48–49 "fetched … by the Round-8 Pass B reviewer and by the
    author"; Budget §3 row now says "whether (T) is differentiated end-to-end is side-project item
    (a)"; Distilled §3, Why_05 row 25, side project §1.1 agree.
16. **Direct probe — closed.** Ladder §3 Q8(a): "family-projected coupling ∂²ΔE/∂u_A∂u_B … by
    four-point mixed differences of ΔE at Cartesian step h … four energies per (pair, family); the
    full 3×3 block only for the deck's near pair"; identical in Distilled Q8, Budget §4.11, probes
    README 12.
17. **M1 displaced columns — closed.** M1 "prints, along one totally symmetric, one degenerate and
    one non-symmetric benzene mode, the assignment permutation and E(displaced, frozen) −
    E(displaced, fresh) per point, without a verdict" — Ladder §3, Budget §4.2, probes README 2,
    side project M1.
18. **Alarm quietness — closed.** Side project §4: "makes that bucket large early and the alarm
    below correspondingly quiet at first — said here so it is not a surprise."

**Tally: 17 closed, 1 re-worded (item 9), 0 open.**

---

## Blocking findings

### 1. Mode-E responses carry the first-order term Δ₁·p, which is 3–14× the Δ₂ signal; RMS_resp, ρ_noise and the stopping rule are defined on the raw response, so the closure of Round-8 finding 2 measures Δ₁, not Δ₂
**Where:** Distilled §3 "Responses" ("mode E: the energy difference Δ(E) at the pattern geometry
minus at equilibrium"); Distilled §3 "Hold-out and residual ρ; the noise floor" ("ρ_noise =
σ(mode)/RMS_resp(rung) … RMS_resp the rung's own held-out response RMS"); Ladder §3 "K is a
measurement" ("RMS_resp the RMS of the rung's own held-out responses"); Goal glossary
("response = the CC−DFT energy … difference at a pattern"); Distilled §3 "Patterns" (the 2M block
is ±q_s; the multi-atom patterns are not said to come in ± pairs).
**What — the arithmetic.** ΔE(p) − ΔE(0) = Δ₁·p + ½ pᵀΔ₂ p + (1/6)Δ₃ppp + …, where Δ₁ =
∇(E_CC − E_DFT) at the **DFT** equilibrium is not zero: the two minima differ. Recalled scale:
B3LYP and CCSD(T) aromatic C–C bond lengths differ by 0.001–0.003 Å; take 0.002 Å = 0.0038 bohr
with k ≈ 0.42 E_h/bohr² → |Δ₁| ≈ 1.6×10⁻³ E_h/bohr per bond. The plan's q_s = 1 along a
1,500 cm⁻¹ C–C stretch is a bond-length amplitude of ≈ 0.085 bohr, so the linear term per stretched
bond is ≈ 1.6×10⁻³ × 0.085 = **1.4×10⁻⁴ E_h = 140 µE_h**. The quadratic signal for a 5 cm⁻¹
correction (Δk = 2(δω/ω)k = 2.8×10⁻³ E_h/bohr²) is ½·Δk·δ² = **10 µE_h** — the plan's own "≈ 11 µE_h
at q_s = 1" from Round 8. Ratio ≈ 14 per bond; in a hashed multi-atom pattern the bond changes
carry mixed signs, so the linear term partly cancels, but its RMS still exceeds the quadratic
signal by 3–10× for any pattern set that is not symmetry-adapted (and the deck's patterns are
hashed, not symmetry-adapted). At δr = 0.001 Å the ratio is still ≈ 7.
**Consequences.** Either (a) the recovery model is Δ₂-only, as every document says ("recover Δ₂"),
in which case the held-out residual contains the unfit Δ₁·p, ρ floors near 1, c·ρ_noise is
irrelevant, and every rung reads "not recovered at cap" or "at noise" — Round-8 finding 2's
default-by-construction outcome in a new guise; or (b) the solver quietly fits a linear term (not
written anywhere), in which case ρ and ρ_noise are computed against an RMS_resp inflated 3–14× by a
term that carries no Δ₂ information: ρ_noise is 3–14× too small, c·ρ_noise sits far below ρ_max,
and the rule stops when Δ₁ is fitted — K reads small while Δ₂ is unresolved. Mode G does not have
the problem (∇ΔE(p) − ∇ΔE(0) removes Δ₁ exactly), which is one more reason the mode-E rule needs
to say what it does. Note also that Round 7's noise line was derived for E₊ − 2E₀ + E₋ — already a
symmetric combination — so the Q6 line and the response definition are currently inconsistent.
**Why it matters.** K is the promised cost record; as written it is a measurement of the CC−DFT
force at the DFT geometry.
**What would close it (in spec).** (i) Every pattern p enters the deck as the pair ±p (the 2M
block already does); the mode-E response is the symmetric combination R_s(p) = ½[ΔE(+p) + ΔE(−p)]
− ΔE(0) = ½ pᵀΔ₂ p + O(p⁴) — Δ₁ and Δ₃ cancel exactly; the antisymmetric combination R_a(p) =
½[ΔE(+p) − ΔE(−p)] = Δ₁·p + (1/6)Δ₃ppp is a free by-product (Δ₁ from the 2M block; the diagonal
cubic along single modes, which is the bonus probe, at no extra energies once a second amplitude is
in the block). (ii) K counts energies, so an off-diagonal ± pair counts 2 in K_off — write it in
Ladder §1's record form and Goal glossary. (iii) ρ, RMS_resp and ρ_noise are defined on R_s, with
σ(R_s) = σ_E/√2 stated. (iv) The same sentence in Distilled §3 "Responses" and "Patterns", Goal
glossary "response" and step 2, and the dry run (which has the same term, larger, and will
otherwise report it as a solver failure).

### 2. The frozen-space object's occupied half — "re-localise, then assign by maximal overlap" — is the wrong object on the two D₆h rungs: π localisation is soft, so the mapping mixes rather than switches, and the argmax is not differentiable; M2's kill criterion can fire on a designed-in feature
**Where:** Ladder §3 "Frozen spaces — the object, written once" ("the localized occupied orbitals
are mapped to the stored ones by maximal overlap and the assignment permutation is printed");
Goal glossary "re-projected"; side project §1.2, §2(c), M1/M2 rows, kill criterion ("if M2's
correctness check fails after the AD and the finite-difference reference have both been re-derived
once"), §7 risk 3; probes README 2; Budget §4.2.
**What.** The sentence presupposes a fresh localisation at every displaced geometry followed by a
discrete one-to-one assignment. (i) *Mixing.* Boys or Pipek–Mezey localisation of benzene's three
occupied π orbitals is not unique (recalled: the Kekulé-type sets are degenerate under D₆h, and the
localiser lands on one of them, or on a rotated set, by starting guess); the interior of coronene
is the same case. Along a non-symmetric mode the degeneracy is lifted by an amount ∝ q, so the
landing point moves continuously with q: the displaced π LMO overlaps each stored one by 0.5–0.9,
no permutation is right, the frozen LNO space assigned to it is wrong by a continuously varying
amount, and E_frozen(x) inherits the localiser's path. Along a totally symmetric mode the degeneracy
is exact at every q and the landing is arbitrary point by point — scatter that Q6 reads as noise
and M1's permutation log cannot see (the permutation can read identity throughout while the
orbitals rotated). The "fresh" arm has the same arbitrariness, so E(frozen) − E(fresh) mixes two
arbitrary choices. (ii) *Differentiability.* An argmax (or Hungarian) assignment inside a JAX graph
has zero derivative: AD returns the one-sided branch derivative; a finite-difference stencil that
straddles a switch returns step/(2δq) — for a 5 µE_h step over δq = 0.05 bohr that is 5×10⁻⁵
E_h/bohr, five times M2's 10⁻⁵ tolerance. M1's log catches a switch only between consecutive
logged points at 0.25 spacing; M2's FD stencils are finer and can straddle a switch M1 never
logged. The kill criterion then reads a physics feature as a correctness failure and stops the side
project. The Löwdin step itself is differentiable (S^{-1/2} is analytic while S is nonsingular, and
for |q| ≤ 1 the smallest singular value of the projected-space overlap is 1 − O(q²)); the argmax is
the only non-smooth element, and it is avoidable.
**Why it matters.** Q6's σ_E at R1, M1's verdict-free printout and M2's correctness check all rest
on this object; as written, the object contains an arbitrary component that will be reported as
"frozen-space noise" and may end the side project for the wrong reason.
**What would close it (in spec, both arms).** Replace re-localise-and-assign by **transport by
projection**, exactly as the plan already treats the virtual vectors: C_occ(x) = Löwdin[P_occ(x)
C_occ(0)], where P_occ(x) is the projector onto the displaced geometry's occupied space — no
localiser runs at displaced geometries, no assignment exists, the map is analytic and
differentiable, and "projection inside the graph" holds for both halves. M1 prints, instead of a
permutation, the smallest singular value of the occupied overlap S_oo(x) = C_occ(0)ᵀ S(x) C_occ(x)
and the largest off-diagonal of the pre-Löwdin overlap — continuous diagnostics; and, for the
fresh arm, the localiser's functional value and its overlap with the transported set, so the
landing arbitrariness is visible in the "fresh" column and not attributed to freezing. Write it in
Ladder §3 and the glossary ("re-projected" covers occupied and virtual), and mirror in probes
README 2, Budget §4.2, side project §1.2, §2(c), M1/M2, §7 risk 3. M2's correctness check then
needs no switch caveat; keep the kill criterion.

### 3. u_band's temperature term reaches R1: naphthalene's only NIST gas-phase spectra are hot vapour, so "unconditional on the gas-phase rungs (R0–R1)" is not true of R1's C–C families; and the term's "estimated magnitude" has no floor and no owner
**Where:** Goal prime directive ("unconditional on the gas-phase rungs (R0–R1)"); Ladder §2
"Decidability per family" ("R0–R1 are gas-scored throughout against NIST spectra whose u_band M03
measures the same way; they are unconditional in the sense that no matrix gate applies, and their
C–H and CH-oop families are expected decidable") and the temperature term ("or, until one is
pinned, the labelled uncertainty 'hot-vapour scoreboard, 0 K prediction' with its estimated
magnitude"); Distilled §1; Frozen_Lines "The criterion"; Method debts ("PAH hot-band shift
references … until then the term is a labelled uncertainty").
**What — opened today.** The WebBook lists for **naphthalene** three IR entries: a solution
spectrum; a Coblentz **gas** spectrum "VAPOR (1.0 MICROLITER AT 245 C)", 4 cm⁻¹, "digitized from
hard copy"; and a NIST Mass Spectrometry Data Center gas entry — the owner line of the GC-IRD
entries Round 8 verified for triphenylene. No room-temperature gas spectrum exists there. For
**benzene** the WebBook lists a Coblentz gas spectrum at 2 cm⁻¹ (600 mmHg total pressure, room
temperature by construction) and twenty NIST Quantitative IR gas spectra at 0.125–1.93 cm⁻¹ — R0
is fine and should name which entry it scores.
**Arithmetic.** 245 °C = 518 K. With the C–C stretch shift rate of about −0.020 cm⁻¹ K⁻¹ (Joblin
et al. 1995, snippet grade; the plan's own recalled range is 0.01–0.03), the hot-band shift of a
naphthalene C–C band relative to a 0 K prediction is ≈ −10 cm⁻¹ (−5 at half the slope). That is
u_band's term (iii) for R1's C–C families unless a correction is applied; it exceeds τ ≈ 5 cm⁻¹ by
itself, so **R1's C–C families are inconclusive by construction on the NIST source exactly as R2's
are** — and the plan promises R1 as "unconditional". For benzene at 296 K the lowest mode
(≈ 400 cm⁻¹) carries ≈ 0.3 quanta on average and the shift is of order −0.5 to −1 cm⁻¹ (recalled):
decidable. Second problem: "the labelled uncertainty … with its estimated magnitude" is estimated
by nobody in particular from nothing in particular; as written the author can set it to 1 cm⁻¹ and
make a family decidable.
**Why it matters.** The R0–R1 green light was given for a programme whose R1 scoring is
"unconditional"; for the 6.2/7.7 µm families at R1 it is not, and the plan should say so before the
pilot note, not at P2. This is also where the plan can *gain*: a pinned hot-band correction is the
only thing that makes C–C scoring at R1–R2 decidable on the data that exists.
**What would close it (in spec; one debt made concrete).** (i) Goal and Ladder §2: "R0 unconditional
(room-temperature cell spectra with stated resolution exist — the NIST Quantitative IR series, entry
named in the pilot note); R1 per family under the same u_band rule as R2; on the 245 °C Coblentz
vapour spectrum or the GC-IRD entry R1's C–C families are expected inconclusive by construction
unless a hot-band correction is pinned before the note." (ii) A floor for the unpinned term, written
now: u_T ≥ |χ_max|·T_source, χ_max = 0.03 cm⁻¹ K⁻¹ (recalled; replaced by Joblin 1995's table on
fetch), T_source the source's stated temperature (245 °C for the Coblentz naphthalene entry; the
SRD 35 lightpipe temperature once item 50's PDF is read — until then 250 °C, labelled recalled).
(iii) Better, and honest if done before the note: pin a per-family **correction** χ_F·T_source with
χ_F from Joblin et al. 1995 (A&A 299, 835 — measured naphthalene, pyrene and coronene vs
temperature, recalled) and Pirali et al. 2009 for naphthalene (PCCP 11, 3443; Crossref record
verified today), and carry ±30 % of the correction plus the temperature uncertainty as u_T; if that
brings a C–C family under its margin, it is decidable, and the pilot note says so with the
citation. (iv) M03's probe prints, per spectrum, the source class (cell / GC-IRD / vapour cell),
the stated temperature and resolution, so the scoreboard's provenance is a column, not a footnote.

### 4. At coronene the ring-closed fragment radii for an interior pair are exactly two — one ring, or the whole molecule — so part (b) has one testable radius; the fail rule then refuses a licence that (b′) could earn; and part (c) at R6 is a B3 batch that no document classifies
**Where:** Ladder §3 "The fragment licence" (b), (b′), (c) and "If (b) found no passing radius
smaller than coronene, the licence is not earned and R6 is not fragment-probed"; Goal item 1;
Budget §4.12–13; probes README 13–15.
**What — geometry.** Coronene's 24 carbons lie at 1.42 Å (six, the central ring), 2.84 Å (six) and
≈ 3.68 Å (twelve) from the centre, hydrogens at ≈ 4.7 Å. The plan's fragments are "capped" and
their radius is counted in rings ("r_f + one ring"), so they are ring-closed, H-capped pieces. For
an interior pair (a central-ring bond or a spoke) the ring-closed fragments containing it are the
central ring alone (a capped benzene, r ≈ 1.4 Å) and the central ring with its six neighbours —
coronene itself. There is no intermediate shell. Edge pairs have more candidates (three- to
five-ring pieces), but the licence exists for the interior. So (b)'s "smallest passing radius" for
interior couplings has one candidate smaller than the molecule.
**Two outcomes.** If a capped benzene at coronene's interior geometry reproduces coronene's
interior Δ₂ per family within τ₇ — plausible for C–H and CH-oop, doubtful for the 6.2/7.7 µm C–C
families whose CC−DFT difference grows with conjugation (item 44) — then r_f = one ring and R6's
(c) compares one-ring (12-atom) with two-shell (36-atom) fragments: affordable, and a strong result.
If it does not, the Ladder's rule fires ("not earned; R6 not fragment-probed") although the natural
hypothesis, r_f = two shells, has been tested nowhere: coronene cannot test it; circumcoronene can,
and that is (b′), which the plan already promises conditional on B3. As written, the licence refuses
a method that its own next part could license.
**Cost of (c).** n_pairs ≥ 9 (three per class) × ≈ 5 families × 4 energies × 2 radii = **360
frozen-space local-CC energies** of fragments carved unrelaxed from the flake: at r_f = two shells
the fragments are coronene-size (36 atoms; 888 cc-pVTZ functions, recalled count) and
circumcoronene-size (C₅₄H₁₈, 72 atoms, ≈ 1,872 functions). At the Budget's own assertion for a
coronene-size local-CC point ("tens of minutes to hours") that is 100–700 h — over the 168 h
checkpoint: B3 by the rule, which no document applies to (c). At r_f = one ring the fragments are
12 and 36 atoms and (c) is laptop work.
**Why it matters.** Decision 1 rests on the licence being earnable by measurement. As written it
can be un-earnable for a reason of geometry rather than physics, and its decisive test at R6 has no
budget class.
**What would close it (in spec).** (i) Write the fragment construction once (ring-closed, H-capped,
carved unrelaxed from the rung's DFT geometry, radius counted in ring shells around the pair, basis
= the rung's deck basis). (ii) At (b), distinguish "failed at one shell; two shells untestable at
coronene" from "failed": in the first case the licence is **pending (b′)** — earned only if (b′)
passes at two shells on circumcoronene under B3, not earned otherwise; the Distilled §8 refusal
sentence gains that clause. (iii) Part (c) at R4 and R6 is a probe batch classified by Budget §2's
rule like any other, with its energy count printed (the 360 above, or the deck's); Budget §4.13
and probes README 14–15 say so. (iv) Say which radii (b) actually tests at coronene: one shell for
interior pairs, the ring-closed pieces for edge pairs — so the reader knows in advance that (b) is
one comparison, not a scan.

### 5. Q8(c) compares K_off at two different thresholds, because ρ\* is now rung-dependent; "the same ρ\* rule" is not the same ρ\*
**Where:** Ladder §1 size sentence ("with the structural prior at the same ρ\* rule"); Ladder §3
Q8(c) ("same mode and same prior at both rungs, at the same ρ\* rule"); Distilled Q8 (c) ("same
prior, same c"); Goal cost question.
**What.** ρ\* = c·σ/RMS_resp. Between R1 and R2 both factors change: σ moves from the R1 value to
the R2-size measurement (item 44's growth — the plan's own risk), and RMS_resp changes with the
molecule (more modes contribute per pattern; Δ₂'s size differs). Example: R1 ρ_noise = 0.10,
c = 2 → ρ\* = 0.20; R2 with σ × 1.3 and RMS_resp × 1.5 → ρ_noise = 0.087, ρ\* = 0.17 — R2 must fit
tighter, and K_off(R2) is inflated relative to a common threshold; the reverse case deflates it. A
γ of 1.5 can be met or missed by this alone, and the size sentence — the only one the thesis may
write — then reports the threshold's drift as a property of Δ₂. The cost record's extra columns
(Round-9 Pass A closure 2) make this visible but do not remove it.
**What would close it (in spec; no cost).** ρ(n) is stored for every n at every rung. Define Q8(c)
on K_off read from both curves at a **common threshold** ρ\*_common = max(ρ\*(R_n), ρ\*(R_{n+1}))
— both rungs reached it, since each reached its own ρ\* ≤ ρ\*_common — and print both the record
K_off and the common-threshold K_off. One sentence in Ladder §1, Ladder §3 Q8(c) and Distilled Q8.

### 6. The σ estimator: "RMS residual" must divide by the residual degrees of freedom (4, not 9), and a per-mode σ from four degrees of freedom is a ±50 % number
**Where:** Ladder §3 Q6 bullet ("σ_E is the RMS residual of ΔE(q) about a least-squares polynomial
of degree 4, and σ_g the RMS residual of g(q) about a polynomial of degree 3"); Distilled Q6;
probes README 5; Budget §4.5; the per-mode use of σ in the noise lines and in ρ_noise.
**What — the statistics.** Nine points, five coefficients: SSR/σ² ~ χ²₄. √(SSR/9) underestimates σ
by √(4/9) = 0.67 — a σ reported 1.5× too small, in the direction of passing bad data, and the same
factor in ρ_noise and every stopping decision; only √(SSR/(n − p)) is unbiased. With ν = 4 the
90 % range of σ̂/σ is [√(0.711/4), √(9.49/4)] = **[0.42, 1.54]**: a per-mode verdict near the line
is a coin toss within ±50 %. Pooling the four modes of one arm gives ν = 16 (relative SD ≈ 18 %);
17 points at 0.125 spacing give ν = 12 per mode (136 energies for the probe).
**Outlier / switch.** The leverage of a degree-4 fit on nine equispaced points is ≈ 0.85 at the end
points and ≈ 0.45 at the centre (a property of polynomial leverages; the script can print h_ii): a
step at |q| = 1 is 85 % absorbed into the coefficients — including the sealed quadratic one, i.e. a
bias in Δ₂,ii — and shows 15 % in σ; a step at the centre shows and dominates. A 5 µE_h step
(Madriaga-class) therefore adds ≈ 1 µE_h to σ_E at the edge and ≈ 3 µE_h at the centre; against
the q_s = 1 line (18.6 µE_h at τ = 5 cm⁻¹) both pass, and at q_s = 1 the step's effect on Δ̂₂,ii
(≤ 5 µE_h ≈ 1.1 cm⁻¹) is tolerable — the plan's choice of q_s = 1 is right for this reason too. But
the estimator will not *report* the switch; only a per-point diagnostic does.
**Physics vs noise.** The degree-4 fit captures ΔE through the quartic exactly; the first
unabsorbed term (Δ₅/120)q⁵ leaves an RMS residual of ≈ 0.04 of its amplitude over [−1, 1] (the
P₅ component of q⁵ is 8/63): σ_E measures noise, not physics — and absorbs 5/9 of the noise, which is
the ν correction above. **Mode G:** degree 3 is the derivative of degree 4 — consistent; the two σ's
are comparable through the 2τ convention only if g(q) is the derivative of ΔE with respect to the
same dimensionless q (state the conversion from Cartesian E_h/bohr: g = ∇ΔE·∂x/∂q); and there is
no reason to use one component when 3N are computed — non-blocking 7.
**What would close it (in spec).** (i) "σ_E = √(SSR/(n − p)), n = 9, p = 5; σ_g likewise with
p = 4" in Ladder §3 and probes README 5. (ii) One σ_E per freezing arm pooled over the four modes
(ν = 16), the per-mode values printed beside it; the noise line evaluated on the pooled σ_E; the
pilot note records its 90 % interval. (iii) Studentised residuals per point printed; |r| > 2.5
flagged as a candidate discontinuity beside blocking 2's continuity diagnostics, which the
smoothness probe prints at naphthalene as well — free. (iv) If per-mode verdicts are wanted, the
17-point grid.

---

## Non-blocking findings

### 7. σ_g cannot come from "one gradient": the estimator needs nine gradients per Q6 mode, and it should pool all 3N components
**Where:** Side project M2 ("the Q6 mode-G noise line … along the Q6 modes"), M4 ("one gradient at
pyrene … and σ_g"), M5 ("one gradient at coronene … and σ_g at the R3 size class"); Budget §4.11–12;
probes README 12–13; Ladder §1 mode-G form.
**What.** σ_g is "the RMS residual of g(q) about a polynomial of degree 3" over nine points: nine
gradients per mode, 36 per milestone. M4 and M5 are costed as one gradient. At pyrene and coronene
36 gradients are B3 by the plan's own sizing (side project §4). Separately, each gradient returns
3N components and every one of them is a smooth function of q with the same noise; fitting each to
its own degree-3 polynomial and pooling gives ν = 3N × 5 — 180 at benzene, 540 at coronene — against
ν = 5 for the single projected component. **Close:** M2/M4/M5 say "nine gradients per Q6 mode
(36)"; the σ_g estimator is pooled over all 3N components (Ladder §3); M4/M5 are classified by
Budget §2. This is the re-wording of Part 1 item 9.

### 8. Pilot-note leak check: one new input is a latent Δ₂ source — M1's raw displaced energies
**Where:** Ladder §3 "Order of the pilot inputs"; Budget §4.2; probes README 2; side project M1.
**What.** Confirmed leak-free: the canonical feasibility probe (one energy at equilibrium), M03's
u_band table (lab-side), the noise-injection column (DFT-only), the gradient run/no-run at
equilibrium (yields Δ₁, not Δ₂), the R0 pilot's single local-CC timing point. Not leak-free as
written: M1 computes E(displaced, frozen) and E(displaced, fresh) at 27 benzene geometries along
three modes; with the R0 pilot's DFT energies at the same geometries, Δ₂,ii for three benzene modes
is readable from files on disk before the note. M1 prints only the difference — but the R1 probe's
seal exists precisely because "printed" is not "unreadable". **Close:** M1's raw energies go to the
same hashed, sealed file as the R1 fit coefficients; the printout is the difference column and the
continuity diagnostics of blocking 2. Procedural, and cheap.

### 9. The canonical feasibility probe: measure one gradient instead of freezing a factor; the cc-pVDZ bias line is a lower bound on the TZ bias, not a substitute
**Where:** Ladder §3 anchor-basis bullet ("by factors frozen in the Q0 deck before the probe
runs"); Budget §4.1b; probes README 1b; Distilled Q7(i), §8.
**What — numbers.** Benzene/cc-pVTZ: 264 functions, 15 active occupied, 243 virtual (recalled
counts). vvvv = 243⁴ × 8 B = 27.9 GB — in-core at the 31.3 GB edge, so peak memory, not time, is
the binding number and the out-of-core/direct path is the one to time. One energy: an expectation
of 0.5–2 h on 8 cores (the probe prints it). Bias line: 61 energies → 1–5 days, inside 168 h. Full
reference by energies: 1,801 → 900–3,600 h, B3 at any plausible time. By gradients: PySCF has
`pyscf/grad/ccsd_t.py` (fetched today), so the 72-gradient branch is live; a CCSD(T) gradient costs
several energies (Λ equations, the (T) derivative, orbital response — factor 3–5 recalled) → 72 ×
(1.5–10 h) = 108–720 h, straddling the checkpoint, with a higher memory peak. The likely printout is
"bias line fits; full reference does not"; the fallback branch is then the expected one and should
be written as expected, not as a contingency. A gradient/energy factor "frozen before the probe
runs" is a number typed, not read; the probe should run **one canonical gradient** (a single job)
and extrapolate from it. **Basis dependence of the freezing bias:** the bias is the response of the
truncated energy to freezing versus relaxing the LNO space, proportional to the LNO truncation
error, which is larger at TZ than at DZ (more virtuals discarded). A DZ bias line therefore
under-reads the TZ bias — a lower bound, not a licence for the TZ arm. **Close:** the probe
measures one gradient if the code runs it; the DZ fallback sentence adds "the TZ freezing bias is
unlicensed; 'beat' from the TZ arm requires the DZ bias ≤ τ/2" (or a margin the plan chooses now).

### 10. Attack C holds; define the distance classes by bond topology and print the class scales
**Where:** Ladder §3 Q8(a) ("near, mid, far … equal frozen count per class"); item 12; probes
README 12.
**What — numbers.** Near C–C coupling ≈ 2.8×10⁻³ E_h/bohr² (Round 8); σ_coupling at σ_E = 1 µE_h,
h = 0.1 Å = 0.189 bohr: σ_E/(2h²) = 1.4×10⁻⁵. With r_c = 1.5 Å, mid pairs at 2.8 / 3.5 / 4.2 Å are
1.1×10⁻³ / 6.9×10⁻⁴ / 4.3×10⁻⁴ → S_mid = 7.9×10⁻⁴; at η₈ = 0.2 the tolerance is 1.6×10⁻⁴, i.e. the
4.2 Å pair must agree to 37 % of itself and the 2.8 Å pair to 14 % — the test bites on the mid class
as intended. Under the old single S (1.7×10⁻³ for three-per-class) a zeroed 4.2 Å mid pair would
have passed at η₈ = 0.25. Far pairs at 7 Å are at 5σ (r_c = 1.5 Å) or at noise (r_c = 1 Å) — both
handled by the "at noise" rule. Residual: the class windows are deck numbers; a "mid" window that
starts at the 1,3 distance (2.4 Å, coupling ≈ 1.5×10⁻³) inflates S_mid. **Close:** classes by bond
count (near = bonded; mid = two or three bonds; far = five or more), frozen now; the probe prints
S_class, n_class, σ_coupling and the windows.

### 11. Goal item 1 (c) lacks the "which r_f" sentence
**Where:** Goal "The goal binds" item 1 (c) vs Ladder §3 (c). Round-9 Pass A asked for the mirror;
the Ladder and probes README 15 carry it, the Goal does not. One clause.

### 12. The 2M block already contains the diagonal-cubic bonus and Δ₁
**Where:** Goal "diagonal-cubic bonus probe (Δ₃ along each scored family's mode, four energies per
mode)"; Distilled §3; probes README 6.
**What.** With ± single-mode patterns at q_s and one further amplitude (the Q6 grid at R1 already
has nine points per Q6 mode), the antisymmetric combinations give Δ₁,i and φ_iii without new
energies. Say so, or count the four energies per mode honestly as two (the second amplitude only).
Follows from blocking 1.

---

## Attack-by-attack disposition (A–G)

| # | Attack | Lands? | Disposition |
|---|---|---|---|
| A | σ estimator | **Yes — blocking 6, non-blocking 7** | ν = 4 per mode → σ̂/σ ∈ [0.42, 1.54] at 90 %; "RMS" must divide by n − p or σ is 1.5× too small; a switch at the grid edge is 85 % absorbed (biasing the sealed Δ₂,ii) and not reported; degree 4 absorbs no Δ₅ physics worth naming (P₅ share of q⁵ = 8/63); mode-G degree 3 is consistent and should pool 3N components. Recommend: divide by ν, pool the four modes per arm (ν = 16), print studentised residuals; 17 points only if per-mode verdicts are wanted. |
| B | Noise-aware stopping rule | **Yes, twice — blocking 1 and 5** | The rung's own RMS_resp is the right object for a stopping rule, but the raw mode-E response is Δ₁·p-dominated (140 vs 10 µE_h per bond at q_s = 1): symmetrise (± pairs) or the rule measures the CC−DFT force. "Stop early when Δ₂ is small" is the right behaviour once R_s is the response and the record carries σ, RMS_resp, ρ_noise — but Q8(c) must read K_off at a common threshold or the size sentence reports threshold drift. |
| C | η₈ and S | **No — non-blocking 10** | S_class with equal counts (Round-9 Pass A) already prevents a near pair carrying a mid pair; the arithmetic above shows the mid class is where the test bites at η₈ ≈ 0.2. Only the class definition needs pinning. |
| D | Fragment licence (b), (b′), (c) | **Yes — blocking 4** | Coronene has one non-trivial interior radius (one ring); the fail rule can refuse what (b′) could license; (c) at R6 is ≈ 360 fragment energies at 36/72 atoms — B3 at two shells, laptop at one — and unclassified. Licence earnable under the plan's budgets only via (b′) + B3 unless one ring passes. |
| E | Frozen space and M2's projection term | **Yes — blocking 2** | The virtual half (projection + Löwdin) is sound and differentiable; the occupied half (re-localise + argmax) is not: soft π localisation mixes rather than switches on the D₆h rungs, the argmax has zero derivative, M2's FD can straddle a switch M1 never logged, and the kill criterion can misfire. Transport the occupied LMOs by projection too; no assignment then exists. |
| F | u_band's temperature term | **Yes — blocking 3** | Naphthalene's only NIST gas spectra are 245 °C vapour or GC-IRD (opened today): ≈ −10 cm⁻¹ hot-band shift on C–C at the snippet-grade slope, so R1's C–C families are inconclusive by construction, contra "unconditional on R0–R1"; benzene has room-temperature cell spectra at 0.125–2 cm⁻¹ (R0 is fine). Pinnable sources exist: Joblin et al. 1995 (snippet grade) and Pirali et al. 2009 (Crossref record). The "estimated magnitude" needs a floor now. |
| G | Canonical feasibility probe | **Partly — non-blocking 9** | 61 energies fit (days inside 168 h); 1,801 do not; 72 gradients straddle the checkpoint and the code has them (`pyscf/grad/ccsd_t.py`, fetched) — measure one gradient rather than freeze a factor. The DZ fallback under-reads the TZ freezing bias; label it a lower bound. |

Also-worth items: Round-8 non-blocking 11 and 12 are closed, not acknowledged (Part 1). Change
table rows 28–32 match the documents; row 29 carries Round-8's wording of the stopping rule without
the Round-9 guards (ρ_max, the minimum count) — acceptable, since the row cites the finding it
closed and the Ladder is the binding text, but one clause would make it current. The pilot-note
leak check is in non-blocking 8: one latent source (M1's raw energies).

---

## What would settle it

In the order they decide things. Items 1–4 are spec edits and cost nothing; 5–8 are the measurements
the R0–R1 programme then runs.

1. **Symmetrise the mode-E response** (blocking 1) — ± pairs, R_s as the response, K_off counted in
   energies; the dry run's noise-injection column then measures Δ₂ recovery and not Δ₁ fitting.
2. **Transport the occupied LMOs by projection** (blocking 2) — one paragraph in Ladder §3; M1's
   diagnostics become singular values, not permutations; M2's correctness check needs no caveat.
3. **Re-word R0–R1's "unconditional"** and write the temperature-term floor (blocking 3); make the
   Joblin 1995 / Pirali 2009 fetch the first paid debt, because a pinned hot-band correction is the
   only route to decidable C–C families on existing gas data at R1 and R2.
4. **Write the fragment construction, the "pending (b′)" clause and (c)'s classification**
   (blocking 4); read K_off at a common ρ in Q8(c) (blocking 5); divide by ν and pool (blocking 6).
5. **M1 with the continuity diagnostics and sealed raw energies** — decides whether E_frozen is a
   smooth function of the nuclei on a D₆h molecule without an arbitrary localiser component; tens
   of benzene energies.
6. **The canonical feasibility probe with one gradient** — decides the R0 reference's form; hours.
7. **M03's u_band table with the source-class column** — decides which R0–R1 families are
   decidable, before the note; zero compute.
8. **The R1 smoothness probe with the pooled, ν-corrected σ_E and per-point residuals** (72
   energies) — the first frozen-space number the plan reads; then Round 7's order as before.

Until 1–4 are written, R0–R1 is a programme whose stopping rule measures the wrong quantity and
whose R1 scoring promise is over-stated; once they are, it is a green light and the R2–R3 scoring
follows under the same rules. The promised set beyond R3 needs only blocking 4 in spec; whether
fragments earn their licence is then a measurement, as decision 1 intended.

---

*Pass B complete. No frozen document was edited. Facts opened this pass are listed at the top with
how they were opened; the Joblin 1995 slope is snippet grade, Pirali 2009 is a Crossref record only,
and the bond-length differences, force constant, function counts, leverages, lightpipe temperature
and π-localisation degeneracy are recalled and marked so where used. Verify-on-use applies to
everything here before it enters a scored document.*

Pass B complete

