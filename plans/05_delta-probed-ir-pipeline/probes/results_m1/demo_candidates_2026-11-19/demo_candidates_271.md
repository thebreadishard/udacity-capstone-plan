# TASKS 271: candidate 'never seen' molecules for the 25 Nov demo (19 Nov 2026)

Read-only screen; nothing tracked was edited, nothing computed beyond RDKit and the timing fit.
Scripts (scratchpad, same folder as this note): `demo_candidates_271.py` (the screen, writes `out.json`), `summarise_271.py`
(the table below, `table_full.md`), `domain_271.py` (how the release pool covers the families, `domain.txt`).
Run from `PLAN/modules/08_industry_synthesis` with `PYTHONPATH` set to it; each run is a few hundred MB (torch loads six
1.3 MB checkpoints for their `train_ids`; no corpus Hessians are read).

## What the screen used

- Product networks: `pipeline.product_networks()` gives kind **release**, nothing held back:
  `E7_rungC_v14s3clean_c00_control_release_model_n1132_seed{0,1,2}.pt` — **1,132 training ids (1,082 neutral + 50 P3c cations)**.
  Measurement networks: `E7_rungC_v14s3clean_c00_control_model_n1082_seed{0,1,2}.pt`; hold-outs from their evaluation records (`seen.load`).
- 'Seen': `seen.release_index` / `seen.load` (canonical SMILES via `catalog.canonical`), cations indexed apart under their parent.
- Corpus: every row of `modules/05_support_predictor/corpus/manifest.csv` (14,258 rows, any layer, any status — `done`, `pending`,
  `failed`, `moved`), matched by canonical SMILES. P3c rows carry their parent's SMILES, so a cation row shows up as a corpus row of the
  neutral.
- Gates (`pipeline.admit`): neutral (net formal charge 0), no radical, at least one aromatic atom, one fragment, elements inside the
  release networks' training set — **C, Cl, F, H, N, O, S** (`pipeline.training_set`). Size is *not* refused: the admission records
  `inside_training_sizes` against the training range **8–40 atoms**. Br/I are refused (and `anchor_plan` has no basis count for Br).
- Time: `runtime.estimate_or_other(smiles, threads=6, pyscf="2.15.0")`. **There are 0 timed laptop runs on pyscf 2.15.0**, so it
  falls back to **pyscf 2.14.0's fit: 10 runs, 4 sizes (102, 162, 230, 320 basis functions: benzene ×4, cinnoline ×1,
  phenanthrene ×3, candidate06 ×2), seconds ∝ n^3.23, half-hour line at ≈ 172 basis functions.** Step 3 now runs 2.15.0 and is slower
  (TASKS 270: benzene's step 3 alone 462 s against the whole 2.14.0 run's 324 s), so the column '×1.43' multiplies by 462/324 as a
  *floor* on the slowdown. Both columns are provisional until row 270's v1.4 run enters the fit.
  Measured anchor: cinnoline (162 bf) took 1,261 s = 21 min on 2.14.0 (`pipeline_rehearsal_2026-10-30/cinnoline`); the fit says 25.

## Shortlist (outside the corpus entirely, gates pass, inside 8–40 atoms, ≤ 30 min even ×1.43 unless marked)

None of these has a corpus row of any id, layer or status; none is in the release or measurement networks' training data, no hold-out
holds it or a twin, and no radical cation of it was trained (it has no P3c row). NIST gas-phase IR is **from memory, not verified**.

| # | name | SMILES | atoms | bf | est. min (2.14.0 fit) | ×1.43 | corpus / release / cation | NIST IR (memory) | why |
|---|---|---|---|---|---|---|---|---|---|
| 1 | pyrazine | `c1cnccn1` | 10 | 98 | 5 | 7 | none / no / no | yes | textbook diazine, high symmetry so a clean spectrum; 18 trained molecules hold a 1,4-diazine ring; fastest safe run |
| 2 | pyrimidine | `c1cncnc1` | 10 | 98 | 5 | 7 | none / no / no | yes | the nucleobase ring every chemist knows; 7 trained molecules hold n:c:n |
| 3 | benzoxazole | `c1ccc2ocnc2c1` | 14 | 145 | 17 | 25 | none / no / no | likely | fused bicyclic heteroaromatic, demo-sized; 24 trained molecules hold an oxazole/imidazole/thiazole n:c:X ring |
| 4 | benzimidazole | `c1ccc2[nH]cnc2c1` | 15 | 147 | 18 | 26 | none / no / no | likely (may be condensed phase only) | drug scaffold (omeprazole, albendazole); N–H stretch on show; same ring coverage as 3 |
| 5 | 1,3,5-trifluorobenzene | `Fc1cc(F)cc(F)c1` | 12 | 141 | 16 | 22 | none / no / no | yes | a substituted benzene; fluorine is well trained (175 molecules); D3h, strong C–F bands |
| 6 | thiophene | `c1ccsc1` | 9 | 87 | 3 | 5 | none / no / no | yes | the classic five-ring heteroaromatic; S trained (52 aromatic-S molecules), but only substituted five-rings were trained and 9 atoms is near the 8-atom floor |
| 7 | 2,6-dimethylphenol | `Cc1cccc(C)c1O` | 19 | 155 | 21 | 30 | none / no / no | yes | industrial monomer (PPO resin); OH + aryl-CH3 both trained (99 aryl-methyl molecules); at the half-hour edge ×1.43 |
| 8 | N,N-dimethylaniline | `CN(C)c1ccccc1` | 20 | 157 | 22 | 32 | none / no / no | yes | very well known; **but no trained molecule has an N(CH3)2 group** — an honest extrapolation, and over 30 min ×1.43 |

