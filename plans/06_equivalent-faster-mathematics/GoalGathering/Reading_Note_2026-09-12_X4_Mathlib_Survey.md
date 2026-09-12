# Plan 06 — reading note X4 (2026-09-12): what Mathlib already holds for the Lean route

*Survey of the Lean 4 mathematics library (Mathlib) against the needs named in Orientation §5 and X4:
symmetric matrices, rank, graph colouring, the variational principle in finite dimension — plus the
operator, many-body and analysis infrastructure an E1 statement about the Schrödinger problem would
touch. Reading only; no proofs, nothing compiled. No Lean toolchain is installed on the laptop (checked
2026-09-12: no `lean`, `lake` or `elan`). Sources: the Mathlib4 documentation site and the source
repository (branch `master`) and Loogle name searches, all fetched on 2026-09-12; Lean names are quoted
as they appear today — Mathlib renames and moves files often (the vertex-colouring file itself moved to a
subdirectory on 2026-04-02), so every name below must be re-checked against the pinned Mathlib version
before it is used in a file.*

## 1. Method

- Documentation pages fetched: `Analysis/InnerProductSpace/{Rayleigh, Spectrum, Adjoint, Positive,
  JointEigenspace, LinearPMap, ExteriorPower, Laplacian}`, `Analysis/Matrix/Spectrum`,
  `LinearAlgebra/Matrix/{Rank, PosDef}`, `LinearAlgebra/{ExteriorAlgebra, CliffordAlgebra}/Basic`,
  `Analysis/Distribution/Sobolev`, `Combinatorics/SimpleGraph/Coloring/Vertex` (source file, 26.7 kB).
- Directory listings fetched (GitHub API): `Mathlib/Combinatorics/SimpleGraph`, its `Coloring/`
  subdirectory, `Mathlib/Analysis/InnerProductSpace`.
- Loogle substring searches on declaration names: `"Courant"` (0 hits), `"minmax"` (1 hit, a Lean
  tactic option, unrelated), `"rayleigh"` (15 hits, all in the Rayleigh module), `"Sobolev"` (20 hits,
  modules `Analysis.Distribution.Sobolev` and `Analysis.FunctionalSpaces.BesselPotentialSpace`).
- Two first fetches returned 404 (`LinearAlgebra/Matrix/Spectrum`, `Data/Matrix/Rank`); the material lives
  at `Analysis/Matrix/Spectrum` and `LinearAlgebra/Matrix/Rank`. Recorded because it shows how quickly
  paths move.

## 2. What is there — by need

