# Plan 06 — reading note S1 (2026-09-12): the rigorous side of locality — Benzi, Boito & Razouk on decay of spectral projectors

*Read from the open arXiv text (1203.3953v1; PDF and extracted text in `Papers/plan06/`, git-ignored) of Benzi,
M., Boito, P., & Razouk, N. (2013), "Decay properties of spectral projectors with applications to electronic
structure", SIAM Review 55(1), 3–64, DOI 10.1137/100814019 (Crossref record verified 2026-09-12). Sections 8–10
and 12 read in full, the rest skimmed. A follow-up with sharper constants exists: Benzi, M., & Rinelli, M. (2022),
Linear Algebra Appl. 647, 1–30, DOI 10.1016/j.laa.2022.04.005 (record only, not read). This is the mathematics the
Orientation's "ambitious target" (a class-restricted locality theorem for the correction) would have to be built
on; the note says what the theorems state, what they assume, and what they do and do not give plan 06.*

## 1. The theorems, as stated (their numbering)

Setting throughout: sequences of n × n Hermitian matrices H_n with n = n_b · n_e → ∞ (n_b basis functions per
atom fixed, n_e electrons growing), spectra scaled into [−1, 1].

- **Theorem 8.1 (banded case, finite temperature).** If every H_n is m-banded with spectrum in [−1, 1], then the
  Fermi–Dirac function F_n = f_FD(H_n) obeys |[F_n]_ij| ≤ c·e^{−α|i−j|} with **c, α independent of n**, and the
  constants explicit: α = (1/m)·ln χ, where χ > 1 is set by the largest Bernstein ellipse with foci ±1 inside
  which f_FD is analytic (its poles sit at μ ± iπ/β), and c = 2χM(χ)/(χ−1). The whole proof is polynomial
  approximation: a function analytic in an ellipse around the spectrum is approximated by polynomials at a
  geometric rate (Bernstein, Theorem 8.7), and a polynomial of degree k in an m-banded matrix is km-banded.
- **Theorem 8.4 (general sparsity).** Drop "banded": for any sparsity pattern the same bound holds in the **graph
  distance** d_n(i, j) of H_n's adjacency graph, with α = ln χ. The authors add that O(n) truncation needs the
  graphs to have **uniformly bounded maximum degree**, so that graph distance grows without bound.
- **Corollary 8.6 (gapped systems, zero temperature).** If each H_n is m-banded and there are two fixed intervals
  [−1, a] and [b, 1] with gap γ = b − a > 0 such that [−1, a] holds exactly the n_e lowest eigenvalues, then the
  spectral projector P_n onto the occupied space obeys |[P_n]_ij| ≤ min{1, c·e^{−α|i−j|} + ε} for any ε > 0, with
  c, α independent of n. (Proof: choose β so that f_FD is within ε of the step on the two intervals — Proposition
  8.5 gives β ≥ (1/γ)·ln(2(1−ε)/ε) — then apply Theorem 8.1.)
- **§8.6 (rate versus gap).** Writing the bound as C·e^{−ξ|i−j|/m} with ξ = ½·ln((1+a)/(1−a)) for a normalised
  gap, the Taylor expansion gives ξ = a + a³/3 + …: **to first order the decay rate is the gap itself**, the
  conservative end of the literature's estimates (some systems decay faster, like √gap).
- **Theorem 9.2 (products).** Products of exponentially decaying matrix sequences decay exponentially (with any
  rate below the original, constant independent of n) — so orthogonalising a non-orthogonal basis
  (Löwdin, Cholesky) preserves the decay of Ĥ = Zᵀ H Z and of P.
- **Theorem 10.1 and §12 (vanishing gap).** For a banded Toeplitz model with gap → 0 ("metal"), the projectors
  converge to a projector with no exponential decay; the decay is a power law, in their example linear in the
  distance. The metallic case is left open.
- **§8.2, the numerical example.** For the linear alkane C₅₂H₁₀₆ (209 occupied states), the density matrix's
  bandwidth at a 10⁻⁸ truncation is "only slightly larger than that of the Hamiltonian"; HOMO–LUMO gap ≈ 0.1 on
  the scaled axis; the bandwidth is independent of chain length because gap and Hamiltonian bandwidth are.

