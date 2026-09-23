# Pre-registration 2026-09-14 — probe M3: can the coupled-cluster deck be run in cc-pVDZ, with the basis step carried by MP2 and a transferred beyond-MP2 increment? (mandate ledger idea I7; written before any number of the probe exists)

*Why this probe exists.* The user's mandate (13 September) is an affordable plan whose end product is the trained network; its binding constraint is the number of coupled-cluster labels a desktop plus a small Snellius share can produce per year — with the measured F, one or two full naphthalene-class corrections (ledger §2). Every label's price is set by the anchor basis: on this laptop one LNO-CCSD(T) tight energy of benzene costs **180 s in cc-pVDZ against 2,087 s in cc-pVTZ** (factor 11.6, `probes/results_timing/benzene_cc-pvdz_tight.json`, `benzene_cc-pvtz_tight.json`), and naphthalene's TZ tight energy is 41,375 s, so a naphthalene DZ tight energy is **≈ 1 h by the benzene ratio (an estimate until measured)**: a full naphthalene deck (474 energies) would be ≈ 20 laptop-days or ≈ 7 desktop-days instead of 226 / 759 laptop-days — twenty to forty naphthalene-class corrections per desktop-year instead of one or two. That is the single largest lever on the goal sentence found so far. It is only a lever if the DZ → TZ change of the correction can be carried by cheap terms.

## 1. What is already measured (benzene, M1 §2.2d, `probes/results_m1/BASIS_SENSITIVITY_dz_tz.md`)

The DZ → TZ change of the harmonic frequency along three probed modes, split by method:

| mode | family | total CCSD(T) | SCF | MP2 correlation | CCSD(T) correlation | **beyond-MP2 = CCSD(T) corr − MP2 corr** | of which (T) |
|---|---|---|---|---|---|---|---|
| 6 | C–H out-of-plane | +66.8 | +44.2 | +14.7 | +22.6 | **+7.9** | −2.6 |
| 12 | C–H in-plane bend | −33.3 | −22.4 | −11.8 | −10.8 | **+1.0** | −0.4 |
| 18 | C–C stretch | −72.7 | −50.6 | −16.1 | −22.1 | **−6.0** | +2.7 |

(cm⁻¹; even-part fits over the same 27 geometries; tight thresholds.) So a DZ-anchored deck plus the SCF and MP2 basis terms that decision 33 already computes (minutes per point at any size) misses the TZ anchor by the **beyond-MP2 increment: +7.9 / +1.0 / −6.0 cm⁻¹** on these three modes — above the 2.5 cm⁻¹ margin on two of three families if left uncorrected, systematic in sign per family, and almost entirely a CCSD effect (the (T) share is small). The literature says the same thing at the complete-basis level: Chan & Ho 2023 (item 86) reach ≈ 2 cm⁻¹ of CCSD(T)/CBS harmonic frequencies at double-ζ cost, but with CCSD(T)-F12 and G3(MP2)-type terms that the pipeline's open stack does not have (no F12 in PySCF/psi4; and an external F12 code would forfeit the frozen, transported LNO spaces that make the 5-point curvatures smooth — the pipeline's central measured result).

## 2. The question M3 answers (fixed)

**Does the beyond-MP2 basis increment of the curvature transfer per band family from benzene to naphthalene within the margin?** If it does, the deck runs in cc-pVDZ, the SCF and MP2 basis terms are computed at TZ/QZ/5Z per point as in decision 33, and the beyond-MP2 increment is carried per family (or per local type, X17/X18 form) from the molecule where it was measured. If it does not, the anchor stays in cc-pVTZ and the label budget stays as in ledger §2.

## 3. Cells (fixed)

Naphthalene, at the B3LYP/6-31G* geometry and normal modes of the timing run, **one mode per judged family**: the C–H out-of-plane mode nearest 780 cm⁻¹ (ν₄₆'s family; lead G's band), the C–H in-plane bend nearest 1,020 cm⁻¹ family, and the C–C stretch nearest 1,380 cm⁻¹ — the same three families as benzene's probed modes. Per mode, **5 points** (q = 0, ±h, ±2h; h as in M1) in **both bases**, tight thresholds, frozen transported LNO spaces as in every deck; the even-part fit a0 + a2 q² + a4 q⁴ per basis; Δω = ½·Δ(2a2). At every point the SCF and MP2 energies in both bases fall out of the same runs (the anchor terms), so the split SCF / MP2 / beyond-MP2 is obtained exactly as at benzene.

## 4. Reading (fixed before any number)

