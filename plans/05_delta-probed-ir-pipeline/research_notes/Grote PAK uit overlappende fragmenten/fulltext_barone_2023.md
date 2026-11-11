# Barone 2023 — Nano-LEGO refinement for structures of large molecules (full-text read)

V. Barone, G. Ceselin, F. Lazzari, N. Tasinato, "Toward Spectroscopic Accuracy for the Structures of Large Molecules at
DFT Cost: Refinement and Extension of the Nano-LEGO Approach", J. Phys. Chem. A 127, 5183–5192 (2023),
doi 10.1021/acs.jpca.3c01617 (Raghavachari Festschrift issue; received 9 Mar 2023, published 7 Jun 2023). Read whole,
11 Nov 2026 16:22, from the local SNS author copy
(`Papers/Barone_2023_Nano-LEGO_structures_large_molecules_JPCA_author_copy.pdf`, 10 PDF pages = journal pages
5183–5192; PDF page n = journal page 5182+n). Text extracted with PyMuPDF (no page renderer installed); Eqs. 1–2 checked
on a PyMuPDF render of p. 5184. **The SI is not in the PDF** (it ends with the reference list, p. 5192): Tables S1–S7
(SE structures of the Br/I molecules, and the bare and Nano-LEGO-corrected geometries of the five test molecules) were
not seen. Page references below are journal pages.

**Corrections to the report are marked `CORRECTION`.** Inferences of ours (not stated in the paper) are marked
`INFERENCE`.

## Bottom line

- Geometry only. Fragments ("templating molecules") transfer a semi-experimental (SE) **bond-length** correction to the
  target; nothing vibrational is computed on a fragment or transferred (Sec. 3 below).
- Vibrational quantities appear only as **ΔB_vib**, the VPT2 vibrational correction to rotational constants (harmonic
  force constants, Coriolis terms, semidiagonal cubic force constants), computed **on the whole target molecule** at DFT
  (PW6, or rDSD/MP2 for the SE database species) (pp. 5184, 5187, 5189).
- No PAH, no fused ring system, no molecule above 14 atoms anywhere in the paper. The test set is 5–12 atoms (Sec. 2).
- The authors name the cost of the vibrational corrections for large systems as one of three remaining limitations
  (p. 5190). They do not announce a fragment-based vibrational correction.

## 1. What the method does

- **Linear regression approach, LRA (Eq. 1, p. 5184).** r_M = a_XY × r_M^DFT + b_XY, per bond type X–Y. Valence and
  dihedral angles are left at their DFT values (p. 5184); "valence angles can be safely left uncorrected at the rDSD
  level, whereas this is not the case at the PW6 level" (p. 5187; how PW6 angles are corrected is not stated here, it
  points to ref 18, Ceselin, Barone, Tasinato, JCTC 17, 7290 (2021), the original Nano-LEGO paper).
- **Templating molecule approach, TMA (Eq. 2, p. 5184).** For each fragment of the target that matches a templating
  molecule (TM) whose SE equilibrium structure is known: r_M = α × (r_M^DFT − r_TM^DFT) + r_TM, with r_TM the SE value.
  Eq. 1 is used for the inter-fragment parameters (the linkages). The original TMA (refs 21, 22, 2015) used α = 1; the
  2023 change is α = a_XY "whenever possible", to make LRA and TMA "fully consistent" (p. 5184). That consistency step is
  the paper's methodological novelty, plus the Br/I extension of the database.
- **What a "brick" is.** A TM is a whole small molecule with an SE structure (benzene for halobenzenes, pyrazole for
  halopyrazoles, p. 5189), chosen "on the basis of chemical intuition"; ML-based automatic fragment recognition is "work
  in progress" (p. 5184, ref 23, the Proxima library). There is **no capping, no link atoms, no overlap bookkeeping**: the
  target is optimised whole at DFT, and the TM's (SE − DFT) bond-length differences are applied to the matching bonds of
  the target. Fragment size = the TM's size (6–12 atoms in this paper).
