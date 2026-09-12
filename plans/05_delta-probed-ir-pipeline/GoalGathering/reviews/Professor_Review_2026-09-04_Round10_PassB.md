# Professor Review — Round 10, Pass B (did the Round-9 closures hold; attacks A–G)

**Date:** 2026-09-04. **Reviewer role:** hostile domain examiner (local coupled cluster,
vibrational spectroscopy, numerical differentiation, sparse recovery); web access used and
cited by date; anything recalled is marked so and never presented as verified. **Brief:**
[Review_Brief_2026-09-04_Round10_PassB.md](Review_Brief_2026-09-04_Round10_PassB.md).
**Read in full, in the brief's order:** Professor_Review_2026-09-04_Round10_PassA (all twenty
findings checked against today's text), plan-05 README, Overarching_Goal (glossary first),
Why_05_Supersedes_04, Research_Note_2026-09-03, Frozen_Lines_to_Beat, Frozen_Ladder_and_Tolerances,
Compute_Budget_2026-09-03, Distilled_Project_Plan_and_Quality_Checks, Relevant_Scientific_Papers,
probes/README, Capstone_Mapping, Project_Proposal_2026-09-03, Side_Project_2026-09-04_ModeG_Gradients,
then Professor_Review_2026-09-04_Round9_PassB for the twelve items of Part 1. Plans 01–04 not
opened; the Round 7–9 briefs and the other reviews not opened except to trace a constant.
Issues are numbered 1–N continuously across the blocking and non-blocking lists.

(File written incrementally; sections below are appended as the reading proceeds. If the file
ends without the line "Pass B complete", the review was cut off and what stands is partial.)

**Round-10 Pass A closure check (its 20 findings).** All twenty are in today's text: 1 (ΔE(0)
"one shared reference energy per rung … the recovery carries a fitted constant that absorbs it",
σ(R_s) = σ_E/√2, ρ_noise = σ(R_s)/RMS_resp — Ladder §3, Distilled §3, glossary); 2 (K in energies,
"ρ(n) is evaluated after each complete pair", K_off ≥ 2, probes README 1 "K in energies, a ± pair
counting 2, exactly as probe 6"); 3 (the pair is the hold-out unit with one deck index — glossary,
Ladder, Distilled); 4 ("the pooled σ gates", per-mode 2× flag, q_s one number per rung and mode —
Ladder amplitude bullet, Budget §4.5, README 5); 5 (row 31 restored); 6 (Mapping M08 "R0
unconditionally … R1–R3 per family"; root README checked below); 7 (anthracene direct-coupling
probe, 180 for nine pairs × five families, 8,713 stated as what a full Δ₂ would cost — Budget §4.9,
README 9, Proposal §8); 8 (status lines; the Distilled file's *second* status paragraph still ends
at "Round-8 Pass A and Pass B" while its header line says Round-10 — a residue, non-blocking 14);
9 (72 × families ≈ 360, "the expectation, not a verdict"); 10 ("r_f + one shell" in README 15);
11 (the 1 cm⁻¹ term "likewise recalled", the no-temperature default written); 12 (items 54–56,
"R0 is expected unconditional" in Ladder §2 — but the Goal's prime directive still says
"unconditional on R0" without "expected"; the Goal wins on drift, so the Ladder's hedge is the
one that should be checked against it, non-blocking 14); 13 (Δ₁·p "recalled order of magnitude …
the R_a by-product measures it"); 14 (glossary entries present; σ_E entry now √(SSR/(n − p))
pooled); 15 ("passed", "by the shell rule"); 16 (Proposal §5.3 "in addition", §8 expected outcome
and u_band re-read, §9 extended — but §7's "seven inputs" still lists "the opponent side" and not
the R0 pilot, so it is still not Budget §4's seven, and §11 risk 7 still reads "an four-weekly";
non-blocking 14); 17 (M2 Cartesian 72; M4 run/no-run); 18 (item 20 → 52–53; note §9 erratum
re-pointed at "the Round-8 Ladder text"); 19 (61 / 72 / 1,801 with arithmetic); 20 (ρ\*_common
column NOT_RUN until Q8(c)). Eighteen closed cleanly, two (8, 16) with small residues listed under
non-blocking 14.

---

**Verdict: conditional — in two scopes, all conditions in-spec.**