| need (Orientation §5 / X4) | Mathlib today (2026-09-12) | verdict |
|---|---|---|
| **symmetric / Hermitian matrices, spectral theorem** | `Matrix.IsHermitian.eigenvalues` (indexed by the matrix index), `eigenvalues₀` (indexed by `Fin (card n)`, **`eigenvalues₀_antitone`**: sorted decreasing), `eigenvectorBasis` (orthonormal), `eigenvectorUnitary`, `spectral_theorem` (A = U D U*), `mulVec_eigenvectorBasis`, `det_eq_prod_eigenvalues`, `trace_eq_sum_eigenvalues`, **`rank_eq_card_non_zero_eigs`**, `spectrum_real_eq_range_eigenvalues`. Operator form: `LinearMap.IsSymmetric.eigenvectorBasis`, `.eigenvalues` (sorted decreasing, `eigenvalues_antitone`), `.diagonalization`, `orthogonalFamily_eigenspaces`, `direct_sum_isInternal`, `conj_eigenvalue_eq_self` (real eigenvalues) | **present, complete for finite dimension** |
| **variational principle (finite dimension)** | `ContinuousLinearMap.rayleighQuotient` (re⟪Tx,x⟫/‖x‖²); **`LinearMap.IsSymmetric.hasEigenvalue_iInf_of_finiteDimensional`** and `…_iSup_…`: the infimum / supremum of the Rayleigh quotient of a symmetric operator on a nontrivial finite-dimensional space is an eigenvalue; `IsSelfAdjoint.hasEigenvector_of_isMinOn` / `isMaxOn` (complete space, extremum attained on the sphere ⇒ eigenvector); `norm_eq_iSup_rayleighQuotient`; compact self-adjoint operators: `ContinuousLinearMap.orthogonalComplement_iSup_eigenspaces_eq_bot` (spectral theorem), `finite_dimensional_eigenspace` | **present for the lowest / highest eigenvalue** |
| **min–max for the k-th eigenvalue (Courant–Fischer)** | no declaration name contains "Courant"; nothing under "minmax"; not listed in either spectral module | **absent** — would have to be proved (a known, contained exercise on top of `eigenvalues₀_antitone`) |
| **rank** | `Matrix.rank` (finrank of the range of `mulVecLin`), `cRank`/`eRank` (cardinal / ℕ∞ versions), `rank_eq_finrank_span_cols`, `_span_row`, `rank_mul_le`, `_left`, `_right`, `rank_mul_eq_left/right_of_isUnit_det`, `rank_le_card_width/height`, `rank_transpose`, `rank_conjTranspose`, `rank_self_mul_transpose`, `rank_submatrix`, `rank_reindex`, `rank_diagonal`, `rank_unit` | **present** (no sub-additivity lemma listed on the page — check before relying on it) |
| **graph colouring** | `SimpleGraph.Coloring` (as a homomorphism into a complete graph), `Colorable n`, `chromaticNumber` (ℕ∞-valued), `Coloring.colorClass(es)`, `IsClique.card_le_of_colorable`, `cliqueNum_le_chromaticNumber`, `cliqueFree_of_chromaticNumber_lt`, `chromaticNumber_top` (complete graph), `CompleteBipartiteGraph.chromaticNumber`, `chromaticNumber_mono(_of_hom)`, `coloringCongr`; sibling files `Coloring/Constructions.lean`, `Coloring/EdgeLabeling.lean`; also `AdjMatrix`, `LapMatrix` (graph Laplacian), `Clique`, `Matching`, `Hall`, `Tutte` in the same directory | **definitions present; no greedy colouring, no Δ+1 degree bound, no Brooks' theorem** in the vertex-colouring file (checked in the source) — the Powell–Toint / Coleman–Moré bound of X1 needs the greedy Δ+1 lemma written |
| **operators on Hilbert spaces** | `ContinuousLinearMap.adjoint` (conjugate-linear isometric equivalence), `adjoint_inner_left/right`, `adjoint_adjoint`, `adjoint_comp`, `isSelfAdjoint_iff'`, `LinearMap.adjoint` (finite dimension) with `LinearMap.isSymmetric_iff_isSelfAdjoint`, `Matrix.toEuclideanLin_conjTranspose_eq_adjoint`; the C*-algebra structure on `E →L[𝕜] E`; positivity: `LinearMap.IsPositive` / `ContinuousLinearMap.IsPositive` (symmetric with re⟪Tx,x⟫ ≥ 0), `IsPositive.nonneg_eigenvalues`, `IsPositive.conj_adjoint`, the **Loewner partial order** on operators (`instLoewnerPartialOrder`, `nonneg_iff_isPositive`); **joint eigenspaces**: `LinearMap.IsSymmetric.directSum_isInternal_of_commute`, `iSup_iInf_eq_top_of_commute` (a pairwise commuting family of symmetric maps in finite dimension is simultaneously diagonalisable), `orthogonalFamily_iInf_eigenspaces` | **present**; the joint-eigenspace results are exactly the algebra behind plan 05's symmetry blocking (commuting symmetry operators ⇒ block structure) |
| **unbounded operators** | `LinearPMap.adjoint` (partially defined), `IsFormalAdjoint`, `IsSelfAdjoint` for `LinearPMap` (A† = A), `IsSelfAdjoint.dense_domain`, `adjoint_isClosed`, `IsSelfAdjoint.isClosed` | **skeleton only**: no symmetric-operator notion, no essential self-adjointness, no Kato–Rellich, no spectral theorem for unbounded operators |
| **many-body structures (Slater determinants, fermions)** | `ExteriorAlgebra R M` (= `CliffordAlgebra 0`), `ι`, `ι_sq_zero`, `lift` (universal property), `exteriorPower` (⋀[R]^n M as a submodule), `ιMulti` (alternating n-fold product), `ιMulti_span_fixedDegree`; **`Analysis/InnerProductSpace/ExteriorPower`**: inner product on ⋀^n E by the Gram determinant (`exteriorPower.inner_ιMulti_ιMulti` = det ⟪xⱼ, yᵢ⟫), **`OrthonormalBasis.exteriorPower`**: an orthonormal basis of E induces an orthonormal basis of ⋀^n E indexed by the n-element subsets; `CliffordAlgebra Q` with `ι_sq_scalar`, `ι_mul_ι_add_swap` (symmetric product is a scalar), `ι_mul_ι_comm_of_isOrtho` (orthogonal vectors anticommute) | **the finite-basis N-electron space exists**: ⋀^N of the orbital space with its Slater-determinant orthonormal basis is `OrthonormalBasis.exteriorPower`, and the Gram-determinant inner product is the Slater overlap rule; the Clifford relations are the CAR skeleton. **Absent**: Fock space, creation/annihilation operators, second-quantised Hamiltonians, any Hamiltonian at all |
| **analysis for the continuum problem** | Sobolev spaces as Bessel-potential spaces of tempered distributions: `TemperedDistribution.MemSobolev s p`, `besselPotential`, `memSobolev_besselPotential_iff`, **`MemSobolev.laplacian`** (H^s → H^{s−2}), `MemSobolev.lineDerivOp`, `fourier_memL1` (s > d/2), `mono`; pointwise Laplacian on finite-dimensional real inner product spaces (`InnerProductSpace.laplacianWithin`, `laplacian_eq_iteratedFDeriv_orthonormalBasis`, linearity); the Gagliardo–Nirenberg–Sobolev inequality (contributed 2024, per the ITP 2024 paper found in the search) | **foundations present, no Schrödinger operator**: no −Δ + V as a self-adjoint operator, no Coulomb potential, no Hardy/Kato inequalities, no ground-state existence |
| **complexity theory (X0's QMA/NP results)** | not surveyed today (`Mathlib/Computability` exists; complexity classes were not checked) | out of scope for the Lean route: X0's results bound the general problem, the route targets class-restricted statements |

## 3. What this means for the three formal targets of Orientation §5

**T1 — the S5 measurement algebra (first formal target).** Statement: a symmetric M × M matrix with a
known zero pattern P, and a proper colouring c of the column-intersection graph of P (columns adjacent when
they share a row with two non-zeros — Coleman & Moré 1983), is determined exactly by the |c| products
A·d_k, d_k the indicator of colour class k. Every ingredient is elementary and present: `Matrix`,
`Matrix.IsSymm`, `mulVec`, `Finset.sum`, `SimpleGraph.Coloring` and colour classes. Nothing about it is
in Mathlib as a theorem, and the greedy Δ+1 colouring lemma that turns the statement into the X1 bound
(X1's product count; corrected the same evening to 8–18 by X1b) is also missing. Estimate, not a measurement: a few hundred lines of Lean
for someone who knows Mathlib's `Matrix` API; a first project, not a research one. **Feasible; the
infrastructure is sufficient.**

**T2 — an E1 statement in a finite basis.** "Method X's energy equals the lowest eigenvalue of H restricted
to subspace S" can be *stated* today: `LinearMap.IsSymmetric` for H, `Submodule` for S, the restriction,
and `hasEigenvalue_iInf_of_finiteDimensional` for "lowest eigenvalue = infimum of the Rayleigh quotient".
Full configuration interaction in a finite orbital basis is the case S = ⋀^N(orbital space), whose
orthonormal Slater basis is `OrthonormalBasis.exteriorPower`. What is missing to say anything about
*coupled cluster* is the exponential ansatz (an exponential of a nilpotent excitation operator; Mathlib
has `NormedSpace.exp` for Banach algebras — its use for nilpotent operators was **not checked today**) and
the fact that CC is not variational, so the statement is a fixed-point equation, not an infimum. **Statable
for variational methods now; CC needs one more survey step; proofs of anything beyond definitions are
research.**

**T3 — a class-restricted locality theorem for correlation energies.** Needs decay estimates for
operators on large finite or infinite-dimensional spaces, i.e. the analysis layer: Mathlib has Hilbert
spaces, Sobolev spaces and the Laplacian as a map between them, but no Schrödinger operator, no
self-adjointness of −Δ + V, and no ground state. **Out of reach as a formalisation; it is new mathematics
first (Orientation §5 already said so), and the analytic infrastructure would have to be built as well.**

## 4. The honest summary

Mathlib is strong exactly where plan 05's *algebra* lives — finite-dimensional symmetric operators,
their spectra, rank, positivity, commuting families, exterior powers with the Slater inner product — and
empty where the *physics* lives: no Hamiltonian, no Fock space, no Schrödinger operator, no
Courant–Fischer, no greedy colouring. So the Lean route can referee E1 claims of the kind "this
truncation of a finite symmetric problem is exact under hypothesis h" (T1, and the statements of T2),
and cannot yet touch claims about the continuum problem (T3). That matches the Orientation's assessment
and sharpens it: the first Lean file, if the user wants one, is T1, and it needs (i) `elan` + `lake`
and a Mathlib cache on the laptop (several GB; a light Windows-side install, allowed beside an anchor
job), (ii) a pinned Mathlib version recorded in `lean/lakefile`, and (iii) the greedy colouring lemma as
its first proved statement.

## 5. Ledger change

Lean route: **proposed → assessed (X4 done)**. Infrastructure sufficient for T1 and for stating T2;
T3 out of reach. *Same evening:* the user decided to install; `lean/` exists (Lean v4.34.0-rc2, Mathlib
`v4.34.0-rc2`), builds, and T1a is proved — see `lean/README.md` and the ledger.

## Sources fetched 2026-09-12 (Mathlib4 documentation, `master`)

- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/Rayleigh.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/Spectrum.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Matrix/Spectrum.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Matrix/Rank.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Matrix/PosDef.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/Adjoint.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/Positive.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/JointEigenspace.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/LinearPMap.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/ExteriorPower.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/InnerProductSpace/Laplacian.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/ExteriorAlgebra/Basic.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/CliffordAlgebra/Basic.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Distribution/Sobolev.html
- https://raw.githubusercontent.com/leanprover-community/mathlib4/master/Mathlib/Combinatorics/SimpleGraph/Coloring/Vertex.lean
  (and the directory listings via https://api.github.com/repos/leanprover-community/mathlib4/contents/…)
- Loogle: https://loogle.lean-lang.org/ (name searches "Courant", "minmax", "rayleigh", "Sobolev")
- Literature already in the Orientation: Moura & Ullrich (2021); The mathlib Community (2020); Coleman &
  Moré (1983); Powell & Toint (1979). The Gagliardo–Nirenberg–Sobolev formalisation: "A Formalization of the
  Gagliardo-Nirenberg-Sobolev Inequality", ITP 2024, LIPIcs vol. 309, paper 37 (title and venue from the
  search result list; authors not recorded here because the paper was not opened).
