# The remaining DFT and CC computations: routes, prices, blockers (23 Oct 2026)

Desk work for TASKS 92–97 (the user, 23 Oct: what the corpus fill and the anchor cover cost on the laptop, Helsinki, a PC and Snellius;
whether one month of Helsinki holds it all). Every number below names its input. The fits ran in scratchpad scripts beside the cation run;
TASKS 92 turns them into a tested `price` action of `probes/anchor_plan.py`.

## 1. What is needed

| block | molecules | basis of the price |
|---|---|---|
| CC anchor cover (2 per cell, ≤ 26 atoms) | 86 (61 neutral, 25 cations) | `out/anchor_plan/selection_m2_max26.md`: 7,045 CPX62 hours ≈ €1,465 by the cost rule of anchor set three |
| its composite MP2 step (cc-pVDZ + cc-pVTZ gradient rows) | 86 | section 3 |
| corpus fill to 30 per cell (TASKS 85/87) | 405 (no cations) | `out/anchor_plan/fill_t30.json`, section 2 |
| cation candidates for the 27 short cation cells (TASKS 86) | 260 | section 7 |
| lever 5 (ten large PAHs) / TASKS 74 (chain 41's sixty) | 10 / 60 | ≈ €80 / ≈ €120 on the CCX53 (TASKS, 15 Nov plan) |
| S2b (anharmonic learning curve) | 24 new scaffolds | ≈ €97, 6.5 days on three CPX62 (the S2b rows of TASKS) |

## 2. The corpus fill per machine

Fits of seconds = e^a · n^b on finished rows of the corpus deck `9e27bf8e9348` (psi4, finite differences of analytic gradients,
grid 75/302), n = 6-31G* functions, main ledger plus shard ledgers:

| machine class | rows | fit | fill (405) |
|---|---|---|---|
| CPX62, one 16-thread runner | 601 | e^−9.25 n^3.22 (scatter ×1.16) | 867 runner-hours |
| CPX62, 8-thread runner (two per server) | 315 | e^−8.89 n^3.20 (scatter ×1.10) | 1,098 runner-hours = 549 server-hours ≈ €114 |
| laptop (Ryzen 7 260, 8 cores) | 70 | ×1.29 of the 8-thread runner at the same size (quartiles 0.95–1.77) | ≈ 1,420 h |

The corpus rule (corpus README: new layers get analytic Hessians, or grid 99/590 where finite differences remain) makes the deck price a
lower bound. The analytic labels as the labels server makes them (both functionals + APT, 8-thread lanes on the CCX53):
0.149 · n_atoms^3.54 s, fitted on 707 molecules of 8–30 atoms (lane logs, 23 Oct 03:4x UTC) → **2,658 lane-hours = 664 CCX53 hours
≈ €570**. Extrapolated: 33 fill molecules lie above the CPX62 data's largest size (401 functions), 127 above the lanes' 30 atoms.

## 3. The MP2 step of the cover

Scaled from the five anchors of 20 Oct (`probes/results_m1/dfmp2_anchors_2026-10-20/`: `time -v` wall time and peak RSS, NBF and the
gradient count from each psi4 log; laptop, WSL, 6 threads): per gradient, cc-pVDZ s = e^−18.03 n^3.99, cc-pVTZ s = e^−14.78 n^3.17,
cc-pVTZ peak GB = e^−9.36 n^1.74. With 6N gradients per molecule (no symmetry credit): **≈ 385 laptop hours (≈ 16 days)**; the largest,
generator r4+ N #938 (688 cc-pVTZ functions), ≈ 22 h at ≈ 7.6 GB (extrapolated from 384–472 functions). Unchecked: the 25 cations need
psi4's open-shell DF-MP2 gradient, which the 20 Oct checks did not cover (TASKS 99).

## 4. Memory: two blockers in the CC cover

- **Cations (25 anchors, 2,055 of the 7,045 hours).** The UHF CCSD(T) gradient is not computable at these sizes with the current route:
  benzene⁺ was OOM-killed at 31.5 GB on a CPX62 on 30 Sep, because pyscf's `uccsd_t_rdm` builds unblocked o³v³ arrays (~22 GB each at
  nocc ≈ 15, nvir ≈ 93; ledger 30 Sep). o³v³ grows with the sixth power of size: a 20-atom cation is two orders of magnitude beyond
  that, past any node. The cation anchors need new software first: a blocked UHF (T) density, as the RHF kernels are (TASKS 98).