- **R0–R1 and the pre-pilot-note programme: green light once blocking findings 1–4 are written
  in.** None needs a measurement first. They are: the noise-injected dry run must inject noise per
  *energy*, not per response (or c and K_cap are read at a σ that is √2 off the real run's); the
  "fitted constant" that is said to absorb ΔE(0)'s offset is unidentifiable at a single pattern
  amplitude and turns the offset into a same-sign shift of every recovered frequency; the
  first-order term Δ₁ the symmetrisation discards is physics the scored spectrum carries (the
  Hessian is taken at the DFT minimum, not at the corrected surface's minimum — a 0.5–2 cm⁻¹-class
  per-band term that no error-budget line names); and a room-temperature, 0.1 cm⁻¹ gas-phase
  naphthalene spectrum *does* exist outside the WebBook (PNNL, opened today), so R1's scoreboard
  must name it before M03 prints u_band — under the plan's own no-swap rule it cannot be added
  after scoring.
- **R2–R3: green light under the same four.** Nothing the Round-9 closures introduced re-breaks
  the R2–R3 conditions of Round 9 (finding 5 held; the fragment licence and decidability closures
  held).
- **The promised set beyond R3 (R4 checks, fragment-probed R6): green light as worded, conditional
  on B3 exactly as the plan already says.** The Round-9 condition (its finding 4) held; what I
  expect — C–H and CH-oop earnable at coronene on edge pieces, the C–C families pending (b′) and
  hence B3 — is a measurement the plan is now written to report honestly (non-blocking 16–17).
  Blocking 3's error-budget term applies on every rung, R6 included.

---

## Part 1 — Round-9 closures

1. **Symmetrised response — closed.** Ladder §3: "Every pattern p enters the Q0 deck as the pair
   ±p, and the mode-E response is the symmetric combination R_s(p) = ½[ΔE(+p) + ΔE(−p)] − ΔE(0) =
   ½ pᵀΔ₂ p + O(p⁴) … K counts energies in mode E (a ± pair counts 2) … ρ, RMS_resp and ρ_noise are
   defined on R_s"; Budget §4.1 "Responses are the symmetric combinations R_s over ± pairs exactly
   as in the real run"; identical in the glossary, Goal step 2, Distilled §3, probes README 1/6. All
   four sub-requests of Round 9 (i)–(iv) are in. What the closure introduced — the unidentifiable
   "fitted constant", the quartic term, the dry run's noise placement, and the Δ₁ by-product's
   physics — is Part 2 A.
2. **Frozen space by projection — closed.** Ladder §3: "both halves are transported by projection,
   and nothing is re-localised or assigned: the occupied set is C_occ(x) = Löwdin[P_occ(x) C_occ(0)]
   … the stored virtual-space vectors are likewise projected … and Löwdin-orthonormalised"; M1 prints
   "the continuity diagnostics — the smallest singular value of the occupied overlap S_oo(x) … and
   the largest off-diagonal of the pre-Löwdin overlap, for both halves"; mirrored in the glossary
   ("re-projected"), Budget §4.2, probes README 2, side project §1.2/§2/M1/§7. No permutation or
   maximal-overlap survivor outside the historical record lines. Attacked in Part 2 B.
3. **R0-only unconditional, the floor, items 52–53 — closed.** Goal prime directive: "unconditional
   on R0 … on R1–R3 per family"; Ladder §2: "R1 is per family under the same rule as R2: naphthalene's
   only NIST gas spectra are a 245 °C Coblentz vapour spectrum and a GC-IRD entry … at χ_max the
   unpinned temperature floor is ≈ 7–8 cm⁻¹, above τ"; the floor "u_T ≥ χ_max·(T_source − 296 K)
   + 1 cm⁻¹ … χ_max = 0.03 cm⁻¹ K⁻¹ (recalled …)"; "items 52–53 — the first paid debt" in Ladder §2,
   Why_05 row 28, Method debts, README. M03 prints source class, temperature and resolution as
   columns (Round 9 (iv)). The plan chose a *different* floor form from the one Round 9 offered
   (χ_max·(T_source − 296 K) + 1 cm⁻¹ instead of |χ_max|·T_source, i.e. ≈ 7.7 rather than
   ≈ 15.5 cm⁻¹ at 518 K); both are above τ, the expected verdict is unchanged, and the plan's form is
   the physically better one *except* for the size of the room-temperature term — Part 2 C(i),
   non-blocking. Closed.
4. **Fragment written once; (b) one comparison at one shell; pending (b′); (c) classified —
   closed.** Ladder §3: "The fragment, written once: ring-closed, hydrogen-capped, carved unrelaxed
   from the rung's DFT geometry, its radius counted in ring shells … (b) is one comparison at one
   shell for interior pairs … If one shell fails, the two-shell hypothesis is untestable at coronene
   and the licence is pending (b′) … (c) is a probe batch like any other: its energy count is
   printed (… 72 × families; ≈ 360 for five families …) and it is classified by Budget §2's rule";
   Distilled §8 carries the pending sentence; Budget §4.12–13 and README 13–15 agree. Closed.
5. **Q8(c) at a common threshold — closed.** Ladder §1: "both counts read from the rungs' stored
   ρ(n) curves at the common threshold ρ\*_common = max(ρ\*(R_n), ρ\*(R_{n+1}))"; Ladder §3 Q8(c),
   Distilled Q8, README 12 identical; glossary entry added. Closed; the choice of axis is Part 2 E.
6. **σ = √(SSR/(n − p)), pooled, studentised residuals — closed.** Ladder §3: "σ_E = √(SSR/(n − p))
   of ΔE(q) about a least-squares polynomial of degree 4 (n = 9 points, p = 5 coefficients, ν = 4 per
   mode — never √(SSR/n) …) … One σ per freezing arm, pooled over the four modes (ν = 16 in mode E)
   … Studentised residuals are printed per point and |r| > 2.5 is flagged"; Distilled Q6 and README 5
   agree; the Round-10 Pass A ambiguity about what gates is resolved ("the pooled σ gates"). Closed;
   pooling is Part 2 F.
7. **M2–M5 at nine gradients per Q6 mode, σ_g pooled over 3N, M4/M5 classified — closed.** Side
   project M2 "nine gradients per Q6 mode (36), σ_g = √(SSR/(n − p)) pooled over all 3N components";
   M3 "(36 gradients)"; M4 "nine gradients per Q6 mode (36) … classified by Budget §2"; M5 the same
   "B3 by expectation"; Budget §4.11–12, README 12–13, Ladder §3 estimator ("pooled over all 3N
   Cartesian components … ν = 5·3N"). Closed; the B3 question is Part 2 G(i).
8. **M1's raw displaced energies sealed — closed.** Ladder §3: "M1's raw displaced energies are not
   printed: they go to the same hashed, sealed file as the R1 fit coefficients"; Budget §4.2, README 2,
   side project M1 ("raw energies sealed"). Closed.
9. **One canonical gradient; expected outcome; DZ lower bound — closed.** Ladder §3: "also runs one
   canonical CCSD(T) gradient of benzene (PySCF ships `pyscf/grad/ccsd_t.py` …) so the
   gradient-to-energy factor is measured, not typed … The expected printout, written now so it is
   not a contingency: the bias line fits and the full reference does not. A bias line measured in
   cc-pVDZ is a lower bound on the cc-pVTZ freezing bias … 'beat' language from the TZ arm requires
   the DZ bias ≤ τ/2"; Budget §4.1b and README 1b agree. Closed; whether that one gradient fits the
   laptop at all is Part 2 G(ii).
10. **Distance classes by bond count with S_class — closed.** Ladder §3: "three classes by bond
    count — near = bonded, mid = two or three bonds apart, far = four or more — with an equal frozen
    count per class … the probe prints S_class, n_class, σ_coupling and the class windows"; Distilled
    Q8 and README 12 identical. (Round 9 wrote "far = five or more"; the plan's "four or more" leaves
    no gap between the classes and is the better choice.) Closed.
11. **Goal item 1 (c) carries the r_f rule — closed.** Goal "The goal binds" item 1 (c): "r_f is the
    R3 value from (b), or (b′)'s if larger; run once, the passing radius printed in the certificate;
    a probe batch classified like any other". Closed.
12. **Diagonal-cubic bonus as two extra energies per mode — closed.** Goal: "from the antisymmetric
    combinations of the single-mode ± block plus one further amplitude: two extra energies per
    mode"; Distilled §3 and README 6 identical. Closed.

**Tally: 12 closed, 0 re-worded, 0 open.** Three closures (1, 2, 3) are design changes and are
attacked below on what they introduced; attacks A and C land (blocking 1–4).

---

## Literature and software facts opened this pass (how; date 2026-09-04)

- **PNNL / JQSRT 2024** — Schneider, Baker, Scharko, Blake, Tonkyn, Forland, Johnson, "A method
  for generating quantitative vapor-phase infrared spectra of solids: results for phenol, camphor,
  menthol, syringol, dicyclopentadiene and naphthalene", J. Quant. Spectrosc. Radiat. Transfer
  **323**, 109045 (2024), DOI 10.1016/j.jqsrt.2024.109045. Abstract read on the OSTI landing page
  (osti.gov/biblio/2477598); the OSTI full-text PDF (osti.gov/servlets/purl/2477598) downloaded and
  text-extracted by me: "a composite spectrum is generated from typically ten or more 760-Torr
  pressure-broadened spectra over the 600 to 6500 cm⁻¹ spectral range at 0.1 cm⁻¹ spectral
  resolution"; "the White cell thermostatted at 25 °C" (general procedure; the two 50 °C runs
  named in the text are syringol and menthol); naphthalene "analyzed only in CS₂"; "(naphthalene,
  phenol, syringol and menthol) are already found in the" PNNL/NWIR gas-phase database, and the
  paper's ref. [2] (Sharpe et al. 2004, Appl. Spectrosc., the PNNL database paper, 5/25/50 °C,
  ≈ 500 molecules — Sage landing page seen in search) is cited for naphthalene's existing entry.
  **Grade: full text opened; the naphthalene-specific cell temperature is 25 °C by the paper's
  general procedure statement — M03 confirms it against the paper's table and the database record
  before u_band is printed.**
- **Pirali, Vervloet, Mulas, Malloci, Joblin, PCCP 11, 3443 (2009)** — RSC page 403; Crossref record
  (api.crossref.org) confirms title/authors/venue/pages 3443–3454, no abstract field. Search-snippet
  grade for content: "naphthalene absorption in the 1.6–200 μm spectral range with a resolution of
  0.005 cm⁻¹, and the spectrum at room temperature shows complex structures in the Q branches of
  c-type bands assigned to hot-band sequences" — i.e. a **room-temperature (and heated) cell study
  at high resolution**, not a jet, with room-temperature band centres of the c-type (CH-oop)
  bands and anharmonic parameters for the hot-band sequences.
