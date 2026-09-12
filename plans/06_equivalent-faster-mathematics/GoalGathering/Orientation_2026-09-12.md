# Plan 06 — Orientation (2026-09-12)

*Idea plan beside plan 05. Written to structure a conversation, not to commit to anything. Every
claim below is a measured number from plan 05, a verified reference, or marked as a guess. Revised
the same day after the user named the target: **the Schrödinger equation itself**, not the bookkeeping
around it.*

## 1. The target, stated precisely

Plan 05 needs, per molecule and per displaced geometry, one number: the electronic ground-state
energy at coupled-cluster quality (CCSD(T), cc-pVTZ, frozen core) — the solution of the
time-independent electronic Schrödinger equation in the Born–Oppenheimer setting, to a tolerance set by
plan 05's own bias budget (arm-A composite bias 0.47/0.03/0.79 cm⁻¹ at TZ tight; σ_E per mode). The
measured price is 2,087 s for benzene and 41,375 s for naphthalene per energy, with local natural
orbitals (LNO) already exploiting locality.

The question of plan 06: **is there a mathematics that yields the same energies faster?** Three
levels of "the same", each admitting different candidates:

| level | equivalent means | what a candidate must show |
|---|---|---|
| **E1 — identical object** | the same energy, exactly, by a different route (a reformulation with a proof of equivalence) | a theorem; Lean can referee it |
| **E2 — within plan 05's budget** | the same energy to within the bias and noise plan 05 already tolerates | a numerical comparison against plan 05's sealed benzene truth lines (probe M1) |
| **E3 — identical scored outcome** | the same band positions to within u_total | the same comparison on the scored quantity |

## 2. What is known to be impossible, and what is not

Two results bound the search and should be read first, in full, before anything else is proposed:

- **The general problem is hard.** Finding the ground-state energy of a local Hamiltonian is
  QMA-complete (Kempe, Kitaev & Regev, 2006), and this carries over to interacting electrons: the
  universal functional of density-functional theory exists (Hohenberg & Kohn, 1964; Levy, 1979) but
  computing it is QMA-hard (Schuch & Verstraete, 2009). Consequence for plan 06: **no method can be
  both exactly equivalent and fast on every molecule** unless complexity classes collapse. Any
  candidate that claims E1 *in general* is wrong before it is tested.
- **The specific instances are not general.** Plan 05's molecules are gapped, closed-shell, near
  equilibrium, and aromatic — instances with structure: nearsightedness of electronic matter (Prodan &
  Kohn, 2005) makes correlation local, which is exactly why LNO-CCSD(T) works and why plan 05's frozen
  spaces are smooth. **Every honest "faster equivalent" is a theorem or a measurement about a class of
  instances, not about the equation.** The search is therefore for *structure of the class* that the
  current algebra does not yet exploit.

That reframes the user's premise fairly: what was impossible is the general case, and it still is;
what is open is whether a sharper description of *this* class of molecules admits an exact or
certified shortcut that nobody has written down. That is a legitimate research question.

## 3. The mathematics on the table (exact reformulations that exist)

Each of these is an exact restatement of the same problem; each has a different cost profile; each is a
place where a class-specific structure theorem could turn "exact but expensive" into "exact and cheap
*for this class*". Verified entry points in brackets.

| reformulation | exact? | where the cost sits | class-structure that would make it fast |
|---|---|---|---|
| Coupled cluster, exponential ansatz on a reference determinant (Bartlett & Musiał, 2007) | exact at full excitation order; CCSD(T) is a truncation | N⁷ for (T); locality brings it near-linear (Riplinger & Neese, 2013; Nagy, Samu & Kállay, 2018; Nagy & Kállay, 2019) | proven decay of amplitudes with distance; low rank of the amplitude tensors (tensor hypercontraction: Hohenstein, Parrish & Martínez, 2012; Parrish et al., 2012) |
| Two-electron reduced density matrix as the variable (Mazziotti, 2011) | exact given N-representability | the N-representability conditions (semidefinite programs) | a class for which a finite set of conditions is provably sufficient |
| Density-functional theory (Hohenberg & Kohn, 1964; Levy, 1979) | exact with the exact functional | the functional is QMA-hard in general (Schuch & Verstraete, 2009) | a class-restricted functional with a bound — this is what plan 04/05's opponents and Δ-corrections implicitly assume |
| Matrix-product states / DMRG (Chan & Sharma, 2011) | exact at large bond dimension | bond dimension grows with entanglement across a cut | π-systems as quasi-one-dimensional: bounded entanglement would make DMRG exact and cheap for aromatic flakes (guess; to be checked against the literature on PAHs) |
| Neural-network wavefunctions (Pfau et al., 2020; Hermann, Schätzle & Noé, 2020) | variational, exact only in the limit | Monte-Carlo sampling; cost per molecule high, no reuse across molecules yet | a shared ansatz across a molecular family whose error is certified against sealed CC lines — this is the AI-native reformulation |

