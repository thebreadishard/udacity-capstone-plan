# ML trained on small molecules or fragments, applied to large molecules (Hessians, frequencies, IR), with emphasis on PAHs

Scope: test the claim "Building a large PAH's (34–60+ atoms) ML-predicted vibrational correction from overlapping,
corpus-size pieces (~10–30 atoms) has never been tried." Our own reference point (from the assignment, not from a
source): a transformer predicting the per-normal-mode correction B3LYP/6-31G* → ωB97X, trained on molecules up to
~30 atoms, takes the frequency rms error on coronene, peropyrene, ovalene and hexabenzocoronene (36–60 atoms) from
22.8 to 7.9 cm⁻¹; that error is 4.4× its error on corpus-size molecules. Train:test size ratio ≈ 1:1.2 to 1:2.

Searches ran on 11 November 2026 (web search plus full-text reads of the AMONs, Laurens et al., Domenichini & Dellago,
Tang et al. and HIP texts). Where only an abstract or a search snippet was available, that is said.

## The claim: closest prior art and verdict

### Takeaway
I found no paper that builds a large molecule's ML-predicted vibrational *correction* (or Hessian) by explicitly
assembling it from overlapping, corpus-size molecular pieces. The closest prior art falls into four groups, none of
which does exactly this: (1) local MLIPs and Hessian models, which build a molecule's Hessian from atom-centred
environments within a cutoff of ~4–6 Å, so the "pieces" are implicit and much smaller than 10–30 atoms; (2) training on
overlapping fragments but evaluating the whole system (GEMS, energies and forces of proteins); (3) query-specific
fragment training sets (AMONs: energies, forces, charges, NMR, polarisabilities, no frequencies); (4) non-ML
fragmentation of Hessians (MTA/MIM, partial-Hessian analysis). The claim holds only in its narrow form. Stated broadly
("predicting large-molecule vibrations from small-piece training has never been tried") it is false.

