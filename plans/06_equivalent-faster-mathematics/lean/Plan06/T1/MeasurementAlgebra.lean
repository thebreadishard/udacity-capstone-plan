import Mathlib

/-!
# T1 — the measurement algebra of plan 05's probing deck (direction S5)

Plan 06, first formal target (Orientation §5; reading note X4, 2026-09-12).

**Informal statement.** Let `A` be a real `n × n` matrix whose non-zero entries lie inside a known
*pattern* `P ⊆ n × n`. Build the *column-intersection graph* of `P`: columns `j ≠ j'` are adjacent
when some row `i` has both `(i, j)` and `(i, j')` in `P`. Let `c` be a proper colouring of that
graph. Then `A` is determined exactly by the products `A · d_k`, where `d_k` is the 0/1 indicator
vector of colour class `k` — one matrix–vector product per colour. This is the Curtis–Powell–Reid
scheme (1974) in the graph language of Coleman & Moré (1983). It is the algebra behind experiment
X1's count ("4–5 Hessian–vector products recover every element above the noise at benzene").

**What is proved here (T1a).** `recover_probe`: the entries of `A` inside `P` are read off the
probes, so the reconstruction map returns `A` itself. No `sorry`.

**What is stated and owed (T1b, T1c).** The symmetric refinement of Powell & Toint (1979), where a
symmetric `A` may be read at `(i, j)` *or* `(j, i)` and fewer colours suffice, and the greedy bound
"a graph with maximum degree `Δ` is `(Δ + 1)`-colourable", which turns the theorem into the count of
X1. Both carry `sorry` and are the next two proofs. Before proving T1c, search Mathlib for it
(`exact?`); the X4 survey found no such lemma in `Combinatorics/SimpleGraph/Coloring/Vertex.lean`
on 2026-09-12, but Mathlib moves.

