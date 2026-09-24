# Module 06 dataset — fused-aromatic SMILES from PubChem (frozen 2026-09-24)

**Source.** PubChem (public domain; NIH/NLM), through PUG-REST on 2026-09-24: for each core below, `fastsubstructure/smiles/<core>/cids` with
MaxRecords = 50000; the union of CIDs; properties `ConnectivitySMILES, MolecularFormula, HeavyAtomCount, Charge, IsotopeAtomCount` in
batches of 500. Cores: naphthalene (`c1ccc2ccccc2c1`), quinoline (`c1ccc2ncccc2c1`), isoquinoline (`c1ccc2cnccc2c1`), indole (`c1ccc2[nH]ccc2c1`), benzofuran (`c1ccc2occc2c1`), benzothiophene (`c1ccc2sccc2c1`), quinoxaline (`c1ccc2nccnc2c1`), benzimidazole (`c1ccc2[nH]cnc2c1`), azulene (`c1ccc2cccc-2cc1`). Raw responses are cached in `cache/` (not committed; the CSV is the frozen dataset).

**Filters (RDKit 2026.03.6).** parses; neutral (PubChem charge 0, no charged atom); elements within C H N O S F Cl; heavy atoms ≤ 30; no isotopes;
at least two aromatic rings that share an atom (fused); one row per canonical SMILES.

| step | molecules |
|---|---|
| union of the core searches | 404,877 |
| with properties returned | 404,877 |
| parsed by RDKit | 404,853 |
| neutral | 379,381 |
| elements within C H N O S F Cl | 355,757 |
| ≤ 30 heavy atoms | 174,198 |
| no isotopes | 173,958 |
| ≥ 2 fused aromatic rings | 167,805 |
| **unique canonical SMILES (the dataset)** | **160,972** |

**File.** `pubchem_aromatics_2026-09-24.csv` — columns `cid, smiles, formula, n_heavy, n_arom_rings, cores`; SHA-256 `c7fe9e9e2932da0d187f3b271afbffa8227a1707cc2b8dd6f7c163880564fd88`.

**Rubric statement.** Publicly available before this module started (PubChem, deposited records), appropriate for academic use, real deposited chemistry —
not synthetic, not AI-generated — and not the dataset of modules 02 (PAHdb computed library), 03 (PAHdb laboratory bands), 04 (matched pairs) or
05 (Hessian QM9 and the project's own corpus). The core list biases the sample toward fused aromatics on purpose (the atlas's domain); the bias is
reported in the module's ethics section. Retrieval took 1166 s.

**Committed form.** The CSV (12.8 MB) is committed as two gzip parts, each with the header: `pubchem_aromatics_2026-09-24.part1.csv.gz` and
`.part2.csv.gz` (the repository's pre-commit hook refuses files above 1.5 MB). Reassemble with
`python -c "import gzip,glob; parts=sorted(glob.glob('pubchem_aromatics_2026-09-24.part*.csv.gz')); out=open('pubchem_aromatics_2026-09-24.csv','w',encoding='utf-8',newline='');
[out.write(gzip.open(p,'rt',encoding='utf-8').read() if i==0 else ''.join(gzip.open(p,'rt',encoding='utf-8').readlines()[1:])) for i,p in enumerate(parts)]"` and check the SHA-256 above.
