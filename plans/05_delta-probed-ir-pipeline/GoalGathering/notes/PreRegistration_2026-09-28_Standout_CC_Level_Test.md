# Pre-registration 2026-09-28, 20:2x — the standout proposer's plan on real coupled-cluster responses (benzene now, naphthalene when its Hessian lands)

**Why.** Every result of the pattern proposer so far is proxy-level: Δ₂ = ωB97X − B3LYP from the corpus, 97 evaluation molecules
(`PreRegistration_2026-09-26_Standout_Pattern_Proposer.md`, outcomes of 26–28 September). The claim the module and the proposal make is about the
coupled-cluster responses a rung spends. Two molecules have a real CCSD(T)/cc-pVDZ Hessian at the corpus geometry: benzene (E8, 24 September,
`probes/results_m1/e8_benzene_ccpvdz/hessian_ccsd_t.npz`, symmetry-validated, pair checks passed) and naphthalene when the frozen-10 rerun assembles
(≈ Tuesday 29 September, evening). This note fixes, before any number, how the same test is run on those responses and what it may be called.

## 1. Method (one code path)

`pp/core.py` gains `hi_override`: `delta2()` and `export_molecule()` take another projected Hessian at the same geometry as the high level (the geometry
is checked to 1e-6 bohr). The CC export of a molecule is therefore built by the proxy's own code with Δ = H_CCSD(T) − H_B3LYP(6-31G*) in place of
ωB97X − B3LYP: the same B3LYP modes, the same deterministic deck and hash (both come from the B3LYP frequencies), the same design rows and the same
banded-ℓ₁ recovery in mode E. Script: `modules/standout_pattern_proposer/cc_level_test.py <molecule id> <cc hessian npz>` → `out/cc/<id>_cc_test.json/.md`.
Orderings: P0 (the hashed deck), P1 (the hand-feature scorer, seeds 0–2 as trained on the proxy exports — nothing is retrained), P3 (the oracle, which
knows the CC Δ₂). Read-outs per ordering, as registered on 26 September: **K_off(0.3)** (primary), **n_half** and the **AUC ratio** against P0, on
ρ_off; the same three on the proxy export of the same molecule (`out/exports/<id>.npz`), side by side.

## 2. Lines (a confirmation on one or two molecules, not a statistic)

- **C1 (the registered S1 threshold, per molecule):** P1's K_off(0.3) ratio against P0 on the CC responses ≤ 0.80 (seed median), and n_half ratio ≤ 0.80.
- **C2 (proxy fidelity):** the direction of P1 against P0 on CC agrees with the proxy on the same molecule (both below 1, or both not), and the CC ratio lies
  within a factor 1.5 of the proxy ratio.
- **C3 (headroom):** the oracle's K_off(0.3) on CC is reported as the ceiling; P1 within 1.5× of it is "near the ceiling", as registered.
- **Reading.** C1 and C2 pass on benzene → the molecule page's plan line (module 08, decision 3) may read *"confirmed on one molecule (benzene, CC)"*, and
  *"on two"* when naphthalene passes too; C1 fails → the line stays *proxy* and the failure and its size go into the standout notebook as a dated section;
  C2 fails with C1 passing → the plan works on CC but the proxy misjudged its size; the proxy's role (training data) is then reviewed, not the plan.

## 3. Prediction on record

The scorer's inputs are cheap-level pair features; nothing in them depends on the response level, so the *order* P1 proposes is identical on proxy and CC,
and only the responses differ. On benzene the CC correction is larger (ΔH RMS 4.98e-3 against the proxy's 3.48e-3 a.u., E8) and one bond less local,
so more of the off-diagonal power sits beyond the first patterns: prediction — C1 passes (ratio ≈ 0.6–0.8), C2 passes with the CC ratio somewhat higher
than the proxy's (harder to order), C3: P1 farther from the oracle on CC than on proxy. If the oracle itself needs more energies on CC than on proxy, that is
the size of the "knowledge gap" the 28 September reading spoke of, measured on a real response for the first time.

## 4. What is not claimed

Two molecules, both bare parents, both in the evaluation split (never in the scorer's training). Nothing here licenses the learned representation (P2) —
its stages 4 and 5 remain as registered — and nothing changes plan 05's deck before the wide-candidate pre-registration of 27 September is executed.
