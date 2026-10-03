# Design note, 3 October 2026 — pool 3: the three missing axes (charge, nitrogen in large rings, size)

*Decision 54 (the user, 3 Oct 2026 11:3x: "Goed plan. Zet alles wat nodig is om dit goed en secuur te doen op de takenlijst. Besteed aandacht aan code
kwaliteit."; answers (a) 60 cations, (b) five-ring scaffolds in batch 1, (c) benzene⁺ as a CC anchor on the CCX53 after anthracene). Companion of the
pool-composition rule (decision 52, `Design_Note_2026-10-03_Pool_Composition_Rule.md`). Working rows: TASKS "Pool 3".*

## Where the pool stands (3 Oct 2026, 847 molecules done, the 200 running on the CPX62)

| scaffold family | done | in the 200 | by decision 52 |
|---|---|---|---|
| 2 fused rings, carbocyclic (naphthalene, fluorene) | 335 | +102 | far past saturation — nothing more |
| 1 ring N (pyridines) | 152 | 0 | finished |
| 3 fused carbocyclic / 3 fused with N | 76 / 75 | 0 | finished |
| 4 fused carbocyclic (fluoranthene, pyrene) | 29 | +55 | covered after the 200 |
| 2 fused with N (quinolines) | 51 | 0 | +10 to finish |
| biphenyl-type (2 separate rings) | 20 | +6 | +10 to 30 |
| 2 or 3 fused rings with O or S | 4–15 each | +16 | under 30 |
| 4 fused rings with N (aza-pyrenes, aza-fluoranthenes) | 0 | 0 | missing |
| 5 fused rings (perylene, benzo[a]pyrene, benzo[e]pyrene) | 0 | 0 | missing |
| **radical cations** | **0** | 0 | missing |

Counts from `corpus/manifest.csv` (status done, layers A/A2/B) through `probes/rungC_error_map.kind_of`. The 200 close the four-ring gap; what remains
are three missing **axes**, not missing families: charge, nitrogen inside large ring systems, and size. These are the three the astrophysical goal needs
most: PAH cations carry the 6.2 / 7.7 / 8.6 µm bands in many sources, the 6.2 µm band position is the argument for nitrogen in the ring, and the
mandate's object is a large PAH.

## Pool 3 — ≈ 245 molecules in two batches

**Batch 1, the three new axes (150).**
- **60 radical cations** on scaffolds the pool already knows, so the network learns charge as a difference on known ground: benzene⁺ and ≈ 14 substituted
  benzenes⁺, naphthalene⁺ and ≈ 14 substituted, anthracene⁺ / phenanthrene⁺ / pyrene⁺ / fluoranthene⁺ with ≈ 5 children each, quinoline⁺ and pyridine⁺
  with ≈ 4 each. Rows come from `corpus/cation_rows.py` (deck `deck_v1_cation.json`: UKS B3LYP and ωB97X, charge +1, doublet, a seeded 0.01 Å
  distortion so a Jahn–Teller minimum is reachable in c1), started from the neutral corpus geometry.
- **30 aza-four-rings**: 1-, 2- and 4-azapyrene, azafluoranthenes, benzo[h]quinoline / benzo[f]quinoline / benzo[c]phenanthridine-type parents with
  mixed children. No candidates exist in the manifest: the list is generated (`probes/pool3_candidates.py`, see TASKS).
- **30 five-ring scaffolds**: perylene, benzo[a]pyrene, benzo[e]pyrene, benzo[k]fluoranthene, picene-type parents with children — the test whether the
  family rule holds at five rings. 2–4 box-hours per molecule.
- The parents of each new family (3–4 per family) go to a new **hold-out (c)**, so every read is per family against its own children count (decision 52).

**Batch 2, filling to 30 (≈ 95):** 2- and 3-fused O/S families +75, biphenyls +10, quinolines +10.

## What the cations require before the first row trains (all on TASKS)

1. **A charge input in the rung-C model.** `rungC_hybrid.HybridDeltaFModel` has no charge or multiplicity input (the older `deltah_model` had one). One
   embedding for (charge, multiplicity) added to the body's scalar channel, **zero-initialised** so that every neutral prediction is unchanged to the bit
   (the lesson of the C2-elements incident: unseen rows are reset, never random), with tests: neutral output identical before and after, equivariance
   kept, `design_check.py` extended to count cation rows and refuse a run whose model has no charge input while the pool holds cations.
2. **A cation gate (noise principle).** UKS finite differences are noisier than closed shell and the Jahn–Teller surface has soft modes. The existing
   benzene⁺ row (`probes/results_m1/cations/benzene`, FD + analytic second route for both functionals) is read first with
   `probes/rungC_family_floor_ceiling.py floor` on that row; then the first ten cation rows get the analytic second route. Only if the floor per family is
   ≤ 1.5 cm⁻¹ (the neutral standard) do the remaining fifty run on FD alone; otherwise every cation row carries the analytic route (cost ≈ 2×).
3. **A cation CC anchor for T3.** Benzene⁺ CCSD(T)/cc-pVDZ was OOM-killed on the CPX62 on 30 Sep (UHF route, 32 GB). On the CCX53 (128 GB) it fits:
   queued after anthracene's Hessian, before the server is deleted; the UHF path is the one gate 1 validates on water (`check` incl. the `dvvVV` patch);
   memory estimate from the 30 Sep log, water dry-run on the CCX53 first (the smoke rule). The unrestricted (T)-lambda C kernel (software ledger row 13)
   stays a separate task: the anchor runs on the validated slow path if the kernel is not ready.

## Registered questions (pre-registration amendment of 3 Oct 11:3x)

- **Q1, charge transfer:** with zero cations in the pool, how much of the cation correction does the neutral-trained network already carry (ratio on
  hold-out (c)'s cations)? Then the curve 0 / 10 / 30 / 60 cations per family — the children learning curve of decision 52 on the charge axis.
- **Q2, nitrogen in large rings:** do the N-three-rings and the carbocyclic four-rings together carry the aza-four-rings (ratio at zero children), and
  how many own children close the gap (0 / 10 / 30)?
- **Q3, size:** do the four-rings carry the five-rings, and does the rule "≈ 30 covers, ≈ 60 finishes" hold at five rings?

Predictions and lines are in the pre-registration; the standard of "covered" is decision 52's: parents ≤ 0.20 with ≤ 60 children. If cations need more
than 60 per family, the charge axis is a per-family cost and the Spectrum Atlas prices a cation as "its family's cations first".

## Cost and timing

Neutral rows ≈ 1 box-hour per molecule on a CPX62 (two runners × 8 threads), five-rings 2–4, cations ≈ 2.5 (UKS, two functionals, the distorted
optimisation). Pool 3 ≈ 150 + 150 + 95 ≈ 400 box-hours ≈ 17 days on one CPX62 ≈ €85 at €0.208/h; a second CPX62 halves the wall time if Hetzner's
limits allow it. Start when the 200 finish (≈ 10–14 Oct) or earlier on a second box; batch 1 first; the merge path is the one of the 200
(`fetch_nextpool.sh merge`, dry-run on a corpus copy before the first merge).

## Code quality (the user's explicit ask)

Every new switch with tests; ruff clean; py_compile + a water or 2-epoch smoke before any queued job; `design_check.py` before every training run;
the candidate generator deterministic (canonical SMILES, no duplicate against the manifest, heavy-atom cap, a frozen list committed with its hash);
cation rows validated by the second route before they enter a release; no run on the production checkout; registrations before runs, records after reads.