- **The largest neutrals (6 anchors above 250 cc-pVDZ functions, 2,402 hours).** One measured peak: quinoline (175 functions) 8.59 GB per
  gradient (`results_m1/anchors3_server_2026-10-19/dpir/timing.log`); naphthalene (180) 4.4 GB per lane (ledger 1 Oct). Scaled by n²–n⁴
  to 260–314 functions: ≈ 19–89 GB. Anthracene (246) ran on the CCX53, so 32 GB was never shown at this size. Until one gradient at
  ~300 functions is measured, these six belong on a 64–128 GB machine: a CCX43/CCX53 at Hetzner, or larger Snellius slots.

## 5. Snellius

From public SURF and NWO pages (23 Oct): 1 SBU per Rome core-hour, a Genoa node 288 SBU per hour (1.5 per core; smallest allocation 16
cores + 28 GiB); maximum wall time 120 h per CPU job; tariff €16 (2025) / €17 (2027) per 1,000 SBU. A small application (≤ 1 M SBU, one
year) goes through SURF's service desk, is checked for technical feasibility only and is usually decided within two weeks; the main
applicant needs a tenured, tenure-track or (for small requests, with conditions) temporary position at a Dutch research organisation —
the supervisor's route. Not found without a login: the per-account limit on running jobs. Our own needs: pyscf with our C kernels built
there, and the CC gradients split per displacement (each well under 120 h).

## 6. The block total

| block | Helsinki | Snellius (core-hours ≈ SBU on Rome; ×1.5 on Genoa) | laptop / PC |
|---|---|---|---|
| CC cover, 55 neutrals ≤ 250 functions | ≈ 2,590 CPX62 h ≈ €540 | ≈ 41,000 | — |
| CC cover, 6 neutrals > 250 functions | 2,402 h by the rule, on a larger machine: price open | ≈ 38,000, larger slots | — |
| CC cover, 25 cations | blocked (software, TASKS 98) | blocked | — |
| MP2 step | — | ≈ 2,300 | ≈ 385 laptop h |
| corpus fill, analytic | 664 CCX53 h ≈ €570 | ≈ 21,000 | ≈ 3,400 laptop h (scaled, unmeasured) |
| cation fill (TASKS 86) | not priced there | ≈ 3,500 | ≈ 584 laptop h (6 threads) |
| lever 5 + TASKS 74 | ≈ €200 (CCX53) | not converted | — |
| S2b | ≈ €97 | not converted | — |

Snellius core-hours: one CPX62 hour ≈ 16 cores, one CCX53 lane-hour ≈ 8 cores, one laptop hour at 6 threads ≈ 6 cores — a conservative
equivalence, not a measurement. What one month of Helsinki holds under the 10 Oct limits (5 CPX62 + 1 CCX53): 3,600 CPX62 hours and 720
CCX53 hours — the fill and the 55 smaller neutral anchors fit, the six large neutrals do not without a larger machine, the cations not at
all. Decision 63 stands: new CC anchors are the supervisor's after June 2027; this table is what to show her.

## 7. The cation fill (TASKS 86)

260 radical cations of computed neutrals (twins not yet in the manifest; 822 candidates touch a short cell) fill 15 of the 27 short cation cells to 30, ≈ 584 laptop hours at 6 threads (≈ 24 days), 117–307 6-31G* functions, all under a 12 GB peak by the fit (wall s = e^−2.13 n^2.11, peak GB = e^−6.61 n^1.57 on the 21 measured cations of the 12g run, 100–228 functions — the largest extrapolated). 12 cells stay short (193 places): one-ring cells by nature (benzene⁺ alone is the sextet, pyridine⁺ the aza quintet) and one-ring substituted cations with too few computed neutrals. The cation of a neutral covers the same adjacency cells with charge +1 (`anchor_plan.cells` with layer P3c); the selection is anchor_plan's greedy cover with the laptop hours as cost.
