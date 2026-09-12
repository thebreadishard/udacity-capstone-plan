# Plan 06 — result note X1 / X2 (2026-09-12): what the benzene Δ₂ actually needs

*Printed by `experiments/x1_x2_benzene.py` on plan 05's sealed dry-run tensor (benzene, B3LYP → BHHLYP,
6-31G*, M = 30; a stand-in with the algebraic form of CC − DFT, not CC − DFT itself). Full tables in
`experiments/x1_x2_benzene.md`. Nothing here changes plan 05; both directions go to the ledger as alive.*

## X2 — direction S4 (reduce the target): almost no off-diagonal element moves a band position

Exact harmonic positions from diag(ω²) + Δ₂, benzene:

| quantity | measured |
|---|---|
| shift from the diagonal of Δ₂ alone | −18.2 to +81.1 cm⁻¹ per band |
| largest band change when **all 435** off-diagonal elements are dropped | 19.58 cm⁻¹ |
| off-diagonal pairs whose removal moves any band by > 0.5 cm⁻¹ | **6 of 435** (16 above 0.1 cm⁻¹) |
| the one pair that carries the effect | modes 15/18 (1186 / 1357 cm⁻¹): 19.58 cm⁻¹; the next 1.7, 1.0, 0.9, 0.8, 0.8 |
| elements that move any band by > 0.5 cm⁻¹ when perturbed by plan 05's own per-element noise (σ_E/2 per q², σ_E = 0.5–1 µE_h) | **0** (largest effect 0.05 cm⁻¹) |

**Reading.** For *positions* at plan 05's tolerance, the off-diagonal part of Δ₂ is, on benzene, one
strong coupling plus a handful of weak ones; the rest of the 435 elements could be zero without a
scored consequence. Plan 05's mode-E deck spends 388 of its 448 energies on those 435 elements. That
is not a mistake of plan 05 — the deck was budgeted without a prior precisely because no one knew
which elements matter — but it is a measured statement that the *scored* information is far smaller
than the matrix, which is what S4 conjectured. Two caveats that keep this a first test and not a
finding: (i) the stand-in functional pair may place the couplings differently from CC − DFT; the
sealed benzene points of probe M1 can settle that once Δ₂'s off-diagonal elements exist at CC level;
(ii) the plan's VPT2 step uses Δ₂ through the corrected normal modes as well, and the six-pair count
is a harmonic-position statement only. **Consequence for plan 06:** S4 is alive at level E3, and its
next test is the same count on the naphthalene dry-run tensor when it exists (does the "one strong
pair" pattern persist, and is it a resonance-like near-degeneracy or a family coupling?).

## X1 — direction S5 (query algebra): exact recovery needs few products, but products are dear

| scheme | count at benzene |
|---|---|
| plan 05 mode E, measured | 448 energies |
| dense symmetric lower bound, mode E (± pairs) | 930 energies |
| off-diagonal elements above 1 µE_h | 53 of 435 |
| exact sparse recovery of the pattern above θ (Powell–Toint / Coleman–Moré type), greedy colouring bound | **4–5 Hessian–vector products** (θ from 0.25 to 5 µE_h) |
| the same expressed in energies if a product costs 2M energies | 240–300 |
| numerical rank at the noise level | 30 of 30 — Δ₂ is **not** low-rank; the randomised low-rank route needs r + p = 35 products |

**Reading.** The sparsity is real (53 elements above 1 µE_h) and the exact-recovery algebra is cheap
in *products*: four or five Hessian–vector products would recover every element above the noise on
benzene. The obstacle is the price of a product: plan 05's local-CC engine has no analytic gradient,
and a canonical CCSD(T) gradient cost about fifty energies at cc-pVDZ, so in energies the scheme is
240–300 against 448 — better, not transformative, and only if the sparsity pattern is known in
advance (which is what the symmetry prior and, later, the learned prior of Module 05 provide). Low
rank is not there: the singular values fall slowly and the rank at the noise level is full.
**Consequence:** S5 stays alive on the condition "a cheap Hessian–vector product exists"; that
condition is a literature question about local-CC analytic gradients (Nagy & Kállay's LNO family has
published gradient work; to be read, not recalled) and is the first thing to check before any more
algebra.

## S5's condition, checked the same day (Crossref search 2026-09-12, records only, papers not read)

Analytic gradients for local correlation methods are published at the **MP2** level — DLPNO-MP2:
Pinski & Neese, *J. Chem. Phys.* 148 (2018), DOI 10.1063/1.5011204 (communication) and *J. Chem.
Phys.* 150 (2019), DOI 10.1063/1.5086544 (full). For **local CCSD or CCSD(T)** (DLPNO, PNO-LCCSD,
LNO) the same search returned no analytic-gradient record; a numerical gradient of a local-CC energy
costs 2 × 3N energies (72 at benzene), more than the 2M = 60 energies a Hessian–vector product by
energies would cost. So, as far as verified today, **no cheap product exists at the anchor's level**;
the X1 counts (4–5 products) stay a statement about the algebra, not about a route. A deeper search
(the ORCA and MRCC literature since 2020) is the only thing that could revive S5; until then it is
parked, not dead.

## Ledger changes

S4 → alive (E3), next test on the naphthalene tensor. S5 → **parked** (no verified local-CC(T)
analytic gradient; MP2-level gradients exist); revives only on a verified record. X1, X2 done.
