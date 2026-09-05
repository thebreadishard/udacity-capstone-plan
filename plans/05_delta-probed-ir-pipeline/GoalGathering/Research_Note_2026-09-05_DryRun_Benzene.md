# Dated note 2026-09-05 — the zero-CC dry run at R0 (benzene): what it measured and what it asks

**Status.** A dated note under the freeze of 2026-09-04: it names measurements (printed by
`probes/dryrun_dft_delta_recovery.py`, results in `probes/results_dryrun/benzene/`) and the
design questions they raise. **It changes no frozen rule by itself.** Every proposal below is
marked *proposal* and waits for the user's decision; the Ladder stays as written until then.
Both arms of every number here are DFT (B3LYP vs BHHLYP, 6-31G*); no local-CC number exists.

## 1. What ran

| Item | Value (this laptop, Asus18, 8 threads, psi4 1.11, conda env `qc`) |
|---|---|
| Geometry optimisation B3LYP/6-31G* | 11 s |
| Hessian B3LYP / BHHLYP (grid 590/99) | 388 s / 454 s |
| One DFT gradient call, benzene | ≈ 6.3 s |
| One ± pair, both arms (4 gradient calls) | ≈ 25 s |
| Deck (hash `0158e130…`) | 334 pairs in K: 30 single-mode ±q_s (q_s = 1.0), 184 two-mode within 200 cm⁻¹, 120 multi-mode; plus 30 q₂ pairs (q₂ = 0.5) outside K; 61 pairs held out (f_h = 0.2, pair = unit) |
| Energies and gradients evaluated | 729 per arm; stage B 2 h 30 min |
| Nine-point Q6 scans | four modes (CC-stretch 1532, CH-stretch 3199, CH-oop 865, totally symmetric 1020 cm⁻¹), 72 energies |

Deviations from the frozen form in this first version, printed by the script: the low-rank
term of the structural prior is not implemented (banded ℓ₁ only); the completion patterns are
random sparse mode combinations, not the O1NumHess construction. The dry run at larger
molecules (README item 1 asks for "the largest molecules the laptop affords") has not run yet.

## 2. What it measured

1. **Δ₁ dominates the raw response** — |Δ₁| up to 2724 µE_h per unit q against an RMS symmetric
   response R_s of 215 µE_h. Without the ± pairs of Round 9 nothing could have been read.
2. **The shared-reference constant** c₀ = 0.20 ± 0.26 µE_h from the two-amplitude read: consistent
   with zero in a noiseless run; the spread is quartic leakage into that read.
3. **The DFT-arm numerical floor** (Q6 estimator, √(SSR/(n − p)), pooled over four modes, ν = 16):
   σ_E = 0.147 µE_h (per mode 0.002–0.229). The mode-E noise line at τ = 5 cm⁻¹, q_s = 1 is
   18.7 µE_h; the DFT arms sit a hundred times below it.
4. **The structure of the direct Δ₂ (BHHLYP − B3LYP, B3LYP mode basis).** The five off-diagonal
   blocks above 0.2 × the RMS diagonal couple modes **170–450 cm⁻¹ apart** ((1186, 1357) at 0.95;
   (1208, 1656) at 0.41; (1069, 1531) at 0.34). They are not near-degenerate pairs. In D₆h benzene
   these are same-symmetry pairs; the frequency-band picture is not what the data show.
5. **Mode E recovers the off-diagonals with the full deck.** Per-family RMS frequency error,
   recovered vs direct, after re-diagonalisation: CC-stretch 0.36, CH-in-plane-bend 0.43, CH-oop
   0.21, CH-stretch 0.11, ring 0.31 cm⁻¹. Diagonal-only (the CMA-0 block): 6.90 / 7.47 / 0.62 /
   0.04 / 0.37. The off-diagonal correction is worth up to 7 cm⁻¹ on the ring families.
6. **Mode G recovers everything from 30 pairs (60 gradients)**: 0.30 / 0.16 / 0.21 / 0.03 /
   0.09 cm⁻¹; model floor ρ_dry(G) = 0.0025.
7. **The raw held-out ρ is blind to the off-diagonals.** The off-diagonal part of the held-out
   responses has RMS 5.2 µE_h against 215 µE_h raw (2.4 %). ρ on raw R_s is 0.024 after the first
   off-diagonal pair and 0.005 at the end; any declared ρ ≥ 0.03 stops at K = 62 (K_off = 2) with the
   7 cm⁻¹ errors of item 5 still in place. The off-diagonal residual ρ_off (diagonal prediction from
   the single block subtracted) falls from ≈ 1 to 0.30 at 462 energies and 0.21 at 502:
   **K_off(ρ_off ≤ 0.3) = 388 energies** for 435 off-diagonal unknowns.
8. **The model floor.** With noiseless responses ρ never falls below ρ_dry(E) = 0.0049 (quartic
   contamination of the quadratic model at q_s = 1). The frozen rule ρ ≤ c·ρ_noise is therefore
   unreachable whenever c·ρ_noise < 0.0049, i.e. for σ_E ≲ 1 µE_h at c ≤ 3 — exactly the quiet
   regime the plan hopes for.
