# Design and pre-registration, 4 October 2026, 14:5x — the composite anchor level: CC/cc-pVDZ plus a cheap TZ−DZ step (TASKS 24; the user: "Prima om duurdere ankers te maken … Verfijn de meetlat en labels")

*Registered before anything runs. Lever 2's read of 13:3x said the cc-pVDZ anchors overstate the CC correction out of plane (63–110 % of it is the
basis) and reverse it for the C–H stretch (143 %). Full cc-pVTZ anchors cost 1.5–2 h per gradient for benzene and N⁷ beyond, so the anchor level
has to be composed: the full CCSD(T) Hessian at cc-pVDZ plus the basis step measured at a cheaper level X,*

    H_composite = H_CC/DZ + [ H_X/TZ − H_X/DZ ],   X ∈ { B3LYP, MP2 } (frozen core as the anchors),

*the usual additivity assumption of composite thermochemistry applied element by element to a Hessian. Two tests, in order; the first costs an hour
and runs today, the second needs the full benzene TZ anchor that completes tonight.*

## Test 1 — the three measured coordinates of benzene (today, 4 threads beside step 3)

`probes/cc_composite_basis_check.py` (pyscf under WSL qc05): for the coordinates k = 2 (C z), 18 (H x), 20 (H z) of the lever-2 read, the basis step
Δ_X = H_kk(X/cc-pVTZ) − H_kk(X/cc-pVDZ) by finite differences of analytic gradients (step 0.005 bohr, the anchors' step; frozen core 6 for MP2,
the anchors' value), beside the measured Δ_CC = H_kk(CC/TZ) − H_kk(CC/DZ) = +0.01678, −0.02425, +0.00421 a.u. Second route for the B3LYP numbers: the
analytic B3LYP Hessian's diagonal at cc-pVDZ against its FD value (agreement ≤ 1e-4 a.u., or the FD is not trusted). Smoke on water first.

**Predictions.** B3LYP's step tracks the two out-of-plane coordinates within 20 % (the basis stiffness of out-of-plane bends is a one-electron effect
visible at DFT) and under-reproduces the C–H one (the C–H basis step is largely a correlation-basis effect: predicted 30–60 % of Δ_CC). MP2's step
tracks all three within 20 %.

**Reading rule (test 1).** A level *tracks* a coordinate when |Δ_X − Δ_CC| ≤ 0.2 |Δ_CC|. The level that tracks all three is X for test 2; if only MP2
tracks the C–H and both track the out-of-plane, test 2 runs with MP2 and B3LYP is kept as the cheaper fallback for out-of-plane only; if neither
tracks the C–H coordinate, the composite is tried in test 2 anyway but the C–H family is flagged as the place where only TZ anchors will do.

## Test 2 — the full benzene anchor (after the TZ anchor of the night of 4–5 October)

With `hessian_ccsd_t.npz` at cc-pVTZ assembled: the full H_X/TZ − H_X/DZ for the chosen X (B3LYP: two analytic Hessians, minutes; MP2: 13 gradient
pairs per basis, ≈ 1–2 h), the composite Hessian, and the read-out the project uses everywhere — corrected frequencies per family (ring-ip,
CH-stretch, CH-oop, other) of the composite against CC/TZ, with CC/DZ against CC/TZ as the baseline that shows what the composite repairs.

**Predictions.** CC/DZ against CC/TZ: CH-oop and CH-stretch 20–60 cm⁻¹ rms, ring-ip 5–15. The composite with MP2: every family ≤ 3 cm⁻¹; with B3LYP:
CH-oop ≤ 3, CH-stretch 5–15.

**Lines (test 2).** *Composite within 3 cm⁻¹ of CC/TZ in every family* → the composite is the anchor level: each existing DZ anchor (benzene,
fluorobenzene, pyridine, benzonitrile, naphthalene; anthracene when it lands) gets its basis step at X (hours per molecule, no CC), the T3 read-out
gets its TZ-corrected lines for out-of-plane and C–H on the composite anchors, and the label plan's anchors are priced as DZ + step. *3–10 cm⁻¹ in
some family* → the composite per family with the better X per family, and that family's line stays provisional. *> 10 cm⁻¹ in any family* →
the composite is rejected for that family; TZ anchors where affordable (benzene, pyridine), LNO beyond, and the family's targets wait.

