# The three-band test at benzene (20 September 2026, 21:4x) — does the coupled-cluster curvature correction move B3LYP's bands toward experiment?

*Desk reading of existing sealed data; no new compute. Inputs: `results_dryrun/benzene/stageA.json` and `stageA_hessians.npz` (B3LYP/6-31G* harmonic
frequencies and mode vectors L), `results_m1/benzene_cc-pvtz_tight/` and `benzene_cc-pvdz_tight/` (`canonical_truth_sealed.json`: canonical CCSD(T) at the
27 displaced geometries, frozen core, DF-RHF reference; `m1_sealed_energies.json`: the frozen composite arm A at the same points), `benzene_cc-pvtz_xtight/`
(arm A only). Even-part fit E = a₀ + a₂q² + a₄q⁴ over the nine points per mode; curvature k = 2a₂; B3LYP's curvature in the same dimensionless coordinate is
ω itself (the displacement is L·q/√ω). Diagonal-only correction: ω′ = ω_B3LYP √(k_CC / k_B3LYP) along the B3LYP mode vector; couplings within the family are
not included (they need the deck). Experimental fundamentals: NIST WebBook / CCCBDB, Shimanouchi 1972 tables, fetched 20 September; the three modes are
IR-inactive, their values come from Raman (liquid) and combination-band work — gas values differ by 1–2 cm⁻¹ (Goodman, Ozkabak & Thakur 1991, not held).*

## 1. Which three modes

| M1 mode | B3LYP/6-31G* ω | family label | identification from L | Herzberg/Shimanouchi mode | experiment ν (cm⁻¹) |
|---|---|---|---|---|---|
| 6 | 864.7 | CH-oop | degenerate pair (with mode 7), 100 % out of plane, 79 % H motion | ν11 (e1g), CH out-of-plane | 849 |
| 12 | 1020.4 | "CH-ip-bend" | in plane, 9 % H motion, all six C–C bond-length derivatives equal (−0.99 … −1.00): ring breathing | ν2 (a1g) | 992 |
| 18 | 1356.5 | CC-stretch | in plane, 7 % H motion, C–C derivatives alternating ±1: Kekulé | ν9 (b2u) | 1310 |

(The M1 family label of mode 12 was wrong: it is the a1g ring breathing, not a C–H bend. Modes 11 and 12 of the B3LYP set are accidentally 0.4 cm⁻¹ apart,
a1g and b1u; the L vector of mode 12 is the breathing one. Noted for the family assignment code.)

## 2. The corrected harmonic frequencies (cm⁻¹)

| mode | B3LYP | canonical CCSD(T)/cc-pVTZ | frozen composite, TZ xtight | frozen composite, TZ tight | canonical CCSD/cc-pVTZ | SCF/cc-pVTZ | canonical CCSD(T)/cc-pVDZ | experiment ν |
|---|---|---|---|---|---|---|---|---|
| ν11 e1g oop | 864.7 | **874.2** | 874.3 | 874.7 | 901.9 | 1004.3 | 805.4 | 849 |
| ν2 a1g breathing | 1020.4 | **1007.0** | 1007.0 | 1007.1 | 1013.8 | 1038.8 | 1040.2 | 992 |
| ν9 b2u Kekulé | 1356.5 | **1335.3** | 1335.6 | 1336.1 | 1285.4 | 1205.5 | 1407.2 | 1310 |

The frozen composite reproduces the canonical curvature to 0.1–0.3 cm⁻¹ at xtight and 0.1–0.8 at tight (the XTIGHT_READIN numbers, now seen as
frequencies). The cc-pVDZ column shows why tonight's naphthalene result was no surprise: at DZ the out-of-plane mode falls to 805 and the Kekulé mode
rises to 1407 — the double-ζ basis is unusable for either, in opposite directions.

## 3. The reading: harmonic minus experiment, before and after

| mode | ω_B3LYP − ν_exp | ω_CC − ν_exp | scaled B3LYP (0.9614) − ν_exp |
|---|---|---|---|
| ν11 oop | +15.7 | **+25.2** | −17.6 |
| ν2 breathing | +28.4 | **+15.0** | −11.0 |
| ν9 Kekulé | +46.5 | **+25.3** | −5.9 |

What a harmonic frequency should be, relative to the fundamental, is the fundamental plus the anharmonic shift, which for benzene's in-plane and
out-of-plane skeletal modes is positive and of the order of 10–30 cm⁻¹ (1–2 %). Read that way:

- **B3LYP's gaps span 16 to 47 cm⁻¹** — three times as wide as any plausible anharmonic shift on the Kekulé mode, and the well-known reason B3LYP needs a
  scale factor that then over-corrects the out-of-plane mode (−18) while under-correcting the Kekulé one (−6).
- **The coupled-cluster-corrected gaps are 15, 25 and 25 cm⁻¹** — all inside the range of an anharmonic shift, and nearly uniform. The correction moves
  the Kekulé mode by −21 cm⁻¹ and the breathing mode by −13, the two directions a scale factor cannot both take, and it moves the out-of-plane mode *up*
  by +10, which no scaling does either.
- The test is not yet a verdict, because the anharmonic shift per mode is not measured here: our benzene VPT2 run (B3LYP/6-31G*, pyVPT2) was killed by the
  16 September reboot at 2,162 of ≈ 4,100 gradients and never rerun; CCCBDB's anharmonic page returned a server error tonight. With those three shifts the
  table above becomes three predicted fundamentals against three measured ones. Until then the honest sentence is: *after the coupled-cluster correction of the
  diagonal, the remaining harmonic-to-fundamental gaps of the three benzene modes are 15–25 cm⁻¹ and nearly equal; before it they were 16–47 cm⁻¹.*

