# Pre-registration 2026-09-25, 07:1x — size-extrapolation desk test on today's corpus (the user: "Doe de grootte-extrapolatiesplitsing")

**Question (fixed).** Does the pair model of E7 rung B, trained only on molecules of at most 26 atoms, predict the correction of larger
molecules (27–34 atoms) — the direction of the mandate — and does that prediction improve with the number of small molecules? A first cut
of hold-out (c) of the proof-of-learning pre-registration, on the data that exist today (layers A and A2, 229-molecule release; layer B is
still running).

**Split (fixed).** Admitted molecules (no imaginary mode). Hold-out (a) := every admitted molecule with **more than 26 atoms** (A2's upper end).
Hold-out (b) := E6's scaffold hold-out restricted to ≤ 26 atoms (kept as the within-size control). Pool := all remaining admitted molecules with
≤ 26 atoms, in E6's hashed order; training sizes 45, 100 and all. Model, features, seeds, epochs and read-outs exactly as E7 rung B
(`m05/e7_rungB_pairs.py --split size:26`).

**Reading (fixed before any number).** On the size hold-out: the ring coupling ratio and the corrected-frequency RMS at the full pool against the
zero rule, and their trend over 45 → 100 → all.
- **Encouraging:** ratio ≤ 0.6 and corrected RMS below half the zero rule at the full pool, decreasing with pool size → size extrapolation works at
  this range; the layer-B curve's hold-out (c) is expected to behave the same.
- **Warning:** ratio ≥ 0.9 or no decrease with pool size → the model does not carry from small to large at this range; the layer-B run keeps its
  value (it tests the same thing at ten times the data) but the proposal says so.
- Between: reported as such. Not a verdict on the design (that is the layer-B pre-registration); a desk test that costs half an hour on the
  CCX53's idle threads.

**Cost.** ≈ 30 min on the CCX53 (8 threads; the L2 run is stopped first, its reading being already determined), no new quantum chemistry.
Output `modules/05_support_predictor/out/E7_rungB_size26_2026-09-25.{json,md}`.

## Outcome — 25 September 2026, 07:1x: ENCOURAGING, at the edge of the bar

Run on the CCX53 (m05 env, eight threads, `--use-analytic`, 318 s): hold-out (a) 45 molecules of 27–34 atoms, (b) 18 scaffold molecules ≤ 26, pool 161.
MLP (three-seed means; the gradient-boosted check in the .md):

| training molecules (≤ 26 atoms) | (a) > 26 atoms: ring coupling ratio | (a) corrected ω RMS (zero 22.8) | (b) scaffolds ≤ 26: ratio | (b) corrected ω RMS (zero 23.5) |
|---|---|---|---|---|
| 45 | 0.66 | 6.61 | 0.40 | 5.68 |
| 100 | 0.62 | 6.01 | 0.39 | 4.92 |
| 161 | **0.59** | **5.76** | 0.36 | 4.45 |

Registered bars at the full pool: ratio ≤ 0.6 (met, just), corrected RMS below half the zero rule (5.76 < 11.4, met), decreasing with pool size
(met on both read-outs). **Encouraging** — with the honest remark that the ratio sits on the line and the curve is shallow (0.66 → 0.59 over a
factor 3.6 of data). The within-size control learns faster (0.40 → 0.36, 5.7 → 4.5), so size extrapolation costs about 0.2 in ratio and
1.3 cm⁻¹ at this range. Diagonals carry over well (C–H stretch 3.3, ring in-plane 6.3 cm⁻¹ on the larger molecules). Files
`modules/05_support_predictor/out/E7_rungB_size26_2026-09-25.json` and `.md`. For the layer-B pre-registration this is the expectation for hold-out
(c): learnable, slower than within-size; the 1.5×-per-decade bar on (c) is not obviously met from this short curve and stays the test.