- **Joblin, Boissel, Léger, d'Hendecourt, Défourneau, A&A 299, 835 (1995)** — ADS abstract page
  returned 405 to me as to the author. Content at second hand only: the 3.3 µm review
  (arXiv:2107.09189, search result) describes it as 1 cm⁻¹ spectra of the 3.3 µm band of
  naphthalene, pyrene, coronene and ovalene over ≈ 400–900 K with near-linear position and width
  slopes; Chakraborty, Mulas, Rapacioli, Joblin (arXiv:2102.06582, **HTML full text opened**)
  Table 3 quotes the gas-phase experimental slopes for pyrene at 573–873 K as **χ′(3.3 µm) =
  −2.5 × 10⁻² cm⁻¹ K⁻¹ and χ′(11.8 µm CH-oop) = −1.4 × 10⁻² cm⁻¹ K⁻¹**, and its own DFT
  anharmonic result over 300–523 K as −0.1 × 10⁻² for the 3.3 µm band — "non-linear behavior at
  low temperatures". The plan's snippet "≈ −0.02 for a C–C stretch" is consistent with these; I did
  not see a naphthalene 6.2/7.7 µm slope from the 1995 paper anywhere I opened.
- **Chakraborty, Mulas, Demyk, Joblin, J. Phys. Chem. A 2019, DOI 10.1021/acs.jpca.8b11016**
  (PMC6557715, full text opened): pyrene from 14 to 723 K in **KBr pellets** (condensed phase, not
  gas), 0.2 cm⁻¹; χ′ (10⁻² cm⁻¹ K⁻¹) −1.4 (1433.6), −0.7/−0.8 (1184.8), −0.6 (1096.3), −1.1
  (839.9), −1.6 (749.4). Condensed-phase numbers — context only; they bound the same order.
- **Maltseva, Petrignani, Candian, Mackie, Huang, Lee, Tielens, Oomens, Buma, ApJ 831, 58 (2016)**
  (IOPscience abstract opened): jet-cooled IR–UV ion-dip spectra, 2950–3150 cm⁻¹, "resonance band
  widths down to 1 cm⁻¹", for phenanthrene, **pyrene, benz[a]anthracene, chrysene, triphenylene**,
  perylene — a **cold gas-phase C–H-stretch source for the whole R2 gas set**, which the plan does
  not name.
- **pyscf-forge `pyscf/lno/lno.py`** (raw GitHub, opened): `def __init__(self, mf, lo_coeff,
  frag_lolist, lno_type=None, lno_thresh=None, frozen=None)` — the localized occupied orbitals are
  an **input**; no localiser is called in the class. Per-fragment LNO spaces are built inside
  `make_las()` on every `kernel()` call ("Projection of LO onto occ and vir" → `make_lo_rdm1_occ`,
  `make_lo_rdm1_vir` → `natorb_select()`); no attribute stores or accepts pre-built LNO vectors;
  `impurity_solve(self, mf, mo_coeff, uocc_loc, eris=None, frozen=None, log=None)` takes explicit
  orbitals but is called after `make_las`.
- **PySCF `pyscf/grad/ccsd_t.py`, `pyscf/cc/ccsd_t_rdm.py`, `pyscf/cc/ccsd_t_lambda.py`** (raw
  GitHub, opened): the gradient imports `ccsd_t_rdm` and `grad.ccsd`, uses `_gamma2_outcore` with
  `lib.H5TmpFile()`; both the (T) lambda and (T) rdm codes **block over virtual triples** with
  `blksize = min(nvir, int(((max_memory*0.9e6/8)/6.0/(nocc**3))**(1/3)))` and allocate
  `w_blk, v_blk = numpy.empty((blksize, blksize, blksize, nocc, nocc, nocc))` — no full o³v³
  array.
- **Root `README.md`** line 34 now reads "(benzene, naphthalene — plan 05: benzene only, naphthalene
  per family)" and line 79 "benzene unconditionally, naphthalene and the larger accuracy rungs per
  family" — Round-10 Pass A issue 6 closed there too.