9. **The noise column (noise per energy, shared ε₀; per component in mode G).**
   - Mode E with the floor ρ* = max(1.1·ρ_dry, c·ρ_noise): K ≈ 450–500 energies at σ_E ≤ 1 µE_h
     (the honest value, item 7); at σ_E = 2 µE_h K = 430–496 for c ≤ 2 but 76 at c = 3; at
     σ_E ≥ 5 µE_h K = 62–76 for every c — the rule stops before the off-diagonals are seen.
     In ρ_off terms the off-diagonal noise floor is (σ_E/√2)/5.2 µE_h: 0.14 at 1 µE_h, 0.27 at
     2 µE_h, 0.69 ("at noise") at 5 µE_h.
   - Mode G: K = 64 gradients for every σ_g from 0.5 to 5 µE_h per unit q and every c; 96 at the
     quietest setting with c = 1. Robust.
10. **The w rule** read w = 25 cm⁻¹ with λ = 10⁻⁶ (the smallest band, the weakest penalty; w = 400
    is worse, ρ = 0.077). Given item 4, the band did not select the important elements; the
    recovery worked because the deck's two-mode patterns isolated them and the penalty was weak.

## 3. What this asks (proposals, for decision)

- **P1 — ρ on the off-diagonal residual.** Define ρ, ρ_noise and the stopping rule on R_s minus
  the single-block diagonal prediction (ρ_off), not on raw R_s. Zero extra cost; the diagonal is
  known after the first block anyway. Without it the frozen rule reads K_off = 2 on benzene.
- **P2 — restore the model floor.** ρ\* = max(1.1·ρ_dry(rung, mode), c·ρ_noise), with ρ_dry printed
  by the dry run per rung and mode. The Round-9 reviewer proposed this floor; the plan dropped
  it; the measurement says it is needed.
- **P3 — the mode-E noise requirement is set by the off-diagonal signal, not by the Q6 line.** At
  benzene the off-diagonal signal is 5 µE_h RMS, so mode E needs σ_E ≲ 2 µE_h to recover the
  couplings, ten times stricter than the 18.7 µE_h line (which was derived for the diagonal
  second difference). Proposal: the Q6 report prints RMS_off and the implied σ_E ceiling beside
  the line; if the local-CC σ_E measured at R1 exceeds that ceiling, mode E cannot recover the
  off-diagonals at that size and the mode-G side project is load-bearing, not additional.
- **P4 — the structural prior's band hypothesis.** The large couplings are same-symmetry pairs far
  apart in frequency. Candidate replacement, parameter-free and exact for symmetric molecules:
  penalise only elements between modes of **different irreducible representations** (they are
  zero by symmetry), leave same-symmetry elements free, keep the ℓ₁ only for the low-symmetry
  rungs. To be tested in the naphthalene dry run before it enters the deck.
- **P5 — the declared ρ.** 0.1 is far too loose; whatever c is read into pilot-note item 8 must be
  read on ρ_off (P1).
- **P6 — the mode-E cost picture.** K_off ≈ 390 energies at benzene is ≈ 0.9 × the number of
  off-diagonal unknowns: the sparsity saving at R0 is small. The size sentence is a measurement
  at R1–R3, not R0, and R0 is 12 atoms; but the plan should expect K_off of order M² /2 in mode E
  unless P4 or the M05 prior bites.

## 4. Two answers for the mapping checklist (Uitleg hoofdstuk 16, §16.4)

- **Question 2 (module 05, subset size).** One B3LYP/6-31G* Hessian of a QM9-size molecule costs
  3–7 min on this laptop at the dry run's grid (benzene 6.5 min; QM9 molecules are smaller); the
  ωB97x side is already in Hessian QM9. One thousand molecules ≈ three days unattended; five
  thousand ≈ two weeks. No floor is needed; the size is set by dated note after the corpus build
  starts.
- **Question 3 (module 07, framework).** Decided by the user 2026-09-05: **LangGraph** (defensible
  through Udacity's "Agentic AI Engineer with LangChain and LangGraph" elective; the core
  Agentic AI course used Pydantic, smolagents, CrewAI and OpenAI endpoints). Proposed and
  awaiting confirmation: the **Anthropic API** as the model endpoint (the rubric's "or
  equivalent"), Claude Opus 5 as the default model with the model id logged in every certificate,
  no second endpoint unless a measurement asks for one; LangGraph open-source is free, LangSmith
  optional, token costs of order tens of euros over the project.

## 5. Software facts (recorded 2026-09-05)

The laptop's conda environment `qc` (psi4 1.11, NumPy 2.5, SciPy 1.18, pandas 3.0) ran the dry
run. There is no pyscf, no PyTorch and no WSL; the anchor code (pyscf-forge, PySCFAD) needs
Linux, so probe M1 and every local-CC probe wait for `wsl --install` (user, administrator,
reboot) and a Linux Python environment, to be set up afterwards.

*Printed numbers: `probes/results_dryrun/benzene/REPORT.md`, `stageC_recovery.json`,
`stageB2_floor.json`, `benzene_full.log`. Quick pipeline test (156 pairs): `benzene_quick/`.*
