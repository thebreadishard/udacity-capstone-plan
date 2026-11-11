# Alessandrini, Savarese, Melosso, Bizzocchi, Puzzarini, J. Phys. Chem. A 130, 3403–3415 (2026) — full text

"Assessing the Limits of the 'Lego-Brick' Approach: Equilibrium Structures of Strained and Flexible Cyclic Molecules".
DOI 10.1021/acs.jpca.6c00650, CC-BY 4.0, received 30 Jan 2026, published 15 Apr 2026 (p. 3403). Bologna (Puzzarini group);
Barone is not an author. Read in full on 11 Nov 2026 from the local PDF (13 pages, text extracted with PyMuPDF; Figure 1 viewed
as an image). **The SI is not in the PDF** (separate file; per p. 3412 it holds Figures S1–S4, Table S1 and Z-matrices of all
revDSD/TM/TM+LR structures). Page numbers below are journal pages (PDF page = journal page − 3402).

## Verdict for our claim

- **No vibrational quantity is transferred from fragments.** Bricks carry geometry corrections only. The only vibrational
  quantities (VPT2 ΔB0, ZPE) are computed on the **whole target** at B3LYP/jun-cc-pVDZ (p. 3406, eqs 4–5). For this paper the
  report's "stops at geometries" holds.
- **No PAH, no fused aromatic ring system beyond indole/indane/phthalan, no π-conjugation-length analysis.** PAH performance is
  only referred to Ye et al. 2022 (p. 3403, p. 3407). Largest target: serotonin, C10H12N2O = 25 atoms (formula count, mine).
- **The method is structurally a Δ-transfer scheme, the geometry analogue of ours** (p. 3404, eqs 1–2): full target optimised at
  low level (revDSD/junTZ); each brick's (r_e^SE − r_e^revDSD) difference is added to the corresponding parameters of the target;
  the change on joining comes from the full-molecule DFT, not from the bricks (p. 3409). This is what our report should say
  (see Correction 1).
- **Failure mode = coordinates no brick covers.** Inter-fragment dihedrals are corrected by neither TM nor LR and dominate the
  residual error (p. 3407, p. 3412). Our analogue: torsion/out-of-plane coordinates across piece boundaries.

## 1. What is tested (pp. 3404–3406, Figure 1 p. 3405)

**Method** (p. 3404):
- Eq 1: r_e^TM,T = r_e^revDSD/junTZ,T + Δ_TM. Eq 2: Δ_TM = r_e^SE,F − r_e^revDSD,F (fragment SE equilibrium value minus the same
  parameter at revDSD/junTZ). "The TM approach is able to transfer the typical accuracy of r_e^SE to geometries computed at the
  DFT level" (paraphrase of p. 3404).
- Eq 3: linkage parameters between fragments: r_e^LR,T = (1 + a) r_e^revDSD,T + b, a and b from Ceselin et al. 2021 (ref 11),
  applied to bond distances and valence angles only (not dihedrals).
- TM alone = r_e^TM; both = r_e^TM+LR. LETSGO (any experimental structure as template) vs r_e^SE: SE templates lower the rotational-
  constant error by a factor 3, 0.3% → 0.1% (protonated species, ref 14; p. 3404).
- Levels: revDSD-PBEP86/jun-cc-pV(T+d)Z for the target, D3(BJ) on all DFT, Gaussian 16 (p. 3404). Vibrational corrections ΔB0
  by VPT2 at B3LYP/jun-cc-pVDZ (p. 3406). Accuracy check: B0 = B_e(theory) + ΔB0(B3) against experimental B0 (eq 5); statistics
  mean, MAE, max, std in % (eqs 6–9), plotted as Gaussians (eq 10).
- Reference: experimental ground-state rotational constants; for inner glycidol also CCSD(T)/CBS+CV (ref 32) and an r_e^SE
  (ref 70) (Table 2).

**Molecules: 50 species incl. conformers** (p. 3406). None is a PAH. Atom counts are my formula counts, not the paper's.
- Three-membered rings (8): glycidol inner/outer (11 atoms), glycidaldehyde (9), methyloxirane (10), cyclopropanecarboxaldehyde
  anti/syn (11), N-cyclopropylformamide cis/trans (13).
- Four-membered (10): oxetane (10), trimethylene sulfide (10), cyclobutanone (11), cyclobutane-1,2-dione (10), cyclobutenone (9),
  eq-trans cyclobutanol (13), 2-azetidinone (10), cyanocyclobutane (13), cyanocyclobutene (11), methylenecyclobutane (13).
