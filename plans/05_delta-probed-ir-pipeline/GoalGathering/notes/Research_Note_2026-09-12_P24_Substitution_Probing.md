# Research note 2026-09-12 — P24: substitution probing as a second measurement layer (transfer from plan 06, direction S5)

**Status.** A proposal for the user, not a decision. Nothing in the Ladder, the Budget or the deck changes until
it is accepted; if accepted it enters as a dated note that adds one measurement to the R0 pilot and one
pre-registered comparison, and nothing else. Written the day plan 06's X1 series finished (X1b correction,
X1c count, X1d noise), under plan 06's protocol §6.3: a result of plan 06 reaches plan 05 only through a
plan-05 dated note or decision proposal. The user asked the same evening whether plan 05's computations can be
shortened with plan 06's ideas; this note is the honest answer, including the part that says "not yet".

## 1. The idea in one paragraph

Plan 05 measures the correction matrix Δ₂ element by element with a fixed deck of energies (K = 448 at benzene,
measured; K = 2M + K_off, one ± pair per mode for the diagonal and about one energy per coupling under the
symmetry prior). Plan 06 asked whether Δ₂ can instead be read from a few *matrix–vector products* A·d_k, with
d_k the 0/1 indicator vectors of a colouring of the sparsity pattern (Curtis–Powell–Reid 1974; Coleman & Moré
1983, 1984; Powell & Toint 1979). Verified on the sealed benzene dry-run tensor: the pattern-graph colouring
X1 first printed (4–5 products) was invalid; the valid direct schemes need 8–18 (CPR) or 7–14 (symmetric
direct) products; Powell & Toint's **triangular substitution needs 6–7 products**, meets Coleman & Moré's lower
bound, recovers the matrix exactly on noise-free data, and under plan 05's own noise model moves band positions
by 0.10 cm⁻¹ (median) against 0.07 for the full deck — a magnification of 1.4–1.5, no trial above 0.5 cm⁻¹
(plan 06 notes X1b, X1c, X1d; the Lean file `plan 06/lean/` proves the recovery theorems T1a–T1c). So the
*algebra* is sound and the *noise* is tolerable. What plan 06 cannot supply is the price of one product in
plan 05's engine — and that price decides everything.

## 2. The cost of a product, stated honestly (this corrects the headline of X1c/X1d)

