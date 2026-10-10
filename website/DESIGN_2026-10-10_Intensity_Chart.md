# Spectrum Atlas — an intensity chart per molecule (design, 10 October 2026)

*TASKS 44; the user, 10 Oct: "per molecuul een grafiek met de intensiteiten … eerst ontwerp, daarna implementatie". Design only: nothing is built
until the user has chosen in §8. Publication of the Atlas stays on the user's word.*

## 1. What it is for

An astronomer compares spectra, not lists of wavenumbers: where the bands are **and how strong they are**. The molecule page shows positions only;
`site/src/components/Spectrum.astro` draws every band at unit height ("Intensities are not in the export yet"). The chart adds the heights, says how
well the shape is known, and says plainly where heights do not exist yet. It follows the Atlas design of 23 September (§4.3: spectrum with a micron
axis, a data-table twin, provenance; §6–7: phone layout, WCAG 2.2 AA, no client JavaScript on first load beyond the budget).

## 2. What exists today (measured, 10 Oct)

- **Heights need dipole derivatives (the APT).** 10 corpus molecules have one (B3LYP, CPHF, `probes/dipole_derivs_cphf.py`, 2 Oct): the ten parents
  of hold-out (a). The Atlas has **1,046 molecule pages** (rung ≥ 1; median 22 atoms).
- **One implementation of the heights already exists:** module 08's `m08/spectrum.py` (TASKS 39) computes them from the APT and the cheap rung's own
  Hessian (`hessian_b3lyp.npz`, the Hessian the listed positions come from), counts infrared-active bands (≥ 0.5 % of the strongest), sums
  degenerate partners in its figure, and reads the stated accuracy from module 05's records. The intensities stored inside the APT files are not
  used (8 of 10 were computed with the FD Hessian, 2 with the analytic one).
- **Measured accuracy of the shape** (module 08 certificate, seed means): proxy level (10 unseen molecules) spectrum overlap 0.27 cheap → 0.97
  corrected, height error 0.30 → 0.13; CCSD(T)/cc-pVTZ on benzene overlap 0.26 → 0.59, heights not testable there (symmetry). Open: the APT is
  computed at the cheap level; its CC-minus-B3LYP difference is ≈ 20 % on benzene.

## 3. Coverage: three routes to heights for the other ~1,036 pages

| route | what | cost (measured basis) | when |
|---|---|---|---|
| **A** | heights for the 10 with an APT; every other page keeps unit sticks, labelled "heights not computed yet" | none | at once |
| **B** | a CPHF APT batch for every page (`dipole_derivs_cphf.py` as is) | the 10 laptop timings (194 s at 12 atoms … 6,783 s at 26) fit t ∝ N^4.33 → **≈ 1,030 runner-hours** for 1,046 molecules: ≈ 43 laptop-days, or ≈ 3 weeks and **≈ €107** on one CPX62 (two runners, €0.208/h) | after the five-ring pool and the cations |
| **C** | the APT **from the analytic Hessian's own CPHF**: `analytic_hessians.py` (the labels route) already solves ∂C_occ/∂R (`hessian.rhf.solve_mo1`) — the same response `dipole_derivs_cphf.py` solves again; the APT is a contraction of it with dipole integrals | to be measured (water, benzene): expected a small fraction of the Hessian; every molecule that gets analytic labels would get an APT with it | for the labels not yet computed (the server runs smallest-first; a new version can go in at a molecule boundary, as the 8 Oct list switch did), plus a back-fill of the rest by B |

C needs one probe first: capture `mo1` inside the Hessian route (the same way `cc_dipole_capture.py` captures the relaxed density from
`grad_elec`), compare its APT with `dipole_derivs_cphf.py` on water and benzene (two routes, the noise principle), and time it. **Recommended:**
A now; C measured, then in the labels route if it is cheap; B only for what C does not reach, priced again then.

## 4. What is drawn

- **One figure, "Infrared spectrum at the cheap level (B3LYP)"**: the Lorentzian-broadened curve (FWHM 10 cm⁻¹, module 05's read-out, so the page
  and the accuracy numbers use the same shape) with the sticks under it; wavenumber axis below (high on the left, as now), micron axis above (as now).
- **Default window 500–3500 cm⁻¹ (2.9–20 µm)**, the window of the interstellar bands; the full range in the table.
- **Heights in km/mol** for the sticks (left axis); the curve shares that axis (Lorentzian peak height = A/(π · HWHM)), so the strongest band's peak and
  stick agree. IR-inactive modes have height zero and are not drawn; degenerate partners (within 1 cm⁻¹) are drawn as one stick with the summed height.
- **B3LYP only for heights** (the APT is B3LYP); the ωB97X positions stay in the existing positions chart and table. *(Decision 2 below.)*
- **Text summary** under the figure (WCAG): "7 infrared-active bands; the strongest at 695 cm⁻¹ (14.4 µm), 78 km/mol".
- **Pages without an APT** keep today's unit-height chart with the line "Band heights are not computed for this molecule yet (no dipole
  derivatives); positions only" — never invented heights.

## 4a. Where it sits on the page (added 10 Oct 15:2x; the user: "waar precies komt het in de UI? Desktop, tablet en telefoon?")

