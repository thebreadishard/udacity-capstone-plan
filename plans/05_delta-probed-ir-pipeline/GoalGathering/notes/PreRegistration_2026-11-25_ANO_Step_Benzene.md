# Registration: another target basis in the composite's MP2 step, on benzene

Written 25 Nov 15:53, before any run of it (TASKS 300; the user, 25 Nov 2026: 'Eerst de ANO-proef'). To be approved by the user before
the first calculation; nothing here has been computed except what is cited as already known.

## The question

Our reference Hessian is H = CCSD(T)/cc-pVDZ + (MP2/X − MP2/cc-pVDZ), with X = cc-pVTZ. On benzene, corrected to the higher
level's minimum (the first-order geometry term, 25 November), it stands against published CCSD(T)/ano-pV5Z harmonics (Semidalas &
Martin, Mol. Phys. 2023, [doi.org/10.1080/00268976.2023.2263593](https://doi.org/10.1080/00268976.2023.2263593), Table 5) at 7.6
cm⁻¹ rms on the four C–H stretches, 30.2 on the six out-of-plane modes and 8.9 on the other ten
(`probes/results_m1/supervisor_chat_2026-11-25/benzene_geometry_term.txt`). The out-of-plane modes ω4, ω5 and ω17 are 37, 50 and
36 cm⁻¹ low. **Does another X bring the out-of-plane modes to the published values, without a larger basis in the CCSD(T)
part?**

## Fixed before the run

- **Molecule:** benzene, at the corpus geometry (B3LYP/6-31G*), where the CCSD(T)/cc-pVDZ Hessian and the full
  CCSD(T)/cc-pVTZ Hessian already exist.
- **Reference:** the twenty CCSD(T)/ano-pV5Z values as typed into `benzene_geometry_term.py`; each mode labelled from its own
  vector (in or out of plane, parity under inversion, character under C6) and matched within a symmetry species by order; a
  degenerate pair counted once.
- **The geometry term:** as computed on 25 November — the Newton step from the stored CCSD(T)/cc-pVTZ gradient and the Hessian
  being corrected, the B3LYP cubic constants of level G, the functions of `probes/geometry_term_check.py`. The same gradient for
  every recipe, so that the recipes differ in the step alone.
- **The recipes, X =**
  1. cc-pVTZ, by DF-MP2 — the control. It must repeat the conventional-MP2 composite's 7.6 / 30.2 / 8.9 within 0.5 cm⁻¹ per
     group; its difference is the number for the change from conventional MP2 to DF-MP2 that the supervisor page lacks.
  2. cc-pVQZ.
  3. roos-ano-tz — the atomic-natural-orbital triple-zeta basis that psi4 1.11 ships.
  4. ano-pVTZ and 5. ano-pVQZ (Neese & Valeev) — the family of the published reference. psi4 does not ship them; the files come
     from the Basis Set Exchange and are compared with a second source before use. **Only on the user's word for the download.**
- **MP2 as in production:** psi4 DF-MP2 analytic gradients, the anchors' symmetry-unique displacements, step 0.005 bohr, frozen
  1s, spherical functions (`probes/dfmp2_rows.py`). For cc-pVXZ the matched cc-pVXZ-JKFIT and cc-pVXZ-RI auxiliary sets; for
  the ANO sets, which have none, cc-pVQZ-JKFIT and cc-pVQZ-RI, with one row recomputed with cc-pV5Z auxiliary sets as the
  check on the fitting (line: the row's largest element changes by less than 1e-6 Eh/bohr²).
- **Groups and measure:** rms over the four C–H stretches, the six out-of-plane modes and the other ten in-plane modes, each
  distinct mode once, corrected composite minus ano-pV5Z, cm⁻¹.

## Lines

- **PASS (the user's bar, 25 Nov: '2 cm⁻¹ per soort'):** a recipe with all three groups at or under 2.0.
- **USEFUL:** a recipe with the out-of-plane group at or under 10.0 and neither other group more than 1.0 above the control's.
  Then that X is proposed as the step's target, and the same test follows on a second molecule before anything is adopted.
- **NO GAIN:** no recipe lowers the out-of-plane group by 5.0 or more below the control. Then MP2 does not carry the basis-set
  effect on these modes, and the CCSD(T) part itself needs the larger basis.
- Anything between USEFUL and NO GAIN is reported as measured, without a verdict.

What is expected, said beforehand: PASS is not expected from any recipe — full CCSD(T)/ano-pVTZ itself is 5.2 / 3.4 / 3.3 from
ano-pV5Z in these groups by the same table, and a DF-MP2 cc-pVQZ step moved benzene's out-of-plane modes up by only 0.5–11.8
cm⁻¹ on 10 November (TASKS 194). The test is run to find out whether USEFUL or NO GAIN holds.

## Not decided by this test

Whether the recipe holds on any other molecule (one molecule; a second with a published reference follows, TASKS 302); whether
the supervisor accepts it (TASKS 310); anything about the network.

## Before the launch

- `probes/dfmp2_rows.py` names the auxiliary sets after the orbital basis; it needs an option for them. A change of code that
  runs use: a test for the switch, an independent review, then the merge.
- The upstream test that makes the same psi4 call with a user-supplied basis is named in the launch note.
- A run spec per recipe through `tools/runspec.py`, each with its memory bound (the cc-pVQZ rows peaked at 5.5 GB on 10 Nov) and
  its dry run; on the laptop, free.
- The read is a script that takes the row files and prints the table and the outcome by the lines above; it is run on the
  control first.

## Amendment 1 (25 Nov 16:14, before any run): what the supervisor's papers add

Read the same day (`Literature_2026-11-25_Supervisor_Papers.md`); nothing of this test had been computed.

- **A second reference beside ano-pV5Z:** Martin, Taylor & Lee's CCSD(T)/ANO4321′ values of 1997 (ω4 708.8, ω5 1008.8, ω10
  865.1, ω11 687.2, ω16 405.8) are printed beside the published ano-pV5Z ones in the read; the lines stay on ano-pV5Z.
- **Two more recipes, both MP2 only:** 6. the step's target extrapolated to the basis-set limit from cc-pVTZ and cc-pVQZ (the
  review's 'cheap' scheme: Hartree–Fock and MP2 correlation separately, the latter by n⁻³); 7. recipe 6 plus an MP2
  core-valence term (all electrons minus frozen core in cc-pwCVTZ). Same lines.
- **One diagnostic, not a recipe:** [CCSD(T) − MP2] on ω4, ω5 and ω17 from the Hessians we hold, in cc-pVDZ and in cc-pVTZ
  (full CCSD(T)/cc-pVTZ minus MP2/cc-pVTZ). If that difference changes by more than 5 cm⁻¹ between the two basis sets on any of
  the three modes, the artefact sits in the coupled-cluster part as well and no MP2 step can remove it: said with the outcome.
- **The ano-pVTZ file** fetched on 25 November has a double-zeta shape and is not used; recipe 4 runs only with a file that has
  carbon f functions (C [4s3p2d1f], H [3s2p1d]), from a source checked against a second one.
