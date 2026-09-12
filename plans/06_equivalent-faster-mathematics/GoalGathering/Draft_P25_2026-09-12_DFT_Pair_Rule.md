# Draft P25 (2026-09-12, evening; NOT submitted to plan 05) — a free DFT rule inside the symmetry prior: which off-diagonal pairs the deck measures first

*Written in plan 06 under its protocol §6.3 (a plan-06 result reaches plan 05 only through a plan-05 dated note or decision proposal). This is the draft of such a proposal, kept in plan 06 until two things happen: the user decides it should be made, and the naphthalene repeat of X10 (the licence test below) has run. Until then nothing in plan 05 changes. Form and discipline follow P24 (decision 34).*

## 1. The idea in one paragraph

Plan 05's deck measures the diagonal of Δ₂ (2 energies per mode) and then the off-diagonal pairs the symmetry prior allows (same irreducible representation; 2 energies per pair in the deck's two-mode patterns), in an order set by the dry run's stopping rule. X10 (plan 06, 2026-09-12) shows on the benzene stand-in tensor that the pairs which move a band position can be ranked **before anything is measured**, from the DFT Hessian alone: by the resonance denominator 1/|ω_i² − ω_j²| within an irrep, the DFT-only part of the second-order band shift Δ_ij²/|ω_i² − ω_j²|. Ranked that way, 19 of the 47 eligible benzene pairs hold every band within 0.5 cm⁻¹ of the full correction (a perfect element-size prior: 17; the best possible order: 6); Spearman 0.75 against the measured effect. The rule is free, needs no model, and stacks with the substitution layer of decision 34 (X11: 4 products on the 19-pair pattern against 7 on the full symmetry prior).

## 2. What P25 would ask plan 05 to change — and what not

**Change:** the *order* in which the off-diagonal pairs enter the deck, and nothing else. The symmetry prior stays the outer filter; the stopping rule (decisions 8, 9, 12, on ρ_off with constant c) stays the judge of when to stop; the hold-out, the noise column and the licence tests are untouched. The deck's pair batches are filled in decreasing order of 1/|ω_i² − ω_j²| (the DFT Hessian's own frequencies) instead of the dry run's present order. If the rule is good, the stopping rule stops earlier; if it is useless, the stopping rule stops where it would have anyway. **The rule cannot make the deck worse than the present order; it can only make it stop sooner.** That is why it can be proposed as an ordering rather than a truncation.

**Not changed:** no pair is excluded by the rule; K is still read from ρ_off; no tolerance, no gate, no calendar moves. The Module-05 learned prior, if it earns its licence, replaces this ordering by a better one (X10: the oracle magnitude ordering saves two more pairs at benzene) — P25 is the baseline that prior must beat, which the pilot note's item 5 already records.

## 3. The licence test, pre-registered (the naphthalene repeat of X10)

On the naphthalene dry-run tensor (after machine-queue item 5; the B3LYP half already exists in plan 02's stored Hessian), the same three rankings over the eligible pairs (same irrep of D2h, degenerate partners excluded — none in D2h), the same exact harmonic rule:

- **Winning condition:** the DFT-only ranking reaches 0.5 cm⁻¹ with at most half the eligible pairs, and lies within a factor 1.5 of the oracle-magnitude ranking's count.
- **Losing condition:** more than half the eligible pairs, or a factor above 1.5 — then the rule is recorded as benzene-only and P25 is withdrawn without entering plan 05.
- Printed either way: the counts, the Spearman correlations, the top-10 lists, and the substitution counts on the selected patterns (X11's table for naphthalene).

## 4. Honest cost and honest value

- **Cost of the test:** minutes of numpy once the tensor exists; the tensor itself is the DFT dry run plan 05 owes anyway.
- **Value if licensed, at benzene's ratio:** the off-diagonal part of the R1 deck (282 energies, proposal §3.2) shrinks by up to a factor 2.5 → the deck from 474 to ≈ 300 energies (the cost ladder's lever B); with the substitution layer and gradients (decision 34's conditional branch) from 14 to 8 gradients per correction at benzene. The ratio at naphthalene is what the test measures; it may be smaller.
- **What it does not do:** it does not touch the price per energy, which is where the calendar lives (P13); it reorders what the deck measures, so its saving is bounded by the deck's off-diagonal share.

## 5. Bookkeeping if the user makes it a proposal and it is accepted

Decision number next in line; Ladder §3 dated note (the ordering rule inside the symmetry prior, licensed per rung like everything else, with the naphthalene test as its first licence); Budget dated note (lever B's factor as measured at naphthalene); the dry-run deck builder gains the ordering (a ledger row in `Software_Changes_Ledger.md`: own layer, no third-party change); pilot-note skeleton item 5 already carries the baseline. The proposal to the supervisor is unchanged.

## References

- Plan 06: `Result_Note_2026-09-12_X10_DFT_Predictable_Pairs.md` (X10, §5 X11), `Result_Note_2026-09-12_X1_X2_Benzene.md` (X2), `Cost_Ladder_2026-09-12_Network_Data.md`; `experiments/x10_dft_predictable_pairs.py`, `x11_sparse_pattern_products.py`.
- Plan 05: `probes/results_dryrun/benzene/deck.json` (the deck's pattern conventions), `stageC_symmetry_prior.json` (the eligible pairs), decisions 8, 9, 12, 34.
