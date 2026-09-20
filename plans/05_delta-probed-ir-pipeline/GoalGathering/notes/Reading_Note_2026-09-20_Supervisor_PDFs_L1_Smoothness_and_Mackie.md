# Reading note, 20 September 2026 — the five PDFs from the supervisor: the three L1 smoothness papers and Mackie 2015/2016

*Received 20 September (evening), copies in `Papers/` (ignored by git): `Russ_Crawford_2004_JCP_121_691_…`, `Subotnik_HeadGordon_2005_JCP_123_064108_…`,
`Mata_Werner_2006_JCP_125_184110_…`, `Mackie_2015_JCP_…`, `Mackie_2016_JCP_…`. Read in full the same evening (text extracted with pypdf; the three L1
papers end to end, the two Mackie papers abstract, theory/methods, results and conclusions). This note records what each paper establishes and what
that changes in plan 05. Papers table items 68, 69, 67, 12.*

## 1. Russ & Crawford 2004 (JCP 121, 691) — the problem, measured

Pulay–Saebø local correlation (Pipek–Mezey occupied orbitals, projected-AO virtual domains chosen by the Boughton–Pulay completeness criterion, 0.02)
gives potential-energy surfaces with steps wherever a domain's atom list changes. Their measurement (LMP2 and LCCSD, cc-pVDZ, PSI3 pilot code):

- Homolytic C–F cleavage in CH₃F: no steps in the dissociation region (the spin-restricted PM bond orbital stays delocalised over both fragments); one step
  of ≈ 1 mE_h at short distance from a lone-pair domain expanding.
- Heterolytic C–C cleavage in singlet ketene: four steps, two of them **near equilibrium** (1.30 and 1.47 Å; 0.15–0.25 mE_h), two in the bond-breaking
  region (0.7–1.0 mE_h).
- Propadienone (more conjugation): **ten** steps, five near equilibrium, 0.1–0.8 mE_h, "a jagged, unphysical appearance".
- Their reading: the steps are "usually small, but often of the same magnitude as the localisation error (ca. 1 mE_h)" and appear "for shifts in the bond
  structure of conjugated systems … even in the vicinity of the equilibrium geometry".

**For us.** This is the effect the frozen spaces remove, and it is the reference scale for our smoothness numbers: their steps are 10²–10³ µE_h; the
transported-space residuals of M1 are 0.05–1.2 µE_h at tight thresholds, and the stage-0 round trip is 0.0002 µE_h. The conjugation remark matters:
PAHs are the class where re-localising at every displaced geometry is most likely to hop, and our decks displace by 0.5–1.0 in the dimensionless
coordinate — inside the range where they saw near-equilibrium steps. The paper does not treat vibrational properties; the frequency application is ours
to make.

## 2. Mata & Werner 2006 (JCP 125, 184110) — the standard remedy, and the prior art for freezing

The direct prior art for the frozen object, stated in §II in two sentences that any referee will quote back at us: *"One obvious remedy to this problem is
to keep the domains fixed. This is a valid procedure when the geometry changes are relatively small, as in geometry optimizations of equilibrium
structures and numerical gradient or Hessian calculations."* And: *"If finite energy differences are used, the domains are determined at the reference
structure and frozen, and the same gradient is obtained as with the analytical method (within the numerical accuracy)."* Frozen domains for numerical
Hessians have been Molpro practice since before 2006 (their refs 23–25 on harmonic frequencies; Rauhut & Werner 2001). The paper's own contribution is
**domain merging** along reaction paths (domains determined at reactants, TS, products; center lists united; fixed for the whole path), shown smooth for
ketene, propadienone, SN2 reactions and a QM/MM enzyme barrier; plus two observations we can use:

- *(T0) is not invariant to unitary rotations among orbitals sharing a domain; pseudocanonical blocks are formed by diagonalising the Fock matrix in
  those subspaces.* This is the precedent for our semicanonicalisation of the transported spaces before the triples.
