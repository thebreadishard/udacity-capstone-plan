# Pre-registration 2026-09-27 — a cheap estimate of the answer as an input to the pair scorers (decision on the user's word, 27 Sep 08:3x)

*Written on 27 September 2026 before any data for it exist. Compute (minutes per molecule of DFT or semi-empirical work on the corpus shards) starts after
the supervisor conversation of 28 September, on the user's word for the machine. The test runs on the layer A + A2 + B set as it stands then (≈ 300 molecules).*

## The question

The pair scorers of the standout pattern proposer (P1 hand features, P2 learned embedding on the rung-C body) predict log₁₀|Δ_ij| — the size of the
coupling difference between two functionals for a pair of modes — from the molecule's cheap side (geometry, atomic numbers, the low-level Hessian, the
mode participations). Their ordering quality on validation is a Spearman ρ of 0.58–0.65 against the truth's 1.00, and the oracle gap on the evaluation
molecules is a factor 2.6–4 (E2). The adaptive-ordering test of 27 September showed that this gap is knowledge, not feedback. The Δ-learning principle of
the whole plan says where such knowledge comes from: a cheap estimate of the quantity itself. This registers that idea one rung below the corpus.

## The input (one of two, chosen before the run by cost)

- **X1 — same functional pair, small basis:** ωB97X − B3LYP Hessians at 3-21G or def2-SVP on the corpus geometry (no re-optimisation), projected on the
  corpus modes, giving Δ^cheap_ij for every pair. Cost: two Hessians per molecule at a small basis — minutes on a shard.
- **X2 — semi-empirical against DFT:** GFN2-xTB Hessian against the corpus's B3LYP Hessian, same projection. Cost: seconds. Weaker relation to the
  target (different physics), stronger as a test of "any cheap estimate helps".
- The first run takes X1 if the two small-basis Hessians cost ≤ 5 minutes per molecule on a shard at 16 threads (to be timed on water and benzene);
  otherwise X2. Both may be run later; each is one column of the export.

## How it enters

- P1: two more hand features per pair — log₁₀|Δ^cheap_ij| and its in-band flag interaction — appended to the 21 registered features (P1x).
- P2: the cheap Δ^cheap_ij joins the pair head's inputs (e_i + e_j, e_i ⊙ e_j, |ω_i − ω_j|, log₁₀|Δ^cheap_ij|) (P2x); the body is unchanged.
- P0x: the cheap estimate used *alone* as the ordering (order by |Δ^cheap_ij|) — the control that says how much of the gain is the estimate and how much
  the learning.

## Read-outs, pass lines, predictions (fixed now)

- **Validation (the selection read):** Spearman ρ of predicted against true log₁₀|Δ_ij| over all pairs, per molecule, as in `stage_readout.py`; paired
  per molecule against the incumbent (Wilcoxon signed-rank, one-sided, p < 0.05), three seeds.
- **C1 — the estimate carries information:** Spearman of log₁₀|Δ^cheap| against log₁₀|Δ| on validation ≥ 0.5 (X1) / ≥ 0.3 (X2). Prediction: X1 ≈ 0.7,
  X2 ≈ 0.4.
- **C2 — it helps the scorer:** P1x and P2x beat P1 and P2 on validation Spearman by ≥ 0.05 with the paired test significant. Prediction: X1 gives +0.10
  to +0.15 (to ≈ 0.75), X2 +0.03 to +0.05.
- **C3 — it moves the read-out:** on the evaluation molecules (band pool and wide pool, `run_simulation.py`), the n_half ratio of P12x against P12 is
  ≤ 0.85 on ≥ 70 % of molecules. Prediction: X1 0.7–0.8; and P0x alone sits between P1 and the oracle.
- **Fail:** C1 met but C2/C3 not → the scorers already extract what the cheap estimate carries (write it as such); C1 not met → the small-basis or
  semi-empirical Δ does not resemble the target and the idea is closed for that input.

## Guards

- The estimate must never be computed at the label level or with the target's own functionals at the target's basis: it is cheap by definition.
- Splits are the standout's hashed splits (parents evaluation; A2/B 70/10/20); nothing is chosen on the evaluation molecules.
- Every new column goes into the export (`run_export.py`) with its provenance (method, basis, wall time per molecule) so that REPRODUCE.md can rebuild it.
- The five-stage fairness search for P2 (12:1x rule) is unaffected: P2x is compared against P2 at the same stage.
