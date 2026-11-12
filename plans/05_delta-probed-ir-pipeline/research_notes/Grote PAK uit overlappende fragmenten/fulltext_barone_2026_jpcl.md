# Barone, Crisci, Lazzari, J. Phys. Chem. Lett. 17, 10555–10561 (2026) — full text

"Integrating Local and Normal Modes for Multilevel Vibrational Spectroscopy". DOI 10.1021/acs.jpclett.6c02504, received
25 Jul 2026, published 4 Sep 2026 (p. 10555). Read in full on 12 Nov 2026 from the local PDF (7 pages, PyMuPDF text; p. 10558
viewed as an image for eqs 3–4 and Figure 4). **The SI is not in the PDF**; per p. 10560 it holds the full four-system tables
(frequencies, cost, overlaps), alternative coupling means, cross-geometry transfer, open-shell and transition-metal tests,
adaptive diagnostics. The SONIC coordinates themselves are in a separate preprint (ref 9, arXiv:2607.16550; p. 10556).

## Verdict for our claim

- **No fragments, no cross-molecule transfer, no PAH.** One molecule at a time; L0 gives the full coupled force field, L1
  gives diagonal curvatures only (p. 10556, 10558). Fragmentation appears once, as an outlook: it "can supply the same
  directional curvatures" for larger systems (p. 10560). The narrow claim of TASKS 199 stands.
- **Largest test: ferrocene, 57 modes (21 atoms); aromatics are uracil, p-EBN (39 modes), phenol** (p. 10558, 10560). No
  fused ring system.
- **Off-diagonal couplings are not learned or computed: they are L0 couplings rescaled**, F_ij = √(K_i K_j) F⁰_ij with
  K_i = F¹_ii/F⁰_ii (eqs 3–4, p. 10558). "No L1 off-diagonal force constant was calculated" (p. 10556).
- **Anchor cost: possibly, with a caveat that matters for training.** Up to 2N one-dimensional L1 energy curvatures replace
  a full L1 Hessian, at 0.59–1.13 cm⁻¹ RMS from it (p. 10558). But the off-diagonal ΔH of such an anchor would be a fixed
  function of the diagonal ratios and L0, so it carries no independent coupling label (our inference). It could serve as a
  frequency-level anchor for the large PAHs, not as a ΔH training target for couplings.

## 1. What is done

- L0 = affordable model for geometry, full harmonic field and modes ("typical" B3LYP-D3(BJ)/6-31+G*); L1 = "advanced
  double-hybrid functionals" with analytic Hessians in Gaussian 16, so that full L1 Hessians serve as noise-free references
  (p. 10555). The exact L1 functional per fixture is not named in the main text.
- Three routes at matched L1 budget (p. 10556): (a) concordant modes (CM): diagonal L1 curvatures along L0 normal modes,
  mass-weighted Cartesian metric, N curvatures; (b) SONIC pass 1: diagonal L1 curvatures along symmetry-adapted
  non-redundant internal coordinates (Wilson G metric), congruence scaling eqs 3–4, N curvatures; (c) sequential: (b), then
  re-diagonalise (eq 5, GF⁽¹⁾L = LΛ) and run a CM pass on the new directions, 2N curvatures in total.
- Adaptive second pass: modes ranked by rotation from L0 modes and frequency spread over five coupling treatments;
  batches of three until the predicted remainder is ≤ 0.5 cm⁻¹ RMS and ≤ 2.0 cm⁻¹ max (p. 10558).
- Fixtures: uracil, p-EBN, phenol, glycine II transition structure (p. 10558); cyclohexane at four stationary points and
  12 cross-geometry transfers (p. 10559–10560); ferrocene, D5d, L0 = RHF, L1 = B3LYP (p. 10560); cyclobutane HF/STO-3G as a
  locality control (p. 10557).

## 2. Errors against reference

All references are the full L1 Hessian at the same geometry unless stated.

