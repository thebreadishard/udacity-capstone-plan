# M3 cc-pVDZ cells — even and odd parts per mode, read while the run is live (15 September 2026, 08:5x; modes 12 and 22 complete, mode 31 running)

Printed by `probes/m3_even_odd_parts.py results_m1/naphthalene_cc-pvdz_tight_m3` (arm A, tight thresholds, frozen spaces reloaded per point; differences in µE_h, no absolute energy). Definitions: even(q) = ½[E(+q) + E(−q)] − E(0); **odd(q) = ½[E(+q) − E(−q)]** — the force term Δ₁·p. *Note on the 02:52 ledger entry:* its odd-part numbers for mode 12 (SCF +22.5/+45.8, composite −34.9/−68.4) were the raw differences E(+q) − E(−q), i.e. twice the odd part as defined here; the finding is unchanged.

## mode 12 (CH-oop, 785.3 cm⁻¹)

| quantity | even(0.5) | even(1) | odd(0.5) | odd(1) | k (µE_h/q²) | c₄ (µE_h/q⁴) |
|---|---|---|---|---|---|---|
| SCF | +537.47 | +2149.39 | +11.259 | +22.896 | +4300.1 | −2.7 |
| LNO-CCSD(T) corr | −236.27 | −900.59 | −28.746 | −57.196 | −1919.8 | +237.3 |
| MP2 corr | −254.83 | −953.91 | −22.163 | −43.981 | −2082.3 | +348.9 |
| composite | +281.90 | +1183.51 | −17.451 | −34.186 | +2217.9 | +298.1 |

## mode 22 (CH-ip-bend, 1045.1 cm⁻¹)

| quantity | even(0.5) | even(1) | odd(0.5) | odd(1) | k (µE_h/q²) | c₄ (µE_h/q⁴) |
|---|---|---|---|---|---|---|
| SCF | +642.97 | +2574.37 | +0.378 | +0.600 | +5142.1 | +13.2 |
| LNO-CCSD(T) corr | −37.70 | −150.75 | −1.480 | −2.964 | −301.6 | +0.3 |
| MP2 corr | −32.02 | −128.06 | −0.975 | −1.955 | −256.1 | −0.0 |
| composite | +604.27 | +2419.58 | −1.102 | −2.363 | +4832.5 | +13.4 |

## Reading (no verdict; M3's verdict waits for mode 31 and the TZ cells)

- **The odd parts are linear in q for both modes** (odd(1) ≈ 2 × odd(0.5) within 2–15 %), i.e. a force term, not noise: the factory geometry is not exactly the D₂h stationary point along these mode vectors (the 02:52 finding: 4–7 × 10⁻⁵ bohr from D₂h plus a 3 × 10⁻⁴ Ag admixture in mode 12's vector). Mode 22's force term is 15–30 × smaller than mode 12's — the admixture is mode-specific.
- **What a single-sided response would have carried, had it been used here:** the odd part itself, as an error on the response — mode 12: 34 µE_h on a 1,184 µE_h composite response at q = 1 (2.9 % in k, ≈ 1.4 % in the frequency, ≈ 11 cm⁻¹); mode 22: 2.4 µE_h on 2,420 (0.1 % in k, ≈ 0.5 cm⁻¹). Both exceed the 2 µE_h per-energy noise requirement the couplings tolerate at benzene; the symmetrised-geometry prerequisite of decision 37 is therefore load-bearing, not cosmetic, and the dry run must show the odd part below ≈ 1 µE_h at q = 1 before I14 counts.
- **The even parts are unaffected** (± pairs cancel the force term exactly): the M3 curvature comparison rests on them. The quartic content is small for mode 22 (c₄/k = 0.3 %) and larger for mode 12 (13 % of k in the composite, dominated by the correlation part — a CH-oop mode's known anharmonicity), which the two-amplitude design was made for.
- The correlation contributions to k: mode 12 −1,920 (LNO-CCSD(T)) against −2,082 (MP2) µE_h/q² — MP2 overshoots by 8 %; mode 22 −302 against −256 — MP2 undershoots by 15 %. The beyond-MP2 increment M3 transfers is the difference of these two columns per mode; its cc-pVTZ counterpart is what the TZ cells (≈ 21 September) measure.
