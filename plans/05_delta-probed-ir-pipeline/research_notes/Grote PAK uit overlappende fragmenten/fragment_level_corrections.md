# Fragment-level corrections to DFT vibrational frequencies of large molecules (fragment ΔH / multi-level Hessians)

Scope: test of the claim "Building a large PAH's (34–60+ atoms) vibrational correction (high level minus low level) from
overlapping, corpus-size pieces (~10–30 atoms) has never been tried." Search done 11 November 2026 (web search, ~22 tool
calls). Several publisher pages (RSC, ouci, uohyd dspace) refused fetches, so a number of figures below come from abstracts
or search-engine extracts of abstracts; this is flagged where it applies. Context for the reader: our own test E9 rebuilt a
substituted aromatic's ΔH (ωB97X − B3LYP) from the parent core's block plus its own Hessian columns within two bonds of the
substituent: 1.72 cm⁻¹ rms frequency error (zero rule 23.1).

## Q1. ONIOM / multilayer / MIM / MTA-type Hessian corrections: does "full low-level + fragment high-minus-low" exist for frequencies, and with which errors?

### Takeaway
Yes, the general construction exists and is well established: the full molecule at a low level plus high-minus-low corrections
computed on fragments, assembled into a Hessian, has been published for frequencies in at least four families (ONIOM, MIM2/MIM3,
"grafted" MTA, N-body:many-body QM:QM). The reported errors against the unfragmented calculation are a few cm⁻¹ or less. But the
test systems are water clusters, peptides, carbohydrates and other saturated or hydrogen-bonded systems, not PAHs.

