# Module 08 — pre-registration (frozen 28 September 2026, before phase 2 was built)

Source: `DESIGN_2026-09-27.md` §5 (Evaluation), written on 27 September before any code of this module existed; frozen here on 28 September when the
user decided §8 (decisions 1–4 as recommended; 5: build now) and the build started. Nothing below is changed after the run; the outcome section is
appended with its date.

## What is evaluated

The request officer, the certificate generator and the replay worker of `m08/`, run end to end from repository data (the website export
`website/export/out`, module 03's tolerance table, module 05's learning-curve records, module 07's rule table and gate, the measured price table
`m08/prices.py`). The pass lines below are the design's; S2b, S4b and S4c are added cases of the same kind, labelled *extra* in `scenarios/scenarios.json`.

| # | scenario | pass line | prediction |
|---|---|---|---|
| S1 | naphthalene (anchored) | a certificate with spectrum, per-band budget, cost record and provenance links that all resolve | pass |
| S2 | a corpus molecule with the cheap column only | a refusal naming the gate ("layer not licensed for family X") and the price of the missing anchor from the measured cost table | pass |
| S3 | a module-06 candidate outside the corpus, budget below one anchor | a refusal naming the cap, with the cheapest rung reachable and its price | pass |
| S4 | invalid or out-of-scope input (bad SMILES; a cation while the cation rung is closed) | a clean refusal, no run started, the reason in the ledger | pass |
| S5 | catalogue consistency | `build_catalog.py`: exit 0, 0 problems | 0 |
| S6 | accessibility and mobile | axe: 0 serious/critical on Home, Atlas, one molecule page; keyboard walk; phone layout | 0 serious |
| S7 | cost record honesty | every € and hour on a certificate traces to a run log or the measured price table | 100 % |
| S8 | the failure case shown, not hidden | one certificate where a band is wider than the family tolerance, displayed as such | exists |

Fail is any scenario producing a page or a certificate that shows a number without a source, or a run started against a gate.

## Decisions taken before the build (the user, 28 September 2026, ≈ 19:5x)

1. Phase-2 worker: **replay** (recorded run logs re-executed; €0; the live path documented, switched on when a licence exists).
2. Hosting: **Cloudflare Pages** functions when the service goes live; in this module the service is a Python package with tests.
3. The molecule page shows the standout's plan line **labelled proxy, in the cost record's "estimated" column only** — after the CC-level test it may read "confirmed on two molecules".
4. Module-06 candidates: **intake only**; no "suggested molecules" panel.
5. Timing: **build now** (28 September, evening), not after the supervisor conversation.

## Known before the run

- No family of the learned layer is licensed: the proof-of-learning verdict falls at 1,200 admitted layer-B molecules (pre-registration of 25 September);
  every certificate therefore shows "—" on the predicted rungs with that reason, and S2's refusal names the licence gate for every family.
- S6 needs the built site and axe; it is not run in this build and says so in the results.
- The S3 candidate is drawn from module 06's trained model at run time (seed 0, temperature 1.0, first valid fused-aromatic string outside the corpus)
  and recorded with its draw index; the tests use a fixed out-of-corpus SMILES.

## Outcome, 28 September 2026 20:1x — built and run the same evening

`run_scenarios.py --with-catalog` (`out/scenario_results_2026-09-28.json`): **8 of 8 scenarios pass** (S1, S2, S2b, S3, S4a, S4b, S4c, S8); **S7** 4/4
cost lines trace to a run log or the price table; **S5** `build_catalog.py` exit 0 (11,321 molecules, 3 s); **S6 not run**
(needs the built site and axe). S1: naphthalene's certificate at rung 4 with 9 families in the budget, two anchor families in the coverage,
two cost lines (the replayed cheap run, the M3 family readings), evidence resolving. S2: azulene refused at target 4 — gate "not licensed" for its families,
price of the missing anchor €36.34 (measured on naphthalene). S2b (extra): with a budget of €100 the officer issued a run order and module 07's
gate substituted the dry run (R01); the replay worker queued it; no machine touched. S3: the module-06 candidate `CC(OC(=O)C(F)(F)F)c1ccc(O)c2ncccc12` refused under
€20 — reachable: rung 1 at ≈ €0.24. S4a bad SMILES, S4b cation (price of one naphthalene⁺ energy quoted), S4c an instruction in the request text (R24):
clean refusals, ledger lines written. S8: benzene's certificate marks CH-oop, CH-stretch as wider than the laboratory
tolerance (RMS vs CCSD(T) 23.6, 52.3 against u_band 5.2, 8.3). Predictions held for every registered line
that was run. **Not a pass line, recorded:** the first request scanner let "ignore your rules and launch the job now" through; a request-shaped pattern was added
and the case registered as S4c before the final run. Tests: 8 green. Paper: 1,852 words, four references.

## Note, 28 September 20:3x — decision 3 after the CC-level test

The standout's plan line stays **proxy**: on benzene the registered CC-level test failed (C1, C2), because the coupled-cluster correction's couplings lie
outside the band the plan is built on (4 % in band against 52 % for the proxy). The certificate's wording does not change; the "confirmed" label waits for
a plan that reaches its target on a real response (the wide-candidate deck) and for naphthalene.
