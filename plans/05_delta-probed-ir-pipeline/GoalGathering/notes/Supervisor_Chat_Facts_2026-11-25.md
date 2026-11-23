# Fact sheet for the conversation with the supervisor, 25 November 2026

Reference for `Supervisor_Chat_Brief_2026-11-25.md`, whose rules govern every answer; split off on 23 November 2026. Read at the
start of the conversation, used only where a question touches it. It is there to answer rightly, not fully: a fact that was not
asked for is not mentioned, and no answer carries more than two numbers per part of her question.

Every number here has its source in the project's records as found on 23 November; where the source is a file, it is named.

## Numbers likely to be asked, with their counterpart and slide

- The network against ωB97X, harmonic, rms per kind of vibration, on the 48 test molecules: 0.8–2.4 cm⁻¹; B3LYP alone ≈ 23
  (slide 12). Thin spots: 'other' on the 8 small molecules has mean 2.38 with an interval 1.45–3.19; CH out-of-plane there rests on
  5 molecules. The networks that measure train on 1,075 of the 1,132, without the test molecules.
- Beyond the training sizes: 7.9 cm⁻¹ rms over all modes on four molecules of 36–60 atoms (24–42 carbon atoms: coronene,
  peropyrene, ovalene, hexabenzocoronene); B3LYP 22.8. Adding five large molecules to the training left it at 7.8. Nothing tested
  reaches 50 carbon atoms (slides 12, 15).
- CCSD(T) reference Hessians: the slides say 11 done (benzene full CCSD(T)/cc-pVTZ, ten composite) and 32 running on five rented
  servers. **Since the PDF was sent, seven of those 32 have finished and passed their checks: 18 on 23 November**, and the DFT
  step for the remaining molecules of the plan is done (122 of 128 usable; six have an imaginary mode and are redone). 167
  planned, about 300 as an estimate with 'other' and first cations (slides 10, 11, 20, 21).
- The 167: from a rehearsal on ωB97X data, a simpler task than the real step; CH out-of-plane crosses 3 cm⁻¹ at 167 (153–177);
  'other' does not by 200 (3.6); the priced 167 are the cheapest molecules, not the random draw of the rehearsal. The first read
  against CCSD(T) comes when 20 reference Hessians are in the training (slides 20, 21).
- The composite against full CCSD(T)/cc-pVTZ on benzene, the only check: 4.6 cm⁻¹ rms, largest 8.5 (slides 10, 26).
- First read against CCSD(T) on the 11, too few for a verdict: B3LYP 16–35 cm⁻¹ per kind of vibration, the ωB97X-trained network
  29–78. The stand-in proves the method learns; it is not a step towards CCSD(T) (slide 15).
- The same molecule turned, mirrored or re-listed: bands move up to 10–11 cm⁻¹ for two molecules; not repaired; each spectrum
  measures it and drops the claim above 3 cm⁻¹ (slides 13, 15).
- Cost of one reference Hessian: naphthalene 19 hours on a rented 16-core server plus about 2 hours for the MP2 step, about €6
  (our record of 20 November; not on a slide). The cheapest 167: about €4 each for the CCSD(T) part, about €730 together; the
  average over all molecules we could still compute is about €18. Growth: formally N⁷; measured, anthracene costs 13 times
  naphthalene per gradient; pyrene and coronene not measured. The step from 167 to about 300: roughly €1,000–2,500, an estimate
  (slides 10, 21).
- Cost so far at the hosting company, all calculations of the project: about €1,790 (slide 21).
- A finished run: benzonitrile, 12 minutes for the DFT step, 1.4 seconds for the network, 31 minutes for the anharmonic step on a
  busy laptop (11 minutes on a free one) (slide 9).
- Not done: any comparison with measured spectra; cations (no reference Hessian yet, though the open-shell code now fits in
  memory); intensities are uncorrected B3LYP.

## Her field: what we did, so that 'I will look that up' is rarely needed

