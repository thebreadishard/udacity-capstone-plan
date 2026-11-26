# Pre-registration: the ano-pVQZ MP2 step on a second molecule, naphthalene

Written 26 Nov 2026, 07:55, before any ano-pVQZ row of naphthalene exists. TASKS 300 and 320. It follows the benzene test
(`PreRegistration_2026-11-25_ANO_Step_Benzene.md`, outcome USEFUL by recipe 5 on 26 Nov 03:06), whose registration says: the same
test on a second molecule before anything is adopted. The user chose naphthalene (26 Nov 07:41) and all 15 rows on a rented server
('Alles, server').

## Question

Does the MP2 step in ano-pVQZ, which took benzene's out-of-plane group from 30.2 to 7.1 cm⁻¹ against CCSD(T)/ano-pV5Z, do the same
on a fused-ring molecule?

## What is computed and what is held

- Composite Hessian at the corpus geometry (B3LYP): H = CCSD(T)/cc-pVDZ + (MP2/X − MP2/cc-pVDZ).
- Held: the CCSD(T)/cc-pVDZ Hessian (`probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz`, VALID, 10
  frozen orbitals) and the DF-MP2 rows in cc-pVDZ and cc-pVTZ (`dfmp2_composite_2026-10-19/`, psi4 1.10.2, 15 rows).
- Run: the 15 DF-MP2 rows in ano-pVQZ (the Basis Set Exchange file the benzene test used, cc-pVQZ fitting sets, 10 frozen
  orbitals, step 0.005 bohr, psi4 through `probes/dfmp2_rows.py`), and the plan's first row once more with cc-pV5Z fitting sets.
  Lane `probes/ano_step_naphthalene.sh`; check W on water is its smoke. Upstream calls are those of the benzene run: psi4's
  tests/dfmp2-grad1 and dfmp2-grad5 (DF-MP2 gradient against finite differences) and tests/psithon2 (PSIPATH).
- Two recipes are read: the control (X = cc-pVTZ, held rows) and the ano-pVQZ step. The other recipes of the benzene test did not
  reach its USEFUL line and are not repeated.

## The counterpart, and what it can and cannot show

No published CCSD(T) force field of naphthalene was found (searched 23 Nov). The counterpart is the measured fundamentals
(Martin, El-Yazal & François 1996, [doi 10.1021/jp960598q](https://doi.org/10.1021/jp960598q), as listed by NIST CCCBDB;
`probes/data/naphthalene_fundamentals_martin1996.json`). A harmonic frequency belongs above its fundamental; benzene's
out-of-plane harmonics (ano-pV5Z) lie 5 to 22 cm⁻¹ above theirs. So this test can show that a fault of tens of cm⁻¹ goes away. It
cannot show 2 cm⁻¹, and it is not read as if it could.

Frequencies are read **as computed**, without the first-order geometry term: there is no force field of naphthalene at the corpus
level and no CCSD(T)/cc-pVTZ gradient. On benzene that term moves a C–H wag down by up to about 20 cm⁻¹, so here a C–H wag's place
above its fundamental is flattered; the rise of a mode between the two recipes is not affected to first order. Every outcome
carries this sentence.

Modes are named by D2h species from the mode vectors and paired with the measured ones by frequency order inside a species (the
method of `probes/fundamentals_vs_experiment.py`, registered 25 Oct); a pair with a neighbour of its species within 15 cm⁻¹ is
flagged as a possible crossing.

## Known beforehand

The control is known (read of 19 Nov on the carried composite; repeated today from the DF rows by the read script): harmonic minus
fundamental for the 15 out-of-plane modes, cm⁻¹ —
B3u 176 −9.1, Au 195 −15.0, B1g 386 −4.5, B2g 461 +1.4, B3u 476 −1.5, Au 581 +17.5, B1g 717 +16.9, **B2g 770 −32.6**, B3u 782
+15.7, Au 841 +2.5, B2g 876 −3.7, B1g 943 +0.2, B3u 958 −3.2, **Au 970 −15.6**, **B2g 980 −17.1**.
The B2g mode at 770 is the ring puckering, the counterpart of benzene's ω4, which rose by 34.8 cm⁻¹ with the ano-pVQZ step
(−36.1 → −1.3 against ano-pV5Z). No ano-pVQZ number of naphthalene is known.

## Lines (compared on unrounded values)

Judged: the 13 out-of-plane modes above 300 cm⁻¹. The two butterfly modes (176, 195) are reported and not judged: for a floppy
mode of that kind the fundamental may lie above the harmonic value, so its sign proves nothing.

- **TRANSFERS**: the B2g mode at 770 rises by at least 20.0 cm⁻¹ from the control, **and** no judged mode's harmonic lies more
  than 5.0 cm⁻¹ below its fundamental.
- **NO TRANSFER**: the B2g mode at 770 rises by less than 10.0 cm⁻¹.
- **BETWEEN**: anything else.
- **CONTROL FAILED** (no outcome): the control does not repeat the three values in bold (pins −33.0, −15.6, −17.1 from the read
  of 19 Nov) within 0.5 cm⁻¹ each.
- **NO OUTCOME**: the ano-pVQZ composite has an imaginary mode or its modes do not sort into naphthalene's species.

Reported, not judged: the 33 in-plane modes' change between the two recipes (mean, rms, largest; C–H stretches apart). Against
fundamentals a few cm⁻¹ in plane cannot be read — most in-plane harmonics sit 7 to 120 cm⁻¹ above their fundamentals (anharmonicity
and the geometry convention), which hides a basis-set effect of that size. On benzene the step left 'other in plane' where it was (8.8 → 8.9) and improved the C–H stretches.

Checks reported under any outcome: the fitting check (largest change of any element of the repeated row, line 1e-6 E_h/bohr²; on
benzene it was 2.2e-5, at the size of the rows' own symmetry spread — over the line, said, not blocking); the rows' symmetry
spread; the psi4 version; possible crossings among the judged modes.

## The read

`probes/ano_step_read_naphthalene.py <run dir> <out prefix>` (tests: `tests/test_ano_step_read_naphthalene.py`, the lines at their
edges on made-up rows and the read through row files built from the held Hessians: control's own rows read as NO TRANSFER with
zero rise, a 2 % stiffer composite reads as its √1.02, an imaginary mode gives NO OUTCOME, wrong files are refused).

## What follows

- TRANSFERS: the step's effect is shown on two molecules, one against a converged reference and one against measurement. TASKS
  320 (the step into the reference recipe) goes to the user with both, and with what remains open: the C–H wags' 7–10 cm⁻¹ on
  benzene, which the diagnostic assigns to the coupled-cluster part (TASKS 319).
- NO TRANSFER: the benzene result is not a property of the step on PAHs; 320 is not proposed and the ring-puckering fault of
  fused rings is a question of its own.
- BETWEEN: reported as it is, mode by mode; no adoption on it without the user.

## Price (estimates, to be measured by the run)

Scaled from the cc-pVTZ rows of both molecules (21 → 136 s per row; memory × 2.6): about 2.6 h per row, 39 h for 15 rows, on
benzene's laptop timing. psi4 was given 8 GB on benzene and peaked at 6.9 GB (9.3 GB with cc-pV5Z fitting sets); what naphthalene
needs is not known. The run states each label's time and peak memory.