## 2. What this gives plan 06 — and what it does not

**What it gives.** A complete, rigorous template for a class-restricted locality theorem: *hypotheses* (a
sequence of systems with bounded interaction range or bounded-degree graphs, uniformly bounded spectra, and a
gap bounded away from zero) → *conclusion* (exponential decay of the entries of any function of H that is
analytic in a neighbourhood of the spectrum, with rate ∝ gap and constants independent of size). The proof
technique — Bernstein's theorem plus "polynomials of banded matrices are banded" — is elementary enough that
it is a realistic Lean target in principle: it needs Chebyshev/Bernstein approximation on an ellipse (whether
Mathlib has Bernstein's ellipse theorem was **not checked** in X4; Chebyshev polynomials exist there, the
complex-analytic approximation theorem probably not). That is the concrete content behind T3.

**What it does not give.** Plan 05's object is not the density matrix. Δ₂ is the second derivative, with respect
to two nuclear displacements, of the *difference* between a correlated energy and a DFT energy. Two gaps between
the theorems and that object:

1. *From spectral projectors to energies.* Correlation energies (MP2 pairs, CC amplitudes) are not matrix
   functions of one Hamiltonian; they involve the resolvent (analytic off the spectrum, so the same machinery
   applies to the linear-response density and to Green's functions) *and* the two-electron integrals, whose own
   decay in a local basis is a separate, well-known fact. The X3b measurement (MP2 pair energies at naphthalene
   decaying with λ = 0.75 Å) is the empirical shadow of a resolvent-decay statement, not of Corollary 8.6 itself.
2. *From energies to their second derivatives.* Δ₂'s element for an atom pair (A, B) is a mixed derivative; its
   decay in the A–B distance follows, heuristically, from the decay of the second-order response of P to the two
   displacements — again resolvent decay, twice. Nobody has written that theorem for a correlated energy
   difference, which is why the Orientation calls T3 new mathematics.

**Two consequences that are already testable.**

- **Graph distance, not Euclidean distance, is the right variable.** X5 found the benzene ring "flat": meta and
  para C–C blocks as large as bonded ones. In graph distance those are 2 and 3 bonds — small numbers, exactly
  where Theorem 8.4 predicts little decay yet. The flat ring is not a violation of locality; it is locality
  measured in the wrong metric. The next X5-type test should tabulate the blocks against **bond-graph distance**
  (0, 1, 2, 3 bonds) rather than bohr; on benzene the range of graph distances is too small (max 3) to see a
  slope, so the naphthalene tensor (max 5) is the first informative case.
- **The rate should scale with the HOMO–LUMO gap (§8.6).** Benzene's gap is large; the acenes' gap shrinks with
  length (Hachmann et al. 2007, the S3 note); PAH flakes sit in between. So locality of the correction is
  expected to *weaken* exactly towards the large PAHs the plan targets, at a rate the theorems predict to be
  proportional to the gap. That is a falsifiable, cheap prediction for the ladder: λ (from an X3b-type fit of
  pair-energy decay) against the DFT HOMO–LUMO gap, benzene → naphthalene → pyrene → coronene. Benzene's λ can
  be printed from existing fragment logs if they carry pair energies; otherwise it is one cheap MP2 (compute,
  after the anchor job) — **X7**, defined here: λ versus gap on the ladder's first three molecules; losing
  condition for "rate ∝ gap": λ·gap varies by more than a factor two across them.

## 3. Ledger

S1: alive; **the E1 statement is now typed** — a Benzi–Boito–Razouk-style theorem for the response of a gapped,
bounded-degree system, with rate ∝ gap — and two cheap tests follow: blocks versus bond-graph distance (X5 on
naphthalene) and λ versus gap (X7). T3 stays "new mathematics first"; its Lean prerequisites (Bernstein's
ellipse theorem in Mathlib?) go on the next X4-type check. Benzi & Rinelli 2022 to be read for the sharper
constants if T3 is ever attempted.