- **Our VPT2 runs** (the reference for the provisional anharmonic correction, and where the coronene modes come from): a quartic
  force field in normal coordinates built by our own code from finite differences of Hessians, at B3LYP; VPT2 by our own code;
  Fermi resonances by Martin's test with the open-source program's default thresholds, a window of 200 cm⁻¹ in frequency and a
  minimum interaction of 1 cm⁻¹ (Martin et al. 1995); the polyads are then diagonalised by that program's solver, with a repair of
  ours for polyads it left unmerged. **Darling–Dennison resonances are not treated**: there is no such term in our code.
- **Degenerate modes**: the quartic constants are averaged over the pairs of a two-dimensional irreducible representation, and a
  resonance that touches such a pair is left deperturbed and named. Coronene is D6h, so this applies to it.
- **The two coronene modes**: +179.2 cm⁻¹ on the mode at 807.1 and +66.3 on the one at 642.9. Checked: the diagonal quartic
  constant on two integration grids agrees within 0.7 %; the deperturbed and the resonance-treated results are equal for these
  modes; the one near-resonant triple has a zero cubic constant by symmetry. That does not exclude a missed resonance or an error
  in the force field; say the checks and stop (rule 8); see also 'beyond second order' below. In our set 28 of 2,244 vibrations shift by more than 5 % of their frequency.
- **The provisional anharmonic correction in the pipeline**: a fitted shift per fundamental that uses GVPT2 on the molecule's own
  xTB force field as one of its inputs (details under 'More facts'); its error against B3LYP VPT2 on the two molecules held out
  of the fit, coronene and tetracene, is 3.4–8.4 cm⁻¹ per kind of vibration; on benzonitrile the CH stretch is 17.8. Not compared
  with experiment.
- **Her group's published spectra and software**: never described from memory (rule 7).

## More facts, asked in the second rehearsal

- **The 1,132 are not all neutral.** They are 1,082 neutral closed-shell entries and the radical cations of 50 molecules, each
  with ωB97X as the stand-in target; the network takes the charge state as an input. So it has seen cations, but there is no
  separate error for them in this brief and no CCSD(T) reference for any. The pipeline of slide 8 admits neutral closed-shell
  molecules only, so it gives nothing for a cation, positions or intensities. This is what squares slide 15 with the training set.
- **Frozen core**: the 1s orbitals are frozen in the CCSD(T) and in the MP2 calculations (one per first-row atom), the
  density-fitted MP2 ones included.
- **Our own three scale factors** use PAHdb's region boundaries, 9 and 4 µm (1111 and 2500 cm⁻¹); refitted to ωB97X they leave
  2.0 / 9.2 / 15.5 / 8.6 cm⁻¹ for CH stretch / CH out-of-plane / ring in-plane / 'other', where the network of that date left
  1.25 / 2.36 / 1.82 / 3.35 (25 October). The ≈ 23 cm⁻¹ of slide 12 is unscaled B3LYP.
- **A mode that is half CC stretch and half CH in-plane bend is 'ring in-plane'**: the two motions are one kind with us (slide 12).
  A mode gets its kind from a frequency window together with its character (the share of hydrogen motion and of out-of-plane motion).
- **Where numerical derivatives are used**: (1) the CCSD(T) Hessians, finite differences of analytic gradients, each
  symmetry-unique displacement forward and back; (2) the quartic force fields for VPT2, finite differences of Hessians along normal
  coordinates; (3) a repair of very soft modes in the DFT set, finite differences along the mode. The DFT Hessians themselves are
  analytic. The short note of slide 19 is about (3): a step along a soft normal mode biases the curvature by a term in the square
  of the step. It is not about the CCSD(T) Hessians.
- **The same molecule turned, mirrored or re-listed**: measured on ten molecules with the current network; two are above 3 cm⁻¹
  (9-methylanthracene 10.0, diphenylacetylene 11.2), biphenyl 2.85, 4-phenylpyridine 2.5, benzonitrile 2.4, diphenyl ether 1.4,
  the rest below 1. Not measured on all 1,132. The cause is in signed inputs of the last part of the network and, for a linear
  group, in a reference direction taken from the coordinate axes; the message-passing part gives 0.000 when tested alone.
- **The gradient term**: the Hessians of the better method are taken at the B3LYP geometry, and the gradient term of the
  coordinate transformation is left out (slide 25); its effect on the frequencies is not measured for any molecule. Never say it
  is 'absorbed' in the target.
