# Pre-registration M2 — when the in-house frozen-space gradient is "done", what it must print, and the gate through which it enters plan 05 (written 18 September 2026, evening, before any code)

*Builds on the design note of 13 September (`Design_Note_2026-09-13_M2_Frozen_Space_Gradients_in_JAX.md`, pieces A–G) and on decision 43 (18 September, 00:0x: Python on JAX/PySCFAD, `stop_gradient` on the reference vectors, Rust rejected). That note says what is built; this one fixes, before the build, the tests that say it is finished, the number it must print, the prediction that number is scored against, and the rule by which a gradient from it may enter a plan-05 deck. Nothing here starts before the anchor run has written its REPORT.md (≈ 24 September) and the user has said so.*

## 1. The object, restated in one sentence

E_A(x): the LNO-CCSD(T) energy of the molecule at geometry x in correlation spaces that were built once at x₀ (Pipek–Mezey occupied LMOs, per-fragment PNO spaces at plan 05's thresholds) and are carried to x by projection onto the displaced occupied/virtual space and Löwdin orthonormalisation — exactly `transport()` in `probes/m1_frozen_spaces.py`. M2 is ∇ₓE_A(x). The reference coefficients C₀ are constants (`stop_gradient`); the SCF at x, the projection M = C_space(x)ᵀ S(x) C₀ and the Löwdin step are on the tape (design note §4).

## 2. Done criterion — three tests, all pre-stated

**T-M2-1 (the derivative is right).** `jax.grad` of M2's own E_A against central finite differences of M2's own E_A, component by component over all 3N Cartesian coordinates of benzene (36) at the reference geometry and at one displaced geometry (mode 12, q = +1), step h = 0.005 bohr, repeated at h = 0.010 bohr to show the O(h²) fall. Pass: max |g_AD − g_FD| ≤ 1·10⁻⁵ E_h/bohr at h = 0.005 on both geometries. Same code on both sides, so the only noise is convergence noise; SCF and CC convergence are set to 10⁻¹⁰ E_h for this test.

**T-M2-2 (it is plan 05's function).** M2's E_A at the 27 sealed benzene points of `results_m1/benzene_cc-pvdz_tight/` (modes 12, 18, 6; q = −1 … +1; thresholds 1e-5/1e-6; the same `frozen_spaces_reference.npz`) against plan 05's arm A. Pass: |E_A^M2 − E_A^plan05| ≤ 1·10⁻⁷ E_h at every point, **or** a constant offset (the same to 10⁻⁷ E_h at all 27 points) that is explained in writing by a named difference between the two engines (DF fitting basis, semicanonicalisation, (T) convention). A point-dependent difference above 10⁻⁷ E_h is a fail: the function differentiated is then not the deck's function.

**T-M2-3 (the projection term is measured, not assumed).** The same gradient with the transport under `stop_gradient`, printed beside the full one at the two T-M2-1 geometries. No pass/fail; it is the number the side-project note asked for on 4 September, and it tells how wrong "freeze the coefficients, not the space" would have been.

M2 is done when T-M2-1 and T-M2-2 pass and T-M2-3 is printed. Not before, and not by any weaker criterion agreed later.

## 3. Requirements written into the code from the first commit

- `jax.config.update("jax_enable_x64", True)` before any import that allocates; a runtime assertion that every array on the tape is float64. Single precision would pass no test above.
- `jax.checkpoint` (rematerialisation) around the CC amplitude iterations; peak RSS printed by the run, with and without checkpointing at benzene/6-31G, so that the memory model for cc-pVDZ and cc-pVTZ (design note piece G) is a measurement.
- One log line per gradient: wall time, peak RSS, thread count, basis, thresholds, the projection-term norm.

## 4. The number: g_M2, with a prediction to be scored against

g_M2 = wall(gradient) / wall(energy) for the frozen-space object, measured by M2a's protocol (`PreRegistration_2026-09-13_M2a_Gradient_Cost_Ratio.md` §1): benzene, three repeats, eight threads, energy and gradient in the same process on the same machine, first call discarded (JIT), the correlation part timed. At 6-31G first (the basis of the 6.04 measurement), then cc-pVDZ where memory allows.

**Prediction, fixed now:** 2 ≤ g_M2 ≤ 4. Reason: reverse-mode differentiation of an iterative CCSD solve with rematerialisation costs two to four energy-equivalents, and the frozen arm carries no localiser, no PNO construction and no threshold logic on its tape — the parts that make PySCFAD's shipped LNO gradient cost 6.04 (M2b outcome, reading 2).

**Scoring:** g_M2 ≤ 4 confirms the prediction; 4 < g_M2 ≤ 6.04 is a partial miss to be explained per piece of the tape (profile printed); **g_M2 > 6.04 falsifies it** — the in-house gradient is then no cheaper than the borrowed one, and the pre-stated remedy is implicit differentiation of the converged amplitudes (Λ-equations under AD) instead of the unrolled tape, itself a two-week item. In every case the ladder (X21) is re-priced with the measured g_M2; the break-even values 16.2 (naphthalene) and 29.9 (pentacene) stand.

## 5. The gate into plan 05 (decision rule, rule 2, amended today)

A gradient from M2 enters a plan-05 deck only when: T-M2-1 and T-M2-2 have passed at benzene; g_M2 is printed with its basis and thread count; and the first naphthalene gradient has been checked once against a finite difference along one probe mode (mode 12, h = 0.005 bohr along the mode vector, ≤ 1·10⁻⁵ E_h/bohr). The gate is correctness, not price: the couplings have no energies-only route (amplitude test, 17 September), so a high g_M2 makes the deck dearer, not different.

## 6. What this does not decide

Whether the gradient-difference read of Δ₂ at q = 1 carries quartic contamination for the real correction (mode G's 0.05–0.21 cm⁻¹ was measured on the DFT stand-in; the first M2 deck at benzene measures it on the real object); anything about cc-pVTZ memory (piece G, measured after F); the (T) port (decision 41), which is a separate C item with its own acceptance tests.

## 7. Cost and where

Build: two to three working weeks (design note §3), desk work plus benzene-sized runs. Runs: on the Hetzner machine (a `qcad` environment with pyscfad and pyscf-forge must be built there first, ≈ 1 h) or on the laptop after 24 September; **never beside the anchor run**. T-M2-1 is 2 × (2 × 36 × 2 + 1) ≈ 290 benzene/6-31G energies plus four gradients — an afternoon on sixteen threads. T-M2-2 reuses the 27 sealed energies. g_M2: an evening.

## Outcome

*(empty until the tests have run)*
