# Crisci, Lazzari, Uribe, Barone, J. Chem. Phys. 165, 064104 (2026), 17 pp. — full text

"Topology-dependent refinement of molecular structures and vibrational properties". DOI 10.1063/5.0343929; submitted
15 May 2026, published 10 Aug 2026 (p. 1). Read in full on 12 Nov 2026 from the local PyMuPDF text (18 PDF pages, page 1 a
publisher cover); Figures 2, 3, 4, 8 and 9 viewed as images. **No SI exists**: the paper cites none, and data are "available from
the corresponding author upon reasonable request" (p. 14). Page numbers are journal pages 064104-n (PDF page = n + 1).

## Verdict for our claim

- **Nothing vibrational is transferred from small PAHs to large PAHs.** The topology-dependent layer corrects **bond lengths**
  (and H-bond distances), judged by rotational constants only (pp. 4–5, 7–10). PAH vibrations appear in one figure: harmonic L0
  and L1 IR spectra of fluoranthene, described as "nearly superimposable", with no cm⁻¹ number (p. 12; Fig. 8, p. 11).
- **"Topology" means the choice of space in which the residual is compact** (covalent bond field, atom-pair space, mode
  space, fragment space; Fig. 1, p. 3). The bond graph enters through a smooth distance switch on covalent radii (eqs 5–6, p. 4);
  conjugation is a Gaussian in bond length applied to C=C and C=S only (eqs 8–9, p. 5). No ring, aromaticity or sextet descriptor.
- **The vibrational "mode space" is one mode**: the C≡N stretch of 3-cyanofluoranthene, shifted by −80 cm⁻¹ carried over
  from benzonitrile (77 cm⁻¹ L0→L1 there, 73 cm⁻¹ in the target; p. 12). This is the only cross-molecule vibrational transfer in
  the paper, and the closest thing to our idea: a small molecule's per-mode Δ reused in a fused aromatic (27 atoms, my count).
- **The vibrational "fragment space" is an ONIOM partition of one molecule** (uridine, 29 atoms, my count): MAD 7.1 / 8.2 /
  7.3 cm⁻¹ against full L1 harmonics (p. 12). The pieces are cut from the target, not reused corpus molecules; no PAH.
- The authors call the vibrational part "illustrative rather than as a complete validation of ML1" (p. 13; also p. 12).
  Our idea (overlapping corpus pieces → full ΔH of a 36–60-atom PAH, checked per mode) stays unpublished as far as this paper goes.

## 1. What is done

- **Ladder** (Table II, p. 5): L0 = B3LYP-D3BJ/6-31+G* (close to our B3LYP/6-31G* baseline); L1 = rev-dsdPBEP86-D3BJ/3F12−;
  PL2/L2 = MP2-F12 + (PNO-)CCSD(T*)-F12c correction; L3 = CCSD(T)-F12/4F12 + CCSD(T)/wc3 CV. L2 is limited to "roughly
  10–15 non-hydrogen atoms" (p. 3, repeated p. 9).
- **BL1** = L1 geometry + empirical CV bond term + conjugation term (eqs 3–4, 7–9, pp. 4–5). **PL1** adds an OH···O(H)
  pair term parametrised on small sugars against L2 (eqs 10–12, pp. 5, 9–10). Weighted internal-coordinate back-transformation
  (Appendix, pp. 14–16).
- **Vibrations**: cubic/quartic force constants by finite differences of L0 analytic Hessians (p. 6). The L0/L1 equivalence of
  vibrational corrections to rotational constants is cited from ~100 molecules, "not repeated here" (p. 6). ML1 = L1 harmonic +
  L0 anharmonic, refined only in the modal subspace holding the residual (p. 12).
- **Test sets** (sizes my count): PAHs naphthalene, indene, azulene, fluorene, acenaphthylene, fluoranthene, corannulene,
  sumanene (17–33 atoms; Fig. 4, p. 7); non-conjugated controls up to testosterone/androsterone (49/51 atoms; Fig. 3, p. 7);
  3-cyanofluoranthene; small sugars, erythrose, fructose, glucose; glycine, HCO–Gly–NH₂; uridine.

## 2. Errors against reference

Rotational errors are against experimental ground-state constants, X₀ = X_e(method) − ΔX_vib(L0), unless noted.