*Recalled, not opened (verify-on-use):* dimensionless-normal-coordinate conversions
(q = 1 ↔ 0.116 bohr for a 1,500 cm⁻¹ mode of reduced mass 6 u; 0.2 bohr for a 3,050 cm⁻¹ C–H
stretch); typical diagonal quartic constants φ_iiii of 10–30 cm⁻¹ (C–C) and ≈ 100–150 cm⁻¹ (C–H)
and cubic φ_iij of 20–100 cm⁻¹ in dimensionless units; the 0.001–0.003 Å B3LYP-vs-CCSD(T) bond-length
difference (Round 9's recall); naphthalene's low-frequency modes (≈ 166, 176, 359, 386 cm⁻¹) and
benzene's (398 e₂u, 606 e₂g); µE_h-class geometry dependence of DFT quadrature errors on default
grids; χ²₄ quantiles; benzene/cc-pVTZ counts (264 functions, 15 active occupied).

---

## Blocking findings

### 1. The noise-injected dry run adds noise to the *response*, but c and K_cap are read at σ_E, the per-*energy* scatter — a √2 mismatch built into the two numbers the stopping rule depends on
**Where:** Budget §4.1: "the same recoveries with Gaussian noise at a grid of σ values added to
every response, K and ρ printed per σ — the column the stopping constant c and K_cap are taken
from"; Distilled §3 "Dry run": "Gaussian noise at a grid of σ values … added to every dry-run
response"; probes README 1: "Gaussian noise at a grid of σ added to every response"; Ladder §4
item 8: "read off the noise-injected dry run's K-vs-σ curves — for mode E at the σ_E the R1
smoothness probe printed"; item 9 "at the same σ per mode as item 8".
**What.** Round 10 Pass A closed σ(R_s) = σ_E/√2 (ΔE(0) a shared reference). The real run's
response noise is therefore σ_E/√2 per R_s. The dry run injects σ per *response* and its column is
read at σ = σ_E: the recovery whose c and K_cap are frozen was run at a response noise 1.41× the
real one. K_cap errs on the large side (harmless as a cap); c does not err in a known direction —
c is the ratio ρ\*/ρ_noise at which the noise-injected recovery is judged faithful, and the shape of
the K-vs-σ curve moves with σ. Worse, injecting independent noise into every R_s never tests the
one thing the Pass A closure asserts — that a *shared* ΔE(0) error is absorbed by a fitted constant
(blocking 2) — because the dry run never has a shared error.
**Why it matters.** c and K_cap are pilot-note items 8–9, frozen before any local-CC number exists
and never raised; they are read from this column and nowhere else.
**What would close it (in spec; one sentence in three files).** "Noise is injected per energy:
ε(+p), ε(−p) ~ N(0, σ_E²) independently for every displaced energy, and one ε₀ ~ N(0, σ_E²) per
dry-run molecule for the shared reference, drawn once; R_s is formed from the noisy energies; the
column is indexed by σ_E and read at the R1 probe's σ_E. In mode G, ε ~ N(0, σ_g²) per gradient
component." Budget §4.1, Distilled §3, probes README 1.

### 2. The "fitted constant that absorbs ΔE(0)'s offset" is unidentifiable when every pattern has the same amplitude: the offset becomes the same-sign shift δω = δE₀/q_s² of every recovered frequency — a fake scale factor of up to τ
**Where:** Ladder §3: "ΔE(0) is one shared reference energy per rung, computed once; its scatter is
a common offset to every R_s, not per-pattern scatter, and the recovery carries a fitted constant
that absorbs it"; Distilled §3 "Responses": "ΔE(0) is one shared reference per rung whose offset the
recovery's fitted constant absorbs"; Ladder §3 amplitude bullet: "q_s is one number per rung and
per mode E/G"; Distilled §3 "Patterns": "the 2M single-mode ±q_s energies … followed by ± pairs of
simultaneous multi-atom displacements" (no second amplitude for the multi-atom block).
**What — the algebra.** Let the shared error be c₀. Every response reads R_s(p) = ½ pᵀΔ₂ p + c₀.
For a pattern of norm |p|² = q_s² in the normal-coordinate metric, ½ pᵀ(Δ₂ + λI)p = ½ pᵀΔ₂ p +
½ λ q_s²: the design-matrix column of "a constant" equals ½ q_s² times the column of "add λ to every
diagonal element". With one amplitude per rung and mode the two are exactly collinear; a solver
that carries a constant cannot separate them, and a solver that does not (the banded prior
penalises only out-of-band off-diagonals; the diagonal is free) puts c₀ into the diagonal. The
result is Δ₂,ii → Δ₂,ii + 2c₀/q_s² for every i, i.e. every harmonic frequency shifts by δω =
c₀/q_s² in the dimensionless-coordinate convention (V = ½ ω q²; a frequency change δω is the
response δω·q², so ½Δ₂,ii ↔ δω). Numbers: at q_s = 1, c₀ = σ_E = 5 µE_h gives δω = 1.1 cm⁻¹ on
every band, same sign; c₀ at the q_s = 1 noise line's ceiling (18.6 µE_h at τ = 5 cm⁻¹) gives
4.1 cm⁻¹ — the whole beat margin, on every band, looking exactly like a scale-factor error. What
ΔE(0)'s "noise" physically is: at the reference geometry the frozen spaces *are* the fresh spaces
(M1's 10⁻⁹ E_h round trip), so the projection artefact is zero there; what remains is one draw of
the per-evaluation SCF/CC convergence and DFT-grid noise. Small — but one draw, unbounded by
averaging, and the plan currently says it is "absorbed".
**Why it matters.** The Round-10 Pass A closure of σ(R_s) rests on this constant; Q7's per-family
RMS test at τ₇ ≈ 5 cm⁻¹ would pass a uniform 1–4 cm⁻¹ shift; and P2's calibrated-harmonic opponent
is exactly a fitted scale — a same-sign bias on every band is the one error that costs the
pipeline its beat on every family at once.
**What would close it (in spec; zero cost).** Pick one and write it in Ladder §3 and Distilled §3:
(a) **identify the constant from the second amplitude the diagonal-cubic bonus already buys**: on
every scored family's mode the block has R_s at q_s and at q₂, and Δ₂,ii = 2[R_s(q₂) − R_s(q_s)]/
(q₂² − q_s²) is independent of c₀, so c₀ = R_s(q_s) − ½Δ₂,ii q_s² is over-determined (one unknown,
several modes) and is subtracted from every response before the recovery — printed in the cost
record beside σ; or (b) declare ΔE(0) exact to the deck's convergence thresholds (SCF, CC, grid — all
deck numbers), drop the constant, and print the bound δω ≤ δE₀/q_s² from those thresholds in the
error budget; or (c) give the multi-atom block two norms. The dry run of blocking 1 (with its ε₀
draw) then tests whichever is chosen.

### 3. Δ₁ is not merely a by-product: the recovered Δ₂ is the Hessian correction *at the DFT minimum*, and the corrected surface's own minimum is elsewhere — a first-order term ½Σ_j φ_iij δq_j of 0.5–2 cm⁻¹ per band that no error-budget line names
**Where:** Goal glossary: "Δ₁ = the CC−DFT gradient at the DFT equilibrium geometry (not zero; a
by-product, never a geometry correction)"; Ladder §3: "R_a(p) … = Δ₁·p + O(p³) is a free by-product
(Δ₁ from the single-mode block …)"; Goal step 4 "Error budget: every claimed band carries its
measured error sources — DFT level; ρ; local-CC noise floor and space-freezing bias …; the
long-range share …; matrix–gas shift" (no geometry term); Distilled §3 anharmonic routes ("GVPT2
on DFT anharmonic constants with the Δ₂-corrected harmonic part").
**What — the physics.** The symmetrisation removes Δ₁·p from the *response*; it does not remove
Δ₁ from the *spectrum*. The pipeline's corrected surface is V_DFT + Δ near the DFT geometry x₀;
its minimum is displaced by δq_j = −Δ₁,j/(ω_j + Δ₂,jj) along the totally symmetric modes (Δ₁ is
totally symmetric by symmetry). The harmonic force constants of that surface at its own minimum
differ from those at x₀ by k_ii(q_min) − k_ii(0) = Σ_j φ_iij δq_j, i.e. a frequency shift ≈ ½ Σ_j
φ_iij δq_j per band, with φ_iij the (DFT-level, to first order) semi-diagonal cubic constants
between band mode i and totally symmetric mode j. Numbers (recalled scales, marked above): a
0.002 Å B3LYP-vs-CC C–C bond-length difference is δq ≈ 0.03–0.04 on a ring-breathing coordinate
(q = 1 ↔ ≈ 0.1 bohr for a 1,000 cm⁻¹, 12 u mode); φ_iij of 20–100 cm⁻¹ gives ½·φ·δq ≈ 0.3–2 cm⁻¹
per coupled totally symmetric mode; two or three such modes per band give **0.5–2 cm⁻¹, systematic
per family** — the same order as the ≈ 5 cm⁻¹ correction the plan is trying to resolve and above
the ~1 cm⁻¹ bind. Every hybrid-QFF precedent the plan cites evaluates the high-level quadratic
constants at a consistent reference; whether CMA (items 42–43) displaces from the low-level or
the high-level geometry I could not verify today and do not claim.
**Why it matters.** Goal, forbidden quotes: "Any band position without its measured error source
named." This one is unnamed, is of the size that decides P2, and is *free to compute*: Δ₁ per mode
comes out of R_a of the single-mode block at no extra energies, and the DFT cubics are already
computed for the resonance-closed set (adding the totally symmetric modes to that set costs
2 × n_TS DFT Hessians per molecule — nine a_g modes at naphthalene, laptop work through R3). The
glossary's "never a geometry correction" is a policy with no stated reason; under the user's own
directive (inheritance is not authority) a rule with no reason does not bind.
**What would close it (in spec).** One paragraph in Ladder §3 and Distilled §3, mirrored in Goal
step 4: either (a) **apply the first-order relaxation** — the scored harmonic part is Δ₂ +
Σ_j φ_iij^DFT δq_j with δq_j from Δ₁ (printed per mode), labelled "corrected-surface minimum,
first order", and the Goal's glossary entry drops "never a geometry correction" for "applied only as
the printed first-order term"; or (b) **keep the DFT reference and carry ½Σ_j φ_iij δq_j per scored
band in the error budget**, printed with the cost record. In both cases Δ₁ per totally symmetric
mode is printed — the brief's "diagnostic of the DFT geometry's quality", and worth having for
that reason alone — with one sentence that no atom is moved by it unless (a) is the rule. The
resonance-closed family set gains the totally symmetric modes (item 7).