Furan (`c1ccoc1`, 9 atoms, 3–4 min, NIST yes) and pyrrole (`c1cc[nH]c1`, 10 atoms, 3–4 min, NIST yes) are equivalent swaps for 6.

## Unsure / flagged

- **N–N aromatic bond never trained**: `n:n` matches **0** of the 1,082 trained neutrals. Cinnoline, pyridazine and indazole pass the gates
  and the clock but test a bond type the network never saw; the error may be larger than the hold-out figure. Cinnoline is also the
  30 Oct rehearsal molecule (already run in front of the project on v1.3), so it is unseen by the networks but not new to the show.
- **sp3 groups beyond methyl never trained**: 0 trained molecules with an aryl ethyl, isopropyl, ethoxy, N(CH3)2, S–CH3, acetamido or a
  ring ketone; 29 have any sp3 CH2. So cumene, phenetole, 4-ethylphenol, thioanisole, N,N-dimethylaniline, acetanilide and 1-indanone
  are outside the corpus but are extrapolations in their substituent; mesitylene is in-family (aryl CH3) but its 1,3,5-trimethyl pattern
  is absent.
- **Small parents**: 55 trained molecules have ≤ 12 atoms; the 9–10-atom five-rings (furan, thiophene, pyrrole, imidazole, oxazole) are
  inside the 8–40 range but sit near its floor, and their trained relatives are all substituted.
- **Time near the line**: acetanilide (28 → 40), cinnamaldehyde (27 → 38), 1-indanone (27 → 38), cinnoline (25 → 35; measured 21 on
  2.14.0), mesitylene/cumene (23 → 33), N,N-dimethylaniline (22 → 32): within half an hour on the 2.14.0 fit, likely past it on 2.15.0.
  Wait for row 270 before offering these.
