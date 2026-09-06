# Inventory of the PDFs that were committed under `Papers/` — 6 September 2026

**Why this file exists.** On 6 September 2026 it was found that 37 PDFs had been committed to this
public repository (36 in commit b28644b of 25 August 2026, one in 23c5c74 of 29 August). They were
removed from version control the same day (commit 8c06bc7; `Papers/` is now git-ignored and the
local copies are kept), but they remain in the repository's **history** and are retrievable from
GitHub through the old commits. This inventory classifies each file by its source, so the decision
whether to rewrite the history (step 2) can be taken on facts. Classification is from each file's
first two pages and metadata (arXiv stamp, publisher typesetting, copyright and licence notices).

## A. Publisher PDFs of subscription journals, or personal-use-only — redistribution not permitted

| # | file | journal | evidence |
|---|---|---|---|
| 08 | 08_ApJ2020_HighThroughputPAH.pdf | ApJ 2020 (Kovács et al.), DOI 10.3847/1538-4357/abb5b6 | IOP typesetting, "© 2020"; AAS journals were subscription until 2022 |
| 09 | 09_Zhu2021_PAH_EmpiricalMapping.pdf | ApJ 2021 (Meng et al.), DOI 10.3847/1538-4357/ac2c78 | IOP typesetting, "© 2021" |
| 11 | 11_Zakuskin2025_PAH_ChargeModels.pdf | J. Chem. Inf. Model. 2025, DOI 10.1021/acs.jcim.5c00372 | "© 2025 American Chemical Society" |
| 13 | 13_Fortenberry2025_CN_PAHs.pdf | ACS Earth Space Chem. 2026, DOI 10.1021/acsearthspacechem.5c00249 | "© 2025 American Chemical Society" |
| 18 | 18_Boersma2014_PAHdb.pdf | ApJS 211, 8 (2014) | "© 2014 The American Astronomical Society. All rights reserved." |
| 37 | 37_the_hydrogen_molecular_ion_revisited.pdf | J. Chem. Educ. 2002 (Grivet) | "may be downloaded for personal use only" (encrypted PDF) |

## B. Publisher PDF, licence not established from the file

| # | file | journal | evidence |
|---|---|---|---|
| 10 | 10_Meng2023_PAH_Charges_OUP.pdf | MNRAS Lett. 525, L29 (2023), DOI 10.1093/mnrasl/slad089 | OUP typesetting, "© 2023 The Author(s) Published by Oxford University Press"; no CC line found in the first two pages — treat as A until shown otherwise |

## C. Open access at the publisher (CC licence or fully open journal) — redistribution permitted with attribution

| # | file | licence evidence |
|---|---|---|
| 01 | 01_Ramakrishnan2014_QM9.pdf | Scientific Data (fully open, CC BY) |
| 12 | 12_Mai2025_MLMD_PAHs.pdf | "Open Access ... Creative Commons Attribution License" |
| 14 | 14_ACSomega2025_DFT_Scaling.pdf | ACS Omega (fully open) |
| 15a | 15a_AA2026_JWST_Study1.pdf | A&A 2026, "© The Authors" (A&A is open access) |
| 15b | 15b_AA2026_JWST_Study2.pdf | A&A 2026, "© The Authors" |
| 30 | 30_Sylvetsky2020_LocalCC_Porphyrins.pdf | "Creative Commons Attribution (CC-BY) License" |

## D. Preprints and author manuscripts (arXiv, conference, Distill, ChemRxiv-style) — freely redistributable

02 SchNet; 03 Gastegger 2017 (arXiv:1705.05907); 04 Käser 2021 (arXiv:2103.05491); 05 Dral 2025
(preprint); 06 NequIP; 07 NewtonNet; 16 FNO (ICLR 2021); 17 Jin 2026; 19 Mordvintsev 2020 (Distill);
20 Aitomia (preprint); 21 Snyder 2012 (arXiv:1112.5441); 22 Brockherde 2017; 23 Li 2021
(arXiv:2009.08551); 24 Zhang 2024 (arXiv:2309.16578); 26 Kotaru 2026 (arXiv); 27 Käser 2021
(arXiv:2109.08407); 28 Käser 2023; 29 Kumar 2020 (SI, arXiv); 31 Tang 2025 (arXiv:2504.11898); 32 Ji
2025 DetaNet (preprint); 33 Chen 2026 (A&A manuscript); 34 MACE; 35 MACE-OFF; 36 MACE-POLAR-1.

## What step 2 would involve

Rewriting the history so that the seven files of A and B never existed there (`git filter-repo
--invert-paths` on those seven paths, or on all of `Papers/`), then a forced push. Consequences:
every commit hash after 25 August 2026 changes (the plan's notes cite about a dozen of them; they
would be updated from the commit map the tool writes); anyone holding a clone must re-clone (as of
6 September nobody outside the author is known to); GitHub may keep the old objects reachable
until its support is asked to run garbage collection, so a request to GitHub support is part of the
step. Cost: about an hour, once. Alternative without rewrite: none that removes the files from the
public history.

## Step 2 — done on 6 September 2026

History rewritten with `git filter-repo --invert-paths --path-glob '*.pdf' --path-glob '*/Papers/*' --path Papers/`
(two passes: the files had also lived under `GoalGathering/Papers/` in earlier commits), then a forced
push of `master`. Result: no PDF in any commit (`git rev-list --objects --all | grep -i '\.pdf$'` is
empty); pack size 89.5 → 10.2 MB. Every commit hash after 25 August 2026 changed; the three hashes
the documents cited were updated from the commit subjects (21d937a → see M1 note; 4872efb → see M1
note; 800f3aa → see plan-02 history note). A full pre-rewrite bundle is kept outside the repository
(`../CapstonePlan_backup/pre-filter-2026-09-06.bundle`). Still to do: ask GitHub support to run
garbage collection so that the old commits stop resolving by hash; until then the old objects may
remain fetchable by anyone who already knows a hash.