## 4. What would close it, and what it costs

- The benzene VPT2 at B3LYP/6-31G* with pyVPT2: ≈ 4,100 finite-difference gradients, 9 h on the laptop's eight threads; on one Helsinki CPX62 (16 vCPU)
  an evening and a euro or two, after `pip install pyvpt2` in a fresh environment there (the Windows install needed two packaging fixes, Software Changes
  Ledger rows 10–11). It gives the shift for all 30 modes, so the same table can be made for every band with a canonical or frozen curvature — today three;
  with the diagonal deck of §4 of the two-hour check (≈ 50 tight TZ energies) all thirty.
- Nothing here touches the anchor or the laptop; it is the user's call whether it runs before the 28th.

## 5. What it does not show

Couplings within a family (the off-diagonal blocks) are absent — that is what the 448-energy deck measures; the three modes are single, non-resonant
fundamentals, chosen in September for the smoothness probe, not for spectroscopy; and three modes are three modes. It is the first evidence that the
correction moves bands in the right direction by the right amount, not a licence.

## 6. Added 21 September, 06:0x — the benzene VPT2 ran, and its numbers are not usable for a D6h molecule

`results_vpt2/benzene_b3lyp_631gs_vpt2.md` (hel1-14, psi4 1.10.2, pyVPT2 0.1.2, 61 analytic Hessians in 4 h 28 min, checkpoint cache complete) and the
rerun `…_K0.md` from the cache with `FERMI_K_THRESH 0` (every near-degeneracy within 200 cm⁻¹ into a polyad, the SPECTRO-2016 recipe; 1,050 detections,
94 with K > 0.01 cm⁻¹). Both give the same picture: the exactly degenerate pairs come out split and asymmetric (e1g 864.4 → +11.3 and −9.1; e2g 1531.5 →
−15 and −71; e1u 1656 → −47 and −183; C–H stretches −75 to −280), and the accidental a1g/b1u pair at 1020.1/1020.8 explodes (+23.7 and −217). The polyad
treatment does not repair it, so the cause is not missed Fermi resonances but the first-order degeneracies themselves: pyVPT2 is written for asymmetric
tops and carries Coriolis and resonance denominators that vanish for a symmetric top. This is the failure Mackie et al. 2016 report for triphenylene
(D3h) and Esposito et al. 2024 avoid by computing benzene in D2h with the caveat that degenerate modes split artificially.

What survives: the **Kekulé mode** (b2u, non-degenerate, no near neighbour) has ν − ω = −10.2 (K = 1) or −20.3 (K = 0; a 2ν10 ≈ ν14 polyad enters).
Predicted fundamental from the coupled-cluster-corrected harmonic 1335.3: **1315–1325 cm⁻¹ against 1310 measured**; from B3LYP alone 1336–1346. For the
e1g out-of-plane and the a1g breathing mode no shift can be read from this run.

What this changes: (1) the three-band test keeps its harmonic-gap statement of §3, with one band now within 5–15 cm⁻¹ of experiment after correction and
anharmonic shift (26–36 before); (2) **the pipeline's VPT2 step needs a degenerate-mode-capable treatment before benzene, coronene or any symmetric top can
be scored** — pyVPT2 as shipped does not have it; SPECTRO handles symmetric tops with care (Mackie 2016, Appendix), Gaussian treats degenerate modes; this
goes to the Software Changes Ledger and to the text of blad 8, not to the caption; naphthalene (D2h, no degeneracies) is the safe first spectrum, which is
another reason the anchor is where it is; (3) the cleanest closing test that needs no VPT2 at all: compare the corrected harmonic frequencies with the
**experimental harmonic frequencies** of benzene from the anharmonic analyses of Goodman, Ozkabak & Thakur 1991 (JPC 95, 9044) and Miani, Cané,
Palmieri, Trombetti & Handy 2000 (JCP 112, 248) — two PDFs to ask of the supervisor; with them the test is harmonic against harmonic for all three
modes, and the basis-set term (TZ → CBS) is the only remaining caveat. The 61 cached Hessians on hel1-14 are a complete B3LYP/6-31G* quartic force field
of benzene and can be fed to another VPT2 code without recomputation.

## 7. Correction, 21 September 06:3x — the cause is finite-difference noise, not the degeneracies

§6 blamed the symmetric-top degeneracies. The own assembly `probes/qff_from_hessians.py` (same 61 Hessians, independent harmonic analysis, both
finite-difference routes kept for every φ_iijj; it reproduces pyVPT2's fundamentals to 0.1 cm⁻¹) shows the quartic constants themselves are noise: the
two routes to the same φ_iijj disagree by a median of 22 cm⁻¹ and up to 1,265 cm⁻¹ (`results_vpt2/qff_benzene_2026-09-21.md`). psi4 has no analytic
B3LYP Hessian, so each displaced Hessian is a 3-point finite difference of gradients, and pyVPT2's default step of 0.05 in reduced coordinates
(≈ 0.004 Å) divides that noise by 0.0025. The degenerate-pair asymmetry is a symptom. Whether a symmetric-top treatment is also needed can only be
judged on clean constants; two reruns with step 0.20 (psi4 3- and 5-point Hessians) are running on hel1-14, and the route-disagreement statistic is the
meter. The Kekulé shift of §6 (−10 to −20) is therefore also provisional. The harmonic-gap statement of §3 and the request for the experimental
harmonic frequencies (Goodman 1991, Miani 2000) are unaffected.