- Five-membered (11): methylenecyclopentane (16), cycloserine I/II (13), 2-aminooxazole (10), 3-aminoisoxazole (10), THF (13),
  tetrahydrothiophene (13), hydantoin (11), 2,5-oxazolidinedione (10), 2- and 3-furonitrile (10). Aromatic: furonitriles,
  amino-oxazoles.
- Six-membered (12): toluene (15), 3-methylene-1,4-cyclohexadiene (15, cross-conjugated), aspirin rotamers I/II (21), caffeic acid
  syn/anti × 4 conformers (21). Aromatic: benzene ring in toluene, aspirin, caffeic acid.
- Bicyclic (6): spiro[2.4]hepta-4,6-diene (15), 2-indanone (18), phthalan (17), serotonin × 3 conformers (25). Only fused aromatic
  cases: benzo-fused indanone, phthalan, indole of serotonin.
- Plus three open-chain hydantoic acid conformers C5-I, C5-II, C7-II (14).

**Bricks** (Figure 1 column B, p. 3405; text pp. 3404, 3406, 3408, 3410–3411): H2O, HCCH, HCOOH, CH4, C2H4, H2CO, NH3, HCN-type
nitrile, acetone, formamide, dimethyl ether, dimethyl sulfide, oxirane, cyclopropane-type ring, cyclobutane, cyclopentane,
cyclopentadiene, furan, oxazole, isoxazole, maleic anhydride, glycine, NH2OH, acrylic acid (r_e^SE derived here, partial, Table S1),
acrolein, methyl formate, propanal, benzene, pyrrole. Largest brick: benzene (12 atoms). New SE fragment structures needed: acetone,
cyclobutane, methane, cyclopentane, cyclopentadiene, formamide, acrylic acid (p. 3406).
- Open-chain bricks for rings: oxetane/thietane from dimethyl ether or dimethyl sulfide + CH4; cyclobutenone from CH4 + C2H4 + H2CO
  (p. 3408); THF/THT from Me2O/Me2S + 2 CH4; cycloserine from glycine + NH2OH + CH4; hydantoin from H2CO + NH3 + glycine (p. 3410).
- Aspirin = benzene + formic acid + methyl formate + CH4; serotonin side chain −CH2CH2NH2 from propanal because isolated CH4 bricks
  reproduce it badly (p. 3411, Figure 6).

## 2. Errors against reference

All in % of rotational constants vs experiment (mean / MAE / max / std).

| Set (source) | revDSD/junTZ | TM | TM+LR |
|---|---|---|---|
| 3-membered (Table 1, p. 3407) | −0.69 / 0.69 / 1.31 / 0.33 | −0.37 / 0.44 / 1.06 / 0.40 | −0.19 / 0.30 / 0.76 / 0.32 |
| 4-membered (Table 3, p. 3408) | −0.48 / 0.50 / 0.88 / 0.18 | −0.15 / 0.22 / 0.47 / 0.21 | −0.03 / 0.13 / 0.66 / 0.18 |
| 5-membered (Table 3, p. 3408) | −0.57 / 0.57 / 0.99 / 0.19 | −0.12 / 0.22 / 0.58 / 0.24 | −0.01 / 0.14 / 0.55 / 0.19 |

- revDSD baseline: 3-ring 0.69% is "nearly twice" the PA(N)H value 0.4% (Ye 2022) and below protonated species 0.89% (p. 3407).
- TM alone widens the error distribution (std up); LR restores it (p. 3407, p. 3411 Conclusions).
- 3-rings do not reach 0.1%: MAE 0.7 → 0.3%, whereas protonated species went 0.9 → 0.1% (p. 3407).
- **Inner glycidol, Table 2 (p. 3408):** TM+LR bond lengths within 1–2 mÅ of CCSD(T)/CBS+CV and r_e^SE; angles and dihedrals within
  1°. Yet B0 errors TM+LR −0.76/−0.63% (B0/C0) and +0.21% (A0) vs CCSD(T)/CBS+CV −0.07/−0.06/+0.17%; TM+LR vs CC differs by 4, 28,
  21 MHz (A0, B0, C0); A0 off experiment by 43.3 MHz (p. 3407). Culprit: dihedral C7C3C2O1 (TM+LR 101.63°, CC 101.40°, SE 101.02(13)°).
  Changing it by 1.5° drops errors to 0.07/0.05/0.02% (p. 3407). An empirical LR for that dihedral (a = 0.01476, b = 0) lowers the
  other oxirane derivatives from ~0.3% to ~0.2% (p. 3407).