Plan 06 priced a product at "2M energies" (X1's convention). That convention assumes a gradient costs M
energies, i.e. one-sided first differences — an accuracy plan 05 never accepts (its deck uses symmetric
patterns throughout). The three honest options:

| how the product A·d is obtained | energies per product (M = 30 at benzene) | 6 products | against K = 448 |
|---|---|---|---|
| energies only, second-order: each component `(A d)_i` from the four points `x ± h e_i ± h' d` | ≈ 4M = 120 (a little less with shared points) | **≈ 720** | **more, not fewer** |
| energies only, one-sided (X1's "2M") | 2M = 60 | 360 | fewer, at an accuracy the plan does not accept |
| two analytic gradients at `x ± h' d` (the side project's mode G, milestone M2: LNO-CCSD(T) gradients by automatic differentiation) | 2 × (cost of one gradient in energy units) | 12 × g | fewer by a large factor if g ≲ 10; e.g. g = 4 → 48 energies |

So: **with energies alone, substitution probing does not shorten plan 05's computations at benzene** (720
against 448). It shortens them only if the frozen-space engine delivers gradients, at which point the saving is
not 20 % but an order of magnitude — and it grows with size, because the deck grows with M² while the
substitution count grows with the largest row count of the pattern (Coleman & Moré's `maxr`; 6 at benzene).
This is exactly the question the side project's milestone M2 was pre-registered to measure (cost and accuracy
of an LNO-CCSD(T) gradient with frozen spaces, AD against finite differences), and it is why plan 06's ledger
already said "conditional on M2". P24 does not change that dependence; it fixes what M2's number is *for*.

## 3. What P24 asks plan 05 to add (two items, both after the R0 pilot deck exists)

1. **One measurement, inside the R0 pilot.** In the frozen-space arm at benzene, at the reference geometry,
   one Hessian–vector product along one colour-class vector `d_k` of the X1c colouring (the 6-colour
   substitution colouring on the benzene pattern at θ = 0.5 µE_h, stored with X1c's outputs), obtained the
   *cheapest way the engine then has*: by energies (4 points per component) if M2 has not licensed gradients,
   by two gradients if it has. Printed: energies (or gradient-equivalents) spent, wall time, and the noise of
   the product's components against the deck's per-element σ_E — the "g" of the table above, measured.
2. **One pre-registered comparison, on the R0 pilot deck.** Reconstruct Δ₂ (i) from the deck as the plan does,
   (ii) from the 6 substitution products (all six measured the same way as item 1). Compare the two Δ₂'s and
   the harmonic band positions they give. **Winning condition:** band positions agree within the plan's own
   noise budget for R0 (the X2 rule's 0.5 cm⁻¹, or the pilot note's tighter figure if it sets one) *and* the six
   products cost fewer energies than the deck. **Losing condition:** either fails. Written now so that the
   result cannot shape the rule.

Nothing else: no change to the deck, the licence tests, the tolerances or the calendar. The energies of item 1
and 2 are ≈ 720 at benzene if measured by energies (about 1.6 decks; a laptop-week at xtight) — which is why
the pre-registration says "the cheapest way the engine then has": if M2 fails, item 2 is run only if the user
accepts that cost as the price of the answer; if M2 succeeds, items 1 and 2 are cheap.

## 4. What happens on success and on failure

- **Success (both conditions met):** substitution probing enters the Ladder by a dated note as a **second
  measurement layer** beside the deck, licensed per rung like everything else: at each new rung the six-ish
  products are compared with the deck once before they replace it; the pattern comes from the symmetry prior
  at R0–R1 and, if Module 05 earns its licence, from the learned prior above. The Budget's per-rung cost
  sentences get a second column. The deck remains the reference object; the licence comparison (decision 33
  terms, canonical points) is untouched because it concerns energies, not the probing scheme.
- **Failure:** the note records the measured g and the band-position error, plan 06's S5 is closed for plan 05
  at the "energies only" level, and the direction survives only as the gradient-conditional statement it
  already is. No other rule moves.

## 5. Why it is worth pre-registering now

Three reasons. (i) The algebra is settled and machine-checked; the only unknown is an engine number that the
plan already intends to measure (M2), so the marginal cost of the pre-registration is a page. (ii) The
substitution scheme is the *only* route found so far by which the number of expensive energies could stop
growing quadratically with the molecule — the cost question of §4 of the proposal — and plan 06 exists to find
such routes; a pre-registered test is how the plan turns an idea into a measured yes or no. (iii) Writing the
losing condition today keeps the plan's discipline: if the products turn out to cost 720 energies, that is a
result, printed, not an argument.

## 6. Bookkeeping if accepted

Decision number next in line (34); Ladder §3 dated note (second measurement layer, licensed per rung);
Budget dated note (the two items' cost, ≈ 720 energies by energies at benzene, or 12 g with gradients);
Research_Note Probe M1 gains the R0-pilot item; plan 06 ledger: S5 → "in plan 05's pilot, P24 accepted";
Software_Changes_Ledger unaffected. The proposal to the supervisor is not changed for Monday: §4 already names
the cost question and §6 the side project; P24 becomes a §10 item only when accepted.

## References (verified records; the 1984 paper read in full as Cornell TR 82-535 on 2026-09-12)

- Curtis, A. R., Powell, M. J. D., & Reid, J. K. (1974). *IMA J. Appl. Math.* 13(1), 117–119. DOI 10.1093/imamat/13.1.117
- Coleman, T. F., & Moré, J. J. (1983). *SIAM J. Numer. Anal.* 20(1), 187–209. DOI 10.1137/0720013
- Coleman, T. F., & Moré, J. J. (1984). *Math. Programming* 28(3), 243–270. DOI 10.1007/BF02612334
- Powell, M. J. D., & Toint, Ph. L. (1979). *SIAM J. Numer. Anal.* 16(6), 1060–1074. DOI 10.1137/0716078 (not read; supervisor PDF request item 29)
- Plan 06: `GoalGathering/Note_2026-09-12_T1b_…`, `Result_Note_2026-09-12_X1d_…`, `Reading_Note_2026-09-12_Coleman_More_1984_…`; `experiments/x1b_…`, `x1c_…`, `x1d_…`; `lean/Plan06/T1/MeasurementAlgebra.lean`.
