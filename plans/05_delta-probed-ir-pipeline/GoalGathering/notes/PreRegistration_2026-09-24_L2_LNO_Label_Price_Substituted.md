# Pre-registration 2026-09-24, 22:2x — L2: the LNO-CCSD(T)/cc-pVDZ price of one substituted molecule (lever 2 of the evening odds; the user: "Doe 1")

**Why.** After E9 (21:5x) the cost of a substituted label on the proxy is the cost of its neighbourhood. What that neighbourhood costs at the
coupled-cluster level has never been measured on a real substituted molecule: the anchor priced naphthalene at cc-pVTZ (≈ 9 h per LNO-CCSD(T)
energy on the laptop, eight threads), E8 priced a canonical CCSD(T)/cc-pVDZ gradient of naphthalene at 20,998 s on the CCX53. This measurement
prices one LNO-CCSD(T)/cc-pVDZ energy of a 25-atom substituted molecule at the anchor's thresholds, on the CCX53's idle cores, beside the
running naphthalene E8 (five processes in their single-threaded (T) phase; load 9 of 32, 52 GB free at 22:1x).

**Molecule (fixed).** phenanthrene+CN, corpus id `A2_0f86544b37` (C₁₅H₉N, 25 atoms, 16 frozen 1s cores), at its corpus B3LYP/6-31G* geometry —
the admitted E9 molecule closest to the E9 mean size with a rigid one-heavy-atom-plus-one substituent; neighbourhood at r = 2: five atoms.

**Deck (fixed; the anchor's, basis cc-pVDZ).** DF-RHF, conv 1e-11; Pipek–Mezey localisation of the active occupied orbitals with Jacobi stability
sweeps; LNO-CCSD(T) with one fragment per localised orbital, thresholds tight [1e-6, 1e-7], frozen core = number of heavy atoms; DF-MP2 (frozen
core) for the composite E_SCF + E_LNO-CC − E_LNO-MP2 + E_MP2. pyscf 2.14 + pyscf-forge 1.1.1 (the laptop's LNO code), eight threads,
max_memory 16,000 MB, in a cloned environment `qclno` so the running naphthalene processes' environment is not touched.

**Points (fixed).** Three energies: the reference geometry and q = ±1 along the B3LYP normal mode (projected Hessian of the corpus) with the
largest mass-weighted amplitude on the E9 neighbourhood atoms (substituent + ipso + ortho), displaced as the anchor displaces
(x = x₀ + L q / √ω · M^{-1/2}). Water first (smoke, the same script with `--smoke`), then the molecule.

**Read-outs (fixed).** Per point and per stage (SCF, localisation, LNO-CCSD(T), MP2): wall seconds and peak RSS; the number of fragments; the
composite curvature along the mode against B3LYP's own (ω′ = ω √(k/k_B3LYP), printed as a sanity line, not judged). The price: **P = wall seconds
of one LNO-CCSD(T)/cc-pVDZ energy** (the mean of the three points), at eight threads beside the naphthalene processes.

**Reading (fixed before any number).** The label a substituted molecule needs, under E9, is the neighbourhood: with gradients 2 × 3 × 5 = 30
of them (no LNO gradients exist); with energies, the near × near block by directional second differences, ≈ 2·15 + 2·105 = 240 energies for five
atoms (whether energies suffice at all is the post-hoc E9 variant (d) of 22:2x, run tonight on the proxy). So:
- **Pass:** P ≤ 30 min → a 240-energy neighbourhood label ≤ 5 days on eight threads, ≈ 1.3 CCX53-days with four such runs side by side;
  the cost line of the odds moves up again and lever 2 continues with the block measurement on this molecule.
- **Fail:** P > 2 h → the neighbourhood label alone exceeds a CCX53-week per molecule; the energy route is out for substituted molecules and the
  cost line stays; the next lever is a cheaper correlation level for the probe (LNO-CCSD without (T), or MP2-anchored decks per family).
- **Between:** 30 min < P ≤ 2 h → reported as such; the thread scaling (a second run at 16 threads once naphthalene E8 is done) decides.
- Not registered: anything read from the curvature sanity line; the choice of the next molecule.

**Cost.** ≈ 3 × P plus minutes; nothing is bought; the naphthalene processes keep their cores (they use ≈ 13 of 32) and memory (16 GB cap here,
52 GB free).

Script `probes/l2_lno_price.py`; server directory `/root/l2/`; results `probes/results_m1/l2_phenanthrene_CN_ccpvdz/` (log, `l2_price.json`).
