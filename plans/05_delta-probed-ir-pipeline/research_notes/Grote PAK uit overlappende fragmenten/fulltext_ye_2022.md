# Full text: Ye, Alessandrini, Melosso & Puzzarini, PCCP 24, 23254 (2022), "Lego brick" for PA(N)H structures

Read in full 11 Nov 2026 from `Papers/Ye_2022_Lego_brick_rotational_constants_PCCP24_23254.pdf` (11 pages, journal pp.
23254–23264 = PDF p. 1–11; text extracted with PyMuPDF, pp. 23256 and 23260 also checked as rendered images for
signs and Fig. 1/Fig. 4). DOI 10.1039/d2cp03294e, CC-BY-NC 4.0. **The ESI (Fig. S1, Tables S1–S3, simulated
spectra) is not in this PDF**; nothing below rests on it.

Authorship: Bologna (Puzzarini, corresponding) with Scuola Normale Pisa and SSM Naples affiliations (p. 23254).
**Barone is not an author** of this paper; he is co-author of the method papers it builds on (ref. 27 Melli, Tonolo,
Barone & Puzzarini, JPCA 125, 9904 (2021); ref. 28 Piccardo et al. 2015 for TM; ref. 29–30 for LR/SE100), p. 23263.

## 1. What the method does

- **Template-molecule (TM) step, eqn (1)–(2), p. 23255:** r_e^T = r_e^{DFT,T} + Δr_e^{TM,F}, with
  Δr_e^{TM,F} = r_e^{SE,F} − r_e^{DFT,F}. The target is optimised **whole** at revDSD-PBEP86-D3BJ/may-cc-pVTZ
  (p. 23255–23256); each internal coordinate belonging to a fragment gets that fragment's (semi-experimental − DFT)
  offset for the corresponding parameter. So it is not an assembly of fragment geometries: it is **cheap full-molecule
  geometry + fragment-derived high-minus-low correction** — the same shape as our ΔH transfer, but for structural
  parameters, and the "high" level is semi-experimental (SE) structures from the SE100 database (ref. 30), not a
  higher QC level (p. 23255, §2.1; "we make use of the latter option").
- **LR step, eqn (3)–(4), p. 23256:** the bonds and angles *linking* fragments cannot be templated; their DFT value is
  scaled, r_e^T = (1 + a) r_e^{DFT,T} + b, with a = −0.00184, b = 0 for linkage C–C and a = −0.00297, b = 0 for
  linkage C–O (signs read from the rendered page). Linkage angles and dihedrals stay at revDSD/mayTZ (p. 23260).
- **SE structures, eqn (5)–(6), p. 23256:** B_e^SE = B_0^exp − ΔB_vib^calc, ΔB_vib^i = −½ Σ_r α_r^i; α needs cubic force
  constants, so an anharmonic force field per fragment (isotopologue fits). This is the only place vibrational theory
  enters the fragments, and it enters the *fragment's own* SE structure, not anything transferred.
- **Bricks (p. 23256, Table 2 footnote b p. 23259):** benzene (12 atoms), pyridine (11), HCN (3), HCCH (4), H2O (3),
  trans-formic acid (5); in an alternative scheme for 1-/2-cyanonaphthalene, benzonitrile (13; ref. 54) (p. 23258,
  ESI Fig. S1/Table S1). **All bricks are single rings or small chains, ≤ 13 atoms; no polycyclic brick.** Aromatic
  bricks: benzene, pyridine, benzonitrile.
- **Fused rings / overlap (Fig. 1, p. 23256):** naphthalene = 2 benzenes, anthracene/phenanthrene = 3, pyrene = 4
  (Table 2 fn. b). The benzene bricks share atoms (Fig. 1: the two dashed contours overlap at C3/C8); "none [linkage]
  is required between the two benzene rings because the internal coordinates defining 1-cyanonaphthalene do not
  involve it" (p. 23256). So for fused PA(N)Hs there is **no linkage bond and no LR at all**; every ring C–C and C–H
  gets the benzene (or pyridine) offset. Bond-length alternation in the result comes entirely from the full-molecule
  DFT (Fig. 4, p. 23260: TM ring C–C from 1.3681 to 1.4309 Å in 2-ethynylnaphthalene).
- Small inconsistency in the paper: the cyanonaphthalene linkage is called C1–C2 (p. 23256 col. 1, Fig. 1) and then
  "The C2-C3 bond length is corrected" (p. 23256 col. 2); Fig. 1 calls the brick a "biphenyl ring fragment".

## 2. Test molecules and errors