For each family f, with Δ_b(f) the benzene beyond-MP2 increment above and Δ_n(f) the naphthalene one measured here:

- **Win:** |Δ_n(f) − Δ_b(f)| ≤ 2.5 cm⁻¹ on all three families → the DZ-anchored deck with a per-family increment is licensed for the naphthalene class; the ledger §2 table is recomputed with the DZ price; the P26 revision of §12 and the Snellius request are rewritten with it (dated).
- **Partial:** within 2.5 on two families, within 5 on the third → licensed for the two, the third stays TZ-anchored (a mixed deck; the modes of that family are ≈ a third of the deck).
- **Lose:** > 5 cm⁻¹ on any family, or the sign flips → the anchor stays cc-pVTZ; M3 is closed and the measured increments are printed in the error budget as the basis term of decision 26.
- Whatever the outcome, the naphthalene DZ energy time is measured and replaces the estimate above.

## 5. Cost and order

DZ arm: 3 modes × 5 points, minus the shared reference, = 13 energies × ≈ 1 h ≈ **13 laptop-hours** (estimate). TZ arm: 13 × 11.5 h ≈ **6.2 laptop-days** at tight (the timing run's setting; xtight would be ×3.3 and is not needed for a difference of two arms). Memory: TZ tight in-core peaked at 19.8 GB (fits the 25 GB WSL ceiling); DZ well under. Order: after M2a (g), before or instead of the σ-run of decision 35 — the user decides which of the two runs first; M3 moves the label budget by a factor of ten to forty if it wins, the σ-run moves an error-budget term. Script: the existing timing/deck machinery with `--basis cc-pvdz`; the even-part fit code of M1. Nothing sealed is touched: naphthalene has no R1 deck yet; the three modes used here are declared so that a later R1 deck reuses these points or excludes them, at the user's choice.

## 6. What would make it stronger, later

Two more families (ring / C–H in-plane, the low skeletal modes) at 5 points each (+2 × 6.2 days TZ); the local-type form of the increment (X17's types) instead of a per-family constant; and, once benzene's R0 deck exists at TZ, the same deck at DZ (448 × 3 min = 22 laptop-hours) gives the increment for **every** benzene mode and type at negligible cost — the training table for a learned increment.

## Outcome, first family — 20 September 2026, 18:5x (mode 12, C–H out-of-plane): LOSE on this family

TZ cells for mode 12 complete (five points). Beyond-MP2 increment of the curvature, DZ → TZ, at naphthalene: **−8.1 cm⁻¹** as the composite carries it (k(LNO-CC) − k(LNO-MP2)), or +23.0 cm⁻¹ in the mixed form k(LNO-CC) − k(full MP2); benzene's registered value +7.9 cm⁻¹. |Δ_n − Δ_b| = 16.0 (sign flipped) or 15.1 cm⁻¹: beyond the 5 cm⁻¹ lose line under either definition. Under §3 M3 therefore loses at its first family: the anchor stays cc-pVTZ for the C–H out-of-plane family and the measured increments enter the error budget as the basis term. Mechanism (not registered, read from the components): the double-ζ out-of-plane pathology of MP2 for arenes (SCF + MP2 gives 618 cm⁻¹ at DZ for a 785 cm⁻¹ mode, 748 at TZ), inherited in part by the frozen LNO-CC arm at DZ; it grows with the arene and does not touch in-plane modes. Modes 22 and 31 are still read when they land (≈ 22 and 24 September) because the plan licenses per family; the registered rule ("any family") makes M3 as a whole a loss regardless. Full table: `probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md`.


## Outcome, second family — 23 September 2026, 10:0x (mode 22, C–H in-plane bend): WIN on this family

TZ cells for mode 22 complete (five points, the last sealed 22 September 19:21). Beyond-MP2 increment of the curvature, DZ → TZ, at
naphthalene: **+1.2 cm⁻¹** as the composite carries it (k(LNO-CC) − k(LNO-MP2)); benzene's registered value +1.0 cm⁻¹; |Δ_n − Δ_b| = 0.2 cm⁻¹,
same sign → **win on this family**. The mixed form k(LNO-CC) − k(full MP2) gives +6.5 cm⁻¹ (5.5 off); it measures the DZ → TZ growth of the
LNO-MP2 truncation, which the composite removes, so the composite definition carries the verdict (both are printed). Reading and tables:
`probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md` (`probes/m3_family_reading.py 22 1.0`, which also reproduces the mode-12 table).
Per family: DZ-anchored deck licensed for the C–H in-plane bend family, closed for the C–H out-of-plane family; mode 31 (C–C stretch) decides
the third, ≈ 26 September.
