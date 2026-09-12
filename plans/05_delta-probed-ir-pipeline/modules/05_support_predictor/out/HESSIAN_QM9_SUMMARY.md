# Hessian QM9 — inventory of the download — 2026-09-12 09:28

Record: <b>Hessian QM9 Dataset</b> — DOI 10.6084/m9.figshare.26363959.v4 (version 4, CC0, published 2024-12-12); paper Williams et al., Scientific Data 12 (2025), DOI 10.1038/s41597-024-04361-2. Downloaded 2026-09-12 with the user's permission.

Archive `hessian_qm9_DatasetDict.zip`: 6,281,831,499 bytes; md5 `f3e36130e5cc47021ab403767a19ddf7` (matches figshare); sha256 `ce595041d718b2dff8c5b5a2b4ce7cfcef3c3f98035193d2612db6ea3d17b2c7`. Splits in the archive: vacuum, thf, toluene, water (9.47 GB unpacked); **only `vacuum/` extracted** (2.37 GB, 5 Arrow stream shards).

**Vacuum split: 41,645 molecules.** Schema: energy, positions, atomic_numbers, forces, frequencies, normal_modes, hessian, label. Example `dsgdb9nsd_045682`: 18 atoms, hessian [18, 3, 18, 3] (symmetric: True), frequencies [54, 2], normal_modes [54, 54].

Heavy atoms per molecule: 1: 2, 2: 2, 3: 1, 4: 11, 5: 51, 6: 150, 7: 764, 8: 4,637, 9: 36,027 (atoms 3–29).

Aromatic-like proxy (n_C ≥ 6 and n_H ≤ n_C, a composition rule, not ring detection): **2,120 molecules (5.1%)** — labels in `data/hessian_qm9/aromatic_like_labels.txt`; an upper bound for the recomputed B3LYP subset, whose size the RECIPE fixes by dated note after the Hessian timing.

Most common compositions (C,H,N,O,F): (6, 9, 1, 2, 0): 2415; (7, 10, 0, 2, 0): 2380; (7, 11, 1, 1, 0): 2203; (7, 12, 0, 2, 0): 2108; (8, 12, 0, 1, 0): 2037; (7, 9, 1, 1, 0): 1626; 518 distinct compositions.

Shards (sha256 first 16): data-00000-of-00005.arrow 8fb0ae620ddaf83b, data-00001-of-00005.arrow 4a5435bab3710f71, data-00002-of-00005.arrow 2df9a6977971f0a2, data-00003-of-00005.arrow 67cf5c6dbb9e03ab, data-00004-of-00005.arrow 5cda6cd30270bd9c

Units and conventions of the fields (energies, Hessian units, frequency columns) are to be read from the paper before any use — not assumed here.