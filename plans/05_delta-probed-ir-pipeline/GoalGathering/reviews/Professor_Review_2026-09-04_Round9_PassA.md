# Professor review — Round 9, Pass A (cold read after the Round-8 Pass B patches)

**Date.** 2026-09-04.
**Role.** Cold reader with no memory of Rounds 7 and 8; no web access; nothing fetched. The
question is the brief's: does the set say what it thinks it says, and is any of it unsupported?
Chemistry is left to Pass B.
**Corpus.** Read in the brief's order, in full: root `README.md`, `plans/README.md`, plan-05
`README.md`, `Overarching_Goal.md` (glossary first), `Why_05_Supersedes_04.md`,
`Frozen_Ladder_and_Tolerances.md`, `Distilled_Project_Plan_and_Quality_Checks.md`,
`Compute_Budget_2026-09-03.md`, `probes/README.md`, `Side_Project_2026-09-04_ModeG_Gradients.md`,
`Frozen_Lines_to_Beat.md`, `Relevant_Scientific_Papers.md`, `Capstone_Mapping.md`,
`Project_Proposal_2026-09-03.md`, `Research_Note_2026-09-03_Delta_Probing.md` (§§8–9 as the parts
that win), `Professor_Review_2026-09-04_Round8_PassB.md` (its 18 findings, to check each closure is
in the text). The Round-7 Pass B review was opened only to trace the origin of the constant 0.82.
Plans 01–04 not reviewed. No file other than this one was written.

**Round-8 Pass B closure check (its 18 findings).** All eighteen are present in the text in
substance: 1 (one σ estimator, degree-4/degree-3 fits, totally symmetric mode), 2 (ρ\* = c·ρ_noise,
c and K_cap from the noise-injected column), 3 (absolute η₈·S, "at noise" pairs), 4 (four-part
fragment licence), 5 (frozen-space object written once; M1 assignment log; M2 re-projected FD and
third number), 6 (u_band decidability; R2 C–C families inconclusive by construction; supervisor ask
load-bearing), 7 (mode E on every rung, mode G in addition; no "elsewhere mode E runs" survivor
anywhere), 8 (cc-pVTZ at R0–R1; canonical feasibility probe with fallback), 9 (M5 both checks),
10 (closure depth one), 11 (P3 on PAH tensors; licence tied to the structural recovery's Q8),
12 (M06 display criteria; PAH tensors out of M06 training), 13 (inheritance walk in the Goal),
14 (proposal sweep — partial, see issues 12, 13, 16, 24, 28), 15 (items 48–51; author's fetch
recorded), 16 (four energies per (pair, family), step h), 17 (M1 displaced-geometry columns),
18 (alarm quietness stated). Five of the closures, however, introduced objects that are used
inconsistently or left undefined across files; those are the blocking findings below.

---

**Verdict: not yet.** Five in-spec seams left by the last patch must be written in before Pass B —
a pilot-note item that cannot be filled for mode G as the set is written (issue 1), a stopping rule
that is not closed (issue 2), a placeholder inside a frozen formula (issue 3), a feasibility probe
with no decision rule and the wrong extrapolation target (issue 4), and a licence input that is
undefined at the rung it governs (issue 5). Everything else is sweep work: stale survivors of
"means sealed", "three parts", "relative η₈", "gas grid", "ρ\* frozen", "six decisions" and
"Round 8 Pass B owed", plus number drift on the smoothness-probe count and the Q6 mode count. The
architecture (mode E guaranteed, mode G in addition, u_band decidability, four-part fragment
licence, frozen-space object, earned/spent learned prior) is consistent across the Goal, Ladder,
Distilled and probes README; the seams are at the edges.

---

## Blocking findings

1. **Pilot-note items 8 and 9 cannot be filled for mode G: they are read "at the σ the R1
   smoothness probe printed", and no σ_g can exist before the note**
   Where: Ladder §4 items 8–9; Ladder §3 "Order of the pilot inputs"; Budget §4.3; Distilled §4;
   Side project §3 (opening paragraph and "What success means").
   What: Ladder §4 item 9: "**K_cap per rung and per mode (E and G)**, derived from the
   **noise-injected** dry-run K at that rung's molecule (or the largest dry-run size available),
   **at the σ the R1 smoothness probe printed**, by a factor stated in the note. Both are filled for
   every rung regardless of local-CC gradient availability". Item 8: "The stopping constant c
   (ρ\* = c·ρ_noise; c ≥ 1) per mode, chosen from the noise-injected dry run's K-vs-σ curves". The
   side project agrees: "K_cap(G) and the stopping constant for mode G are frozen in the note from
   the **gradient-mode, noise-injected dry run**". Reading a point off a K-vs-σ curve needs a σ.
   For mode E that is σ_E from the R1 smoothness probe. For mode G the set says three times that no
   σ_g can exist before the note: Budget §4.3 "No displaced-geometry gradient is computed before the
   pilot note"; Distilled §4 "a displaced-geometry local-CC gradient before the note is a deviation
   in itself"; Side project §3 "no displaced-geometry gradient, hence no Δ₂ column, exists before
   the note." Yet Ladder §3's input list says the smoothness script "prints σ_E (**and σ_g where a
   gradient runs**)", and Budget §4.5 and probes README 5 repeat "(σ_g about a degree-3 fit where a
   gradient runs)" — a σ_g that the same documents forbid. The first σ_g the plan can print is M2's,
   which Budget §4.7 schedules in the same step as the R0 probe batch, i.e. after local-CC Δ₂
   numbers are readable, when Distilled §4 forbids amending the note.
   Why it matters: as written, c(G) and K_cap(G) are either filled from a σ that does not exist
   (a number typed, not read) or filled after Δ₂ is readable (the leak the pilot note exists to
   prevent). Either way "K is a measurement, not a choice" fails for mode G on every rung, and the
   side project's promise "No pilot-note item changes" is false.
   What would close it (in spec): say in Ladder §4 items 8–9, Distilled §3 and the side project
   which σ mode G's c and K_cap are read at in the note — for instance σ_g^assumed = 2.8·τ·q_s
   (the mode-G noise line itself, i.e. the cap at the worst admissible noise), labelled as an
   assumption, with M2's measured σ_g compared to it and printed; and delete "(and σ_g where a
   gradient runs)" from the three pre-note descriptions of the smoothness probe.
   Status: open