- **In the corpus only as `pending` rows** (queued, never labelled, not in either network's training): toluene, anisole, benzaldehyde,
  acetophenone, aniline, benzoic acid, the xylenes and cresols (o-, m-), ethylbenzene, nitrobenzene, benzyl alcohol, catechol, resorcinol,
  hydroquinone, the picolines, 2,6-lutidine, 2-aminopyridine, nicotinamide, 1,2-dichlorobenzene, 4-fluorotoluene and others (full table).
  These are 'outside the release networks' 1,132 entries' but not 'outside the corpus'; p-toluidine is a `done` B row the networks did
  not train on (in the catalogue). If the supervisor names one of these, the subtitle's second clause applies, not the first.
- **Trained by the release networks** (not usable): phenol, styrene, benzonitrile, p-cresol, salicylaldehyde, phenylacetylene, pyridine,
  quinoline, isoquinoline, quinoxaline, quinazoline, indole, benzofuran, benzothiophene, naphthalene and its methyl/1-naphthol
  derivatives, biphenyl, fluorene, azulene, acenaphthylene, acenaphthene, anthracene, phenanthrene, indene, chlorobenzene, fluorobenzene,
  benzene, benzophenone, diphenyl ether, carbazole, dibenzofuran, 2-methylindole, 8-hydroxyquinoline, 2-methylfuran, trans-stilbene.
  Benzonitrile, benzophenone, biphenyl, fluorene, phenanthrene and benzene are hold-out (a) molecules for the measurement networks.
  Radical cations trained (release): pyridine, quinoline, anthracene, fluorobenzene, benzene.
- Larger well-known molecules outside the corpus but past half an hour: vanillin (35), paracetamol (37), methyl salicylate (35), coumarin
  (33), thymol (43), aspirin (58), caffeine (77), nicotine (55), ibuprofen (115), 2,2'-bipyridine (46), xanthene, phenoxazine, benzil,
  diphenylmethane, tetralin (31), phthalimide/phthalic anhydride (30–32), hexafluorobenzene (35). Minutes on the 2.14.0 fit.

## Subtitle draft (TASKS 271, for the regenerated show with TASKS 246)

> "Never seen" means the network did not learn from this molecule: it is not among the 1,132 molecules the shipped networks were
> trained on, and it is not in our database at all, so no one had computed its answer before today.

Variant when the pick is a queued corpus row (the `pending` list above):

> "Never seen" means the network did not learn from this molecule: it is not among the 1,132 molecules the shipped networks were
> trained on. It is on our list of molecules to compute later, but its answer had not been computed before today.

## Full table

Columns: basis functions (6-31G*), minutes on pyscf 2.14.0's fit, ×1.43 floor for 2.15.0, ≤ 30 min on the 2.14.0 fit, corpus rows
(id(layer,status), first three), release-trained ids, measurement-trained ids, hold-out, radical cation trained by the release networks,
gates.

| name | SMILES | atoms | bf | est min (2.14.0) | ≥ min ×1.43 (2.15.0) | ≤30? | corpus rows | release | meas. trained | hold-out | cation trained (rel) | gates |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| toluene | `Cc1ccccc1` | 15 | 121 | 10 | 14 | yes | B_e0830a4b11(B,pending) | - | - | - | - | pass |
| anisole | `COc1ccccc1` | 16 | 136 | 14 | 20 | yes | B_3f48f24c66(B,pending) | - | - | - | - | pass |
| benzaldehyde | `O=Cc1ccccc1` | 14 | 132 | 13 | 18 | yes | B_da3341b60b(B,pending) | - | - | - | - | pass |
| acetophenone | `CC(=O)c1ccccc1` | 17 | 151 | 20 | 28 | yes | B_33134a8efc(B,pending) | - | - | - | - | pass |
| phenol | `Oc1ccccc1` | 13 | 117 | 9 | 12 | yes | B_3db4fe6829(B,done), P3c_3db4fe6829(P3c,pending) | B_3db4fe6829 | B_3db4fe6829 | - | - | pass |
| aniline | `Nc1ccccc1` | 14 | 119 | 9 | 13 | yes | B_9e83fe5a5d(B,pending) | - | - | - | - | pass |
| benzoic acid | `O=C(O)c1ccccc1` | 15 | 147 | 18 | 26 | yes | B_aaba64840a(B,pending) | - | - | - | - | pass |
| o-xylene | `Cc1ccccc1C` | 18 | 140 | 15 | 22 | yes | B_3551181f91(B,pending) | - | - | - | - | pass |
| m-xylene | `Cc1cccc(C)c1` | 18 | 140 | 15 | 22 | yes | B_65edb23016(B,pending) | - | - | - | - | pass |
| p-xylene | `Cc1ccc(C)cc1` | 18 | 140 | 15 | 22 | yes | B_07cd55a1e1(B,pending) | - | - | - | - | pass |
| ethylbenzene | `CCc1ccccc1` | 18 | 140 | 15 | 22 | yes | B_5a8607cf49(B,pending) | - | - | - | - | pass |
| styrene | `C=Cc1ccccc1` | 16 | 136 | 14 | 20 | yes | A_8f6ed7c002(A,done), B_8f6ed7c002(B,pending), P3c_8f6ed7c002(P3c,pending) | A_8f6ed7c002 | A_8f6ed7c002 | - | - | pass |
| benzonitrile | `N#Cc1ccccc1` | 13 | 130 | 12 | 17 | yes | A_3100da3761(A,done), B_3100da3761(B,done), P3c_3100da3761(P3c,pending) | A_3100da3761, B_3100da3761 | - | a: A_3100da3761 | - | pass |
| nitrobenzene | `O=[N+]([O-])c1ccccc1` | 14 | 145 | 17 | 25 | yes | B_c699246cbb(B,pending) | - | - | - | - | pass |
| benzyl alcohol | `OCc1ccccc1` | 16 | 136 | 14 | 20 | yes | B_24703bb682(B,pending) | - | - | - | - | pass |
| methyl benzoate | `COC(=O)c1ccccc1` | 18 | 166 | 27 | 38 | yes | B_cf0c793a92(B,pending) | - | - | - | - | pass |
| acetanilide | `CC(=O)Nc1ccccc1` | 19 | 168 | 28 | 40 | yes | - | - | - | - | - | pass |
| o-cresol | `Cc1ccccc1O` | 16 | 136 | 14 | 20 | yes | B_e52731943c(B,pending) | - | - | - | - | pass |
| p-cresol | `Cc1ccc(O)cc1` | 16 | 136 | 14 | 20 | yes | B_188d8de09c(B,done), P3c_188d8de09c(P3c,done) | B_188d8de09c | B_188d8de09c | - | - | pass |
| m-cresol | `Cc1cccc(O)c1` | 16 | 136 | 14 | 20 | yes | B_838f1e8ca3(B,pending) | - | - | - | - | pass |
| catechol | `Oc1ccccc1O` | 14 | 132 | 13 | 18 | yes | B_88f0ac486b(B,pending) | - | - | - | - | pass |
| resorcinol | `Oc1cccc(O)c1` | 14 | 132 | 13 | 18 | yes | B_c762672fe7(B,pending) | - | - | - | - | pass |
| hydroquinone | `Oc1ccc(O)cc1` | 14 | 132 | 13 | 18 | yes | B_2e2f0f7872(B,pending) | - | - | - | - | pass |
| p-toluidine | `Cc1ccc(N)cc1` | 17 | 138 | 15 | 21 | yes | B_c66f269f67(B,done), P3c_c66f269f67(P3c,pending) | - | - | - | - | pass |
| N,N-dimethylaniline | `CN(C)c1ccccc1` | 20 | 157 | 22 | 32 | yes | - | - | - | - | - | pass |
| salicylaldehyde | `O=Cc1ccccc1O` | 15 | 147 | 18 | 26 | yes | B_00bd5ba845(B,done), P3c_00bd5ba845(P3c,pending) | B_00bd5ba845 | B_00bd5ba845 | - | - | pass |
| methyl salicylate | `COC(=O)c1ccccc1O` | 19 | 181 | 35 | 50 | no | - | - | - | - | - | pass |
| mesitylene | `Cc1cc(C)cc(C)c1` | 21 | 159 | 23 | 33 | yes | - | - | - | - | - | pass |
| cumene | `CC(C)c1ccccc1` | 21 | 159 | 23 | 33 | yes | - | - | - | - | - | pass |
| phenylacetylene | `C#Cc1ccccc1` | 14 | 132 | 13 | 18 | yes | A_a848c04a21(A,done), B_a848c04a21(B,pending), P3c_a848c04a21(P3c,pending) | A_a848c04a21 | A_a848c04a21 | - | - | pass |
| 4-hydroxybenzaldehyde | `O=Cc1ccc(O)cc1` | 15 | 147 | 18 | 26 | yes | B_81152bb7c8(B,pending) | - | - | - | - | pass |
| vanillin | `COc1cc(C=O)ccc1O` | 19 | 181 | 35 | 50 | no | - | - | - | - | - | pass |
| paracetamol | `CC(=O)Nc1ccc(O)cc1` | 20 | 183 | 37 | 52 | no | - | - | - | - | - | pass |
| aspirin | `CC(=O)Oc1ccccc1C(=O)O` | 21 | 211 | 58 | 83 | no | - | - | - | - | - | pass |
| thymol | `Cc1ccc(C(C)C)c(O)c1` | 25 | 193 | 43 | 62 | no | - | - | - | - | - | pass |
| eugenol | `C=CCc1ccc(O)c(OC)c1` | 24 | 204 | 52 | 74 | no | - | - | - | - | - | pass |
| cinnamaldehyde | `O=C/C=C/c1ccccc1` | 18 | 166 | 27 | 38 | yes | - | - | - | - | - | pass |
| anthranilic acid | `Nc1ccccc1C(=O)O` | 17 | 164 | 26 | 37 | yes | B_563c201278(B,pending) | - | - | - | - | pass |
| 4-nitrophenol | `O=[N+]([O-])c1ccc(O)cc1` | 15 | 160 | 24 | 34 | yes | B_b1290ad655(B,pending) | - | - | - | - | pass |
| benzophenone | `O=C(c1ccccc1)c1ccccc1` | 24 | 230 | 77 | 109 | no | A_08dde334d8(A,done), P3c_08dde334d8(P3c,pending) | A_08dde334d8 | - | a: A_08dde334d8 | - | pass |
| diphenyl ether | `c1ccc(Oc2ccccc2)cc1` | 23 | 215 | 62 | 88 | no | A_5a75c6c39e(A,done), P3c_5a75c6c39e(P3c,pending) | A_5a75c6c39e | A_5a75c6c39e | - | - | pass |
| 2-picoline | `Cc1ccccn1` | 14 | 119 | 9 | 13 | yes | B_954284efbd(B,pending) | - | - | - | - | pass |
| 3-picoline | `Cc1cccnc1` | 14 | 119 | 9 | 13 | yes | B_98a51e3fe1(B,pending) | - | - | - | - | pass |
| 4-picoline | `Cc1ccncc1` | 14 | 119 | 9 | 13 | yes | B_5a63b4134e(B,pending) | - | - | - | - | pass |
| 2,6-lutidine | `Cc1cccc(C)n1` | 17 | 138 | 15 | 21 | yes | B_80bc326a7d(B,pending) | - | - | - | - | pass |
| 2-aminopyridine | `Nc1ccccn1` | 13 | 117 | 9 | 12 | yes | B_98b9523eac(B,pending) | - | - | - | - | pass |
| nicotinamide | `NC(=O)c1cccnc1` | 15 | 147 | 18 | 26 | yes | B_9d292a1f45(B,pending) | - | - | - | - | pass |
| nicotine | `CN1CCC[C@H]1c1cccnc1` | 26 | 208 | 55 | 79 | no | - | - | - | - | - | pass |
| pyridine | `c1ccncc1` | 11 | 100 | 5 | 7 | yes | A_6e858b26e5(A,done), P3c_6e858b26e5(P3c,done) | A_6e858b26e5 | A_6e858b26e5 | - | P3c_6e858b26e5 | pass |
| pyrimidine | `c1cncnc1` | 10 | 98 | 5 | 7 | yes | - | - | - | - | - | pass |
| pyrazine | `c1cnccn1` | 10 | 98 | 5 | 7 | yes | - | - | - | - | - | pass |
| pyridazine | `c1ccnnc1` | 10 | 98 | 5 | 7 | yes | - | - | - | - | - | pass |
| quinoline | `c1ccc2ncccc2c1` | 17 | 164 | 26 | 37 | yes | A_ff98e1160d(A,done), P3c_ff98e1160d(P3c,done) | A_ff98e1160d | A_ff98e1160d | - | P3c_ff98e1160d | pass |
| isoquinoline | `c1ccc2cnccc2c1` | 17 | 164 | 26 | 37 | yes | A_d09f8d1ef8(A,done), P3c_d09f8d1ef8(P3c,pending) | A_d09f8d1ef8 | A_d09f8d1ef8 | - | - | pass |
| quinoxaline | `c1ccc2nccnc2c1` | 16 | 162 | 25 | 35 | yes | A_7aa232d4e9(A,done), P3c_7aa232d4e9(P3c,pending) | A_7aa232d4e9 | A_7aa232d4e9 | - | - | pass |
| quinazoline | `c1ccc2ncncc2c1` | 16 | 162 | 25 | 35 | yes | A_d295f2fa80(A,done), P3c_d295f2fa80(P3c,pending) | A_d295f2fa80 | A_d295f2fa80 | - | - | pass |
| cinnoline | `c1ccc2nnccc2c1` | 16 | 162 | 25 | 35 | yes | - | - | - | - | - | pass |
| indole | `c1ccc2[nH]ccc2c1` | 16 | 149 | 19 | 27 | yes | A_76e053ce6a(A,done), P3c_76e053ce6a(P3c,pending) | A_76e053ce6a | A_76e053ce6a | - | - | pass |
| pyrrole | `c1cc[nH]c1` | 10 | 85 | 3 | 4 | yes | - | - | - | - | - | pass |
| furan | `c1ccoc1` | 9 | 83 | 3 | 4 | yes | - | - | - | - | - | pass |
| thiophene | `c1ccsc1` | 9 | 87 | 3 | 5 | yes | - | - | - | - | - | pass |
| benzofuran | `c1ccc2occc2c1` | 15 | 147 | 18 | 26 | yes | A_fead28d796(A,done) | A_fead28d796 | A_fead28d796 | - | - | pass |
| benzothiophene | `c1ccc2sccc2c1` | 15 | 151 | 20 | 28 | yes | A_9d7c66d274(A,done) | A_9d7c66d274 | A_9d7c66d274 | - | - | pass |
| benzimidazole | `c1ccc2[nH]cnc2c1` | 15 | 147 | 18 | 26 | yes | - | - | - | - | - | pass |
| benzoxazole | `c1ccc2ocnc2c1` | 14 | 145 | 17 | 25 | yes | - | - | - | - | - | pass |
| indazole | `c1ccc2[nH]ncc2c1` | 15 | 147 | 18 | 26 | yes | - | - | - | - | - | pass |
| carbazole | `c1ccc2c(c1)[nH]c1ccccc12` | 22 | 213 | 60 | 85 | no | A_8152ea74fd(A,done) | A_8152ea74fd | A_8152ea74fd | - | - | pass |
| dibenzofuran | `c1ccc2c(c1)oc1ccccc12` | 21 | 211 | 58 | 83 | no | A_20db5837c9(A,done) | A_20db5837c9 | A_20db5837c9 | - | - | pass |
| coumarin | `O=c1ccc2ccccc2o1` | 17 | 177 | 33 | 47 | no | - | - | - | - | - | pass |
| caffeine | `Cn1c(=O)c2c(ncn2C)n(C)c1=O` | 24 | 230 | 77 | 109 | no | - | - | - | - | - | pass |
| purine | `c1ncc2[nH]cnc2n1` | 13 | 143 | 16 | 24 | yes | - | - | - | - | - | pass |
| adenine | `Nc1ncnc2[nH]cnc12` | 15 | 160 | 24 | 34 | yes | - | - | - | - | - | pass |
| naphthalene | `c1ccc2ccccc2c1` | 18 | 166 | 27 | 38 | yes | A_01f3186607(A,done), P3c_01f3186607(P3c,done) | A_01f3186607 | A_01f3186607 | - | - | pass |
| 1-methylnaphthalene | `Cc1cccc2ccccc12` | 21 | 185 | 38 | 54 | no | A_ea73419366(A,done), B_ea73419366(B,pending), P3c_ea73419366(P3c,pending) | A_ea73419366 | A_ea73419366 | - | - | pass |
| 2-methylnaphthalene | `Cc1ccc2ccccc2c1` | 21 | 185 | 38 | 54 | no | A_69789470db(A,done), B_69789470db(B,pending), P3c_69789470db(P3c,pending) | A_69789470db | A_69789470db | - | - | pass |
| 1-naphthol | `Oc1cccc2ccccc12` | 19 | 181 | 35 | 50 | no | A_466972291d(A,done), B_466972291d(B,pending), P3c_466972291d(P3c,pending) | A_466972291d | A_466972291d | - | - | pass |
| 2-naphthol | `Oc1ccc2ccccc2c1` | 19 | 181 | 35 | 50 | no | B_884132846f(B,pending) | - | - | - | - | pass |
| biphenyl | `c1ccc(-c2ccccc2)cc1` | 22 | 200 | 49 | 70 | no | A_fdc27f1bd1(A,done), P3c_fdc27f1bd1(P3c,pending) | A_fdc27f1bd1 | - | a: A_fdc27f1bd1 | - | pass |
| fluorene | `c1ccc2c(c1)Cc1ccccc1-2` | 23 | 215 | 62 | 88 | no | A_e72997e726(A,done), P3c_e72997e726(P3c,pending) | A_e72997e726 | - | a: A_e72997e726 | - | pass |
| azulene | `c1ccc2cccc-2cc1` | 18 | 166 | 27 | 38 | yes | A_d9139359ab(A,done) | A_d9139359ab | A_d9139359ab | - | - | pass |
| acenaphthylene | `C1=Cc2cccc3cccc1c23` | 20 | 196 | 46 | 65 | no | A_45187bb7c8(A,done) | A_45187bb7c8 | A_45187bb7c8 | - | - | pass |
| acenaphthene | `c1cc2c3c(cccc3c1)CC2` | 22 | 200 | 49 | 70 | no | A_8d1f3c46b0(A,done) | A_8d1f3c46b0 | A_8d1f3c46b0 | - | - | pass |
| anthracene | `c1ccc2cc3ccccc3cc2c1` | 24 | 230 | 77 | 109 | no | A_a1e6ec1862(A,done), P3c_a1e6ec1862(P3c,done) | A_a1e6ec1862 | A_a1e6ec1862 | - | P3c_a1e6ec1862 | pass |
| phenanthrene | `c1ccc2c(c1)ccc1ccccc12` | 24 | 230 | 77 | 109 | no | A_541c53d1a5(A,done), P3c_541c53d1a5(P3c,done) | A_541c53d1a5 | - | a: A_541c53d1a5 | - | pass |
| indene | `C1=Cc2ccccc2C1` | 17 | 151 | 20 | 28 | yes | A_90df3e4aa9(A,done), P3c_90df3e4aa9(P3c,pending) | A_90df3e4aa9 | A_90df3e4aa9 | - | - | pass |
| tetralin | `c1ccc2c(c1)CCCC2` | 22 | 174 | 31 | 44 | no | - | - | - | - | - | pass |
| chlorobenzene | `Clc1ccccc1` | 12 | 119 | 9 | 13 | yes | B_1ed01fda1b(B,done), P3c_1ed01fda1b(P3c,pending) | B_1ed01fda1b | B_1ed01fda1b | - | - | pass |
| fluorobenzene | `Fc1ccccc1` | 12 | 115 | 8 | 12 | yes | B_8b12a55d3a(B,done), P3c_8b12a55d3a(P3c,done) | B_8b12a55d3a | B_8b12a55d3a | - | P3c_8b12a55d3a | pass |
| 1,2-dichlorobenzene | `Clc1ccccc1Cl` | 12 | 136 | 14 | 20 | yes | B_b1858926df(B,pending) | - | - | - | - | pass |
| 4-fluorotoluene | `Cc1ccc(F)cc1` | 15 | 134 | 13 | 19 | yes | B_4ab88e3abc(B,pending) | - | - | - | - | pass |
| benzene | `c1ccccc1` | 12 | 102 | 6 | 8 | yes | A_8448043181(A,done), P3c_8448043181(P3c,done) | A_8448043181 | - | a: A_8448043181 | P3c_8448043181 | pass |
| ibuprofen | `CC(C)Cc1ccc(C(C)C(=O)O)cc1` | 33 | 261 | 115 | 164 | no | - | - | - | - | - | pass |
| 2-acetylpyridine | `CC(=O)c1ccccn1` | 16 | 149 | 19 | 27 | yes | B_ed5260c2cb(B,pending) | - | - | - | - | pass |
| 4-methylanisole | `COc1ccc(C)cc1` | 19 | 155 | 21 | 30 | yes | B_cb62cc9459(B,pending) | - | - | - | - | pass |
| phenetole | `CCOc1ccccc1` | 19 | 155 | 21 | 30 | yes | - | - | - | - | - | pass |
| benzamide | `NC(=O)c1ccccc1` | 16 | 149 | 19 | 27 | yes | B_daaa473345(B,pending) | - | - | - | - | pass |
| 2-methylindole | `Cc1cc2ccccc2[nH]1` | 19 | 168 | 28 | 40 | yes | B_01dbe38ea1(B,done), P3c_01dbe38ea1(P3c,pending) | B_01dbe38ea1 | B_01dbe38ea1 | - | - | pass |
| 3-methylindole (skatole) | `Cc1c[nH]c2ccccc12` | 19 | 168 | 28 | 40 | yes | B_aae1cdcdab(B,pending) | - | - | - | - | pass |
| 8-hydroxyquinoline | `Oc1cccc2cccnc12` | 18 | 179 | 34 | 49 | no | B_02b3315726(B,done), P3c_02b3315726(P3c,pending) | B_02b3315726 | B_02b3315726 | - | - | pass |
| 2,2'-bipyridine | `c1ccc(-c2ccccn2)nc1` | 20 | 196 | 46 | 65 | no | - | - | - | - | - | pass |
| phenoxazine | `c1ccc2c(c1)Nc1ccccc1O2` | 23 | 228 | 74 | 106 | no | - | - | - | - | - | pass |
| xanthene | `c1ccc2c(c1)Cc1ccccc1O2` | 24 | 230 | 77 | 109 | no | - | - | - | - | - | pass |
| 1,3,5-trifluorobenzene | `Fc1cc(F)cc(F)c1` | 12 | 141 | 16 | 22 | yes | - | - | - | - | - | pass |
| hexafluorobenzene | `Fc1c(F)c(F)c(F)c(F)c1F` | 12 | 180 | 35 | 49 | no | - | - | - | - | - | pass |
| 2-fluoropyridine | `Fc1ccccn1` | 11 | 113 | 8 | 11 | yes | B_7148015d8e(B,pending) | - | - | - | - | pass |
| thioanisole | `CSc1ccccc1` | 16 | 140 | 15 | 22 | yes | - | - | - | - | - | pass |
| 2-methylthiophene | `Cc1cccs1` | 12 | 106 | 6 | 9 | yes | B_75cff4ffb1(B,pending) | - | - | - | - | pass |
| 2-methylfuran | `Cc1ccco1` | 12 | 102 | 6 | 8 | yes | B_29ee41c012(B,done) | B_29ee41c012 | B_29ee41c012 | - | - | pass |
| furfural | `O=Cc1ccco1` | 11 | 113 | 8 | 11 | yes | B_ae8d6e0581(B,pending) | - | - | - | - | pass |
| 1-methylpyrrole | `Cn1cccc1` | 13 | 104 | 6 | 8 | yes | - | - | - | - | - | pass |
| imidazole | `c1c[nH]cn1` | 9 | 83 | 3 | 4 | yes | - | - | - | - | - | pass |
| 1-methylimidazole | `Cn1ccnc1` | 12 | 102 | 6 | 8 | yes | - | - | - | - | - | pass |
| oxazole | `c1cocn1` | 8 | 81 | 3 | 4 | yes | - | - | - | - | - | pass |
| 2,6-dimethylphenol | `Cc1cccc(C)c1O` | 19 | 155 | 21 | 30 | yes | - | - | - | - | - | pass |
| 4-ethylphenol | `CCc1ccc(O)cc1` | 19 | 155 | 21 | 30 | yes | - | - | - | - | - | pass |
| 4-methoxyphenol | `COc1ccc(O)cc1` | 17 | 151 | 20 | 28 | yes | B_e4c1b75812(B,pending) | - | - | - | - | pass |
| p-anisaldehyde | `COc1ccc(C=O)cc1` | 18 | 166 | 27 | 38 | yes | B_a49258eda0(B,pending) | - | - | - | - | pass |
| 4-methylbenzaldehyde | `Cc1ccc(C=O)cc1` | 17 | 151 | 20 | 28 | yes | B_37354e4ae0(B,pending) | - | - | - | - | pass |
| 4-aminobenzoic acid | `Nc1ccc(C(=O)O)cc1` | 17 | 164 | 26 | 37 | yes | B_3482c22008(B,pending) | - | - | - | - | pass |
| phthalic anhydride | `O=C1OC(=O)c2ccccc21` | 15 | 173 | 30 | 43 | no | - | - | - | - | - | pass |
| phthalimide | `O=C1NC(=O)c2ccccc21` | 16 | 175 | 32 | 45 | no | - | - | - | - | - | pass |
| benzil | `O=C(C(=O)c1ccccc1)c1ccccc1` | 26 | 260 | 114 | 162 | no | - | - | - | - | - | pass |
| trans-stilbene | `C(=C\c1ccccc1)/c1ccccc1` | 26 | 234 | 81 | 115 | no | A_7a57a52879(A,done), P3c_7a57a52879(P3c,pending) | A_7a57a52879 | A_7a57a52879 | - | - | pass |
| diphenylmethane | `c1ccc(Cc2ccccc2)cc1` | 25 | 219 | 65 | 93 | no | - | - | - | - | - | pass |
| 1-indanone | `O=C1CCc2ccccc21` | 18 | 166 | 27 | 38 | yes | - | - | - | - | - | pass |

KEEP (outside corpus, gates pass, inside sizes, ≤ 30 min on the 2.14.0 fit):
- acetanilide `CC(=O)Nc1ccccc1` atoms 19 bf 168 est 28 min (x1.43: 40) cation_rel [] cation_meas []
- N,N-dimethylaniline `CN(C)c1ccccc1` atoms 20 bf 157 est 22 min (x1.43: 32) cation_rel [] cation_meas []
- mesitylene `Cc1cc(C)cc(C)c1` atoms 21 bf 159 est 23 min (x1.43: 33) cation_rel [] cation_meas []
- cumene `CC(C)c1ccccc1` atoms 21 bf 159 est 23 min (x1.43: 33) cation_rel [] cation_meas []
- cinnamaldehyde `O=C/C=C/c1ccccc1` atoms 18 bf 166 est 27 min (x1.43: 38) cation_rel [] cation_meas []
- pyrimidine `c1cncnc1` atoms 10 bf 98 est 5 min (x1.43: 7) cation_rel [] cation_meas []
- pyrazine `c1cnccn1` atoms 10 bf 98 est 5 min (x1.43: 7) cation_rel [] cation_meas []
- pyridazine `c1ccnnc1` atoms 10 bf 98 est 5 min (x1.43: 7) cation_rel [] cation_meas []
- cinnoline `c1ccc2nnccc2c1` atoms 16 bf 162 est 25 min (x1.43: 35) cation_rel [] cation_meas []
- pyrrole `c1cc[nH]c1` atoms 10 bf 85 est 3 min (x1.43: 4) cation_rel [] cation_meas []
- furan `c1ccoc1` atoms 9 bf 83 est 3 min (x1.43: 4) cation_rel [] cation_meas []
- thiophene `c1ccsc1` atoms 9 bf 87 est 3 min (x1.43: 5) cation_rel [] cation_meas []
- benzimidazole `c1ccc2[nH]cnc2c1` atoms 15 bf 147 est 18 min (x1.43: 26) cation_rel [] cation_meas []
- benzoxazole `c1ccc2ocnc2c1` atoms 14 bf 145 est 17 min (x1.43: 25) cation_rel [] cation_meas []
- indazole `c1ccc2[nH]ncc2c1` atoms 15 bf 147 est 18 min (x1.43: 26) cation_rel [] cation_meas []
- purine `c1ncc2[nH]cnc2n1` atoms 13 bf 143 est 16 min (x1.43: 24) cation_rel [] cation_meas []
- adenine `Nc1ncnc2[nH]cnc12` atoms 15 bf 160 est 24 min (x1.43: 34) cation_rel [] cation_meas []
- phenetole `CCOc1ccccc1` atoms 19 bf 155 est 21 min (x1.43: 30) cation_rel [] cation_meas []
- 1,3,5-trifluorobenzene `Fc1cc(F)cc(F)c1` atoms 12 bf 141 est 16 min (x1.43: 22) cation_rel [] cation_meas []
- thioanisole `CSc1ccccc1` atoms 16 bf 140 est 15 min (x1.43: 22) cation_rel [] cation_meas []
- 1-methylpyrrole `Cn1cccc1` atoms 13 bf 104 est 6 min (x1.43: 8) cation_rel [] cation_meas []
- imidazole `c1c[nH]cn1` atoms 9 bf 83 est 3 min (x1.43: 4) cation_rel [] cation_meas []
- 1-methylimidazole `Cn1ccnc1` atoms 12 bf 102 est 6 min (x1.43: 8) cation_rel [] cation_meas []
- oxazole `c1cocn1` atoms 8 bf 81 est 3 min (x1.43: 4) cation_rel [] cation_meas []
- 2,6-dimethylphenol `Cc1cccc(C)c1O` atoms 19 bf 155 est 21 min (x1.43: 30) cation_rel [] cation_meas []
- 4-ethylphenol `CCc1ccc(O)cc1` atoms 19 bf 155 est 21 min (x1.43: 30) cation_rel [] cation_meas []
- 1-indanone `O=C1CCc2ccccc21` atoms 18 bf 166 est 27 min (x1.43: 38) cation_rel [] cation_meas []