- Oxetane 0.5% → TM 0.3% → TM+LR mean 0.12%, max 0.15% (B0); trimethylene sulfide 0.56% → 0.15% → 0.14%, max 0.25% (A0); open-chain
  bricks cut the error to 1/4 (pp. 3408–3409).
- Cyclobutanone: max error in Table 3; a 2° change of the O-position dihedral lowers the mean from 0.37% to 0.07%.
  Methylenecyclobutane TM+LR 0.07% (p. 3409).
- Partial r_e^SE vs TM+LR (Table 4, p. 3409): methylenecyclobutane C–C within 1–2 mÅ; r_s off by 10–12 mÅ. 2-Azetidinone distances
  within 1–4 mÅ, angles about 0.05°; r_s 10 mÅ and 0.2/0.7°.
- THF (p. 3410): revDSD mean 0.8% (Cs) and 0.6% (C2), so DFT cannot discriminate; TM+LR C2 0.26% MAE, Cs stays 0.8%. Hence C2 is
  assigned. Tetrahydrothiophene 0.2%. Methylenecyclopentane with a partial cyclopentane template: 0.48 → 0.15%.
- Hydantoin 0.35% (A0 dominates; B0, C0 < 0.2%); hydantoic acid C5-I and C7-II 0.15%, C5-II 0.28% (p. 3410).
- C7H8 isomers (toluene, methylene-cyclohexadiene, spiroheptadiene): 0.4% → < 0.1% (p. 3410). Caffeic acid × 8: revDSD 0.50–0.56%
  → TM+LR 0.10–0.12%, max 0.27% (p. 3411). Aspirin both rotamers < 0.2% per constant; serotonin 7 of 9 constants < 0.1%, two at
  0.1% (p. 3411). Bicyclic/six-ring statistics are only in Figure 7 (no table).
- **π-conjugated / fused / delocalised: no failure is reported and none is analysed.** The aromatic and conjugated cases (toluene,
  cross-conjugated methylene-cyclohexadiene, spiroheptadiene, caffeic acid, serotonin, indanone, phthalan) are among the best results.
  The failures are strained 3-rings and carbonyl- or CH2OH-positioning dihedrals (p. 3407, p. 3409, p. 3411).

## 3. Vibrational part

- ΔB0 = −½ Σ_r α_r^i (eq 4, p. 3406) by VPT2 cubic force fields at B3LYP/jun-cc-pVDZ, on the **full target molecule**, justified as
  "safely computed at a low-level of theory" (p. 3406, ref 4). Inner glycidol: ΔA0 = 70.26, ΔB0 = 66.39, ΔC0 = 55.19 MHz (Table 2
  footnote c, p. 3408).
- Hydantoic acid C7-I excluded "due to nonreliable VPT2 results" (p. 3410).
- ZPE (B3/junDZ) reverses the THF conformer order: Cs 0.04 kJ/mol below C2 on revDSD energies, C2 ~0.6 kJ/mol below Cs with ZPE
  (p. 3410).
- Fragment r_e^SE structures (ref 11) carry vibrational corrections from fc-CCSD(T)/cc-pVTZ to revDSD/junTZ. NH3: r_e^SE with
  ae-CCSD(T)/cc-pwCVQZ corrections 1.0106(4) Å / 106.83(9)° vs double-hybrid 1.0111(1) Å / 106.93(2)°, so 0.5 mÅ and 0.1° (p. 3412).
  The quality of vibrational corrections is said to change TM+LR results only marginally (p. 3412).
- **No frequencies, Hessians, force constants or anharmonic constants are transferred from bricks or reported. No prior art for a
  fragment-to-PAH vibrational transfer in this paper.**

## 4. Pitfalls that matter for us

- **Uncovered coordinates dominate.** "the accuracy of the latter tends to be dominated by the uncertainty affecting dihedral angles
  and, more generally, by those parameters that cannot be corrected using either the TM or LR approach" (p. 3412). Their future work
  is LR terms for inter-fragment dihedrals (p. 3412). For us: high-minus-low corrections for coordinates spanning two pieces
  (torsions, out-of-plane at junctions) have no piece that owns them. This matches our R0 read, where out-of-plane is worse.