**Measured on the live benzene page today (the app's browser).** Phone, 375 px: the chart's SVG is 309 px wide, so its 11-unit labels render at
**4.7 px**, and the spectrum starts **1,427 px down** (below Structure, the status ladder and the request card) on an 812 px screen. Tablet portrait,
820 px: 707 px wide, labels 10.8 px, spectrum 1,284 px down. The present positions chart therefore already fails on phones; the new chart must not
inherit that.

**Desktop (≥ 1024 px, the 2:3 columns; landscape tablets share it with the sticky side column).** A new first card in the right column,
"Infrared spectrum (cheap level, B3LYP)": the chart at the column's width (≈ 700 px), the one-line summary under it, then "How well is this shape
known?" as an open `<details>` block. The existing card "Harmonic frequencies at the cheap level" follows unchanged (its two-functional positions chart
and the table, now with a height column); Second route and Provenance below it. The left column is unchanged.

```
┌ Structure ─────────┐  ┌ Infrared spectrum (cheap level, B3LYP) ───────────┐
│ depiction, 2D/3D   │  │  µm axis                                           │
├ Status ladder ─────┤  │  curve + sticks (km/mol), 500–3500 cm⁻¹            │
│ …                  │  │  "7 infrared-active bands; strongest 695 cm⁻¹ …"   │
├ Request a run ─────┤  │  ▾ How well is this shape known?  (open)           │
└────────────────────┘  ├ Harmonic frequencies (positions, both functionals)┤
                        │  chart + table (+ height column)                   │
                        ├ Second route ─┤ ├ Provenance ─┤
```

**Tablet portrait (768–1023 px, one column).** The same card, full width (≈ 700 px, labels ≈ 11 px), placed **directly under the header, before the
Structure | Status ladder pair** — the spectrum is the page's reason to exist and should not start 1,284 px down. The details block open.

**Phone (< 768 px).** Order: header → **Infrared spectrum** → Structure → Status ladder → Harmonic frequencies → Second route → Provenance →
Request (design §6's order, with the spectrum moved up). The chart gets **its own narrow SVG** rather than the desktop one scaled down: viewBox
≈ 360 units wide so labels render at ≈ 12 px, ticks every 1,000 cm⁻¹, micron ticks at 3, 5, 10, 20 µm, sticks and curve as on desktop; the desktop
SVG and the phone SVG are both in the page and CSS shows one (no JavaScript). The summary sentence under it; "How well is this shape known?" collapsed;
the band table collapsed as "All bands (table)". The same narrow-SVG fix goes into the positions chart, which has the 4.7 px problem today.

**Pages without heights (1,036 of 1,046 today, route A).** No new card; the positions card moves up to the same first place, with the line "Band
heights are not computed for this molecule yet (no dipole derivatives); positions only."

**How the order changes without duplicating the page.** On phones and portrait tablets the two wrappers (`.side`, `.mainc`) get `display: contents`
and the cards an `order`, so one DOM serves all three layouts; on desktop the wrappers stay as they are. Checked at build: 375, 820, 1024 and 1280 px
widths, no horizontal scroll, labels ≥ 11 px rendered, the spectrum card's top within the first screen on phone and tablet portrait.

## 5. How well the shape is known (the block beside the chart)

The same numbers as module 08's certificate, read at export time from the same records (not typed): a two-row table (proxy level; CCSD(T) on
benzene) with "spectrum overlap" and "height error", cheap and corrected; one sentence that the corrected column is measured but not served until a
family is licensed; one sentence on the open APT level. A link to the Methods page, which gets a short paragraph on what the overlap and the height
error mean.

## 6. Data path and code

- `website/export/build_catalog.py` calls module 08's `m08.spectrum.shape(mid, listed_positions)` — **one implementation** for the certificate and
  the Atlas — and writes, per molecule JSON, `intensities_km_mol.b3lyp` aligned with `frequencies_cm.b3lyp.vibrational`, plus `apt_source`,
  `hessian_source`, `n_ir_active`; the summary JSON gets the accuracy block once and the count of pages with heights. A molecule whose computed
  positions differ from its listed ones by > 0.5 cm⁻¹ gets no heights (the consistency check `shape` already reports). `export/SCHEMA.md` updated.
- `Spectrum.astro` takes the `heights` prop it already foresees, draws the curve as one SVG path at build time (≈ 3,000 points thinned to the pixel
  width), no client JavaScript; the modes table gets a height column.
- **Tests:** export — benzene has 7 infrared-active bands, the strongest at 694.6 cm⁻¹, heights aligned with the listed positions; naphthalene has
  none and a reason; the accuracy block equals module 08's. Site — a build check that benzene's page contains the summary sentence and naphthalene's
  the "not computed yet" line.
- After the export change: rebuild the export and module 08's notebook (the memory rule of 8 Oct), a local site build, the axe audit (S6) on two
  pages, phone width checked. **Publication only on the user's word.**

## 7. Effort

Route A with §4–6: about half a desk day (the implementation exists in module 08; the work is the export field, the SVG path, the table column,
tests). Route C's probe: an hour of desk time plus a few minutes of laptop compute (water, benzene) — it can run beside the five-ring runner.
Route B: compute only, scheduled and priced when chosen.

## 8. Decisions for the user

1. **Coverage:** A now, C measured next, B only for the rest (recommended) — or B at once for everything (≈ €107 or ≈ 43 laptop-days), or A only.
2. **Heights for B3LYP only** (recommended; the APT is B3LYP) — or also ωB97X heights, which need a second APT per molecule.
3. **Default view:** broadened curve with sticks (recommended) — or sticks only with a toggle (the toggle needs a small JavaScript island).
