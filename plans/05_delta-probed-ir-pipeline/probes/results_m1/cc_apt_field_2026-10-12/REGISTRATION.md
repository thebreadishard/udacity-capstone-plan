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

**12 Oct, 16:3x.** Run `probes/runs/lever6_cc_apt_1012.json`, 14:14–16:35, log `lever6.log`.

**F2 — PASS.** Benzene: the field route is 1.0e-4 e from the E8 run's FD APT (line 1e-3). Its sum rule is 4.7e-11, against the FD APT's
2.8e-4. Six CC gradients took 3,128 s at 4 threads (`F2_benzene_check.log`).

**F3 — PASS.** Pyridine: sum rule 6.0e-11, 2,799 s (`pyridine_ccpvdz_field.npz`). No B3LYP APT exists for pyridine, so no distance to it is
reported.

**R3H — informative, FAIL on the registered column.** Intensity rel. rms with modes matched by eigenvector, pyridine, CC APT
(`out/T3_tz_pyridine_apt_c34_seed{0,1,2}_2026-10-12.log`):

| column | seed 0 | seed 1 | seed 2 | mean |
|---|---|---|---|---|
| zero rule | 0.262 | 0.262 | 0.262 | 0.262 |
| head tuned, L2 1 (registered) | 0.305 | 0.303 | 0.323 | **0.310** |
| head tuned, L2 0 (reported, not judged) | 0.147 | 0.059 | 0.113 | 0.106 |

The zero rule is 0.262 ≥ 0.05, so the test is informative: pyridine's modes do mix, unlike benzene's. The registered column is 0.310, which
fails both conditions: it is above 0.25 and above the zero rule. With the standard fine-tune (λ = 1), the network's corrected Hessian gives
pyridine worse intensities than the B3LYP Hessian does.

The spectrum overlap, which also counts the positions, goes the other way: 0.751 against the zero rule's 0.626 (λ = 0: 0.781). The positions
improve; the intensities from the mode shapes do not. This matches the note written before the read: CH-oop frequencies are already worse
than the zero rule on pyridine (10.6 against 5.4 cm⁻¹).

The λ = 0 column (0.106) is far better than both. It is post hoc and one molecule, so it is not a result. It does say what to register
next: whether the L2 pull of the TZ standard (amendment (A), chosen on frequencies) costs mode shapes in general. That needs a second
low-symmetry molecule with a CC APT: fluorobenzene or benzonitrile, at the same cost (≈ 50 min each), with this read registered for both
columns before it runs.

## Lever 6b — two more low-symmetry anchors (registered 12 Oct, 16:4x, before the runs; the user: 'Ja, doe fluorbenzeen en benzonitril maar')

**Question.** Does the L2 pull of the TZ standard (head tuned, λ = 1; amendment (A) of 7 Oct, chosen on frequencies) cost the mode shapes
in general? On pyridine the registered column (λ = 1) gave 0.310 against the zero rule's 0.262, and λ = 0 gave 0.106. That was read
post hoc, on one molecule.

**Molecules.** Fluorobenzene (B_8b12a55d3a) and benzonitrile (A_3100da3761). Both are C2v carried TZ anchors with CCSD(T)/cc-pVDZ FD
Hessians from 30 Sep and no dipoles.

**CC APT.** Same method as above: `probes/cc_apt_field.py`, F = 1e-3, cc-pVDZ, frozen core by the E8 rule, `--fast`.
- Line: sum rule ≤ 1e-6 per molecule. F2 already validated the route on benzene.

**Read.** T3 with chain 34's three models as in R3H, `--apt` for all three low-symmetry anchors (pyridine, fluorobenzene, benzonitrile).
Matched intensity rel. rms, seed means, two columns: "head tuned, L2 1" (λ = 1) and "head tuned" (λ = 0), against the "zero rule".

**Lines, per molecule** (informative when the zero rule is ≥ 0.05):
- **Registered column, unchanged:** pass when λ = 1 is ≤ 0.25 and below the zero rule.
- **The pattern:** the L2 cost holds on a molecule when λ = 1 minus λ = 0 is at least 0.05.
  - **Holds on both:** with pyridine that makes three of three. A chain to re-choose λ on frequencies and intensities together is registered
    next. The standard is not switched by this read.
  - **Holds on neither:** pyridine's λ = 0 advantage was one molecule's, and λ = 1 stays.
  - **One of two:** noted; the next low-symmetry CC APT decides.

Pyridine is re-read in the same T3 run; its numbers must reproduce R3H within seed noise. That is a check on the run, not a new result.

**Cost.** About 50 min of CC per molecule at 4 threads, then three T3 seeds of ≈ 13 min. The four threads come from the APT recompute's
second lane, which is stopped for the run and restarted after it.

### Outcome of lever 6b (12 Oct, 22:2x)

Run `probes/runs/lever6b_cc_apt_1012.json`, 16:41–22:26 (`lever6b.log`).

**CC APTs — both PASS.**
- Fluorobenzene: sum rule ≤ 1e-6, 1 h 44 min.
- Benzonitrile: sum rule 8.9e-11, 11,432 s.

Each gradient took about twice benzene's time: the (T) lambda needed up to 26 cycles. My estimate of ≈ 50 min per molecule was wrong.

**Read** (matched intensity rel. rms, CC APT, seeds 0/1/2 → mean; `out/T3_tz_lowsym_apt_c34_seed{0,1,2}_2026-10-12.log`):

| molecule | zero rule | λ = 1 (registered) | λ = 0 | λ = 1 − λ = 0 | registered column | L2 cost (≥ 0.05) |
|---|---|---|---|---|---|---|
| pyridine (re-read) | 0.262 | 0.305 / 0.303 / 0.323 → 0.310 | 0.147 / 0.059 / 0.113 → 0.106 | 0.204 | FAIL | holds |
| fluorobenzene | 0.104 | 0.178 / 0.170 / 0.169 → 0.172 | 0.081 / 0.157 / 0.057 → 0.098 | 0.074 | FAIL (≤ 0.25 but above the zero rule) | holds |
| benzonitrile | 0.258 | 0.462 / 0.446 / 0.420 → 0.443 | 0.296 / 0.211 / 0.248 → 0.252 | 0.191 | FAIL | holds |

**The run check holds.** Pyridine reproduces R3H to the third digit in every seed and column.

**All three molecules are informative**, since every zero rule is ≥ 0.05. The registered column fails on all three: with λ = 1 the network's
mode shapes give worse intensities than B3LYP's Hessian. The L2 cost holds on both new molecules, so with pyridine it is three of three.

As registered, a chain to re-choose λ on frequencies and intensities together is registered next. The standard is not switched by this read.

**Reported beside, not judged:**
- λ = 0 is about level with the zero rule on two molecules (fluorobenzene 0.098 against 0.104, benzonitrile 0.252 against 0.258) and well
  below it on pyridine. So at λ = 0 the network's mode shapes are at least as good as B3LYP's; at λ = 1 they are worse.
- The spectrum overlap (positions and heights) is better than the zero rule in both columns, for example benzonitrile 0.617 (λ = 1) and
  0.822 (λ = 0) against 0.479.
- The cost of λ = 1 sits in the eigenvectors, not in the band positions.