| Molecule | Quantity | Route | Value | Page |
|---|---|---|---|---|
| uracil / p-EBN / phenol / glycine II | freq RMS, L0 | — | 12.0 / 16.4 / 15.6 / 29.0 cm⁻¹ | Fig 4, 10558 |
| same | freq RMS | CM, N | 1.94 / 1.49 / 0.86 / 1.26 cm⁻¹ | 10558 |
| same | freq RMS | SONIC pass 1, N | 3.88 / 3.65 / 3.26 / 6.22 cm⁻¹ | 10558 |
| same | freq RMS | two-step, 2N | 0.59 / 1.00 / 1.13 / 1.08 cm⁻¹ | 10558 |
| uracil / p-EBN | adaptive pass 2 | 27/30, 33/39 curvatures | 0.23 / 0.25 cm⁻¹ from full pass 2 | 10558 |
| four fixtures | unsupplied coupling correlation | SONIC | 0.9867–0.9994; rel. error 0.037–0.171 | 10559 |
| four fixtures | rotation residual / eigenvalue residual (CM = 1 / 0) | SONIC | 0.27–0.79 / 0.07–0.24 | 10557 |
| cyclohexane, 4 structures | freq RMS | CM / two-step | 0.46–1.39 / 0.36–1.01 cm⁻¹ | 10559 |
| cyclohexane, 4 structures | coupling correlation | SONIC | 0.949–0.996 | 10559 |
| cyclohexane, 12 transfers | fixed-geometry freq RMS | additive ΔF from N source curvatures | 27.20 → 5.80 cm⁻¹ (oracle, full source ΔF: 4.51) | 10559–10560 |
| ferrocene, 56-coord block | freq RMS | L0 / CM / two-step | 91.52 / 7.79 / 5.27 cm⁻¹ | 10560 |
| ferrocene | coupling pattern | SONIC | rel. error 0.113, corr. 0.9936 | 10560 |
| uracil | mean assigned L0/L1 mode overlap | — | 0.975 | 10560 |
| uracil | off-diagonal Frobenius fraction | Cartesian → local | 0.50 → 0.18 | 10560 |
| cyclobutane (HF/STO-3G) | normalised coupling, mean / 95th pct | Cartesian → frozen local → sym-adapted | 0.151/0.394 → 0.028/0.085 → 0.013/0.056 | 10557 |

No error bars by design: "deterministic diagnostics of the stated fixtures" (p. 10559).

## 3. Method details that matter for us

- **How curvatures are obtained.** In every benchmark the L1 directional curvatures are read from the analytic L1 Hessian
  (noise-free); production would use "one-dimensional energies along frozen L0-derived directions" (p. 10558). **No step
  size, stencil or convergence threshold is given in the main text**, and no production finite-difference run is reported.
  The noise of energy second derivatives is therefore untested here.
- **Cost count.** ≤ N curvatures per one-pass route, ≤ 2N for the full route, independent and parallel (p. 10556, 10560). In
  energies, a 3-point stencil would be about 2 energies per curvature plus one reference, i.e. ≈ 4N+1 energies for the full
  route (our inference). For our anchors: if they are finite differences of analytic CCSD(T) gradients (6·N_atoms gradients
  without symmetry), 4N ≈ 12·N_atoms CCSD(T) energies is comparable, and one pass (≈ 6·N_atoms energies) cheaper only by
  the gradient/energy cost ratio (our inference; not in the paper).
- **Common geometry.** G, F⁰ and the L1 reference are evaluated at one geometry (p. 10558); production uses no L1
  optimisation (p. 10555). Errors exclude the L0→L1 geometry shift.
- Cross-irrep elements set to zero before scaling (p. 10558). Geometric mean is a default, not shown optimal; other means
  in the SI; "only a marginal influence after a complete second pass" (p. 10559).