- **Why four substituents do not transfer** (CH₃, OCH₃, SH, CONH₂; 4.1–7.5 cm⁻¹): not established. What was seen: OH, NH₂, CHO
  and CF₃ also have a torsion and do transfer (2.2–2.6 cm⁻¹). The ωB97X gradient at the B3LYP geometry for these four was not
  looked at.
- **Where the composite's 4.6 cm⁻¹ on benzene sits** (rms against full CCSD(T)/cc-pVTZ, per kind of vibration; record of
  6 October, `modules/05_support_predictor/out/composite_test2_benzene_2026-10-06.md`): ring in-plane 3.3, CH stretch 4.4, CH
  out-of-plane 7.3, 'other' 3.3. For comparison CCSD(T)/cc-pVDZ alone: 24.9 / 137.9 / 69.6 / 40.8, and B3LYP: 14.1 / 38.7 / 14.9 /
  13.3. So the largest part is in the CH out-of-plane modes. The single largest deviation, 8.5 cm⁻¹, is the out-of-plane mode at 709
  cm⁻¹ in CCSD(T)/cc-pVTZ, which the composite puts at 700 (23 November, both stored Hessians diagonalised and paired by mode
  overlap: rms 4.61 over the 30 modes, the same per kind; `probes/results_m1/supervisor_facts_2026-11-23/benzene_mode.txt`).
  Its label is a2u, the infrared-active CH wag in which all six hydrogens move to the same side: odd under inversion (−1.00),
  even under the six-fold rotation (+1.00), fully out of plane (`probes/results_m1/supervisor_facts_2026-11-23/benzene_mode_label.txt`). The
  other single out-of-plane mode, b2g (even under inversion, odd under the six-fold rotation), is at 674 cm⁻¹ in our
  CCSD(T)/cc-pVTZ Hessian, so a2u lies above b2g there (709 / 674), against published CCSD(T) harmonics near the basis-set
  limit (a2u 683.6, b2g 712.4 with ano-pV5Z; Semidalas & Martin, Mol. Phys. 2023, doi 10.1080/00268976.2023.2263593, Table 5). Two known causes, both looked up on 23 November:
  (1) our reference Hessians are taken at the B3LYP geometry (C–H 1.0871 Å, where the CCSD(T) gradient is 3e-3 Eh/bohr), not
  at the CCSD(T) minimum: that puts the four C–H stretches 31–37 cm⁻¹ and a2u +25 away from the published values. It was
  found on 22 September; the first-order geometry term through the B3LYP cubic constants brings a2u to +2 and the C–H
  stretches back, and was validated on 18 molecules on 1 November — but it is not yet a step of the pipeline. (2) The two b2g
  ring-puckering modes are 38 and 31 cm⁻¹ too low, and the geometry term does not repair them. That is a published basis-set
  effect: Martin, Taylor and Lee (Chem. Phys. Lett. 275, 414, 1997) found these two modes hypersensitive to the basis set at
  CCSD(T), traced to intramolecular basis-set superposition error and cured by atomic-natural-orbital basis sets; the 2023
  paper has them 17 and 14 cm⁻¹ low even with an explicitly correlated triple-zeta basis and 4 and 6 low with ano-pVTZ. The
  other in-plane modes of our Hessian are within 8 cm⁻¹ of the published values, except one (b1u at 1010, −15). So the
  composite's 4.6 cm⁻¹ on benzene is agreement with a cc-pVTZ reference that itself has this deficiency in the two b2g
  modes. If she raises it: yes, known for these two modes, with the references; whether an ANO basis in the MP2 step repairs
  it for our composite has not been tried. All six out-of-plane modes come out too low in the composite: −8.5, −7.8 (a pair),
  −7.3 (a pair), −4.9. The largest in-plane deviations are +5.7 at 1336 and −5.1 at 1378. On her point
  about MP2 and out-of-plane modes: anthracene's CCSD(T)/cc-pVDZ Hessian came out with an imaginary out-of-plane mode (−51 cm⁻¹,
  B3LYP 92), the small-basis arene artefact, so from three rings on the out-of-plane basis step is a repair, not a refinement;
  whether MP2's own small-basis artefact contaminates that step was checked on benzene only.
