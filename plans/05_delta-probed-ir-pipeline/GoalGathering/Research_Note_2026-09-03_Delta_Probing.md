# Research note — Δ-probing (2026-09-03)

**Status.** Source document for plan 05. This is the record of a literature search run on
2026-09-03 in answer to one question the user asked: *what is the single most inventive way to
make the plan-04 pipeline (aromatic molecule in, infrared spectrum out, CC-anchored) fast
enough that super-large PAHs fit into roughly a year of computing, without giving up the
intended accuracy?* It is a **source**, like `AI_Chats/grok_chat_4.md` was for plan 04 — not a
plan, not a result. Every identifier below carries a verify status; nothing here is a measured
number of this project.

The trigger: the user reported that a separate assistant session estimated that one large PAH
would still take "many, many hours" of supercomputer time through the plan-04 pipeline. That
report is an **assertion**, recorded as such; the plan-04 source conversation's own figure was
"~10⁴ DLPNO points for coronene ≈ thousands of node-hours" (grok_chat_4, lines 352–360), also
an assertion.

---

## 1. Where the plan-04 cost actually sits

Plan 04 learns a **per-molecule surface** from self-generated local-CC points and extracts the
anharmonic spectrum from that surface. The cost is structural, not an implementation detail:

- the surface is a global object over 3N−6 coordinates (coronene 102, C₃₈₄H₄₈-class ≈ 1,290);
- almost all of it is already known at DFT quality; the CC anchor is paid for every point
  although the CC−DFT *difference* is the only new information;
- local-CC energies are noisy in the ways that matter for curvature (domain changes on
  displacement), so the learned surface must average that noise with more points.

Rust or any other language change does not touch this: the expensive kernels already run in
compiled Fortran/C++/CUDA inside ORCA, Psi4, MRCC or PySCF, and the Python glue is negligible.
The only Rust electronic-structure code found (REST, 2025) has no local coupled cluster.

## 2. The idea: probe the correction, not the surface

Let Δ be the difference between the local-CC and the DFT potential energy surfaces near the
equilibrium geometry, expanded in force constants: Δ₂ (Hessian correction), Δ₃ (cubic), Δ₄
(semi-diagonal quartic). Three properties of Δ that the full surface does not have:

1. **Small and smooth** — the standard Δ-learning observation (Käser & Meuwly and many
   others): the CC−DFT difference varies far less with geometry than either surface.
2. **Short-ranged in real space** — the correlation-energy error of DFT is a local quantity.
   This is the premise of every local-correlation method (DLPNO, LNO, PNO-LCCSD), of
   short-range Δ-machine-learning (Mészáros, Szabó & Daru 2025: a Δ-correction trained on
   finite clusters transfers to condensed phase), and of molecular-orbital-based ML transfer
   from small to large molecules (Welborn, Cheng & Miller 2018).
3. **Sparse in the DFT normal-mode basis** — if DFT modes are approximately the true modes, the
   Δ Hessian in that basis is close to diagonal.

A short-ranged force-constant tensor has two exploitable structures: it is **sparse** in an
atom-local basis, and its off-diagonal blocks between distant atom groups are **low-rank**.
Both allow recovery from a number of *simultaneously multi-displaced* probes that does **not
grow with molecule size**:

- **O1NumHess** (Wang, Luo, Wang & Liu; arXiv:2508.07544; JCTC 21, 10893, 2025): a full
  molecular Hessian from O(1) gradients at displaced geometries, by exploiting the
  off-diagonal-low-rank property; the gradient count **saturates around 100–124** for systems
  with hundreds of atoms; open-source Python with an ORCA interface; frequency errors about
  twice those of a conventional double-sided seminumerical Hessian. Tested at DFT level only.
- **Sanders, Andrade & Aspuru-Guzik** (ACS Cent. Sci. 1, 2015; PMC4827532): compressed-sensing
  recovery of a B3LYP/6-31G* Hessian in the eigenbasis of a cheap method (MM3). On
  **anthracene**, 30 % of the Hessian columns gave a maximum frequency error below 3 cm⁻¹;
  across **polyacenes with 1–15 rings** the required column count grew only logarithmically.
  This is the PAH class of this project. Not extended to coupled cluster or to anharmonic
  constants by its authors.
- **Compressive-sensing lattice dynamics** (Zhou, Nielson & Ozolins; arXiv:1805.08904) and the
  hiPhive package recover cubic and quartic force constants of solids from a modest number of
  randomly displaced DFT configurations by ℓ₁-regularised regression. Solids, DFT only.

**What the 2026-09-03 search did not find** (queries listed in §6): any application of
compressed-sensing or O(1)-gradient Hessian recovery to the *difference* between a local-CC
and a DFT surface; any extension of that recovery to cubic/semi-diagonal quartic Δ constants
for GVPT2; any application at PAH sizes above anthracene at a coupled-cluster level. That
combination is the proposal.

## 3. What would slot where (the plan-05 method skeleton, in one paragraph)

