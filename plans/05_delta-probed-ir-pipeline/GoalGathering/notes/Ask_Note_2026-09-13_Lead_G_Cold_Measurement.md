# Ask note 2026-09-13 — lead G: one laboratory measurement that would make the pyrene rung decidable (a question for the supervisor)

*Written at the user's request ("doe lead G voor de begeleider") after the reflection of 13 September and its literature check. It sharpens §13 item 3 of the proposal from "a source the search missed" to "a source or a measurement, specified". Every number below is Module 03's own (`modules/03_lab_scoreboard/out/U_BAND.md`, `out/cold_columns_items61_62.md`, `out/origin_columns_naphthalene.md`, `notes/Research_Note_2026-09-05_R2_GasPhase_MidIR_Sources.md`); every record is Crossref-verified in the bibliography. It is a draft the user decides to send or not; nothing in it changes a rule of the plan.*

## 1. The situation the numbers describe

The plan's promise is a coupled-cluster correction of order 5 cm⁻¹ per band (benzene: 5.45 cm⁻¹, Esposito et al. 2024), scored per family against laboratory band centres whose uncertainty u_band must be small enough to decide. Module 03 measured u_band for every gas-phase record the plan holds:

| rung | species | best available source in 6–15 µm | u_band per family (cm⁻¹) | decides at 2.5 / 5 / 10 |
|---|---|---|---|---|
| R0 | benzene | NIST Quantitative IR (Chu et al. 1999), 296 K | 2.55 (floor form) | yes / yes / yes |
| R1 | naphthalene | Pirali et al. 2009, 0.005 cm⁻¹, resolved fundamentals; ν46 origin to 10⁻⁶ (Albert et al. 2011; Pirali et al. 2013, jet) | 0.5 (head-to-origin bound); ν46 ≈ 0 | yes / yes / yes |
| R2 | pyrene, chrysene, triphenylene | NIST WebBook gas records, 8 cm⁻¹ resolution, 523 K, hot bands unresolved | **8.6–16.1** by family (C–C families 16) | no / no / partly (CH-oop, CH-ip-bend only) |
| R2 | tetracene | Lemmens et al. 2019, jet-cooled FELIX, bandwidth ≈ 1 % | ≥ 5–17 (resolution term alone; lower bound) | no / partly / yes |
| R2 | pyrene, one band | Brumfield, Stewart & McCall 2012, rotationally resolved ν68 (≈ 8.5 µm), jet | ≈ 0 for that band | one band only |
| R3 | coronene | Lemmens, Rijs & Buma 2021, jet-cooled FELIX, six 6–15 µm bands | ≥ 8–16 (lower bound) | no / no / yes |

So the ladder is decidable at R0 and R1 and **not decidable at the C–C families of R2 and R3 with any source the plan has found** — not for lack of compute, but for lack of a band centre known to better than about 5 cm⁻¹ in the gas phase. The compute tables of §8 and §12 price thousands of cluster hours to *produce* the R2 corrections; the numbers above say they could not be *scored* at the promised level once produced. A cold, resolved measurement of one molecule is therefore the cheapest lever in the project.

## 2. The ask, specified

**Molecule: pyrene** (R2's anchor: 26 atoms, 72 modes, D2h; the first molecule beyond PAHdb's anharmonic front; the 6.2/7.7/8.6/11.2 µm carriers all present; one rotationally resolved band already exists, ν68, which calibrates any new measurement). Second choice: chrysene or triphenylene (the isomer-discrimination question of §5.2, which Module 03 showed cannot be closed on existing gas-phase data). Third: coronene's 7.7 and 8.8 µm bands, where the cold FELIX centres and the hot Joblin et al. 1994 centres disagree by 10–19 cm⁻¹ for a reason the plan has not found (proposal §13, question 7).

**Bands: one strong fundamental per family**, so that each family of the scoreboard gets one decidable entry:

| family | region | why this one |
|---|---|---|
| C–C stretch | 6.2 µm (≈ 1600 cm⁻¹) | the family with the largest expected correction (benzene: −36 to +65 cm⁻¹ per mode in the stand-in) and u_band 16 today |
| C–C stretch / C–H in-plane | 7.7 µm (≈ 1300–1450 cm⁻¹) | the astronomical 7.7 µm complex; u_band 16 today |
| C–H in-plane bend | 8.6 µm (≈ 1180 cm⁻¹) | ν68 of pyrene is already resolved (Brumfield 2012): the cross-check |
| C–H out-of-plane | 11.2–13 µm (≈ 850, 710 cm⁻¹) | the size/edge diagnostic; the family X17 found cannot be σ/π-split, so a measurement is the only arbiter |

**Conditions:** supersonic jet or equivalent cold gas phase (u_T = 0, no hot-band envelope); **band-centre precision ≤ 1 cm⁻¹**, i.e. either rotational resolution (synchrotron FTIR on a jet, as Pirali et al. 2013 did for naphthalene ν46 at Jet-AILES, or the SLS/ETH instrument of Albert et al. 2011; or a QCL/OPO jet measurement as Brumfield 2012) or, failing that, a free-electron-laser measurement with the **bandwidth stated per band and the centres tabulated with uncertainties** (at 0.5 % of 1400 cm⁻¹ that is u_band ≈ 3–4 cm⁻¹: decides at 5, not at 2.5 — still four times better than today's 16). The deliverable the plan needs is a **table of band centres with uncertainties**, not a spectrum figure (Module 03 ingests band lists; the 2019/2021 FELIX papers give tables, which is why they could be used at all).

**Target uncertainty:** u_band ≤ 2.5 cm⁻¹ per band (the R0 benchmark floor, Module 03 `U_BAND.md`), which makes the R2 C–C families decidable at the plan's own 5 cm⁻¹ promise.

## 3. What the student offers in return (the plan's discipline, unchanged)

- The scoreboard rows for the chosen bands are **pre-registered before the measurement**: family, predicted band, the Δ₂ = 0 null row, the opponents' values (PAHdb v4.00 scaled harmonic; PAHdb Anharmonic where it exists), the beat margin. Laboratory numbers enter before, never after, a comparison is scored (Ladder §2; the R2 dated note of 5 September).
- The pipeline's own prediction with its error budget is sealed before the centres arrive (the same seal discipline as the benzene CC energies).
- A one-page cost table: the beamtime or laser time of one such measurement against the cluster hours of §12 for R2 — so the supervisor can weigh the two levers on the same page.
- Authorship and data ownership as the laboratory decides; the plan only needs the table.

## 4. What is not in the student's hands, said plainly

Beamtime and laser time are proposals with their own calls and reviewers; the student cannot promise a measurement, only ask whether the supervisor's network (the FELIX work of Lemmens, Rijs and Buma; the supervisor's own 3 µm work with Maltseva et al. 2015/2016) reaches an instrument that can do it, and whether an existing but unpublished table already does. If neither, the honest consequence for the proposal is the one §12 and the duration note already carry: R2 is *produced* and *reported against the hot records at 10 cm⁻¹*, not *decided* at 5, and the proposal's claim for R2 is written that way.

## 5. Proposed wording for §13 item 3 (replacing "at better than 8 cm⁻¹ resolution and known temperature")

> **Laboratory sources — or one measurement.** Module 03 finds no gas-phase source that makes the C–C families at the pyrene rung decidable at the plan's 5 cm⁻¹ promise (hot records: u_band 8.6–16 cm⁻¹; jet-cooled FELIX lists: ≥ 5–17 from the stated bandwidth). One cold, resolved measurement of pyrene — one strong band per family at 6.2, 7.7, 8.6 and 11–13 µm, band centres tabulated to ≤ 1 cm⁻¹ — would make the rung decidable; a source the supervisor knows of, or an instrument in the supervisor's network that could take the request, is the cheapest lever the project has, cheaper than any cluster request in §12. The student pre-registers the scoreboard rows before any such number arrives (`notes/Ask_Note_2026-09-13_Lead_G_Cold_Measurement.md`).