- *The effect of the domain approximation is very similar at LMP2 and LCCSD(T); test it at MP2/LMP2 before the expensive calculation.* This is the
  precedent for our composite (SCF + LNO-CC − LNO-MP2 + full MP2) and for using MP2-level checks (M2's gate) as the cheap witness of the space error.
- Local methods carry less BSSE, which improves basis-set convergence (their ref 25: vibrational frequencies). Relevant background for the DZ/TZ
  reading of tonight, but our mode-12 effect is MP2's own double-ζ behaviour, not BSSE; do not conflate.

**For us — the novelty statement of gate A must change.** "Correlation spaces held fixed across displaced geometries" is not new; it is textbook Molpro
practice and Mata & Werner say so explicitly. What their frozen object is: an **atom list per occupied orbital** (a PAO domain), which is trivially
geometry-independent because it names atoms, not functions. What ours is: **the orbital spaces themselves** — localised occupied orbitals and the
pair-density-defined LNO virtual subspaces — which have no atom-list description and therefore cannot be "kept fixed" by naming atoms; they have to be
**transported** to each displaced geometry (projection onto the displaced AO basis, re-orthogonalisation, semicanonicalisation), and the transport has
an error that must be measured. That transport rule, its measured projection term, the two-arm diagnostic (fresh vs transported PM, match 1.000;
E_A(0) − E_C(0) = 0.0002 µE_h) and the demonstration at cc-pVTZ on naphthalene are the claim. The sentence "we make local-CC force constants smooth"
must go; the sentence "we make LNO-type spaces, which have no domain list to freeze, transportable, and measure the price" can stay. The literature
search of 6–10 September already found no frozen-space option in PySCF's LNO and only fixed domains for DLPNO-MP2 in ORCA (bib 29); that finding
stands and is now bracketed by the Molpro precedent on the PAO side.

## 3. Subotnik & Head-Gordon 2005 (JCP 123, 064108) — the other remedy, and two cautions we should print

Bump functions multiply the CCD residual so that amplitudes pass smoothly from iterated to perturbative treatment; the implicit function theorem then
gives a C^∞ energy. Demonstrated on N₂ (6-31G*, UHF-based LCCD/LMP2): steps of millihartrees without bumping, none with; **price: the absolute error
doubles** at their aggressive cutoffs. Two remarks bear directly on our design:

- *"For cutoffs slightly smaller … the error decreases by orders of magnitude … when the error is on the order of microhartrees, the discontinuities in the
  amplitudes are no more than numerical noise and not important."* Smoothness is a threshold question as much as a construction question; our tight
  thresholds put us in the regime they describe, and the frozen spaces remove what is left. The paper's own numbers give a way to say this quantitatively.
- *"Smoothness for a mathematician does not mean smoothness for the practising chemist"*: the chemist needs curves that look smooth on the 0.01 Å step
  scale without spurious extrema. Our even/odd fits (c₄/k ≤ 1 % at TZ in-plane) and the linearity of the odd part are exactly that test; print them as such.
- They criticise fixed-domain schemes as "not a theoretical model chemistry" (hysteresis between paths). For a Hessian at one reference geometry this
  criticism is beside the point, but the paper should say so in one sentence: the label is defined at the reference, and the two arms measure what the
  freezing costs there.
- Their orbital machinery (BoysQuad to break rotational degeneracy; caveat that atom-localised hard virtuals become discontinuous when the AO basis nears
  linear dependence) is a reminder that re-localising at every geometry is itself a source of hops in symmetric molecules (naphthalene D2h has degenerate
  PM solutions); transport avoids re-localisation entirely, which is one of its arguments.

## 4. Mackie et al. 2015 (JCP 143, 224314) and 2016 (JCP 145, 084313) — the supervisor's anharmonic line, in detail

Method (both papers): B971/T2ZP quartic force field from Gaussian 09 (tight optimisation, Int = 200 974 grid), transformed to Cartesian derivatives and
fed to a locally modified SPECTRO; VPT2 with resonances handled in polyads; intensities: double-harmonic for fundamentals and for polyad members
(redistributed by the squared polyad eigenvectors), Gaussian's anharmonic intensities only for non-resonant combination bands and overtones. Resonance
thresholds Δ = 200 cm⁻¹ and W = 10 cm⁻¹ in 2015; in 2016 W was set to zero (missed resonances were entering VPT2 as singularities) with a separate
symmetry subroutine. Gaussian's own VPT2 could not reproduce the C–H stretching region (no polyad intensity sharing). No frequency scaling anywhere.

Accuracy against experiment:

| paper | comparison | positions |
|---|---|---|
| 2015 | naphthalene, anthracene, full mid-IR vs matrix isolation, secondary C–H bumps excluded | average 5.6 cm⁻¹ (max 13), 9.9 cm⁻¹ (max 18) |
| 2015 | tetracene, mid-IR | average 6.4 cm⁻¹ (max 20) |
| 2015 | C–H stretch, jet-cooled gas, three molecules | average 19.3 / 10.5 / 11.7 cm⁻¹ (max 29.8 / 21.0 / 19.9) |
| 2016 | five non-linear PAHs vs matrix isolation | 0.41 % ± 0.63 % |
| 2016 | vs high-temperature gas phase | 0.53 % ± 0.95 % |
| 2016 | C–H stretch vs jet-cooled gas | −0.13 % ± 0.25 % |
| 2016 | harmonic for comparison | "typically over 4 %"; anharmonic "less than 1 %" |

Their reading of their own results (2016 §VI): anharmonic calculations are "the instrument of choice" in the absence of gas-phase data; triphenylene's QFF
was poor and its intensities wrong; all strong C–H-stretch bands are type-two Fermi resonances (C–C stretch + in-plane C–H bend with C–H stretch
fundamentals), all strong pure-combination bands are pairs of out-of-plane C–H bends; and the closing hope of both papers is **generalisation across the PAH
family without a full anharmonic analysis per molecule** ("patterns are beginning to arise … holds promise for generalizing anharmonic effects").

**For us.**

- **Line B's numbers, now from the source.** At 1000–1500 cm⁻¹, 0.41–0.53 % is 4–8 cm⁻¹ with a standard deviation of 6–14 cm⁻¹; in the mid-IR the
  per-molecule averages are 5.6–9.9 cm⁻¹. That is the accuracy the target pipeline has to match or beat *per family*, and it is the number the per-family
  tolerance should be set against (Frozen Ladder; reading copy §7 dated note of 19 September). The harmonic part of their pipeline is B971/T2ZP,
  unscaled; the anharmonic part is what closes the 4 % gap. Our correction acts on the harmonic part only (H = H₀ + ΔH) and inherits their anharmonic
  machinery downstream — so the honest comparison is "their harmonic part vs our corrected harmonic part, both through the same VPT2", not spectrum vs spectrum.
- **The pipeline (blad 8) needs the polyad treatment.** Mackie shows that VPT2 without polyad intensity sharing fails in the C–H stretching region.
  pyVPT2 on psi4 is our VPT2 step; whether it does polyads must be checked before the 3 µm column is anything but "shown, not promised" (decision 25
  stays). Action: one desk check of pyVPT2's resonance handling; if absent, the 3 µm column is out of scope for the first releases, and the pipeline
  sheet says "VPT2 with polyads (pyVPT2 or SPECTRO)".
- **Intensities.** Their rule — double-harmonic intensities redistributed across a polyad by the squared eigenvectors — is what our "Intensiteitsberekening"
  step should do; the dipole derivatives we now store in every corpus record are the input.
- **The motivation sentence for the proposal is theirs.** Both papers end by hoping for family-wide generalisation of anharmonic effects without a per-molecule
  QFF; the network of plan 05 is one answer to that hope, coming from the reader's own group. The cover note can say so in one line, with the quote.
- **Nothing here bears on the coupled-cluster correction itself:** their force fields are DFT throughout; naphthalene at CCSD(T)/cc-pVTZ QFF level is named
  in 2015 as "just barely feasible" and under study — that is the canonical benchmark our benzene/naphthalene labels will be compared with if it was published
  (to look up: Mackie et al. 2018, JPCA, naphthalene QFF at higher levels — not requested, not held).

## 5. Actions taken and to take

Taken tonight: PDFs filed; this note; papers table items 12, 67, 68, 69 marked read in full; the PI assessment's gate A prerequisite "three L1 papers read"
is met and its claim reworded per §2; ledger.

To take (desk, no compute): rewrite gate A's claim sentence in the PI assessment and the reading copy §1 prior-art paragraph (the Molpro fixed-domain
practice named as prior art, the transport of LNO spaces as the contribution); check pyVPT2's polyad handling; add Mackie's per-region numbers to the
opponents table of the Frozen Ladder with the source lines; one line in the cover note quoting the family-generalisation hope.

