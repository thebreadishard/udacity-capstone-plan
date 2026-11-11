# Collins 2014 — SMFA forces, geometries and frequencies (full-text read)

M. A. Collins, J. Chem. Phys. 141, 094108 (2014), doi 10.1063/1.4894185. Read whole, 11 Nov 2026, from the local PDF
(`Papers/Collins_2014_SMFA_forces_frequencies_JCP141_094108.pdf`, 14 PDF pages: page 1 is the AIP cover, journal pages
094108-1 to -13 are PDF pages 2–14). Text extracted with PyMuPDF (no page renderer installed); tables read from the
extracted text, columns checked against the captions. Page references below are journal pages, "p. -N" = 094108-N.

**Corrections to the report are marked `CORRECTION`.** Inferences of ours (not stated in the paper) are marked `INFERENCE`.

## 1. How the Hessian is assembled

- **Groups and bonds (App. A, p. -12).** Every atom goes into a functional "group". Two atoms are single-bonded if their
  distance is below the sum of covalent radii + 0.4 Å; a single bond becomes a *multiple* bond if the distance is below
  the sum + 0.08 Å, unless an atom already has its normal valence (C four single bonds, N three, O two). Atoms joined by a
  multiple bond are in the same group; H goes with its heavy atom. Formally charged atoms absorb single-bonded neighbours
  (–(CH2)COO⁻ is one group). Hydrogen bonds (O/N–H···O/N within 2.4 Å) can be declared as bonds that are broken without a
  cap; for water clusters they are the only inter-group bonds.
- **Fragmentation (Sec. II A, p. -2, Eq. 2.2).** Groups are linked by single bonds; Level L keeps each group with its
  substituents out to L bonds (Level 1 α, Level 2 β, …). Chain example G1…G5: Level 1 = G1G2 + G2G3 + G3G4 + G4G5 − G2 − G3 − G4;
  Level 2 = G1G2G3 + G2G3G4 + G3G4G5 − G2G3 − G3G4; Level 3 = G1G2G3G4 + G2G3G4G5 − G2G3G4. Integer coefficients f_n, balanced:
  every group counts a net once (p. -3). This is inclusion–exclusion over overlapping fragments; it is defined by bonded
  connectivity, not distance (p. -1).
- **Rings (p. -8).** Small rings cannot be fragmented, because partial-ring fragments put caps too close together: rings
  of up to 5, 6, 7, 8 groups cannot be fragmented at Levels 2, 3, 4, 5 or above. To fragment α-helices the amide C–N
  (default: multiple) was set to single for the 38-molecule set (p. -8); the protein conformers used the default
  (amide C–N multiple, p. -9).
- **Aromatic / conjugated groups.** The paper states no explicit "do not break aromatic bonds" rule; it follows from the
  bond rule: a multiple bond is never cut, both atoms share a group. For the proteins it says the aromatic His and Phe
  side chains impose "a lower limit on the size of the largest fragments" (p. -10). `INFERENCE`: aromatic C–C (≈1.39–1.42 Å)
  is shorter than 2 × r(C) + 0.08 Å and the ring carbons are three-coordinate, so a benzene ring is one group, and in a
  fused PAH every C–C bond is "multiple": the whole carbon skeleton with its H atoms becomes **one group**, i.e. SMFA as
  defined here cannot fragment a PAH at all. Not tested or discussed in the paper.
- **Caps (Eq. 2.3, p. -2).** H cap placed on the broken bond j–m at X(H) = X(j) + [(r(j)+r(H))/(r(j)+r(m))]·[X(m) − X(j)]
  (standard covalent radii); fragment atoms keep their exact positions in the whole molecule, so a cap has the same
  position in every fragment. Cap gradient is redistributed onto j and m with the fixed Jacobian of Eq. 2.7 (p. -3): a
  link-atom Jacobian with ratio g = (r(j)+r(H))/(r(j)+r(m)). The author calls these cap contributions "based on guesswork"
  but argues they cancel because caps appear with coefficients summing to zero (p. -3, p. -12).
- **Hessian (Eq. 2.15, p. -4).** ∂²E_b = Σ_n f_n ∂²E(F_n), cap contributions mapped through Eq. 2.7. Single level of
  theory throughout: no low-level full-molecule Hessian, no high-minus-low correction. Fragment Hessians from Gaussian 09.