Validation is **only through ground-state rotational constants vs experiment** (TM B_e + B3LYP-D3BJ/jun-cc-pVDZ ΔB_vib,
p. 23256 §2.4). **No bond length is compared with a reference structure.** The bond-length accuracy is an inference:
"uncertainties smaller than 0.001 Å for bond lengths and 0.1° for angles" (p. 23259–23260).

Benchmark set, 18 molecules (p. 23255; list p. 23256; Table 1 p. 23258; Table 2 p. 23259). MAE in % over A0, B0, C0
(revDSD/mayTZ → TM → TM+LR; all include B3/junDZ ΔB_vib). Atom counts are mine from the formulas.

| Molecule | atoms | PAH? | revDSD | TM | TM+LR | source |
|---|---|---|---|---|---|---|
| naphthalene | 18 | PAH | 0.36 | 0.03 | – | Table 2 |
| anthracene | 24 | PAH | 0.41 | 0.08 (A 0.11) | – | Table 2 |
| phenanthrene | 24 | PAH | 0.13 | **0.46** | – | Table 2 |
| pyrene | 26 | PAH | 0.34 | 0.02 | – | Table 2 |
| 1-cyanonaphthalene (CCN bent) | 19 | CN-PAH | 0.39 | 0.11 | 0.09 | Table 1 |
| 1-cyanonaphthalene (CCN 180°) | 19 | CN-PAH | 0.42 | 0.23 | 0.21 | Table 1 |
| 2-cyanonaphthalene | 19 | CN-PAH | 0.38 | 0.06 | 0.04 | Table 1 |
| 9-cyanoanthracene | 25 | CN-PAH | 0.37 | 0.06 | 0.03 | Table 2 |
| 9-cyanophenanthrene | 25 | CN-PAH | 0.39 | 0.08 | 0.05 | Table 2 |
| trans-2-naphthol | 19 | OH-PAH | 0.38 | 0.08 | 0.03 | Table 2 |
| cis-1-naphthol | 19 | OH-PAH | 0.39 | 0.07 | 0.02 | Table 2 |
| quinoline | 17 | PANH | 0.36 | 0.01 | – | Table 2 |
| isoquinoline | 17 | PANH | 0.36 | 0.01 | – | Table 2 |
| phenanthridine | 23 | PANH | 0.38 | 0.05 | – | Table 2 |
| 3-cyanopyridine | 12 | no (one ring) | 0.36 | 0.09 | 0.04 | Table 2 |
| 2-ethynylpyridine | 13 | no | 0.35 | 0.10 | 0.04 | Table 2 |
| cis-3-hydroxypyridine | 12 | no | 0.38 | 0.12 | 0.03 | Table 2 |
| 4-hydroxypyridine | 12 | no | 0.38 | 0.10 | 0.003 | Table 2 |
| cis-benzoic acid | 15 | no | 0.45 | 0.13 | 0.05 | Table 2 |

- Largest single TM error outside phenanthrene: ~0.2% on B of the hydroxypyridines and benzoic acid (p. 23259).
- **Phenanthrene fails** (0.13% → 0.46% with TM); the authors blame the experimental constants (ref. 41) but could not
  check, the assigned line list being unavailable (p. 23258). Not resolved.
- 1-cyanonaphthalene: bare revDSD B_e is *closer* to B_0^exp (MAE 0.19%) than revDSD B_e + ΔB_vib (0.42%) — DFT error
  cancellation that the vibrational correction undoes (Table 1, p. 23258). Benzonitrile-brick variant: MAE 0.08% (1-CN)
  and 0.05% (2-CN) (p. 23258, ESI Table S1, not available here).
- Ref. 27 (benzonitrile, two bricks): DFT 0.4% → TM+LR 0.02% (p. 23255).
- Summary claim: 0.4% average at revDSD → "less that 0.1%, with deviations as small as 0.01–0.03%" (p. 23262).

Application set, 13 molecules without experiment (Table 3, p. 23261; Fig. 5 p. 23262): 1-/2-ethynylnaphthalene (20
atoms), 2-/3-/4-quinolinecarbonitrile (18), 9-ethynylanthracene, 9-ethynylphenanthrene (26), 1-/2-/4-pyrenecarbonitrile
(27), 1-/2-/4-ethynylpyrene (28). TM raises every constant, by ≤ 3.5 MHz (p. 23260); accuracy "expected" better than
0.1% from the benchmark, no reference (p. 23260). **Largest molecule in the paper: 28 atoms** (ethynylpyrenes, C18H10),
below our 36–60-atom range.