## Cost and place

Test 1: ≈ 20 B3LYP and 12 MP2 gradient evaluations on benzene at cc-pVDZ/cc-pVTZ plus one analytic B3LYP/cc-pVDZ Hessian — of the order of an hour at
4 threads, run today beside chain 34 step 3 (12 threads). Test 2: after the TZ anchor assembles (≈ 5 Oct midday), minutes for B3LYP, 1–2 h for MP2,
on free lanes. Nothing changes in the Ladder, the anchors or the T3 lines before test 2 is read; test 1 only picks X.

## Outcome of test 1, 4 October 16:4x — MP2 tracks all three coordinates, B3LYP none; X = MP2

`modules/05_support_predictor/out/composite_test1_benzene_2026-10-04.{md,json}` (`probes/results_m1/composite_test1_benzene_2026-10-04_b.log`; 5,161 s at
4 threads beside step 3). The first launch (14:46) died in the MP2/cc-pVTZ gradient: pyscf's `grad/mp2.py` sizes its AO blocks from
`max_memory − current memory`, and after the B3LYP work in the same process 6,000 MB left a block of one function, smaller than a d shell — an empty
block and a reshape error; relaunched 15:21 with MP2 first and 12,000 MB (the B3LYP numbers of the first run are identical to the digit).

| k | coordinate | Δ_CC | Δ_MP2 | Δ_B3LYP | MP2 / CC | B3LYP / CC | B3LYP analytic vs FD |
|---|---|---|---|---|---|---|---|
| 2 | C z (oop) | +0.01678 | +0.01585 | +0.00467 | 0.94 tracks | 0.28 | 4.7e-6 |
| 18 | H x (C–H) | −0.02425 | −0.02356 | −0.01782 | 0.97 tracks | 0.73 | 1.0e-5 |
| 20 | H z (oop) | +0.00421 | +0.00376 | +0.00271 | 0.89 tracks | 0.64 | 6.2e-7 |

**Predictions.** MP2 within 20 % on all three: yes (6–11 % short). B3LYP within 20 % on the out-of-plane pair: **no** — it gives 28 % and 64 % of the
step; the basis stiffness of the out-of-plane bends is a correlation-basis effect too, not a one-electron one. B3LYP under-reproducing the C–H step:
yes (73 %). Second route: the analytic B3LYP/cc-pVDZ Hessian agrees with the FD values to ≤ 1.0e-5 a.u. at the production grid (the water smoke's
4e-4 was the small grid 75,302). **Reading rule → X = MP2 for test 2.** Cost at TZ: 640–850 s per MP2 gradient of benzene at 4 threads, so the
full benzene step is ≈ 2 h and a naphthalene step a night; B3LYP is dropped as a fallback (it tracks nothing).

*Test 2 preparation (16:5x):* `probes/cc_composite_full_check.py compute` writes the MP2 Hessian rows of the symmetry-unique displacements at a basis
(cc-pVDZ and cc-pVTZ for benzene run tonight beside step 3); `… read` assembles the composite when the TZ anchor exists and reads it per family against
CC/TZ with CC/DZ as the baseline, as registered above.

*16:5x:* the `read` step smoked on benzene with the DZ anchor and the DZ rows standing in for TZ — the composite reproduces CC/DZ to 0.00 cm⁻¹ in every family (the identity the assembly must satisfy); the zero-rule column (B3LYP alone against CC/DZ: ring-ip 25.0, CH-stretch 99.3, CH-oop 72.0, other 55.9) matches the T3 read-out's convention. The MP2 rows at cc-pVTZ run until ≈ 19:30; the read waits for the TZ anchor (5 Oct).