- **Embedded charges (Sec. II A, App. B, pp. -2, -12, -13).** Point charges from Natural Population Analysis of each single
  group (capped), cap charge moved onto its heavy atom; charges placed on atoms (c_mj = 0 or 1, Eq. 2.11–2.12). Default:
  only formally charged groups get charges; optionally highly polar groups (water, amides). Gradient on charges from the
  Hellmann–Feynman field (Eq. 2.9), sum rule holds to ~1e-6 a.u. (Eq. 2.10, p. -4); Hessian diagonal block from the field
  gradient (Eq. 2.14); **off-diagonal second derivatives between fragment atoms and charge-represented atoms are neglected**
  (p. -4). Double counting of charge–charge pairs must be corrected (p. -3). Distributed-multipole embedding tried and found
  unnecessary (p. -13).
- **Non-bonded / long-range (Sec. II B, pp. -4 to -6).** Interactions between groups never in a common fragment, computed
  between Level-1 × Level-1 fragments (L1 = L2 = 1 "sufficient", p. -5), with editing to "allowed" pairs. Ab initio
  dimer-minus-monomers (Eq. 2.19) if any atom pair has distance / (sum of van der Waals radii) < d_tol; default d_tol = 1.1
  for energies (p. -8), d_tol = 0 at Level 2 (to avoid cap clashes), d_tol = 2.1 recommended for geometries and
  frequencies, 3.1 used for (Gly)₁₂ (pp. -10, -11). Beyond d_tol: GDMA distributed multipoles to hexadecapole (Eq. 2.20),
  dispersion from group polarisabilities (Eq. 2.22; not evaluated for HF), induction (Eq. 2.25, only without embedded
  charges). Their gradients and Hessians use only the derivatives of the T tensors; multipole and polarisability
  derivatives are neglected (Eqs. 2.21, p. -5; p. -6). Finite d_tol makes the gradient discontinuous (p. -6).
- **Why it works, per the author (p. -11/-12):** large forces come from the Level-L bonded fragments; caps cancel; the
  crudely treated long-range forces are small.

## 2. Test systems and errors

Energies and gradients only (no frequencies):
- **38 CSD structures** (p. -7): 24 neutral (sugars, peptides, misc.; 42–169 atoms, mean 64) and 14 ions/zwitterions (62–180
  atoms, mean 93); HF/6-31G. Energy MAE converges to a few kJ/mol, generally by Level 4 (Fig. 3, p. -8). Mean 24.5 groups
  per molecule; fragments 6.6 groups at Level 3, 9.3 at Level 4 (p. -8). Gradient MAE (Fig. 4, p. -9): Level 4, d_tol 1.1:
  5.5e-4 Eh/bohr with E_ele gradients, 6.0e-4 without; ions 2.7e-4 with charge forces, 2.8e-4 without. Level 4 and
  d_tol ≈ 2 recommended for optimisation. The paper says this set contains aromatic rings (p. -7), but gives no per-molecule
  aromatic analysis.
- **20 protein conformers**, 2KA5 terminal chain, 246 atoms (245 neutralised), HF/6-31G, whole molecule 1410 basis
  functions (pp. -7, -9). Relative energies converged at Level 3, conformer range ~367 kJ/mol (Figs. 5–6, p. -9/-10).
  Gradient MAE at Level 4 below 3e-4 for d_tol above ~1.8 (Fig. 7, p. -10). Largest fragment 241 (Level 4) / 183 (Level 3)
  basis functions (p. -10), set by the aromatic side chains.

Frequencies (the only two frequency tables). **Frequencies are computed at each method's own optimised geometry**:
SMFA frequencies at the SMFA minimum against whole-molecule frequencies at the whole-molecule minimum (Table I caption,
p. -10; p. -11), so the frequency error includes the geometry error. The paper does not say how modes were paired, and
gives **no breakdown by frequency range** and no mode assignment of the maximum errors.

**Table I (p. -10): NH₃⁺(CH₂)ₙCOO⁻, n = 5–9, Level 3, d_tol = 2.1** (the caption writes NH₃⁺CH₂(CH₂)ₙCH₂COO⁻ — the
paper is inconsistent on chain length). Fragment basis sizes not given.

