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