### Cited Findings
- The one PAH study with a small-train/large-test split for frequencies: Behler–Parrinello ANN (n2p2) trained on 11
  PAHs up to coronene (C24H12, 36 atoms), tested on 6 others including ovalene (C32H14, 46 atoms), all at B3LYP/N07D.
  Harmonic-frequency RMSD vs DFT: 18.3 cm⁻¹ on the training molecules and 22.1 cm⁻¹ on the test molecules (30-node
  network); 19.8 cm⁻¹ RMSD / 15 cm⁻¹ MAE over all. Worst were ovalene, pentacene and triphenylene, "large structures
  [...] not included in the training database" — [Laurens, Rabary, Lam, Peláez, Allouche, Theor. Chem. Acc. 2021,
  DOI 10.1007/s00214-021-02773-6; arXiv:2010.13686](https://arxiv.org/abs/2010.13686)
- Inconsistency in that paper: the abstract says "8 large PAHs" outside the training set; the methods list six
  validation molecules (benzoperylene, benzopyrene, ovalene, pentacene, tetracene, triphenylene); the conclusions say
  "19 PAH molecules" were compared — [arXiv:2010.13686](https://arxiv.org/abs/2010.13686)
- GEMS trains on fragments that "can be overlapping pieces, or even just be structurally related to the original
  system"; the fragments are not used when the force field is evaluated. Top-down fragments are spherical cut-outs
  around an atom with dangling bonds saturated; bottom-up fragments are chemical graphs of 1–8 non-hydrogen atoms.
  Applied to crambin (46 residues) in water, >25k atoms — [Unke et al., Sci. Adv. 10, eadn4397 (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11809612/); [arXiv:2205.08306](https://arxiv.org/abs/2205.08306v1)
- HIP predicts the Hessian directly, as symmetrised 3×3 atom-pair blocks built from l ≤ 2 equivariant pair features
  within the interaction cutoff (H = H′ + H′ᵀ). The large molecule's Hessian is thereby assembled from local pair blocks —
  [Burger et al., arXiv:2509.21624 (2025, rev. 2026)](https://arxiv.org/html/2509.21624v2); journal version
  [Nature Computational Science 2026, DOI 10.1038/s43588-026-01066-x](https://www.nature.com/articles/s43588-026-01066-x)
- I found no source reporting an ML-predicted ωB97X (or any higher-level) minus B3LYP *per-mode* correction for PAHs
  larger than the training set, apart from our own result. (Negative search result; see Gaps.)

### Inferences
- The defensible novelty is the combination: (a) a Δ-correction on top of B3LYP, not a full MLIP; (b) per normal mode
  of the whole molecule; (c) built from explicit, overlapping molecular pieces of corpus size (10–30 atoms, i.e.
  several rings, far larger than an MLIP cutoff sphere); (d) on PAHs of 34–60+ atoms. Each part alone has precedent.
- Reviewers will point to local equivariant Hessian models (HIP and similar) as "already assembling from local pieces".
  The answer is the size of the piece (a whole multi-ring fragment with its delocalised modes vs a ~5 Å sphere) and the
  target (a correction to a computed spectrum, not the spectrum itself).
- Our test:training error ratio of 4.4× is much larger than Laurens et al.'s 22.1/18.3 ≈ 1.2×. But their test molecules
  were barely larger than training (46 vs 36 atoms; coronene was in training), and their absolute error against their
  own level of theory (~20 cm⁻¹) is larger than our 7.9 cm⁻¹ against ωB97X. The two numbers measure different things
  (full B3LYP frequencies from an MLIP vs a correction to B3LYP), so they do not compare directly.

### Gaps
- I could not rule out work published only in non-indexed theses or recent conference proceedings (NeurIPS/ICML
  workshops) on fragment-assembled Δ-Hessians.
- No source gives a Δ(ωB97X − B3LYP) frequency benchmark for coronene, ovalene or HBC from any ML model.

## AMONs (Huang & von Lilienfeld, Nature Chemistry 2020)

### Takeaway
AMONs build a query-specific training set from small fragments (amons, mostly ≤ 7 heavy atoms) of the target. They
were demonstrated for energies, forces, atomic charges, NMR shifts, core-level shifts and polarisabilities, not for
Hessians or vibrational frequencies. They had no PAH test. The closest delocalisation test (polyacetylene) shows the
error growing with query length unless the amons grow too.

### Cited Findings
- Properties demonstrated: "energies, forces, atomic charges NMR shifts, polarizabilities"; systems from organic
  molecules, 2D materials and water clusters to Watson–Crick base pairs and ubiquitin — [Huang & von Lilienfeld,
  Nat. Chem. 12, 945 (2020), DOI 10.1038/s41557-020-0527-z; arXiv:1707.04146](https://arxiv.org/abs/1707.04146v5)
- About 11,000 QM9 query molecules (9 heavy atoms) reach 2 kcal/mol with fewer than ~50 selected training amons; for a
  typical QM9 molecule chemical accuracy needs "only tens of small training instances (no more than 7 atoms)" vs
  thousands of molecules with random selection — [arXiv:1707.04146v4 full text](https://arxiv.org/pdf/1707.04146v4)
- Force components were predicted for furanylpropanol (9 heavy atoms); "prediction geometry and training amons had to
  be distorted" for forces. Learning curves reach or beat hybrid-DFT accuracy after ~30 amons of ≤ 7 heavy atoms —
  [arXiv:1707.04146v4](https://arxiv.org/pdf/1707.04146v4)
- Scale-up: chignolin (77 heavy atoms) and ubiquitin (602 heavy atoms); atomization-energy error falls below
  10 kcal/mol; unrelaxed amons were needed because of strong intramolecular non-covalent interactions; ubiquitin had no
  force reference — [arXiv:1707.04146v4](https://arxiv.org/pdf/1707.04146v4)
- Delocalisation test (SI Fig. S12): error grows with polyacetylene length. Amons of ≤ 3 acetylene units (6 heavy
  atoms) stay below 1 kcal/mol up to 14 C; 4 or 5 units reach chemical accuracy up to 28 or >30 C. Periodic amons were
  used for h-BN sheets — [arXiv:1707.04146v4](https://arxiv.org/pdf/1707.04146v4)
- Watson–Crick pairs needed amons of up to 11 heavy atoms "as they extend over larger spatial domains" and through
  "non-local effects through their conjugated moieties" — [arXiv:1707.04146v4](https://arxiv.org/pdf/1707.04146v4)
- Stated limitation: "challenging non-local quantum effects, such as in highly electron correlated situations
  (Peierls/Jahn-Teller distortions, metal-insulator transitions)" — [arXiv:1707.04146v4](https://arxiv.org/pdf/1707.04146v4)
- A derived data set, "Dictionary of 140k GDB and ZINC derived AMONs" (Materials Cloud), lists harmonic frequencies,
  force constants, IR intensities and normal coordinates among its properties. It is a data set; I found no model built
  on it for frequencies (seen in a search-result description only) — [b2find record](https://b2find.eudat.eu/dataset/cef7a41e-4ee2-5263-9d18-6da3e1a64313)

### Inferences
- AMONs are the conceptual ancestor of "train on the pieces of the target", but for scalar and atomic properties with
  kernel ridge regression. They never did a mode-resolved quantity. A normal mode of a large PAH is not a sum of
  per-atom terms, which is the hard step our fragment approach must solve.
- The polyacetylene result is the closest analogue to our size penalty. Error grows with conjugation length at fixed
  fragment size and shrinks as the fragments grow, which argues for the largest affordable pieces (our 10–30 atoms) over
  AMON-sized ones (≤ 7 heavy atoms).
- Size ratio: fragments ≤ 7 heavy atoms → targets up to 602 heavy atoms (~86×) for energies, with errors of
  ≤ 10 kcal/mol at that end, not chemical accuracy.

### Gaps
- No AMONs work on aromatic or PAH vibrational properties found. Later AMON papers (e.g. on other properties) were not
  searched exhaustively.

## MLIPs trained on fragments or small molecules and applied to large systems; PAH or graphene frequencies

### Takeaway
Fragment- and small-molecule-trained MLIPs routinely run on large systems (GEMS proteins, PAHs up to 216 C). But the
only large-PAH frequency validation against DFT I found (Laurens et al.) used test molecules only ~1.3× the largest
training size, with ~22 cm⁻¹ RMSD. The 216-C PAH spectra of Mai et al. have no DFT check beyond 32 C. I found no
benchmark of MACE-OFF, ANI or AIMNet frequencies on large PAHs or graphene flakes.

### Cited Findings
- Laurens et al.: trained on 8,863 energies and 735,447 forces of 11 PAHs from displaced geometries (up to ±0.5 Å),
  B3LYP/N07D; ANN CPU time three orders of magnitude below DFT. Anharmonic (GVPT2) fundamentals: RMSD 19.8 cm⁻¹
  (30 nodes), but coronene and ovalene were excluded because their DFT VPT2 failed — [arXiv:2010.13686](https://arxiv.org/abs/2010.13686)
- Mai et al. (MLMD): NeuralIL force field (spherical Bessel descriptors, 3.8 Å cutoff) plus a message-passing dipole
  model; trained on 17,175 configurations of 687 neutral PAHs from PAHdb v3.2 at B3LYP/4-31G; applied to 1,704 PAHs up
  to 216 C; cost ∝ N_C^0.7 vs ∝ N_C^4 for DFT. Validation: 49 PAHs (10–50 C) against experiment, DFT anharmonic only for
  26 PAHs (≤ 32 C); accuracy given as intensity RMSE, not frequency error in cm⁻¹. The authors note the model "may
  exhibit increased uncertainty" for molecules unlike the training set — [Mai, Wang, Pan, Schörghuber, Kovács, Carrete,
  Madsen, arXiv:2503.05120 (2025); MNRAS, DOI 10.1093/mnras/staf1156](https://arxiv.org/html/2503.05120v2)
- MACE-OFF: trained on ωB97M-D3(BJ)/def2-TZVPPD energies and forces; IR spectra via a MACE dipole model; no PAH-flake
  benchmark found — [Kovács D.P. et al., arXiv:2312.15211](https://arxiv.org/html/2312.15211v3)
- Zero-shot study of GNN potentials: both MACE-OFF models reproduce high- and low-frequency modes for rMD17 molecules
  (which include naphthalene); GO-MACE-23 loses accuracy for high-frequency modes (search snippet) —
  [arXiv:2502.21317](https://arxiv.org/pdf/2502.21317)
- GEMS (above): mixing small bottom-up fragments (short-range baseline) with larger top-down fragments (long-range
  effects) — [Unke et al., Sci. Adv. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11809612/)
- A transferable potential for linear alkanes trained on C14H30 and tested on C4H10–C30H62 (title only, seen in search) —
  [PMC11983714](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11983714/)

### Inferences
- GEMS's two-tier fragment recipe (small graphs plus larger overlapping cut-outs) is the closest *training-set* analogue
  to our corpus of overlapping pieces. GEMS aims at MD of proteins, not at vibrational corrections.
- Mai et al.'s 3.8 Å cutoff MLIP on PAHs to 216 C is the clearest case of "train on PAHdb-size, apply far beyond" for
  PAH IR. It has no reported frequency error for the large ones, so it gives no evidence on size extrapolation.

### Gaps
- No published cm⁻¹ errors found for any MLIP on coronene, ovalene, HBC or graphene flakes against a DFT Hessian of the
  same molecule (apart from Laurens et al.'s ovalene, which is reported only in a per-molecule figure).
- SpookyNet, AIMNet2, NequIP/Allegro: not searched individually for PAH frequencies (budget). I found none in the
  general searches.

## ML for PAH IR spectra (PAHdb) and size extrapolation

### Takeaway
PAHdb-trained spectrum predictors (fingerprint/GNN, 2020–2026) degrade beyond the training size. Tang et al. 2026
(train ≤ 47 C, test 50–100 C) report rising errors for N_C > 40, blamed on scarce large-PAH data, topology-only inputs,
and the collective low-frequency modes with "long-range couplings". These works predict binned spectra, not per-mode
frequencies, and report no cm⁻¹ peak errors.

### Cited Findings
- Tang, He, Wang, Qiu (2026): 1,570 neutral PAHs (≤ 47 C, PAHdb v3.2) for training/validation; 997 neutral PAHs with
  50–100 C (PAHdb v4.0α) as a large-PAH test. AttentiveFP shows "increasing errors in both spectral regions" for
  N_C > 40; an MLP on ECFP shows "a more gradual error increase". Mean JSD 0.097 (low-frequency) and 0.029 (high) at
  18.23 cm⁻¹ bins. Stated causes: limited large-PAH data; SMILES-only inputs; low-frequency modes "involve collective
  motions" and "long-range couplings"; the models "should not be applied to astronomical PAHs outside the training
  domain" — [arXiv:2602.12560](https://arxiv.org/html/2602.12560)
- Kovács, Zhu, Carrete, Madsen, Wang (2020): NN on Morgan fingerprints of skeletal formulas, trained on PAHdb; applicability
  limited by "the limited diversity of the training data"; errors estimated with an NN ensemble — [ApJ 902, 100 (2020),
  DOI 10.3847/1538-4357/abb5b6](https://iopscience.iop.org/article/10.3847/1538-4357/abb5b6); [arXiv:2010.09150](https://arxiv.org/abs/2010.09150v1)
- Charge-aware NN (Guangxi group, A&A 2026): 12,599 species in four charge states; handles PAHs up to 150 C; accuracy at
  130–150 C improves notably even with limited data (abstract/search snippet; full text returned HTTP 403) —
  [A&A 2026, DOI 10.1051/0004-6361/202659248](https://www.aanda.org/articles/aa/abs/2026/04/aa59248-26/aa59248-26.html)
- Mai, Lu, Wang (Oct 2026): ML double-harmonic framework (NN force field plus dipole model), 144,111 spectra of 48,037
  benzenoid PAHs in three charge states, with per-spectrum uncertainty; "small to medium-sized PAHs"; no cm⁻¹ errors
  in the abstract — [arXiv:2610.21205](https://arxiv.org/abs/2610.21205)
- ML fragments responsible for PAH emission features: ECFP-fragment interpretation of PAHdb spectra at B3LYP/6-31G with
  scale factor 0.961 (search snippet) — [arXiv:2307.08277](https://arxiv.org/pdf/2307.08277)
- "Ethereal AI" preprint: ML scaling factors per frequency from computed frequency, intensity, reduced mass and force
  constant; MAE / max error 5 / 13 cm⁻¹ vs 10 / 23 cm⁻¹ for a single scale factor (ResearchGate snippet only; authors,
  data set and any size test unverified) — [ResearchGate 398558241](https://www.researchgate.net/publication/398558241_Ethereal_AI_Infrared_Spectra_of_Polycyclic_Aromatic_Hydrocarbons_with_Machine_Learning_DFT_Scaling_Factors)

### Inferences
- The "Ethereal AI" per-frequency scaling is the closest PAH work to a per-mode correction. It is a per-mode feature
  model, not a fragment assembly, and the reference appears to be experiment/scaled DFT, not ωB97X. Worth reading in
  full before claiming novelty of per-mode PAH corrections.
- The astro-PAH ML literature's consensus failure mode (error rising past the training size, worst in the collective
  low-frequency region) is the same pattern as our 4.4× penalty. Their remedy so far is more large-PAH training data,
  not fragment assembly.

### Gaps
- No PAHdb-ML paper reports per-mode frequency errors (cm⁻¹) vs size; all use spectral distances (JSD, intensity RMSE).
- Full text of the A&A 2026 charge-aware paper and the "Ethereal AI" preprint not read (403 / ResearchGate only).

## Δ-learning of frequencies/Hessians and ML Hessian prediction: size extrapolation

### Takeaway
Δ-ML for vibrational frequencies is almost always molecule-specific (a PES correction for one molecule, e.g. ethanol to
CCSD(T)). Transferable Hessian learning (HORM, Hessian QM9, HIP, random-forest internal-coordinate Hessians) is trained
and tested on QM7/QM9/Transition1x-size molecules (≤ ~30 atoms). Size-extrapolation tests are either tiny
(QM7 → 8–9 heavy atoms) or asserted without published per-size error tables I could verify.

### Cited Findings
- Δ-ML ethanol: a correction PES fitted to DFT–CCSD(T) differences reproduces CCSD(T) harmonic frequencies; one molecule
  only — [Nandi, Qu, Bowman et al., JCTC 20, 8807 (2024), DOI 10.1021/acs.jctc.4c00977](https://pubs.acs.org/doi/10.1021/acs.jctc.4c00977); see also [arXiv:2011.11601](https://arxiv.org/pdf/2011.11601)
- NN + VPT2 with transfer learning: anharmonic frequencies within 20 cm⁻¹ of experiment for ~90 % of modes on the best
  surface vs ~60 % for MP2 surfaces; per-molecule surfaces (search snippet) — [Käser, Meuwly et al., arXiv:2103.05491](https://arxiv.org/pdf/2103.05491)
- (Author names for the two entries above are from memory, not read from the pages; check before citing.)
- Hessian QM9: 41,645 QM9 molecules at ωB97x/6-31G* in implicit solvents; an MLIP trained on energies and forces only had
  ~42 cm⁻¹ MAE (400–4000 cm⁻¹), 9.49 cm⁻¹ with Hessians in the loss; tests stay within QM9 (search snippet) —
  [Williams et al., Sci. Data 2025; arXiv:2408.08006](https://arxiv.org/pdf/2408.08006)
- HORM: ~1.84 M Hessians at ωB97x/6-31G(d) on Transition1x/RGD1 geometries; Hessian-informed training cuts Hessian MAE by
  up to 63 % — [Cui et al., Sci. Data (2025), DOI 10.1038/s41597-025-06350-5; arXiv:2505.12447](https://arxiv.org/html/2505.12447v1)
- HIP: Hessian MAE 0.030 eV/Å² (HIP-EquiformerV2) on HORM; "2x lower Hessian MAE, 3.5x lower eigenvalue MAE" vs
  autodiff baselines; experiments on "small organic molecules", speed tests on 5–30 atoms —
  [arXiv:2509.21624v2](https://arxiv.org/html/2509.21624v2). A search snippet of the Nature Computational Science version
  says HIP errors "remain relatively flat across system sizes, including for molecules larger than those in the training
  set". I could not find that test in the arXiv text I read (first 100k of 144k characters); treat as unverified —
  [Nat. Comput. Sci. 2026](https://www.nature.com/articles/s43588-026-01066-x)
- Hi-MLIP (2026): Hessian-informed training needing two to four orders of magnitude fewer Hessian labels; evaluated on
  HORM (search snippet) — [Yin et al., arXiv:2603.25373](https://arxiv.org/html/2603.25373)
- NewtonNet analytical Hessians for TS search; notes that common chemical data sets lack Hessians — [Nat. Commun. 2024,
  s41467-024-52481-5](https://www.nature.com/articles/s41467-024-52481-5)
- NequIP-based Hessians for neutron vibrational spectra, claimed transferable "over a wide range of molecules" (abstract
  snippet) — [arXiv:2502.13070](https://arxiv.org/pdf/2502.13070)
- An ML model for nuclear Hessians predicted atom pair by atom pair, ~180× speed-up "with only minor deviations in the
  vibrational spectra" (search snippet; full text 403) — [ChemRxiv 2026, 10.26434/chemrxiv.10001864](https://chemrxiv.org/doi/pdf/10.26434/chemrxiv.10001864)

### Inferences
- No transferable Δ-frequency model (lower → higher DFT level, per mode) tested for size extrapolation turned up. The
  transferable Hessian models predict the Hessian of one level of theory, not a correction between two.
- The training-size ceiling of the Hessian data sets (QM9 ≤ 9 heavy atoms; T1x ≤ 7 heavy atoms) means every published
  "larger molecule" test of a learned Hessian is near that range. Our 36–60-atom PAH test is outside all of them.

### Gaps
- Exact per-size error data for HIP's larger-molecule test (if it exists) not verified.
- No study found that learns a Hessian *difference* between two DFT functionals across molecules.

## Locality-based Hessian ML: is it effectively the fragment idea?

### Takeaway
Yes in spirit, no in form. Local models predict each atom-pair Hessian block (or internal-coordinate force constant)
from a local environment, so a large molecule's Hessian is assembled from pieces by construction. The published
results show the expected failure: stretches transfer well (< 5–10 cm⁻¹), but low-frequency, delocalised modes are
poorly predicted "because such vibrations are strongly non-local".

### Cited Findings
- Domenichini & Dellago: random forest learns individual second derivatives in redundant internal coordinates (diagonal
  plus selected adjacent couplings) from local descriptors; trained on QM7, tested on 13 QM9 molecules of 8–9 heavy
  atoms, "bigger than any molecule in the training set"; "given the locality of our representation, it is possible to
  predict the Hessian matrix for molecules of any given size" — [J. Chem. Phys. 159, 194111 (2023), DOI 10.1063/5.0169384;
  arXiv:2307.16512](https://arxiv.org/pdf/2307.16512)
- In the same paper, C–H stretches within 5 cm⁻¹ and C≡N / C=O stretches within 10 cm⁻¹ of B3LYP/cc-pVDZ for the example
  molecule; low-frequency modes worse because angle/dihedral terms are harder and "such vibrations are strongly
  non-local, and involve larger parts of the molecule"; ZPE always underestimated, by 1.3–14.5 % over the 13 molecules —
  [arXiv:2307.16512](https://arxiv.org/pdf/2307.16512)
- HIP builds 3×3 pair blocks only for atom pairs within the message-passing cutoff and justifies the sparsity by the
  locality of electron interactions; its limitations section does not discuss long-range couplings —
  [arXiv:2509.21624v2](https://arxiv.org/html/2509.21624v2)
- Non-ML precedent for assembling Hessians from fragments: the molecular tailoring approach (MTA) and molecules-in-molecules
  (MIM) give VCD frequencies and intensities of large molecules close to full calculations (authors not confirmed in my
  search) — [ResearchGate 282926832](https://www.researchgate.net/publication/282926832_Vibrational_Circular_Dichroism_Spectra_for_Large_Molecules_through_Molecules-in-Molecules_Fragment-Based_Approach);
  partial-Hessian vibrational analysis diagonalises fragment sub-blocks —
  [ResearchGate 225488552](https://www.researchgate.net/publication/225488552_Partial_Hessian_vibrational_analysis_The_localization_of_the_molecular_vibrational_energy_and_entropy)

### Inferences
- Atom-pair-block models are the "fragment idea" at the smallest scale: each piece is one atom pair plus a ~5 Å
  environment. Our approach differs by using whole overlapping molecules of 10–30 atoms as pieces. Each piece then
  contains complete ring systems and their collective modes, and its correction is computed for real normal modes, not
  learned per block. This is the distinction to state against HIP-type prior art.
- MTA/MIM show that overlapping-fragment Hessian assembly works for *computed* Hessians. Applying the same assembly to an
  *ML-predicted correction* is the untested step.

### Gaps
- No locality-based Hessian model has been tested on PAHs larger than the training set with per-mode cm⁻¹ errors.
- GEBF and Cartesian-coordinate tensor transfer (Bouř-type) for Hessians: my searches did not reach them; worth a
  targeted check, since tensor transfer from fragments to large molecules is long-standing non-ML prior art.

## Reported pitfalls: delocalised modes, long-range π-conjugation, out-of-distribution interior carbons

### Takeaway
Three failure modes recur: (1) collective, low-frequency, delocalised modes predicted badly by local models; (2) error
growing with conjugation length when fragments or cutoffs are fixed (AMONs polyacetylene); (3) missing training
coverage for large and interior-rich PAH environments, giving errors that rise above the training size (Tang et al.
N_C > 40; Laurens et al. worst on ovalene, pentacene, triphenylene).

### Cited Findings
- Low-frequency modes "involve collective motions" and "long-range couplings" (PAH GNN) — [Tang et al. 2026](https://arxiv.org/html/2602.12560)
- Low-frequency Hessian terms "strongly non-local" and "not easy to predict [...] using just a local representation" —
  [Domenichini & Dellago 2023](https://arxiv.org/pdf/2307.16512)
- Error grows with polyacetylene length; larger amons lower the offset — [Huang & von Lilienfeld 2020](https://arxiv.org/pdf/1707.04146v4)
- Conjugated moieties produce "strong non-local effects" requiring amons of up to 11 heavy atoms for base pairs —
  [Huang & von Lilienfeld 2020](https://arxiv.org/pdf/1707.04146v4)
- Highest test RMSDs on the largest unseen PAHs (ovalene, pentacene, triphenylene); DFT VPT2 itself failed for coronene
  and ovalene — [Laurens et al. 2021](https://arxiv.org/abs/2010.13686)
- Increased uncertainty for molecules unlike the training set (PAH MLMD) — [Mai et al. 2025](https://arxiv.org/html/2503.05120v2)
- Topology-only inputs (no 3D) "may fundamentally limit their ability to generalize" — [Tang et al. 2026](https://arxiv.org/html/2602.12560)

### Inferences
- For 36–60-atom PAHs, the interior (fully fused, no-H) carbon environments are rare or absent in ≤ 30-atom training
  molecules (coronene has six; pyrene two). This fits the reported "OOD interior" penalty and the size-dependent error.
  Overlapping corpus-size pieces that contain such interior carbons (e.g. coronene-like cores) are the logical remedy.
  This is our hypothesis, not a published result.
- Delocalised whole-molecule modes of a large PAH (low-frequency out-of-plane, ring-breathing) have no counterpart in
  any single piece. A fragment-assembled correction will need a rule for modes that span pieces; the literature has no
  solution to copy.

### Gaps
- No source quantifies the error contribution of interior carbons vs edge carbons for ML frequency predictions of PAHs.
- No source found on how far π-conjugation effects on force constants extend in PAHs in terms an ML cutoff could use
  (e.g. decay of Hessian off-diagonal blocks with distance in coronene/ovalene).
