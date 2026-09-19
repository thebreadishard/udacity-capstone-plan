# Pre-registration X19 — lead A: does an optimally tuned range-separated functional shrink the coupled-cluster correction? (16 September 2026; not run)

*Decided 16 September morning: no plan 07 yet ("We wachten op de test"). This is the test. It runs after plan 05's TZ cells (no psi4 beside the anchor), costs about one laptop-hour, and decides whether lead A deserves a plan of its own.*

## Question

Plan 05's pipeline learns the correction from a cheap functional (B3LYP) to the coupled-cluster anchor. Lead A asks whether a functional tuned per molecule (an optimally tuned range-separated hybrid, OT-RSH) starts closer, so that the correction to learn is smaller. The literature check of 13 September says the tool exists (Baer–Kronik lineage) and predicts the failure mode: the optimal range parameter ω drifts almost linearly with acene length (Körzdörfer et al. 2011), and the one paper that tuned with vibrations in view got zero-point energies worse than B3LYP (Tamblyn et al. 2014). So the test has two parts: does tuning shrink the correction at all (X19a), and does the ω tuned on one molecule carry to the next (X19b, only if X19a wins).

## X19a — benzene, three modes, measured truth

- **Truth:** the canonical CCSD(T)/cc-pVTZ curvatures of benzene's three probe modes (the totally symmetric ring breathing, the degenerate C–C stretch, the C–H out-of-plane scan mode) from plan 05's M1 §2.2d (`probes/results_m1/`, the 61-energy bias line; curvatures in cm⁻¹ per mode).
- **Baselines, same modes, same basis (cc-pVTZ), psi4 1.11 analytic Hessians:** (i) B3LYP, the pipeline's low arm; (ii) LRC-ωPBEh with ω tuned on benzene by the ionisation-potential condition (ε_HOMO(N) = E(N−1) − E(N), ω scanned 0.1–0.5 bohr⁻¹ in steps of 0.05, then 0.01 around the crossing; neutral and cation single points, cc-pVTZ, DF); (iii) the same functional at its default ω, as the control that separates "range separation" from "tuning".
- **Quantity:** per mode the correction Δ = curvature(CC) − curvature(functional), in cm⁻¹ of first-order frequency shift; the RMS over the three modes.
- **Win:** RMS(Δ, tuned) ≤ 0.5 × RMS(Δ, B3LYP) with no sign flip on any mode. **Lose:** RMS(Δ, tuned) ≥ 0.8 × RMS(Δ, B3LYP), or a sign flip. Between: inconclusive, X19b runs anyway.
- **Cost:** ω scan ≈ 12 single points × 2 charge states ≈ 10 min; three Hessians (B3LYP, LRC-ωPBEh default, LRC-ωPBEh tuned) ≈ 3 × 8 min. About one hour, Windows psi4, quiet machine not required.

## X19b — transfer of ω, only after a win

Tune ω on naphthalene the same way; compare with benzene's ω (the literature expects a shift); compute naphthalene's three M3 modes with benzene's ω and with its own; the question is whether the correction with the *transferred* ω is still ≤ 0.5 × B3LYP's on the naphthalene cc-pVDZ curvatures that M3 measured (`results_m1/M3_EVEN_ODD_READING_2026-09-15.md`, the composite k per mode; DZ, so the functional Hessians for X19b are cc-pVDZ). Win/lose thresholds as X19a.

## What each outcome does

- **X19a and X19b win:** lead A becomes the pipeline's cheap arm candidate — a dated plan-05 proposal (P28: the low arm of pipeline B and the network's input functional), and *then* a plan 07 is worth opening for the σ/π and functional questions together, after 26 September.
- **X19a wins, X19b loses:** tuning helps per molecule but does not travel; the network would have to learn the ω drift too — recorded, no plan 07.
- **X19a loses:** lead A closed on measured data; the correction is not a matter of the functional's long-range form.

## Bookkeeping

Script to write: `experiments/x19_tuned_functional.py` (psi4, prints the ω scan, the three Hessian curvatures and the table above; every number from the files). Runs after the TZ cells (≈ 22 September) or on the desktop; results as `X19_<date>_….md` beside this note; README item 33.

## Outcome — 19 September 2026, 12:41 (run on the Hetzner CPX62, 16 threads, 28 minutes): **X19a LOSE**

`experiments/x19_tuned_functional.py`; results `experiments/x19_tuned_functional.{json,md}`, energies in `x19_tuned_functional_cache.json`, log `x19_tuned_functional_run_2026-09-19.log`. Truth: a2 per mode from the sealed canonical CCSD(T)/cc-pVTZ scan (9 points per mode, fit σ ≤ 0.02 µE_h). Baselines on the same 27 geometries, cc-pVTZ, DF, grid (99, 590). ω tuned by the IP condition: J(ω) crosses zero between 0.20 and 0.25, ω* = 0.24 bohr⁻¹ (|J| = 1.4·10⁻⁴ E_h).

| functional | mode 6 CH-oop | mode 12 CH-ip-bend | mode 18 CC-stretch | RMS (cm⁻¹) |
|---|---|---|---|---|
| B3LYP | −12.30 | +5.71 | +26.72 | 17.30 |
| LRC-ωPBEh, ω = 0.2 (default) | −9.31 | −3.90 | +30.73 | 18.68 |
| LRC-ωPBEh, ω* = 0.24 (tuned) | −17.37 | −5.77 | +42.41 | 26.67 |

Ratio tuned/B3LYP = 1.54 (LOSE ≥ 0.8) and a sign flip on mode 12: **LOSE** by the rule of 16 September. The tuned functional makes the coupled-cluster correction *larger* on every mode, and even the untuned range-separated hybrid is no better than B3LYP. X19b does not run. Per the rule above: lead A is recorded, **no plan 07**. The B3LYP correction itself — −12.3 / +5.7 / +26.7 cm⁻¹ at cc-pVTZ — is a number pipeline B measures anyway and is consistent in size with M1's DZ readings.