- Relation to CMA: CM here is CMA's concordant-mode diagonal at N curvatures (refs 4, 5). CMA-2 picks off-diagonal elements
  to compute at the target level from the B/C level response; Barone objects that this assumes L0–L1 and L1–L2 sensitivity
  patterns agree, and computes no off-diagonals at all (p. 10556).
- Relation to our ΔH (our inference): eqs 3–4 are a parameter-free, physics-based model of local-coordinate ΔH, ΔF_ij =
  (√(K_i K_j) − 1) F⁰_ij. It is a natural baseline for our learned head: if our net cannot beat it given the same diagonal,
  the couplings it learns add nothing. Its locality result (cyclobutane, uracil) agrees with our finding that local ΔH is
  learnable and mode-basis couplings are not.
- The 12 cyclohexane transfers are the only transfer of a correction to a structure where no L1 data was taken: even the
  full exact source ΔF leaves 4.51 cm⁻¹ (p. 10559–10560), a floor for any copy-the-correction scheme between structures.

## 4. Pitfalls that matter for us

- **The coupling correlation 0.987–0.999 measures the full couplings, which L0 already dominates**, not the L1−L0 change in
  them. The "unchanged" L0 couplings are one of the alternatives in the SI (p. 10558), and the choice of mean barely matters
  after pass 2 (p. 10559). So the number does not show that coupling corrections are recovered (our reading).
- **Sign changes break the multiplicative scaling.** A curvature with opposite signs at L0 and L1 gives a non-real √K:
  half-chair cyclohexane (p. 10560) and ferrocene's A1u Cp rotation, excluded from scaling (p. 10560). Our analogue: soft
  out-of-plane PAH modes where B3LYP and the higher level disagree in sign at a non-minimum geometry.
- **Localised modes coupled to a delocalised sector.** Phenol's OH stretch: the two-step route (1.13) is worse than CM (0.86),
  because its ring coupling is not corrected (p. 10558). Large-PAH delocalised modes may be the same case.
- **Frequencies only at an L0 geometry.** No L1 geometry, no intensities.
- **"p-EBN" is named "para-ethylbenzonitrile" (p. 10558) but called a 39-mode C2v aromatic**; ethylbenzonitrile has 19 atoms
  (51 modes) and is not C2v, para-ethynylbenzonitrile (15 atoms) fits (our inference). Check against the SI before citing.

## 5. Check of our report

Grep of `reports/Grote PAK uit overlappende fragmenten.md` for Barone/JPCL/10555/"local and normal":

- **Line 42** ("at most 2N higher-level curvatures ...; coupling correlations 0.987–0.999"; "single-molecule Δ-Hessian by
  probing ...; no cross-molecule transfer"): **holds** (abstract; 0.9867–0.9994 on p. 10559). Refine: the main route is a
  multiplicative congruence scaling of F⁰, not an additive ΔH; an additive ΔF appears only in the cyclohexane cross-geometry
  transfer (p. 10559), which the row could mention.
- **Line 56** ("a few high-level probe columns of the large molecule itself, as E9 and the JPCL 2026 curvature-probing scheme
  both use"): **does not hold for JPCL.** It probes diagonal curvatures only; columns from L1 gradients are named as a future
  extension outside the method (p. 10558). Suggested: "a few high-level probes of the large molecule itself (columns in E9,
  diagonal curvatures in JPCL 2026)".
- **Line 92** ("Barone's JPCL 2026 probing paper does not cover [the hybrid] across molecules"; "one paper away"): **holds**,
  and is strengthened by p. 10560, where fragmentation is named as a source of the same curvatures.
- **Line 5** ("the closed Barone ones ... still read as abstracts only") and **line 100** (status "closed"): now out of date
  for this paper; full text read 12 Nov 2026, SI not.
- **Line 79** (questions "cm⁻¹ errors, any polycyclic case in the SI"): cm⁻¹ errors answered (section 2); no polycyclic case
  in the main text; the SI is unread.
- Line 3's "tested on PAHs" refers to JCP 165, 064104, not to this paper; nothing to correct here.