2. **The stopping rule is not closed: it accepts Δ₂ = 0 whenever c·ρ_noise ≥ 1, it has no minimum
   count, and the "2M diagonal" block it subtracts is not a defined part of the deck**
   Where: Ladder §3 "K is a measurement, not a choice"; Distilled §3 rows "Hold-out and residual ρ"
   and "K"; Goal glossary (K) and "Method skeleton" step 2; Round-8 Pass B finding 2 (accepted).
   What: (a) Ladder §3: "**K is the smallest n at which ρ(n) ≤ ρ\* with ρ\* = c·ρ_noise**, c ≥ 1 the
   pilot-note constant of item 8". Distilled §3: "ρ(n) = RMS over held-out patterns of (response
   predicted by the recovered Δ₂ − computed response) ÷ RMS of the computed held-out responses";
   "ρ_noise = σ(mode)/RMS_resp(rung)". The trivial recovery Δ₂ ≡ 0 has ρ = 1 exactly at every n.
   So whenever c·ρ_noise ≥ 1 the rule is satisfied at the first count by a recovery that recovered
   nothing, and K reads its minimum. That regime is not exotic: the plan accepted Round-8 Pass B
   finding 2's arithmetic that "at the noise line the per-response signal is below the per-point
   noise" and "ρ for a *perfect* Δ₂ is ≈ σ_E / RMS(response) ≈ 0.3–1" — i.e. ρ_noise of order 1 is
   the expected regime at the admissible amplitude. The reviewer's proposed form carried a floor,
   "ρ\*(mode, rung) = max(ρ_dry, c·σ_E(q_s)/RMS_resp)"; the adopted form dropped it, and no sentence
   says what happens when c·ρ_noise ≥ 1 (Q7's discriminability clause exists only at R0–R1;
   Distilled §8 has a "not recovered at cap" sentence but no "responses at noise" sentence).
   (b) Nothing states a minimum n. The Goal defines "K = 2M + K_off with M the number of modes" and
   Ladder §3 "K_off = K − 2M in mode E", which presumes 2M single-mode patterns are consumed before
   the rule can stop the run; but Ladder §3 says only "Patterns are consumed in the hashed order of
   the Q0 deck", and the deck is described (Goal step 2, Distilled §3 "Patterns") as "simultaneous
   multi-atom displacements built so every atom's local displacement space is complete, plus
   explicit two-mode patterns for every off-diagonal block the zero-CC dry run flags as large" —
   no ±q single-mode block is named anywhere. If the deck has no such block, "2M diagonal" in the
   cost record is a fiction; if it has one but hashed order interleaves it, K − 2M can be negative.
   Why it matters: K and K_off are the promised cost record and the only input to the size
   sentence. As written, the rule can return K = 1 with Δ₂ = 0 on a rung whose responses sit at
   noise, and the decomposition into 2M + K_off is undefined.
   What would close it (in spec): (i) a floor in Ladder §3 and Distilled §3 — if c·ρ_noise ≥ ρ_max
   (a frozen number < 1, e.g. 0.5) the rung's responses are "at noise", K is NOT_RUN and a
   fail-closed sentence is added to Distilled §8; or equivalently require ρ(K) ≤ ρ\* **and**
   ρ(K) ≤ 1/d₇-class discriminability against Δ₂ = 0 on every rung, not only at R0–R1; (ii) define
   the deck's first block as the 2M single-mode ±q_s patterns (the CMA-0 block), consumed first,
   with the stopping rule evaluated only for n > 2M; state it in Ladder §3, Distilled §3 "Patterns"
   and the Goal glossary identically.
   Status: open

3. **A frozen pass/fail floor contains the words "something like"**
   Where: Ladder §3 "Q8 has a fixed form", part (a).
   What: "a pair whose direct coupling is below 3σ_coupling (σ_coupling = σ_E·√(something like
   4)/(4h²) per the four-point formula, printed) is reported **"at noise"**". This floor decides
   which pairs are "resolved" — and a disagreement on a resolved pair is "a Q7-class breach"
   (Ladder §3, §5.4; Distilled Q7(iv), Q8) — and it enters the learned-prior licence and fragment
   licence part (c) through η₈·S. Distilled Q8 and probes README 12 cite "3σ_coupling" without the
   formula, so the Ladder's placeholder is the only definition.
   Why it matters: a frozen threshold with an unfixed constant is not frozen; two implementers
   would write different floors and different licence verdicts.
   What would close it: the four-point mixed difference [ΔE(+,+) − ΔE(+,−) − ΔE(−,+) + ΔE(−,−)]/
   (4h²) with independent per-point scatter σ_E has σ_coupling = σ_E·√4/(4h²) = σ_E/(2h²) — the
   figure Round-8 Pass B finding 3 already used ("σ_block ≈ σ_E/(2h²)"). Write that, once, in
   Ladder §3, and cite it from Distilled Q8 and probes README 12.
   Status: open

