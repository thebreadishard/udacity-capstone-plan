# Benzonitrile CCSD(T)/cc-pVDZ Hessian: self-check "INVALID", energy route says the Hessian is right (30 Sep 2026)

hel1-23, anchor set two, corrected route (explicit (T) lambda, C kernels, gate 1 passed). 54 gradients (27 symmetry-unique displacements),
pair checks ≤ 5.2e-5 a.u., FD asymmetry 4.6e-5, symmetry reconstruction self-check 6.4e-12. The assembling run (11:42 UTC) wrote
`hessian_ccsd_t_INVALID.npz`: "null space 87.0 cm⁻¹ (limit 10)". The watchdog alarm (13:58 local, `watchdog_alarm.log`) was not read until 17:0x.

Analysis of the stored Hessian: the six translation/rotation eigenvalues are exactly zero; the "null space" check takes the six lowest |ω|
and two imaginary *vibrations* displaced two of the zeros — one purely out of plane (−87.0 cm⁻¹), one purely in plane (−81.9 cm⁻¹), i.e. the
low C–C≡N bends. The geometry is the B3LYP corpus geometry (max |g| 3.6e-2 a.u. at CCSD(T)), not a CCSD(T) minimum.

Second route (`curvature_route.py`, laptop WSL, energies only, frozen 8, tight tolerances; E0 reproduces the FD reference to 2.8e-9 E_h):
mode out of plane −87.0 (Hessian) vs −86.7 cm⁻¹ (energies), in plane −81.9 vs −81.3; E(±δ) − E0 = −1.2 / −1.4 µE_h on both sides.
The Hessian is computed correctly; the negative curvature is real at this geometry. Whether it may be used (E9 at CC compares Hessians at the
same geometry; frequency-based reads would see two imaginary modes) is the user's decision. The chain went on with SKIP=benzonitrile at 15:10 UTC.

**Decision (the user, 30 Sep 2026 ≈ 17:3x): "let's only use the results of correct calculations."** This Hessian is **excluded** from every
read-out (E9 at CC, R-reads, locality). The self-check now classifies it IMAGINARY rather than INVALID (`probes/e8_hessian_checks.py`,
test case `probes/results_m1/e8_selfcheck_cases/benzonitrile_imaginary.npz`), and IMAGINARY Hessians are never used.