| Molecule / set | Quantity | Level → value | Reference | Page |
|---|---|---|---|---|
| All systems (Fig. 2) | MAPE rot. const. | L0 0.877% (σ 0.205, n=9); L1 0.412% (σ 0.202, n=12); BL1 0.121% (σ 0.136, n=12); PL1 0.083% (σ 0.081, n=12) | expt. | 6 |
| Non-conjugated set, 8 mol. | mean rel. error | L0 1.412%; L1 0.391%; L1+CV 0.063% | SE/L2/expt. | 7, Fig. 3 |
| PAH set, 8 mol. | mean rel. error | L0 0.931%; L1 0.299%; BL1 0.036% | SE/L2/expt. | 7, Fig. 4 |
| Fluoranthene | MAE / MAX (MHz); MAPE / MAX (%) | L0//L0 6.07 / 9.45; 1.01 / 1.08 — L1//L0 1.96 / 3.01; 0.33 / 0.35 — BL1//L0 0.17 / 0.22; 0.031 / 0.044 | expt. (ref 37) | 8, Tab. III |
| 3-Cyanofluoranthene | MAPE | L0//L0 1.07%; L1//L0 0.34%; BL1//L0 0.03% | expt. | 10, Tab. VI |
| Glycidaldehyde / glycidol / glycolaldehyde / glycerol | MAPE, L0→L1→BL1→PL2→L2→L3//L0→L3/L1 | 1.24/0.40/0.15/0.10/0.10; 1.59/0.69/0.60/0.15/0.16/0.09/0.09; 1.55/0.82/0.73/0.23/0.15/0.10/0.08; 1.55/0.91/0.55/0.07/0.07 | expt. | 9, Tab. IV |
| Glycine I / HCO–Gly–NH₂ | MAPE, same columns | 1.45/0.50/0.20/0.20/0.20/0.04; 1.60/0.89/0.56/0.26/0.24 | expt. | 9, Tab. IV |
| Erythrose / fructose / glucose | MAPE, L1→BL1→PL1 | 0.799/0.434/0.076; 0.644/0.277/0.171; 0.633/0.265/0.263 | expt. | 10, Tab. V |
| Uridine | MAPE | L0//L0 0.441%; L1//L0 0.506%; BL1//L0 0.199% | expt. | 12, Tab. VII |
| Benzonitrile | ω(C≡N), L0 − L1 | 77 cm⁻¹ (∼80 recovers L1, "close to experiment", no number) | L1 harmonic | 12 |
| 3-Cyanofluoranthene | ω(C≡N), L0 − L1 | 73 cm⁻¹; gradient along L0 mode gives 74 cm⁻¹ | L1 harmonic | 12 |
| Fluoranthene | harmonic IR, L0 vs L1 | "nearly superimposable", no number | L1 | 12; Fig. 8 p. 11 |
| Uridine | harmonic freq., ONIOM(L1:L0) | MAD ≈ 7.1 (uracil-centred), 8.2 (sugar-centred), 7.3 cm⁻¹ (weighted) | full L1 harmonic | 12 |

No frequency is compared to experiment in cm⁻¹, and no anharmonic correction or intensity is given a number.

## 3. Method details that matter for us

- **Correction form** (pp. 4–5): r_tot = r_L1 + Δr_Conj·f_cov(r) + Δr_CV·f_cov(r), with Δr_CV = −0.0025[max(n_i,n_j) − 1]
  (eq 7) and A_Conj = −Δr_CV, Gaussian centred on the double-bond reference length, so the total correction vanishes at r_dbl
  (eq 9). Switch f_cov: s_cov = 1.3, σ_cov = 0.057 Å (p. 4). A fixed, hand-set function of bond type and length: the opposite
  end from our learned ΔH, but the same Δ-on-top-of-low-level logic.
- **Mode-space criterion** (p. 12): restricting the high-level treatment to a subspace is allowed "when the L0 and L1 normal
  coordinates are concordant" (refs 48–49, Allen/Schaefer). This is a test we could apply per mode to decide which modes a
  piece-wise ΔH must get right versus which inherit the low-level eigenvectors (my inference).
- **One-gradient shortcut** (p. 12): the L1 gradient along the L0 normal mode gave 74 cm⁻¹ against the 73 cm⁻¹ from the full L1
  Hessian. This is a single-mode curvature probe, the same idea as our E9 probe columns.
