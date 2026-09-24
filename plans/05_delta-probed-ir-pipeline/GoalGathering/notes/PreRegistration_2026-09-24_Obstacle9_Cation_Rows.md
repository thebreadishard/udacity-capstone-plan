# Pre-registration 2026-09-24, 23:1x — obstacle 9: benzene⁺ and naphthalene⁺ get their rows (the user: "Zet benzeen⁺ en naftaleen⁺ maar op hel1-14 zodra route 2 klaar is")

**Why.** Obstacle 9 (ledger, 14 September): cations are astronomically as important as neutrals and appear in no row of the affordability
collection; the user's standing instruction is to close that gap, not to price it away. Two rows are missing per molecule: the proxy-corpus row
(DFT–DFT ΔH at deck-v1 numerics, open-shell) and the coupled-cluster price (an unrestricted local CC energy at the anchor's thresholds).

**What runs (fixed), on hel1-14 after route 2, in this order** (`probes/run_cations_after_route2.sh`, wrapper log `/root/cations/chain.log`):
1. Smokes on the water cation for both paths as soon as the environments exist (tonight): the UKS worker path and the ULNO path.
2. **Cation rows** — `corpus/cation_rows.py` with `decks/deck_v1_cation.json` (deck v1 numerics; `reference uks`, charge 1, multiplicity 2;
   psi4 1.11 in env `qc`): UKS-B3LYP/6-31G* optimisation in c1 from the neutral corpus geometry with a seeded 0.01 Å distortion (so benzene⁺ can
   reach its Jahn–Teller minimum), then the B3LYP and ωB97X UKS Hessians at that geometry (psi4 findif of analytic gradients, as deck v1).
   Output in the corpus schema under `/root/cations/rows/<name>/`, to be fetched to `corpus/molecules_cations/<id>_cation/`.
3. **CC price** — `probes/l3_ulno_price.py`: DF-UHF/cc-pVDZ, Pipek–Mezey per spin (the pyscf-forge test recipe), `ULNOCCSD_T` with one fragment per
   localised orbital of either spin, tight thresholds [1e-6, 1e-7], frozen 1s cores, UMP2 for the composite; three points (reference, q = ±1 along
   the UKS-B3LYP mode nearest 990 cm⁻¹), 16 threads, 24 GB.

**Read-outs (fixed).**
- Rows: status done; the number of imaginary modes per functional (expected 0 after the distorted start); the lowest frequencies; ⟨S²⟩ is
  not stored by the worker (noted); timings per stage against the neutral's corpus timings on the same class of machine.
- Price: wall seconds per ULNO-CCSD(T)/cc-pVDZ energy (mean of three) and peak RSS, against the neutral's LNO price on the same machine class
  (naphthalene DZ energies of the M3 DZ run on the laptop; L2's phenanthrene+CN on the CCX53 — different machines, so the ratio is indicative);
  ⟨S²⟩ of the UHF reference; the composite curvature along the chosen mode against UKS-B3LYP's own (a sanity line, not judged).
- Correction read-out (not judged, for the 28th): the per-family diagonal of the cation's DFT–DFT K against the neutral's (E6 machinery), i.e.
  whether the proxy correction of the cation resembles the neutral's.

**What counts as the gap closed (fixed).** Both rows exist with status done and no imaginary mode, and both prices are on record. The
affordability table gets a benzene⁺ and a naphthalene⁺ line with the measured price; the P26 label plan names the ULNO route for cations.
If the ULNO path fails (the forge's (T) for unrestricted references is the `_slow` implementation): the row still stands, the price line says
"ULNO-CCSD(T) not available; ULNO-CCSD price = …" and canonical UCCSD(T)/cc-pVDZ of benzene⁺ alone is queued as the fallback.

**Not registered:** anything about the size of the cation correction (that is what the row is for); the choice of a third cation.

**Cost.** hel1-14 (CPX62) after route 2 (≈ Friday 25 September afternoon): rows ≈ 1–3 h each at the A-layer median, prices ≈ 3 × P each.
