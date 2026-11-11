# Closest prior art: assembling a large PAH's vibrational correction / Hessian from overlapping PAH fragments

Researched 11 November 2026 (web; Crossref, OpenAlex, Europe PMC, Semantic Scholar APIs). Full-text status for each
paper is marked **[FULL TEXT]**, **[ABSTRACT ONLY]** or **[METADATA ONLY]**. The Barone-group papers from 2026 are all
closed access (OpenAlex `oa_status: closed`, Europe PMC `isOpenAccess: N`), and no arXiv or ChemRxiv preprint turned up,
so the key Barone claims below rest on abstracts only. The publisher pages (AIP, ACS, RSC) returned only the abstract or
HTTP 403, and PMC/PubMed returned a browser-check or cookie wall.

Our idea, for reference: a large PAH (34–60+ atoms: coronene, peropyrene, ovalene, HBC) gets its vibrational correction
(high-level minus B3LYP Hessian, a per-mode frequency correction, or an ML-predicted correction) assembled from
overlapping PAH pieces of ~10–30 atoms from the corpus, and benchmarked against the full calculation.

## Q1. Barone group, J. Chem. Phys. 2026, article 064104: topology-dependent local corrections (PAHs)

### Takeaway
The paper is **Crisci, Lazzari, Uribe, Barone, "Topology-dependent refinement of molecular structures and vibrational
properties", J. Chem. Phys. 165, 064104 (2026), DOI 10.1063/5.0343929**. It is volume **165**, not 164. It corrects
double-hybrid DFT structures and vibrational properties with transferable local terms keyed to bond topology, and it is
tested on PAHs among other sets. The abstract gives errors only for rotational constants (%). It gives no cm⁻¹ figures and
names no PAHs or sizes. Nothing in the abstract says that a large PAH's force field is built from fragment calculations
and benchmarked against the full molecule. **[ABSTRACT ONLY]**

