# Is our DFT anharmonic shift right for benzene? A free check against experiment (registered 14 Oct 2026, 13:0x, before any table number was read)

*TASKS 56. The pipeline's spectrum is ν = ω(CC, through the network) + Δ_anh(DFT): the hybrid scheme. A full CCSD(T) quartic force field of
benzene is not published as far as we could find (`Relevant_Scientific_Papers.md`, section of 14 Oct). What is published: benzene's CCSD(T)
harmonic frequencies near the basis-set limit (Martin, Taylor & Lee 1997, item 102) and gas-phase experimental fundamentals (Miani et al.
2000, 'MCP'), both tabulated by Boese & Martin 2004 (item 104, arXiv:physics/0311069, Tables I and II). Their difference is a
semi-experimental anharmonic shift.*

## Quantity

Per benzene fundamental: **Δ_semi = ν_MCP − ω_CCSD(T)/spdf** (Table II's MCP column minus Table I's CCSD(T) column), against our
**Δ_anh(G)** and **Δ_anh(R)** from S1 (`probes/results_m1/s1_anharmonic_benzene_2026-10-13/s1_benzene/{G,R}/qff_report.npz`,
`nu_sym − omega_cm`). Modes are matched by D6h irrep and, within an irrep, by the order of ω (our irreps from the mode's symmetry under
`e8_symmetry.point_group_ops`, the tables' from their row labels). Numbers are read from the rendered PDF pages, not from the text
extraction, which scrambles Table I's columns; every number is entered once into a small data file with its table, row and column.

**Window and exclusions (fixed now):** modes with ω in 550–2,000 cm⁻¹, as in S1. Excluded: every fundamental the paper names as part of a
Fermi resonance (from its text: ν3+ν16 with ν15, ν13+ν16 with ν12, ν16+ν13 with ν5, ν2+ν18 with ν16 — so ν5, ν12, ν15 and ν16 in the
tables' numbering), and any mode without an MCP value. The excluded modes are listed in the outcome.

## Line

**rms over the window's modes of Δ_anh(G) − Δ_semi ≤ 3.0 cm⁻¹** (the same 3.0 that licenses a route for the large PAHs in S2). Reported
beside, without a line: the same for R; max |difference|; B3LYP/TZ2P's own ν − ω from the two tables (a second DFT anharmonic route at a
larger basis); and Δ_semi − Δ_anh per mode.

**Caveat, stated now:** Δ_semi carries the error of ω_CCSD(T)/spdf (a few cm⁻¹; the paper and item 102 flag the out-of-plane b2g modes as
hypersensitive to the basis) and VPT2's own approximations; it is a semi-experimental reference, not truth. A miss is therefore not a
verdict on the hybrid scheme from one molecule: it is read per mode (is it the b2g pair? one family?), and the next point is the next
molecule with published CCSD(T) harmonics and gas-phase fundamentals (none found yet for naphthalene; searched 3 Oct).

**My prediction:** passes, rms ≈ 2–3 cm⁻¹, with the largest differences in the b2g out-of-plane modes. Boese & Martin report B3LYP/TZ2P
fundamentals against MCP at RMS 4.8 cm⁻¹ without the C–H stretches, and that includes B3LYP's harmonic error, which Δ_anh does not carry.

## Outcome (14 Oct 2026, 13:4x)

`probes/hybrid_check_benzene.py` → `probes/results_m1/hybrid_check_benzene_2026-10-14/hybrid_check.{json,md}`; the table numbers in
`boese_martin_tables.json` (pypdf layout extraction, columns checked row by row; Table I's e2u row has two misaligned values in its last two
columns, which are not used). 14 fundamentals in the window; excluded ν5, ν12, ν15, ν16 (Fermi, as registered) and ν1, ν20 (window).
Implementation note: our modes are classed by symmetry from their own vectors (degeneracy by symmetry, because G's coarse grid splits the
pairs beyond dpir's frequency tolerance); b1u and b2u share a class and are paired by ω order.

**G: rms 7.16, max 17.47 cm⁻¹ → misses the line (≤ 3.0).** R: 7.18 / 17.59. Beside: B3LYP/TZ2P's own ν − ω from the same tables 6.89 / 11.00;
exploratory, added after the registered read: B97-1/TZ2P 5.19 / 10.00.

**Read, per mode as registered (no verdict on the hybrid scheme from one molecule):**
1. No DFT anharmonic shift meets 3.0 against this reference — B3LYP/TZ2P 6.89, B97-1/TZ2P 5.19. The reference carries more than 3 cm⁻¹ of
   its own error (the CCSD(T)/spdf harmonics; VPT2's approximations): the line was tighter than the reference allows. It is not moved; the
   next registration on this reference takes the spread of the published DFT routes as its scale.
2. The grid does not matter (G 7.16, R 7.18 — S1's result again). Against B3LYP/TZ2P, our 6-31G* shifts are less negative by ≈ 2–5 cm⁻¹ on
   most modes (mean +2.4 without ν3 and ν19): a basis effect of the size of S1's B setting, in the same direction.
3. Two modes carry most of the miss: **ν19 (e2u, C–H out of plane)**: ours −4.5, semi-experimental −17, B3LYP/TZ2P −20, B97-1/TZ2P −23 —
   ours is the outlier by ≈ 15 cm⁻¹; and ν9 (b2u, Kekulé): ours −34.5, semi −17, TZ2P −28, B97-1 −21. ν3 (a2g) differs from B3LYP/TZ2P by 20
   cm⁻¹, but the paper marks that value as Fermi-affected.
4. **Consequence:** the anharmonic level's open question is the basis, not the grid — and it bites on a C–H out-of-plane mode, the family
   that carries the strongest PAH bands (11–13 µm). Next, to register before it runs: Δ_anh of benzene at G's grid with a triple-ζ basis
   with polarisation (one 61-Hessian set, ≈ 4–8 h on a CPX62, priced on its first Hessian) against 6-31G*, read on ν19 and the out-of-plane
   family; the S2 training set stays at G (its read is relative: route (b) against (c) at one level), but S3's route-A numbers wait for this.