The row that is *new* in kind is the last one; the rows that are *exact* are the first four. A plan-06
direction is the pairing of a row with a class-structure theorem or measurement.

## 4. Candidate directions, each with its cheapest falsification

**S1 — Proven locality: how fast do the CC amplitudes and the frozen-space blocks decay for
aromatic flakes? (E1/E2).** Plan 05 already measures smoothness of the frozen spaces; plan 06 asks
for the *rate*: if the correlation contribution between fragments decays exponentially with distance
(Prodan & Kohn, 2005, for gapped systems), the number of fragment pairs that matter grows linearly and
the constant is measurable now. *Falsification:* the naphthalene timing run wrote 24 fragments; the
LNO output contains per-fragment correlation energies — print their magnitude against fragment
separation. Minutes on existing logs; then benzene → naphthalene → (later) pyrene gives the decay
constant. If the decay is slow, S1 is dead for this class.

**S2 — Low rank of the difference, not of the energy (E2).** Plan 05's target is CC − DFT curvature;
the correlation *difference* may have lower tensor rank than the correlation energy itself. The
factorisations of tensor hypercontraction apply to differences as well as to energies. *Falsification:*
literature first (verified reading of the THC papers and of any work on Δ-quantities); then a
prototype on benzene against the sealed truth line, after the current anchor work.

**S3 — Quasi-one-dimensionality of π-systems (E1 for DMRG at fixed bond dimension).** If the
entanglement across any cut of an aromatic flake's π-system is bounded, DMRG is exact at a fixed bond
dimension and its cost is linear in size — a class-specific exact method. *Falsification:* the
literature on DMRG for polyacenes and PAHs (read, not recalled) gives bond dimensions used; a small
pyscf-DMRG check on benzene's π-space against the sealed line would be the first own number. Not on
the laptop while an anchor job runs.

**S4 — Reduce the target (E3).** To first order a band shift is Δ₂,ii/(2ω_i); off-diagonal elements
enter at second order with 1/(ω_i − ω_j). If only a small set of functionals of the energy surface
moves the scored bands, the Schrödinger problem need only be solved along those functionals.
*Falsification:* on the benzene dry-run tensor, perturb each Δ₂ element by its plan-05 uncertainty and
count the elements that move any position by more than 0.5 cm⁻¹. One script, minutes (experiment X2).

**S5 — Exact query algebra around the energy (E1; the bookkeeping side, kept as a secondary track).**
Gradients are Hessian–vector products; structured matrices are recovered exactly from a colouring
number of products (Curtis, Powell & Reid, 1974; Coleman & Moré, 1983; Powell & Toint, 1979) or from
r + p random products at rank r (Halko, Martinsson & Tropp, 2011); diagonals from few random products
(Hutchinson, 1990; Bekas, Kokiopoulou & Saad, 2007). This does not touch the Schrödinger equation; it
touches how many times it is solved. *Falsification:* rank and colouring number of the benzene Δ₂
against plan 05's measured K = 448 (experiment X1). Caveat: a gradient cost ≈ 50 energies at DZ.

**S6 — Models as proposers, never as authorities.** Large models propose reformulations and read the
literature; every proposal enters the ledger only with a falsification test on existing data or a
verified reading, and is parked if that test cannot be run within a day. Formal search with models has
produced real theorems in narrow, well-formalised domains (Trinh et al., 2024); that is encouragement
for S1/S3/S5 where the statements are clean, and no evidence for S2 where the difficulty is numerical.

## 5. The Lean route, assessed