### Cited Findings
- Bibliographic record: Crisci L., Lazzari F., Uribe L., Barone V.; J. Chem. Phys. 165(6), 064104; published 2026-08-10;
  DOI 10.1063/5.0343929; PMID 42573035; no PMCID; closed access — [Crossref query](https://api.crossref.org/works?query.bibliographic=Barone+Mendolicchio+polycyclic+aromatic+hydrocarbons+local+corrections+conjugation&filter=container-title:The+Journal+of+Chemical+Physics,from-pub-date:2025-06-01); [OpenAlex](https://api.openalex.org/works/doi:10.1063/5.0343929); [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTH:%22Barone%20V%22%20AND%20(PUB_YEAR:2026)%20AND%20(vibrational%20OR%20topology%20OR%20fragmentation%20OR%20aromatic)&format=json&resultType=core)
- Method, as the abstract describes it:
  - The scheme is a local refinement of **double-hybrid DFT** results. The correction depends on molecular topology and is
    applied "in the representation where it is most compact".
  - A **transferable core-valence layer**, obtained empirically or from MP2, is kept separate from the valence correction
    and can be applied from level 0 on.
  - **Level 1** adds a **bond-field term that includes conjugation** and a **pair-local term** for selected atom-pair
    classes.
  - **Vibrational residuals are represented "in normal-mode or fragment space"**.
  - Sources: [AIP landing page (abstract only)](https://pubs.aip.org/aip/jcp/article/165/6/064104/3359000); [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTH:%22Barone%20V%22%20AND%20(PUB_YEAR:2026)%20AND%20(vibrational%20OR%20topology%20OR%20fragmentation%20OR%20aromatic)&format=json&resultType=core)
- Test sets: polycyclic aromatic hydrocarbons, intramolecular OH⋯O systems, carbohydrates and a nucleoside. The abstract
  names no individual PAH and gives no sizes — [AIP landing page](https://pubs.aip.org/aip/jcp/article/165/6/064104/3359000)
- Numbers in the abstract:
  - Rotational-constant errors "near 1%" at the hybrid-functional level fall by more than an order of magnitude for rigid
    covalent molecules.
  - Pair-local refinement brings hydrogen-bonded carbohydrates below 0.3%.
  - No vibrational cm⁻¹ error appears in the abstract.
  - Sources: [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTH:%22Barone%20V%22%20AND%20(PUB_YEAR:2026)%20AND%20(vibrational%20OR%20topology%20OR%20fragmentation%20OR%20aromatic)&format=json&resultType=core); [AIP](https://pubs.aip.org/aip/jcp/article/165/6/064104/3359000)
- The authors' conclusion: residual errors are better treated as structured, low-dimensional corrections than as uniform
  empirical offsets (that is, scale factors) — [OpenAlex abstract](https://api.openalex.org/works/doi:10.1063/5.0343929)
- The Crossref reference list has 52 entries, deposited without titles. Among them are the group's own templating-synthon
  JCP 2025 paper (10.1063/5.0255564), JCTC 2025 21, 10617 (10.1021/acs.jctc.5c01188) and JPCL 2026 17, 5012
  (10.1021/acs.jpclett.6c00413). I found no Raghavachari/MIM or Gadre/MTA DOI in the list, but most entries could not be
  identified from DOI alone — [Crossref record](https://api.crossref.org/works/10.1063/5.0343929)
- Open-access copy: none found (OpenAlex `oa_url` null; Europe PMC full text "Subscription required") — [OpenAlex](https://api.openalex.org/works/doi:10.1063/5.0343929)

### Inferences
- The corrected quantity is the residual of **double-hybrid DFT** (B2PLYP-type), not B3LYP, against a higher reference.
  That reference is presumably the Pisa composite scheme (PCS) or semi-experimental data for structures. For vibrations it
  is not stated in the abstract.
- "Fragment space" for vibrational residuals is the closest wording to our idea anywhere in the literature I found.
  However, the corrections appear to be **parametrised per topology class** (bond-type and conjugation terms, transferable
  across molecules). They do not appear to be **assembled from explicit high-level calculations on overlapping
  fragments** of the target PAH. That makes this a transferable-parameter model, closer to a learned local correction than
  to a fragment-assembly scheme with a full-molecule benchmark.
- The abstract has no cm⁻¹ errors, no PAH sizes and no large-PAH full-calculation benchmark. **Pending the full text**, it
  does not show that coronene-to-HBC-size PAHs were handled.

### Gaps
- Not available without the full text, which is paywalled with no preprint:
  - which PAHs were used and how large the largest is;
  - the vibrational reference level (PCS, CCSD(T), VPT2 fundamentals versus experiment?);
  - whether harmonic frequencies or anharmonic fundamentals are corrected;
  - the cm⁻¹ errors;
  - whether corrections are fitted on small PAHs and transferred to larger ones;
  - what "fragment space" means operationally.
  The full text has to be obtained, through a library or by writing to the authors, before we can claim novelty against
  this paper.

## Q2. Barone group, J. Chem. Theory Comput. 2026, page 7326: multilevel fragmentation for VPT2

### Takeaway
The paper is **Barone, Crisci, Mendolicchio, "Multilevel Fragmentation and Boundary Corrections for Accurate Vibrational
Spectra of Large Molecules", J. Chem. Theory Comput. 22(14), 7326–7343 (2026), DOI 10.1021/acs.jctc.6c00816**. It splits
a 30–50-atom molecule into chemically meaningful subunits, each treated at a different level for the VPT2 force field,
and adds a local harmonic correction at the "electronically delicate" boundary bonds. It is tested on benzonitrile,
tryptophan and uridine. The abstract names **no PAH**. **[ABSTRACT ONLY]**

### Cited Findings
- Bibliographic record: Barone V., Crisci L., Mendolicchio M.; JCTC 22(14), 7326–7343; published 2026-07-07; DOI
  10.1021/acs.jctc.6c00816; PMID 42412036; closed access — [Crossref](https://api.crossref.org/works?query=Barone+multilevel+fragmentation+VPT2+benzonitrile+tryptophan+uridine&filter=from-pub-date:2025-01-01&rows=10&select=DOI,title,author,container-title,volume,article-number,page,published); [OpenAlex](https://api.openalex.org/works/doi:10.1021/acs.jctc.6c00816)
- Method, as the abstract describes it:
  - A multilevel fragmentation strategy for VPT2-quality vibrational analysis of molecules in the **30–50 atom range**.
  - The molecule is partitioned into chemically meaningful subunits, and a **local harmonic correction** is added for
    electronically delicate boundary bonds.
  - The abstract distinguishes cases where one fragment dominates the spectrum from cases where two fragments contribute
    equally.
  - Benzonitrile is described accurately with the nitrile group at high level and the ring at low level.
  - Sources: [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTH:%22Barone%20V%22%20AND%20(PUB_YEAR:2026)%20AND%20(vibrational%20OR%20topology%20OR%20fragmentation%20OR%20aromatic)&format=json&resultType=core); [OpenAlex](https://api.openalex.org/works/doi:10.1021/acs.jctc.6c00816)
- The abstract claims VPT2-quality results at lower cost and gives no cm⁻¹ figure — [OpenAlex](https://api.openalex.org/works/doi:10.1021/acs.jctc.6c00816)
- Open-access copy: none found — [OpenAlex](https://api.openalex.org/works/doi:10.1021/acs.jctc.6c00816)
- Companion paper: **Barone, Crisci, Lazzari, "Integrating Local and Normal Modes for Multilevel Vibrational
  Spectroscopy", J. Phys. Chem. Lett. 17(37), 10555–10561 (2026), DOI 10.1021/acs.jpclett.6c02504.**
  - A low-cost calculation supplies the full coupled force field, and higher-level energies refine selected curvatures in
    symmetry-adapted internal coordinates or along normal-mode directions, without a higher-level Hessian.
  - Local-coordinate models recover unsupplied coupling correlations of 0.987–0.999 on four "validation fixtures".
  - At most 2N higher-level curvatures are needed for N normal modes.
  - Closed access, abstract only.
  - Sources: [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1039/d2cp03294e%22%20OR%20DOI:%2210.1063/5.0313437%22%20OR%20DOI:%2210.1021/acs.jpclett.6c02504%22&format=json&resultType=core)

### Inferences
- The method is a **multilevel ONIOM-like partition inside one molecule**: a high level on the chromophore, a low level on
  the rest, and a boundary-bond patch. It is not an assembly of a large molecule's correction from overlapping
  **corpus-transferable** fragments, and it is not applied to fused PAHs according to the abstract. Its targets are
  functional-group spectra in biomolecules.
- The JPCL companion attacks the same cost problem from another side: a few high-level curvatures on top of a low-level
  Hessian. This is a direct competitor to a "Δ-Hessian" strategy for one molecule. It is not a cross-molecule transfer
  scheme.

### Gaps
- Not available without the full text:
  - the size of the boundary correction;
  - the cm⁻¹ errors against the full VPT2 calculation;
  - the high and low levels;
  - whether any polycyclic system appears in the SI.

## Q3. Earlier related work: Lego brick / templating for structures, and any extension to vibrations

### Takeaway
The Puzzarini "Lego brick" approach and Barone's "templating synthon / Nano-LEGO" approach correct **equilibrium
structures** (bond lengths and angles) of PAHs and PANHs with fragment templates. They are benchmarked on rotational
constants (≤0.1%). None of the abstracts I checked extends the fragment templates to **force constants or frequencies**.
Barone's vibrational work on PAHs uses Pisa composite structures plus a full GVPT2 force field computed for the whole
molecule. **[ABSTRACT ONLY]** for all of them, apart from the partial OA PDF noted below.

### Cited Findings
- **Ye H., Alessandrini S., Melosso M., Puzzarini C., "Exploiting the 'Lego brick' approach to predict accurate molecular
  structures of PAHs and PANHs", PCCP 24(38), 23254–23264 (2022), DOI 10.1039/d2cp03294e.**
  - A molecule is treated as fragments with accurate semi-experimental equilibrium structures. A template-molecule step
    accounts for the change when a fragment is joined, and linear regression corrects the linkages.
  - Rotational constants of small PA(N)Hs are within 0.1%. The approach is extended to systems without spectroscopic data.
  - Hybrid OA; PDF: https://pubs.rsc.org/en/content/articlepdf/2022/cp/d2cp03294e. The RSC HTML returned 403 to me, so I
    did not read it.
  - Sources: [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1039/d2cp03294e%22%20OR%20DOI:%2210.1063/5.0313437%22%20OR%20DOI:%2210.1021/acs.jpclett.6c02504%22&format=json&resultType=core); [OpenAlex](https://api.openalex.org/works/doi:10.1039/D2CP03294E?select=id,doi,title,publication_year,cited_by_count,authorships,open_access)
- **Alessandrini, Savarese, Melosso, Bizzocchi, Puzzarini, "Assessing the Limits of the 'Lego-Brick' Approach: Equilibrium
  Structures of Strained and Flexible Cyclic Molecules", J. Phys. Chem. A 130(17), 3403–3415 (2026), DOI
  10.1021/acs.jpca.6c00650.**
  - Structures only, on 3- to 5-membered rings; linear-regression corrections are essential.
  - **OA, PMC13137258.**
  - Source: [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:40548656%20OR%20DOI:%2210.1063/5.0255564%22%20OR%20DOI:%2210.1021/acs.jpca.6c00650%22%20OR%20DOI:%2210.1021/acs.jctc.4c00900%22&format=json&resultType=core)
- **Di Grande S., Lazzari F., Barone V., "Accurate Geometries of Large Molecules at DFT Cost by Semiexperimental and Coupled
  Cluster Templating Fragments", JCTC 20(20), 9243–9258 (2024), DOI 10.1021/acs.jctc.4c00900.**
  - PCS2 accuracy is about 1 mÅ and 2 mrad.
  - Building blocks of **up to about 20 atoms** cut B3LYP geometry errors by nearly an order of magnitude at no extra cost.
  - Structures only; closed access.
  - Source: [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:40548656%20OR%20DOI:%2210.1063/5.0255564%22%20OR%20DOI:%2210.1021/acs.jpca.6c00650%22%20OR%20DOI:%2210.1021/acs.jctc.4c00900%22&format=json&resultType=core)
- **Lazzari F., Di Grande S., Crisci L., Mendolicchio M., Barone V., "Molecular structures with spectroscopic accuracy at
  DFT cost by the templating synthon approach and the PCS141 database", J. Chem. Phys. 162, 114310 (2025), DOI
  10.1063/5.0255564.**
  - Templating synthons refine the bond lengths and angles of hybrid/double-ζ DFT structures; there is a web tool.
  - Structures only; closed access.
  - Source: [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:40548656%20OR%20DOI:%2210.1063/5.0255564%22%20OR%20DOI:%2210.1021/acs.jpca.6c00650%22%20OR%20DOI:%2210.1021/acs.jctc.4c00900%22&format=json&resultType=core)
- **Barone et al. 2023, J. Phys. Chem. A, "Toward Spectroscopic Accuracy for the Structures of Large Molecules at DFT Cost:
  Refinement and Extension of the Nano-LEGO Approach".**
  - Structures; author copy on the SNS repository:
    https://ricerca.sns.it/retrieve/41d8f0ae-57e3-47ab-af6e-dc888003cd9d/barone-et-al-2023-toward-spectroscopic-accuracy-for-the-structures-of-large-molecules-at-dft-cost-refinement-and.pdf
  - Seen in search results only; not read.
  - Source: [web search hit](https://ricerca.sns.it/retrieve/41d8f0ae-57e3-47ab-af6e-dc888003cd9d/barone-et-al-2023-toward-spectroscopic-accuracy-for-the-structures-of-large-molecules-at-dft-cost-refinement-and.pdf)
- **Barone V., Crisci L., Di Grande S., Lazzari F., Mendolicchio M., Uribe L., "Mechanical and electrical anharmonicity in
  the infrared spectra of graphene fragments: From planar polycyclic aromatic hydrocarbons to buckybowls", J. Chem. Phys.
  164, 114309 (2026), DOI 10.1063/5.0313437.**
  - Pisa composite structures plus full GVPT2 with mechanical and electrical anharmonicity, on **indene, azulene,
    corannulene and sumanene** (C9–C21).
  - Fundamentals typically **5–10 cm⁻¹** from experiment.
  - The abstract mentions no fragment assembly; closed access.
  - Source: [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1039/d2cp03294e%22%20OR%20DOI:%2210.1063/5.0313437%22%20OR%20DOI:%2210.1021/acs.jpclett.6c02504%22&format=json&resultType=core)
- Of the 34 works citing Ye 2022 (OpenAlex), none is evidently a fragment or template treatment of vibrational force
  fields:
  - Two are IR or ro-vibrational studies of small molecules: formamide–water (JPCA 2026) and H2COD+ (PCCP 2026).
  - The others are structure or rotational-spectroscopy papers.
  - The check was on titles only.
  - Source: [OpenAlex citing list](https://api.openalex.org/works?filter=cites:W4293752094&per-page=50&select=doi,title,publication_year,primary_location&sort=publication_year:desc)

### Inferences
- The Pisa/Bologna line is moving from **fragment templates for structures** (2022–2025) to **topology-dependent
  corrections for structures and vibrations** (JCP 165, 064104, 2026) and **multilevel fragment VPT2** (JCTC 2026). This
  group is the most likely to publish our idea, or a close version of it, next. Until the 064104 full text is read, our
  claim should be scoped as follows: explicit fragment assembly of the Δ-Hessian with a full-molecule benchmark at 34–60+
  atoms, on fused PAHs.
- Their largest vibrationally treated PAH in the abstracts I found is C21 (sumanene; corannulene is C20). That is below our
  target sizes.

### Gaps
- Whether the 2023 Nano-LEGO or 2024 templating papers include a vibrational section. The abstracts say no; the full texts
  were not read.

## Q4. "Ethereal AI" preprint: machine-learning scaling factors for PAH IR spectra

### Takeaway
This is now a published paper: **Bos, King, Calangian, Davin, McCraley, Putnam, Manjarrés, Stoneburner, "Ethereal AI:
Infrared Spectra of Polycyclic Aromatic Hydrocarbons with Machine Learning DFT Scaling Factors", ACS Omega 10(50),
62282–62290 (2025), DOI 10.1021/acsomega.5c10225** (Point Loma Nazarene University). A linear SVR predicts a per-band
corrected frequency for B3LYP/4-31G against PAHdb experimental bands: test MAE **5.07 cm⁻¹** versus 10.41 for the PAHdb
scaling. The split is random over bands of 80+ small-biased PAHs. There is **no size-extrapolation test and no fragments**.
**[FULL TEXT]**, via the Europe PMC XML; the first ~70% was read and the SI was not.

### Cited Findings
- Publication: ACS Omega 10(50), 62282–62290; received 30 September 2025, published 10 December 2025; PMCID PMC12750190;
  PMID 41476469 — [Europe PMC full text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750190/fullTextXML); ResearchGate entry [398558241](https://www.researchgate.net/publication/398558241_Ethereal_AI_Infrared_Spectra_of_Polycyclic_Aromatic_Hydrocarbons_with_Machine_Learning_DFT_Scaling_Factors)
- DFT level and reference data: B3LYP/4-31G in Gaussian 16. The reference bands are experimental, from the NASA Ames PAHdb
  — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750190/fullTextXML)
- Data and model:
  - "over 80 PAHs", 465 matched pairs of computed band and experimental band.
  - The authors say the experimental data "are biased toward small PAHs".
  - Molecule names and sizes are in the SI, which was not read.
  - Inputs: computed frequency, intensity, relative intensity, reduced mass and force constant.
  - Nine regressors were compared and **linear SVR** was chosen.
  - Output: the corrected frequency per band.
  - Source: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750190/fullTextXML)
- Split: a random 80/20 split (372/93 bands) "from all molecules". **No train-small/test-large experiment** — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750190/fullTextXML)
- Test-set errors (cm⁻¹) — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750190/fullTextXML):

  | Method | RMSE | MAE | Max | Share > 10 cm⁻¹ |
  |---|---|---|---|---|
  | SVR | 6.10 | 5.07 | 13.17 | 8.6% |
  | PAHdb scaling (three factors) | 12.41 | 10.41 | 23.49 | 52.7% |
  | NIST single factor 0.962 | 9.56 | 6.40 | 29.92 | 18.3% |

  By band region, the MAE above 2500 cm⁻¹ is 7.53 (SVR) against 10.26 (PAHdb). In 1111–2500 cm⁻¹ it is 4.31 (SVR)
  against 14.66 (PAHdb) and 3.23 (NIST).
- Scope as the authors state it: no claim beyond PAHs, and no test on large PAHs or fragments — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750190/fullTextXML)
- OA copies: PMC12750190 (https://pmc.ncbi.nlm.nih.gov/articles/PMC12750190/) and the publisher page
  https://pubs.acs.org/doi/10.1021/acsomega.5c10225 (ACS Omega is an OA journal) — [web search result](https://pubs.acs.org/doi/10.1021/acsomega.5c10225)

### Inferences
- This is a **per-band ML correction to experiment**, not a Hessian or Δ-Hessian, and not assembled from fragments. It is
  the nearest "ML replaces the scale factor" competitor. It has a weaker basis (4-31G), a small data set (465 bands), and
  random splits that leak molecules between training and test. It does not address size transfer at all.

### Gaps
- PAH names and the largest molecule (SI not read).
- Whether matrix-isolation shifts were treated.

## Q5. 2025 MTA-VCD paper (Gadre / Sahu) with an oxo-helicene

### Takeaway
The paper is **Sharma S., Khire S. S., Gadre S. R., Sahu N., "Assisting calculation of vibrational circular dichroism
spectra by molecular tailoring approach", J. Chem. Phys. 162(24), 244103 (2025), DOI 10.1063/5.0271469**. It fragments the
Hessian and the atomic polar and axial tensors with MTA, and corrects the fragmentation error with a smaller-basis full
calculation ("grafting"). The test systems are sugars, polypeptides and proteins. The abstract compares an oxo-helicene
VCD with experiment (CDCl3) **without saying whether MTA was used for the helicene**. **[ABSTRACT ONLY]**

### Cited Findings
- Bibliographic record and method: JCP 162, 244103 (published 2025-06-23); PMID 40548656; closed access. The method is
  MTA applied to VCD for the first time, with a grafting correction from a smaller basis set. Tests use several functionals
  and basis sets on sugars, polypeptides and proteins; peak positions and intensities "agree well" with full calculations.
  The oxo-helicene gas- and solvent-phase spectra match the CDCl3 experiment — [OpenAlex](https://api.openalex.org/works/doi:10.1063/5.0271469); [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:40548656%20OR%20DOI:%2210.1063/5.0255564%22%20OR%20DOI:%2210.1021/acs.jpca.6c00650%22%20OR%20DOI:%2210.1021/acs.jctc.4c00900%22&format=json&resultType=core)
- The abstract gives no fragment sizes and no numerical errors — [OpenAlex](https://api.openalex.org/works/doi:10.1063/5.0271469)
- Earlier MTA Hessian work:
  - **Rahalkar, Ganesh, Gadre, "Enabling ab initio Hessian and frequency calculations of large molecules", J. Chem. Phys.
    129, 234101 (2008), DOI 10.1063/1.3054300.** Cardinality-guided MTA (CG-MTA) Hessians and frequencies at HF, DFT and
    some MP2 — [IAS repository](https://repository.ias.ac.in/86957)
  - Ganesh, Dongare, Balanarayan, Gadre 2006: energies, gradients and Hessians by the cardinality-guided scheme — [IAS repository](https://repository.ias.ac.in/10384)
  - **Sahu, Khire, Gadre 2023 (J. Chem. Phys. 159)**: MTA geometry optimisation and IR of ten proteins up to 407 atoms;
    about 5 cm⁻¹ against the full calculation. This is from an aggregator summary, not verified at the primary source — [biomed.reviewer.ly](https://biomed.reviewer.ly/app/publication/dba55501-15c7-42e6-8a38-60870761b649)
  - The MTASpec software (Comput. Phys. Commun. 2022) computes IR and Raman spectra of large molecules — [OUCI record](https://ouci.dntb.gov.ua/works/45GRyj29)

### Inferences
- MTA is the strongest **generic** precedent for "a Hessian of a large molecule assembled from overlapping fragments,
  benchmarked against the full calculation". It works at **one level of theory**: fragment Hessians reproduce the parent's
  Hessian at the same level, with a grafting correction. It does not transfer a **high-minus-low correction** from a
  **corpus of other molecules**, and the published tests are biomolecules, not fused PAHs. If the helicene was done by MTA,
  it would be the one fused-aromatic case, but the abstract does not establish this.

### Gaps
- Whether the oxo-helicene was fragmented, the fragment sizes and the cm⁻¹ errors (full text closed).
- I found no Gadre/MTA study on a large PAH (coronene and up).

## Q6. Papers citing AroBOROS (JCTC 2020), AROFRAG (JCTC 2024) and Ye 2022: any vibrational or Hessian application?

### Takeaway
I found none. In the Semantic Scholar citation lists, no paper citing AroBOROS (11 citers listed) or AROFRAG (8 citers)
mentions frequencies, Hessians, IR, normal modes or anharmonicity in its title or abstract. The Ye 2022 citers (34,
OpenAlex) are structure or rotational-spectroscopy papers. **[METADATA/ABSTRACT ONLY]**

### Cited Findings
- AroBOROS: "Aromatic Fragmentation Based on a Ring Overlap Scheme: An Algorithm for Large Polycyclic Aromatic Hydrocarbons
  Using the Molecules-in-Molecules Fragmentation-Based Method", JCTC, DOI 10.1021/acs.jctc.9b00566. The title was found
  through the Crossref SI record; the author list was not verified here — [Crossref](https://api.crossref.org/works?query.bibliographic=AroBOROS+aromatic+fragmentation&rows=5&select=DOI,title,author,container-title,volume,page,published)
- AROFRAG: Masoumifeshani E., Korona T., "AROFRAG–A Systematic Approach for Fragmentation of Aromatic Molecules", JCTC 20,
  1078–1095 (2024), DOI 10.1021/acs.jctc.3c00875. Follow-up on interaction energies: JCC 45, 2446–2464 (2024), DOI
  10.1002/jcc.27429 — [Crossref](https://api.crossref.org/works?query.bibliographic=AROFRAG+automated+fragmentation+polycyclic+aromatic&rows=5&select=DOI,title,author,container-title,volume,page,published)
- AroBOROS citers: Semantic Scholar lists 11. Examples are graphene-QD NIR chromophores (JCC 2026), BN defects (pssb 2025),
  ZZPolyCalc, a PAH review (PCCP 2021) and cluster many-body expansions. **None is vibrational** — [Semantic Scholar](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1021/acs.jctc.9b00566/citations?fields=title,year,venue,externalIds,abstract&limit=100)
- AROFRAG citers: Semantic Scholar lists 8. Examples are "Fusing generative AI and ML-FFs for … fused-ring aromatic
  hydrocarbons" (Cell Rep. Phys. Sci. 2026), a unit-based chemical space of π-hydrocarbons (JCIM 2026) and COMPAS-3
  (PCCP 2024). **None is vibrational** — [Semantic Scholar](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1021/acs.jctc.3c00875/citations?fields=title,year,venue,externalIds,abstract&limit=100)
- Ye 2022 citers: see Q3 — [OpenAlex](https://api.openalex.org/works?filter=cites:W4293752094&per-page=50&select=doi,title,publication_year,primary_location&sort=publication_year:desc)
- Non-PAH fragment-vibration work seen in passing (titles only):
  - MIM energy gradients and IR spectra (University of Hyderabad record) — [dspace.uohyd](https://dspace.uohyd.ac.in/handle/1/13293)
  - "Multi-Molecular Fragment Interception" harmonic frequencies of pharmaceuticals — [PMC10304189](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10304189/)
  - Multilevel vibrational potentials (Hellmers, Czember, König, PCCP 2024) — [RSC](https://pubs.rsc.org/en/content/articlehtml/2024/cp/d4cp02916j)

### Inferences
- The PAH-specific fragmentation schemes (AroBOROS/MIM, AROFRAG) have been used for **energies** (thermochemistry,
  interaction energies), not for Hessians or frequencies, as far as the citation lists show. A ring-overlap PAH
  fragmentation applied to a **Δ-Hessian** appears unpublished.

### Gaps
- Semantic Scholar citation coverage is incomplete; AroBOROS likely has more citers in Google Scholar, which I did not
  query.
- The abstracts of "possible" Ye 2022 citers were not all read.

---

### Open-access PDF list (for later download; nothing downloaded)

| Paper | Legal OA copy |
|---|---|
| Crisci et al., JCP 165, 064104 (2026) | none found (closed) |
| Barone et al., JCTC 22, 7326 (2026) | none found (closed) |
| Barone et al., JPCL 17, 10555 (2026) | none found (closed) |
| Barone et al., JCP 164, 114309 (2026) | none found (closed) |
| Lazzari et al., JCP 162, 114310 (2025) | none found (closed) |
| Di Grande et al., JCTC 20, 9243 (2024) | none found (closed) |
| Barone et al., JPCA 2023 (Nano-LEGO) | author copy on the SNS repository: https://ricerca.sns.it/retrieve/41d8f0ae-57e3-47ab-af6e-dc888003cd9d/barone-et-al-2023-toward-spectroscopic-accuracy-for-the-structures-of-large-molecules-at-dft-cost-refinement-and.pdf |
| Ye et al., PCCP 24, 23254 (2022) | https://pubs.rsc.org/en/content/articlepdf/2022/cp/d2cp03294e (hybrid OA) |
| Alessandrini et al., JPCA 130, 3403 (2026) | PMC13137258 |
| Bos et al., ACS Omega 10, 62282 (2025) | https://pmc.ncbi.nlm.nih.gov/articles/PMC12750190/ ; Europe PMC XML: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750190/fullTextXML |
| Sharma et al., JCP 162, 244103 (2025) | none found (closed) |
| Rahalkar et al., JCP 129, 234101 (2008) | IAS repository record https://repository.ias.ac.in/86957 (PDF availability not checked) |
| AROFRAG, JCTC 20, 1078 (2024) | not checked |
| AroBOROS, JCTC 10.1021/acs.jctc.9b00566 | not checked |