Per molecule: (1) DFT geometry, analytic harmonic Hessian and dipole derivatives — the global,
delocalised part, per molecule, on GPU where available (GPU4PySCF reports an 84-atom
def2-TZVPP B3LYP Hessian in ~30 min on one A100; assertion from the vendor paper, re-timed
before use); (2) **Δ-probing**: a hashed set of K displacement patterns, built so that every
atom's local displacement space is complete and augmented with mode-targeted patterns for the
promised band families; at each pattern the local-CC and DFT energies (and gradients, where the
code provides them) are evaluated **with correlation domains and pair lists frozen at the
reference geometry**, and Δ₂ (plus Δ₃/Δ₄ on the promised families' modes) is recovered by one
sparse-recovery solve in the DFT normal-mode basis; (3) GVPT2 on DFT-plus-Δ with the
resonance rules plan 04 already froze; (4) an error budget whose new terms are the recovery
residual on held-out probes, the local-CC noise floor measured with and without frozen domains,
and the measured locality tail.

## 4. Load-bearing dependencies (each is a probe in plan 05, not an assumption)

1. **Gradients at the anchor level.** The O(1)-probe count needs gradients. ORCA 6.1's change
   log lists canonical CCSD(T) gradients and DLPNO-MP2 gradients; **no analytic
   DLPNO-CCSD(T) gradient is advertised** (verified against the ORCA 6.1 change log and the
   ORCA 6.0 gradient page on 2026-09-03). PySCFAD reports LNO-CCSD(T) gradients by automatic
   differentiation for medium-sized molecules (arXiv:2404.03129). Until a timed probe shows a
   working gradient at the rung's size, the plan's default is **energy-only recovery** in the
   DFT normal-mode basis (K ≈ 2M for the diagonal Δ₂ plus a frozen number of multi-mode
   probes for the off-diagonal part; M = number of modes). A workable split, to be probed:
   CCSD-level gradients plus energy-only (T), since the (T) increment is the smoothest, most
   local piece (Ruth, Gerbig & Schreiner 2022 learned it from few points).
2. **Locality decay.** The Δ₂ element between two atoms must decay with their distance within
   the molecule. Measured at R1–R3 before anything larger runs; the decay length r_c is a
   pilot-note number. If Δ₂ does not decay, the probe count does not saturate and the method
   has no size advantage — that outcome is reportable and closes the reach rung honestly.
3. **Frozen domains.** ORCA documents `StoreDLPNOData` / `RefBaseName` to keep pair lists and
   correlation domains fixed for numerical DLPNO-MP2 derivatives, and explains why (domain
   changes on displacement produce discontinuities). The same option is **not documented for
   DLPNO-CCSD(T)** (checked 2026-09-03). Psi4 ships an open-source DLPNO-CCSD(T)
   (single-node OpenMP; crambin-size systems reported) in which domain freezing could be
   implemented; MRCC's LNO-CCSD(T) is another candidate. Madriaga & Crawford (JPCA 129,
   10014, 2025) report that PNO domain changes of order 1 μE_h in energy produce errors above
   100 % in finite-difference field derivatives — the same failure mode this project would meet
   on curvatures. Which code, and whether domains can be frozen, is a Q-gate.
4. **Where CC pays.** The hybrid-force-field literature (Bégué et al. 2005, acetonitrile:
   CCSD(T) quadratic + B3LYP cubic/quartic gives mean deviations under 0.8 %; the Barone /
   Puzzarini CC/DFT hybrid schemes) puts the high level in the **harmonic** constants and the
   cheap level in the anharmonic ones. Plan 04 had it the other way round (DFT Hessian, CC in
   the anharmonic correction). Δ-probing spends CC where that literature says it pays most —
   Δ₂ first — and only then on Δ₃/Δ₄ for the scored families. This is a change of frozen
   intent relative to plan-04 Distilled §3 and is recorded as such in `Why_05_Supersedes_04.md`.

## 5. Two levers that are *not* promised, recorded for the user's decision

- **Fragment probing.** Because Δ is short-ranged, the Δ constants around an atom can be
  probed on a capped fragment of radius r_c instead of on the whole flake; a D₆h flake such as
  C₃₈₄H₄₈-class has few symmetry-unique local environments, and its interior looks like every
  other large flake's interior. This would make the CC cost of R6 genuinely size-independent.
  It is *transfer of a local electronic-structure correction*, verified per molecule by the
  whole-molecule probes where affordable — not transfer of a spectrum. Plan 04's no-transfer
  rule was written against motif transfer of band positions (a global normal-mode property,
  measured to fail by tens of cm⁻¹). Whether the rule covers this is a **scope decision the
  user has not made**; plan 05 is written to work without it and lists it as an open decision.
- **GPU canonical CCSD(T) as the licence reference.** TeraChem's GPU CCSD(T) (arXiv:2512.01055,
  Feb 2026) reports the (T) correction for 63 atoms / >1,000 basis functions in ~8 h on one
  node. If re-timed on hardware this project can reach, the canonical-vs-local-CC licence
  check (plan-04 Q6) could run at coronene rather than stopping at benzene/naphthalene. Access
  to such a node is not a fact; it is a B3 object.