Conventions: everything is finite-dimensional; the matrix ring is `ℝ` (plan 05's numbers are real);
`Matrix.mulVec` is `A *ᵥ v`, with `(A *ᵥ v) i = ∑ j, A i j * v j`.
-/

namespace Plan06.T1

open Matrix Finset

variable {n : Type*} [Fintype n]

/-- A sparsity pattern: the set of index pairs allowed to be non-zero. -/
abbrev Pattern (n : Type*) := Finset (n × n)

/-- `A` respects the pattern `P`: every entry outside `P` is zero. -/
def Respects (P : Pattern n) (A : Matrix n n ℝ) : Prop :=
  ∀ i j, (i, j) ∉ P → A i j = 0

/-- The column-intersection graph of a pattern (Coleman & Moré 1983): two distinct columns are
adjacent when some row holds both of them in the pattern. -/
def colGraph (P : Pattern n) : SimpleGraph n where
  Adj j j' := j ≠ j' ∧ ∃ i, (i, j) ∈ P ∧ (i, j') ∈ P
  symm := ⟨fun _ _ ⟨h, i, hj, hj'⟩ => ⟨h.symm, i, hj', hj⟩⟩
  loopless := ⟨fun _ ⟨h, _⟩ => h rfl⟩

omit [Fintype n] in
/-- Adjacency in the column-intersection graph, unfolded. -/
theorem colGraph_adj (P : Pattern n) {j j' : n} :
    (colGraph P).Adj j j' ↔ j ≠ j' ∧ ∃ i, (i, j) ∈ P ∧ (i, j') ∈ P := Iff.rfl

variable {P : Pattern n} {α : Type*} [DecidableEq α]

/-- The 0/1 indicator vector of colour class `k` of a colouring `c`. -/
def classVec (c : (colGraph P).Coloring α) (k : α) : n → ℝ :=
  fun j => if c j = k then 1 else 0

/-- The measurement of `A` by colour class `k`: the matrix–vector product `A · d_k`.
In plan 05 one such product costs `2M` energies (a Hessian–vector product by finite differences). -/
def probe (c : (colGraph P).Coloring α) (A : Matrix n n ℝ) (k : α) : n → ℝ :=
  A *ᵥ classVec c k

omit [Fintype n] [DecidableEq α] in
/-- Two columns of the same colour never share a row of the pattern. -/
theorem not_mem_of_same_color (c : (colGraph P).Coloring α) {i j j' : n}
    (hij : (i, j) ∈ P) (hne : j' ≠ j) (hc : c j' = c j) : (i, j') ∉ P := by
  intro hij'
  exact c.valid ((colGraph_adj P).2 ⟨hne, i, hij', hij⟩) hc

/-- **Key identity (Curtis–Powell–Reid).** For `(i, j)` in the pattern, row `i` of the probe of
`j`'s colour class is exactly `A i j`: every other column of that colour is zero in row `i`. -/
theorem probe_eq_entry (c : (colGraph P).Coloring α) {A : Matrix n n ℝ} (hA : Respects P A)
    {i j : n} (hij : (i, j) ∈ P) : probe c A (c j) i = A i j := by
  unfold probe classVec
  simp only [mulVec, dotProduct]
  rw [Finset.sum_eq_single j]
  · simp
  · intro j' _ hne
    by_cases hc : c j' = c j
    · have h0 : A i j' = 0 := hA i j' (not_mem_of_same_color c hij hne hc)
      simp [h0]
    · simp [hc]
  · intro h
    exact absurd (Finset.mem_univ j) h

/-- The reconstruction map: inside the pattern, read the probe of the column's colour; outside,
zero. -/
def recover [DecidableEq n] (c : (colGraph P).Coloring α) (probes : α → n → ℝ) :
    Matrix n n ℝ :=
  fun i j => if (i, j) ∈ P then probes (c j) i else 0

/-- **T1a.** A matrix respecting `P` is recovered exactly from its colour-class probes. -/
theorem recover_probe [DecidableEq n] (c : (colGraph P).Coloring α) {A : Matrix n n ℝ}
    (hA : Respects P A) : recover c (probe c A) = A := by
  ext i j
  unfold recover
  split_ifs with h
  · exact probe_eq_entry c hA h
  · exact (hA i j h).symm

/-- **T1a, counted.** If the column-intersection graph is `k`-colourable, `k` matrix–vector
products determine every matrix respecting `P`: two such matrices with the same probes are equal. -/
theorem eq_of_probes_eq (c : (colGraph P).Coloring α) {A B : Matrix n n ℝ}
    (hA : Respects P A) (hB : Respects P B) (h : probe c A = probe c B) : A = B := by
  classical
  rw [← recover_probe c hA, ← recover_probe c hB, h]

/-! ## Owed: the symmetric refinement (T1b) and the greedy bound (T1c) -/

/-- The pattern of a symmetric matrix may itself be taken symmetric. -/
def Pattern.IsSymm (P : Pattern n) : Prop := ∀ i j, (i, j) ∈ P → (j, i) ∈ P

omit [Fintype n] in
/-- **T1b (owed; Powell & Toint 1979).** For a symmetric `A` with symmetric pattern, an entry
`A i j` may be read from the probe of `j`'s class at row `i` *or* from the probe of `i`'s class at
row `j`; a colouring only has to separate columns that would be *unreadable both ways*. The
statement below fixes only the shape of the claim: some subgraph of the column-intersection graph
(the symmetric-conflict graph, to be defined when this is proved) already has the recovery
property for symmetric matrices. -/
theorem symmetric_recovery_shape [Fintype n] (P : Pattern n) (hP : P.IsSymm) (A : Matrix n n ℝ)
    (hA : Respects P A) (hAs : A.IsSymm) :
    ∃ (G : SimpleGraph n), (∀ j j', G.Adj j j' → (colGraph P).Adj j j') ∧
      ∀ {β : Type} [DecidableEq β] (c : G.Coloring β), ∀ B : Matrix n n ℝ,
        Respects P B → B.IsSymm →
        (∀ k, A *ᵥ (fun j => if c j = k then (1 : ℝ) else 0) =
              B *ᵥ (fun j => if c j = k then (1 : ℝ) else 0)) → A = B := by
  sorry

/-- **T1c (owed; the greedy bound).** A finite graph with maximum degree `Δ` is
`(Δ + 1)`-colourable. With `Δ` the maximum number of conflicting columns in the pattern, this is
X1's "4–5 products" bound. Search Mathlib first (`exact?`), then prove by induction on the
vertex list. -/
theorem colorable_maxDegree_succ (G : SimpleGraph n) [DecidableRel G.Adj] :
    G.Colorable (G.maxDegree + 1) := by
  sorry

end Plan06.T1