- **Levels.** Cheap level: PW6B95-D3BJ/jul-cc-pVDZ ("PW6") and rev-DSD-PBEP86-D3BJ/jun-cc-pVTZ ("rDSD"); jul-/jun-cc-pV(n+d)Z
  for S and Cl; aug-cc-pVnZ-PP with small-core pseudopotentials for Br and I (p. 5184). Reference level: **SE equilibrium
  structures** (experimental ground-state rotational constants of several isotopologues minus computed ΔB_vib, then a
  least-squares structure fit with the MSR code) (p. 5184). Not CCSD(T): CCSD(T)/TZ2Pf is cited only once, as agreement for
  the C–Br bond of BrCCF (p. 5185). Software: Gaussian 16 for DFT, CFOUR for MP2 (p. 5184).
- **Database.** SE100 (ref 18) extended to **SE127**: 12 organobromine + 6 organoiodine molecules, 9 others added
  (1,3,4-oxadiazole, H2O2, benzonitrile, phenylacetylene, H2CO–O, glycolic acid, 1-chloro-2-fluoroethene,
  1-chloro-2,2-difluoroethene, aminoacetonitrile), and pyrimidine, pyridazine, thiophene revised (p. 5187).
- **LRA parameters (Table 5, p. 5188)** for C–X (X = C, N, O, F, S, Cl, Br, I), N–X (N, O, S), O–X (O, S), S–S, Y–H
  (C, N, O, S). rDSD: all a_XY within 0.971–1.002; b_XY = 0 except C–S (0.01672 Å), C–Br (0.05037 Å), C–I (0.04213 Å).
  PW6: a_XY 0.928–1.175, non-zero b_XY for C–N, C–O, C–S, C–Br, C–I, O–H. C–C: a = 0.99816 (rDSD), 1.00014 (PW6).
  Note the sign convention: a_XY here = 1 − a_XY of ref 18 (p. 5187).

## 2. Test molecules and errors

### 2a. SE database species (reference structures, not tests of Nano-LEGO)

All small, none a PAH. Br (Fig. 1, p. 5185): BrCN (3 atoms), Br2CO (4), BrCCH (4), BrCCF (4), BrCCCl (4), BrCCCN (5),
CH3Br (5), CH2Br2 (5), CH2BrF (5), CH2CHBr (6), CH3CH2Br (8), CHBr(CH3)2 (11). I (Fig. 2, p. 5187): ICN (3), HCCI (4),
CH3I (5), CH2FI (5), CH2CHI (6), (CH3)2CHI (11). Largest SE127 additions: benzonitrile (13), phenylacetylene (14).

Bare-DFT bond-length errors vs SE (Tables 1–4, pp. 5185–5187), e.g. C–Br: rDSD +2.4 mÅ (BrCCH), +5.9 (CH2Br2),
+7.1 (CH3CH2Br), +6.9 (CHBr(CH3)2); PW6 up to +21.1 mÅ (CHBr(CH3)2, 1.9845 vs 1.96334 Å). C–I in (CH3)2CHI: rDSD
+7.7 mÅ, PW6 +30.6 mÅ (Table 4). After LRA, MAE for all bond types < 1.5 mÅ at rDSD; bare rDSD MAE up to 7.5 mÅ (C–Cl)
(p. 5187). Outliers named: the O–O bond of H2CO–O falls off the LRA line at both levels "due to the strong zwitterionic
character" (p. 5187). Not discussed by the authors: BrCCCl's SE C≡C (1.1935(28) Å) is 14.8 mÅ shorter than rDSD and its
SE C–Br is 6 mÅ *longer* than rDSD, the reverse of every other C–Br in Tables 1–3 (Table 1, p. 5185) — a doubtful SE fit
(INFERENCE).

### 2b. The five Nano-LEGO test cases (validation against experimental B0 only)

Chosen "simply on the basis of the availability of experimental ground state rotational constants" (p. 5187). Procedure:
bare DFT geometry → LRA or LRA+TMA → equilibrium rotational constants → plus PW6 ΔB_vib → compared with experimental
A0, B0, C0 (p. 5187). No Nano-LEGO bond lengths are compared with an SE or CC structure in the main text (they are in the
SI, not available).