| n | HF/6-31G ⟨\|δω\|⟩ / max (cm⁻¹) | MP2/6-31+G(d,p) ⟨\|δω\|⟩ / max (cm⁻¹) |
|---|---|---|
| 5 | 0.6 / 3.9 | 0.9 / 4.2 |
| 6 | 0.6 / 3.1 | 1.2 / 4.7 |
| 7 | 0.7 / 3.3 | 1.1 / 3.7 |
| 8 | 0.7 / 2.0 | 1.3 / 8.7 |
| 9 | 0.7 / 2.9 | 1.4 / 9.4 |

Energy errors −0.34 to −0.95 kJ/mol (HF), −1.20 to −3.38 (MP2); bond-length MAE 1.5–2.2e-4 Å. MP2 errors "slightly
larger" (p. -10); the MP2 mean and max grow with chain length (0.9 → 1.4 mean, 4.2 → 9.4 max). These are the only
correlated-level frequencies in the paper.

**Table II (p. -11): HF/6-31G(d), systems from Hua et al. 2008 (GEBF, ref. 54).** "Basis" = largest single fragment /
whole molecule.

| System | Level | Basis | ⟨\|δω\|⟩ (cm⁻¹) | max \|δω\| (cm⁻¹) | dihedral MAE (deg) |
|---|---|---|---|---|---|
| GelA | 3 | 216/710 | 0.8 | 6.3 | 0.32 |
| GelB | 3 | 178/706 | 0.7 | 10.5 | 0.30 |
| (H₂O)₂₈ | 2 | 114/532 | 5.7 | 62.2 | 57.41 |
| (H₂O)₂₈ | 3 | 209/532 | 2.5 | 17.1 | 27.18 |
| (H₂O)₂₈ | 2 (chgs) | 114/532 | 1.6 | 17.3 | 10.69 |
| (H₂O)₂₈ | 3 (chgs) | 209/532 | 0.7 | 8.0 | 0.26 |
| (Gly)₁₂ | 3 (chgs) | 140/881 | 2.4 | 8.8 | 4.82 |

GelA/GelB are "largely alkanes with two charged nitrogen or oxygen containing groups" (p. -8); charges on the formally
charged groups only (p. -11). (H₂O)₂₈: NPA charges of isolated monomers; H bonds counted in the geometry measures; charges
make geometry and frequencies "much more accurate" (p. -11). (Gly)₁₂: α-helix, charges on the 13 amide groups, no H bonds
declared, d_tol 3.1; "similar accuracy was not possible" without charges (p. -11). Atom counts for the Table II systems are
not given in this paper. SMFA is judged comparable or better than GEBF, often with smaller fragments (p. -11).

**Worst cases and why (as far as the paper says):** (H₂O)₂₈ without embedded charges (Level 2: 5.7 / 62.2 cm⁻¹; Level 3:
2.5 / 17.1) — dense polar H-bond network, many-body induction missing, soft dihedrals off by 27–57° (p. -11). (Gly)₁₂ has
the largest mean among the carried rows (2.4) and a 4.8° dihedral error. MP2 chains show the max error growing with
length. Which individual modes carry the maxima is not reported.

## 3. Aromatic, conjugated, PAH; delocalised and low modes

- **No aromatic, conjugated or PAH system has a frequency test.** Aromatics appear only in the energy/gradient sets (38
  CSD molecules, p. -7; His/Phe side chains in the proteins, p. -10), and there the ring is kept whole inside one group —
  it raises the largest-fragment size rather than testing a cut through conjugation.
- **Nothing on delocalisation error, π conjugation, or limits for conjugated systems.** The only conjugation-related
  statements are the bond rules (App. A) and the aromatic lower bound on fragment size (p. -10). `INFERENCE`: under these
  rules a fused PAH is a single group and SMFA would return the whole molecule as its one fragment; the method gives no
  evidence either way on cutting through a π system.
- **Low-frequency / delocalised modes:** one sentence and one figure. Fig. 8 (p. -11) plots the highest and lowest
  frequencies of the MP2 chains, whole vs Level 3; the text says the chain-length variation of the lowest mode is well
  reproduced "even though this mode is a delocalised cooperative motion of the whole chain" (p. -10). No numbers are given
  for it in the text. For water, the soft dihedrals are the sensitive coordinates (p. -11).

## 4. Check of our report (`reports/Grote PAK uit overlappende fragmenten.md`)

Report mentions: line 3 (summary), line 13 (paragraph), line 21 (table row), line 119 (reference list).

