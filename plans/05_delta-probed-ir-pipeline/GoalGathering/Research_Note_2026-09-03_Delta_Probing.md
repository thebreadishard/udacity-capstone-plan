# Research note — Δ-probing (2026-09-03)

**Status.** Source document for plan 05. This is the record of a literature search run on
2026-09-03 in answer to one question the user asked: *what is the single most inventive way to
make the plan-04 pipeline (aromatic molecule in, infrared spectrum out, CC-anchored) fast
enough that super-large PAHs fit into roughly a year of computing, without giving up the
intended accuracy?* It is a **source**, like `AI_Chats/grok_chat_4.md` was for plan 04 — not a
plan, not a result. Every identifier below carries a verify status; nothing here is a measured
number of this project. **§§1–7 are left as written on the morning of 2026-09-03; §8 records
what the same day's two reviews corrected; §9 records what the 2026-09-04 decisions changed.**
Where they disagree, §9 wins over §8 and §8 over §§1–7.

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
combination is the proposal. *(Corrected in §8: the Concordant Mode Approach is prior art for
the diagonal part.)*

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
   local piece (Ruth, Gerbig & Schreiner 2022 learned it from few points). *(Withdrawn in §8:
   no engine exists for that split.)*
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

## 7. Honest limits of this note

- No cost in this note is a measurement of this project. The probe-count classes ("~2M",
  "~100–150") are literature figures at DFT level or arithmetic on them; plan 05 turns each
  into a timed probe before any budget cites it.
- "Nobody has done X" means "not found on 2026-09-03 with the queries above"; a Pass B
  reviewer is asked to try to falsify it.
- The locality of the *DFT-vs-DFT* Δ (usable as a zero-CC dry run of the recovery machinery
  at any size) is not the locality of the CC−DFT Δ; the dry run validates the estimator, not
  the physics.

## 8. Errata and corrections after Round-7 Pass A and Pass B (2026-09-03, same day)

Appended after both reviews; the sections above are left as written. Where they disagree,
this section wins and the frozen documents follow it.

**After Pass A (issues 8, 19):**

- **Atom and mode counts (§1).** Coronene C₂₄H₁₂: 36 atoms, 3N−6 = 102 modes. C₃₈₄H₄₈: 432
  atoms, 1,290 modes; "C₃₈₄H₄₈-class" species differ in size, so the count is for that formula.
- **TeraChem GPU CCSD(T) (§5).** arXiv:2512.01055 was posted in December 2025; the JPCA
  article (130(10), 2225–2237) went online 2026-02-26 (Crossref).
- **Sanders et al. (§2).** The paper itself treats a DFT Hessian only; the 2026-09-03 search
  found no later extension by its authors — a search result, not a claim about a decade.
- **Locality (§2).** "Short-ranged in real space" is the plan's bet, supported by evidence on
  *energies* in other systems; no curvature evidence on PAHs exists in this note. Q8 exists
  because of that.
