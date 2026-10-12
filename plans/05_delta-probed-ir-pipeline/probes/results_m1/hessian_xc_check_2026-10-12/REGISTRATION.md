# Do pyscf's analytic DFT Hessians — the labels — carry the XC-response error? — registration (12 October 2026, 03:5x, before the run)

**Why.** The night of 11–12 Oct (`../uks_apt_margin_2026-10-11/REGISTRATION.md`, outcome) found the dipole derivatives contracted from pyscf's
DFT Hessian response wrong in the exchange-correlation part: benzene B3LYP 4.0e-4 e against two routes that agree, HF exact. The analytic
Hessian is built from the same response (`make_h1`, the CPHF solution, `hess_elec`), and the corpus's labels are pyscf analytic B3LYP and ωB97X
Hessians. If the Hessian carries a related error, every analytic label does.

**The comparison.** pyscf's analytic DFT Hessian has no grid response: it is the second derivative with the integration grid frozen. Its exact
counterpart is the central finite difference of pyscf's analytic gradient *without* grid response, every displaced SCF and gradient evaluated on
the reference geometry's grid (points and weights frozen; the screening mask rebuilt for the displaced basis). That gradient was validated tonight
(its field derivative agrees with FD of the dipole, and at HF with the CPHF route as F²). Script: `probes/hessian_fixed_grid_fd.py`; step
h = 0.005 bohr; B3LYP/6-31G* Cartesian, grid (99, 590) unpruned, conv_tol 1e-11, conv_tol_grad 1e-8, 4 threads at nice 19.

**Smoke first:** water (where the APT error is 7e-6) — the floor of this comparison.
**Then:** benzene (`corpus/molecules/A_8448043181`), its saved labels-route Hessian (`hessian_b3lyp_analytic.npz`, H_raw), 72 displaced
gradients.

**Lines (on the harmonic frequencies of the projected Hessians, the labels' quantity; max over modes).**
- |Δω| ≤ 0.5 cm⁻¹ → the analytic Hessian is consistent with the gradient; the labels do not carry the APT's XC error at a level that matters.
- |Δω| ≥ 2 cm⁻¹ → the labels carry it; the labels route and its two-route checks are reviewed before more labels are used for a read.
- Between → recorded with the per-mode pattern; ωB97X gets the same check before any conclusion.
Reported beside: max |ΔH| (Eh/bohr²), water's floor, the per-mode Δω.
