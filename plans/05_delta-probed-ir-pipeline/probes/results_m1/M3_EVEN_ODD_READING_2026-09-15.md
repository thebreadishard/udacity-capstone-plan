# M3 cc-pVDZ cells — even and odd parts per mode (15 September 2026; run complete 13:43, all three modes)

Run: `m1_frozen_spaces.py --molecule naphthalene --basis cc-pvdz --thresh tight --npts 5 --modes 12,22,31 --arms A --basis-terms none --threads 8 --tag _m3`, 14 September 17:51 → 15 September 13:43 (19 h 52 min): reference arm C 4,403 s, arm A 4,159 s, round trip 0.0001 µE_h; fifteen displaced points at **4,075–4,606 s each (median 4,154 s = 69 min)**, RSS ≤ 1.7 GB, scratch ≤ 1.8 GB. Output `results_m1/naphthalene_cc-pvdz_tight_m3/` (REPORT.md, sealed energies, sha256 `58700bfa37c5fac1…`).

Printed by `probes/m3_even_odd_parts.py` (arm A; differences in µE_h, no absolute energy). Definitions: even(q) = ½[E(+q) + E(−q)] − E(0); **odd(q) = ½[E(+q) − E(−q)]** (the force term Δ₁·p). *Note on the 02:52 ledger entry:* its odd-part numbers for mode 12 were the raw differences E(+q) − E(−q), twice the odd part as defined here.

## mode 12 (CH-oop, 785.3 cm⁻¹, B3g in the principal frame; factory-mode impurity 2.4 × 10⁻⁴)

| quantity | even(0.5) | even(1) | odd(0.5) | odd(1) | k (µE_h/q²) | c₄ (µE_h/q⁴) |
|---|---|---|---|---|---|---|
| SCF | +537.47 | +2149.39 | +11.259 | +22.896 | +4300.1 | −2.7 |
| LNO-CCSD(T) corr | −236.27 | −900.59 | −28.746 | −57.196 | −1919.8 | +237.3 |
| MP2 corr | −254.83 | −953.91 | −22.163 | −43.981 | −2082.3 | +348.9 |
| composite | +281.90 | +1183.51 | −17.451 | −34.186 | +2217.9 | +298.1 |

## mode 22 (CH-ip-bend, 1045.1 cm⁻¹, B3u; impurity 1.4 × 10⁻⁶)

| quantity | even(0.5) | even(1) | odd(0.5) | odd(1) | k (µE_h/q²) | c₄ (µE_h/q⁴) |
|---|---|---|---|---|---|---|
| SCF | +642.97 | +2574.37 | +0.378 | +0.600 | +5142.1 | +13.2 |
| LNO-CCSD(T) corr | −37.70 | −150.75 | −1.480 | −2.964 | −301.6 | +0.3 |
| MP2 corr | −32.02 | −128.06 | −0.975 | −1.955 | −256.1 | −0.0 |
| composite | +604.27 | +2419.58 | −1.102 | −2.363 | +4832.5 | +13.4 |

## mode 31 (CC-stretch, 1409.9 cm⁻¹, B3u; impurity 2.1 × 10⁻⁴)

| quantity | even(0.5) | even(1) | odd(0.5) | odd(1) | k (µE_h/q²) | c₄ (µE_h/q⁴) |
|---|---|---|---|---|---|---|
| SCF | +767.46 | +3079.64 | +20.579 | +37.028 | +6133.1 | +52.3 |
| LNO-CCSD(T) corr | +70.68 | +280.98 | −18.769 | −36.001 | +566.6 | −9.2 |
| MP2 corr | +149.78 | +592.53 | −26.702 | −50.133 | +1202.6 | −35.1 |
| composite | +836.24 | +3353.04 | +1.802 | +1.010 | +6684.5 | +43.1 |

## Reading

**The pre-registered mode-31 test (11:4x, `MODE_PURITY_2026-09-15.md`): the prediction as registered failed, the mechanism held.** Registered: "|odd(1)| ≈ 10–40 µE_h in the composite, linear in q; ≲ 1 µE_h refutes the mechanism." Measured: the composite odd part is +1.8 / +1.0 µE_h at q = 0.5 / 1 — neither in the predicted band nor below the refutation line, and not linear. The **components** are exactly what the mechanism predicts: SCF +20.6 / +37.0 and LNO-CCSD(T) −18.8 / −36.0 µE_h, linear in q, the same order as mode 12's (+11.3 / +22.9 and −28.7 / −57.2) and 30–60 × mode 22's, in the ratio of the admixture amplitudes. At mode 31 the SCF and correlation force terms happen to be equal and opposite (the SCF gradient and the correlation gradient along the admixed Ag direction point the other way), so the composite cancels; at mode 12 they have the same structure with the correlation part larger, so the composite does not. The registration should have been on the components, where the mechanism makes its prediction; a composite of two force terms of opposite sign is not something the purity number predicts. Recorded as such.

**Consequence for decision 37, unchanged and sharpened.** A single-sided response carries the odd part of *every* component that enters it; with impure mode vectors that is tens of µE_h in SCF and in correlation separately (1–3 % of the response, ≈ 8–11 cm⁻¹ in the frequency at modes 12 and 31), whether or not the composite happens to cancel. The prerequisite (symmetrised geometry, irrep-projected modes — both implemented today in `dryrun_dft_delta_recovery.py --symmetrised`) must be shown to bring each component's odd part below ≈ 1 µE_h at q = 1; `i14_odd_part_dft.py` measures it at DFT level on factory and projected modes side by side.

**What the DZ cells give M3 now.** The curvature k per mode at cc-pVDZ tight for SCF, MP2 and LNO-CCSD(T), and the beyond-MP2 increment of the curvature, k_CC − k_MP2: mode 12 **+162.5**, mode 22 **−45.5**, mode 31 **−636.0** µE_h/q² (the correlation part of the CC−MP2 difference is large at the C–C stretch, where MP2 overbinds the curvature by a factor two). M3's verdict (pre-registration: the increment's DZ→TZ transfer per family within 2.5 cm⁻¹ against benzene's) needs the same three modes at cc-pVTZ — the TZ cells, ≈ 13 energies × 11.5 h, launched tonight. Nothing about the verdict can be read from DZ alone.

**The price, measured.** 69 min per DZ tight energy at naphthalene in the frozen arm (against 11.5 h at TZ tight: ratio 9.9–10.0), 1.7 GB resident; this is the number P27 and the plan-06 cost ladder §5 use. The q = 0 point was computed three times (4,131 / 4,154 / 4,129 s) — the dedupe patch of this morning removes that from the TZ cells (saves ≈ 23 h).

**Quartic content.** Small at the in-plane modes (c₄/k = 0.3 % at mode 22, 0.6 % at mode 31), 13 % at the CH-oop mode 12 in the composite — carried by the correlation part, which is why the two-amplitude design exists.