- **The direction of the correction: ωB97X and CCSD(T) point opposite ways.** On nine reference Hessians (27 October), the mean
  shift from B3LYP to the composite divided by the mean shift from B3LYP to ωB97X, median over the molecules: 'other' −1.45, ring
  in-plane −1.39, CH stretch −0.79; CH out-of-plane 0.02 for a single ring, −0.45 for fused rings, −0.90 with a five-membered
  ring. A negative ratio means opposite sign. This agrees with her likely suspicion that the stand-in corrects the wrong way, and
  it is why the ωB97X-trained network is further from CCSD(T) than B3LYP. Per molecule and per mode it was not tabulated.
- **The same on today's 18 reference Hessians** (23 November, labels only, no network run; per molecule in
  `probes/results_m1/supervisor_facts_2026-11-23/``anchor_sign.json`). Mean shift of B3LYP's modes under the composite / under ωB97X, median over the molecules, cm⁻¹:
  ring in-plane −14.6 / +10.6, CH stretch −34.8 / +43.3, 'other' −12.1 / +9.6, CH out-of-plane −7.2 / +21.8. The two means
  have opposite sign in 17 of 18 molecules for ring in-plane, 18 of 18 for CH stretch, 17 of 18 for 'other', 11 of 18 for CH
  out-of-plane. So B3LYP's harmonic frequencies are too high against the composite and ωB97X's are higher still. The eleven
  older molecules reproduce the 27 October ratios (−1.42, −0.79, −1.45). The seven new ones, all substituted single rings but
  indole, differ in two kinds: 'other' has ratio −0.25 instead of −1.45 and its pattern within a molecule now follows ωB97X
  (correlation +0.65 against −0.35), and CH out-of-plane has a composite mean near zero or positive (+0.8 against −9.4).
  Seven molecules: a description, not a finding.
- **Our VPT2 force fields**: B3LYP/6-31G* in PySCF, integration grid (75, 302) unpruned, each molecule at its own minimum at
  that setting, analytic Hessians displaced ± along every normal coordinate with a step of 0.10 in reduced (dimensionless)
  coordinates, our own code with a check that two routes to the same constants agree; Fermi window 200 cm⁻¹. So a smaller basis
  than her B97-1/TZ2P. The coronene result (harmonic, deperturbed and resonance-treated fundamentals) is in a file; the force
  field with its cubic and quartic constants is stored too, but where and in which format was not checked: check before promising
  to send it.
- **What the provisional anharmonic correction is, exactly** (`probes/anharmonic_step.py`): for each B3LYP mode a shift from a
  kernel ridge regression on five inputs — the kind of vibration, the harmonic frequency, the share of hydrogen motion, the share
  of out-of-plane motion, and the anharmonic shift of the matched mode from GVPT2 on the molecule's own GFN2-xTB quartic force
  field. It was fitted to the B3LYP GVPT2 fundamentals of 37 molecules, so the Fermi treatment of those references (window
  200 cm⁻¹, minimum interaction 1 cm⁻¹) is what it imitates. It gives a shift for fundamentals only: **no combination bands and
  no polyad of its own**, so in the CH-stretch region it cannot reproduce the structure she means. A mode gets no shift, with the
  reason printed, when it is a large-amplitude mode, has no xTB partner, or lies where nothing was measured. No accuracy claim is
  made for the anharmonic position. CH stretch: 6.2 cm⁻¹ against B3LYP GVPT2 on the two held-out molecules, 9.0 leaving one ring
  system out at a time, 17.8 on benzonitrile.
- **The two coronene modes, beyond second order** (13 November, afternoon; this is newer than the notes of slides 13 and 19):
  the pair was also solved without perturbation theory, by diagonalising the two modes together in a product basis on the same
  quartic force field. The shifts stay large: +162.3 cm⁻¹ instead of +179.1 for the mode at 807, +38.5 instead of +66.2 for the
  one at 643. The mixed quartic constants of the pair are not zero (−189 and −437 cm⁻¹), so our earlier symmetry argument for them
  was wrong. So within our B3LYP/6-31G* force field the large positive shift is not an artefact of second-order perturbation
  theory; whether the force field itself is right (basis, grid, the step) is the open question, and hers to judge. Three other
  molecules of our set with such modes could not be solved this way.