### 4. A room-temperature, 0.1 cm⁻¹ gas-phase naphthalene spectrum exists outside the WebBook (PNNL/NWIR; JQSRT 2024) — R1 can be scored as R0 is, and the plan's own no-swap rule means the source must be named *before* M03 prints u_band
**Where:** Ladder §2 R1 row: "NIST gas — hot sources only: a Coblentz vapour spectrum at 245 °C …
and a NIST MS Data Center GC-IRD entry; no room-temperature gas spectrum is listed"; decidability
paragraph: "R1 is per family under the same rule as R2 … R1's C–C families are expected inconclusive
by construction unless a hot-band correction is pinned before the note"; Frozen_Lines §5 scoreboard
table (NIST WebBook only for gas); Frozen_Lines preamble: "After a comparison against a line has
been scored, that line may not be swapped, re-versioned, or reweighted"; Proposal §13.3.
**What — opened today.** Schneider et al., JQSRT 323, 109045 (2024; DOI
10.1016/j.jqsrt.2024.109045): quantitative vapour-phase spectra of six moderately volatile solids
**including naphthalene**, "760-Torr pressure-broadened … 600 to 6500 cm⁻¹ … at 0.1 cm⁻¹ spectral
resolution", White cell "thermostatted at 25 °C" (the general procedure; only syringol and menthol
are named at 50 °C), naphthalene "analyzed only in CS₂"; the paper says naphthalene, phenol, syringol
and menthol "are already found in the" PNNL/NWIR database and cites Sharpe et al. 2004 for the
existing naphthalene entry. So a 25 °C composite spectrum at 0.1 cm⁻¹ with stated conditions exists,
with N₂ pressure broadening (which shifts band centres by far less than the hot-band term; the
paper's stated accuracy is for intensities, and M03 must take the position uncertainty from the
resolution and the composite's centroid scatter). Second source: Pirali et al. 2009 (item 53) is a
**room-temperature high-resolution (0.005 cm⁻¹) cell** study (snippet grade), which gives the c-type
CH-oop band centres and the anharmonic parameters that pin χ_F for the Coblentz 245 °C entry — item
53 is therefore *both* a room-temperature scoreboard entry for the CH-oop family and the hot-band
pin, and the plan currently lists it only as the latter. Third, for R2: Maltseva et al., ApJ 831,
58 (2016) — jet-cooled 3 µm spectra of **pyrene, chrysene, triphenylene** with band widths down to
1 cm⁻¹ — a cold gas-phase source for the C–H-stretch family of the entire R2 gas set. For pyrene
in the 6–15 µm region I found nothing at room temperature (its vapour pressure is far below the
PNNL method's reach; the WebBook's pyrene gas entry is the GC-IRD one the plan already grades hot):
**the R2 C–C expectation stands.**
**Arithmetic.** On the PNNL entry u_band(R1) = √(0.1² + centroid² + u_T(296 K)²) with u_T(296 K) ≈
1–2 cm⁻¹ (non-blocking 5) → ≈ 1–2 cm⁻¹ < τ ≈ 5 cm⁻¹ for every family: R1 is **expected unconditional**
on that source, exactly as R0 is, without any pinned correction; the Coblentz 245 °C entry becomes
a second, hot column.
**Why it matters.** Two ways. (i) Left as is, M03 prints "inconclusive by construction" for R1's
6.2/7.7 µm families and the pilot note freezes that; the plan then cannot add PNNL later without
breaking "never swapped … after a comparison has been scored" — a false refusal locked in by the
plan's own honesty rule. (ii) The Round-9 verdict's R0–R1 green light was narrowed to "R0 only
unconditional" on the belief that no such spectrum existed; that belief was a WebBook-only search.
**What would close it (in spec; before M03).** Bibliography items 57 (Schneider et al. 2024, DOI
above, full text to be read by the author; the NWIR naphthalene record and its stated temperature
and resolution) and 58 (Maltseva et al. 2016), and item 53 re-labelled as a room-temperature
source as well as the hot-band pin; Frozen_Lines §5 scoreboard gains "PNNL/NWIR quantitative
vapour-phase database (25 °C, 0.1 cm⁻¹, 760 Torr N₂) — naphthalene" and "jet-cooled 3 µm
(Maltseva 2016) — pyrene, chrysene, triphenylene, C–H stretch only"; Ladder §2 R1 row: "room-
temperature cell spectrum exists (item 57); R1 expected unconditional on it; the Coblentz 245 °C
and GC-IRD entries scored as labelled hot columns"; probes README 2a reads the PNNL record's
conditions as it does item 56's; Proposal §5.2/§13.3 updated (the supervisor ask now concerns R2's
6–15 µm region only). None of this is a measurement; all of it must precede the note.

---

## Non-blocking findings

### 5. The temperature floor: χ_max = 0.03 bounds every gas-phase slope I could find, the linear-from-296 K form is *conservative* (low-temperature slopes are smaller, not larger), but the "+1 cm⁻¹" room-temperature term is benzene's and under-reads naphthalene and everything larger
**Where:** Ladder §2: "u_T ≥ χ_max·(T_source − 296 K) + 1 cm⁻¹, for a room-temperature source u_T ≥
1 cm⁻¹ … the 1 cm⁻¹ room-temperature term likewise recalled (the Round-9 reviewer's benzene
estimate)"; probes README 2a.
**What.** (i) Bound: the gas-phase pyrene slopes quoted from Joblin 1995 by Chakraborty et al. 2021
(Table 3, 573–873 K) are −0.025 (3.3 µm) and −0.014 cm⁻¹ K⁻¹ (11.8 µm oop); the plan's snippet gives
≈ −0.02 for a C–C stretch; the KBr-pellet pyrene numbers (Chakraborty 2019) are −0.006 to −0.016.
χ_max = 0.03 is an upper bound on all of them. (ii) Linearity: the same 2021 paper's anharmonic
calculation gives −0.001 cm⁻¹ K⁻¹ for the 3.3 µm band over 300–523 K against −0.025 measured at
573–873 K — "non-linear behavior at low temperatures": the shift grows with vibrational energy
content, which is *sub*-linear in T below ≈ 500 K. Extrapolating from 296 K to 518 K at the
high-temperature slope therefore over-estimates the 296→518 K shift; the floor is conservative
there. (iii) The 0→296 K term: for benzene (lowest mode 398 cm⁻¹, ≈ 0.17 quanta ×2 at 296 K) the
Round-9 estimate of −0.5 to −1 cm⁻¹ is fair. Naphthalene has modes at ≈ 166 and 176 cm⁻¹ (≈ 0.8
quanta each at 296 K) and ≈ 2.5 thermal quanta in all — roughly 800 cm⁻¹ of vibrational energy
against benzene's ≈ 300 — so its 0→296 K shift is ≈ 2–3× benzene's: ≈ 1.5–2.5 cm⁻¹ for a C–C band
(recalled scales; an estimate, not a number). Pyrene and coronene, with more low modes, are larger
again. On the PNNL source (blocking 4) this term *is* u_T, so it now decides R1's C–C margin.
**Close.** "+ u_296(molecule)" in place of "+ 1 cm⁻¹", with u_296 = 1 cm⁻¹ at benzene and, until
items 52–53 pin it, 3 cm⁻¹ at naphthalene and 5 cm⁻¹ at the R2 species (labelled recalled
estimates; replaced on fetch by χ_F·E_vib(296 K)/C_v or the pinned paper's own room-temperature
number). Still < τ at R1 on the 0.1 cm⁻¹ source.