4. **The canonical feasibility probe has no decision rule, no owner for its extrapolation factor,
   and extrapolates to a diagonal-only count while Q7 needs a full canonical Hessian**
   Where: Budget §4.1b; probes README 1a; Ladder §3 "Anchor basis fixed per rung"; Ladder §2 R0
   row; Distilled Q7(i) and Q7(iv); probes README 6.
   What: Budget §4.1b: "wall-clock and peak memory printed and extrapolated to the R0 Hessian count
   (≈ 61 energies or ≈ 72 gradients). Decides whether Q6's bias line exists at R0 in the anchor
   basis, in cc-pVDZ with both arms re-run, or as the first B3 request". Ladder §3: "if the
   canonical feasibility probe shows cc-pVTZ canonical CCSD(T) does not **fit** the B2 laptop at
   R0". "Fit" is never defined — against the 168 h checkpoint? against 31.3 GB? — and no document
   says who fixes the extrapolation factor or when (before the probe runs, one hopes; the text does
   not say). Separately, 61 = 2·30 + 1 is the count for a *diagonal* Hessian along benzene's 30
   modes — enough for the Q6 bias line ("per R0 mode") but not for what Q7 asks of the same object:
   Distilled Q7(i) "at R0 also canonical CCSD(T) minus DFT in the same basis (the only reference
   independent of the freezing)" compared as a full matrix, and Q7(iv) / Ladder R0 row "Q8(a/b) on
   the reference Hessian" (couplings between atom pairs, which a diagonal cannot give). probes
   README 6 likewise lists "the references (numerical local-CC Hessian with frozen spaces;
   canonical CCSD(T) Hessian)". A full Hessian from energies is O(M²) points (of order 1,800 for
   M = 30), thirty times the extrapolation target; from gradients it is the 72 the Budget names
   only if canonical CCSD(T) gradients run in the chosen code, which no document states.
   Why it matters: the probe is the one measurement before the note that decides whether the space
   freezing is ever licensed against anything but itself (Round-8 Pass B finding 8). As written it
   can print "fits" for a count that is a thirtieth of what Q7 consumes, and a dated note can then
   say the R0 canonical Hessian is B3 after all — the outcome the probe was added to pre-empt.
   What would close it (in spec): state in Ladder §3 / Budget §4.1b / probes README 1a identically:
   the two objects (bias line: 61 energies; Q7(i)/(iv) reference: 72 canonical gradients if the code
   has them, else the energy count, written out), the rule ("fits" = extrapolated wall-clock ≤ the
   168 h checkpoint **and** peak memory ≤ 31.3 GB, or whatever the plan chooses), and that the
   factor and rule are frozen in the deck before the probe runs. If only the bias line is affordable
   at R0, say now that Q7(i) at R0 compares to the local-CC reference only and that Q7(iv) reads
   the reference Hessian from the local-CC arm.
   Status: open

5. **Fragment licence part (c) uses r_f at a rung where two different r_f values may exist or none
   has been measured; the set does not say which**
   Where: Ladder §3 "The fragment licence" (b), (b′), (c); Goal glossary (r_f); Goal "The goal
   binds" item 1; Budget §4.13; probes README 14–15.
   What: (b) defines r_f at R3: "coronene's Δ₂ recovered whole and recovered from capped fragments
   **at the smallest fragment radius r_f that passes**"; the glossary: "r_f = the smallest passing
   fragment radius (measured)". (b′) repeats the comparison "on a molecule larger than coronene
   (circumcoronene-class, R4), promised conditional on B3 classification" — which yields a second
   smallest passing radius, unnamed. (c) then reads: "direct couplings … computed from fragments of
   radius r_f and r_f + one ring carved from the rung's own DFT geometry … first instance on
   circumcoronene's central ring at R4, then on the R6 flake". Which r_f: coronene's, or
   circumcoronene's when (b′) ran, or neither when (b′) was not classified affordable? And if (c)
   fails at (r_f, r_f + one ring) but would pass at (r_f + one ring, r_f + two rings), is r_f
   raised — and does the R6 Δ₂ then use the raised radius? Nothing says.
   Why it matters: (c) is the one part of the licence that "can fail because the interior is
   different" (Round-8 Pass B finding 4, accepted). A test whose input radius is unspecified can be
   run at whichever radius passes.
   What would close it (in spec): one sentence in Ladder §3 (c), mirrored in the Goal's item 1 and
   probes README 15: "r_f in (c) is the R3 value from (b); if (b′) ran and its smallest passing
   radius is larger, that larger value is used; the R6 fragment probe uses the radius at which (c)
   passed, printed in the certificate; (c) is run once at (r_f, r_f + one ring) and is not re-run at
   a larger radius without a dated note before the second run."
   Status: open

## Non-blocking findings

6. **"Means sealed" survivors contradict the sealed fit coefficients**
   Where: Ladder §2 R1 row; probes README "Before the pilot note" header.
   What: Ladder R1 row: "scatter printed before the pilot note, **means sealed**"; probes README:
   "single-mode scatter with **sealed means**". The current object (Ladder §3, Budget §4.5, probes
   README 5) is "the fitted polynomial coefficients (which contain the diagonal Δ₂ elements) to a
   hashed, sealed file". A mean carries no Δ₂ information; the quadratic coefficient does. Two
   readers will disagree about what is sealed.
   Why it matters: the seal is the pilot note's leak control; its object must be named once.
   Status: open