Lean 4 (Moura & Ullrich, 2021) with Mathlib (The mathlib Community, 2020) can state and machine-check
exact statements about finite-dimensional linear algebra, symmetric forms, finite group actions and
graph combinatorics — and, with more work, the variational principle and the Hohenberg–Kohn and Levy
constructions in a finite basis. It cannot do floating-point numerics, quantum chemistry, or *find* a
fast algorithm. Its value here is as a referee for E1 claims: a proposer (human or model) that says
"for this class the amplitudes decay like this, therefore this truncation is exact to ε" produces a
statement that is either a theorem or not, and Lean settles that in a way one molecule's numbers
cannot. The realistic first formal target is small and real: the measurement-operator algebra of S5
(exact recovery under a sparsity hypothesis, Powell & Toint, 1979). The ambitious target — a
class-restricted locality theorem for correlation energies — would be new mathematics whether or not it
is formalised; formalisation would be the certificate, not the discovery. What the Lean route does not
give is speed; it gives certainty about which shortcuts cannot be wrong, so that the search for speed
is confined to them.

**Dated addition 2026-09-12 (evening) — T3 stated as a conjecture, and its Lean prerequisites checked.** After the
S1 reading note (Benzi, Boito & Razouk 2013) the ambitious target can be written down: *Conjecture T3.* Let (M_n) be a
family of closed-shell π-conjugated molecules whose bond graphs have maximum degree ≤ 3 (sp²/sp³ carbon and hydrogen),
whose DFT HOMO–LUMO gaps are bounded below by γ > 0, and whose correlated and DFT energies are computed in a fixed
local basis. Then the atom-pair blocks of the correction Δ₂ = H_CC − H_DFT satisfy ‖Δ₂[A,B]‖ ≤ C·e^{−α·d(A,B)} with
d the bond-graph distance and constants C, α (∝ γ to first order) independent of n. *Status:* conjecture; the
density-matrix analogue is a theorem (their Cor. 8.6, Thm 8.4); the two missing steps are named in the S1 note
(resolvent decay → correlation-energy decay; energy decay → second-derivative decay). *Lean prerequisites (Loogle,
2026-09-12):* Mathlib has Bernstein polynomials and the Bernstein–Weierstrass approximation on [0, 1]
(`Mathlib.Analysis.SpecialFunctions.Bernstein`: `bernsteinApproximation_uniform`) and the Chebyshev minimax
properties on [−1, 1] (`Polynomial.Chebyshev.leadingCoeff_le_of_forall_abs_le_one` and companions), but **not**
Bernstein's theorem on geometric convergence of polynomial approximation for functions analytic inside an ellipse —
the step every decay theorem of the paper rests on. So even the density-matrix theorem is not yet formalisable
without first proving that classical result; T3 in Lean is two theorems away, not one.