### Cited Findings
- ONIOM's two-layer extrapolation is E(High,Real) ≈ E(Low,Real) + [E(High,Model) − E(Low,Model)]. NWChem's documentation adds that it works when the model contains the interactions that dominate the difference. Derivatives, including Hessians, follow by differentiating this expression, and Gaussian prints ONIOM frequencies per layer — [NWChem ONIOM doc](https://grok.dragonflybsd.org/xref/dports/science/nwchem-data/nwchem-7.0.2-release/doc/user/oniom.tex?a=true); [Imperial ChemWiki: frequency calculations, high level vs ONIOM](https://chemwiki.ch.ic.ac.uk/wiki/Frequency_Calculations_on_a_Small_System_(high_level_vs._ONIOM))
- Molecules-in-Molecules (MIM; Jose & Raghavachari) extended to energy gradients and IR spectra (J. Chem. Theory Comput. 2015, 11, 950): the two-layer MIM2 improved IR frequencies and intensities by roughly 75% over one-layer MIM1. MIM2 means high-level fragments plus a low-level calculation of the full molecule that recovers the long-range interactions — [uohyd repository record, "Evaluation of energy gradients and infrared vibrational spectra through molecules-in-molecules fragment-based approach"](https://dspace.uohyd.ac.in/handle/1/13293)
- MIM for VCD (J. Chem. Theory Comput. 2015, 11, 4238): Hessians and polar and axial tensors are computed from independent fragment calculations, and link-atom contributions are projected back onto host atoms with an ONIOM-like Jacobian. Frequencies and VCD intensities were reproduced for 10 carbohydrate benchmarks against full calculations — [uohyd record](https://dspace.uohyd.ac.in/handle/1/13292). A 2016 extension covers ROA and VCD of polyalanine conformers — [uohyd record](https://dspace.uohyd.ac.in/handle/1/13291). A 2017 book-chapter review covers α-D-cyclodextrin and cryptophane-A — [uohyd record](https://dspace.uohyd.ac.in/items/d0cf98a7-a477-4e21-86cf-78f128bbe8fe)
- Molecular Tailoring Approach (MTA; Gadre group). Rahalkar, Ganesh & Gadre, J. Chem. Phys. 2008, "Enabling ab initio Hessian and frequency calculations of large molecules" (DOI 10.1063/1.2978387): a cardinality-guided MTA Hessian for extended molecules, with MP2 test calculations and "negligible loss of accuracy" claimed — [IAS repository](https://repository.ias.ac.in/86957); [zendy DOI page](https://zendy.io/pdf-viewer/10.1063/1.2978387)
- "Grafted" MTA (Sahu & Gadre, 2015, water clusters, MP2): a full calculation at a lower level or basis plus the fragment-assembled correction (higher minus lower) estimates the full higher-level property. This is the closest structural analogue to a "full low-level Hessian + fragment ΔH" scheme. For (H2O)16 the grafted MTA frequencies differed from the full MP2 calculation by at most 2 cm⁻¹ (abstract-level figure, via search extract) — [peeref record](https://peeref.com/zh/works/1090207); related energy grafting (6-31+G(d) correction grafted onto aug-cc-pVDZ/TZ, MP2), errors ≈ 0.2 mEh — [IAS repository](https://repository.ias.ac.in/10384)
- "Fragments-in-Fragments" MTA (Sahu & Gadre, J. Chem. Phys. 2016) for IR and Raman spectra of polypeptides: no full calculation at all, and the maximum difference is about 3 cm⁻¹ against the full calculation "for most cases" (abstract) — [peeref record](https://www.peeref.com/works/2510458); [BVB record](https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_proquest_journals_2121830601). MTA Hessians of nine (H2O)32 isomers at MP2/aug-cc-pVDZ (Mol. Phys. 2015, DOI 10.1080/00268976.2015.1062150) — [peeref](https://peeref.com/zh/works/11367648)
- Systematic Molecular Fragmentation (SMF/SMFA; Collins), J. Chem. Phys. 141, 094108 (2014): energies, gradients and Hessians by fragmentation with embedded charges, applied to geometries and vibrational frequencies of neutral molecules, zwitterions and ions. The SMFA package computes IR spectra with isotopic substitution — [ANU research portal](https://researchportalplus.anu.edu.au/en/publications/molecular-forces-geometries-and-frequencies-by-systematic-molecul/); [ANU full text PDF](https://openresearch-repository.anu.edu.au/bitstream/1885/16184/1/01_Collins_Molecular_forces%2c_geometries%2c_2014.pdf)
- A fragment quantum-chemical approach to geometry optimisation and vibrational spectra of proteins exists. The authors and numbers were not read in this session — [peeref record](https://www.peeref.com/works/3006156)
- A 2024 J. Chem. Theory Comput. paper is described in a search extract as a "stepping-stone" scheme: fragments at low and high level, with the difference added to the full low-level molecule. It notes that accuracy is limited by the high-level fragment calculations. The search tool attributes it to Collins and Raghavachari; I did not verify the authorship or the title — [par.nsf.gov listing](https://par.nsf.gov/servlets/purl/10510320)

### Inferences
- The algebra the claim relies on (H_big^high ≈ H_big^low + Σ_fragments ±[H_frag^high − H_frag^low], mapped back to parent atoms
  with link-atom Jacobians) is published and named: ONIOM Hessians, MIM2/MIM3, grafted MTA. A claim of novelty for the
  *construction itself* would be wrong. Novelty can only lie in (a) the system class (large PAHs, delocalised π), (b) the
  correction pair (CCSD(T)/double hybrid minus B3LYP on a fully covalent, fully conjugated framework), and (c) reusing pieces
  that are corpus molecules with their own closed-shell aromatic identity, rather than capped fragments cut ad hoc from the target.
- Our E9 rule (parent block + columns within two bonds) is functionally a distance-cutoff fragmentation, like MIM's bond-count
  fragments or MTA's R-goodness. The 1.72 cm⁻¹ sits in the same range as the 2–3 cm⁻¹ the fragmentation literature reports
  against the full calculation.

### Gaps
- No full text of the MIM IR paper was read, so the cm⁻¹ numbers for MIM2 and MIM3 frequencies (versus full) are not recorded
  here. Only the "~75% better than MIM1" figure was found.
- I could not open Gaussian's documentation on ONIOM frequency handling or any benchmark of ONIOM(CCSD(T):DFT) Hessians for an
  aromatic molecule.

## Q2. Fragment-based / local-correlation CCSD(T) and MP2 Hessians: MBE, GEBF, LNO, DLPNO, incremental

### Takeaway
High-level (CCSD(T)) fragment Hessians with an MP2 or DFT full-system background are shown to work within a few tenths to a few
cm⁻¹, but only for hydrogen-bonded clusters (MBE). Local-correlation CCSD(T) has gradients, including an automatic-differentiation
LNO-CCSD(T) route, but I found no LNO-CCSD(T) or DLPNO harmonic frequencies for large aromatic molecules.

### Cited Findings
- Howard & Tschumper, J. Chem. Phys. 139, 184113 (2013), "N-body:Many-body QM:QM vibrational frequencies". The 1- to N-body terms are CCSD(T) and all higher-order terms MP2, i.e. a full MP2 calculation plus a CCSD(T)−MP2 correction from fragments. On (H2O)n, n = 3–7, 2-body:many-body CCSD(T):MP2 harmonic frequencies differ from canonical CCSD(T) by at most a few cm⁻¹. With 3-body terms the maximum deviations are typically a few tenths of a cm⁻¹, at a fraction of the wall time — [BVB record (abstract)](https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_proquest_miscellaneous_1467065261); [Tschumper, Sanibel 2013 abstract](https://sanibelsymposium.qtp.ufl.edu/wp-content/uploads/sites/20//2013/Tschumper,%20Gregory.pdf); [Tschumper talk, St Andrews 2024](https://scotchem.wp.st-andrews.ac.uk/files/2024/05/tschumper_talk.pdf)
- Follow-up (Howard, Gray, Hardwick, Nguyen, Tschumper, J. Chem. Theory Comput. 2014): an augmented basis of at least quadruple-ζ quality is needed for MP2 and CCSD(T) harmonic frequencies of (H2O)2 and (HF)2 within 10 cm⁻¹ of the CBS limit (abstract via search extract) — [scholarsmine record](https://scholarsmine.mst.edu/chem_facwork/3871)
- LNO-CC gradients via automatic differentiation (PySCFAD; arXiv 2404.03129): LNO-CCSD(T) gradients, dipoles and Baker-set geometry optimisations benchmarked against canonical CCSD(T). The formal scaling is O(N⁵ + Ñ⁷), and the authors warn that loose LNO cut-offs cause PES discontinuities that slow optimisations. That warning matters directly for finite-difference Hessians — [arXiv 2404.03129](https://arxiv.org/html/2404.03129v3)
- The MRCC 2025 overview (Kállay group) describes analytic gradients with cost reduction for local methods and the aim of "accurate properties for large molecules". The extract did not show LNO-CCSD(T) Hessians or frequencies — [MRCC overview 2025, REAL repository](https://real.mtak.hu/224485/7/mester-et-al-2025-overview-of-developments-in-the-mrcc-program-system.pdf); local-correlation review (LNO-CCSD(T) for hundreds of atoms, reported more accurate and efficient than DLPNO-CCSD(T) on its measures) — [REAL repository](https://real.mtak.hu/205919/1/state-of-the-art-local-correlation-methods-enable-affordable-gold-standard-quantum-chemistry-for-up-to-hundreds-of-atoms.pdf)
- A whole-molecule (not fragment) Hessian difference correction: a 2023 benchmark of G4-like composites finds that a CCSD(T)−MP2 difference plus a larger-basis MP2 term gives the most accurate harmonic frequencies for benzene, RMSD ≈ 3 cm⁻¹ (search extract) — [arXiv 2308.06079](https://arxiv.org/pdf/2308.06079)

### Inferences
- MBE-type CCSD(T):MP2 Hessians converge quickly because the subsystems are weakly coupled monomers. A PAH has no such
  natural monomers. Every cut goes through a conjugated C–C bond, so the convergence evidence from water clusters does not
  transfer to it.
- If LNO-CCSD(T) Hessians become practical, they are the natural *validation counterpart* for a fragment-ΔH PAH result: a
  whole-molecule local-correlation Hessian on one 30–40-atom PAH.

### Gaps
- GEBF Hessians (Li Shuhua group) and the incremental scheme for frequencies were not reached in this session; no numbers.
- Analytic DLPNO-MP2 or PNO-based Hessians, and any frequency benchmark of them on aromatics, were not found.
- Hirata's embedded-fragment CCSD/MP2 phonons and Beran's HMBI vibrational work (molecular crystals) were not searched.

## Q3. Composite and hybrid schemes for large PAHs, and transfer from small to large PAHs

### Takeaway
For PAHs the established multi-level route mixes *levels by derivative order* (high-level harmonic, low-level cubic and quartic,
for the whole molecule), not *by region*. The only fragment ("Lego brick") transfer to PAHs that I found is for equilibrium
geometries and rotational constants, not force constants. Large-PAH experiments (coronene to HBC) show that harmonic B3LYP is
already good from 100 to 1000 cm⁻¹, while anharmonic VPT2 breaks down for large PAHs.

### Cited Findings
- Hybrid harmonic and anharmonic force field for cyano-PAHs: harmonic force constants from the double hybrid rev-DSDPBEP86 (MP2-type correlation), cubic and quartic constants from B3LYP. For 9-cyanoanthracene the CN band centre is 2207 cm⁻¹, matching experiment — [UvA repository, "Pinpointing the CN stretch frequency of neutral cyano PAHs" (PDF)](https://pure.uva.nl/ws/files/263562047/pinpointing-the-cn-stretch-frequency-of-neutral-cyano-polycyclic-aromatic-hydrocarbons-a-laboratory-and-quantum.pdf)
- Anharmonic PAH work (Leiden/Amsterdam groups) uses B3LYP/N07D quartic force fields with VPT2. B97-1/TZ2P was reported unstable for PAH quartic force fields (search extract) — [arXiv 1809.09868](https://arxiv.org/pdf/1809.09868); harmonic spectra compare poorly at 3.1–3.5 µm and 5–6 µm because they lack combination bands, overtones and resonances — [Mackie et al., PCCP 2018](https://pubs.rsc.org/en/content/articlepdf/2018/cp/c7cp06546a)
- Lemmens, Rijs & Buma, ApJ 923, 238 (2021), DOI 10.3847/1538-4357/ac2f9d: the first jet-cooled IR spectra (3–100 µm) of coronene C24H12, peropyrene C26H14, ovalene C32H14 and hexa-peri-benzocoronene C42H18. The harmonic prediction agrees well with experiment at 100–1000 cm⁻¹ but shows significant shortcomings at 1600–2000 cm⁻¹ (combination bands) and 2950–3150 cm⁻¹ (CH stretch). The anharmonic GVPT2 treatment that works for small PAHs gives "large and unrealistic" shifts for large PAHs in the CH out-of-plane region (667–1000 cm⁻¹), "a challenge for theory" — [UvA DARE record](https://dare.uva.nl/id/651db345-cc4a-45f2-bd19-71c5ac331a12); [BVB record](https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_proquest_journals_2614803563)
- For small PAHs (Lemmens et al., A&A 628, A130, 2019; naphthalene to pentacene, FELIX), VPT2 anharmonic frequencies agree with experiment within 0.5% on average — [arXiv 1907.09351](https://arxiv.org/pdf/1907.09351)
- "Lego brick" approach: Ye, Alessandrini, Melosso & Puzzarini, PCCP 24, 23254–23264 (2022), DOI 10.1039/D2CP03294E. Equilibrium structures of PAHs and PANHs are assembled from accurate (semi-experimental) fragment structures, with a template-molecule correction for embedding and linear regression for the linkages. Small PA(N)Hs reproduce experimental rotational constants within ~0.1%, and predictions are given for 13 uncharacterised species — [RSC landing page](https://pubs.rsc.org/en/content/articlelanding/2022/cp/d2cp03294e). Origin: Melli, Tonolo, Barone & Puzzarini, J. Phys. Chem. A 2021 — [SNS repository PDF](https://ricerca.sns.it/retrieve/fe3d5821-f41e-48ed-927f-34be686e050b/acs.jpca.1c07828.pdf). Extended to substituted benzenes (Spaniol et al., PCCP 2023, 25, 6397) — [RSC](https://pubs.rsc.org/en/content/articlepdf/2023/cp/d2cp04825f)
- Puzzarini & Stanton (PCCP 2023) note that for larger systems, locality-exploiting alternatives to brute force such as the Lego-brick approach "are likely to prove useful" (search extract) — [RSC](https://pubs.rsc.org/en/content/articlehtml/2023/cp/d2cp04706c). A 2024 Barone PCCP review describes double-hybrid harmonic and hybrid anharmonic composites and notes that suitable fragments are not always available (search extract; I did not confirm which article the extract came from) — [RSC](https://pubs.rsc.org/en/content/articlepdf/2024/cp/d3cp05169b)
- The CosmicPAH-IRDB web application (de Bentzmann, Joblin, Demyk, Mulas et al., arXiv 2609.01696, 1 September 2026) handles temperature and anharmonic effects in PAH spectra *empirically*, from collected experimental and theoretical spectra. The abstract does not describe a fragment or transfer scheme — [arXiv 2609.01696](https://arxiv.org/abs/2609.01696)

### Inferences
- In PAH spectroscopy the "hybrid" (Barone/Bloino-type) force field is a split by derivative order over the *whole* molecule, and
  "Lego brick" is a fragment transfer of *geometries*. I found nothing that transfers a high-minus-low *Hessian* (harmonic force
  constant) correction from small PAHs or pieces onto a large PAH. This is the narrow space in which the claim can survive.
- The Lemmens 2021 result means the payoff for a large PAH's harmonic ΔH lies mainly above 1000 cm⁻¹ (CC stretch, CH in-plane,
  CH stretch) and in the input to anharmonic treatments. The 100–1000 cm⁻¹ harmonic region is already good at B3LYP.

### Gaps
- I did not reach a paper that transfers anharmonic constants (χ_ij) from small to large PAHs, if one exists (Mackie/Candian
  "cascade" work was seen only via abstracts).
- No paper was found with a CCSD(T) or double-hybrid harmonic force field of coronene or larger to serve as a reference; no
  numbers.

## Q4. SQM / scale-factor transfer from small reference molecules to large PAHs, and reported errors

### Takeaway
Transfer of *corrections* from small molecules to PAHs has a long history, but as scale factors, not as Hessian blocks. Uniform
scaling of B3LYP gives about 10 cm⁻¹ average error against matrix fundamentals up to ovalene (C32H14). Pulay-type SQM factors
per coordinate type give under 8.5 cm⁻¹ on organic training sets.

### Cited Findings
- Langhoff, J. Phys. Chem. 100(8), 2819–2841 (1996): DFT harmonic frequencies and intensities of 13 PAH neutrals and cations up to ovalene. Uniformly scaled frequencies agree with matrix-isolation fundamentals within an average error of about 10 cm⁻¹; the scaling mainly absorbs anharmonicity — [NASA NTRS](https://ntrs.nasa.gov/citations/20020040898); [Unibo index entry](https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/15053115). The widely used factor 0.958 is cited to this line of work (search extract; I did not confirm its basis set) — [arXiv 0802.1071, IR spectra of very large compact PAHs](https://arxiv.org/pdf/0802.1071)
- Bauschlicher & Langhoff (1997, naphthalene): with large basis sets, accurate DFT frequencies need two factors (CH stretch versus the rest). At B3LYP/4-31G one factor suffices (search extract) — [Unibo index, "The calculation of accurate harmonic frequencies of large molecules: the PAHs, a case study"](https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/8054175)
- Mode-dependent PAH factors with 6-311G** against matrix data: 0.974 (CH oop), 0.972 (CH in-plane and CC stretch), 0.965 (CH stretch) (search extract) — [arXiv 1407.2010](https://arxiv.org/pdf/1407.2010)
- Rauhut & Pulay, J. Phys. Chem. 1995, DOI 10.1021/j100010a019, "Transferable scaling factors for density functional derived vibrational force fields": BLYP and B3LYP/6-31G* force fields for 31 organic molecules, scaled with 11 coordinate-type factors — [CiNii](https://cir.nii.ac.jp/crid/1362825893384188672); [Stuttgart record](https://puma.ub.uni-stuttgart.de/bibtex/479425b47dc4213589b86390144f65ab). Baker, Jarzecki & Pulay scaled primitive valence force constants (30-molecule training set) and reached average frequency errors under 8.5 cm⁻¹ at B3LYP/6-31G* — [SDU record](https://opact.sdu.edu.tr/vufind/SummonRecord/FETCH-LOGICAL-a361t-17ed34c164e42647afdf23e522ea1aa14cd67ecf3e933521eaadba52a7d0b13a3)
- Modern scaled-harmonic benchmark (Zapata Trujillo & McKemmish, arXiv 2302.04448, 2023): over 600 model chemistries. The best median error is ≈ 7.6 cm⁻¹ (DSD-PBEP86/def2-TZVPD), "close to the error of the harmonic approximation". Hybrids with double-ζ bases reach 11–12 cm⁻¹ — [arXiv 2302.04448](https://arxiv.org/abs/2302.04448)

### Inferences
- SQM is the historical precedent for "learn a correction on small molecules, apply it to large PAHs". It is a low-dimensional
  correction (one to a dozen factors on internal-coordinate diagonal and off-diagonal blocks). A fragment-ΔH scheme transfers the
  full local correction matrix, couplings included, which SQM cannot represent. The scale-factor floor of ~7–12 cm⁻¹ is the
  baseline any fragment-ΔH approach should beat. (Per the project's own rules, a scale factor is only ever the baseline, never an
  option.)

### Gaps
- Whether Rauhut & Pulay's 31-molecule set contained PAHs was not confirmed.

## Q5. Applications to 30–60+ atom PAHs (coronene, ovalene, circumcoronene, HBC); errors and reported pitfalls

### Takeaway
I found no fragment-based or multi-level (region-split) *Hessian* calculation on coronene, ovalene, circumcoronene or HBC. The
closest evidence on conjugated systems is energy and gradient fragmentation in DFT: it works in 1D (< 1 mEh) but carries
millihartree errors in 2D π systems, which is the key pitfall.

### Cited Findings
- Nagata, Fedorov, Sawada, Kitaura & Gordon, J. Chem. Phys. 2010, "On the applicability of fragmentation methods to conjugated π systems within density functional framework" (MTA in DFT): for 1D conjugated molecules the energy error against the full calculation is < 1 mEh. For **2D** π-conjugated systems the energy errors are a few mEh, while gradients agree "reasonably well", enough for MTA geometry optimisation. The authors suggest extension to large 2D and 3D π systems (abstract) — [OUCI record](https://ouci.dntb.gov.ua/works/4KJQLwp7)
- In conjugated polymers, fragment-based excitonic couplings reproduce full TDDFT only for weakly coupled systems; strongly coupled ones need higher fragment states (2017) — [INIS record](https://inis.iaea.org/records/9rmbs-sp307)
- Large-PAH harmonic and anharmonic status up to C42H18 (HBC): see Q3 (Lemmens, Rijs & Buma 2021). Harmonic is good at 100–1000 cm⁻¹; VPT2 fails for large PAHs in the CH oop region — [UvA DARE](https://dare.uva.nl/id/651db345-cc4a-45f2-bd19-71c5ac331a12)
- The Lego-brick PAH geometries (Ye et al. 2022) are the only fragment-assembly applied to PAHs that I found, and they target structures, not Hessians — [RSC](https://pubs.rsc.org/en/content/articlelanding/2022/cp/d2cp03294e)

### Inferences
- Pitfalls to expect for a PAH fragment ΔH, from the cited evidence and first principles:
  (i) delocalisation: the 2D π-system energy errors (Nagata 2010) mean every fragment boundary cuts a delocalised bond, and
  long-range couplings in ΔH (e.g. ring-breathing modes coupled across the whole sheet) are what fragments miss;
  (ii) capping and aromaticity: an H-capped piece of a PAH is itself a different aromatic molecule (Clar sextets move), so
  high-minus-low differences on it may not equal the embedded difference. Lego brick needed a template-molecule embedding
  correction even for geometries;
  (iii) low-level background: MIM2's ~75% gain over MIM1 shows that the full-molecule low-level layer carries the long-range part.
  In a ΔH scheme the low level (B3LYP) is that layer, so only the *difference* has to be local. The localness of ΔH (not of H)
  is the property to test, and E9 (1.72 cm⁻¹) is evidence for it on a substituted aromatic.
- On the evidence found, the claim survives only in narrowed form. What I did not find is a vibrational *correction*
  (high minus low Hessian) of a 34–60+ atom PAH built from overlapping aromatic pieces of ~10–30 atoms. What is published is
  the general fragment-ΔH and ONIOM-Hessian method (MIM2/3, grafted MTA, N-body:many-body CCSD(T):MP2), on clusters, peptides
  and carbohydrates, within 2–3 cm⁻¹ of the full calculation. The safe wording is "not found for PAHs or delocalised π systems
  in a targeted search", not "never tried".

### Gaps
- No search was made for fragment Hessians of graphene nanoflakes or nanoribbons, or for periodic graphene phonons corrected by
  cluster CCSD(T). These are adjacent areas where a precedent could exist.
- Full texts of the MIM and MTA frequency papers were not read, so I cannot exclude that one of them includes a small aromatic
  test case.
- I did not search Google Scholar's "cited by" lists of the Lego-brick PAH paper and the Nagata 2010 paper. That would be the
  cheapest way to close the remaining risk that someone has done PAH Hessians by fragments.