- **ONIOM vs modes** (p. 12): ONIOM when the separation lives in geometric space (weakly coupled fragments), concordant modes
  when it lives in mode space. The uridine partitions and the weighting of the two are not specified.
- **Fragment tool named but unused for vibrations**: Nano-LEGO handles "fragmentation and pattern recognition" and LCB25 supplies
  covalent reference structures (p. 6); neither feeds a force constant in this paper.
- Back-transformation: weighted minimum-change update, W = F_int is the minimum-harmonic-energy solution (eqs A5, A13–A14,
  p. 15); class-based vs unit weights differ "about two orders of magnitude less than the target structural accuracy" (p. 6).

## 4. Pitfalls that matter for us

- **Five-membered rings resist fragments**: "compact PAHs containing a five-membered ring are poorly suited to fragment-based
  shortcuts" (p. 8, fluoranthene). Our pieces near five-rings (fluoranthene-, corannulene-type) need a check.
- **Intensities change where frequencies are corrected**: in Fig. 8 (p. 11) the C≡N band of 3-cyanofluoranthene is ~78 at L0
  and ~24 at L1 (relative intensity, read from the plot by me); ML1 shifts the frequency only. A per-mode frequency transfer
  leaves intensity errors untouched.
- **Spectra plots hide 10–20 cm⁻¹ shifts**: the fluoranthene "nearly superimposable" claim rests on a 0–3500 cm⁻¹ plot with
  σ = 10 cm⁻¹ broadening (p. 12; Fig. 8 caption, p. 11). Our own B3LYP→ωB97X rms on large PAHs is 22.8 cm⁻¹, so we should not read it as "B3LYP
  harmonics of PAHs need no correction" (my inference; the levels differ).
- **Transfer is rough even for one localized mode**: 77 vs 73 cm⁻¹ (p. 12), i.e. ~4 cm⁻¹ off, already above our 3 cm⁻¹ licence bar.
- **Fragment ONIOM error ~7–8 cm⁻¹ MAD** on 29 atoms (p. 12), on a molecule with weakly coupled sugar and base. Fused PAHs are
  the strongly coupled case.
- Error averaging: Fig. 2 mixes n = 9 and n = 12 sets (p. 6); the glucose PL1 gain is 0.265 → 0.263% (p. 12).

## 5. Check of our report

Grep of `reports/Grote PAK uit overlappende fragmenten.md` for "Crisci", "topology", "064104":

- **Line 36**, "moved from fragments for structures to topology-dependent corrections for vibrations": **does not hold** for
  064104. The topology-dependent layer is structural (bond lengths, H-bond distances; pp. 4–5); vibrations get one mode shift and
  one ONIOM test, called illustrative (pp. 12–13).
- **Line 40**, "test sets include PAHs" and "transferable per-topology parameters, not explicit overlapping-fragment
  calculations": **holds** (8 PAHs of 17–33 atoms, Fig. 4). "no cm⁻¹, no PAH names or sizes in the abstract" was true of the
  abstract; the full text has cm⁻¹ numbers (73, 74, 77, 80; 7.1/8.2/7.3) and the PAH names. The row should now read "fragment space
  = ONIOM partition of uridine; mode space = one C≡N mode".
- **Line 44**, the sink condition ("explicit high-level calculations on PAH pieces, transferred to larger PAHs and checked
  against a full calculation"): **not met**. "parametrised topology classes": holds for structures. The line can drop the
  conditional.
- **Line 68**, "not per-topology parameters, as appears to be the case in 064104": **holds**; "appears" can go. Add that the one
  cross-molecule vibrational transfer is a single-mode Δω (benzonitrile → 3-cyanofluoranthene, p. 12).
- **Line 78**, open item 1 "full text and SI … closed; library or e-mail": full text now read; **no SI exists** (p. 14). Answers:
  PAHs 17–33 atoms; fragment space = ONIOM within one molecule; no small-to-large PAH vibrational transfer.
- **Line 92**, "The Barone group is one paper away from this idea": a judgement, not checkable. This paper does not move
  toward it: its PAH work is geometry only, and its vibrational transfer is one localized mode (my reading).
- Line 98 lists 064104 as "closed" access: superseded by the local copy.
