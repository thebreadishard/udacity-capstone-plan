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