7. **The R1 smoothness probe's energy count drifts and none of the numbers matches its own
   specification**
   Where: Budget §4.5; probes README 5; Proposal §8; Research note §8.
   What: Budget §4.5: "(B2, **~40** local-CC energies of naphthalene): four modes (C–C stretch, C–H
   stretch, CH-oop, one totally symmetric), nine points each at q ∈ [−1, 1], TightPNO, **with and
   without frozen spaces**"; probes README 5: "**≈ 40** local-CC energies"; Proposal §8: "the
   naphthalene noise-floor measurement (**about thirty** energies)"; Research note §8: "(naphthalene,
   three modes, nine points, frozen data, **~30** energies)". The specification itself is
   4 modes × 9 points × 2 arms = 72 local-CC energies (65 if the q = 0 point is shared between arms
   and modes). The count is pre-note B2 work and not a gate, so this is drift, not a hole; but the
   plan's own convention is that arithmetic is printed, not typed, and here four typed numbers are
   all wrong.
   Status: open

8. **The side project still counts three Q6 modes; the set has four**
   Where: Side project §3 rows M4 and M5; probes README 13.
   What: M5: "AD-vs-FD along the **three** Q6 modes (six frozen-space energies)"; M4: "correctness
   (FD along the Q6 modes, **six** energies)" — six is two per mode for three modes. Ladder §3 and
   Distilled Q6 now name "a C–C stretch, a C–H stretch, a CH-oop mode **and one totally symmetric
   mode**", and the side project's own §1.2 says "the Q6 grids (which now include a totally
   symmetric mode)". M4/M5 as written omit exactly the mode the totally-symmetric case was added to
   watch (assignment switches on the D₆h rungs — coronene is one).
   Status: open

9. **The mode-G noise-line constant 2.8 has no derivation anywhere in the workspace**
   Where: Ladder §3 Q6 bullet; Distilled Q6; Side project M2; probes README 5 and 6; Research
   note §8.
   What: Ladder §3: "the **mode-G noise line**: σ_g ≤ 2.8·τ·q_s" and "the per-point scatters the
   noise lines were derived for". The mode-E constant is traceable: Round-7 Pass B issue 1
   "σ_E ≤ (2/√6)·δω̃·q_s² ≈ 0.82·δω̃·q_s²" and note §8's three worked values. For 2.8 there is no
   sentence in any frozen document, in note §8/§9 or in either Round-8 review (grep for "2.8·",
   "√2", "fewer power" finds only the formula itself). The brief expected a "one fewer power of q_s"
   sentence stated as arithmetic; none exists. The constant is consistent with the same convention
   (a central first difference of gradients, σ(Δ̂₂) = σ_g/(√2·q_s) ≤ 2τ, gives σ_g ≤ 2√2·τ·q_s ≈
   2.83), but that is my arithmetic, not the plan's.
   Why it matters: a frozen threshold whose constant cannot be traced is a number from recall by
   the plan's own standard.
   Status: open

10. **ρ\* is still called a frozen target in four places; it is now a per-rung computed quantity**
    Where: Goal glossary; Proposal §5.1 step 2 and §7; Why_05 rows 7 and 21.
    What: Goal glossary: "**ρ\*** = its frozen target". Proposal §5.1: "the probe count K is the
    number at which a held-out residual first meets **a target frozen before any coupled-cluster
    response exists**"; §7: "so no **residual target**, probe cap, tolerance or margin can be shaped
    by a result". Why_05 row 21: "(so K_cap and **ρ\* are frozen** for mode G without any local-CC
    gradient existing)"; row 7: "**new items 8–13**: residual target ρ\*". Against Ladder §3:
    "ρ\* = c·ρ_noise" with "RMS_resp the RMS of the rung's own held-out responses" — only c is
    frozen; ρ\* is computed from the rung's responses. The glossary is the file that "wins on drift",
    so the wrong definition currently wins.
    Status: open

11. **The change table contradicts itself and its own README description**
    Where: Why_05 status line, rows 7, 21, 22, 29; row order; "What plan 05 does not change";
    plan README reading-order item 2.
    What: (a) Row 22: "with a **relative** block-disagreement tolerance η₈" vs row 29: "η₈ in
    **absolute** form" — both sides in one table. (b) Row 7 lists the pilot-note items as "residual
    target ρ\*, cap K_cap per mode, … Q8 numbers (r_max, ε₈, η₈, γ) and direct-coupling pairs" —
    item 8 is now c, item 12 also carries h. (c) Rows run 1–25, then 28–32, then 26–27; the README
    says "every change relative to plan 04, in one table (**27 rows**)" — there are 32. (d) The
    status line says "revised the same day after Round-8 Pass A (issues 11, 13)" and "the user's
    **six** decisions"; rows 28–32 cite Round-8 Pass B and decision 7 exists. (e) "What plan 05 does
    not change" lists "the numerical tolerances (…)" and "the neutral-charge rule", while row 28 adds
    a gas-side decidability tolerance (u_band) and Ladder §2 "Charge" makes the charge rule "a
    per-rung choice, not a capability limit" that "a pilot note may name".
    Status: open

