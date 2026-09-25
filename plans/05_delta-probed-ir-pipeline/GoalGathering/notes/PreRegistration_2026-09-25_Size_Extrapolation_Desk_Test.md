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
