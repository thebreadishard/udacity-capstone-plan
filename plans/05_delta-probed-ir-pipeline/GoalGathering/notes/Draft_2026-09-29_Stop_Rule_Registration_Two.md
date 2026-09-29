# Draft, 29 September 2026 — stop-rule registration two (concept for the user; not registered)

*Written before reading (ii) reports (the band-free-prior run on the laptop, ≈ Wed 30 Sep evening), so that nothing here is fitted to its numbers. It is
the registered consequence of reading (i) of 28 September (`PreRegistration_2026-09-27_Wide_Candidate_Deck_Stop_Rule.md`, outcome 21:5x): the deck stays,
the stop rule's three ingredients are re-registered. Becomes a pre-registration only on the user's word.*

## What reading (i) showed, in one paragraph

Under P12 with the band prior the rule "stop at the second consecutive checkpoint with held-out ρ_off ≤ 0.3" fired within 2× the band deck on 53 % of the 97
evaluation molecules (line 90 %), and 29 % of those stops were false (truth-based off-diagonal error > 0.4; line 5 %). The mechanism was quantified: the
held-out set is the band deck's, so under a band-first order it reads ahead of the truth near the threshold (median truth error 0.34 at the crossing);
over all checkpoints the disagreement is rare (2 % under P12) and the two scales agree at the end of the pool. Three things were therefore wrong at once:
the held-out set (what it samples), the threshold (no margin for the held-out/truth gap), and the budget (2× the band deck is not what the wide pool costs).

## The three changes

1. **Held-out set drawn from the wide pool.** Before the run, 15 % of the two-mode patterns of the wide pool are held out, stratified by frequency gap
   (in band ≤ 200 cm⁻¹ / out of band), plus the multi-mode patterns as now; the deck orders the remaining 85 %. The stop quantity then measures what the
   deck buys, not what the band deck bought. Cost: the held-out energies are counted in the cost of every molecule (they are measured), as now.
2. **τ with a margin set on the validation split.** τ is not 0.3 by decree. On the validation molecules (the corpus split `val`, never the evaluation
   splits), the recovery is run to the end of the pool under P12 and the pair (held-out ρ_off, truth-based frob_off) is recorded at every checkpoint;
   τ is the largest threshold for which, at the first two consecutive checkpoints under τ, frob_off > 0.4 occurs on ≤ 2 % of validation molecules. τ is
   frozen before the evaluation molecules are read and written into the outcome. Prediction: τ lands between 0.20 and 0.27.
3. **B_max from the measured cost distribution.** B_max per molecule = 2 × the median cost at which the oracle reaches truth-based frob_off ≤ 0.3 on the
   validation split, expressed as a multiple of the molecule's single-mode block (so it scales with M), instead of 2 × the band deck. Prediction: B_max is
   3–4 × the block.

Unchanged: the checkpoint stride, the hysteresis (two consecutive checkpoints), the band-free solver prior as the Ladder default (amendment of 28 Sep),
the orders P0 / P12 / oracle, the reading conventions of the amendment (seed median, stop = second checkpoint, cost = energies beyond the block).

## Lines (fixed now; the evaluation splits only)

- **W1′:** the rule stops within B_max on ≥ 90 % of the 97 evaluation molecules under P12. Prediction: 85–92 % (the line is at risk on the substituted
  molecules, as in reading (i): parents 63 % / A2-B 45 % then).
- **W2′:** false stops (frob_off > 0.4 at the stop) ≤ 5 % of the stopped molecules under P12. Prediction: 3–6 %; the validation-set construction targets
  2 %, the evaluation set will be worse.
- **W2″ (new, the honest complement):** among molecules that do *not* stop within B_max, the truth-based error at B_max is ≤ 0.4 on ≤ 20 % — a rule that
  fails to stop on molecules that are in fact recovered is a cost failure, not a safety failure, and is reported as such.
- **W3:** unchanged (naphthalene at CC level through `hi_override`, with the analytic B3LYP low level per the 29 Sep amendment of the anchor set).

Fail: W1′ < 80 % or W2′ > 10 % — then the stop quantity itself (held-out ρ_off) is the wrong instrument and the next registration replaces it (candidates:
a cross-validated reconstruction error on a second held-out draw; the solver's own residual on a fresh random probe), not its threshold.

## What is not claimed

No claim about the learned order's quality beyond what E2 established; no claim at CC level except W3. The validation-split procedure fixes τ and B_max
once for the corpus at the proxy level; at CC level they are re-fitted when there are ≥ 10 CC-level molecules (the PC), under a registration of their own.

## Cost and where it runs

Reading on the laptop from the recorded curves where possible (the validation-split curves under P12 exist for the band deck; the wide-pool curves with
the new held-out set need a new run of `run_simulation.py` with a `--holdout wide` switch: ≈ 97 evaluation + ≈ 60 validation molecules, 8 shards, ≈ 2 days
at the laptop's present load — or 6 h on the PC). Build: the `--holdout wide` switch (deck-building change in `pp.core.export_molecule`, a new export
set), the τ-fitting reader (`stop_rule_readout.py --fit-tau`), tests for both. Nothing starts before the user's word and before reading (ii) is read.

*Scope note, 18:0x (the user): the wide deck is the only focus; the band deck is dropped as a comparison column, so this registration reports no band-relative numbers — costs are in energies beyond the block and as multiples of the block only.*