12. **"Three parts" survivors of the fragment licence**
    Where: Mapping M07 and M08; Proposal §5.2 R6 row and §9; Research note §9.
    What: Mapping M07: "no R6 job other than fragment-probed, and none before the fragment licence's
    **three parts** have printed"; Mapping M08: "the fragment-probed R6 under its **three-part**
    licence"; Proposal §5.2 R6 row: "under a **three-part** measured licence (locality at R2–R3;
    coronene probed in fragments reproducing coronene probed whole; **direct blocks on the R6
    fragments**)" — the last is the old, withdrawn part (c), while the same table's R4–R5 row
    already names the convergence test and (b′); Proposal §9: "(now **three** measured parts including
    a convergence test …)"; note §9: "under a **three-part** measured licence (Q8 at R2–R3; coronene
    probed in fragments vs whole at R3; direct blocks on the R6 fragments)". The Goal, Ladder §3,
    Distilled §4/P5/§8 and probes README all have four parts (a), (b), (b′), (c).
    Status: open

13. **The pilot-note input lists do not agree**
    Where: Ladder §4 opening; plan README "Not yet done"; Budget §4 "Before the pilot note";
    Proposal §7 and §8.
    What: Ladder §4 names seven inputs across (a)–(f): the R0 pilot, the dry run with its
    noise-injection column, "the scoreboard re-read probe with M03's u_band table", the canonical
    feasibility probe, the gradient run/no-run, probe M1, the R1 σ. The README's list matches. Budget
    §4's pre-note order (items 1, 1b, 2, 3, 4, 5, then "6. Pilot note committed") has **no M03 u_band
    probe and no R0 pilot** as such; the probes README does (its items 2 and 4). Proposal §7: "it is
    written with the laboratory side, the opponent side, a DFT-only dry run of the probing machinery,
    the noise-floor measurement and single-point timings in hand — **and nothing else**" — five
    items, omitting M1, the canonical feasibility probe, the gradient run/no-run and u_band, with an
    explicit "nothing else". Proposal §8's list omits M1 and the feasibility probe. Also the README's
    "the **two-mode** zero-CC dry run" reads as two normal modes; it means both modes E and G.
    Status: open

14. **K_cap "from the dry run" without "noise-injected"**
    Where: Budget §3 table (row "Gradients for a full Hessian, DFT level"); probes README 3.
    What: Budget §3: "K_cap(G) is frozen from the gradient-mode dry run for every rung"; probes
    README 3: "K_cap(G) comes from the dry run regardless". Ladder §3: "from the **noise-injected**
    dry run … — never from the noiseless one"; Distilled §4 forbids "taking c or K_cap from a
    noiseless dry run". Two survivors of the pre-patch wording.
    Status: open

15. **One engine hedge survives and one sentence claims more than the fetch shows**
    Where: probes README 1b; Budget §3 table (row "Local-CC(T) gradient").
    What: probes README 1b: "(pyscf-forge LNO-CC; **whether the release is CCSD or CCSD(T) is
    printed**)" — item 48 says "**LNO-CCSD(T) is present, closed- and open-shell**" (fetched
    2026-09-04 by the reviewer and the author); the hedge is now the inaccurate sentence. Budget §3:
    "PySCFAD's **differentiable LNO-CCSD(T) exists in released code** (`pyscfad/lno/`, bib 49,
    fetched 2026-09-04)" — the fetch is a directory listing with a `ccsd_t.py`; whether (T) is
    differentiated end-to-end is the side project's item (a): "whether (T) is differentiated
    end-to-end in `pyscfad/lno/ccsd_t.py` as released. Printed as the first side-project output."
    The Budget's sentence states as fact what item (a) is to verify. Elsewhere (Goal, Distilled §3,
    Why_05 row 25, side project §1.1, items 48–49) the wording is correct: present in the released
    code; behaviour is M1/M2's measurement.
    Status: open

16. **The proposal states the 8 cm⁻¹ resolution and the hot-vapour temperature as "verified"; the
    bibliography grades them snippet and recalled**
    Where: Proposal §5.2 (R2 row and the paragraph below the table); §11 risk 7; §13.3.
    What: Proposal §5.2 R2 row: "hot-vapour GC-IR spectra **at 8 cm⁻¹**"; §5.2 text: "The second
    domain review (4 September) **verified** that the NIST gas-phase spectra … are hot-vapour GC-IR
    spectra homogenised to 8 cm⁻¹ resolution"; §11 risk 7: "**Verified on 4 September**: the NIST/EPA
    spectra are hot-vapour GC-IR at 8 cm⁻¹ resolution." Item 50: the 8 cm⁻¹ statement is "**snippet
    grade**"; the JCAMP has "no resolution or temperature line"; the lightpipe temperature is listed
    by the Round-8 reviewer under "Recalled, not verified". The Ladder R2 row, Frozen_Lines §5,
    Why_05 row 28 and Mapping M03 carry the grade correctly; the proposal does not, and a supervisor
    reads the proposal.
    Status: open

17. **"Gas grid" survivors of the point-spacing rule**
    Where: Mapping §2 (M03 need row), §3 M03 heading, M08; Proposal §12.
    What: Mapping §2: "**the gas grid per molecule and family** that the decidability rule
    consumes"; M03 heading: "the scoreboard, the measured tolerance, and **the gas grid**"; M08:
    "**M03** (scoreboard, matrix tolerance, **gas grid**)"; Proposal §12: "the laboratory scoreboard
    with the measured matrix tolerance and **gas grids**". The rule now consumes u_band (Ladder §2;
    the Goal's forbidden quotes ban "Decidable … from a point spacing"). The M03 body text is
    correct; its headings and the summaries are not.
    Status: open

