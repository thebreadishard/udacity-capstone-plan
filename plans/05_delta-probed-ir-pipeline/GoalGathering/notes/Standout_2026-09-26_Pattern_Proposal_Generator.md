# Standout candidate — the generative *pattern* proposer (module 06's original idea), parked 26 September 2026

*The user, 26 Sep 10:0x: "Kun je ervoor zorgen dat we het oude idee niet vergeten. Ik wil het nog wel doen, mogelijk als standout module."*

## The idea (Capstone_Mapping.md § Module 06, 6 September 2026)
K_off — the number of off-diagonal coupled-cluster responses — is the scarce quantity. The deterministic deck spends it by rule. A generative model
(frozen intent: a VAE over two-mode displacement patterns, conditioned on the molecule's DFT mode structure) proposes candidate patterns, an acquisition
rule scores them (expected reduction of the recovery residual ρ under the structural prior), accepted patterns enter the hashed, ordered deck *before any
response for that rung is computed*, and are then evaluated by a real calculation like any other pattern. Pre-registered metric: **pattern efficiency at
zero CC cost** — K_off to reach ρ\* with proposed patterns in the deck against the deterministic deck alone, everything else matched. Losing is a
publishable outcome.

## Why it was parked
On 24 September the module was rescoped to the SMILES candidate generator because its dataset (pattern-response records) did not exist while PubChem did.
The rubric vak is the same; the pattern proposer would be a second, project-specific generative artefact — hence *standout*.

## When the response data exist
- **DFT-level, derivable now.** A pattern response is a projection of the Δ-Hessian onto a displacement pattern. The corpus factory writes full
  Cartesian Δ-Hessians (ωB97X − B3LYP) for every molecule: 229 in layer A/A2, layer B growing (111 on 26 Sep 09:5x, ≈ 4 per hour on three shards).
  Pattern-response records for *any* deck can therefore be computed on the desk from `corpus/molecules/*/hessian_*.npz` without new quantum chemistry,
  and the efficiency experiment (deterministic deck vs proposer, K_off to ρ\*) can be run as a simulation on hundreds of molecules. This is the
  training corpus the mapping asked for, with the PAH tensors held out as module 05's test set (Distilled plan, quality check).
- **CC-level, the real thing.** Responses at the label level exist for the anchor (naphthalene, the M3 cc-pVTZ deck, 24 Sep) and benzene (M1/E8);
  more arrive only through the P26 label plan on rented machines after 28 September, a few molecules at a time. The proposer's *test* on real
  responses is therefore a post-28-September item; its *training* is not blocked.

## What it needs when picked up
1. A pattern-response export from the corpus (script, seconds per molecule): for each molecule the deck's patterns and their Δ-responses; split hash
   distinct from module 05's; PAH held-out.
2. The recovery solver and ρ from plan 05 (already in `src/dpir` / probes) to score K_off → ρ curves.
3. The VAE (or, honestly cheaper, a conditional scorer) and the acquisition rule; a pre-registration before the first run; the same rubric artefacts as
   module 06 (notebook, report, requirements).
Estimated desk work: two to three days. Owner of the decision: the user.

## Status, 27 September 2026, 03:5x (picked up on the user's word of 26 Sep 10:1x; everything below is in `PreRegistration_2026-09-26_Standout_Pattern_Proposer.md` and the ledger)

- Built as `modules/standout_pattern_proposer/` (export of the corpus Δ₂ response records, banded-ℓ₁ recovery, orderings P0/P1/P2/P12/P3, `readout.py`, 7 planted tests).
- E1 (band pool, 97 evaluation molecules): the learned order reaches the halfway point with ≈ one fifth of the fixed order's energies (S1 pass); oracle ≈ one sixteenth.
- E2 (all pairs): the pool matters more than the order — a deck that reaches every pair ends at ρ_off 0.08/0.14 where the band deck ends at 0.53/0.47; ordering still 1.3–1.4× on K_off(0.3), P12 best, oracle ×2.6–4.
- P2 (learned embedding on the rung-C body): stages 1–3 of the registered fair-chance search read on validation; nothing licensed either way; stage 4 at 300 molecules, stage 5 after the 28th.
- Adaptive ordering (P0+A/P1+A/P2+A, the user: "Akkoord", 26 Sep 18:4x): built, rule corrected on the planted dry run, running on hel1-23 (band pool, ≈ Sun 11:00).
- Still to do for the rubric: design note, notebook, report, requirements of the module; the CC-level test on the anchor's real responses after the 28th.
