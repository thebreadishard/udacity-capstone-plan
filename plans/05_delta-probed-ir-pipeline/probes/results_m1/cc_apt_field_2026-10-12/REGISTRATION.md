# Lever 6: a CCSD(T) APT for pyridine by the field route, and read-out (3) on a molecule of low symmetry (registered 12 October 2026, before the runs)

*On the user's word (12 Oct, 14:0x: 'Doe 6 ook'), lever 6 of the odds of the same day. Why: read-out (3) on benzene (9 Oct) could not test the
Hessian's part of the intensities — with one APT, benzene's symmetry fixes its mode shapes (network 0.003 = zero rule 0.003). A molecule whose
modes mix within their symmetry blocks can. Pyridine (C2v, 27 modes, a carried TZ anchor) has a CCSD(T)/cc-pVDZ FD Hessian from 30 Sep but no
dipoles: its run predates the dipole capture of 3 Oct. Re-running its 66 displacements for the dipoles would cost about 55 h at 8 threads.*

## Method

`probes/cc_apt_field.py`: P = −∂g/∂F by central differences of the CCSD(T) gradient in a uniform field (F = 1e-3 a.u.). That takes six
gradients, with the field term in the gradient's core-Hamiltonian derivative (`apt_field_route.field_hcore_generator`, validated for DFT on
12 Oct). The CC chain is `cc_dipole_capture`'s: RHF → CCSD → (T) → (T) lambda → gradient, the call pyscf/grad/test/test_ccsd_t.py makes. Frozen
core as the E8 probe derives it, cc-pVDZ, the anchor's own geometry, and the (T) C kernels (`--fast`).

**Measured on water before this registration** (`tests/test_cc_apt_field.py`):
- the field route is 1.6e-5 e (cc-pVDZ) and 1.8e-5 e (6-31G) from central differences of the relaxed CCSD(T) dipole;
- the field route moves 6e-6 when F halves;
- translation sum rule: 4e-12 for the field route, 3e-6 for the dipole FD.

## Lines

**F2 — benzene, against the E8 run's own FD APT** (`e8_benzene_ccpvdz_dip_2026-10-03/apt_ccsd_t.npz`; same geometry and frozen core):
- max |ΔP| ≤ **1e-3 e**. The FD APT's own noise is a sum rule of 2.8e-4 and a symmetry spread of 5.8e-4.
- The field route's sum rule ≤ 1e-6.
- Fails → the pyridine APT is not used, and the cause is found first. The run stops there (`probes/cc_apt_field_check.py`).

**F3 — pyridine:** sum rule ≤ 1e-6. The distance to its B3LYP APT is reported, not judged.

**R3H — read-out (3) on pyridine.** T3 at the TZ tier with chain 34's three carried models, the same arguments as the 10 Oct folds run
(`probes/runs/t3_folds_1010.json`), with `--apt` for pyridine (and benzene's cc-pVTZ APT as before). The quantity is the intensity rel. rms,
modes matched by eigenvector, for "head tuned, L2 1" against the "zero rule" column.
- **Informative** when the zero rule's value is ≥ 0.05.
- **Pass** when the network's mean over the three seeds is ≤ 0.25 and below the zero rule.
- Spectrum overlap is reported beside it.
- **Not informative** (zero rule < 0.05) → pyridine's symmetry also fixes its shapes. Fluorobenzene or benzonitrile is next, at the same cost and
  with the same lines.

**Note before the read:** pyridine's T3 frequencies are already known (10 Oct folds, seed 0, head tuned L2 1). CH-oop is 10.6 cm⁻¹ against the
zero rule's 5.4, while ring-ip and CH-stretch are better than the zero rule. A fail on intensities is therefore possible, and it would be
informative in its own right.

**Cost:** six CCSD(T)/cc-pVDZ gradients per molecule at 4 threads beside the five-ring runner and the APT recompute. Not measured for a gradient
in a field; the E8 displaced points took ≈ 2 min of (T) lambda at 5 threads. The first gradient's time is logged, and T3 takes ≈ 8 min per seed.

## Outcome

*(appended after the runs)*