- **Coronene's force field on disk**: per molecule a file with the cubic and semi-diagonal quartic constants in reduced normal
  coordinates (cm⁻¹) and one with the full semi-diagonal quartic tensor, beside the displaced Hessians; coronene's is
  `probes/results_m1/routea_server_2026-11-10/routea/coronene/G/qff_report.npz` (found 23 November); its contents were not opened, so check the arrays before promising to send them.
- **Cations in the training set, what is on record**: 50 radical cations with ωB97X targets. No error for the cations taken apart
  is in the release's records; the search for the training settings read, on its own selection molecules, 6.1 cm⁻¹ for cations against 2.6 for neutrals (corrected harmonic frequencies against ωB97X, 33 and 474 reads, 23 November). One thing was seen (17 November): with the benzene cation in the training, the network gave
  neutral benzene part of the cation's correction (CH out-of-plane 8.7 cm⁻¹ against 1.6 without the cations); the test molecules'
  cations were then taken out of the measuring networks' training.
- **Do the cations' Hessians break symmetry?** Checked on 23 November for the 60 computed cations of the pool against their
  neutral parents (`probes/results_m1/supervisor_facts_2026-11-23/``cation_symmetry.json`). (a) At the 38 cations whose geometry has a symmetry operation, the B3LYP
  and ωB97X Hessians obey it as well as the neutrals' do (largest violation over the largest element: median 1.3e-3 for
  cations and for parents, the level of the finite-difference noise): no sign of a symmetry-broken wavefunction in the
  Hessian. (b) 11 of 60 cations sit at a less symmetric minimum than the parent. Benzene⁺ went from D6h to D2h (24 operations
  to 8), the expected Jahn–Teller distortion; fluoranthene⁺ lost its two-fold axis (atoms up to 0.2 bohr from the symmetric
  place), which was not expected and is not explained; nine substituted ones lost an operation, four of them by less than
  0.05 bohr. (c) 5 of 60 cation labels have an imaginary B3LYP mode and 4 an imaginary ωB97X mode (−53 to −161 cm⁻¹ for the
  three looked at), so those are not minima or the finite-difference Hessian is noisy there. The training does not use them:
  the loader leaves out every molecule with an imaginary mode at either level, 7 of the 60 cations (read in the
  code on 23 November). Not looked at: ⟨S²⟩ (it is not in the stored records).
- **The network's error on cations taken apart** (23 November, the settings search's selection molecules, three seeds, corrected
  harmonic frequencies against ωB97X; `probes/results_m1/supervisor_facts_2026-11-23/``cation_error.txt`): 11 cations 6.5 cm⁻¹ against 2.9 for 158 neutrals (rms over
  molecules of the seed mean; 6.1 against 2.6 counted per read). It is not one outlier: the eleven lie between 4.7 and 12.5
  (worst fluoranthene⁺ with CONH2), 5.5 without the worst. None of the eleven has a distorted geometry or an imaginary mode.
  All eleven are three- and four-ring cations, so size and charge are mixed in this number. The released network's own records
  have no cation figure.

## Not known to the assistant on 23 November — look these up before Wednesday, or say 'not known'

1. Whether an atomic-natural-orbital basis in the composite's MP2 step repairs the two b2g modes of benzene, and how large the
   same deficiency is in the ring-puckering modes of the larger reference molecules.
2. The signed error against CCSD(T) per single mode (per kind of vibration and per molecule it is known, on 18).
3. ⟨S²⟩ of the cations' B3LYP wavefunctions, and why fluoranthene⁺ lost its two-fold axis.
4. The network's error on cations of one and two rings (the eleven read are three- and four-ring cations).

Where to look for more: the speaker notes of the slides (`C:\\Users\\thebr\\Documents\\CapstoneDeck_2026-11-25\\deck3\\project\\slides`, the text
in each file's `<aside>`), the task board through `probes/state.sh`, and the design notes of 23 November. Look there before
answering from memory; a number that cannot be found is 'I will look that up', not a guess.