18. **Three small ladder/side-project inconsistencies on where Q6 runs and in which basis**
    Where: Ladder §2 R0 row and R1 row; Ladder §3 "Anchor basis" and Q6 bullet; Side project §3 M4.
    What: (a) R0 row licenses "the Q6 noise grid at R0", while Ladder §3 and Distilled Q6 measure
    the noise grid "at R1 and at the R2-size family" only. (b) R1 row: "the licence downgrades to
    **R0-only plus a declared cross-basis protocol**", while Ladder §3 freezes "the same basis on both
    arms of every comparison" — a cross-basis protocol is what that sentence forbids; the R0 fallback
    (both arms re-run in cc-pVDZ) is the consistent form and should be R1's too. (c) Side project
    M4: "one gradient at **pyrene/cc-pVTZ**" licenses mode G at R2, while Ladder §3 says "the R2–R6
    basis is a deck number frozen before that rung's first probe"; M5 correctly says "in the R3 deck
    basis". If the R2 deck picks another basis, M4's σ_g was measured in the wrong one.
    Status: open

19. **The amplitude "choice from the grid" is decided by arithmetic, and σ in ρ_noise has no rung
    index**
    Where: Ladder §3 "Pattern amplitudes come from the Q6 step grid" and the Q6 bullet; Ladder §3
    "K is a measurement"; Distilled §3 "Hold-out and residual ρ".
    What: (a) Ladder §3: "the largest step at which the R1 smoothness probe's σ is under the noise
    line of the mode used" together with "both evaluated for each grid step q_s ∈ {0.25, 0.5, 1.0}
    from the one σ (the formula, not the data, supplies the q_s dependence)". With one σ and a line
    that grows with q_s, passing at a smaller step implies passing at every larger one, so "the
    largest step under the line" is q_s = 1.0 whenever anything passes. The three-point grid is
    therefore not a choice but a single test (σ_E ≤ 0.82·τ). That may be intended; the text presents
    it as a selection. (b) "ρ_noise(rung, mode) = σ(mode)/RMS_resp(rung), where σ is the per-point
    scatter σ_E or σ_g measured by the R1 smoothness probe" — σ carries no rung index, yet Q6 also
    measures σ "at the R2-size family". Which σ enters ρ_noise at R2 and R3 (R1's, or the R2-size
    measurement) is not said; the two can differ (item 44's size growth is the plan's own risk).
    Status: open

20. **η₈·S: the pair list's composition is unconstrained, so S is whatever the deck makes it**
    Where: Ladder §3 Q8(a) and item 12; probes README 12.
    What: "S = √(Σ direct² / n_pairs)" over "deck-chosen π-system pairs at near, mid, far
    distances"; item 12 freezes "the direct-coupling pair list per rung (which atom pairs, at which
    distances…)" with no count or composition rule. S is dominated by the near pairs; a list with
    many near pairs raises S and lets every mid pair pass η₈·S regardless of its own size. The list
    is frozen before responses (good), but nothing stops it being frozen that way. State a rule
    (equal numbers per distance class, or S per class), or say the mid pairs are the only ones the
    test is meant to bite on and freeze their count.
    Status: open

21. **The learned-prior licence's PAH number is reported, not gated, and the R2–R3 saving is
    assumed in a parenthesis**
    Where: Ladder §3 "The learned prior"; Ladder §4 item 5; Distilled §5, P3.
    What: Ladder §3: "P3 must have shown a saving on the dry-run corpus **and its effect size on
    the PAH held-out tensors is reported beside it**"; item 5: "**reported on the PAH held-out
    tensors as well**". No threshold attaches to the PAH report, so a prior that saves patterns on
    QM9 and none on the PAH tensors is licensable provided the R2/R3 agreement within τ₇ holds. And
    at R2/R3 the text says "the prior-assisted recovery to its **(smaller)** K" — the saving is
    presupposed, not required; a prior-assisted recovery that agrees within τ₇ at the *same* K as
    the structural one earns the licence as written. Say whether a saving at R2–R3 is required and
    whether the PAH held-out effect size is gated or informational; either is defensible, silence is
    not.
    Status: open

22. **M3's 28 GB cap has no stated origin on a 31.3 GB machine**
    Where: Side project §3 M3; probes README 8; Budget §1 and §3.
    What: M3: "peak memory ≤ **28 GB**"; probes README 8: "peak memory ≤ 28 GB". Budget §1: "32.0 GB
    DDR5-5600 (**31.3 GB usable**)". The only other 28 GB in the set is the old machine's:
    Budget §3 "canonical (T) fails at ~114 bf with **28 GB**" (plan-02 provenance). If 28 is
    "31.3 minus OS headroom", say so; as written it reads as the previous laptop's RAM carried by
    habit.
    Status: open

23. **The budget file breaks its own supersede-only rule and its status line is stale**
    Where: Budget status paragraph; §1 B2 row; §4 item 1b; §5.
    What: Status: "under that file's own supersede-only rule — **a later change needs a new dated
    file, never an edit in place**"; §5: "Supersede this file only with a new dated compute-budget
    doc." The same 2026-09-03 file contains "**Decided 2026-09-04**: this is the current laptop" and
    the 2026-09-04 item "1b. Canonical feasibility probe", and its status line names only the
    Round-7 revisions. Either the rule is dropped for plan 05 (say so) or the file is re-dated.
    Also cosmetic but confusing: the Budget numbers the feasibility probe "1b" and M1 "2", the probes
    README numbers them "1a" and "1b".
    Status: open