## 3. Vibrational part — none transferred

- **ΔB_vib is computed on the whole target molecule**, B3LYP-D3BJ/jun-cc-pVDZ, from an anharmonic (cubic) force field
  via α_r^i (eqn 5–6, p. 23256; p. 23256 §2.4; Table 2 fn. a p. 23259; Table 3 fn. b p. 23261). Size ≈ 0.6% of B_0
  (p. 23260); values in Table 3 (e.g. 2-ethynylnaphthalene ΔB_vib(A) = 18.694 MHz; 4-ethynylpyrene A 4.051 MHz).
- Quartic centrifugal distortion constants and vibrationally averaged dipole components: also B3/junDZ on the whole
  molecule (p. 23260 §3.3).
- **No frequency, Hessian, force constant, cubic term or ΔB_vib is taken from a brick.** No vibrational error is
  reported. Fragments carry vibrational information only implicitly, through their SE structures (whose own ΔB_vib were
  computed on the fragment, eqn 5). Not prior art for a fragment-transferred vibrational correction.
- Incidental: the introduction says IR selectivity is poor because "the transition frequency of a given vibrational
  mode varies marginally" with environment (p. 23254) — a motivation for rotational spectroscopy, not a transfer method.

## 4. Delocalisation, fused rings, limits, extensions

- **No discussion of delocalisation, π-conjugation, aromaticity, Clar sextets or bond-length alternation.** Fused rings
  are handled silently by overlapping benzene/pyridine bricks without linkage terms (p. 23256, Table 2 fn. b).
- Limits stated: works for "rather rigid systems"; ref. 27 "suggested that flexibility might reduce the accuracy"; OH
  and COOH species show no degradation (TM+LR 0.02% average); NH2 "preliminary results" similar; amino acids and
  non-planar flexible systems announced as a subsequent study; TM+LR on flexible molecules "requires a validation
  study" (p. 23261–23262).
- Size claim: "can be applied to systems of increasing dimensions without the deterioration of the accuracy; indeed,
  increasing the number of fragments does not affect its performance" (p. 23262) — on 12–28-atom molecules, 1–4 bricks.
- **No vibrational extension is announced.** The only extension named is flexible systems (p. 23262).

## 5. Report check (`reports/Grote PAK uit overlappende fragmenten.md`, grep only)

- **Line 3, "The Lego-brick and templating-synthon work stops at geometries."** — *Holds for Ye 2022*: nothing
  vibrational is transferred from bricks (§3). **Suggested precision:** vibrational corrections (ΔB_vib, anharmonic, B3LYP-D3BJ/jun-cc-pVDZ)
  are computed on the whole molecule, up to 28 atoms, not on bricks (p. 23256, 23260).
- **Line 36 — CORRECTION (wording):** "assembles PAH and PANH equilibrium structures from semi-experimental fragment
  structures. It needs a template-molecule step for the change on joining" misdescribes the method. The TM step *is*
  the method: a full-molecule revDSD/mayTZ geometry plus, per internal coordinate, the brick's (SE − DFT) offset
  (eqn 1–2, p. 23255); LR rescales only linkage bonds between bricks (eqn 3–4, p. 23256), and fused rings need no
  linkage at all (p. 23256). Proposed: "The Lego-brick approach corrects a full-molecule double-hybrid geometry with
  per-parameter (semi-experimental − DFT) offsets taken from small bricks — benzene, pyridine, HCN, HCCH, H2O, formic
  acid — plus a linear regression for the bonds that link bricks; on 18 PA(N)Hs of 12–26 atoms it brings ground-state
  rotational constants from 0.4% to about 0.1% or better (phenanthrene excepted, 0.46%) (Ye et al. 2022)."
- **Line 36 — ADD:** the scheme is structurally our scheme's shape (cheap full molecule + fragment high-minus-low),
  applied to geometries — worth one clause, because a reviewer will see the analogy.
- **Line 72**, "fragment templates (Lego brick) for PAH geometries" — correct; could add "of up to 28 atoms, from
  single-ring bricks" to make the size gap explicit.
- Line 36, "reaches rotational constants within 0.1%" — correct as an average (p. 23259, 23262); the phenanthrene
  exception (0.46%, p. 23258) is not mentioned.
- Not checkable here: "None of the 34 citers of Ye 2022 applies the templates to force fields" (line 36; OpenAlex).
- Attribution: the report's "Pisa–Bologna line" (line 36) fits; calling Ye 2022 a "Barone group" paper would not
  (authors Ye, Alessandrini, Melosso, Puzzarini; p. 23254).
