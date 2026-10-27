# Design note — band heights for cations: an APT for every open-shell molecule (27 Oct 2026)

TASKS 50, gap 2. Written before any cation APT is computed; the run waits for the user's word.

## Why

A spectrum is band positions and band heights. The heights come from the molecule's atomic polar tensor (APT) and its mode shapes. The
labels route writes the APT only for closed shells (`corpus/analytic_hessians.py`, `want_apt = … and not run.spin`), so every cation in
the corpus has positions only: the 60 pool-3 cations (46 with analytic Hessians on the laptop, the 14 largest now on the CCX53) and, later,
the cation fill (TASKS 121: 414 candidates). Ionised PAHs matter most in astronomy, so the product without their heights is incomplete.

The closed-shell route (the APT from the Hessian's own CPHF response, residual-checked since 12 Oct) is not available for UKS: on the
cation 3-hydroxypyridine⁺ the CPHF-based APT — ours and pyscf-properties' — was 3.3e-3 e off two routes that agreed with each other, the
field route (`probes/apt_field_route.py`) and finite differences of the dipole (`probes/results_m1/uks_apt_margin_2026-10-11/REGISTRATION.md`;
the cause, pyscf 2.14's Krylov CPHF stopping early, was found on 12 Oct and is fixed upstream by #3333, unreleased).

## What

**Route: the field route.** P[t, 3A+x] = −(g_Ax(+F e_t) − g_Ax(−F e_t)) / 2F with pyscf's analytic UKS gradient in a uniform field
(`probes/apt_field_route.py`, written 12 Oct, already takes `--charge/--spin`): six gradients and six SCFs per molecule, no CPHF. It runs
on the molecule's corpus geometry and the label settings (B3LYP/6-31G* Cartesian d, grid 99/590), so the APT matches the Hessian it is
paired with.
- **Production mode: without grid response**, the convention of the closed-shell route C (the analytic Hessian of pyscf 2.14 has no grid
  response either); the tool's grid-response variant is computed only in the check below. That halves the tool's cost.
- **File:** `dipole_b3lyp_field.npz` beside the Hessians (route `field`, F, charge, spin, the software stamp, sum rule); `m08/spectrum.py`
  and the Atlas export add it to `APT_FILES` after the two existing names, with a test.

**Checks on every molecule (the noise principle: a second route or a symmetry check for every derived quantity).**
1. Translational sum rule for an ion: Σ_A P_A = q·I (`corpus/apt.sum_rule(P, charge)`), against the bound the closed-shell route meets
   without grid response (benzene 3e-5 … 1.6e-4; line 5e-4).
2. The same electronic state in both fields: ⟨S²⟩ at ±F within 1e-3 of the field-free value, and E(+F) + E(−F) − 2E(0) < 0 (a positive
   polarisability). A cation with a degenerate hole (benzene⁺, Jahn–Teller) may flip state in a field; such a molecule is named and gets
   no APT, never a silent one.

**Two-route check on a subset (before the production run, registered with its line).** Five cations — the smallest, the largest that
fits the laptop, a polar push-pull one, an aza one and one with a five-membered ring — by the field route at F = 1e-3 and 2e-3
(Richardson; the 16 Oct lesson: a polar molecule's field route needs two fields) and by finite differences of the dipole (the 11 Oct
route, grid response on). Line: max |ΔP| ≤ 1e-3 e between the routes on each, as the closed-shell L-lines; heights reported beside.

## Cost and place

The laptop only, nothing paid. Measured 11 Oct: the field route (both grid modes) 935 s on a pool-3 cation of ≈ 115 basis functions,
437 s on benzene. The 60 run from 117 to 303 functions; at t ∝ n^3.4 (the labels lanes' exponent) the largest would take several hours
each, so the largest is timed first and the whole set priced with `probes/compute_prices.py` before the run (an exact number, not this
estimate). Memory: a UKS gradient, far below a Hessian; measured on the largest first, inside the 13 GB laptop budget. Runs through
`tools/runspec.py` in WSL with pyscf's own log on (`probes/library_log.py`), beside a waiting chain but never beside a training.

## Order

1. A runner `probes/cation_apt_field.py` (one molecule per call: field route, both checks, the file) with tests on water⁺ (sum rule = q·I,
   the state check refusing a forced flip) — on the existing tool, no copy of its algebra.
2. The five-molecule two-route check, registered first; read.
3. The 46 laptop cations, then the 14 once fetched from the CCX53; then the export and module 08 read the new files.
4. For the cation fill (TASKS 121): the same runner as a step of the labels route for open shells, so a new cation row carries its APT.

Not in scope: a UKS branch of the CPHF-based route (needs pyscf with #3333; TASKS 47), CC-level APTs for cations (frozen, TASKS 29).
