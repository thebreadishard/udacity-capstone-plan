# Relevant scientific papers — Plan 05

**Rule.** Do not cite from recall in a scored document. Every identifier below is re-fetched
before it enters a Module 03–09 reference list. Statuses: **OK (date; how)** = landing page,
Crossref record, arXiv abstract or full text fetched on that date, with *how* stated;
**record (plan-02/03/04)** = identifier carried from an earlier bibliography, re-verify at first
scored use; **record (search 2026-09-03)** = seen only in web-search result snippets on that
date — *not* a cite; **NOT FETCHED** = named debt. A Crossref record verifies title, authors and
venue; it does **not** verify any number quoted from the paper — numbers are marked
separately below where they are used.

Items 1–22 are plan 04's bibliography, carried with their statuses; items 23 onward are new
to plan 05 (from [Research_Note_2026-09-03_Delta_Probing.md](notes/Research_Note_2026-09-03_Delta_Probing.md)).
Statuses of items 25–28, 30, 34, 36–38, 41 were upgraded on 2026-09-03 after Round-7 Pass A
issue 8 by fetching Crossref records and arXiv abstracts; items 42–47 were added the same day
after Round-7 Pass B (issues 2, 4, 7, 8, 9) and verified via Crossref/arXiv.

| # | Use in plan 05 | Working identifier | Verify |
|---|---|---|---|
| 1 | **Line A** — PAHdb computed library v4.00 | Ricca, Boersma, Maragkoudakis, Roser, Shannon, Allamandola, Bauschlicher, ApJS **282**, 7 (2026). DOI 10.3847/1538-4365/ae1c38 | **OK (2026-09-02; IOP full text)** |
| 2 | Line A scale-factor lineage (v3.00) | Bauschlicher, Ricca, Boersma, Allamandola, ApJS **234**, 32 (2018). DOI 10.3847/1538-4365/aaa019 | **OK (2026-09-02; PAHdb citations block)** |
| 3 | PAHdb v2.00 tools paper | Boersma et al., ApJS **211**, 8 (2014). DOI 10.1088/0067-0049/211/1/8 | **OK (2026-09-02)** |
| 4 | **Scoreboard** — PAHdb laboratory spectra | Mattioda et al., ApJS **251**, 22 (2020). DOI 10.3847/1538-4365/abc2c8 | **OK (2026-09-02)**; **Read in full 2026-09-06** (laboratory readings below): Ar matrix at 15 ± 3 K, 0.5 cm⁻¹, apex positions, A-values scaled to the computed sum over 500–1550 cm⁻¹ — the matrix intensities are not theory-independent |
| 5 | **Line C** — MLMD anharmonic to C₂₁₆ | Mai et al., MNRAS **541**, 3073 (2025); arXiv:2503.05120 | **OK (2026-09-02; arXiv)**; MNRAS landing NOT FETCHED (debt 3); **arXiv v3 full text + Zenodo record 10.5281/zenodo.14998197 read 2026-09-10** (B3LYP/4-31G teacher; 50/300/600 K; 102 MB data archive, CC BY-NC-SA) |
| 6 | **Line B** — anharmonic DFT-QFF pyrene/coronene (**B97-1**: TZ2P for pyrene, 6-31G* for coronene; cubic/quartic constants by differencing analytic Hessians along modes) | Mulas, Falvo, Cassam-Chenaï, Joblin, JCP **149**, 144102 (2018). DOI 10.1063/1.5050087; arXiv:1809.05669 | **record (plan-02)**; arXiv re-verified by the Round-6 Pass B reviewer 2026-09-02; full text read by the Round-7 Pass B reviewer 2026-09-03 (functional and method details from that reading) |
| 7 | **Cheap line** — ML-corrected DFT scaling | Bos et al., ACS Omega **10**(50), 62282 (2025). DOI 10.1021/acsomega.5c10225 | **OK (2026-09-02; Crossref)**; **full text read 2026-09-10 via Europe PMC PMC12750190**: MAE 5.07 / max 13.17 cm⁻¹ (SVR) vs 10.41 / 23.49 (conventional), Ar-matrix reference bands, 80/20 split by instance (debt 1 paid) |
| 8 | Matrix lab source (the 1998 species: naphthalene, anthracene, phenanthrene, benz[a]anthracene, chrysene, pyrene, tetracene, triphenylene) | Hudgins & Sandford, J. Phys. Chem. A **102**, 329 (1998). DOI 10.1021/jp9834816 | **PDF from the supervisor 2026-09-08; methods, abstract and conclusions read** (Readings of 2026-09-08): Ar matrix at 10 K, Ar:PAH 1200:1 (naphthalene), **0.9 cm⁻¹ resolution**, 0.23 cm⁻¹ sampling; matrix shifts "typically 0–15 cm⁻¹" vs gas; relative intensities only |
| 9 | IRMPD standard at R2 (cations, context only) | Tang et al., JCP **163**, 044304 (2025); arXiv:2504.11898 | **record (plan-02)** |
| 10 | Equivariant-attention precedent for M05 | Ji et al., DetaNet, arXiv:2510.04227 (2025) | **record (plan-02)** |
| 11 | Tier-1/2 emission template | Chen, Li & Li, A&A (2026); arXiv:2607.20015 | **record (plan-02)** |
| 12 | PAHdb Anharmonic v1.00 method papers — **specified 2026-09-08** from the reference list of Ricca et al. 2026 (ApJS 282, 7; Crossref deposit, 84 references), which is where the collective label "Mackie et al. 2015–2022; Esposito et al. 2024a–c" comes from | (1) Mackie, Candian, Huang, Maltseva, Petrignani, Oomens, Buma, Lee & Tielens, JCP **143**, 224314 (2015), DOI 10.1063/1.4936779 — naphthalene, anthracene, tetracene QFF; (2) Mackie et al. (+ Mattioda), JCP **145**, 084313 (2016), DOI 10.1063/1.4961438 — benz[a]anthracene, chrysene, phenanthrene, pyrene, triphenylene; (3) Mackie, Chen, Candian, Lee & Tielens, JCP **149**, 134302 (2018), DOI 10.1063/1.5038725 — fully anharmonic cascade spectra; (4) Mackie, Candian, Lee & Tielens, Theor. Chem. Acc. **140**, 124 (2021), DOI 10.1007/s00214-021-02807-z — 11.2 µm cascade; (5) Mackie, Candian, Lee & Tielens, JPCA **126**, 3198 (2022), DOI 10.1021/acs.jpca.2c01849 — anharmonicity and the emission spectrum; (6) Esposito, Allamandola, Boersma, Bregman, Fortenberry, Maragkoudakis & Temi, Mol. Phys. **122**, e2252936 (2024), DOI 10.1080/00268976.2023.2252936 — phenanthrene, pyrene, pentacene neutral and cation; (7) Esposito, Ferrari, Buma, Boersma, Mackie, Candian, Fortenberry & Tielens, Mol. Phys. **122**, e2261570 (2024), DOI 10.1080/00268976.2023.2261570 — phenylacetylene; (8) Esposito, Ferrari, Buma, Fortenberry, Boersma, Candian & Tielens, JCP **160**, 114312 (2024), DOI 10.1063/5.0191404 — phenylacetylene mid- to far-IR; (9) Esposito, Fortenberry, Boersma & Allamandola, JCP **160**, 211101 (2024), DOI 10.1063/5.0208597 (= item 45, held, read); (10) Esposito, Fortenberry, Boersma, Maragkoudakis & Allamandola, MNRAS Lett. **531**, L87 (2024), DOI 10.1093/mnrasl/slae037 (CC BY) — cyano-PAH CN stretch | **identifiers Crossref-verified 2026-09-08**; texts: (9) read in full; (10) held (user download 2026-09-08, CC BY) and its method section read: B3LYP/N07D in Gaussian16 with the 200 × 974 grid (vs 99 × 590 ultrafine), QFF → VPT2 in a modified SPECTRO with symmetry-based resonance polyad matrices (Martin et al. 1995), resonance window 200 cm⁻¹, modes below 300 cm⁻¹ excluded, stick spectrum convolved with a 1 cm⁻¹ FWHM Gaussian — the PAHdb-anharmonic protocol as this letter states it; (1)–(8) asked of the supervisor (request item 21, specified). Not in Ricca's list but on the same method line: Mackie et al., PCCP **20**, 1189 (2018), DOI 10.1039/c7cp06546a (hydrogenated/methylated PAHs) |
| 13 | Closest ML-anharmonic precedent and its warning | Lam, Abdul-Al, Allouche, JCTC (2020). DOI 10.1021/acs.jctc.9b00964 | **record (plan-02)**; arXiv PDF held since 2026-09-06; **read in full 2026-09-10** (arXiv:1909.12661v2): B2PLYP/def2tzvpp harmonic part kept, cubic and quartic constants from an n2p2 neural-network potential trained on 24N single points (3N × 8 displaced geometries), iGVPT2; 37 molecules incl. benzene and naphthalene, 407 experimental fundamentals; RMSD 21 cm⁻¹ vs full B2PLYP and 23 vs experiment, full B2PLYP itself 20 vs experiment — the network adds no error, the DFT level sets the floor; the two aromatics were not checked against full B2PLYP (cost, symmetry); the journal volume/page in the file name (16, 1681) still not verified |
| 14 | Origin of the hybrid split (harmonic anchor + cheap anharmonic) | Boese, Klopper, Martin, Mol. Phys. **103**, 863 (2005). DOI 10.1080/00268970512331339369 | **record (plan-02)** |
| 15 | DLPNO caveat on delocalised π (energies) | Sylvetsky, Banerjee, Alonso & Martin, JCTC **16**, 3641 (2020); arXiv:2001.08641 | **pinned 2026-09-02**; re-verify at scored use |
| 16 | Δ-learning precedent (~10² high-level points) | Käser, Boittier, Upadhyay & Meuwly (four authors on the held PDF's first page; "Käser & Meuwly" until 2026-09-06), arXiv:2103.05491; Käser et al., arXiv:2109.08407 | **record (plan-02)**; arXiv PDF held since 2026-09-06; **read in full 2026-09-10** (arXiv:2103.05491v2): PhysNet + VPT2 on 4–9-atom molecules (H₂CO … CH₃CONH₂); transfer learning from an MP2 model to CCSD(T)(-F12) with 188 points for H₂CO and 262 / 452 / 542 / 632 CCSD(T) geometries — energies, gradients and dipoles, ≈ 5 % of the MP2 set — for CH₃CHO / CH₃NO₂ / CH₃COOH / CH₃CONH₂; TL harmonic MAE 0.1–0.3 cm⁻¹ (1.1 for acetamide) vs explicit CCSD(T); VPT2 within 20 cm⁻¹ of experiment for ≈ 90 % of modes at the best level; no aromatic, gradients required, a global surface learned per molecule; the journal record (JCTC 17, 3687) still not verified |
| 17 | DLPNO-CCSD(T) method / ORCA citations | Neese group | **records verified 2026-09-10 (OpenAlex):** Riplinger & Neese 2013, "An efficient and near linear scaling pair natural orbital based local coupled cluster method", DOI 10.1063/1.4773581; Riplinger, Sandhoefer, Hansen & Neese 2013, "Natural triple excitations in local coupled cluster calculations with pair natural orbitals", DOI 10.1063/1.4821834; Riplinger, Pinski, Becker, Valeev & Neese 2016, "Sparse maps … II. Linear scaling domain based pair natural orbital coupled cluster theory", DOI 10.1063/1.4939030 — all closed, not read; cited only for ORCA as a candidate engine (the plan's engine is LNO-CCSD(T), Nagy & Kállay) |
| 18 | Boundary-edge codes (M02 atlas) | Hansen et al. 1996; Caporossi & Hansen 1998 | **record** — fetch at M02 |
| 19 | Rubric-required M03 methods citation | Huebner et al., PLOS ONE **19**(5): e0295726 (2024). DOI 10.1371/journal.pone.0295726 | **record (plan-03)** |
| 20 | Temperature-dependent PAH band shifts (tier-2 scoreboard) | Joblin-era measurements — now identified as items 52–53 for the u_band temperature term | **debt 4 paid 2026-09-06** — items 52 and 64 read in full (Readings below); the tier-2 emission-scoreboard use remains a separate, unpaid debt |
| 21 | M04 fallback dataset | NIST CCCBDB, SRD 101, Release 22 (2022). DOI 10.18434/T47C7Z | **OK (2026-09-02)** |
| 22 | M04 fallback dataset, second option | Zapata Trujillo & McKemmish, J. Phys. Chem. A **126**(25), 4100 (2022). DOI 10.1021/acs.jpca.2c01438 | **OK (2026-09-02; Crossref)** |
| **23** | **O(1)-gradient Hessian recovery (off-diagonal low rank)** — the pattern construction plan 05 adopts | Wang, Luo, Wang & Liu, "O1NumHess: A Fast and Accurate Seminumerical Hessian Algorithm Using Only O(1) Gradients", JCTC **21**(21), 10893–10909 (2025). DOI 10.1021/acs.jctc.5c01354; arXiv:2508.07544. Open-source Python (O1NumHess, O1NumHess_QC; ORCA + BDF interfaces) | **OK (2026-09-03; arXiv abstract + HTML full text; Crossref)**. Numbers quoted (~100–124 gradients; ~2× conventional error) are from the full text |
| **24** | **Compressed-sensing Hessian in a cheap-method eigenbasis; polyacenes** | Sanders, Andrade & Aspuru-Guzik, "Compressed Sensing for the Fast Computation of Matrices: Application to Molecular Vibrations", ACS Cent. Sci. **1**(1), 24–32 (2015). DOI 10.1021/oc5000404; arXiv:1410.4848; PMC4827532 | **OK (2026-09-03; PMC full text; Crossref)**. Numbers quoted (anthracene 30 % columns, <3 cm⁻¹; 1–15-ring polyacenes ~log growth) are from the full text |
| **25** | GPU DFT Hessians (the global part on GPU) | Wu et al., "Enhancing GPU-acceleration in the Python-based Simulations of Chemistry Framework", arXiv:2404.09452 (2024); docs pyscf.org/user/gpu.html | **OK (2026-09-03; arXiv abstract)** — the abstract states a 30× speed-up over a 32-core CPU node and does not mention Hessians; the **84-atom / ~30 min Hessian figure was seen in a search snippet only** and is not a cite; re-time before any budget use |
| **26** | GPU canonical CCSD(T) (licence reference at larger size) | Fajen, Kelly, Hohenstein & Martínez, "Accelerating CCSD(T) on Graphical Processing Units (GPUs)", J. Phys. Chem. A **130**(10), 2225–2237 (2026; online 2026-02-26); arXiv:2512.01055 (posted December 2025) | **OK (2026-09-03; arXiv abstract; Crossref)**. Numbers quoted (63 atoms, >1,000 bf, (T) ~8 h on one node) are from the abstract |
| **27** | Hybrid QFF: CC quadratic + DFT cubic/quartic (precedent for the harmonic-first allocation, with item 14) | Bégué, Carbonnière & Pouchan, "Calculations of Vibrational Energy Levels by Using a Hybrid ab Initio and DFT Quartic Force Field: Application to Acetonitrile", J. Phys. Chem. A **109**(20), 4611–4616 (2005). DOI 10.1021/jp0406114 | **OK (2026-09-03; Crossref)** — author list verified; the "<0.8 % mean deviation" figure seen in a search snippet is **not quoted in any frozen document** and is not a cite until the full text is read; **PDF from the supervisor 2026-09-08, read in full** (Readings below): CCSD(T)/cc-pVTZ quadratic + B3LYP/cc-pVTZ cubic/quartic expressed in the CCSD(T) normal coordinates, acetonitrile, 31 observed bands, mean absolute deviation < 0.8 %; hybrid and full-CCSD(T) quartic fields give "very similar" transitions; factor 10 cheaper |
| **28** | Reduced-dimensionality VPT2 for large molecules | Fusè, Mazzeo, Longhi, Abbate, Yang & Bloino, "Scaling-up VPT2: A feasible route to include anharmonic correction on large molecules", Spectrochim. Acta A **311**, 123969 (2024). DOI 10.1016/j.saa.2024.123969 | **OK (2026-09-03; Crossref)**; **read in full 2026-09-06** (Readings below) |
| **29** | Frozen domains for numerical local-correlation derivatives (`StoreDLPNOData`, `RefBaseName`; DLPNO-MP2 only) | ORCA 6.1.1 manual, §3.9 Perturbation Theory – MP2 | **OK (2026-09-03; manual page)** — documented for DLPNO-MP2, **not for DLPNO-CCSD(T)** |
| **30** | PNO domain discontinuities corrupt finite-difference properties | Madriaga & Crawford, "Occurrence and Impact of Electric-Field-Induced Discontinuities in Correlation Energies from Localized Pair-Natural-Orbital Methods", J. Phys. Chem. A **129**(43), 10014–10030 (2025). DOI 10.1021/acs.jpca.5c05210; PMC12581137 | **OK (2026-09-03; Crossref + PMC full text)** — discontinuities typically ~1 μE_h, largest 6.09 μE_h (water, cc-pVDZ) under field steps; fixing the per-pair PNO dimensions did **not** remove them ("large discontinuities and associated errors persist, especially for larger test cases"); no definitive remedy recommended. Cited in Q6's rationale as the named risk of frozen domains |
| **31** | Analytic gradient status in ORCA 6.x | ORCA 6.1 detailed change log; ORCA 6.0 "Single Point Energies and Gradients" page | **OK (2026-09-03; both pages)** — canonical CCSD(T) gradients listed in 6.1; DLPNO-MP2 (RHF) analytic gradients; **no DLPNO-CCSD(T) analytic gradient advertised** |
| **32** | Open-source DLPNO-CCSD(T) (single node; crambin-size) | Psi4 manual, "DLPNO-CCSD(T)" | **OK (2026-09-03; manual page)** — gradients not mentioned; domain freezing not documented |
| **33** | Local-CC gradients by automatic differentiation | Zhang, Li, Ye, Berkelbach & Chan, "Performant Automatic Differentiation of Local Coupled Cluster Theories: Response Properties and Ab Initio Molecular Dynamics", JCP **161**, 014109 (2024); arXiv:2404.03129 (PySCFAD, LNO-CCSD(T)) | **OK (2026-09-03; arXiv abstract)**; full text read by the Round-7 and Round-8 Pass B reviewers: LNO spaces held fixed in the derivative; localization differentiated implicitly; (T) backward pass on the fly; memory dominated by ⟨ov|vv⟩ with `jax.checkpoint` recomputation; **no GB figures, no gradient-vs-energy wall-clock**; validated against canonical CCSD(T) AD gradients on the Baker set (3–29 atoms, cc-pVDZ), never against finite differences of its own LNO energy |
| **34** | LNO-CCSD(T) at up to ~1,000 atoms (MRCC) | Nagy & Kállay, "Approaching the Basis Set Limit of CCSD(T) Energies for Large Molecules with Local Natural Orbital Coupled-Cluster Methods", JCTC **15**(10), 5275–5298 (2019). DOI 10.1021/acs.jctc.9b00511; Mester et al., J. Phys. Chem. A **129**, 2086 (2025) (MRCC overview) | **OK (2026-09-03; Crossref for Nagy & Kállay)**; Mester et al. record (search 2026-09-03) |
| **35** | Short-range Δ-ML: the CC−DFT correction is short-ranged (condensed phase, energies) | Mészáros, Szabó & Daru, JCTC **21**(11), 5372 (2025); arXiv:2502.16930 | **OK (2026-09-03; arXiv abstract)** |
| **36** | Small-to-large transfer of correlation energies (locality argument, energies) | Welborn, Cheng & Miller, "Transferability in Machine Learning for Electronic Structure via the Molecular Orbital Basis", JCTC **14**(9), 4772–4779 (2018). DOI 10.1021/acs.jctc.8b00636 | **OK (2026-09-03; Crossref)** |
| **37** | Δ-learning the (T) increment from few points | Ruth, Gerbig & Schreiner, "Machine Learning of Coupled Cluster (T)-Energy Corrections via Delta (Δ)-Learning", JCTC **18**(8), 4846–4855 (2022). DOI 10.1021/acs.jctc.2c00501 | **OK (2026-09-03; Crossref)**; PDF from the supervisor 2026-09-08, abstract and conclusions read: GNN Δ-learning of E[CCSD(T)] − E[CCSD] on small organic molecules, MAE 0.25–0.28 kcal mol⁻¹ — energies, not force constants |
| **38** | Compressive sensing of anharmonic force constants (solids) | Zhou, Nielson, Xia & Ozolins, "Compressive sensing lattice dynamics. I. General formalism", Phys. Rev. B **100**, 184308 (2019); arXiv:1805.08904 | **OK (2026-09-03; arXiv abstract)** |
| **39** | MLP-derived quartic force fields, VPT2 in seconds (context for the DFT anharmonic part) | Kotaru et al., J. Phys. Chem. Lett. **17**(24), 6580 (2026); arXiv:2604.20040 | **OK (2026-09-03; arXiv abstract)** |
| **40** | Δ-learning CC−DFT for lattice dynamics (energies only) | arXiv:2507.06929 (2025) | **OK (2026-09-03; arXiv abstract)** |
| **41** | Rust electronic-structure code (cited only to close the language question) | Li, Gao, Wang, Bi, Feng, Zhu, Zhao, Yan, Yu, Gao, Lin, Wu, Zhang & Xu, "REST: Embracing the rust programming language for modern electronic structure theory", Chin. J. Chem. Phys. **38**(6), 788–796 (2025). DOI 10.1063/1674-0068/cjcp2510156 | **OK (2026-09-03; Crossref)**; the statement that REST has no local coupled cluster rests on its abstract as seen in a search snippet (DFT-family methods listed; no CC) — not verified against the full text |

| **42** | **Prior art for the diagonal mode-E recovery**: high-level force constants in a low-level normal-mode basis from single-point energies (CMA) | Lahm, Kitzmiller, Mull, Allen & Schaefer, "Concordant Mode Approach for Molecular Vibrations", J. Am. Chem. Soc. **144**(51), 23271–23274 (2022). DOI 10.1021/jacs.2c11158 | **OK (2026-09-03; Crossref)**; abstract read by the Round-7 Pass B reviewer; **PDF from the supervisor 2026-09-08, read in full** (Readings below): CMA-0A(nc) MAD 0.16–0.23 cm⁻¹, SD < 0.5 over 1,581 CCSD(T)/cc-pVTZ frequencies; the > 2.5 cm⁻¹ outliers are aromatic-ring modes — benzene ω5(b1g) 1001.2 cm⁻¹ +4.6 with CCSD(T)/cc-pVDZ modes, ring puckering 674.7 +3.4 with B3LYP modes, pyridine, pyrrole, furan; one CMA-1A coupling repairs each; concordant modes are **internal-coordinate** normal modes, and the S choice matters once elements are dropped |
| **43** | **CMA-2**: diagnostic-selected off-diagonals; diagonal-only fails on aromatic ring modes (pyridine errors to ±28 cm⁻¹; benzene, pyrrole, furan flagged) | Kitzmiller, Lahm, Olive Dornshuld, Jin, Allen & Schaefer, "Convergent Concordant Mode Approach for Molecular Vibrations: CMA-2", JCTC **20**(24), 10886–10898 (2024). DOI 10.1021/acs.jctc.4c01240; PMC11673116 | **OK (2026-09-03; Crossref)**; full text read by the Round-7 Pass B reviewer (numbers quoted from that reading) |
| **44** | Local-approximation error grows with acene length; CPS extrapolation as remedy | Altun, Ghosh, Riplinger, Neese & Bistoni, "Addressing the System-Size Dependence of the Local Approximation Error in Coupled-Cluster Calculations", J. Phys. Chem. A **125**(45), 9932–9939 (2021). DOI 10.1021/acs.jpca.1c09106; PMC8607505 | **OK (2026-09-03; Crossref)**; full text read by the Round-7 Pass B reviewer and **by the author in full 2026-09-06** (Readings below) |
| **45** | B3LYP/N07D vs CCSD(T)-F12b/cc-pVTZ-F12 harmonic frequencies of **benzene only** (MAD 5.45 cm⁻¹, Table S1) and the PAHdb-anharmonic protocol (B3LYP/N07D, 200 × 974 grid, 2-quanta polyads, 20 cm⁻¹ Lorentzian); **not** a CC/DFT allocation precedent — its force field is DFT throughout, no coupled-cluster constant enters its spectra, nothing coupled-cluster is done on naphthalene (use corrected 2026-09-06 after the literature cold read) | Esposito, Fortenberry, Boersma & Allamandola, "Assigning the CH stretch overtone spectrum of benzene and naphthalene with extension to anthracene and tetracene using 2- and 3-quanta anharmonic quantum chemical computations", JCP **160**(21), 211101 (2024). DOI 10.1063/5.0208597 | **OK (2026-09-03; Crossref)**; **read in full 2026-09-06** (Readings below) |
| **46** | Mode-tracking: selected high-level modes from few gradients (prior art named in the novelty rewrite) | Reiher & Neugebauer, "A mode-selective quantum chemical method for tracking molecular vibrations applied to functionalized carbon nanotubes", JCP **118**, 1634–1641 (2003). DOI 10.1063/1.1523908 | **OK (2026-09-03; Crossref)**; **PDF from the supervisor 2026-09-08, read in full**: Davidson-type subspace iteration on the Hessian with numerical derivatives of analytic gradients along collective displacements; convergence hinges on the guess; the paper itself proposes a cheap-method guess refined at CCSD(T) — named in the novelty table 2026-09-08 |
| **47** | **M05 corpus**: public Hessian set for the DFT-vs-DFT Δ₂ corpus | Williams, Kabalan, Stojanovic, Zolyomi & Pyzer-Knapp, "Hessian QM9: A quantum chemistry database of molecular Hessians in implicit solvents", arXiv:2408.08006 (2024); 41,645 QM9 molecules, ωB97x/6-31G* | **OK (2026-09-03; arXiv abstract)**; the Sci. Data landing page NOT FETCHED |

| **48** | LNO-CC energy code the side project extends | pyscf-forge, `pyscf/lno/`: `domain.py, lno.py, lnoccsd.py, lnoccsd_t.py, make_lno_rdm1.py, tools.py, ulno.py, ulnoccsd.py, ulnoccsd_t.py, ulnoccsd_t_slow.py, test/`; CHANGELOG 1.1.0 (2026-02-20) "LNO-CCSD for molecules and PBC systems" is a summary line; github.com/pyscf/pyscf-forge | **OK (2026-09-04; directory listing fetched by the Round-8 Pass B reviewer and by the author)** — **LNO-CCSD(T) is present, closed- and open-shell**; behaviour with frozen spaces is probe M1's measurement; **API fact (Round-10 reviewer, `lno.py` opened 2026-09-04):** the LNO class takes the localized occupied orbitals as an input (`lo_coeff`) and rebuilds every fragment's LNO space on each call — arm B is free, arm A needs a small override, pinned by commit |
| **49** | PySCFAD repository and its LNO-CC code (automatic differentiation for PySCF; Apache-2.0; Python/JAX) | github.com/fishjojo/pyscfad; `pyscfad/lno/`: `__init__.py, _checkpointed.py, ccsd.py, ccsd_mpi.py, ccsd_t.py, ccsd_t_slow.py, lno_base.py, lno_base_mpi.py, mp2.py, mp2_mpi.py, mp2_rdm.py, tools.py, test/`; `examples/lno/` | **OK (2026-09-04; directory listing fetched by the Round-8 Pass B reviewer and by the author)** — the README does not mention it; the gradient is `jax.grad` of the differentiable energy, so no separate gradient file exists; commit hashes pinned at side-project item (a) |

| **50** | NIST/EPA Gas-Phase Infrared Database (SRD 35) description — the R2 gas scoreboard's provenance | nist.gov/document/35204jcmp-revisedpdf (JCAMP format description) | **record (search 2026-09-04)** — the Round-8 Pass B reviewer downloaded the PDF but could not text-extract it; the statements used (EPA spectra at 4 cm⁻¹; **all spectra converted to 8.0 cm⁻¹ resolution**; all GC/IR, concentrations unknown; 5,228 spectra) are **snippet grade**; the triphenylene species page and JCAMP (`##STATE=gas`, `##DELTAX=4.0`, no resolution or temperature line, "molar absorptivity values cannot be derived") were fetched by the reviewer. M03 re-reads the description before u_band is printed **Read in full 2026-09-12 (the 3-page JCAMP users' guide, text extracted; `Papers/plan05_m03/`):** 5,228 spectra = 3,108 EPA (Sadtler Research Laboratories under EPA contract, Digilab instruments, originally 4 cm⁻¹, 450–4000) + 2,120 NIST (HP integrated capillary GC-MS-IR, IRD 5965, 8 cm⁻¹, 550–3846); "all have been converted to exact 8.0 cm⁻¹ resolution" (now read, not snippet); normalised absorbance, no molar values; **for the EPA spectra "a complete original set of header information has not been located, so analytical conditions are not given"; no temperature is stated for either subset.** Consequence: the GC-IRD source temperature cannot be documented from SRD 35; the u_band columns carry the Ladder's hot default (250 °C) as a labelled assumption per record origin (our naphthalene, anthracene and benzene GC-IRD records are EPA/Sadtler; pyrene, chrysene, triphenylene are NIST/HP) |
| **51** | PNO-space relaxation terms in local-correlation gradients (the term the side project's projection must carry) | Pinski & Neese, DLPNO-MP2 analytic gradient, JCP **148**, 031101 (2018) and JCP **150**, 164102 (2019) | **PDFs from the supervisor 2026-09-08; abstracts, Lagrangian sections and conclusions read** (Readings of 2026-09-08): PNO-relaxation constraints in the Lagrangian are critical; **continuously degenerate localised orbitals (benzene π in Pipek–Mezey) make the coupled-perturbed localisation equations singular — they modify the localisation constraint**; DLPNO-MP2 surfaces keep discontinuities "on a scale of several µE_h" at default thresholds, reducible with tighter ones; domain freezing/merging (Mata & Werner 2006) and residual smoothing (Subotnik & Head-Gordon 2005) named as the known remedies |
| **52** | PAH hot-band shift with temperature — the u_band temperature term's pinned reference (naphthalene, pyrene, coronene vs temperature) | Joblin, Boissel, Léger, d'Hendecourt, Défourneau, A&A **299**, 835 (1995), "Infrared spectroscopy of gas-phase PAH molecules. II. Role of the temperature" | **reference known, not opened** — cited from the Round-9 Pass B reviewer's search (a snippet quotes a C–C stretch shift of about −0.02 cm⁻¹ K⁻¹); the ADS abstract page returned 405 to the author on 2026-09-04 and no Crossref record exists for this 1995 A&A paper; **first paid debt**: obtain and read before M03 prints u_band; **Obtained (ADS scan) and read in full 2026-09-06** (laboratory readings below): Tables 1–2 (slopes χ′ and width slopes χ″) transcribed; the recalled χ_max = 0.03 cm⁻¹ K⁻¹ is exceeded by the coronene 6.2 µm band (−0.044); debt paid |
| **53** | Naphthalene hot-band spectroscopy and anharmonic parameters — second pinnable source for the R1 temperature correction | Pirali, Vervloet, Mulas, Malloci, Joblin, PCCP **11**, 3443 (2009), DOI 10.1039/b814037e, "High-resolution infrared absorption spectroscopy of thermally excited naphthalene. Measurements and calculations of anharmonic parameters and vibrational interactions" | **Crossref record verified 2026-09-04 (author)**; numbers not read — full text before any shift rate is quoted; **also a room-temperature source**: a high-resolution (0.005 cm⁻¹, snippet grade) room-temperature and heated cell study, so its CH-oop band centres are an R1 scoreboard column as well as the hot-band pin; **PDF from the supervisor 2026-09-08, read in full** (Readings below): 0.005 cm⁻¹, 300 K, 0.1 mbar, 8 m White cell; Table 1 gives 16 gas-phase fundamentals with the fundamental Q-branch head **resolved from its hot bands**; Table 2 effective anharmonic constants of the low modes; hot-band structure accounts for the low-resolution temperature shifts — **named as an R1 position source (Ladder dated note 2026-09-08); scored with u_T = 0 + 0.5 cm⁻¹ head-to-origin (decision 21, P11 a)** |
| **54** | NIST WebBook, benzene (CAS 71-43-2), IR spectrum list — the R0 gas scoreboard's source record | webbook.nist.gov `cbook.cgi?ID=C71432&Mask=80` | **opened 2026-09-04 by the Round-9 reviewer and by the author**: a Coblentz gas spectrum (70 mmHg + N₂ to 600 mmHg, 2 cm⁻¹), a NIST MS Data Center gas entry, and **twenty NIST Quantitative Infrared Database gas-phase entries at 0.125–1.93 cm⁻¹** (Bruker IFS66V, five apodizations); **no entry states a temperature** — the series' documentation (item 56) supplies it |
| **55** | NIST WebBook, naphthalene (CAS 91-20-3), IR spectrum list — the R1 gas scoreboard's source record | webbook.nist.gov `cbook.cgi?ID=C91203&Mask=80` | **opened 2026-09-04 by the Round-9 reviewer and by the author**: a Coblentz solution spectrum; a Coblentz **vapour spectrum at 245 °C**, 4 cm⁻¹, digitised from hard copy; a NIST MS Data Center gas (GC-IRD) entry; **no room-temperature gas-phase spectrum** |
| **56** | The NIST Quantitative Infrared Database — measurement conditions (temperature, path, resolution) of the R0 cell spectra | Chu, Guenther, Rhoderick, Lafferty, J. Res. Natl. Inst. Stand. Technol. **104**, 59 (1999), DOI 10.6028/jres.104.004 | **Crossref record verified 2026-09-04 (author)**; the paper itself not read — M03 reads it before u_band is printed, because R0's "unconditional" rests on the temperature it states; **Read in full 2026-09-06** (laboratory readings below): 296 K, 760 Torr N₂, 0.12 cm⁻¹ boxcar, wavenumber scale ±0.0042 cm⁻¹ RMS on 158 water lines, benzene intensities 3.3 % (k = 2) and **not certified in 1325–1900 cm⁻¹** |
| **57** | A room-temperature, 0.1 cm⁻¹ quantitative vapour-phase naphthalene spectrum — the R1 gas scoreboard's source | Schneider, Baker, Scharko, Blake, Tonkyn, Forland, Johnson, J. Quant. Spectrosc. Radiat. Transfer **323**, 109045 (2024), DOI 10.1016/j.jqsrt.2024.109045, "A method for generating quantitative vapor-phase infrared spectra of solids: results for phenol, camphor, menthol, syringol, dicyclopentadiene and naphthalene" | **Crossref record verified 2026-09-04 (author)**; full text opened by the Round-10 reviewer (OSTI PDF): 760 Torr N₂-broadened composites, 600–6500 cm⁻¹, 0.1 cm⁻¹, White cell thermostatted at 25 °C (general procedure; naphthalene's own run to be confirmed in the paper's table), naphthalene already in the PNNL/NWIR database (item 59). **Author's own read owed before M03 prints u_band**; **Read in full 2026-09-06** (laboratory readings below): naphthalene from CS₂ solution only, disseminator-flow into an 8.05 m White cell, 0.112 cm⁻¹, composites at 1 ppm-m and 296 K, ±8 % (2σ); the cell temperature is stated as 25 °C in §2 and 50 °C in the Fig. 6 caption — 2a takes it from the record header |
| **58** | Jet-cooled 3 µm spectra of the R2 gas set — a cold gas-phase source for the C–H-stretch family | Maltseva, Petrignani, Candian, Mackie, Huang, Lee, Tielens, Oomens, Buma, ApJ **831**, 58 (2016), DOI 10.3847/0004-637x/831/1/58, "High-resolution IR absorption spectroscopy of polycyclic aromatic hydrocarbons in the 3 µm region: role of periphery" | **Crossref record verified 2026-09-04 (author)**; abstract read by the Round-10 reviewer (pyrene, chrysene, triphenylene among the species; band widths down to 1 cm⁻¹); the 6–15 µm region is not covered — the R2 C–C expectation stands |
| **59** | The PNNL/NWIR gas-phase quantitative IR database — conditions of the naphthalene record (5 / 25 / 50 °C, 760 Torr N₂) | Sharpe, Johnson, Sams, Chu, Rhoderick, Johnson, Appl. Spectrosc. **58**, 1452 (2004), DOI 10.1366/0003702042641281, "Gas-phase databases for quantitative infrared spectroscopy" | **Crossref record verified 2026-09-04 (author)**; not read; M03 reads it and the naphthalene record's own header before u_band is printed; **PDF from the supervisor 2026-09-08, read in full** (Readings below): PNNL 0.112 cm⁻¹ boxcar, 19.94/19.96 cm static cell backfilled to 760 ± 5 Torr N₂, sample temperatures 5 / 25 / 50 °C (± 1 °C), wavenumber RMS 0.0018 cm⁻¹, systematic 2.3 % (2σ), statistical < 2 % (1σ); every record ships a metadata PDF with the sample conditions — 2a reads it; NIST measured at 23 °C, corrected to 296 K |
| **60** | Gas-phase PAH hot-band slopes at second hand (pyrene 573–873 K: −0.025 cm⁻¹ K⁻¹ at 3.3 µm, −0.014 at 11.8 µm, quoted from item 52) and the sub-linear low-temperature behaviour | Chakraborty, Mulas, Rapacioli, Joblin, arXiv:2102.06582 (thermally excited pyrene) | **HTML full text opened by the Round-10 reviewer 2026-09-04**; the author's own read owed; supports χ_max = 0.03 as an upper bound and the conservative linear-from-296 K floor |
| **61** | Jet-cooled mid-IR (5–18 µm) band list of tetracene — the only cold gas-phase 6–15 µm datum for an R2 species | Lemmens, Rap, Thunnissen, Mackie, Candian, Tielens, Rijs, Buma, A&A **628**, A130 (2019), DOI 10.1051/0004-6361/201935631; arXiv:1907.09351 | **Crossref record verified 2026-09-05 (author)**; arXiv PDF opened by the 2026-09-05 scout (Table A.2, ≈ 30 bands 548–1970 cm⁻¹); FEL bandwidth ≈ 1 % of frequency — the u_band resolution term; author's own read owed before M03 uses it; **Read in full 2026-09-06** (laboratory readings below): FELIX bandwidth ≈ 1 % of the frequency is the resolution term |
| **62** | Jet-cooled 3–100 µm spectra of coronene and larger PAHs — six tabulated 6–15 µm bands ("five" until 2026-09-06), the first gas-phase datum for R3 | Lemmens, Rijs, Buma, ApJ **923**, 238 (2021), DOI 10.3847/1538-4357/ac2f9d (CC BY) | **Crossref record verified 2026-09-05 (author)**; IOP full text opened by the scout (Table A1: 854.6, 1132.1, 1208.1, 1306.4, 1607.1 cm⁻¹; T_rot ≈ 2 K; FEL bandwidth 0.5–1 %); author's own read owed; **Read in full 2026-09-06** (laboratory readings below): Table A1 transcribed (12 bands 121–1903 cm⁻¹); FELIX bandwidth 0.5–1 %; cross-checked against the hot and Ne columns of items 52/64 — the 7.7 and 8.8 µm bands disagree with the temperature model by 10–19 cm⁻¹ |
| **63** | One rotationally resolved cold band of pyrene near 8.5 µm (ν68) — a single-line check, not a scoreboard | Brumfield, Stewart, McCall, J. Phys. Chem. Lett. **3**, 1985 (2012), DOI 10.1021/jz300769k | **Crossref record verified 2026-09-05 (author)**; content at snippet grade (slit jet, T_rot ≈ 25 K); paywalled; band origin not read; **PDF from the supervisor 2026-09-08, read in full** (Readings below): ν68 (B3u, C–H in-plane bend) band origin **1184.035595(20) cm⁻¹**, T_rot ≈ 23 K, T_vib ≤ 111 K (3σ), Ar slit jet from a 420 K oven, calibration 0.00049 cm⁻¹ |
| **64** | Gas-phase PAH spectra in a heat-pipe oven, 3–20 µm, 500–800 K (pyrene, coronene) — hot points and the companion of item 52 | Joblin, d'Hendecourt, Léger, Défourneau, A&A **281**, 923 (1994) | **reference known, not opened** (ADS 405; no Crossref DOI for 1994 A&A); same debt as item 52; **Obtained (ADS scan) and read in full 2026-09-06** (laboratory readings below): Tables 1–3 (gas / solid / Ne positions) and 4–6 (integrated cross sections, ±20 %) transcribed for pyrene and coronene; 1 cm⁻¹ resolution, 200 Torr N₂, thermocouple ±0.5 K |
| **65** | Concordant Mode Approach extended to intermolecular vibrations — symmetry zeroing as standard CMA clean-up; the aug-cc-pVTZ 495i cm⁻¹ ring-puckering artefact; MP2 Level B reproduces 435 CCSD(T) frequencies to MAE 0.23 cm⁻¹ | Olive Dornshuld, Lahm, Kitzmiller, Allen & Schaefer, "Concordant Mode Approach (CMA): Vibrational Analysis of New and Upgraded Intermolecular Benchmarks for Noncovalent Bonding", J. Phys. Chem. A **130**, 3249 (2026). DOI 10.1021/acs.jpca.6c00689; CC-BY | **held (user download 2026-09-06) and read in full 2026-09-06** (Readings below); item added 2026-09-06 after the literature cold read — it had been cited in the proposal and the Ladder without a numbered item |
| **66** | The DLPNO-CCSD(T) method papers — thresholds and what the defaults recover (context for items 30, 44 and for the anchor's composite energy) | Riplinger & Neese, JCP **138**, 034106 (2013); Riplinger, Sandhoefer, Hansen & Neese, JCP **139**, 134101 (2013); Riplinger, Pinski, Becker, Valeev & Neese, JCP **144**, 024109 (2016) | **PDFs from the supervisor 2026-09-08; headers, threshold sections and conclusions read**: T_CutPNO 3.33 × 10⁻⁷, T_CutPairs 10⁻⁴, T_CutMKN 10⁻³ (defaults); ≈ 99.9 % of the correlation energy recovered; the triples are semicanonical (T0) with a TNO cut-off, and **at default PNO thresholds at most 96–97 % of the semicanonical triples (91–94 % of the canonical triples) is recoverable** — the (T) piece is the least converged part of a local CC energy; 2016: linear scaling, up to 7× faster |
| **67** | Domain freezing / merging along a potential-energy surface — **prior art for holding local-correlation domains fixed across geometries** (missed by the 2026-09-06 novelty search; found via item 51's text) | Mata & Werner, J. Chem. Phys. **125**, 184110 (2006) | **Crossref-verified 2026-09-10**: "Calculation of smooth potential energy surfaces using local electron correlation methods", DOI 10.1063/1.2364487; closed (AIP returns 403 to scripted access, no abstract via Semantic Scholar); **asked of the supervisor** (PDF request item 24); **not read** — Pinski & Neese describe it as "domain freezing or domain merging introduced by Werner and co-workers"; named in the proposal's novelty table 2026-09-08; read before the pilot note cites the frozen-space object as new |
| **68** | Discontinuities of local-correlation potential-energy surfaces — "a well-known problem" | Russ & Crawford, J. Chem. Phys. **121**, 691 (2004) | **Crossref-verified 2026-09-10**: "Potential energy surface discontinuities in local correlation methods", J. Chem. Phys. 121, 691–696, DOI 10.1063/1.1759322; closed; asked of the supervisor (item 25); **not read**; the problem statement behind item 30 and probe M1 |
| **69** | Smoothing functions in the residual equations against local-correlation discontinuities | Subotnik & Head-Gordon, J. Chem. Phys. **123**, 064108 (2005) | **Crossref-verified 2026-09-10**: "A local correlation model that yields intrinsically smooth potential-energy surfaces", DOI 10.1063/1.2000252; closed; asked of the supervisor (item 26); **not read**; an alternative remedy to freezing |

## Named debts (identical to Frozen_Lines §7)

1. Bos 2025 full text → the actual MAE (item 7).
2. Mackie/Esposito anharmonic method papers (item 12).
3. MNRAS landing for Mai 2025 (item 5); Mulas 2018 landing re-fetch (item 6).
4. Joblin-era T-dependence references (item 20) — **paid 2026-09-06** (items 52 and 64 read in full).
5. Local-CC method and software citations — the DLPNO-CCSD(T) method papers (item 17, NOT
   FETCHED) and the Mester et al. 2025 MRCC overview (item 34, second identifier); items 32,
   33 and 34's Nagy & Kállay are OK; Sylvetsky pinned.
6. C₃₈₄H₄₈ per-species presence in PAHdb v4.00 — an M02 task.

## Method debts (plan 05 only; not in Frozen_Lines because they concern method, not opponents)

- Full texts of items 27 and 37 before any number from them is quoted anywhere (item 28 read in full 2026-09-06; item 30's
  full text was read by the Round-7 Pass B reviewer and its figures are quoted with that
  provenance; the author's own re-read is owed before a scored document quotes them).
- Item 46 (mode-tracking, snippet level) before it is cited as prior art in a scored
  document; item 44 re-read by the author — **done 2026-09-06**.
- The O1NumHess licence and code version, pinned before its pattern construction is used.
- Mester et al. 2025 (MRCC overview) landing page, if MRCC is the chosen code.
- The GPU4PySCF Hessian timing, re-measured (never quoted from the snippet).
- Side project item (a): pin the PySCFAD and pyscf-forge commit hashes actually used (items 48,
  49 — locations now fetched).
- **PAH hot-band shift references** for the u_band temperature term (items 52–53, now named):
  obtain and read before M03 prints u_band — **the first paid debt**, because a pinned per-family
  correction is the only route to decidable C–C families on the existing gas data at R2, and the
  only pin for the R1 hot columns and u_296;
  until then the term is the Ladder §2 floor (χ_max = 0.03 cm⁻¹ K⁻¹, recalled).
- **The M05 reading-2 fallback**: a public Hessian dataset other than Hessian QM9, searched and
  verified before Module 05 starts; none named from recall.
- **QM9's size range** (≤ 9 heavy atoms; no PAH beyond benzene — recalled by the Round-8
  reviewer): verify against the QM9 paper (item 1 of plan 01's bibliography, `Papers/01_…`)
  when the M05 corpus is built.
- Item 50's description PDF, text-extracted and read, before u_band is printed; the 250 °C
  lightpipe temperature used as its default is recalled until then.
- Item 56 (the NIST Quantitative IR database paper) read before u_band is printed: R0's
  "unconditional" rests on the measurement temperature it states.
- Items 57 and 59 (the PNNL/NWIR naphthalene record and its database paper) read, and the record's
  own header fetched, before u_band is printed: R1's "unconditional" rests on them.
- Item 60 read by the author (the Round-10 reviewer's reading is the only one so far).
- Items 61–62 read by the author before M03 builds the tetracene and coronene cold columns; item 63's band origin read before it is used as a one-line check; item 64 with item 52.
- The arm-A override of the pyscf-forge LNO-space construction (item 48 API fact), pinned by
  commit before M1 runs.
- Item 45's MAD figure — **read 2026-09-06**: benzene only, 5.45 cm⁻¹, Table S1; there is no naphthalene figure, so the expected-effect line cites none; item 47's journal landing page; the CMA code/paper details
  (items 42–43) re-read by the author, not only by the Pass B reviewer, before Q7's
  diagonal-only column is specified in a deck.

**Status.** Working bibliography after the 2026-09-03 search pass; readings of 2026-09-06 recorded below; the literature cold read of 2026-09-06 ([Cold_Read_2026-09-06_Literature.md](reviews/Cold_Read_2026-09-06_Literature.md)) addressed the same day; the 2026-09-03 sentence follows: working bibliography after the 2026-09-03 search pass and the same-day Crossref
upgrade. Not a claim that plan 05 is complete.

## Novelty search 2026-09-06 (author, web search; recorded so the proposal's "what is new" table is a measurement, not an assertion)

Eight queries, each read from the result list and, where open, the abstract or full text:

1. "coupled cluster correction to DFT Hessian normal mode displacements off-diagonal force constants sparse recovery 2025 2026" — nearest: Sanders et al. 2015 (bib 24); CMA-2 (bib 43); a 2025 JCTC paper on coupling force constants of metal carbonyls (compliance matrices from full Hessians, DFT benchmarked against CCSD(T); no correction of one level by another — read on PMC).
2. "concordant mode approach CCSD(T) 2025 OR 2026 new paper off-diagonal aromatic" — new: Lahm/Allen/Schaefer group, J. Phys. Chem. A 130, 3249 (2026): CMA extended to 17 intermolecular complexes with MP2 normal modes and CCSD(T)/aug-cc-pVTZ or h-aug-cc-pVTZ targets with MP2/h-aug-cc-pVTZ as Level B (CC-BY; read in full 2026-09-06; item 65). No multi-mode probing, no symmetry blocking, no local CC.
3. "delta-learning Hessian force constants coupled cluster minus DFT machine learning transferable correction vibrational frequencies" — nearest: Δ-ML of DFT-based potentials to CCSD(T) (search-result identifier "Bowman group, JCTC 20, 8807 (2024); ethanol" — unverified, not cited in any scored document; struck from the proposal 2026-09-06); ML Hessians for metastable structures (arXiv 1803.09827); transfer learning to CCSD(T) anharmonic frequencies (Käser & Meuwly, bib). All learn a surface or a Hessian per system or class; none probes a difference Hessian.
4. "frozen PNO OR LNO domains numerical Hessian displaced geometries local coupled cluster discontinuities" — nearest: Madriaga & Crawford 2025 (bib 30, the problem); Psi4 DLPNO manual (no domain freezing); ORCA fixed domains for DLPNO-MP2 (bib 29). Nothing on transported, semicanonicalised frozen fragment spaces measured against canonical CC. **Correction 2026-09-08:** the reading of item 51 surfaced prior art the query missed — domain freezing / merging along a surface (Mata & Werner 2006, item 67), the discontinuity problem (Russ & Crawford 2004, item 68) and residual smoothing (Subotnik & Head-Gordon 2005, item 69). Holding local-correlation domains fixed across geometries is therefore not new in itself (PAO domains, 2006); what remains unclaimed is the LNO-space object transported by projection and semicanonicalised, used for a Δ-recovery, with smoothness and bias measured against canonical CCSD(T). The proposal's table says so since 2026-09-08.
5. "Hessian reconstruction symmetry irreducible representations block sparse recovery vibrational normal modes compressed sensing point group" — nearest: Sanders 2015; symmetry-adapted finite-difference Hessians in AMS (irreps chosen by IR/Raman activity — a full-Hessian shortcut, not a recovery prior).
6. "local coupled cluster harmonic frequencies polycyclic aromatic hydrocarbons CCSD(T) corrected DFT anharmonic infrared 2025 2026" — nearest: Ethereal AI (bib 7); anharmonic PAH spectroscopy reviews; no local-CC harmonic corrections for PAHs found.
7. "Concordant Mode Approach intermolecular benchmarks 2026" — confirms item 2.
8. "normal mode displacements high-level correction low-level Hessian difference CCSD(T) DFT ... multi-mode displacements energies only" — nearest: normal-mode sampling for ML training sets; iGVPT2; Δ-ML as in 3.

**Result.** Every ingredient exists in print; the combination — a symmetry-blocked recovery of the CC−DFT difference Hessian from multi-mode energy patterns, computed in frozen local-correlation spaces transported across geometries, with the probe count and the locality measured per size — was not found. Re-run before the Module-08 paper is written; the 2026 CMA paper is item 65 (CC-BY; read in full 2026-09-06).

## PDFs held locally (2026-09-06; folder `Papers/` at the repository root, git-ignored; open-access sources only)

Fetched by the author with the user's consent; first page checked against the reference. **Held is not read**: each item's status above changes to "read" only when the author has read it and says so, dated.

| item | file | source |
|---|---|---|
| 5 | Mai_2025_MLMD_PAH_MNRAS541_3073.pdf (arXiv v3, 8 pp.) | arXiv:2503.05120 |
| 6 | Mulas_2018_anharmonic_pyrene_coronene_JCP149_144102.pdf (arXiv, 42 pp.) | arXiv:1809.05669 |
| 16 | Kaeser_Meuwly_2021_transfer_learning_CCSDT_JCTC17_3687.pdf (arXiv v2, 70 pp.; arXiv title "MP2 Is Not Good Enough: Transfer Learning ML Models for Accurate VPT2 Frequencies") | arXiv:2103.05491 |
| 30 | Madriaga_Crawford_2025_PNO_discontinuities_JPCA129_10014.pdf (17 pp.) | Europe PMC, PMC12581137 |
| 43 | Kitzmiller_2024_CMA2_JCTC20_10886.pdf (13 pp.) | Europe PMC, PMC11673116 |
| 47 | Williams_2024_Hessian_QM9.pdf (7 pp.) | arXiv:2408.08006 |
| 56 | Chu_1999_NIST_Quantitative_IR_JResNIST104_59.pdf (23 pp.) | nvlpubs.nist.gov |
| 61 | Lemmens_2019_tetracene_jetcooled_AA628_A130.pdf (arXiv v1, 10 pp.) | arXiv:1907.09351 |
| 62 | Lemmens_2021_coronene_jetcooled_ApJ923_238.pdf (11 pp., CC BY) | IOP |
| PySCFAD (side project, item 48's companion) | Zhang_2024_PySCFAD_local_CC_gradients.pdf (29 pp.) | arXiv:2404.03129 |
| 14 | Boese_Klopper_Martin_2005_anharmonic_DFT_MolPhys103_863.pdf (arXiv v1, 32 pp.) | arXiv:physics/0411065 |
| 13 | Lam_2020_QM_ML_anharmonic_JCTC16_1681.pdf (arXiv, 10 pp.) | arXiv:1909.12661 |
| 4 | Mattioda_2020_PAHdb_laboratory_ApJS251_22.pdf (16 pp.) | IOP (bronze OA) |
| 52 | Joblin_1995_gasphase_PAH_temperature_AA299_835.pdf (ADS scan, 12 pp.) | articles.adsabs.harvard.edu |
| 64 | Joblin_1994_gasphase_PAH_heatpipe_AA281_923.pdf (ADS scan, 14 pp.) | articles.adsabs.harvard.edu |
| 57 | Schneider_2024_quantitative_vapor_naphthalene_JQSRT323_109045.pdf (accepted manuscript, 13 pp.) | OSTI 2477598 (green OA) |

From the supervisor, 2026-09-08 (publisher PDFs, personal use; renamed by the author to the convention; texts extracted to `_txt/`):

| item | file | pages |
|---|---|---|
| 59 | Sharpe_2004_PNNL_NIST_quantitative_IR_databases_ApplSpectrosc58_1452.pdf | 10 |
| 53 | Pirali_2009_naphthalene_hot_bands_highres_PCCP11_3443.pdf | 12 |
| 63 | Brumfield_2012_pyrene_rotationally_resolved_JPCL3_1985.pdf | 4 |
| 42 | Lahm_2022_CMA_concordant_mode_JACS144_23271.pdf | 4 |
| 27 | Begue_2005_hybrid_QFF_acetonitrile_JPCA109_4611.pdf | 6 |
| 37 | Ruth_2022_delta_learning_T_corrections_JCTC18_4846.pdf | 10 |
| 46 | Reiher_Neugebauer_2003_mode_tracking_JCP118_1634.pdf | 9 |
| 51 | Pinski_Neese_2018_DLPNO_MP2_derivatives_JCP148_031101.pdf | 6 |
| 51 | Pinski_Neese_2019_DLPNO_MP2_gradient_JCP150_164102.pdf | 29 |
| 66 | Riplinger_Neese_2013_PNO_local_CC_JCP138_034106.pdf | 19 |
| 66 | Riplinger_2013_natural_triples_DLPNO_JCP139_134101.pdf | 14 |
| 66 | Riplinger_2016_sparse_maps_DLPNO_CCSD_JCP144_024109.pdf | 11 |
| 8 | Hudgins_Sandford_1998_matrix_PAH_2to4rings_JPCA102_329.pdf | 15 |
| 12 (10) | Esposito_2024_cyanoPAH_CN_stretch_MNRASL531_L87.pdf (published version, CC BY; downloaded by the user 2026-09-08 from Chapman University Digital Commons, sees_articles/761 — OUP and the repository both bot-block) | 9 |

Housekeeping (2026-09-06 cold read): `Papers/` also holds a byte-identical duplicate of the Käser PDF and a second (MNRAS-typeset) copy of Mai 2025 from plan 03's numbering, plus an untracked local `Papers/README.md` from that era; this table, not that file, is the index.

Checked with OpenAlex and Europe PMC on 2026-09-06: **open at the publisher but bot-blocked**, downloaded by the user the same day and now in `Papers/`: the 2026 CMA paper (CMA_2026_intermolecular_benchmarks_JPCA130_3249.pdf, 12 pp.), Altun 2021 (Altun_2021_local_error_acenes_CPS_JPCA125_9932.pdf, 8 pp.; item 44), Esposito 2024 (Esposito_2024_CH_overtone_benzene_naphthalene_JCP160_211101.pdf, 11 pp.; item 45), Fusè 2024 (Fuse_2024_scaling_up_VPT2_SpectrochimActaA311_123969.pdf, 18 pp.; item 28). **Closed, no author manuscript found** (2026-09-06): Sharpe 2004, Pirali 2009, Brumfield 2012, Lahm 2022, Bégué 2005, Ruth 2022, Reiher 2003, Pinski & Neese 2018 and 2019, Riplinger et al. 2013a, 2013b and 2016, Hudgins & Sandford 1998; the PAHdb-Anharmonic method papers were not looked up individually. These were asked of the supervisor, **and all thirteen arrived on 2026-09-08** (table above); only request item 21 (the PAHdb-Anharmonic method papers, Mackie et al. 2015–2022) is still outstanding. Wang 2025 (item 23) is not: its arXiv full text (HTML) was read 2026-09-03 and the arXiv PDF is fetchable; it was struck from the request on 2026-09-06.

## Readings of 2026-09-06 (author; full texts from `Papers/`; each line says what was taken and where it is used)

- **Olive Dornshuld, Lahm, Kitzmiller, Allen & Schaefer, J. Phys. Chem. A 130, 3249 (2026)** (CMA, intermolecular; CC-BY) — **read in full.** (i) CMA-0A/1A/2A applied to 17 dimers; MP2/haTZ Level B reproduces 435 CCSD(T)/(h)aTZ frequencies to MAE 0.23 cm⁻¹; CMA-2A with 3.0 % of off-diagonals → 0.08 cm⁻¹. (ii) **Symmetry zeroing is standard CMA practice**: "symmetry was rigorously applied ... by zeroing out numerical residuals of F_CMA force constants between coordinates belonging to differing irreducible representations", non-Abelian degenerate blocks averaged — as a clean-up of a *full* Level-A matrix, not as a prior for recovery. Consequence: the proposal's novelty table must not present symmetry blocking as new in itself (patched 2026-09-06). (iii) Their persistent benzene outliers are a **single coupling between ring deformations** (ω ≈ 1155 and 1331 cm⁻¹ at Level A, residuals ∓4 cm⁻¹, cured by one off-diagonal) — independent corroboration of the same-representation coupling our surrogate found at 1186/1357 cm⁻¹ (B3LYP/6-31G*). (iv) **Benzene basis warning**: CCSD(T)/aug-cc-pVTZ gives a spurious 495i cm⁻¹ b₂g puckering mode from near-linear dependence; h-aug-cc-pVTZ (diffuse on C only) is their fix — never use aug-cc-pVTZ for a PAH anchor. (v) Level B: basis quality matters more than correlation level; they recommend MP2/haTZ over CCSD(T)/DZ — supports a triple-ζ production DFT basis for our normal-mode basis. (vi) No multi-mode probing, no difference Hessian, no local CC.
- **Altun, Ghosh, Riplinger, Neese & Bistoni, J. Phys. Chem. A 125, 9932 (2021)** (item 44; open) — **read in full.** CPS(X/Y) extrapolation E = E_X + 1.5·(E_Y − E_X) with T_CutPNO = 10⁻ˣ, 10⁻ʸ, Y = X+1; DLPNO-CCSD(T)/TightPNO error on **acenes** (cc-pVDZ, absolute energies, vs canonical) grows linearly with ring count: at octacene 11.42 / 4.50 / 1.04 kcal/mol for 10⁻⁶ / 10⁻⁷ / CPS(6/7); error is positive (canonical approached from below); (T0) has its own size-dependent error, use iterative (T1); RI error negligible with a large /C basis; basis-set dependence of the local error small at 10⁻⁷ and CPS. **Use:** the threshold line's extrapolation form for our LNO code is the LNO-family analogue (Nagy & Kállay, JCTC 15, 5275 (2019), added to the reading list); the acene slope is the reason the threshold line is measured per rung; for the *difference* Δ₂ what matters is the geometry dependence of that error, which probe M1 measured directly (composite bias 0.03–0.36 cm⁻¹ at tight thresholds).
- **Esposito, Fortenberry, Boersma & Allamandola, J. Chem. Phys. 160, 211101 (2024)** (item 45; CC-BY) — **read in full.** (i) The "≈ 5 cm⁻¹" figure: **benzene only**, Table S1: B3LYP/N07D vs CCSD(T)-F12b/cc-pVTZ-F12 harmonic frequencies, MAD 5.45 cm⁻¹ (0.59 %). Not naphthalene; proposal Risk 4 corrected 2026-09-06. (ii) The PAHdb-Anharmonic method as practised: B3LYP/N07D, custom grid (200 radial, 974 angular), Gaussian 16 semi-diagonal quartic QFF by displacements along normal modes, VPT2 with 2-quanta resonance polyads in a modified SPECTRO; 3–20 µm accuracy vs experiment quoted as MAD 5–10 cm⁻¹ (their refs 21, 40–52); modes below 300 cm⁻¹ removed from the SPECTRO treatment; stick spectra convolved with a 20 cm⁻¹ FWHM Lorentzian. (iii) **Benzene is computed in D₂h** because the DFT code cannot use D₆h — degenerate modes split artificially. Consequence for decision 11: the symmetry prior must use the **full** point group from the deck's own analysis, not the Abelian labels a DFT code prints (patched in the Ladder and the proposal 2026-09-06). (iv) Overtone/combination region 1–3 µm needs 3-quanta states; not a plan-05 target.
- **Fusè, Mazzeo, Longhi, Abbate, Yang & Bloino, Spectrochim. Acta A 311, 123969 (2024)** (item 28; CC-BY) — **read in full (theory, protocol, template results).** Reduced-dimensionality VPT2: cubic and semi-diagonal quartic constants from numerical differentiation of analytic Hessians along a **subset of P active modes** (2P Hessians instead of 2N); a dimensionless indicator **ᾱ_i(j) = |f_iij / (4ω_j)|** ranks which modes must be added for the energy of state i; thresholds κ_E = 0.01 (close to full) and 0.005 (energies within 1 cm⁻¹ of the full treatment on their 75-mode template, fewer than 10 added modes per target state, up to 20 active modes for a fingerprint window); intensities converge less predictably — add the modes involved in 1-1 Darling–Dennison resonances (energy gap < 100 cm⁻¹, |C⁽²⁾| ≥ 0.3) as a second criterion; Fermi test gap < 200 cm⁻¹, energy 1 cm⁻¹, |C⁽¹⁾| ≥ 0.1; passive modes for large-amplitude motions; a full force field of their Ru complex would cost ≥ 445 harmonic Hessians. **Use:** this is the concrete route for the anharmonic DFT step at R3 and above (the largest R6 cost in the Budget): differentiate only along the scored modes and the ᾱ-selected partners, with the DDR test; the numbers κ_E and the resonance thresholds are candidates for the pilot note.

Reading list additions from these four: Nagy & Kállay, J. Chem. Theory Comput. 15, 5275 (2019) (LNO threshold extrapolation; DOI 10.1021/acs.jctc.9b00511 — **record verified and abstract read 2026-09-10**: "Approaching the Basis Set Limit of CCSD(T) Energies for Large Molecules with Local Natural Orbital Coupled-Cluster Methods"; the Loose / Normal / Tight threshold hierarchy; Normal within 0.2–0.3 (max 0.6–1.0) kcal/mol and Tight 0.1 (max 0.2–0.5) kcal/mol of CCSD(T) on reaction and interaction energies; CBS by extrapolation; ACS hybrid open access but bot-blocked to scripts — the user can download it (PDF request item 28)); Esselman et al., J. Am. Chem. Soc. 145, 21785 (2023) (benzene equilibrium structure and the ω₈ question; from CMA 2026 ref. 31 — **record verified and abstract read 2026-09-10**: Esselman, Zdanovskaia, Owen, Stanton, Woods & McMahon, "Precise Equilibrium Structure of Benzene", DOI 10.1021/jacs.3c03109; the abstract is about the r_e / r_e^SE structure from CCSD(T)/cc-pCV5Z with corrections, R_CC = 1.3913(1) Å, R_CH = 1.0809(1) Å; whether it carries the harmonic-frequency basis-set figure decision 26's input (ii) needs is not decidable from the abstract; closed; asked of the supervisor, item 27); Mackie et al., J. Chem. Phys. 143, 224314 (2015) (PAHdb anharmonic QFF spectra of naphthalene, anthracene, tetracene — the first of item 12's set; full reference from Esposito's ref. 21).


## Readings of 2026-09-06 — laboratory sources (module 03 preparation; author; full texts and scans from `Papers/`)

Purpose: before `m03_band_uncertainty.py` (probes README 2a) prints u_band, every laboratory
source it will quote has been read, and the numbers it will need are transcribed here with page
references so that 2a copies, not recalls. Every number below is transcribed from the paper
named; the few derived numbers are marked "author's arithmetic" and become binding only when 2a
prints them.

### R0 — Chu, Guenther, Rhoderick & Lafferty, J. Res. NIST 104, 59 (1999) (item 56)

- **Conditions.** Benzene-in-nitrogen samples, nine transmission spectra (three gravimetric
  concentrations × three path lengths); absorption coefficients corrected to **296 K and
  760.0 Torr** by the ideal-gas law (§2.3). Nominal resolution **0.12 cm⁻¹** (0.125 cm⁻¹),
  boxcar apodisation, zero-filling factor 2, detector-nonlinearity correction (§2.5).
- **Wavenumber scale.** Calibrated on 158 water-vapour lines against Toth's Kitt Peak list;
  RMS deviation after the linear correction **0.0042 cm⁻¹**, quoted by the authors as the standard
  uncertainty of the frequency (§2.4). This is the R0 position-calibration term.
- **Intensity.** Expanded relative uncertainty (k = 2) for benzene **3.3 %** for α > 10⁻⁴
  (Table 3; benzene has the largest B coefficient of the six compounds — "an effort is
  currently underway to improve the benzene results", §3.2). Detector nonlinearity contributes
  1 % (Table 4).
- **Not certified.** Absorption coefficients are **not certified where H₂O (1325–1900 and
  3550–3950 cm⁻¹), CO (2050–2225 cm⁻¹) and CO₂ (2295–2385 cm⁻¹) absorb** (§3.3).
  **Consequence for the R0 intensity scoreboard (decision 18):** the benzene e₁u C–C band near
  1480 cm⁻¹ lies in a non-certified region; its integrated intensity is scored only as a
  labelled non-certified column, the position is unaffected (the wavenumber calibration is
  global). The certified intensity families at benzene are therefore the C–H out-of-plane
  (≈ 673 cm⁻¹), the C–H in-plane (≈ 1038 cm⁻¹) and the C–H stretch (≈ 3050 cm⁻¹, outside
  the water region).

### R1 — Schneider et al., J. Quant. Spectrosc. Radiat. Transfer 323, 109045 (2024) (item 57)

- **Method.** Solids dissolved in a solvent and disseminated by a syringe pump into a metered N₂
  flow (disseminator-flow method), measured in a thermostatted **8.05 m White cell** at
  ambient pressure (748–766 Torr N₂), resolution **0.112 cm⁻¹**, 256 co-added scans; the
  solvent signature (CS₂ and/or CCl₄) is removed spectrally. **Naphthalene was analysed in CS₂
  only** (§3.2, Fig. 6 caption).
- **Units and temperature.** Composites are normalised to **1 ppm-m at 296 K, 1 atm**; the burden
  measured at the cell temperature is converted to 296 K by the temperature ratio (Eq. 3 and
  text). The cell temperature is stated as **25 °C** in the methods (§2.3, "White cell
  thermostatted at 25 °C"; dicyclopentadiene example "all at 25 °C") and as **50 °C** in the
  Fig. 6 caption ("Resultant composite spectra (50 °C)") and in the introduction ("quantitative
  50 °C gas-phase IR spectra for those compounds" — added 2026-09-06 after the cold read; it tilts the
  default towards 50 °C). The paper does not resolve this for
  naphthalene; **2a takes T_source from the header of the PNNL/HITRAN naphthalene record and
  prints which it found.** At 50 °C the temperature term is χ·27 K — with the pyrene 6–15 µm
  slopes of item 52 as the nearest measured stand-in (0.009–0.017 cm⁻¹ K⁻¹) that is
  0.25–0.5 cm⁻¹, well under τ; at 25 °C it is u_296 alone.
- **Intensity.** Systematic uncertainty **±8 % (2σ)** for the solids-flow composites (§3.3 and
  the conclusions; 7 % for the liquid disseminator alone). This is the R1 intensity-scoreboard
  uncertainty.
- **Naphthalene 6–15 µm temperature slopes are not measured anywhere in items 52/64** (Joblin
  1995 gives naphthalene at 3.3 µm only). The R1 hot WebBook columns therefore use pyrene's
  measured slopes as a labelled stand-in until item 53 (Pirali 2009) is read.

### R2/R3 hot gas — Joblin, d'Hendecourt, Léger & Défourneau, A&A 281, 923 (1994) (item 64)

- **Conditions.** Oven with diamond windows, **≈ 200 Torr N₂** bath, PAH working pressure
  ≈ 50 Torr, Bomem DA8, **1 cm⁻¹ resolution** (5 cm⁻¹ for gas-phase ovalene); pyrene at 570 K,
  coronene at 770 K, ovalene at 820 K; Ne matrix at 4.2 K (1:1000); solid in CsI pellets at
  300 K (§3.1). Purities: pyrene 99 %, coronene 97 %, ovalene 96 %. A contaminant band set
  (2947, 1265, 1080, 1021, 810 cm⁻¹) appears above 600 K and was subtracted (§3.2.1).
- **Positions (Table 2, coronene, cm⁻¹; gas 770 K / solid 300 K / Ne 4 K):**
  3.3 µm 3051, 3017 / 3050, 3018 / 3070, 3035; 5.3 µm 1894 / 1918, 1907, 1891 / 1926, 1913,
  1898; 5.6 µm 1790, 1770 / 1798, 1780 / 1810, 1800, 1787; 5.9 µm 1705, 1682, 1642 / 1715,
  1690, 1650 / 1720, 1697, 1658; 6.2 µm 1599 / 1615, 1608 / 1622, 1610, 1600; **7.6 µm 1308 /
  1314 / 1317**; **8.8 µm 1136 / 1136, 1125 / 1139, 1137**; **11.8 µm 848 / 848 / 857**;
  13.0 µm 767 / 770, 764 / 772, 769; 18.3 µm 545 / 550, 545, 543, 540 / 549.
  Pyrene (Table 1, gas 570 K / solid / Ne): 3.3 µm 3052 / 3048, 3030 / 3066, 3053; 6.2 µm
  1597 / 1597 / 1605; 7.0 µm 1432, 1305, 1240 / 1435, 1314, 1242 / 1437, 1311, 1244; 8.5 µm
  1183 / 1185 / 1185; 9.1 µm 1095 / 1096 / 1098; 11.9 µm 840 / 840 / 844; 13.5 µm 740 / 748 /
  745; 14.1 µm 710 / 710 / 712; 18.5 µm 541 / 542 / 542. The authors' summary (§3.2.2): shifts
  between the three phases vary band to band **but are below 1 %**; Ne is always blue of the
  hot gas, mostly a temperature effect (Paper II).
- **Integrated cross sections (Table 5, coronene gas 770 K, σΔλ in 10⁻²⁵ cm³; the only stated
  uncertainty is 20 % for the repeat of the 11.8 µm coronene band, §3.2.3):** 3.3 µm 29; 5.3 µm 7.2; 5.6 µm 5.3; 5.9 µm 7.3; 6.2 µm 8.8; 7.6 µm 29;
  8.8 µm 19; 11.8 µm 259; 13.0 µm 76; 18.3 µm 248. Pyrene gas 570 K (Table 4): 3.3 µm 22;
  6.2 µm 6.5; 7.0 µm 7.6; 8.5 µm 11; 9.1 µm 6.1; 11.9 µm 220; 13.5 µm 57; 14.1 µm 150;
  18.5 µm 22. Phase effects (§3.2.3): solid attenuates the C–H in-plane modes by ≈ 3, Ne
  attenuates the out-of-plane and C–C 16–18 µm modes by ≈ 5; the 6.2 and 7–8 µm C–C
  fundamentals are little affected. These are the only absolute gas-phase intensities at R2/R3;
  they are hot and ±20 %, so they enter as labelled columns, not as the intensity scoreboard of
  decision 18 (which stays R0/R1).

### R2/R3 temperature term — Joblin, Boissel, Léger, d'Hendecourt & Défourneau, A&A 299, 835 (1995) (item 52)

- **Conditions.** Same oven, 200 Torr N₂, type-K thermocouple **±0.5 K**, spectra every 50 K;
  Kirchhoff check (naphthalene absorption = emission at 420 K, Fig. 2). Positions read at the
  peak (P), at the half-maximum midpoint (H) or in the hole between two maxima (D).
- **Table 1 — linear fits ν(T) = ν_L(0) + χ′T (cm⁻¹, cm⁻¹ K⁻¹):**

  | molecule | band | ν_L(0) | χ′ |
  |---|---|---|---|
  | naphthalene | 3.3 µm (D) / (H) | 3066.9 / 3074.7 | −1.39e-2 / −2.01e-2 |
  | pyrene | 3.3 µm (P) / (H) | 3067.2 / 3062.9 | −2.84e-2 / −2.22e-2 |
  | pyrene | 8.5 µm (D) / (H) | 1187.5 / 1187.9 | −9.30e-3 / −1.00e-2 |
  | pyrene | 12 µm (P) / (H) | 846.5 / 847.6 | −1.43e-2 / −1.69e-2 |
  | coronene | 3.3 µm (P) / (H) | 3076.4 / 3077.2 | −3.28e-2 / −3.52e-2 |
  | coronene | 6.2 µm (P) / (H) | 1627.9 / 1635.1 | −3.82e-2 / −4.36e-2 |
  | coronene | 7.7 µm (P) / (H) | 1326.6 / 1325.9 | −2.24e-2 / −2.38e-2 |
  | coronene | 8.8 µm (H) | 1141.5 | −8.40e-3 |
  | coronene | 11.8 µm (P) / (H) | 860.3 / 865.0 | −1.61e-2 / −2.30e-2 |
  | ovalene | 3.3 µm (P) / (H) | 3081.9 / 3082.3 | −4.20e-2 / −4.90e-2 |

- **Table 2 — width fits Δν(T) = Δν_L(0) + χ″T:** naphthalene 3.3 µm 18.36, 3.53e-2; pyrene
  3.3 µm 5.30, 3.40e-2; pyrene 8.5 µm 7.92, 1.56e-2; coronene 3.3 µm −10.03, 4.18e-2; coronene
  7.7 µm 3.44, 1.22e-2; coronene 8.8 µm 5.77, 1.26e-2; ovalene 3.3 µm −7.69, 5.60e-2 (the
  6.2 µm coronene width is constant with T). Widths grow at least linearly; rotation
  contributes ∝ √T (§4.2). **These are the "drawn, not predicted" width inputs of decision 18
  for hot columns.**
- **Model (§4.1).** δ_i(T) = Σ_k X_ik n̄_k(T) with Bose occupations (Eqs. 3–5); for
  k_BT ≫ hcν_k this is linear, δ_i = (k_BT/hc) Σ X_ik/ν_k (Eq. 6), so the observed linearity
  means the shift is dominated by low-frequency modes (ν_k ≪ 700 cm⁻¹). Replacing the bath by one
  mean mode ν_m with constant X_im, the slope gives X_im/ν_m and the Ne position gives ν_i(0);
  **ν_m ≈ 303 cm⁻¹ for coronene and 221 cm⁻¹ for pyrene** (3.3 µm band). The linear intercept
  ν_L(0) is not the 0 K position: the Bose form saturates, so ν(0) lies below ν_L(0). Hot bands
  of the ν_i mode itself sit at 2X_ii ≈ −130 cm⁻¹·v_i for the C–H stretch (resolved), unresolved
  elsewhere.
- **Consequences for the Ladder's temperature term (recorded in the Ladder as a dated note
  of 2026-09-06):**
  1. The recalled χ_max = 0.03 cm⁻¹ K⁻¹ is **exceeded** by the coronene 6.2 µm band (−0.038 /
     −0.044) and by every 3.3 µm band of coronene and ovalene. Measured 6–15 µm slopes: 7.7 µm
     0.022–0.024; 8.5–8.8 µm 0.008–0.010; 11.8–12 µm 0.014–0.023; 6.2 µm 0.038–0.044. The
     pinned per-family χ_F replaces the single χ_max; where a family has no measured slope the
     largest measured slope in the 6–15 µm window (0.044) is the floor.
  2. **u_296 per family from the paper's own model (author's arithmetic, to be reprinted by
     2a):** with X_m = χ′·hcν_m/k_B and n̄_m(296 K), δ(296) − δ(0) = χ′·(hcν_m/k_B)·n̄_m(296):
     coronene (ν_m = 303 cm⁻¹ → 436 K, n̄ = 0.297) gives **130 K·|χ′|**: 6.2 µm 5.0–5.7,
     7.7 µm 2.9–3.1, 8.8 µm 1.1, 11.8 µm 2.1–3.0, 3.3 µm 4.3–4.6 cm⁻¹; pyrene (ν_m = 221 cm⁻¹
     → 318 K, n̄ = 0.519) gives **165 K·|χ′|**: 8.5 µm 1.5–1.7, 12 µm 2.4–2.8, 3.3 µm 3.7–4.7
     cm⁻¹. The linear bound |χ′|·296 K is 2–2.3× larger (coronene 6.2 µm 11–13 cm⁻¹). The
     recalled 5 cm⁻¹ at R2 covers the measured pyrene families; at R3 the 6.2 µm C–C family
     needs 5–6 (Bose) and the recalled value had no R3 entry. u_296 at naphthalene has no
     measured 6–15 µm input (only the 3.3 µm slope); 2a labels its stand-in.
  3. **Matrix residual, Ne minus ν_L(0)** (items 64/52): coronene 3.3 µm −6, 6.2 µm −6 (P),
     7.7 µm −10, 8.8 µm −2.5, 11.8 µm −3 to −8; pyrene 3.3 µm −1, 8.5 µm −2.5, 12 µm −2.5 to
     −3.6 cm⁻¹. Part of this is the Bose saturation (ν(0) below ν_L(0) by ≈ |χ′|·hcν_m/2k_B,
     ≈ 5 cm⁻¹ at coronene 7.7 µm), the rest is the Ne host. The PAHdb column is **Ar at 15 K**
     (item 4), a different host; the M03 matrix–gas gate measures |matrix − gas| on the PAHdb
     values directly, as written, and these Ne residuals are the expected order (2–10 cm⁻¹).

### R2/R3 cold gas — Lemmens et al., A&A 628, A130 (2019) (item 61) and Lemmens, Rijs & Buma, ApJ 923, 238 (2021) (item 62)

- **Method.** Laser-desorption jet, IR-UV ion-dip with FELIX (5–100 µm) and an OPO for
  2950–3150 cm⁻¹; **FELIX bandwidth 0.5–1 % of the IR frequency** (2021 §2; 2019 §2 quotes
  1 %), i.e. 6–13 cm⁻¹ at 1300 cm⁻¹ and 4–9 cm⁻¹ at 850 cm⁻¹; T_rot ≈ 2 K (2021).
  Predictions in the 2021 paper are convolved with a Gaussian of FWHM 1 % of the frequency.
- **Coronene, Table A1 (2021), exp cm⁻¹ (rel. int.):** 121.1 (0.004), 381.1 (0.03), 549.2
  (0.61), 770.1 (0.21), **854.6 (1.00)**, 1132.1 (0.19), 1208.1 (0.08), 1306.4 (0.35),
  1607.1 (0.23), 1694 (0.09), 1774.4 (0.09), 1902.8 (0.12). The 1694/1774/1903 bands are
  combination bands (their text). Tetracene (2019, Table A.2): ≈ 30 bands 548–1970 cm⁻¹, as
  recorded on 2026-09-05.
- **Cross-source check at coronene (cm⁻¹; hot = item 64 Table 2 at 770 K, Ne = item 64,
  cold = item 62, slope = item 52):**

  | band | hot 770 K | Ne 4 K | cold jet | cold − hot | linear thermal expectation (−χ′·770) | verdict |
  |---|---|---|---|---|---|---|
  | 18.3 µm | 545 | 549 | 549.2 | +4.2 | (no slope) | cold between hot and Ne |
  | 13.0 µm | 767 | 772 | 770.1 | +3.1 | (no slope) | cold between hot and Ne |
  | 11.8 µm | 848 | 857 | 854.6 | +6.6 | +12 to +18 | cold between hot and Ne |
  | 8.8 µm | 1136 | 1139 | 1132.1 | **−3.9** | +6.5 | **cold below hot** |
  | 7.7 µm | 1308 | 1317 | 1306.4 | **−1.6** | +17 to +18 | **cold below hot** |
  | 6.2 µm | 1599 | 1610 / 1622 | 1607.1 | +8.1 | +29 to +34 | cold between hot and Ne |

  The out-of-plane and low-frequency families behave as the temperature model says; the
  7.7 and 8.8 µm families do not — the cold value sits 10–19 cm⁻¹ from where the slope table
  puts a cold band, of the order of the FEL bandwidth there (6–13 cm⁻¹). **Consequence (as first
  written 2026-09-06):** the R3 cold column carries the larger of the FEL bandwidth and this
  disagreement as its resolution term and its 7.7 and 8.8 µm families are inconclusive by
  measurement. **Superseded 2026-09-08 (decision 24, P16)** after the proposal cold read's
  objection that a linear hot-band extrapolation over several hundred kelvin is the weaker
  witness: the jet-cooled band is the primary cold column with the FEL bandwidth as its
  uncertainty, the hot-extrapolated position a second labelled column, and a family is
  inconclusive only when the two columns disagree on the verdict; the disagreement itself is
  printed beside both.
- 2021 also reports that Gaussian's GVPT2 gave unrealistic C–H out-of-plane shifts for the
  larger PAHs of that paper (their §3): a known failure mode our resonance treatment at R3+
  must not reproduce; the 121 cm⁻¹ drumhead mode is 4 % off anharmonically and 1 % off
  harmonically (shallow potential).

### Matrix scoreboard — Mattioda et al., ApJS 251, 22 (2020) (item 4)

- **Conditions.** Ar:PAH > 1000:1 co-deposited on a CsI window at **15 ± 3 K** (Appendix A),
  10⁻⁷–10⁻⁸ Torr; FTIR at **0.5 cm⁻¹**, 250–500 scans; purity ≥ 99 % (§2.1). Detection limit
  ≈ 5 km mol⁻¹ (older instrument) and ≈ 2 km mol⁻¹ (since the early 2000s) (§2.2).
- **Positions.** Isolated bands at the apex; discernible members of complexes integrated
  separately; undiscernible complexes (often the C–H stretch region) integrated whole and
  reported at the strongest peak (§2.3) — so the C–H stretch column is a family centroid, not a
  mode.
- **Intensities are not theory-independent.** The column density is fixed by scaling the sum
  of measured integrated absorbances over **1550–500 cm⁻¹** to the sum of the computed
  A-values of the same molecule in PAHdb's computed library ("their sum is generally accurate
  to within 10–20 %", Eq. 8, §2.3); the C–H stretch (> 1550) and the far-IR (< 500) are excluded
  from the sum. Pre-2000 publications reported relative intensities only; the A-values now in
  the database were derived later and exist only there. **Consequence for decision 18:** the
  matrix column can score **relative** intensities within 500–1550 cm⁻¹ only, and never an
  absolute intensity; the absolute intensity scoreboard stays R0/R1 (items 56, 57), exactly as
  decided. The 15 cm⁻¹ emission red-shift convention is mentioned as customary and questioned
  (Mackie et al. 2018) — irrelevant to absorption scoring, recorded so it is never applied.
- Ion spectra (photolysis, 20 % conversion, anion/cation split 50–50 when both are seen) are
  outside the neutral scope of the Ladder.

### What this closes and what stays open

- Closed: the temperature term's pinned reference (items 52, 64) — the recalled χ_max and
  u_296 are replaced by the table above through the Ladder's dated note of 2026-09-06; the R0
  and R1 series conditions (items 56, 57) that R0/R1 "unconditional" rests on; the matrix
  column's intensity status (item 4).
- Open: item 53 (Pirali 2009, naphthalene hot bands) for a naphthalene 6–15 µm slope; item 59
  (Sharpe 2004) for the PNNL series documentation, which should settle the 25 °C / 50 °C
  question if the record header does not; item 63 (Brumfield 2012) for the single cold pyrene
  band origin. All three are on the supervisor's list.

## Readings of 2026-09-08 — the thirteen PDFs from the supervisor (author; texts extracted from the publisher PDFs in `Papers/`)

Requested on 2026-09-06 (`PDF_Request_2026-09-06.md`), received 2026-09-08, renamed to the
convention and read the same day. Five were read in full (Sharpe, Pirali, Brumfield, Lahm, Bégué);
the eight method and matrix papers were read for their abstracts, the sections the plan leans on,
and their conclusions, and the status cells say which. Per paper: what it says, and **whether it
changes the plan**.

### Changes the plan (two dated notes, one new proposal)

- **Pirali, Vervloet, Mulas, Malloci & Joblin, PCCP 11, 3443 (2009)** (item 53) — **read in full.**
  Gas-phase naphthalene at **300 K**, 0.1 mbar flowing through an 8 m White cell, Bruker IFS 125
  at **0.005 cm⁻¹**, 48 h acquisitions (50–500 cm⁻¹ with a bolometer, 500–3500 cm⁻¹ with MCT).
  Rotational structure is never resolved; positions are the **heads of the Q branches**. Table 1,
  experimental fundamentals (cm⁻¹): b1u ν20 1392.5, ν21 1268.0, ν22 1130, ν24 358.7; b2u ν29 3057,
  ν30 3042, ν31 1514.3, ν32 1361.1, ν33 1210.2, ν34 1135.5, ν35 1011.89, ν36 619.5; b3u ν45 959.04,
  ν46 782.33, ν47 473.33, ν48 166.4 (the calculated column is Cané et al.'s B971/TZ2P anharmonic
  set, e.g. 1388.4 / 1265.2 / 1130.5 / 358.7 / 3048.1 / 2989.9 / 1504.3 / 1357.9 / 1209.8 / 1144.2 /
  1012.1 / 623.7 / 958.9 / 783.4 / 473.2 / 166.4). The c-type (b3u, out-of-plane) bands show sharp Q
  branches in which **the fundamental is resolved from its hot-band sequences** (up to four quanta
  of ν48 at 166 cm⁻¹ and of the IR-inactive ν13 at ≈ 195 cm⁻¹ are populated at 300 K; sequence
  spacing 0.3 cm⁻¹ measured, 0.4 modelled for ν46 + nν48). Table 2, effective anharmonic constants
  from the spectrum (the extracted text lost the minus signs; values without an explicit plus are
  negative in the paper's convention, to be re-checked on the page before 2a copies them): x46,48
  0.3, x46,13 +0.58, x46,16 2.3, x45,48 0.29, x45,13 0.46, x45,16 2.3, x45,28 +0.4, x45,47 1.1, x47,47
  +0.9 cm⁻¹. Statements the plan uses: "typically a redshift of 2 × 10⁻² cm⁻¹ K⁻¹ is observed for
  the CH stretch modes" (their refs 9, 18); "the well-known temperature-dependent shifts seen in band
  positions measured at low resolution are accounted for by anharmonic hot-band structure"; the
  hot-band structure "accounts almost entirely for the apparent width of unresolved Q branches";
  Cané's anharmonic constants predict 1 ← 0 transitions "with an accuracy better than 5 cm⁻¹ in the
  full IR range"; the CH-stretch group is predicted ≈ 15 cm⁻¹ below experiment; the model's own
  accuracy for a single hot-band position is ≈ 0.5 cm⁻¹. A 373 K low-resolution (1 cm⁻¹) spectrum
  from Joblin's thesis is used for the overview figures. **Why it changes the plan:** the
  temperature term u_296 in the Ladder models the 0 → 296 K *shift of a band*; Pirali shows that at
  300 K the fundamental of a c-type band does not move — the envelope acquires hot-band satellites
  around a fundamental that stays put, and at 0.005 cm⁻¹ the fundamental's Q head is read directly.
  For the sixteen fundamentals of Table 1 there is therefore an R1 gas-phase position source whose
  temperature term is not a shift at all. Named today as an R1 column (Ladder dated note
  2026-09-08); **its u_T treatment is proposal P11** below, because it changes how a class of
  sources is scored.
- **Pinski & Neese, JCP 148, 031101 (2018) and JCP 150, 164102 (2019)** (item 51) — abstracts,
  Lagrangian sections, the localisation passage and the conclusions read. (i) The DLPNO-MP2
  gradient needs constraints for PNO relaxation; "omitting PNO-specific constraints can lead to
  dramatic errors for orbital-relaxed properties" (2018). (ii) **"Localized molecular orbitals of
  systems belonging to various symmetry groups may be subject to continuous degeneracies"** —
  benzene's π orbitals under Pipek–Mezey are the named case — which makes the coupled-perturbed
  localisation equations singular; they modify the localisation constraint in the Lagrangian, and
  note this "is of general relevance for derivatives of local correlation methods" (2019,
  conclusions; their §II cites Werner & Pflüger's domain merging for benzene and Toyota/Nakatsuji's
  minimum orbital-deformation mapping of reference orbitals onto perturbed geometries). (iii)
  "Discontinuities of the potential energy surface represent a well-known problem of local
  correlation methods" (ref. 136, Russ & Crawford 2004); remedies: **domain freezing or domain
  merging (Werner and co-workers, ref. 137: Mata & Werner 2006)** and smoothing functions in the
  residual equations (ref. 138, Subotnik & Head-Gordon 2005); with default thresholds "small
  discontinuities are still present … usually on a scale of several µE_h and can be systematically
  reduced with tighter thresholds"; a 14 µE_h discontinuity at a hydrogen-bond minimum came from
  auxiliary-domain reassignment, a 0.35 mE_h one from PAO-domain reassignment at loose thresholds.
  **Why it changes the plan:** (a) the novelty table's fourth row named ORCA's fixed domains and
  Madriaga & Crawford as the nearest work; **freezing domains along a surface is 2006 prior art**
  (item 67) and is now named there — the unclaimed part is the transported, semicanonicalised LNO
  object for a Δ-recovery, measured against canonical CC; (b) the side project's M2 gradient must
  handle the continuous PM degeneracy on the D₆h rungs explicitly (M1 §2.4 measured the arbitrary
  landing; Pinski & Neese give the remedy) — added to the side project's risks; (c) the
  "several µE_h" figure is the same class as M1's 7–11 µE_h (normal) and 0.05–3.4 µE_h (tight)
  for the re-selecting arms — a published anchor for what M1 measured.

### Confirms the plan, adds numbers (statuses updated; no rule changes)

- **Sharpe, Johnson, Sams, Chu, Rhoderick & Johnson, Appl. Spectrosc. 58, 1452 (2004)** (item 59)
  — **read in full.** PNNL: Bruker IFS 66v/S, **0.112 cm⁻¹** boxcar, 19.94 / 19.96 cm gold-plated
  thermostatted single-pass cell, sample 0.1–13 kPa backfilled with UHP N₂ to **760 ± 5 Torr**,
  sample temperatures **5, 25 and 50 °C (all ± 1 °C)**, typically twelve burdens at 25 °C and six
  each at 5 and 50 °C; wavenumber calibration on 165 CO / N₂O lines, RMS **0.0018 cm⁻¹**
  (NIST: 158 water lines, 0.0042 cm⁻¹); positional uncertainty ≤ 0.005 cm⁻¹; statistical 1σ
  < 2 %, systematic (Table III: path 0.5 %, temperature 0.2 %, pressure 0.1 %, baseline 0.2 %,
  MCT nonlinearity 1 %) **2.3 % at 2σ**; NIST–PNNL cross-comparison of 26 bands of 12 compounds,
  benzene among them, RMS 1.66 %, mean −0.63 %. NIST measured at **23 °C** (Table II), data
  corrected to 296 K and offered at 25 °C only; PNNL data offered at 5 / 25 / 50 °C "when chemical
  properties are amenable", **each record with a metadata PDF describing sample conditions**.
  Sample emission is not corrected in either library: below ≈ 1100 cm⁻¹ it raises apparent cross
  sections by 0.4 % (methanol) to 0.9 % (SO₂) at 25 °C and 1.0–1.8 % at 50 °C (their ref. 36).
  **Consequence:** 2a takes the naphthalene record's temperature from its own metadata PDF (the
  2004 static cell is not the 2024 solids-flow White cell, so the 2004 paper cannot settle
  Schneider's 25 / 50 °C); the PNNL wavenumber term is 0.0018 cm⁻¹; the R0 intensity rows below
  1100 cm⁻¹ (the 673 cm⁻¹ C–H out-of-plane band) carry the uncorrected-emission caveat as a
  labelled ≤ 1 % systematic.
- **Brumfield, Stewart & McCall, J. Phys. Chem. Lett. 3, 1985 (2012)** (item 63) — **read in
  full.** Pyrene ν68 (B3u; C–H in-plane bend with in-plane motion of the two central carbons),
  quantum-cascade-laser cavity ring-down, Ar slit-jet expansion from a 420 K oven, 6 mm downstream;
  1182.77–1185.06 cm⁻¹ recorded; calibration 0.00049 cm⁻¹ on SO₂; line width 0.0004 cm⁻¹; 694
  lines (2,222 transitions) fitted, residual SD 0.00053 cm⁻¹; **band origin ν₀ = 1184.035595(20)
  cm⁻¹**; ground-state A, B, C = 0.03372547(66), 0.01855623(43), 0.01197350(33) cm⁻¹, changing by
  −0.013 %, +0.0006 %, −0.015 % on excitation, no centrifugal-distortion constants needed;
  T_rot ≈ 23 K; Q_vib = 1.41 ± 0.17, i.e. **T_vib ≤ 111 K (3σ)**; matrix-vs-gas shifts "on the order
  of several wavenumbers" cited as the reason such data are needed. **Use:** exactly what the
  Ladder's 2026-09-05 note assigned — one cold band origin for the R2 pyrene C–H in-plane family,
  a one-line check; 2a scores it with u_band = 0.0005 cm⁻¹ and class "cold, resolved".
- **Lahm, Kitzmiller, Mull, Allen & Schaefer, J. Am. Chem. Soc. 144, 23271 (2022)** (item 42) —
  **read in full.** CMA: high-level force constants in the basis of **internal-coordinate**
  concordant normal modes from a lower level (nc = natural internal coordinates, dc = delocalised);
  1,581 CCSD(T)/cc-pVTZ frequencies of 122 G2 molecules; raw Level-B errors MAD 10–11 cm⁻¹, range
  −109 to +194; CMA-0A(nc) **MAD 0.16–0.23 cm⁻¹, SD < 0.5**, > 99 % of frequencies within 1.5 cm⁻¹;
  outliers > 2.5 cm⁻¹: seven (CCSD(T)/cc-pVDZ modes) and three (B3LYP/6-31G(2df,p) modes), "most …
  involving aromatic rings" — benzene ω5(b1g) ring deformation 1001.2 cm⁻¹ **+4.6**, pyridine,
  pyrrole, furan ring deformations 2.9–3.4, benzene ring puckering 674.7 **+3.4** (B3LYP modes) —
  each repaired to ≤ 1.1 cm⁻¹ by one CMA-1A(1) coupling; speed-up 7–10×; cyclopentene at
  CCSD(T)/cc-pV5Z every frequency within 1.0 cm⁻¹ at 1/7 the cost. Two remarks that matter to us:
  "a subtle dependence on the internal coordinates (S) chosen … arises whenever some elements of
  F_CMA are ultimately dropped" — our Δ₂ lives in the DFT Cartesian normal-mode basis and drops
  elements by the symmetry prior, so the same caveat applies and is what the dry run's ρ measures;
  and aromatic-ring deformations are "pathologically sensitive to the atomic-orbital basis set"
  (their ref. 10) — the same family the CMA 2026 paper and our rehearsal flagged. Confirms the
  diagonal-first premise and the ring-mode caveat; no rule changes.
- **Bégué, Carbonnière & Pouchan, J. Phys. Chem. A 109, 4611 (2005)** (item 27) — **read in
  full.** Acetonitrile: quadratic constants at CCSD(T)/cc-pVTZ (49-point grid in symmetry
  coordinates), cubic and quartic at B3LYP/cc-pVTZ **expressed in the CCSD(T) dimensionless normal
  coordinates** (117 B3LYP energy+gradient points, 358 parameters), variational vibrational
  treatment; 31 observed fundamentals and overtones in 300–3200 cm⁻¹, **mean absolute deviation
  < 0.8 %** (conclusions: "within an average error of 15 cm⁻¹"); a full CCSD(T) quartic field from
  717 energies gives "very similar" transitions; the hybrid is a factor 10 cheaper. The
  harmonic-first precedent is thus confirmed on a six-atom molecule; the proposal's "Bégué's full
  text is unread" is removed.
- **Hudgins & Sandford, J. Phys. Chem. A 102, 329 (1998)** (item 8) — abstract, methods,
  conclusions read. Ar matrix at **10 K**, Ar:PAH 1200:1 for naphthalene, **resolution 0.9 cm⁻¹**
  with 0.23 cm⁻¹ sampling, 5 × 200 scans; band strengths integrated with baseline choice as the
  stated uncertainty; relative intensities normalised to the 783.4 cm⁻¹ naphthalene band; matrix
  positions "typically undergo only small shifts in the 0–15 cm⁻¹ range relative to their gas-phase
  values"; against scaled B3LYP/4-31G (Langhoff 1996) positions "typically match to within 5 cm⁻¹,
  with the worst mismatches usually no more than 15 cm⁻¹", strong-band intensities to 35 %, weak
  bands to a factor 2–3, CH stretches computed 2× too strong. **Consequence:** the matrix
  scoreboard's resolution term is **per species from its original paper** — 0.9 cm⁻¹ for the eight
  1998 species (naphthalene, anthracene, phenanthrene, benz[a]anthracene, chrysene, pyrene,
  tetracene, triphenylene), 0.5 cm⁻¹ where item 4's later setup applies; the 0–15 cm⁻¹ statement is
  the published order of the matrix–gas gate, which M03 still measures.
- **Riplinger & Neese, JCP 138, 034106 (2013); Riplinger, Sandhoefer, Hansen & Neese, JCP 139,
  134101 (2013); Riplinger, Pinski, Becker, Valeev & Neese, JCP 144, 024109 (2016)** (item 66) —
  headers, threshold sections, conclusions read. Defaults T_CutPNO = 3.33 × 10⁻⁷, T_CutPairs = 10⁻⁴,
  T_CutMKN = 10⁻³; conservative PAO domains recovering > 99.9 % of the correlation energy;
  **(T) is semicanonical (T0) with a TNO cut-off, and at the default PNO thresholds at most 96–97 %
  of the semicanonical triples energy (91–94 % of the canonical triples) is recoverable**; the 2016
  sparse-map redesign is linear scaling and up to 7× faster. **Bearing on us:** the composite
  energy corrects the MP2-level truncation, not the triples truncation; a cheap diagnostic for the
  next M1 variant is to print arm A's bias split into its CCSD and (T) parts (pyscf-forge exposes
  both), which says whether the residual curvature bias sits in the triples. Not a plan change; a
  diagnostic worth adding when the xtight run is read.
- **Ruth, Gerbig & Schreiner, J. Chem. Theory Comput. 18, 4846 (2022)** (item 37) — abstract and
  conclusions read. Graph-neural-network Δ-learning of the (T) increment E[CCSD(T)] − E[CCSD] for
  small organic molecules at cc-pVDZ, aug-cc-pVDZ and cc-pVTZ: MAE 0.25 / 0.25 / 0.28 kcal mol⁻¹,
  R² ≈ 0.998; thermochemistry, no force constants or frequencies. Its place in the novelty table
  (learning a CC increment per system) is unchanged.
- **Reiher & Neugebauer, J. Chem. Phys. 118, 1634 (2003)** (item 46) — **read in full.**
  Mode-tracking: a Davidson-type subspace iteration on the mass-weighted Hessian in which each
  σ-vector is a numerical derivative of the analytic gradient along a collective displacement; a
  few pre-selected vibrations are converged without the full Hessian; convergence "strongly
  depends on the reliability of the initial guess" (they use semi-empirical guesses for DFT
  targets) — and the conclusions state the pattern our side project uses: a cheaper method's guess
  "for subsequent computer-resource-demanding ab initio correlation methods like the popular
  coupled cluster model CCSD(T)". **Bearing on us:** prior art for "selected high-level modes from
  gradients started from a cheap guess" — named as a sixth row of the novelty table; what differs is
  that we recover the *correction* to the whole force-constant matrix from energies, with a
  symmetry prior and a measured probe count, rather than converge selected eigenvectors.

### P11 (new, 2026-09-08, from Pirali 2009) — how a resolved room-temperature fundamental is scored

The Ladder's temperature term treats every room-temperature source alike: u_T ≥ u_296, the modelled
0 → 296 K shift of the band. Pirali's spectrum separates the fundamental Q head from its hot bands
at 0.005 cm⁻¹, so for those sixteen naphthalene fundamentals the quantity the pipeline predicts (the
0 → 1 transition) is read directly and does not shift with temperature; what remains is the offset
between a Q-branch head and the band origin, which Pirali's figures put inside a Q-branch width of a
few tenths of a wavenumber, and the fact that the fundamentals of a-/b-type bands were read at lower
signal-to-noise. **Proposal:** 2a adds a source class "gas, room temperature, **resolved
fundamental**" with u_T = 0 and a head-to-origin term of 0.5 cm⁻¹ (an upper bound read from
Pirali's Fig. 3–6 Q-branch widths, labelled as such until a digitised spectrum lets 2a measure it),
so that u_band(R1) on this column is ≈ 0.5 cm⁻¹ for the c-type family and the same, with a larger
centroid term, for the others; the PNNL column keeps the Ladder's floor. Options: (a) as proposed;
(b) keep u_T = u_296 for every room-temperature source (over-penalises a resolved fundamental by
the very quantity Pirali shows is absent); (c) score Pirali's column but only as a check, not as a
scoreboard. **Decided 2026-09-08 (user): (a) — decision 21**; written into the Ladder's dated note of
2026-09-08 and probes README 2a.


### Readings of 2026-09-10 — the PAHdb scale factors (Module 02 atlas)

- **Ricca et al. 2026, ApJS 282, 7 (item 1, v4.00), IOP full text re-read:** "all spectra were computed using
  the larger basis set 6-31G*"; "harmonic frequencies were scaled using three scaling factors, namely,
  0.964 for C–H stretches around 3 μm, 0.979 for bands between 4 and 9 μm, and 0.975 for bands beyond
  9 μm", "obtained by fitting the theoretical data to 25 bands obtained from gas-phase PAH laboratory
  experiments, which included 17 IR allowed bands and one A_u, one B_1g, two B_2g, and four A_g bands
  (Behlen & Rice 1981; Cané et al. 1996; Pirali et al. 2009)"; no uncertainties; v3.20 and the clusters
  at 4-31G with a single 0.958; §6: systematic uncertainties "currently unquantified".
- **Bauschlicher, Ricca, Boersma & Allamandola 2018, ApJS 234, 32 (v3.00), IOP full text read for
  Table 2:** regions 0–1111.1 / 1111.1–2500 / > 2500 cm⁻¹; B3LYP/4-31G 0.956 / 0.952 / 0.960;
  B3LYP/6-31G* 0.979 / 0.969 / 0.960; B3LYP/6-31G** 0.979 / 0.973 / 0.961; fitted to Pirali 2009's 17
  allowed bands, Behlen 1981's 4 A_g + 2 B_2g and Cané 1998's A_u + B_1g (gas-phase naphthalene).
- **Finding:** the served v4.00 XML stores the v3.00 factors at four decimals (0.9794 / 0.9691 / 0.9597;
  4-31G 0.9563 / 0.9523 / 0.9595) with the v3.00 regions — the v4.00 refit is described in the paper
  but not applied in the file (Frozen_Lines §2 dated note; atlas note §2; **P22**).