### 6. pyscf-forge's LNO class takes the localized occupied set as an input but rebuilds every fragment's LNO space on every call — M1's virtual half needs a code change, and the "fresh" arm should be split in two
**Where:** Ladder §3 frozen-space object; probes README 2 ("stores fragment list, localized orbitals
and LNO vectors … transports the occupied and the virtual vectors by projection"); Budget §4.2;
side project §1.3 ("M1 tests whether they can be stored, projected and reloaded").
**What — opened today.** `lno.py`: `__init__(self, mf, lo_coeff, frag_lolist, lno_type=None,
lno_thresh=None, frozen=None)` — `lo_coeff` "AO coefficient matrix of localized orbitals (must span
occupied space)"; no localiser inside the class. So the **transported occupied set C_occ(x) can be
passed as `lo_coeff` with the reference `frag_lolist` unchanged — the occupied half of the frozen
space is available without touching the code.** The virtual half is not: `kernel()` calls
`make_las()` per fragment, which projects the LO onto occ/vir, builds `make_lo_rdm1_occ/vir` and
runs `natorb_select()` — re-derived every call, no attribute to supply or cache the LNO vectors;
`impurity_solve(self, mf, mo_coeff, uocc_loc, …)` takes explicit orbitals but is reached only after
`make_las`. M1 therefore has to override `make_las` (return the stored, projected, Löwdin-
orthonormalised `orbfrag` and its frozen indices) or call `impurity_solve` directly with the
transported orbitals — a small subclass, whose commit hash the deck pins. Answering B(ii): the API
accepts an external occupied set; it does not accept external LNO vectors.
**The arms (B(iii)).** Because `lo_coeff` is an input, a third column costs nothing: **A** =
frozen–frozen (the probe object); **B** = transported LMOs + fresh LNO spaces built on them
(`make_las` as released, `lo_coeff` = C_occ(x)) — freezes the occupied half only, so E(A) − E(B) is
the virtual-freezing bias in isolation; **C** = fresh localiser + fresh LNO (the production LNO
energy, with the localiser's functional value and its overlap with C_occ(x) printed as the plan
already asks). On the D₆h rungs E(C) carries the localiser's landing; E(B) does not. M1 prints all
three; the Q6 "without frozen spaces" arm at R1 should be **B**, not C, or the smoothness probe
attributes localiser arbitrariness to freezing. Recommend writing A/B/C once in Ladder §3.
**B(i) and B(iv) — estimates, no spec change.** The transported set is the orthonormal set closest
(least squares) to the reference LMOs inside the displaced occupied space; for the σ orbitals the
localisation functional is stationary at the fresh optimum, so its value along the transported
set drifts by O(q²); inside the near-degenerate π set the fresh optimum is arbitrary and "drift"
is undefined — which is the point of not using it. There is no re-truncation: the LNO space is
inherited by projection, and its quality at x is the bias line's measurement, not a discrete
event. Singular value: a C–H stretch at q = 1 moves the H by ≈ 0.105 Å; the bond LMO's centroid
moves by about half that against an orbital extent of ≈ 0.7–1 Å, so s_min(S_oo) ≈ 0.99–0.995 at
q = 1 (Gaussian-overlap scaling, recalled) and reaches 0.9 only near Δr ≈ 0.4–0.6 Å, q ≈ 4–6 —
far outside the grid. M1 prints the actual value; I expect no near-singularity anywhere on
|q| ≤ 1.

### 7. The quartic term in R_s at q_s = 1 is a labelled bias of order 0.1–1 cm⁻¹, not a second amplitude
**Where:** Ladder §3 R_s "= ½ pᵀΔ₂ p + O(p⁴)"; Research note §8 "(the q_s² contamination is
(q_s²/12)·Δ₄ …)".
**What.** Along one mode R_s = ½Δ₂,ii q² + Δ₄,iiii q⁴/24, so a single-amplitude read returns Δ₂,ii +
Δ₄,iiii q_s²/12, i.e. a frequency bias Δ₄,iiii/24 at q_s = 1 (dimensionless units). Δ₄ is the
CC−DFT *difference* of quartic constants: with φ_iiii ≈ 10–30 cm⁻¹ for C–C stretches and ≈ 100–150
for C–H (recalled) and a 10–30 % CC−DFT difference, Δ₄/24 ≈ 0.05–0.4 cm⁻¹ (C–C) and ≈ 0.4–2 cm⁻¹
(C–H) — below τ₇ everywhere, below the ~1 cm⁻¹ bind for C–C. Multi-atom patterns spread |p|² over
many modes and suppress the cross-quartics further. **Close:** accept it as a labelled term; the
sealed degree-4 fits of the R1 probe contain the quartic coefficient of ΔE(q) along four modes, so
the actual contamination is printed after the note at zero cost; on the scored modes the bonus's
second amplitude removes it exactly (as it removes c₀ in blocking 2). No deck change.

### 8. Cost after symmetrisation: K_off is plausibly 3–5 × 2M in energies at coronene, still ≪ a full Hessian; Budget §3's literature rows should carry their units so nobody compares CMA-2's "33 off-diagonals" with K_off
**Where:** Budget §3 rows "Off-diagonal count" and "Gradients for a full Hessian"; Ladder §3 banded
prior.
**What.** Every off-diagonal pattern now costs two energies for one response. What the banded
recovery must determine is the in-band block, which is *fitted*, not sparse: with w ≈ 50 cm⁻¹ and
coronene's ≈ 6 modes per 100 cm⁻¹ in the 400–1,600 cm⁻¹ range, the band holds ≈ 300 elements, plus
the out-of-band sparse and low-rank parts; one response per pair gives K_off ≳ 300 pairs = 600
energies, more with f_h held out — 3–5 × 2M = 204, and ≈ 3 % of the 20,809 energies of a full
central-difference Hessian. The plan claims neither K_off ≪ 2M nor a number; the dry run measures
it. The literature rows count columns (Sanders), gradients (O1NumHess: one gradient = 3N
responses) and selected off-diagonal *elements* (CMA-2: ≈ 33, each costing four energies = 132) —
none is in K's unit. **Close:** a "unit" column in Budget §3 (energies / gradients / columns /
elements × 4), and the sentence "K_off is counted in energies; no literature figure is in that
unit". The ± design itself is right: subtracting Δ₁ (known exactly from R_a of the block) from
single-energy off-diagonal responses would leave the cubic term (1/6)Δ₃ppp, which at q_s = 1 is
of order 20 % of the signal — not a saving.

### 9. ρ\*_common is the right axis; a common χ² per point would import the size-class σ into the size sentence; the max() rule can only be gamed towards a *loose* threshold, and ρ_max bounds that
**Where:** Ladder §1, §3 Q8(c); Distilled Q8.
**What.** ρ is a relative residual on each rung's own held-out R_s; reading both curves at one ρ
asks "how many responses to explain the same fraction of the held-out variance" — apples to apples
in the only sense a size question has. χ² per point = (ρ·RMS_resp/σ)² imports σ(size class) — item
44's growth — so a common c² would make the sentence report noise growth as pattern growth. Gaming:
the noisier rung sets ρ\*_common; at a loose threshold both K_off are small and the ratio drifts
towards 1, so "saturation" passes more easily the noisier the larger rung is. ρ_max = 0.5 caps
that; between ρ = 0.5 and a typical 0.1 the ratio can still differ. **Close (informational):**
print the ratio also at a frozen reference ρ_ref (say 0.3) whenever both stored curves reach it,
beside the ρ\*_common value that decides. Deck choice cannot game it: the hashed order and f_h are
frozen and the curves are stored.

### 10. Pooled σ decides — the lesser evil, and the 2× flag is well placed; write its false-positive rate
**Where:** Ladder §3 Q6 bullet and amplitude bullet; Budget §4.5.
**What.** Pooled σ² is the mean of the four; if one mode carries all the scatter the pooled value is
σ_worst/2 and that mode sits at exactly 2× pooled — the flag fires precisely in the case the brief
worries about. Under homogeneity P(σ̂_mode/σ̂_pooled > 2) ≈ P(χ²₄ > 16) ≈ 0.3 %, so the flag is
almost never a coin-toss artefact, while a per-mode *gate* at ν = 4 would be one ([0.42, 1.54] at
90 %). The Cartesian-amplitude argument is real (a C–H stretch moves one atom 0.1 Å; a breathing
mode moves twelve by ≈ 0.03 Å) but the projection error goes as the *square* of the local
displacement, so it is the C–H stretch, not the ring modes, that would be worst — and it is one of
the four. Keep pooled-decides; add "(false-positive rate ≈ 0.3 % under homogeneity)" so the flag's
weight is stated.

### 11. M4/M5 are B3 by the plan's own recalled sizing; that does not move the 12-week window, but the mode-G size sentence is B3-conditional and Ladder §1 should say so
**Where:** Side project §4 ("pyrene ≈ 620 functions, of order 30 GB — B3"); M4 "B2 or B3"; M5 "B3
by expectation"; kill criterion ("M3 within 12 calendar weeks"); Ladder §1 mode-G form.
**What.** 36 gradients at pyrene/cc-pVTZ with a ≈ 30 GB per-fragment ⟨ov|vv⟩ do not fit 28 GB
unless item (b)'s checkpointing halves it — B3 by construction at the recalled sizing. The kill
clock binds M3 only, so the calendar is unaffected; but the mode-G size sentence needs M3, M4 *and*
M5, hence B3 twice. **Close:** Ladder §1 mode-G form gains "(expected B3-conditional: M4 and M5 are
B3 by the side project's own sizing)".