| Molecule (table) | Atoms | Aromatic | Template | MAPE % PW6 → PW6+NL | MAPE % rDSD → rDSD+NL | Worst single constant, +NL |
|---|---|---|---|---|---|---|
| CHBrF2 (T6, p. 5189) | 5 | no | LRA only | 1.05 → 0.13 | 0.81 → 0.20 | rDSD+NL B0 −0.27% |
| C6H5Br (T7) | 12 | single benzene ring | benzene (TMA), C–Br by LRA | 0.41 → 0.12 | 0.45 → 0.19 | **rDSD+NL A0 +0.50%** |
| C6H5I (T8) | 12 | single benzene ring | benzene, C–I by LRA | 0.60 → 0.13 | 0.50 → 0.22 | **rDSD+NL A0 +0.61%** |
| 4-Br-pyrazole (T9) | 9 | single 5-ring | pyrazole, C–Br by LRA | 0.37 → 0.12 | 0.49 → 0.10 | PW6+NL B0 −0.16% |
| 4-I-pyrazole (T10) | 9 | single 5-ring | pyrazole, C–I by LRA | 0.55 → 0.08 | 0.55 → 0.09 | rDSD+NL B0 −0.12% |

MAPE values are the paper's; the per-constant errors are recomputed by us from the MHz values in Tables 6–10 (script in
the session scratchpad; our MAPEs reproduce the printed ones to 0.01). The abstract's "average error within 0.2%"
(p. 5183) and "final values (<0.22%)" (p. 5189) are MAPEs; for the halobenzenes the rDSD+NL A0 is off by 0.50% and 0.61%,
*worse* than bare rDSD (−0.34%, −0.33%) and bare PW6 (−0.10%). The NL correction improves B0 and C0 and degrades A0 for
both halobenzenes at both levels. The authors do not comment on this.

Vibrational part of the test numbers: ΔB_vib (Ae − A0 etc.) is 0.4–0.8% of the equilibrium constants (e.g. C6H5Br A:
42.54 of 5727 MHz; 4-Br-pyrazole A: 79.18 of 9567 MHz). For C6H5Br, C6H5I and the pyrazoles the same PW6 ΔB_vib is
added to all four columns (identical Ae − A0 in every column). For CHBrF2 the rDSD columns carry a different ΔB_vib
(A: 61.76 vs 59.12 MHz), although the text says PW6 vibrational corrections throughout (p. 5187) — a small inconsistency
in the paper (INFERENCE from Table 6).

## 3. Is there any vibrational part?

- **No vibrational quantity is computed on a fragment or transferred.** Everything transferred is a bond length.
- What is computed: full-molecule DFT optimisation, analytical Hessian, and semidiagonal cubic force constants by
  numerical differentiation of analytical Hessians, for VPT2 ΔB_vib (p. 5184, Methods). Linear Br molecules get ΔB_vib at
  MP2/cc-pVTZ(-PP) because they are "strongly sensitive to numerical errors" (pp. 5184–5185); nonlinear SE species at rDSD
  (p. 5185); (CH3)2CHI at rDSD (p. 5187); test cases at PW6 (pp. 5187, 5189).
- Error statement for ΔB_vib: DFT ΔB_vib "deliver typical errors within 10% (i.e., less than 0.1% of typical rotational
  constants)", citing refs 18, 21, 22, 30, no new number (p. 5184). B2PLYP is said to give comparable accuracy for
  "vibrational properties" with triple-ζ bases, citing refs 22, 36–39, no new number (p. 5184).
- No frequencies, no Hessian differences, no force-constant transfer, no anharmonic constants (χ), no IR intensities.
- `INFERENCE`: the architecture — a cheap full-molecule calculation plus a correction read off a small template's
  (reference − DFT) difference and applied to the matching local coordinates — is the geometric analogue of our ΔH
  transfer. It is prior art for the *idea* of template-transferred corrections, not for transferring vibrational ones.

## 4. Delocalisation, fused rings, transferability, future work