- **Sensitivity amplification.** 1–2 mÅ and < 1° geometry errors still give 0.6–0.8% rotational-constant errors via one dihedral
  (Table 2, p. 3407). For us, a small coupling error in a soft coordinate can dominate low-mode errors.
- **Brick topology need not match.** Open-chain bricks template 4- and 5-rings as well as cyclic ones: cyclisation effects "are
  correctly retained from the revDSD/junTZ geometry" (pp. 3408–3409). This supports a Δ added to a full low-level calculation:
  the low level carries the joining effect. It was not tested for π delocalisation across the cut.
- **Brick availability limits reach.** Missing bricks can block the method. Their way out is sub-fragmentation of a brick (p. 3412);
  for the serotonin side chain, CH4 bricks failed and propanal was needed (p. 3411), so a brick must contain the bond pattern it
  corrects.
- **Partial templates still help** (cyclopentane with 3 C–C only; acrylic acid), applied to a subset of bond lengths (p. 3410,
  p. 3412).
- **Brick reference quality.** A biased r_e^SE (unbalanced isotopologue set) would propagate (p. 3404, p. 3412). Our analogue: a
  noisy piece-level high-level Hessian propagates into every target.
- Fragment size: bricks are 3–12 atoms; no study of brick size vs error and no conjugation-length test.

## 5. Check of our report ("Grote PAK uit overlappende fragmenten.md", grep only)

Alessandrini 2026 appears only in the bibliography (line 104) and inside a bundled Europe PMC query URL on line 36; the body never
cites it.

- **Line 3**, "The Lego-brick and templating-synthon work stops at geometries." **Holds for this paper.** Suggested precision: "stops
  at geometries; the vibrational corrections they use (VPT2 ΔB0, ZPE) are computed on the whole molecule at B3LYP/jun-cc-pVDZ,
  never from bricks (Alessandrini 2026, p. 3406)."
- **CORRECTION 1, line 36**, "The Lego-brick approach assembles PAH and PANH equilibrium structures from semi-experimental fragment
  structures. It needs a template-molecule step for the change on joining and a linear regression for the linkages". This is wrong
  on the mechanism. The target is optimised whole at DFT (revDSD/junTZ). The TM step adds each fragment's error correction
  (r_e^SE − r_e^DFT of the fragment) to the matching parameters. The change on joining comes from the full-molecule DFT (p. 3409,
  cyclisation "retained from the revDSD/junTZ geometry"). LR, r = (1 + a) r_DFT + b, corrects only the linkage distances and angles
  (eqs 1–3, p. 3404). Suggested wording: "The Lego-brick approach corrects a full-molecule DFT structure with fragment corrections
  (semi-experimental minus DFT, per fragment), plus a linear regression for the linkage distances and angles; it is the geometry
  analogue of a fragment Δ added to a cheap full calculation." This matters: it makes the Lego brick a closer conceptual predecessor
  of our ΔH scheme than the current sentence suggests, while it still stops at geometries.
- **Scope note, line 36**, "reaches rotational constants within 0.1% (Ye 2022)". This is for rigid systems. On strained or flexible
  rings TM+LR gives an MAE of 0.30% (3-rings), 0.13% (4-rings) and 0.14% (5-rings) (Tables 1 and 3). It reaches < 0.1% only for the
  C7H8 isomers and serotonin (pp. 3410–3411). The Ye 2022 number itself is left to fulltext_ye_2022.md.
- **Check (not from this paper), line 36 and line 106.** The link labelled "Di Grande, Lazzari & Barone 2024" is a Europe PMC query
  OR-ing four DOIs: 10.1063/5.0255564, 10.1021/acs.jpca.6c00650 (this paper), 10.1021/acs.jctc.4c00900 and PMID 40548656. Line 106
  lists 10.1063/5.0255564 as "Lazzari et al., J. Chem. Phys. 162, 114310 (2025)". The author and year of the "templating synthons"
  claim (2024 vs 2025, Di Grande vs Lazzari) disagree between lines 36 and 106, and the link does not point to one paper. Fix the
  citation to a single source.
- **Line 30** (heading "Aromatic fragmentation stopped at energies and geometries") and **line 72** ("fragment templates (Lego brick)
  for PAH geometries"): consistent with this paper. Line 72 could add "and strained or flexible rings (Alessandrini 2026)".
- **Line 104** (bibliography: OA, PMC13137258): consistent with the PDF (CC-BY 4.0, pp. 3403–3415).
