# Plan 06 — result note X3b (2026-09-12): how fast pair correlation decays in naphthalene

*Printed by `experiments/x3_pair_decay.py` (WSL, pyscf; RHF/cc-pVTZ with density fitting, Pipek–Mezey
localisation of the 24 active occupied orbitals, full DF-MP2 amplitudes rotated to the LMO basis,
pair energies from the antisymmetrised contraction; 15 s in all). Check: the pair energies sum to the
MP2 correlation energy to 10⁻¹³ E_h. Geometry: plan 05's B3LYP/6-31G* naphthalene. Full table in
`experiments/x3_naphthalene_cc-pvtz.md`.*

## Numbers

| quantity | measured |
|---|---|
| pairs | 276 (24 LMOs); LMO-centroid distances up to ≈ 7 Å |
| exponential fit on pairs beyond 2 Å (201 pairs) | decay length **λ = 0.75 Å** (|e_ij| ∝ e^{−r/λ}) |
| mean |e_ij| by distance bin | 0–1.5 Å: 14.8 mE_h; 1.5–2.5: 2.76; 2.5–3.5: 0.66; 3.5–4.5: 0.17; 4.5–6: 0.062; 6–9: 0.0075 |
| share of the correlation energy in pairs beyond a distance | > 2 Å: 8.2 %; > 3 Å: 2.3 %; > 4 Å: 0.3 %; > 5 Å: 0.1 % |

## Reading for S1

1. **Per pair, the decay is fast**: a factor e every 0.75 Å, so a pair two rings apart (≈ 5 Å) is a
   thousand times weaker than a bonded pair. That is the nearsightedness Prodan & Kohn describe,
   measured at MP2 level on the quantity LNO thresholds are built on.
2. **In energy, it is not fast enough at this size.** Because the number of pairs grows with distance,
   the tail carries 2.3 % of the correlation energy beyond 3 Å — 36 mE_h — and 0.3 % beyond 4 Å —
   5 mE_h. Plan 05's anchor needs energies to well below 1 µE_h. Nothing in naphthalene can be
   dropped, which is exactly what X3a showed from the other side (tight LNO keeps 92–100 % of the
   occupied space). Locality starts to pay only when a molecule has pairs beyond ≈ 6–7 Å, i.e. at
   pyrene-to-coronene size and beyond, and then only in the far corners.
3. **What this does not yet say.** Δ₂ is a *difference of curvatures*, not an energy; the relevant
   decay is that of the second derivative of the pair energy along a displacement, which may be
   shorter- or longer-ranged than the energy's. That is the next X3 (same script, at the ± displaced
   geometries of one mode, cheap), and it is the number that would bound how far a fragment's
   correction reaches — the plan's fragment licence in measured form.

## Ledger

S1 stays alive with a first measured constant: λ = 0.75 Å at MP2 level for naphthalene; next test is
the decay of the *curvature* contribution (X3c) and the same numbers at pyrene once its geometry
exists. No consequence for plan 05's frozen text; the number is cited in the M1 note's locality
discussion only when X3c has been run.