### Done the same evening, 21:0x — the four desk points

1. **Reading copy §1 and §3.1** rewritten (prior-art sentence, table row, reading (i)); change-log entry.
2. **pyVPT2 polyad check** (pyvpt2 0.1.2 in the `qc` environment, `vpt2.py` and `fermi_solver.py` read): **positions — yes.** It identifies type-1 (2ω_i ≈ ω_j) and type-2 (ω_i + ω_j ≈ ω_k) Fermi resonances with `FERMI_OMEGA_THRESH` 200 cm⁻¹ and a strength threshold `FERMI_K_THRESH` 1 cm⁻¹ (K = φ⁴/(64 Δ³) or φ⁴/(256 Δ³)), deperturbs the affected χ constants, chains the interactions into polyads, builds the effective Hamiltonian (off-diagonal φ/4 or φ/(2√2) by type) and diagonalises it — the same construction as SPECTRO's, with a K-based filter where SPECTRO 2015 used W = 10 and 2016 used W = 0 plus a symmetry filter; pyVPT2 has no symmetry filter. **Intensities — no:** pyVPT2 computes no anharmonic intensities at all (already noted in `probes/vpt2_benzene.py`, idea I6), and `Polyad.solve` returns the polyad frequencies without exposing the eigenvectors, which Mackie's redistribution rule needs. Consequence: the 3 µm column stays 'shown, not promised' (decision 25) until the intensity step exists; the pipeline's 'Intensiteitsberekening (eigen software)' needs the polyad eigenvectors — a ten-line own patch to `fermi_solver.py` (return the eigenvector matrix with the state enumeration), to be entered in the software-changes ledger when built, after 28 September.
3. **Mackie's numbers** into `Frozen_Lines_to_Beat.md` §3 as a dated line; verification debt 2 paid for Mackie 2015/2016 (Esposito 2024a–c open).
4. **Cover note**: the freezing sentence made honest (known recipe; the transport and its price are ours) and one line quoting the 2016 hope.
