# Reading note, 25 October 2026 — Vats, Mattioda & Ricca 2026: the 5–6 µm overtone region of PAHs and PANHs (item 114)

*Read in full (ACS Earth Space Chem. 10, 1685–1701, 26 Jun 2026, DOI 10.1021/acsearthspacechem.6c00033, CC BY-NC-ND 4.0; local copy
`Papers/Vats_2026_ACSESC10_1685_PAHs_PANHs_5-6um_overtones.pdf`, downloaded by the user; text `Papers/_txt/vats2026.txt`). The search
snippets of the morning had put Esposito et al. as authors — wrong; corrected in the literature record.*

## What they did

- **27 neutral molecules:** 9 PAHs (naphthalene, anthracene, phenanthrene, pyrene, chrysene, benz[a]anthracene, three dibenzanthracenes)
  and 18 PANHs (among them **quinoline and isoquinoline — two of our CC anchors** — acridine, phenazine, 2-azapyrene, phenanthridine,
  the aza-benz[a]anthracenes, aza-chrysenes, dibenzacridines). C10–C22; D2h, C2h, C2v, Cs.
- **Theory:** GVPT2 on B3LYP-D3(BJ)/N07D quartic force fields (Gaussian 16; 1:2 Fermi and 1:2, 2:2 Darling–Dennison resonances; superfine
  grid; 2 cm⁻¹ Lorentzians). On naphthalene vs NIST gas phase: 0.35 % in positions, 15.7 % in relative intensities (Mackie 2015: 0.36 %,
  17.4 %).
- **Experiment:** archived NASA Ames argon-matrix spectra (10–20 K; matrix shifts ~0.2 % ± 0.9 %, intensities ~33 % on naphthalene); all
  bands in 2000–1650 cm⁻¹ tabulated (Tables S2–S14 in the free Supporting Information).
- **Agreement:** positions within 0.15 % (PAHs) and 0.17 % (PANHs), i.e. ~3 cm⁻¹ at 1900 cm⁻¹; absolute intensities ~45 % off.

## What it says that matters to us

1. **The 5–6 µm bands are combination bands and overtones of C–H out-of-plane fundamentals** (977–706 cm⁻¹; in PANHs 97 % CHoop), and
   the upper subregion (2000–1870 cm⁻¹) is built from CHoop fundamentals at **990–940 cm⁻¹ that are IR-inactive or very weak** as
   fundamentals. So these bands are an experimental window on CHoop modes that the fundamental spectrum hides.
2. **That is our hardest family.** Our CC correction to CH-oop is a family mean shift of up to ~20 cm⁻¹ (ωB97X up, CC down; TASKS 82,
   the proxy check of 21–22 Oct). A combination ν_i + ν_j carries the sum of two such corrections, so an error of a few cm⁻¹ per CH-oop
   mode becomes a doubled shift at 5–6 µm — a sensitive, measured test of whether the network has learned CH-oop at CC level.
3. **N substitution moves these bands by ~10 cm⁻¹ on average**, more at bay sites and with two N (phenazine) — the size of effect our
   aza cells must get right.
4. **Their intensities stay ~45 % off** even with GVPT2: band positions are the robust observable here, intensities are not.

## A test it makes possible (TASKS 110)

For naphthalene, quinoline and isoquinoline (CC anchors with VPT2-ready data) and later for any molecule the network covers: compute the
5–6 µm combination positions from (a) the scaled-free DFT Hessian, (b) the CC-anchor Hessian, (c) the network's corrected Hessian, each
with the same anharmonic step, and compare to their matrix positions (Tables S2, S6; argon shifts ≤ ~0.2 %) and, for naphthalene, the
gas-phase data. A pass is CC-corrected positions closer than DFT to experiment on the CH-oop combinations; the registered lines would be
written before the comparison is run (CLAUDE.md, registration rules). Needs: their Supporting Information (free download from the ACS
page), our S1/S2 anharmonic step on the same molecules.