24. **Decision-count and review-status staleness at the entry points; decision numbering differs
    between the Goal and the proposal**
    Where: root `README.md` plan table; `plans/README.md` (table, "Do not call plan 04 or plan 05
    complete", "Layout" paragraph); plan README "Decisions" and reading-order item 9; Goal status
    line; Proposal §10.
    What: root README: "Round 8 Pass A run and addressed; **Round 8 Pass B owed**"; plans/README:
    "Round 8 Pass B owed" (twice) and "Plan 05's completeness waits on its Round-8 Pass B" — the plan
    README records Round-8 Pass B as run with "All 18 addressed". Goal status: "amended on
    2026-09-04 by **six** user decisions"; plan README: "**All six decisions** of 2026-09-04 are
    closed" (decision 7 follows in a separate paragraph); plan README item 9: "(items **23–49** new)"
    — the bibliography runs to 51. Proposal §10 numbers the decisions 1 fragment, 2 M05, 3 R2,
    4 promised set, 5 folders, 6 machine, 7 Foundations; the Goal numbers them 1 fragment,
    2 folders, 3 R2, 4 M05, 5 promised set, 6 B2, 7. The Mapping cites "Goal decision 4" for M05;
    a supervisor reading the proposal's "decision 4" finds the promised set.
    Status: open

25. **Research note §9 was not extended for the Round-8 Pass B changes, so its stale sentences win
    by the note's own precedence rule**
    Where: Research note status paragraph, §8, §9.
    What: The note's rule: "Where they disagree, §9 wins over §8 and §8 over §§1–7." §8 still says
    "(deck-chosen π-system pairs, four-point differences, **≈12 energies per pair**)" (now four
    energies per (pair, family)), "(naphthalene, **three modes**, nine points, frozen data, **~30
    energies**)" (now four modes), and §9 "under a **three-part** measured licence (…; **direct blocks
    on the R6 fragments**)". The plan README says "research note §9 appended" for the Round-8 Pass A
    changes only. Either append the Round-8 Pass B corrections to §9 or add one line to the status
    paragraph saying the frozen documents win over the note from 2026-09-04 on.
    Status: open

26. **Terms used across files that the glossary does not define, and acronyms used before any
    expansion**
    Where: Goal glossary vs Ladder §3/§5, Distilled Q7/Q8, Budget §4.7, probes README 6/13, Side
    project §1.4 and §3, Frozen_Lines §5, Mapping M03, item 50.
    What: Used but not in the glossary: "**resolved pair**" (Ladder §3, §5.4; Distilled Q7(iv), Q8),
    "**at noise**" (defined only inline in Ladder §3 Q8(a)), "**RMS_resp**" (Ladder §3, Distilled §3),
    "**re-projected**" (Budget §4.7, probes README 6, side project M2 — the glossary's frozen-space
    entry does not name the projection), "**AD**" / "**FD**" (side project §1.4 "AD and FD agree",
    M2–M5; probes README 6, 13 — never expanded as automatic differentiation / finite differences),
    "**GC-IRD**" (Ladder R2 row, Frozen_Lines §5, Why_05 row 28, Mapping M03), "**IRMPD**" (Ladder R2
    row, Frozen_Lines §5), "**SRD 35**" (item 50), "**BHLYP**" (Ladder §3, Distilled §3). "S", "c",
    "ρ_noise", "u_band", "r_f", "(b′)", "closure depth one" and "assignment permutation" are covered
    (the last two in the Goal body and Ladder §3 rather than the glossary list; acceptable). Also:
    Side project §5 lists as "What changes in the plan on success (by dated note, not now)" the Goal
    cost-question sentence and the Ladder §1 "M3, M4 and M5 (both checks each)" rule — both are
    already in the current text, so §5 describes as future two edits that were made.
    Status: open

27. **Frozen_Lines carries two stale summaries of documents that moved**
    Where: Frozen_Lines "The criterion" paragraph; §7 closing paragraph.
    What: (a) "**The criterion (from Overarching_Goal.md).** … **gas-phase rungs unconditionally**,
    matrix-scored families only if the M03-measured matrix–gas delta is smaller than the beat
    margin" — the Goal's prime directive now reads "unconditional on the gas-phase rungs (R0–R1); on
    R2–R3 per family, gas-scored families decidable only where … u_band is smaller than the beat
    margin"; the gas-side gate is missing from the sentence that says it quotes the Goal. (b) §7:
    "Debts that concern plan 05's *method* … (full texts of items **27, 28, 30, 37**; the O1NumHess
    code version; the GPU Hessian timing)" — the bibliography's "Method debts" list says item 30's
    full text was read, and adds items 46, 44, Mester 2025, side-project item (a), the hot-band
    references, the M05 reading-2 fallback, QM9's size range, item 50's PDF, item 45's table and the
    CMA re-read. The two lists headed "identical" (§7 vs "Named debts") are identical; this trailer
    is not.
    Status: open

28. **Proposal staleness not covered above**
    Where: Proposal header; §5.3; §11 numbering.
    What: Header: "**Two** external reviews of this plan (a cold read and an adversarial domain
    review, **both on 3 September 2026**) are in the folder" — §9 of the same document describes
    four. §5.3: "whether the frozen space … is a smooth function of the nuclei on the two six-fold-
    symmetric molecules … **The first milestone prints exactly that.**" — the assignment log is
    probe M1, main-project work, not a side-project milestone (M2 prints the projection term).
    §11's risks run 1, 2, 3, 4, 5, 7, 6.
    Status: open