- No discussion of π-conjugation, delocalisation, fused rings, Clar sextets or the size/shape limits of a template.
  Aromatic content is limited to single rings used whole as templates (benzene, pyrazole, p. 5189).
- The only transferability failure named is H2CO–O off the LRA line (zwitterion), with the remark that it can still serve
  as a TM for larger Criegee intermediates (p. 5187).
- The introduction speaks generically of "disentangling local and nonlocal intramolecular interactions" in large flexible
  molecules (p. 5183); nothing quantitative follows.
- **Stated limitations (Conclusions, p. 5190):** (i) no automatic selection of templating molecules; (ii) "the quite high
  cost of the underlying quantum chemical computations for large systems (especially concerning the computation of
  vibrational corrections)"; (iii) restriction to "semirigid neutral molecular species containing only main group
  elements". "Work along these lines is providing new exciting perspectives" — no vibrational extension announced.
- `INFERENCE`: limitation (ii) is exactly the gap the group's 2026 fragment-space vibrational papers address; the 2023
  paper is the point where they name the full-molecule vibrational step as the bottleneck. Cations are excluded by
  limitation (iii) (relevant to our cation rows, obstacle 9).

## 5. The report's wording (grep, 11 Nov 2026)

Lines from `reports/Grote PAK uit overlappende fragmenten.md` that touch this paper or the Lego/templating line:

1. **Line 3:** "The Lego-brick and templating-synthon work stops at geometries." — **Holds for Nano-LEGO 2023.**
   `CORRECTION` (precision, not error): these papers do compute vibrational quantities (VPT2 ΔB_vib with cubic force
   constants) but on the whole target at DFT, never assembled from fragments. Suggested: "The Lego-brick and
   templating-synthon work transfers only geometries; its vibrational corrections to rotational constants are computed
   on the whole molecule, and Barone et al. (2023) name their cost as a main limitation."
2. **Line 36:** "The Pisa–Bologna line moved from fragments for structures to topology-dependent corrections for
   vibrations over 2022–2026" and "The Lego-brick approach assembles PAH and PANH equilibrium structures…" — the second
   sentence is about Ye et al. 2022 (Bologna, Puzzarini), not Nano-LEGO. `CORRECTION` (clarity): Nano-LEGO (Pisa:
   Ceselin/Barone/Tasinato, 2021, 2023) is a separate tool and was **never tested on a PAH** in the 2023 paper (largest
   test molecule 12 atoms, single rings). If the report cites Nano-LEGO 2023 anywhere as PAH evidence, that is wrong; at
   present it does not (grep shows no such sentence).
3. **Line 60:** "Lego-brick needed a template correction even for geometries." — consistent with this paper (TMA for the
   ring, LRA for the linkage, p. 5189); no change.
4. **Line 72 (claim box):** "fragment templates (Lego brick) for PAH geometries" — refers to Ye 2022; fine. Nano-LEGO
   2023 adds nothing vibrational, so the claim box survives this paper unchanged.
5. **Line 84, open item 7** ("Di Grande 2024 and Nano-LEGO 2023 full texts — Confirm they contain no vibrational
   section"): `CORRECTION` — **resolved for Nano-LEGO 2023**: no vibrational section; only full-molecule ΔB_vib for
   rotational constants. The item stays open for Di Grande 2024 only.
6. **Line 107, source table** ("Barone et al., J. Phys. Chem. A 2023, Nano-LEGO refinement | not in notes"):
   `CORRECTION` — DOI 10.1021/acs.jpca.3c01617; J. Phys. Chem. A 127, 5183–5192 (2023); read in full, notes in this file.
7. **Line 5** lists the papers read in full (four); `CORRECTION` — add Barone 2023 when the report is next revised.
8. Not cited in the report: the original Nano-LEGO paper, Ceselin, Barone, Tasinato, J. Chem. Theory Comput. 17,
   7290–7311 (2021) (ref 18 here), "Pick the Bricks and Build Your Geometry", and Melli et al., J. Phys. Chem. A 125, 9904
   (2021) (ref 19, template + LRA on top of DFT). Neither was read; by this paper's description both are geometry-only.
