# Plan 06 — note (2026-09-12): the symmetric-conflict question for T1b, and a correction to X1

*Written before T1b is attempted in Lean, to fix the mathematics first. It answers "which columns must a
colouring separate when a symmetric matrix may be read from either side?", finds that the answer is not a
graph on the columns at all, and — while checking what experiment X1 had actually coloured — finds that
X1's "4–5 products" count was a colouring of the wrong graph. The corrected counts are printed by
`experiments/x1b_symmetric_colouring.py` (table in §6). Everything mathematical below is derived here
and is elementary; the two classical papers are cited as verified records only, not for their content
(neither has been read).*

## 1. Setting

- `A` a real `n × n` matrix, `P ⊆ n × n` a pattern with `A_ij = 0` outside `P`; the diagonal is always
  in `P` (plan 05 always probes it). `H` is the *pattern graph*: `i ~ j` iff `i ≠ j` and `(i, j) ∈ P`.
- A colouring `c : n → colours`, its colour classes `d_k` (0/1 vectors), and the probes `b_k = A d_k`.
  Row `i` of probe `k` is the sum of `A_ij'` over the columns `j'` of colour `k`.
- **Column-readable.** `A_ij` is *readable from column `j`* when no other column `j' ≠ j` with
  `(i, j') ∈ P` has the colour of `j`; then row `i` of probe `c(j)` *is* `A_ij` (T1a's `probe_eq_entry`).
- **Row-readable.** When `A` is symmetric, `A_ij = A_ji`, so `A_ij` is also *readable from column `i`*
  when no other column `i' ≠ i` with `(j, i') ∈ P` has the colour of `i`: row `j` of probe `c(i)`.

Two schemes follow:

| scheme | requirement on `c` | what T1 proves |
|---|---|---|
| CPR (Curtis–Powell–Reid; Coleman & Moré 1983) | every `(i, j) ∈ P` column-readable | = a proper colouring of the *column-intersection graph* `H_cpr` (columns adjacent when some row holds both); T1a proved, T1c gives `Δ(H_cpr) + 1` colours |
| symmetric direct (this note; cf. Powell & Toint 1979, Coleman & Moré 1984, unread) | every `(i, j) ∈ P` column-readable **or** row-readable | T1b, to be proved on the definition of §2 |

## 2. Definition and the two easy theorems

**Definition (symm-valid).** `c` is *symmetrically valid for `P`* when for every `(i, j) ∈ P`:
`readable_col(i, j) ∨ readable_col(j, i)`, where
`readable_col(i, j) := ∀ j', (i, j') ∈ P → j' ≠ j → c(j') ≠ c(j)`.

**Theorem A (recovery; this is T1b).** If `P` is symmetric, `A` is symmetric and respects `P`, and `c`
is symm-valid, then `A` is determined by the probes: define
`recover₂(i, j) := if (i, j) ∉ P then 0 else if readable_col(i, j) then b_{c(j)}(i) else b_{c(i)}(j)`.
*Proof.* Outside `P` both sides are 0. Inside, if column-readable, `b_{c(j)}(i) = A_ij` by T1a's key
identity. Otherwise symm-validity gives `readable_col(j, i)`, so `b_{c(i)}(j) = A_ji = A_ij` by the same
identity applied to the entry `(j, i) ∈ P` (symmetry of `P`) and the symmetry of `A`. ∎
The predicate `readable_col` depends only on `P` and `c`, so `recover₂` is a function of the probes and
the pattern, as required. This is the statement to put in Lean, in place of the vacuous placeholder
(§4).

**Theorem B (the order of the three counts).**
(i) CPR-valid ⇒ symm-valid (trivially: the left disjunct always holds).
(ii) symm-valid ⇒ `c` is a proper colouring of `H`. *Proof.* Let `i ~ j` and suppose `c(i) = c(j)`.
For the entry `(i, j)`: `readable_col(i, j)` fails, because the column `j' = i` has `(i, i) ∈ P` (the
diagonal), `i ≠ j`, and `c(i) = c(j)`. Symmetrically `readable_col(j, i)` fails with `i' = j`. So the
entry is unreadable both ways, contradicting symm-validity. ∎
Hence `χ(H) ≤ (symmetric count) ≤ (CPR count) = χ(H_cpr)`, and a proper colouring of `H` alone is
**necessary but not sufficient** for either scheme. This is the fact X1 missed (§6).

## 3. Is "symm-valid" a proper colouring of some fixed graph on the columns? No.

If it were, there would be a graph `G` on the columns such that `c` is symm-valid iff `c` is proper on
`G`. Then whether two columns `u, w` may share a colour would depend only on the pair `(u, w)`. It does
not. Take the path `a – b – c – d` (pattern: the four diagonal entries and the three edges, symmetric).

- Colouring `(a, b, c, d) ↦ (1, 2, 1, 2)` is proper on `H` but **not** symm-valid: for the entry
  `(b, c)`, `readable_col(b, c)` fails (column `a` sits in row `b` with the colour of `c`) and
  `readable_col(c, b)` fails (column `d` sits in row `c` with the colour of `b`).
- Colouring `(1, 2, 1, 3)` **is** symm-valid: `(b, c)` is now row-readable (no other column in row
  `c` has colour 2); `(a, b)` is column-readable (no other column in row `a` has colour 2); `(c, d)`
  is column-readable (no other column in row `c` has colour 3); the diagonals are readable because
  the colouring is proper on `H`.

So `a` and `c` may share a colour in the second colouring and may not in the first, with the same
pattern. The constraint on the pair `(a, c)` depends on the colour of `d`. Therefore **there is no
"symmetric-conflict graph"** whose proper colourings are exactly the symm-valid colourings; the
condition is a constraint on paths of three edges, not on pairs. (The literature's name for the class
of colourings that make the symmetric direct method work is to be read from Coleman & Moré 1984
before it is quoted; this note claims nothing about what that paper calls it.)

Two consequences. (i) T1b must be stated with the per-entry predicate of §2, not with a graph.
(ii) The symmetric scheme's advantage over CPR is real and can be large: on the star `K_{1,m}` with
centre `0` and the diagonal in `P`, `H_cpr` is the complete graph on `m + 1` vertices (every two
leaves share row `0`), so CPR needs `m + 1` colours, while `centre ↦ 1, every leaf ↦ 2` is symm-valid
(entry `(0, leaf)`: row-readable, since the centre is the only column of colour 1; entry
`(leaf, leaf)`: column-readable, since leaves are not adjacent): **2 colours against `m + 1`.**

## 4. What changes in `lean/`

The placeholder `symmetric_recovery_shape` ("there is a subgraph `G` of `H_cpr` all of whose
colourings recover symmetric matrices") is **vacuous**: `G = H_cpr` itself satisfies it by T1a. It is
replaced by the statement of Theorem A:

```lean
def ReadableCol (P : Pattern n) (c : n → α) (i j : n) : Prop :=
  ∀ j', (i, j') ∈ P → j' ≠ j → c j' ≠ c j
def SymmValid (P : Pattern n) (c : n → α) : Prop :=
  ∀ i j, (i, j) ∈ P → ReadableCol P c i j ∨ ReadableCol P c j i
def recover₂ … : Matrix n n ℝ   -- as in §2, with the probes `fun k => A *ᵥ classVec' c k`
theorem recover₂_probe (hP : P.IsSymm) (hA : Respects P A) (hAs : A.IsSymm) (hc : SymmValid P c) :
    recover₂ P c (fun k => A *ᵥ (fun j => if c j = k then 1 else 0)) = A
```
Here `c` is a plain function (Theorem B(ii) shows properness on `H` follows; it need not be assumed).
The proof is the proof of Theorem A: `probe_eq_entry` generalised to a plain function under the
`ReadableCol` hypothesis, then the symmetric case. This is the next Lean step; the greedy Δ+1 bound
does not transfer to the symmetric scheme as a theorem (there is no graph to bound), so the symmetric
*count* stays a printed number from a verified colouring, not a theorem — which is what §6 does.

## 5. References (Crossref records verified 2026-09-12; texts not read)

- Powell, M. J. D., & Toint, Ph. L. (1979). On the estimation of sparse Hessian matrices. *SIAM Journal
  on Numerical Analysis, 16*(6), 1060–1074. https://doi.org/10.1137/0716078 — already in the
  Orientation's list.
- Coleman, T. F., & Moré, J. J. (1984). Estimation of sparse Hessian matrices and graph coloring
  problems. *Mathematical Programming, 28*(3), 243–270. https://doi.org/10.1007/BF02612334 — **new**;
  the Orientation cites their 1983 Jacobian paper (DOI 10.1137/0720013), which is the CPR / T1a side.
- Reading owed before either is quoted for content: what class of colourings each paper proves
  sufficient (and necessary) for the symmetric direct method, and whether it coincides with §2.

## 6. Correction to X1: the "4–5 products" were a colouring of the wrong graph

Checking `experiments/x1_x2_benzene.py` for this note: its `greedy_colouring(adj)` coloured `H`
itself (columns adjacent when `|Δ₂,ij| > θ`), and the result note called that "the greedy colouring
bound for exact sparse recovery (Powell–Toint / Coleman–Moré type)". By Theorem B(ii) a proper
colouring of `H` is only a **lower bound** for both schemes. `x1b_symmetric_colouring.py` recomputes
the three counts on the same tensor and θ grid and verifies each colouring against the definitions
of §1–2 (only verified colourings are counted; the symmetric greedy is a heuristic, so (c) is an upper
bound on the best symmetric count):

| σ_E (µE_h) | θ (µE_h) | off-diag > θ | Δ(H) | Δ(H_cpr) | (a) X1's count = χ-greedy(H) | (a) unreadable entries | (b) CPR, verified | (c) symmetric, verified | energies at 2M per product (a / b / c) |
|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.25 | 87 | 15 | 26 | 5 | 122 of 204 | **18** | **14** | 300 / 1080 / 840 |
| 0.5 | 0.50 | 66 | 12 | 23 | 4 | 100 of 162 | **15** | **12** | 240 / 900 / 720 |
| 0.5 | 1.25 | 51 | 10 | 18 | 4 | 70 of 132 | **11** | **9** | 240 / 660 / 540 |
| 0.5 | 2.50 | 45 | 6 | 7 | 4 | 72 of 120 | **8** | **7** | 240 / 480 / 420 |
| 1.0 | 0.50 | 66 | 12 | 23 | 4 | 100 of 162 | **15** | **12** | 240 / 900 / 720 |
| 1.0 | 1.00 | 53 | 11 | 19 | 4 | 72 of 136 | **12** | **10** | 240 / 720 / 600 |
| 1.0 | 2.50 | 45 | 6 | 7 | 4 | 72 of 120 | **8** | **7** | 240 / 480 / 420 |
| 1.0 | 5.00 | 44 | 6 | 7 | 4 | 72 of 118 | **8** | **7** | 240 / 480 / 420 |

**Reading.** Under X1's colourings, 70–122 of the 118–204 pattern entries are unreadable from either
side — the colourings do not recover the matrix at all. The honest counts are **8–18 products (CPR)**
and **7–14 products (symmetric direct, greedy, verified)** at benzene, i.e. **420–1080 energies at
2M energies per product**, against plan 05's measured **K = 448**. The T1c bound `Δ(H_cpr) + 1` =
8–27 is respected by (b). So the X1 sentence "240–300 energies against 448 — better, not
transformative" becomes: **at benzene, exact recovery by products costs about as much as, or more
than, the plan-05 deck if a product costs 2M energies; S5 pays only if a Hessian–vector product is
much cheaper than 2M energies — which is exactly the automatic-differentiation gradient condition of
plan 05's side project M2.** The status of S5 in the ledger ("alive, conditional on M2's measured
gradient cost") is unchanged in words and sharper in numbers; the low-rank part of X1 (rank full) is
untouched.

## 7. Ledger and document changes made with this note

- X1 result note: dated correction paragraph pointing here; the ledger row S5 and the Orientation's
  X1 bullet carry the corrected counts; the Lean file header and the corollary's docstring no longer
  quote "4–5".
- `lean/`: the placeholder T1b statement replaced by Theorem A's statement (still `sorry`).
- Reading list: Coleman & Moré 1984 added (verified record).