## What passed

- **Mode E on every rung, mode G in addition.** No survivor of "elsewhere mode E runs" or "mode G
  is the route" in any file; Goal, Ladder §1/§3, Distilled §1/§3/§4, side project and Mapping M07
  say the same thing; Q8(c) per mode; the classification rule classifies both modes. Do not touch.
- **Decision 7 sweep.** Goal, plan README, Mapping (status, M05, §4, §5) and Proposal §10 all say
  closed, nothing submitted, M02 a plan; no text treats the M05 reuse exposure as pending. (Only the
  "six decisions" count survivors of issue 24 remain.)
- **The frozen-space object.** Written once in Ladder §3 (maximal-overlap mapping, assignment
  printed, projection onto the new virtual space, Löwdin orthonormalisation, projection inside the
  graph for mode G) and repeated consistently in probes README 1b, Budget §4.2, side project §1.2/§2
  and M1's row; M2's FD reference is the re-projected energy in all four places.
- **u_band decidability.** Ladder §2 rule, Goal prime directive and forbidden quote, Distilled §1/
  §4/Q1/P2/§8, Mapping M03 body, probes README 2, Frozen_Lines §5, Why_05 row 28 agree; the R2 C–C
  families are declared inconclusive by construction everywhere the R2 scoreboard is described;
  the supervisor ask is marked load-bearing in Ladder §2, Mapping M03 and Proposal §5.2/§13.3.
- **Recalled numbers carry their grades where they appear:** QM9 ≤ 9 heavy atoms (Distilled §6,
  Mapping M05, Method debts — "recalled by the Round-8 reviewer, to be verified"); cc-pVTZ function
  counts and per-fragment GB (side project §4 — "recalled sizing … an expectation, not a number");
  8 cm⁻¹ at snippet grade in Ladder R2, Frozen_Lines §5, Why_05 row 28, Mapping M03, item 50; the
  lightpipe temperature enters no frozen number (the temperature term is "a declared hot-band shift
  … or, until one is pinned, the labelled uncertainty"). Only the proposal drops the grade (issue 16).
- **Engine facts.** The author's own fetch is recorded (items 48–49 "fetched … by the Round-8
  Pass B reviewer and by the author"; side project §1.1 and §8); Distilled §3, Why_05 row 25, Goal
  and Proposal §5.3 say "present in the released code; behaviour with frozen spaces is M1/M2's
  measurement"; (T)'s end-to-end differentiation is correctly left to side-project item (a)
  everywhere except the Budget sentence of issue 15.
- **No timing used as a budget.** Every wall-clock in the set is a NOT_RUN slot, a plan-02
  provenance figure labelled as such, or an assertion labelled as such; the "hours/days" language
  the brief warned of does not appear in Ladder §3's anchor-basis bullet or in Budget §4.
- **The 0.82 constant is traceable** (Round-7 Pass B issue 1: 2/√6; note §8's worked values), and
  the stopping rule's two forms are equivalent as stated (ρ ≤ c·σ/RMS_resp ⇔ held-out χ² per point
  ≤ c²).
- **The pilot-note seal is sound on the point the brief asked.** The least-squares residual is the
  projection of the nine ΔE(q) values onto the orthogonal complement of the degree-≤4 polynomial
  space; its RMS is independent of every fitted coefficient, including the quadratic one that holds
  Δ₂,ii. So σ_E (and σ_g about its degree-3 fit) carries no Δ₂ information, and printing it before
  the note leaks nothing. The seal's object is the coefficient file, and the script-refuses-to-open
  rule (probes README 5) is the right discipline. (Issue 6 is only about two sentences that still
  call the sealed object "means".)
- **The direct-coupling probe** is four energies per (pair, family) with step h, full 3×3 block for
  the near pair only, in Ladder §3, Distilled Q8, Budget §4.11 and probes README 12 identically;
  the anthracene count (133) and the R6 whole-molecule floor (2,580 for 432 atoms) and coronene's
  204 agree across every file that states them.
- **M5 has both checks** (side project M5, "What success means", Budget §4.12, probes README 13,
  Ladder §1) — modulo the mode count of issue 8.
- **Resonance closure at depth one** is bounded identically in the Goal, Ladder §3, Ladder §4
  item 7 and Distilled §3, with size and Hessian count printed in the note.
- **The two debt lists** (Frozen_Lines §7 vs bibliography "Named debts") are identical, as both
  claim.
- **Learned-prior rule** (earned R2–R3 on the same responses within τ₇, direct couplings within
  η₈·S, structural Q8 passed; spent R4–R6; R0–R3 always structural; no mixed-prior ratios) is one
  rule in Goal, Ladder §3/§6, Distilled §3/§4/§5/§9, Mapping §0/M05/M07/M08 and probes README 12.
- **Fragment licence parts (a), (b), (b′), (c)** are one list in Goal item 1, Goal Reach question,
  Ladder §2 rows R3/R4/R6 and Promised, Ladder §3, Distilled §4/P5/§8/§9, Budget §4.12–13, probes
  README 13–15 — the "three parts" survivors of issue 12 are all in summaries, none in the defining
  text.
- **Pointers to "the dated note"** are unambiguous: Ladder §2's two notes are named in the glossary,
  the R2 note's addendum is inside it, and the remaining pointers are to per-rung notes that do not
  exist yet.

Pass A complete