- Line 13, "at HF/6-31G(d), mean/max 0.7/10.5 to 2.4/8.8 cm⁻¹ on gelatin fragments and (Gly)₁₂": numbers correct
  (GelB 0.7/10.5, (Gly)₁₂ 2.4/8.8; Table II, p. -11), but the range skips GelA 0.8/6.3.
  `CORRECTION` (wording): **"gelatin fragments" is not in this paper.** GelA and GelB are labels taken from Hua et al. 2008;
  Collins describes them only as "largely alkanes with two charged nitrogen or oxygen containing groups" (p. -8). Write
  "two charged, mostly aliphatic molecules (GelA, GelB of Hua et al. 2008)" unless the Hua paper confirms gelatin.
- Line 13, "0.7/8.0 cm⁻¹ on (H₂O)₂₈ with embedded charges": correct, **Level 3 with charges** (Table II). Worth adding that
  without charges it is 2.5/17.1 (Level 3) and 5.7/62.2 (Level 2).
- Line 13, "at HF/6-31G(d)": correct for Table II only. `CORRECTION` (omission): the paper also has **MP2/6-31+G(d,p)**
  frequencies (Table I, zwitterion chains, mean 0.9–1.4, max 3.7–9.4 cm⁻¹) and HF/6-31G (mean 0.6–0.7, max 2.0–3.9). The
  overall SMFA mean range is therefore **0.6–2.4 cm⁻¹**, not 0.7–2.4, if Table I is included.
- Line 21, "140–216 of 532–881 basis functions": acceptable as the range of the *largest* fragment per system over the
  carried rows (140/881, 178/706, 209/532, 216/710), but the pairing reads as if 140 belonged with 532. Better:
  "largest fragment 140–216 basis functions against 532–881 for the whole molecule". The Level-2 water row uses 114/532.
- Line 21, "mean 0.7–2.4, max 6–17 cm⁻¹": `CORRECTION`: **the maximum range is 6.3–10.5 cm⁻¹** for the configurations the
  report cites (GelA 6.3, GelB 10.5, (H₂O)₂₈ L3 chgs 8.0, (Gly)₁₂ 8.8). The 17 comes only from non-carried rows
  ((H₂O)₂₈ Level 3 without charges, 17.1; Level 2 with charges, 17.3), and the same table also has 62.2 for Level 2 without
  charges. As written the table row contradicts line 13 of the same report (max 8.0–10.5). Including Table I the
  max range is 2.0–10.5.
- Line 21, systems "gelatin, (Gly)₁₂, (H₂O)₂₈": `CORRECTION`: "gelatin" as above; and the zwitterion chains
  NH₃⁺(CH₂)ₙCOO⁻ (Table I) are missing.
- Line 3, "Plain fragment Hessians at one level (… SMFA 2014 …)": correct — single level, no cheap full Hessian (Eq. 2.15).
  "where errors are reported, they run from 0.7 to 5 cm⁻¹ mean": SMFA's lowest mean is 0.6 (Table I); harmless for the
  overall range. "Every one of these benchmarks is on peptides, proteins, carbohydrates, water clusters or molecular
  crystals": for SMFA's *frequency* benchmarks the systems are zwitterionic alkane chains, two charged mostly-aliphatic
  molecules, a water cluster and polyglycine (Tables I–II) — "peptides" covers only (Gly)₁₂; the claim "not on fused PAHs"
  holds (section 3).
- Line 119 (reference): title, journal, DOI 10.1063/1.4894185 correct.

## 5. What it means for our plan (large PAH from ≤30-atom pieces)

- SMFA's own bond rules keep conjugated atoms together, so the method as published gives **no precedent for cutting a PAH**;
  the His/Phe remark (p. -10) is the only conjugation-related statement and it says aromatic rings set the minimum fragment.
- Transferable pieces: the balanced integer-coefficient inclusion–exclusion (Eq. 2.2), the fixed-ratio H-cap placement and
  its Jacobian (Eqs. 2.3, 2.7), and the d_tol switch between ab initio pair corrections and multipole terms.
- The error figures are single-level fragment-vs-whole at each method's own minimum; they are not the error of a
  correction (high − low) on top of a full cheap Hessian, which is our construction. Best case 0.6–0.7 cm⁻¹ mean, maxima
  up to 10.5 cm⁻¹ (HF) and 9.4 cm⁻¹ (MP2), growing with chain length at MP2.
