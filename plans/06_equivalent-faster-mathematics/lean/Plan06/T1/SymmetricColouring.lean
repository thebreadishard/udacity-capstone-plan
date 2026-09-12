import Plan06.T1.MeasurementAlgebra

/-!
# T1d — Coleman & Moré's Theorem 2.2: symmetric validity is a path-of-length-3 condition

**DRAFT, NOT YET BUILT** (written 2026-09-12 evening while an anchor job owns the machine; a Lean build takes
8 GB and is not allowed beside it — probes/README rule of the same day). Not imported by `Plan06.lean` until
it compiles. Expect small fixes.

Statement (Coleman & Moré, Math. Programming 28 (1984), Theorem 2.2, read as Cornell TR 82-535 §2): for a
pattern that contains the diagonal, a colouring `c` is symmetrically valid (`SymmValid`, their "symmetrically
consistent partition") **iff** (a) it is proper on the pattern graph (adjacent columns get different colours)
and (b) no path of length 3 in the pattern graph is 2-coloured, i.e. for a path `a – b – x – y` (four distinct
vertices, consecutive ones adjacent) it is not the case that `c a = c x` and `c b = c y`.

The pattern graph here is our own `patGraph` (adjacent iff distinct and `(i, j) ∈ P`), defined for a
symmetric pattern so that adjacency is symmetric.
-/

namespace Plan06.T1

variable {n : Type*} {α : Type*}

/-- The pattern graph `G_s(A)` of Coleman & Moré: distinct indices are adjacent when the entry is in the
pattern (symmetrised, so the definition needs no symmetry hypothesis on `P`). -/
def patGraph (P : Pattern n) : SimpleGraph n where
  Adj i j := i ≠ j ∧ ((i, j) ∈ P ∨ (j, i) ∈ P)
  symm := ⟨fun _ _ ⟨h, hp⟩ => ⟨h.symm, hp.symm⟩⟩
  loopless := ⟨fun _ ⟨h, _⟩ => h rfl⟩

/-- Proper colouring of the pattern graph, stated on a plain function. -/
def ProperOnPattern (P : Pattern n) (c : n → α) : Prop :=
  ∀ i j, (patGraph P).Adj i j → c i ≠ c j

/-- No 2-coloured path of length 3 in the pattern graph: for consecutive adjacencies `a ~ b ~ x ~ y` with
`a ≠ x`, `b ≠ y`, `a ≠ y`, the colours cannot satisfy `c a = c x ∧ c b = c y`. -/
def NoTwoColouredP4 (P : Pattern n) (c : n → α) : Prop :=
  ∀ a b x y, (patGraph P).Adj a b → (patGraph P).Adj b x → (patGraph P).Adj x y →
    a ≠ x → b ≠ y → a ≠ y → ¬ (c a = c x ∧ c b = c y)

/-- **T1d, forward direction (their proof, second half).** Symmetric validity, with the diagonal in the
pattern and a symmetric pattern, gives a proper colouring with no 2-coloured `P₄`. -/
theorem symmValid_imp (P : Pattern n) (hdiag : ∀ i, (i, i) ∈ P) (hP : P.IsSymm) (c : n → α)
    (hc : SymmValid P c) : ProperOnPattern P c ∧ NoTwoColouredP4 P c := by
  refine ⟨?_, ?_⟩
  · -- proper: if i ~ j and c i = c j, the entry (i, j) is unreadable both ways because of the diagonal
    intro i j hij hcij
    have hne : i ≠ j := hij.1
    have hijP : (i, j) ∈ P := hij.2.elim id (fun h => hP j i h)
    rcases hc i j hijP with hr | hr
    · exact hr i (hdiag i) hne.symm hcij.symm rfl   -- column i' = i sits in row i (diagonal), i ≠ j, c i = c j
    · exact hr j (hdiag j) hne hcij rfl              -- column j' = j sits in row j (diagonal)
  · -- no 2-coloured path a – b – x – y: the entry (b, x) would be unreadable both ways
    intro a b x y hab hbx hxy hax hby hay ⟨hcax, hcby⟩
    have hbxP : (b, x) ∈ P := hbx.2.elim id (fun h => hP x b h)
    have hbaP : (b, a) ∈ P := hab.symm.2.elim id (fun h => hP a b h)
    have hxyP : (x, y) ∈ P := hxy.2.elim id (fun h => hP y x h)
    rcases hc b x hbxP with hr | hr
    · -- readable from column x at row b: no other column of colour c x in row b — but column a is one
      exact hr a hbaP hax hcax
    · -- readable from column b at row x: no other column of colour c b in row x — but column y is one
      exact hr y hxyP hby.symm hcby.symm

/-- **T1d, converse (their proof, first half).** A proper colouring with no 2-coloured `P₄` is symmetrically
valid, when the diagonal is in the pattern and the pattern is symmetric. -/
theorem symmValid_of (P : Pattern n) (hdiag : ∀ i, (i, i) ∈ P) (hP : P.IsSymm) (c : n → α)
    (hprop : ProperOnPattern P c) (hp4 : NoTwoColouredP4 P c) : SymmValid P c := by
  intro i j hij
  by_cases hij' : i = j
  · -- diagonal entry: readable from its own column because the colouring is proper
    subst hij'
    left
    intro j' hj' hne hcj
    exact hprop j' i ⟨hne, Or.inl (hP i j' hj')⟩ hcj
  · -- off-diagonal: suppose neither side is readable and build a 2-coloured path
    by_contra hnot
    push_neg at hnot
    obtain ⟨hnr1, hnr2⟩ := hnot
    -- not readable from column j at row i: some column a ≠ j in row i with c a = c j
    simp only [ReadableCol, not_forall, not_not] at hnr1 hnr2
    obtain ⟨a, haP, haj, hca⟩ := hnr1
    obtain ⟨y, hyP, hyi, hcy⟩ := hnr2
    -- a ≠ i (else c i = c j on an adjacent pair) and y ≠ j likewise; then a – i – j – y is a 2-coloured P₄
    have hij_adj : (patGraph P).Adj i j := ⟨hij', Or.inl hij⟩
    have hai : a ≠ i := by
      rintro rfl
      exact hprop a j hij_adj hca
    have hyj : y ≠ j := by
      rintro rfl
      exact hprop i y hij_adj hcy.symm
    have hia_adj : (patGraph P).Adj a i := ⟨hai, Or.inr haP⟩
    have hjy_adj : (patGraph P).Adj j y := ⟨hyj.symm, Or.inl hyP⟩
    by_cases hay : a = y
    · -- a = y: then c a = c j and c i = c a give c i = c j on the adjacent pair (i, j)
      subst hay
      exact hprop i j hij_adj (hcy.symm.trans hca)
    · exact hp4 a i j y hia_adj hij_adj hjy_adj haj hyi.symm hay ⟨hca, hcy.symm⟩

/-- **T1d.** Coleman & Moré's Theorem 2.2 in our terms. -/
theorem symmValid_iff (P : Pattern n) (hdiag : ∀ i, (i, i) ∈ P) (hP : P.IsSymm) (c : n → α) :
    SymmValid P c ↔ ProperOnPattern P c ∧ NoTwoColouredP4 P c :=
  ⟨symmValid_imp P hdiag hP c, fun h => symmValid_of P hdiag hP c h.1 h.2⟩

end Plan06.T1
