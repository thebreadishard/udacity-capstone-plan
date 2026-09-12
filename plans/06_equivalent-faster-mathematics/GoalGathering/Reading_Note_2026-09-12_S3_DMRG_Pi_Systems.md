# Plan 06 — reading note S3 (2026-09-12): quasi-one-dimensional π-systems and DMRG — what is verified, what S3 would have to be

*Verified reading only (records via Crossref and the arXiv API; one open full text read in part). No number here
is from recall; where a fact was not found in the text read, it says so. Written after X5, which gave S3 its
first data-side motivation (the correction's nonlocality at benzene is confined to the carbon ring).*

## 1. Records verified (2026-09-12)

- Hachmann, J., Dorando, J. J., Avilés, M., & Chan, G. K.-L. (2007). The radical character of the acenes: A
  density matrix renormalization group study. *J. Chem. Phys.* 127(13), 134309. DOI 10.1063/1.2768362;
  arXiv:0707.3120 (open; PDF in `Papers/plan06/`, text read in part).
- Chan, G. K.-L., & Sharma, S. (2011). The density matrix renormalization group in quantum chemistry. *Annu. Rev.
  Phys. Chem.* 62, 465–481. DOI 10.1146/annurev-physchem-032210-103338 (abstract only: "a pedagogical overview
  of the basic challenges of strong correlation, how the density matrix renormalization group works, a survey of
  its existing applications to molecular problems"; paywalled; already in the Orientation's list).
- Olivares-Amaya, R., Hu, W., Nakatani, N., Sharma, S., Yang, J., & Chan, G. K.-L. (2015). The ab-initio density
  matrix renormalization group in practice. *J. Chem. Phys.* 142, 034102. DOI 10.1063/1.4905329 (record only).
- Chan, G. K.-L., Keselman, A., Nakatani, N., Li, Z., & White, S. R. (2016). Matrix product operators, matrix
  product states, and ab initio DMRG algorithms. *J. Chem. Phys.* 145, 014102. DOI 10.1063/1.4955108 (record only).

## 2. What Hachmann et al. (2007) say that matters here (read in the arXiv text)

- Active space: "the complete π-valence space, consisting of all conjugated carbon p_z orbitals, and all π
  electrons were correlated", frozen core, RHF orbitals; STO-3G up to dodecacene, Dunning DZ up to hexacene with
  two p_z per carbon (a "double" π space). Sizes: pentacene (22, 22) in STO-3G, (22, 44) in DZ; **dodecacene
  (50, 50), "only made possible through the DMRG algorithm"**.
- Result: the acene ground states stay singlets but become polyradical with length; the singlet–triplet gap
  extrapolates to 8.69 ± 0.95 (STO-3G) / 3.33 ± 0.39 (DZ) kcal/mol for the infinite chain; DFT (UB3LYP, UBLYP)
  underestimates the gap.
- **Not found in the text read:** the number of renormalised states (bond dimension) used, and any timing. Both
  are what S3 needs and both must come from the 2011 review or the 2015 "in practice" paper (paywalled; the
  supervisor's list if S3 is pursued).

## 3. What S3 would have to be, now that X5 exists

The Orientation stated S3 as: if the entanglement across any cut of a flake's π-system is bounded, DMRG is exact
at fixed bond dimension and cheap for aromatic flakes — an E1 candidate for the π part. Three things sharpen it:

1. **S3 can only ever address a part of the anchor's correction.** X5: 93.5 % of ‖Δ₂‖²_F at benzene sits on
   atoms and bonds (σ-frame plus π), and the *nonlocal* remainder is the flat carbon-ring profile. A π-space
   DMRG (or, at benzene, an exact π-CAS) computes the π-correlation exactly *within the π space*; it says
   nothing about σ correlation, σ–π coupling, or dynamic correlation outside the active space — which is most of
   what CCSD(T) adds over DFT for harmonic force constants. So the honest form of S3 is E2: "the ring-confined,
   nonlocal part of Δ₂ is a π-space property computable at low cost; the rest is local and cheap by S1". Not an
   equivalent of the anchor.
2. **Acenes are the favourable case, PAH flakes are not.** Hachmann et al. treat linear acenes — genuinely
   quasi-one-dimensional, where DMRG orderings along the chain work. Plan 05's ladder has pyrene, chrysene,
   triphenylene, coronene: two-dimensional flakes, where entanglement across a cut grows with the cut's length
   (the reason DMRG is a chain method). Whether the *correction* Δ₂ — not the wavefunction — has bounded
   entanglement across cuts is exactly the open mathematical question S3 poses, and X5's flat ring profile is
   the first sign that at least at benzene the answer is "ring-sized, not bond-sized".
3. **The first own number needs no DMRG at all.** At benzene the complete π-valence space is CAS(6, 6): exact
   CASCI is trivial. A finite-difference curvature of E_CASCI(6,6) − E_HF along plan 05's three probed modes,
   compared with the sealed cc-pVTZ line's CCSD(T) − DFT curvature, prints how much of the ring-mode correction
   the π space carries. That is **X6**, defined here: cheap (minutes; pyscf CASCI at 6-31G* on the dry-run
   geometry), on existing geometries, but compute — so after the anchor job. Its losing condition: if the π-CAS
   correction is less than half of the CC − DFT correction along the C–C stretch mode, S3 is closed as an E1/E2
   route for the anchor and survives only as "the π part of a decomposition".

## 4. Ledger

S3: proposed → **literature partly read; X6 defined** (π-CAS share of the ring-mode correction at benzene; compute,
after the anchor job). Bond dimensions and timings still to be read from the 2011/2015 papers (paywalled) before
any DMRG number is quoted. The review's cost-scaling statement is deliberately not reproduced here: it was not
read.