## 6. Search record (2026-09-03)

Queries run (web search, English): DLPNO-CCSD(T) analytic gradient ORCA 6; GPU-accelerated
DLPNO-CCSD(T) 2025–2026; rank-reduced / THC CCSD(T) large molecules; LNO-CCSD(T) thousand
atoms / gradients; compressive sensing anharmonic force constants / sparse Hessian recovery;
GPU4PySCF analytic Hessian performance; hybrid CCSD(T)-harmonic + DFT-anharmonic accuracy;
frozen domains / PNO smooth surfaces; Δ-learning CC−DFT locality (MOB-ML, srΔML);
Rust electronic-structure codes; 2026 anharmonic IR of large PAHs; O1NumHess; Sanders et al.
2015; "Scaling-up VPT2"; Hessian probing / Curtis–Powell–Reid; ORCA multilevel DLPNO;
PySCFAD LNO-CC; Madriaga & Crawford 2025; Kotaru et al. 2026 (MLP quartic force fields).

Landing pages or full texts actually fetched (status **OK (2026-09-03)** in the bibliography):
O1NumHess arXiv abstract and HTML; Sanders et al. via PMC; TeraChem GPU CCSD(T) arXiv
abstract; ORCA 6.1 detailed change log; ORCA 6.1.1 MP2 manual page (numerical derivatives,
`StoreDLPNOData`); Psi4 DLPNO-CCSD(T) manual page; PySCFAD LNO-CC arXiv abstract; srΔML
arXiv abstract; Kotaru et al. arXiv abstract; "Machine-learned force fields for lattice
dynamics at CC accuracy" arXiv abstract. Everything else in this note was seen in search
result snippets only and is marked **record (search 2026-09-03)** in the bibliography —
re-fetch before any scored use.

## 8. Errata and status upgrades after Round-7 Pass A (2026-09-03, same day)

This section is appended; the text above is left as written so the record of what was
searched and claimed on 2026-09-03 stays intact.

- **Atom and mode counts (§1).** Coronene C₂₄H₁₂: 36 atoms, 3N−6 = 102 modes. C₃₈₄H₄₈: 432
  atoms, 1,290 modes; "C₃₈₄H₄₈-class" species differ in size, so the count is for that formula.
- **TeraChem GPU CCSD(T) (§5).** arXiv:2512.01055 was posted in December 2025; the JPCA
  article (130(10), 2225–2237) went online 2026-02-26 (Crossref).
- **Sanders et al. (§2).** "Not extended to coupled cluster or to anharmonic constants by its
  authors" overstated what one full text can show; the correct statement is that the paper
  itself treats a DFT Hessian only and that the 2026-09-03 search found no later extension.
- **Locality (§2).** "Short-ranged in real space" is the plan's bet, supported by evidence on
  *energies* in other systems; no curvature evidence on PAHs exists in this note. Q8 exists
  because of that.
- **Status upgrades.** After Pass A issue 8 the following were fetched and their statuses in
  the bibliography raised: Crossref records for Bégué, Carbonnière & Pouchan 2005 (item 27,
  author list now verified; its numerical result remains unquoted); Ruth, Gerbig & Schreiner
  2022 (37); Fusè et al. 2024 (28); Madriaga & Crawford 2025 (30; the μE_h / >100 % figures in
  §4.3 above came from a search snippet and are **not relied on** in any frozen document);
  Nagy & Kállay 2019 (34); Welborn, Cheng & Miller 2018 (36); O1NumHess JCTC (23); Sanders
  et al. (24); Fajen et al. JPCA 2026 (26); REST (41; the "no local coupled cluster" statement
  rests on an abstract seen in a search snippet). arXiv abstracts for Zhou et al. (38; Phys.
  Rev. B 100, 184308, 2019) and GPU4PySCF (25; the abstract states a 30× speed-up over a
  32-core node and does not mention Hessians — the 84-atom/30-min figure in §3 above is a
  snippet figure, not a cite).
- **Item 27's number.** The "<0.8 %" figure in §4.4 above is from a search snippet. The
  harmonic-first allocation in plan 05 rests on the hybrid-split precedent as a *design
  choice* (item 14, plan-02 record; item 27, Crossref) and is tested by Q7's Δ₃/Δ₄ arm and
  P4(a), not justified by that number.

## 7. Honest limits of this note

- No cost in this note is a measurement of this project. The probe-count classes ("~2M",
  "~100–150") are literature figures at DFT level or arithmetic on them; plan 05 turns each
  into a timed probe before any budget cites it.
- "Nobody has done X" means "not found on 2026-09-03 with the queries above"; a Pass B
  reviewer is asked to try to falsify it.
- The locality of the *DFT-vs-DFT* Δ (usable as a zero-CC dry run of the recovery machinery
  at any size) is not the locality of the CC−DFT Δ; the dry run validates the estimator, not
  the physics.