### 12. The one canonical CCSD(T) gradient is not in-core-bound by the (T) part — PySCF blocks the (T) lambda and rdm over virtual triples — so the branch is live; set `max_memory` and print peak RSS, and expect time, not memory, to be the binding number
**Where:** Ladder §3 anchor-basis bullet; Budget §4.1b; probes README 1b.
**What — opened today.** `pyscf/grad/ccsd_t.py` imports `ccsd_t_rdm` and `grad.ccsd` and uses
`_gamma2_outcore` with `lib.H5TmpFile()`; `ccsd_t_rdm.py` and `ccsd_t_lambda.py` allocate
`(blksize, blksize, blksize, nocc, nocc, nocc)` blocks with `blksize` from `max_memory`, never the
full o³v³ (which at benzene/cc-pVTZ, o = 15, v = 243, would be 387 GB). Remaining memory drivers
are the CCSD Λ/rdm part and the vvvv-class integrals, handled out-of-core (790 GB free disk). So
the largest intermediate is bounded by `max_memory`, the gradient is expected to *run* on 31.3 GB,
and the 72-gradient reference's "does not fit" is a *time* expectation to be measured — consistent
with the plan's expected printout. **Close:** README 1b: "`max_memory` = 28,000 MB set explicitly;
peak RSS and disk high-water mark printed". No design change.

### 13. The "noiseless" dry run is not noiseless: the DFT arm's quadrature error is geometry-dependent at the µE_h scale, the Q0 deck does not list the DFT grid, and the plan attributes all of σ_E to the local-CC arm
**Where:** Distilled Q0 (deck hash lists levels, basis, code, thresholds — no grid); Ladder §3 Q6
("frozen-space local-CC energies may not be smooth"); Budget §4.1 ("noiseless" column).
**What.** ΔE = E_CC − E_DFT; every displaced DFT energy on a finite atom-centred grid carries a
geometry-dependent quadrature error of µE_h order on default grids (recalled), which the degree-4
fit reads as scatter exactly like a PNO discontinuity. The R1 σ_E therefore bounds the *sum*; the
DFT–DFT dry run's single-mode block measures the DFT part alone, for free, and is currently called
"noiseless". **Close:** the DFT grid (and SCF/CC convergence thresholds) as Q0 deck numbers; the
dry-run script prints its own σ_E from its single-mode block, labelled "DFT-arm floor"; Q6's
sentence reads "ΔE(q) scatter, both arms' numerical noise included".

### 14. Residues of Round-10 Pass A closures 8 and 16, and two Goal/Ladder hedges that differ
**Where:** Distilled status paragraph; Goal prime directive vs Ladder §2; Proposal §7, §11; Budget §3.
**What.** (a) Distilled's second status paragraph still ends "after Round-8 Pass A and Pass B" while
its header says Round-10. (b) Goal: "unconditional on R0 (cell spectra exist …)"; Ladder §2: "R0 is
*expected* unconditional" — the Goal wins on drift, so either the Goal gains "expected … until item
56 is read" or the Ladder loses it; after blocking 4, R1 gets the same word. (c) Proposal §7 "seven
inputs" still lists "the opponent side" and omits the R0 pilot (Budget §4's seven: 1, 1b, 2, 2a, 3,
4, 5); §11 risk 7 "an four-weekly". (d) Budget §3 "bf" undefined. (e) Change-table rows 28, 29, 31
as amended match the documents (28 carries the Round-9 clause and items 52–53; 29 the symmetrised
response, √(SSR/(n − p)) and the common threshold; 31 restored) — after blocking 4, row 28 gains
"a room-temperature naphthalene source named".

### 15. Pilot-note leak check after the Round-9/10 closures: clean, with one clarification to write
**Where:** Ladder §3 "Order of the pilot inputs"; Budget §4.1b, §4.3; probes README 1b, 2, 3, 6.
**What.** Confirmed leak-free: M1's raw energies sealed (its printed difference column E(frozen) −
E(fresh) is the freezing bias curve, not a CC−DFT number); the canonical feasibility gradient is at
the DFT equilibrium — it yields canonical Δ₁ only; the local-CC gradient run/no-run at equilibrium
likewise Δ₁ only; the R0 pilot's one local-CC energy is a timing at equilibrium; the R1 probe prints
σ only. One thing to write: under blocking 3, Δ₁ becomes a *used* quantity; the equilibrium
gradients before the note therefore make Δ₁ readable before the note — harmless for c, K_cap, τ₇
and the margins (none depends on Δ₁), but the Ladder's leak sentence should say "no local-CC Δ₂
number … (Δ₁ at equilibrium is readable and is not a pilot-note input)".

### 16. At coronene the interior pairs carry no C–H or CH-oop Δ-shift (the central ring has no hydrogen): (b) must be read per family on the pairs that carry that family's shift, or a CH pass on edge pieces will be mistaken for an interior pass
**Where:** Ladder §3 (b): "(b) is one comparison at one shell for interior pairs (edge pairs use the
ring-closed three- to five-ring pieces)"; Q8(b) "the share of the family's Δ-shift carried by pairs
beyond r_max".
**What.** The family-projected coupling uses u = the family mode's local direction at each atom;
for the C–H stretch and the CH-oop families the interior carbons have small u, so the interior
pairs' couplings are small in both fragment and whole — "at noise" or trivially agreeing — and a
capped central benzene carries caps where coronene has spokes. The meaningful (b) comparison for
those families is on the edge pieces; for the 6.2/7.7 µm C–C families it is on the interior, and
that is where a capped benzene (an aromatic sextet) is least likely to reproduce coronene's
interior CC−DFT difference (item 44: the local-correlation error, and DFT's delocalisation error,
grow with conjugation). **Expected outcome:** C–H and CH-oop earnable at coronene on 3–5-ring edge
pieces; C–C **pending (b′)** and therefore B3. Decision 1's licence for the families astronomy
cares most about is, on the page, only ever earnable through (b′). The plan already reports that
honestly. **Close:** "(b) is scored per family on the pairs that carry ≥ (1 − ε₈) of that family's
Δ-shift (Q8(b)'s own share): the interior pairs for the C–C families, the edge pieces for the CH
families" — one clause in Ladder §3 and README 13.

### 17. No two-shell whole-molecule test smaller than circumcoronene exists; the affordable two-shell information under a pending licence is part (c)'s R4 instance on fragments only — say it may run while pending, and that it cannot resolve the pending state
**Where:** Ladder §3 (b′), (c); Distilled §8 pending sentence; Budget §4.13; README 14.
**What.** A two-shell fragment around a central ring *is* circumcoronene (C₅₄H₁₈, 72 atoms, 210
modes); around a central bond it is ovalene (C₃₂H₁₄) — in both the fragment is the whole molecule,
so neither is a (b′) test; dibenzo[bc,ef]coronene-class pieces are ring-closed but not shells. The
circumcoronene whole-molecule mode-E batch is ≥ 2 × 210 = 420 energies of a 72-atom molecule plus
K_off — B3 by expectation at cc-pVTZ; at cc-pVDZ the classification rule decides (an LNO energy
of a 72-atom molecule at DZ on 8 cores is hours, recalled — 420 of them straddle 168 h). What *is*
laptop work by expectation is (c)'s first instance: direct couplings on circumcoronene's central
ring from 12-atom (one-shell) and 36-atom (two-shell) capped fragments, 72 × families energies of
benzene- and coronene-size pieces. (iii): at R6 with r_f = two shells, (c) is 180 coronene-size
plus 180 circumcoronene-size fragment energies — B3 by expectation, as the plan says; (c) is
"simply B3" unless one shell passed at coronene, which for the C–C families I do not expect
(non-blocking 16). **Close:** "(c) at R4 may run under a pending licence (fragments only; laptop
by expectation) and is printed; it does not resolve the pending state — only (b′) does" in Ladder
§3 and Distilled §8.