**Dated addition 2026-09-12 (later the same evening) — T3 as a proof plan** ([note](Note_2026-09-12_T3_Proof_Plan.md)): hypothesis audit against plan 05's setting (bounded degree holds; Gaussian-basis fullness handled by BBR §6 truncation with an n-independent ε; **the stable-gap hypothesis fails asymptotically on the plan's own size sequence**, so α degrades ∝ gap towards the large PAHs); layers L0 (Bernstein, classical, absent from Mathlib) → L1 (BBR's theorems) → L2 (projector decay → correlation-energy decay; new at CC level) → L3 (energy → mixed second derivative; an exercise for the DFT side, new for CC). T3 as written says nothing about the *difference*; the claim plan 05 would profit from is **T3′: the correction decays faster than either Hessian** — no data yet, **X9 defined** (block profiles of H_DFT and Δ₂ side by side, by bond-graph distance, norm- and band-level). Lean: T3a (graph-distance nilpotency of powers of a pattern matrix), T3b (ball count on bounded-degree graphs), T3c (Theorem 9.2 in graph distance) named as buildable lemmas; the resolvent-only bypass of Bernstein noted.

## 6. Protocol

1. Every direction has a level (E1/E2/E3), a falsification test, and a status in the ledger.
2. First tests use existing data and verified reading only; no quantum-chemistry compute for plan 06
   until a direction has passed its first test and plan 05's anchor work has room.
3. Results are dated notes in this folder; a positive result transfers to plan 05 only through a
   plan-05 dated note or decision proposal, so plan 05's frozen text is untouched.
4. References verified before written; no number from recall; complexity claims cited, not asserted.
5. Human-time budget: exploration in conversation; the user decides when a direction gets a day.

## 7. First experiments (all on data or logs in the repository, minutes each)

- **X0 (S1):** read the two complexity papers and Prodan & Kohn in full and record what each does and
  does not exclude (a reading note, the plan's foundation).
- **X1 (S5):** numerical rank and colouring number of the benzene `D2_direct_Q`; implied query counts **Corrected 2026-09-12 evening (X1b):** the colouring X1 printed was of the pattern graph, not of the column-intersection graph; verified counts are 8–18 (CPR) / 7–14 (symmetric) products — see the T1b note §6. **X1c/X1d (same evening):** triangular substitution needs 6–7 products (exact, lower bound met) and magnifies plan 05's noise only 1.4–1.5× in band positions — see the X1d result note.
  against K = 448.
- **X2 (S4):** element-wise sensitivity of first- and second-order band positions to Δ₂ on benzene;
  count of elements that matter at 0.5 cm⁻¹.
- **X3 (S1):** per-fragment correlation energies from the naphthalene LNO log against fragment
  separation; the first decay number.
- **X7 (S1, defined 2026-09-12 evening, not run — compute):** decay length λ of the pair-energy (or atom-pair block) profile against the DFT HOMO–LUMO gap for benzene, naphthalene, pyrene; losing condition for "rate ∝ gap": λ·gap varies by more than a factor two.
- **X6 (S3, defined 2026-09-12 evening, not run — compute):** finite-difference curvature of E_CASCI(6,6) − E_HF along the three probed benzene modes against the sealed CC − DFT curvature; losing condition: π-CAS share < ½ on the C–C stretch mode closes S3 as an anchor route.
- **X9 (S1, T3′; done 2026-09-12 evening):** DFT Hessian and stand-in Δ₂ side by side by bond-graph distance ([result note](Result_Note_2026-09-12_X9_Correction_Longer_Ranged_Than_Hessian.md)). **T3′ loses at benzene:** the ratio ‖Δ[A,B]‖/‖H_DFT[A,B]‖ *rises* with distance (2.7 % on-atom → 6.5 % at three bonds; C–C meta/para 19–26 %); the correction is the longer-ranged object, its range set by the π system, not by the bonds.
- **X10 (S4; done 2026-09-12 evening):** which same-irrep pairs must be measured for 0.5 cm⁻¹, and can DFT alone rank them ([result note](Result_Note_2026-09-12_X10_DFT_Predictable_Pairs.md)). The free resonance-denominator rule 1/|ω_i² − ω_j²| ranks the 47 independent same-irrep pairs with Spearman 0.75 against the measured effect; **19 pairs suffice for 0.5 cm⁻¹** (oracle magnitude 17, oracle effect 6), i.e. 98 energies in the naive 2M + 2n count against K = 448; losing condition (more than half the pairs) not met; a proposal to plan 05 only after the naphthalene tensor repeats it. **X11 (same evening):** the substitution count on X10's pattern is 4 products (8 gradients) against 7 (14) on the symmetry prior alone — the element saving and the product saving stack (`experiments/x11_sparse_pattern_products.py`; X10 note §5).
- **X12 (S1; done 2026-09-12 evening):** the B3LYP Hessian's own decay per bond across nine PAHs from plan 02's stored Hessians (git 57a7910) ([result note](Result_Note_2026-09-12_X12_DFT_Hessian_Decay_Series.md)): a size-independent factor 0.25–0.29 per bond over the first four bonds (coronene 0.35); zeroing blocks beyond three bonds still shifts bands 26–246 cm⁻¹, so not even the mean field is truncatable in Cartesian blocks at 0.5 cm⁻¹ — the X8 lesson holds for nine molecules.
- **X5 (S1/S2, done 2026-09-12):** atom-pair block structure of Δ₂ in mass-weighted Cartesian space ([result note](Result_Note_2026-09-12_X5_Atom_Pair_Structure.md)).
- **X8 (S5/S1, done 2026-09-12 evening):** substitution-product count against element count for connectivity patterns in Cartesian space, benzene to C₃₈₄H₄₈ ([result note](Result_Note_2026-09-12_X8_Size_Scaling_Substitution.md)). Calibration on the real benzene Δ₂: **norm-based sparsity is not band-based sparsity** — the blocks outside every connectivity pattern move bands by 15–32 cm⁻¹, band accuracy at 0.5 cm⁻¹ needs 74 of 78 blocks, so at benzene the Cartesian correction is dense and no pattern is licensed; the size series (k bounded at 9 / 18–30 under bonded / one-ring patterns, ∝ carbons under all-C–C, against elements ∝ N or N²) stands as brackets until the naphthalene tensor exists; energies-only substitution never pays in any bracket (6–11× the elements).
- **X4 (Lean):** survey what Mathlib holds for symmetric matrices, rank, graph colouring, and the
  variational principle in finite dimension; reading notes, no proofs. **Done 2026-09-12**
  ([reading note](Reading_Note_2026-09-12_X4_Mathlib_Survey.md)): spectral theorem, sorted eigenvalues,
  rank, positivity, Loewner order, commuting families and the Rayleigh-quotient variational principle
  (lowest/highest eigenvalue) are all present; exterior powers carry the Slater inner product and an
  orthonormal Slater basis; absent: Courant–Fischer, greedy/Δ+1 colouring, Brooks, Fock space, any
  Hamiltonian, Schrödinger operators. T1 (S5 algebra) feasible; T2 statable; T3 out of reach.

**Dated addition 2026-09-12 (evening) — the cost ladder.** The user's goal for plan 06 restated in numbers ([Cost_Ladder_2026-09-12_Network_Data.md](Cost_Ladder_2026-09-12_Network_Data.md)): the R1 deck of 474 energies at 42–54 h each is 1.3–3 laptop-years; the levers that are measured (tight thresholds ÷ 2.1–4.7, X10's pair rule 474 → ≈ 300) bring one naphthalene-size molecule to days–weeks on a desktop or a node; only gradients at small g change the order of magnitude, and g is the one number nobody has printed. X9 and T3's audit set the expectation for decision 32's precondition (the correction's range grows with size).

## 8. Ledger of directions

| id | level | status (2026-09-12) | first test | result |
|---|---|---|---|---|
| S1 proven locality / decay rate | E1/E2 | **alive** (2026-09-12): X0 read — general E1 closed by QMA-hardness, class-restricted E1/E2 open; X3a from the naphthalene log: tight LNO keeps 92–100 % of active occupied and ~56 % of virtual orbitals per fragment, locality not yet paying at this size | X0 done ([reading note](Reading_Note_2026-09-12_X0_Complexity_and_Locality.md)), X3a done, **X3b done** ([result note](Result_Note_2026-09-12_X3b_Pair_Decay.md)): MP2 pair energies in naphthalene decay with λ = 0.75 Å, yet 2.3 % of the correlation energy sits beyond 3 Å — nothing droppable at this size; next X3c: decay of the curvature contribution | λ = 0.75 Å (energy); curvature decay still to measure; **X5 (2026-09-12)**: in real space 93.5 % of ‖Δ‖²_F sits on atoms and bonds, but all 78 atom-pair blocks are above 3× the noise floor and the carbon-ring profile is flat (meta/para ≈ bonded) — locality is E2/E3 with a measurable floor, not E1 ([result note](Result_Note_2026-09-12_X5_Atom_Pair_Structure.md)); **rigorous side read (2026-09-12, [Benzi–Boito–Razouk 2013](Reading_Note_2026-09-12_S1_Decay_Theorems_Benzi.md))**: exponential decay of functions of banded/bounded-degree Hamiltonians with a gap, rate ∝ gap, constants independent of size (their Thm 8.1/8.4, Cor. 8.6, §8.6) — the template for T3; two cheap tests defined: blocks vs bond-graph distance (X5 on naphthalene) and **X7** λ vs HOMO–LUMO gap along the ladder |
| S2 low rank of the difference (THC) | E2 | **unlikely** (2026-09-12, X1 + X5): full rank in mode space (30/30) and in mass-weighted Cartesian space; top 10 eigen-directions carry 59 % of ‖Δ‖²_F — on the DFT−DFT stand-in | X5 done ([result note](Result_Note_2026-09-12_X5_Atom_Pair_Structure.md)); one test left on the R0 pilot's real Δ₂ | negative twice |
| S3 quasi-1D π-systems (DMRG) | E1 at fixed bond dimension | proposed, literature first — **first data-side motivation from X5** (2026-09-12): the correction's nonlocality is confined to the carbon ring (C–C meta/para blocks as large as bonded ones; H-involving blocks decay) | literature partly read ([reading note](Reading_Note_2026-09-12_S3_DMRG_Pi_Systems.md): Hachmann et al. 2007 open text — complete π-valence CAS up to (50,50) by DMRG; bond dimensions/timings not in the text read); **X6 defined**: π-CAS(6,6) share of the ring-mode correction at benzene (compute, after the anchor job) | honest form is E2: S3 addresses the ring-confined π part only |
| S4 reduce the target | E3 | **alive** (2026-09-12, X2 done): on the benzene dry-run tensor only 6 of 435 off-diagonal pairs move any harmonic position by > 0.5 cm⁻¹ (one pair carries 19.6 of the 19.6 cm⁻¹ total); no element moves a band > 0.05 cm⁻¹ at plan 05's per-element noise | X2 done ([result note](Result_Note_2026-09-12_X1_X2_Benzene.md)); next: the same count on the naphthalene dry-run tensor | scored information ≪ matrix; stand-in functional pair, harmonic positions only |
| S5 query algebra (secondary track) | E1 | **alive, conditional** (2026-09-12, X1 done): 53 of 435 elements above 1 µE_h; exact sparse recovery needs **8–18 Hessian–vector products (CPR, verified colourings) or 7–14 (symmetric direct, greedy, verified) = 420–1080 energies if a product costs 2M energies, against K = 448** — corrected 2026-09-12 evening by X1b ([note](Note_2026-09-12_T1b_Symmetric_Readability_and_X1_Correction.md) §6): X1's "4–5 products = 240–300 energies" had coloured the pattern graph itself, whose colourings leave 70–122 of the pattern entries unreadable; rank is full (30), no low-rank route. **X1c (same evening, after reading Coleman & Moré 1984):** the *triangular substitution* scheme needs **6–7 products** on the benzene pattern (lower bound maxr = 6 met; exact recovery verified numerically) = **360–420 energies at 2M per product, below K = 448** — but substitution propagates measurement noise, and that propagation on plan 05's noisy probes is unmeasured | X1 done; local-CC(T) gradients do exist by automatic differentiation (Zhang, Li, Ye, Berkelbach & Chan 2024, JCP 161, 014109, PySCFAD — plan 05's side-project engine); the open number is their cost per gradient with frozen spaces, measured by plan 05's milestone M2 | **alive** — X1d (same evening, [result note](Result_Note_2026-09-12_X1d_Noise_Propagation.md)): with X2's noise the 6-product substitution recovers the benzene tensor to 0.10 cm⁻¹ median / 0.13 at the 95th percentile in band positions against 0.07 / 0.09 for the deck (magnification 1.4–1.5×; no trial above 0.5 cm⁻¹); **cost convention corrected the same evening:** a second-order finite-difference product costs ≈ 4M = 120 energies, so 6 products ≈ 720 energies > K = 448 — with energies only there is no gain at benzene; with AD gradients (M2) the six products cost 12g energy-equivalents, an order of magnitude below the deck if g ≲ 10, and the gain grows with size. **Transferred to plan 05 as proposal P24 — accepted the same evening = plan 05 decision 34** (`plans/05_…/GoalGathering/notes/Research_Note_2026-09-12_P24_Substitution_Probing.md`: one product measured in the R0 pilot, one pre-registered 6-products-vs-deck comparison). Open: P24's acceptance; the naphthalene repeat |
| S6 models as proposers | — | standing rule | — | — |
| *(addendum to S1, 2026-09-12 evening, X9)* | | **T3′ falsified at benzene**: the correction decays *more slowly* than the DFT Hessian in bond-graph distance (norm and band level); Δ₂ is the long-range object of the problem at this size | X9 done ([result note](Result_Note_2026-09-12_X9_Correction_Longer_Ranged_Than_Hessian.md)) | S1 stays E2/E3; no real-space route can rely on Δ₂ being more local than H |
| *(addendum to S4, 2026-09-12 evening, X10)* | E3 | **alive and sharpened**: a DFT-only ranking of same-irrep pairs (resonance denominators) selects 19 of 47 pairs for 0.5 cm⁻¹ at benzene — the first free prior that shrinks the off-diagonal deck; to be repeated on naphthalene before it becomes a plan-05 proposal | X10 done ([result note](Result_Note_2026-09-12_X10_DFT_Predictable_Pairs.md)) | **draft P25 written** ([Draft_P25_2026-09-12_DFT_Pair_Rule.md](Draft_P25_2026-09-12_DFT_Pair_Rule.md)): an ordering inside the symmetry prior, never a truncation; licence test = the naphthalene repeat; not submitted |
| *(addendum to S5 and S1, 2026-09-12 evening, X8)* | | **X8 done** ([result note](Result_Note_2026-09-12_X8_Size_Scaling_Substitution.md)): in Cartesian space no connectivity pattern is band-accurate at benzene (dropped blocks move bands 15–32 cm⁻¹; 74 of 78 blocks needed for 0.5 cm⁻¹); the size brackets for the product count are printed and wait for the naphthalene tensor | plan 05 ladder step 2, model form | S5 unchanged (conditional on gradients); S1: nothing droppable at benzene at the band level |
| Lean route | referee for E1 | **assessed** (2026-09-12, X4 done); T1d (Coleman & Moré Thm 2.2) **drafted, unbuilt** in `lean/Plan06/T1/SymmetricColouring.lean` (not imported until it compiles; build after the anchor job); Mathlib sufficient for the S5 measurement-algebra target T1 and for stating finite-basis E1 claims (T2); no Hamiltonian/Fock/Schrödinger infrastructure, so T3 out of reach. **Installed the same evening on the user's decision:** elan 4.2.4, Lean v4.34.0-rc2, Mathlib pinned `v4.34.0-rc2` (commit 85e3a25e) with its compiled cache, project `lean/` (Lake package `plan06`, library `Plan06`); **T1a and T1c proved** (`Plan06/T1/MeasurementAlgebra.lean`: `recover_probe`, `eq_of_probes_eq`, `colorable_maxDegree_succ` — the greedy Δ+1 bound, absent from Mathlib on 2026-09-12 — and the corollary `exists_coloring_recover`: Δ+1 probes determine every matrix respecting the pattern; no `sorry`); **T1b proved the same evening** (`recover₂_probe`: one-sided readability `SymmValid` suffices for a symmetric matrix; the pattern need not be symmetric) — **`lean/` has no `sorry`** | X4 done ([reading note](Reading_Note_2026-09-12_X4_Mathlib_Survey.md)); `lean/` builds | next: read Powell & Toint 1979 and Coleman & Moré 1984 and compare `SymmValid` with their conditions; then the X1b counts as theorems about plan 05's benzene pattern (needs the pattern as data) |

## References (all verified in Crossref on 2026-09-12)

- Bartlett, R. J., & Musiał, M. (2007). Coupled-cluster theory in quantum chemistry. *Reviews of Modern Physics, 79*(1), 291–352. https://doi.org/10.1103/RevModPhys.79.291
- Benzi, M., Boito, P., & Razouk, N. (2013). Decay properties of spectral projectors with applications to electronic structure. *SIAM Review, 55*(1), 3–64. https://doi.org/10.1137/100814019 (read 2026-09-12, §§8–10, 12, arXiv:1203.3953)
- Benzi, M., & Rinelli, M. (2022). Refined decay bounds on the entries of spectral projectors associated with sparse Hermitian matrices. *Linear Algebra and its Applications, 647*, 1–30. https://doi.org/10.1016/j.laa.2022.04.005 (record only; not open — PDF request item 31)
- Benzi, M. (2016). Localization in matrix computations: Theory and applications. In *Exploiting Hidden Structure in Matrix Computations: Algorithms and Applications*, Lecture Notes in Mathematics 2173 (pp. 211–317). Springer. https://doi.org/10.1007/978-3-319-49887-4_4 (record only, verified 2026-09-12; not open — PDF request item 30)
- Bekas, C., Kokiopoulou, E., & Saad, Y. (2007). An estimator for the diagonal of a matrix. *Applied Numerical Mathematics, 57*(11–12), 1214–1229. https://doi.org/10.1016/j.apnum.2007.01.003
- Chan, G. K.-L., & Sharma, S. (2011). The density matrix renormalization group in quantum chemistry. *Annual Review of Physical Chemistry, 62*, 465–481. https://doi.org/10.1146/annurev-physchem-032210-103338
- Coleman, T. F., & Moré, J. J. (1983). Estimation of sparse Jacobian matrices and graph coloring problems. *SIAM Journal on Numerical Analysis, 20*(1), 187–209. https://doi.org/10.1137/0720013
- Coleman, T. F., & Moré, J. J. (1984). Estimation of sparse Hessian matrices and graph coloring problems. *Mathematical Programming, 28*(3), 243–270. https://doi.org/10.1007/BF02612334 (read 2026-09-12 as Cornell TR 82-535, December 1982, https://hdl.handle.net/1813/6374)
- Curtis, A. R., Powell, M. J. D., & Reid, J. K. (1974). On the estimation of sparse Jacobian matrices. *IMA Journal of Applied Mathematics, 13*(1), 117–119. https://doi.org/10.1093/imamat/13.1.117
- Halko, N., Martinsson, P.-G., & Tropp, J. A. (2011). Finding structure with randomness. *SIAM Review, 53*(2), 217–288. https://doi.org/10.1137/090771806
- Hermann, J., Schätzle, Z., & Noé, F. (2020). Deep-neural-network solution of the electronic Schrödinger equation. *Nature Chemistry, 12*(10), 891–897. https://doi.org/10.1038/s41557-020-0544-y
- Hohenberg, P., & Kohn, W. (1964). Inhomogeneous electron gas. *Physical Review, 136*(3B), B864–B871. https://doi.org/10.1103/PhysRev.136.B864
- Hohenstein, E. G., Parrish, R. M., & Martínez, T. J. (2012). Tensor hypercontraction density fitting. I. *The Journal of Chemical Physics, 137*(4). https://doi.org/10.1063/1.4732310
- Hutchinson, M. F. (1990). A stochastic estimator of the trace of the influence matrix for Laplacian smoothing splines. *Communications in Statistics — Simulation and Computation, 19*(2), 433–450. https://doi.org/10.1080/03610919008812866
- Kempe, J., Kitaev, A., & Regev, O. (2006). The complexity of the local Hamiltonian problem. *SIAM Journal on Computing, 35*(5), 1070–1097. https://doi.org/10.1137/S0097539704445226
- Levy, M. (1979). Universal variational functionals of electron densities, first-order density matrices, and natural spin-orbitals and solution of the v-representability problem. *Proceedings of the National Academy of Sciences, 76*(12), 6062–6065. https://doi.org/10.1073/pnas.76.12.6062
- Mazziotti, D. A. (2011). Two-electron reduced density matrix as the basic variable in many-electron quantum chemistry and physics. *Chemical Reviews, 112*(1), 244–262. https://doi.org/10.1021/cr2000493
- Moura, L. de, & Ullrich, S. (2021). The Lean 4 theorem prover and programming language. *Lecture Notes in Computer Science*, 625–635. https://doi.org/10.1007/978-3-030-79876-5_37
- Nagy, P. R., & Kállay, M. (2019). Approaching the basis set limit of CCSD(T) energies for large molecules with local natural orbital coupled-cluster methods. *Journal of Chemical Theory and Computation, 15*(10), 5275–5298. https://doi.org/10.1021/acs.jctc.9b00511
- Nagy, P. R., Samu, G., & Kállay, M. (2018). Optimization of the linear-scaling local natural orbital CCSD(T) method. *Journal of Chemical Theory and Computation, 14*(8), 4193–4215. https://doi.org/10.1021/acs.jctc.8b00442
- Parrish, R. M., Hohenstein, E. G., Martínez, T. J., & Sherrill, C. D. (2012). Tensor hypercontraction. II. Least-squares renormalization. *The Journal of Chemical Physics, 137*(22). https://doi.org/10.1063/1.4768233
- Pfau, D., Spencer, J. S., Matthews, A. G. D. G., & Foulkes, W. M. C. (2020). Ab initio solution of the many-electron Schrödinger equation with deep neural networks. *Physical Review Research, 2*(3), 033429. https://doi.org/10.1103/PhysRevResearch.2.033429
- Powell, M. J. D., & Toint, P. L. (1979). On the estimation of sparse Hessian matrices. *SIAM Journal on Numerical Analysis, 16*(6), 1060–1074. https://doi.org/10.1137/0716078
- Prodan, E., & Kohn, W. (2005). Nearsightedness of electronic matter. *Proceedings of the National Academy of Sciences, 102*(33), 11635–11638. https://doi.org/10.1073/pnas.0505436102
- Riplinger, C., & Neese, F. (2013). An efficient and near linear scaling pair natural orbital based local coupled cluster method. *The Journal of Chemical Physics, 138*(3). https://doi.org/10.1063/1.4773581
- Schuch, N., & Verstraete, F. (2009). Computational complexity of interacting electrons and fundamental limitations of density functional theory. *Nature Physics, 5*(10), 732–735. https://doi.org/10.1038/nphys1370
- The mathlib Community. (2020). The Lean mathematical library. *Proceedings of the 9th ACM SIGPLAN International Conference on Certified Programs and Proofs*, 367–381. https://doi.org/10.1145/3372885.3373824
- Trinh, T. H., Wu, Y., Le, Q. V., He, H., & Luong, T. (2024). Solving olympiad geometry without human demonstrations. *Nature, 625*(7995), 476–482. https://doi.org/10.1038/s41586-023-06747-5