- **Status upgrades.** Crossref records fetched for Bégué, Carbonnière & Pouchan 2005 (item 27;
  author list verified; its "<0.8 %" figure in §4.4 is from a search snippet and the frozen
  documents do not rest on it), Ruth, Gerbig & Schreiner 2022 (37), Fusè et al. 2024 (28),
  Madriaga & Crawford 2025 (30), Nagy & Kállay 2019 (34), Welborn, Cheng & Miller 2018 (36),
  O1NumHess JCTC (23), Sanders et al. (24), Fajen et al. JPCA 2026 (26), REST (41; the "no
  local coupled cluster" statement rests on an abstract seen in a search snippet). arXiv
  abstracts for Zhou et al. (38; Phys. Rev. B 100, 184308, 2019) and GPU4PySCF (25; the
  abstract states a 30× speed-up over a 32-core node and does not mention Hessians — the
  84-atom/30-min figure in §3 is a snippet figure, not a cite).

**After Pass B (issues 1–6, 8, 13):**

- **The novelty sentence of §2 is false as written.** The diagonal part of the energy-only
  recovery — high-level force constants along low-level normal modes from single-point
  energies — is the **Concordant Mode Approach** (Lahm et al., JACS 2022; Kitzmiller et al.,
  JCTC 2024, "CMA-2"; bibliography items 42–43): CCSD(T)/cc-pVTZ diagonal constants in a
  B3LYP or MP2 mode basis, off-diagonals selected by a cheap diagnostic, canonical CC,
  molecules to ~17 atoms. Computing F_CC,ii in the DFT basis and computing Δ₂,ii are the same
  measurement. Also prior art: mode-tracking (Reiher & Neugebauer 2003, item 46) for selected
  modes at high level from few gradients; and Sanders et al. also recovered Hessians from
  gradients at randomly displaced geometries, not only from columns. **What remains
  proposed:** local CC with frozen domains, pair lists and PNO counts at PAH sizes; the
  off-diagonal block of Δ₂ by banded sparse recovery from multi-mode patterns rather than one
  element at a time; the recovery licensed against direct references; and locality and K_off
  measured as a function of size. The forbidden-quotes list of the Goal now bans "never done".
- **CMA-2's own result is the strongest evidence against §2 property 3.** Diagonal-only CMA
  fails on aromatic ring modes (pyridine errors to ±28 cm⁻¹, from ring-stretch/CH-in-plane-
  rock couplings; benzene, pyrrole and furan flagged), because low- and high-level mode
  compositions differ there. The plan's structural prior is therefore **frequency-banded**
  (off-diagonals between nearby modes unpenalised), Q7 prints the diagonal-only and the full
  recovery side by side, and the dry run pairs B3LYP with a high-exact-exchange functional so
  that its Δ contains mode rotations. O1NumHess's own worst covalent case — a conjugated
  polyene, MAD 6–12 cm⁻¹ — is the same phenomenon inside a paper this note had already fetched.
- **Δ₃/Δ₄ are withdrawn from the promised set (§3, §4.4).** Energy-only 1-D and 2-D cuts give
  φ_iii, φ_iiii, φ_iij, φ_ijj and φ_iijj but **not φ_ijk**, and PAH combination-band resonances
  are φ_ijk resonances (Mulas 2018 obtains them by differencing analytic Hessians along modes).
  The hybrid-QFF literature (items 14, 27, 45) puts the CC pay-off in the quadratic constants.
  Plan 05 therefore promises Δ₂ only; a diagonal-cubic probe reports the size of the CC
  correction to φ_iii as a bonus; DFT anharmonic constants are computed on a family set closed
  under the resonance search.
- **Mode E's noise floor has a formula (§4.3).** For a diagonal Δ₂ element by central second
  differences at dimensionless step q_s, resolving a δω̃ correction needs a per-point energy
  scatter σ_E ≤ 0.82·δω̃·q_s² — 18.6 μE_h at q_s = 1, 4.7 μE_h at q_s = 0.5, 1.2 μE_h at
  q_s = 0.25 for 5 cm⁻¹ (Pass B issue 1; independent of the mode's frequency; the q_s²
  contamination is (q_s²/12)·Δ₄, not E₄, which is what makes q_s ≈ 1 admissible for a
  difference). Madriaga & Crawford (item 30, full text now read): discontinuities ~1 μE_h,
  largest 6.09 μE_h for water under field steps, and **fixing the per-pair PNO dimensions did
  not remove them**. Whether small nuclear displacements mix PNOs less violently than field
  steps is unknown; the R1 smoothness probe (naphthalene, three modes, nine points, frozen
  data, ~30 energies) measures it before the pilot note, and Q6 has thresholds (pilot-note
  item 13). Psi4 documents no domain reuse: stop 1 fires for Psi4 unless freezing is
  implemented.
- **The gradient landscape (§4.1), verified by the Pass B reviewer on 2026-09-03:** no
  local-CC(T) nuclear gradient in ORCA 6.1.1, Psi4, MRCC or Molpro PNO methods; PySCFAD AD
  gradients demonstrated to 29 atoms; canonical CCSD(T) gradients exist. **Mode E is the
  promised route; mode G is a bonus.** The "CCSD gradient + energy-only (T)" split of §4.1 has
  **no engine** (no production DLPNO-CCSD nuclear gradient either) and is withdrawn.
- **Cost model that follows.** Mode E: K = 2M + K_off local-CC energies per molecule —
  coronene ≥ 204 + K_off; K_off is the unknown and the quantity Q8(c) tests. **Whole-molecule
  R6 in mode E is ≥ 2,580 energies of a 432-atom molecule and is not promised in any branch**;
  fragment probing (§5) is the only route by which R6's CC cost stops depending on M, so the
  user's open decision 1 is made before the pilot note and decides R6's form.
- **Locality must be measured on direct blocks (§4.2).** A recovery built on a locality
  premise and scored on probes designed under it can return a local Δ₂ whose fit passes. Q8
  is therefore computed on the reference Hessian at R0–R1 and on a prior-free direct-block
  probe at R2–R3 (deck-chosen π-system pairs, four-point differences, ≈12 energies per pair),
  with an anthracene numerical Δ₂ (≈133 energies) as the cheapest dated bonus test of whether
  the C–C block is long-ranged. r_c is a measured output, not a pilot-note number.
- **The local-approximation error grows with acene length** (Altun et al. 2021, item 44:
  DLPNO absolute-energy error ≈ linear in ring count; CPS(6/7) extrapolation as remedy at 2×
  cost). Q6 has a threshold column and the deck a CPS field; if mandatory, every probe counts
  double in the classification rule.
- **Mulas 2018 used B97-1**, not B3LYP (TZ2P pyrene, 6-31G* coronene); the P2 comparison
  against line B is functional-specific. Recorded in Frozen_Lines §3 and item 6.
- **Module 05 corpus.** Seven probed CC tensors by R3 is not a deep-learning corpus. The M05
  target becomes the *support* of Δ₂ in the DFT mode basis (CMA-2's diagnostic, learned), on a
  DFT-vs-DFT corpus built from public Hessian QM9 (item 47; 41,645 ωB97x/6-31G* Hessians) plus
  recomputed B3LYP Hessians; the user may veto a DFT–DFT target (open decision 4).
- **R6's DFT Hessian is itself a B3 object** (C₃₈₄H₄₈ at 4-31G: 3,552 basis functions, ~1,300
  perturbations) unless a timed probe at the R4 species shows otherwise.

## 9. What the 2026-09-04 decisions changed (appended; wins over §§1–8 where they differ)

- **Mode E is the guaranteed route and mode G the aimed-for route** that a pre-registered side
  project builds (Side_Project_2026-09-04); §8's "mode G is a bonus" is superseded. The
  frozen-space energy code that mode E needs is main-project probe M1 under Ladder stop 1.
- **Fragment probing is a permitted method** (decision 1), used at R6 under a three-part
  measured licence (Q8 at R2–R3; coronene probed in fragments vs whole at R3; direct blocks on
  the R6 fragments); §5's "scope decision the user has not made" and §8's "open decision 1"
  are closed. Whole-molecule R6 is not promised.
- **Module 05 is adopted** (decision 4): the Δ₂-support Transformer on an aromatic-heavy
  Hessian-QM9 corpus; §8's "the user may veto a DFT–DFT target" is closed. The learned prior
  earns a licence on R2–R3 and is spent on R4–R6 (Ladder §3).
- **The R2 set** (decision 3), **all plan folders in the tree** (decision 2) and **the B2
  laptop** (decision 6) are recorded in the Goal.
- **Inheritance is not authority** (user directive): no rule of plan 04 binds plan 05 unless it
  serves the goal or rests on a measurement.
- The "O(1)" language of §2 is a description of the literature it cites; plan 05 itself writes
  no cost adjective (Goal, forbidden quotes).
