# Probe M3 (B1), first cc-pVTZ family read — mode 12, C–H out-of-plane (20 September 2026, 18:5x)

Source: `m3_even_odd_parts.py results_m1/naphthalene_cc-pvdz_tight_m3 results_m1/naphthalene_cc-pvtz_tight_m3`, run at 18:47 after the
fifth TZ point of mode 12 (q = +1.00) was sealed at 18:43:44 (`naphthalene_ccpvtz_tight_m3.log`). Both arms: frozen arm A, tight
thresholds, the same B3LYP/6-31G* geometry and mode vectors (mode 12, 785.3 cm⁻¹, B3g). Even-part fit even(q) = ½ k q² + ¼ c₄ q⁴ on
|q| = 0.5 and 1.0 (two unknowns, two data: exact). Conversion as in `m1_basis_sensitivity.py`: Δω [cm⁻¹] = ½ Δk × 219474.63 / 10⁶ =
0.10974 cm⁻¹ per µE_h/q².

## The curvatures (µE_h/q²)

| component | k at cc-pVDZ | c₄ at DZ | k at cc-pVTZ | c₄ at TZ | Δk TZ − DZ | Δω TZ − DZ (cm⁻¹) | benzene mode 6, same column (BASIS_SENSITIVITY, 27 points) |
|---|---|---|---|---|---|---|---|
| SCF (DF-RHF) | +4300.1 | −2.7 | +4424.0 | +25.9 | +123.9 | **+13.6** | +44.2 |
| LNO-CCSD(T) correlation (frozen arm) | −1919.8 | +237.3 | −807.8 | −8.8 | +1112.0 | **+122.0** | +22.6 (canonical) |
| full MP2 correlation | −2082.3 | +348.9 | −1180.1 | +157.2 | +902.2 | **+99.0** | +14.7 |
| composite (SCF + LNO-CC − LNO-MP2 + full MP2) | +2217.9 | +298.1 | +3170.2 | +182.0 | +952.3 | **+104.5** | +66.8 (total CCSD(T)) |

## The pre-registered quantity: the beyond-MP2 increment of the curvature, DZ → TZ

The pre-registration (`notes/PreRegistration_2026-09-14_M3_DZ_Anchored_Decks.md` §3) compares, per family, the DZ → TZ change of the
beyond-MP2 part of the curvature at naphthalene (Δ_n) with benzene's (Δ_b = +7.9 cm⁻¹ for the C–H out-of-plane family). Win: |Δ_n − Δ_b| ≤
2.5 cm⁻¹ on all three families. Lose: > 5 cm⁻¹ on any family, or a sign flip.

Two readings of "beyond-MP2" exist in the frozen arm, and both lose:

| definition | DZ | TZ | Δ_n = TZ − DZ | Δ_n − Δ_b |
|---|---|---|---|---|
| what the composite actually carries: k(LNO-CC) − k(LNO-MP2) = composite − SCF − full MP2 | +0.1 | −73.7 | −73.8 µE_h/q² = **−8.1 cm⁻¹** | **16.0 cm⁻¹, sign flipped** |
| the DZ reading's mixed form of 15 Sep: k(LNO-CC) − k(full MP2) | +162.5 | +372.3 | +209.8 µE_h/q² = **+23.0 cm⁻¹** | **15.1 cm⁻¹** |

**Verdict on this family: the beyond-MP2 basis increment of the C–H out-of-plane curvature does not transfer from benzene to
naphthalene.** Under the registered rule ("> 5 cm⁻¹ on any family, or the sign flips") probe M3 loses at its first family; the anchor
stays cc-pVTZ for the C–H out-of-plane family, and the DZ-anchored deck with a per-family constant increment is not licensed. Modes 22
(C–H in-plane bend, ≈ 22 Sep) and 31 (C–C stretch, ≈ 24 Sep) are still worth reading: the plan licenses per family, and the in-plane
families are not expected to share the mechanism below.

## Why this family, and why the effect is larger than at benzene

Converting the curvatures to the frequency a method would give along this mode (ω' = ω_B3LYP √(k / k_B3LYP), k_B3LYP = ω = 3578.1 µE_h/q²):

| method | cc-pVDZ | cc-pVTZ |
|---|---|---|
| SCF | 861 | 873 |
| SCF + full MP2 | **618** | 748 |
| SCF + LNO-CCSD(T) | 641 | 789 |
| composite | 618 | 739 |

At cc-pVDZ, MP2 lowers this out-of-plane C–H frequency by 243 cm⁻¹ against SCF, to 618 cm⁻¹; at cc-pVTZ by 125 cm⁻¹. That is the known
double-ζ out-of-plane pathology of MP2 for arenes (Moran, Simmonett, Leach, Allen, Schleyer & Schaefer, *J. Am. Chem. Soc.* 2006, 128,
9342: MP2 with double-ζ and augmented bases predicts benzene and larger arenes non-planar through spurious softening of the b₂g/out-of-plane
modes — reference cited from memory, to be checked against the paper before it enters any document). The frozen LNO-CCSD(T) arm inherits
part of it at DZ (641 cm⁻¹), and the deviation from quadratic behaviour is also a DZ symptom: c₄/k = 12 % for the DZ correlation part
against 1 % at TZ. The mechanism is basis-driven and grows with the arene, which is exactly why a per-family constant measured at benzene
(+7.9 cm⁻¹) cannot be carried to naphthalene (−8.1 or +23.0 cm⁻¹ depending on the definition). It does not touch the in-plane families.

## What this changes and what it does not

- The cheap-basis route for the C–H out-of-plane family is closed as registered; the TZ price per energy (12.2 h at tight on this laptop)
  stands for that family, and the Snellius request on the 28 September agenda keeps its TZ numbers.
- The measured increments enter the error budget as the basis term of decision 26 for this family (pre-registration's lose branch).
- No number in the reading copy's DZ pricing paragraph (P27) is licensed for this family; the placeholder "[probe B1 verdict on the
  cc-pVTZ cells: to be filled by the student on 25 September]" now has its first family entry; the full M3 verdict waits for modes 22 and 31.
- The frozen-space diagnostics of the run are unchanged by this reading (s_min occ 0.990, vir 0.385 at TZ; stage 0 passed at 0.0002 µE_h).