---

## Attack-by-attack disposition (A–G)

| # | Attack | Lands? | Disposition |
|---|---|---|---|
| A | Symmetrised response R_s | **Yes — blocking 1, 2, 3; non-blocking 7, 8** | (i) Quartic bias Δ₄/24 at q_s = 1 is 0.05–0.4 cm⁻¹ (C–C) and up to ≈ 2 cm⁻¹ (C–H) — a labelled term, no second amplitude; the sealed degree-4 fits print it post-note. (ii) σ(R_s) = σ_E/√2 is the right per-response sigma for ρ_noise *if* ΔE(0)'s shared error is handled — but the "fitted constant" is collinear with the diagonal at one amplitude (blocking 2) and the dry run injects noise per response, not per energy (blocking 1). The noise floor: ρ_noise = (σ_E/√2)/RMS_resp with c₀ identified from the two-amplitude modes or bounded by the convergence thresholds. (iii) Two energies per off-diagonal response is the price of a response that carries Δ₂; K_off plausibly 3–5 × 2M at coronene, ≪ a full Hessian; the literature rows need units. (iv) Δ₁ is worth printing and is *load-bearing*: the Hessian at the DFT minimum differs from the corrected surface's own by ½Σφ_iij δq_j ≈ 0.5–2 cm⁻¹ per band — apply it first-order or budget it (blocking 3). |
| B | Transported occupied orbitals | **No design defect; one code fact and one arm definition — non-blocking 6** | The API takes `lo_coeff` (external LMOs) but rebuilds LNO spaces in `make_las` every call: the occupied half is free, the virtual half needs a `make_las` override. Locality drift of the transported set is O(q²) for σ orbitals and undefined for the soft π set (the reason for the design); no re-truncation occurs. s_min(S_oo) ≈ 0.99 at q = 1 on a C–H stretch; 0.9 needs q ≈ 4–6. Define arms A (frozen–frozen), B (transported LMOs + fresh LNO), C (fresh–fresh); the R1 "without frozen spaces" arm should be B. |
| C | Temperature floor and the sources | **Yes — blocking 4; non-blocking 5** | A 25 °C, 0.1 cm⁻¹ quantitative naphthalene vapour spectrum exists (PNNL/NWIR; JQSRT 2024, opened) and Pirali 2009 is a room-temperature high-resolution cell study: R1 is expected unconditional on a named source, and the no-swap rule requires naming it before M03. χ_max = 0.03 bounds the gas-phase slopes I could find (pyrene −0.025 at 3.3 µm, −0.014 oop, 573–873 K, from Joblin 1995 via Chakraborty 2021); the linear-from-296 K form is conservative (low-T slopes are smaller); the +1 cm⁻¹ term is benzene's and should scale with the molecule. Joblin 1995 itself: not opened (ADS 405). Pyrene 6–15 µm at room temperature: nothing found; jet-cooled 3 µm exists for the R2 set (Maltseva 2016). |
| D | Fragment licence after Round 9 | **Partly — non-blocking 16, 17** | Interior pairs carry no CH-family shift at coronene; (b) must be read per family on the shift-carrying pairs. Expected: CH families earnable on edge pieces, C–C pending (b′) → B3. No two-shell whole-molecule test smaller than circumcoronene exists (the two-shell fragment is the molecule); (c)'s R4 instance on fragments is the laptop-affordable two-shell information and should be allowed under "pending". (c) at R6 with two shells is B3 by expectation — the plan says so. |
| E | ρ\*_common | **No — non-blocking 9** | Common ρ is the right axis; common χ² would import σ growth. The max() rule can only loosen; ρ_max bounds it; add an informational read at a frozen ρ_ref. Not gameable by deck choice under the hash and stored curves. |
| F | Pooled σ | **No — non-blocking 10** | Pooled decides, per-mode flag at 2× is exactly the heterogeneity case and fires falsely ≈ 0.3 % of the time under homogeneity; a per-mode gate at ν = 4 would be a coin toss. The worst Cartesian case is the C–H stretch, which is in the set. |
| G | 36 gradients and the feasibility gradient | **Partly — non-blocking 11, 12** | M4/M5 are B3 by the recalled sizing; the kill window binds M3 only; the mode-G size sentence is B3-conditional and should say so. PySCF's CCSD(T) gradient blocks the (T) lambda/rdm over virtual triples (opened) — not in-core-bound; the one gradient is expected to run; the 72-gradient reference is a time question. |

**Also-worth items.** The dry run must add noise per energy (blocking 1 — the brief's own warning
was right). The leak check is clean (non-blocking 15). Change-table rows 28, 29, 31 match the
documents (non-blocking 14(e)).

---

## What would settle it

Items 1–4 are spec edits and cost nothing; 5–9 are the measurements the R0–R1 programme then runs,
in the order they decide things.

1. **Inject noise per energy in the dry run, with one shared ε₀** (blocking 1) — Budget §4.1,
   Distilled §3, probes README 1; c and K_cap are then read at the σ the real run has.
2. **Make the shared-reference constant identifiable or drop it** (blocking 2) — the second
   amplitude on the scored modes already exists; one paragraph in Ladder §3 and Distilled §3.
3. **Name the Δ₁ term** (blocking 3) — apply it first-order or budget it; print Δ₁ per totally
   symmetric mode; add those modes to the resonance-closed set.
4. **Name the PNNL/NWIR naphthalene spectrum, Pirali 2009 as a room-temperature source, and
   Maltseva 2016 for the R2 C–H stretch** (blocking 4) — bibliography, Frozen_Lines §5, Ladder §2 R1
   row, README 2a, Proposal — before M03 prints anything. R1 then reads "expected unconditional".
5. **M03's u_band table** with the PNNL record's stated conditions and u_296 per molecule — decides
   R1's families before the note; zero compute.
6. **M1 with the three arms A/B/C** (non-blocking 6) and the `make_las` override pinned — tens of
   benzene energies; decides whether E_frozen is smooth and what each freezing half costs.
7. **The canonical feasibility probe with `max_memory` set and one gradient** — hours; the branch
   is live (non-blocking 12).
8. **The zero-CC dry run** as amended — prints the DFT-arm noise floor (non-blocking 13), K_off in
   energies at the largest laptop size (non-blocking 8's plausibility), and tests the constant's
   identification (blocking 2).
9. **The R1 smoothness probe** (72 energies) with arm B as the reference — the first frozen-space
   number the plan reads; then Round 7's order as before.

Until 1–4 are written, R0–R1 is a programme whose two frozen constants are read at the wrong noise
level, whose recovered frequencies can carry a same-sign offset the size of the beat margin, whose
scored spectra omit a first-order term the size of the effect, and whose R1 scoreboard is about to
lock in a refusal that the existing data does not require. Once they are written — all four are
sentences, not measurements — R0–R1 is a green light, R2–R3 follow under the same rules, and the
promised set beyond R3 stands as worded, conditional on B3 as the plan already says.

---

*No frozen document was edited. Facts opened this pass are listed at the top with how they were
opened; Joblin 1995 remains unopened (its slopes are quoted at second hand from Chakraborty et al.
2021, opened), Pirali 2009's content is snippet grade, the PNNL naphthalene temperature is the
paper's general-procedure statement, and every quartic, cubic, bond-length, mode-frequency,
orbital-extent and grid-noise scale used in the arithmetic is recalled and marked so. Verify-on-use
applies to all of it before it enters a scored document.*

Pass B complete
