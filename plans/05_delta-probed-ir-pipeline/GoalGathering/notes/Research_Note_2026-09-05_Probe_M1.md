# Dated note 2026-09-05 — probe M1 (frozen spaces) ran: what it measured and what it asks

**Status.** A dated note under the freeze of 2026-09-04: it names measurements (printed by
`probes/m1_frozen_spaces.py` and `probes/m1_canonical_truth.py`, results in `probes/results_m1/`)
and the design questions they raise. **It changes no frozen rule by itself.** Proposals are marked
*proposal* and wait for the user's decision. The τ the Q6 bias line would be judged against does not
exist yet (pilot note), so **no verdict is printed here either**; the numbers are given in cm⁻¹ so the
reader can hold them against any τ. All three benzene Δ₂,ii stay sealed: the note reports only
differences between local-CC arms and canonical CCSD(T), never a CC−DFT curvature.

## 1. What ran (WSL, `~/qc05`: pyscf 2.14.0, pyscf-forge 1.1.1; 8 threads; benzene at the dry-run B3LYP/6-31G* geometry)

| Run | Basis / LNO thresholds | Points | Wall | Result files |
|---|---|---|---|---|
| Smoke test (mode 12, q ∈ {−1, 0, 1}) | cc-pVDZ / normal [10⁻⁵, 10⁻⁶] | 3 | 21 min | `benzene_cc-pvdz_normal_smoke/` |
| First full run (arm A **without** semicanonicalisation) | cc-pVDZ / normal | 27 | 15:40–18:15 (killed with the WSL VM at 22 points), resumed 18:22–18:48 | `benzene_cc-pvdz_normal/` |
| Canonical CCSD(T) truth line, same 27 geometries | cc-pVDZ, frozen core, same DF-RHF reference | 27 | 20 min (44–48 s per point) | `canonical_truth_sealed.json` (copied into every M1 directory) |
| **Rerun, arm A semicanonicalised** (the numbers of §2) | cc-pVDZ / normal | 27 | 19:11–21:37 (≈ 5.5 min per point, three arms) | `benzene_cc-pvdz_normal_semican/` |
| **Tight thresholds** [10⁻⁶, 10⁻⁷] (§2.2b) | cc-pVDZ / tight | 27 | 21:45–02:07 (≈ 9.5 min per point, three arms; 1.4 GB) | `benzene_cc-pvdz_tight/` |
| **Anchor basis, tight thresholds** (P9 ii; decision 16; §2.2c) | cc-pVTZ / tight | 27 + 27 canonical | 2026-09-06 07:31 → 2026-09-08 09:23 (three arms, 5,944–7,093 s per point, 48 h), then the canonical truth line 09:23 → 17:31 (850–1,272 s per point, 8.1 h); chain 58 h | `benzene_cc-pvtz_tight/` (`CANONICAL_COMPARISON.md`, `_composite.md`) |

Modes (chosen by the script from the dry run's Hessian): **12** (1020 cm⁻¹, the totally symmetric
mode; dry-run family label CH-ip-bend), **18** (1357 cm⁻¹, a CC-stretch), **6** (865 cm⁻¹, CH
out-of-plane). *Correction 2026-09-06 (found by the proposal's cold read):* the script's labels were
wrong — mode 18 is **non-degenerate** (its neighbours are 1187 and 1387 cm⁻¹; it shares its
representation with the 1186 cm⁻¹ mode it couples to), and mode **6 is one component of a degenerate
pair** (modes 6 and 7 both at 864.7 cm⁻¹). The Ladder's requirement — one totally symmetric, one
degenerate, one non-symmetric mode — is therefore met, with the roles of 18 and 6 exchanged relative
to the log's wording; no number changes. Nine points q ∈ [−1, 1] per mode, the Q6 estimator's
grid. Arms as the Ladder §3 writes them: **A** frozen–frozen (transported occupied set and transported
LNO spaces, impurity solves only), **B** transported occupied set with fresh LNO spaces, **C** fresh
localiser and fresh LNO spaces.

## 2. What it measured

**Erratum 2026-09-10 (factor 2 in every frequency bias printed before this date).** In the
dimensionless normal coordinate the probes use (E = ½ ω q², ω in E_h) the curvature is ω, so a
curvature difference 2·a₂ between two energy curves is **twice** the first-order frequency shift;
the frequency bias is a₂, not 2·a₂. The comparison script converted 2·a₂ to cm⁻¹ and labelled it
"≈ Δω", and every bias in this note, the proposal, the README and the blog post inherited the
factor. Verified on 2026-09-10 against the dry run's own identity diag(Δ₂ᵠ) = 2·δω (stageA:
+156.2 = 2 × 78.1 cm⁻¹ on mode 6). The script (`m1_canonical_truth.py`), `m1_basis_sensitivity.py`,
the report files and every number below were corrected on 2026-09-10; σ values (µE_h) and the
µE_h curvature columns were never affected; every ratio and every conclusion stands. Headline
values now: composite frequency bias of arm A **+0.07 / +0.015 / +0.18 cm⁻¹** (cc-pVDZ tight) and
**+0.47 / +0.03 / +0.79 cm⁻¹** (cc-pVTZ tight); DZ → TZ change of the canonical frequency
**+67 / −33 / −73 cm⁻¹**.

**2.1 The object exists and reloads.** Round trip E_A(0) − E_C(0) = 0.0000 µE_h in every run (target
≤ 10⁻³ µE_h). After the VM kill the run was resumed by **reloading** `frozen_spaces_reference.npz`
(not recomputing it): E_A(0) from the reloaded spaces − E_A(0) of the interrupted run = **+0.0000 µE_h**,
and the sha256 over the reloaded arrays reproduced the original hash. That is the pipeline's own
reload path, tested by accident and passed. (The reference construction itself is not
bit-reproducible between runs — thread order — so a resumed run must reload, never recompute; the
energies agree between runs to better than the 0.005 µE_h the tables show.)

**2.2 Smoothness and bias against canonical CCSD(T), cc-pVDZ, normal thresholds** (rerun; residual σ
about a degree-4 fit in q, the Q6 estimator with ν = 4; a₂ the q² coefficient of the even part of
E_arm − E_canonical, so **2·a₂ is the bias the arm puts on that mode's CC curvature**, E = ½ ω q²):

| mode | arm | σ, bare LNO-CCSD(T) (µE_h) | bias 2·a₂, bare (cm⁻¹) | σ, composite (µE_h) | bias 2·a₂, composite (cm⁻¹) | a₄ |
|---|---|---|---|---|---|---|
| 6 (865, CH-oop) | **A** | **0.002** | +13.8 | **0.003** | **+1.30** | ≈ 0 |
| | B | 6.6 | −5.05 | 1.4 | −0.80 | large |
| | C | 8.9 | +3.05 | 8.7 | +11.4 | large |
| 12 (1020, tot. sym.) | **A** | **0.005** | +2.65 | **0.005** | **+0.25** | ≈ 0 |
| | B | 7.4 | −11.0 | 1.6 | −2.60 | large |
| | C | 10.7 | +13.8 | 10.9 | +14.1 | large |
| 18 (1357, CC-stretch) | **A** | **0.059** | +6.05 | **0.059** | **+0.90** | ≈ 0 |
| | B | 10.5 | +14.0 | 3.4 | +2.75 | large |
| | C | 11.1 | +10.0 | 4.4 | +0.45 | large |

"Composite" is the energy the LNO literature reports: E_LNO-CCSD(T) + [E_MP2(full) − E_MP2(LNO)], the
canonical DF-MP2 correction for the truncated space (pyscf-forge's `e_corr_pt2corrected`); MP2(full) is
canonical and smooth, so it adds no roughness. The a₂ of arms B and C are ill-determined (their 7–11
µE_h of noise over nine points) and listed only for completeness.

Reading: **arm A is three orders of magnitude smoother than either re-selecting arm** (0.002–0.06
against 7–11 µE_h; the 7–11 µE_h is the LNO re-selection discontinuity the plan expected, and it is
five times the 2 µE_h mode E needs for the off-diagonals — dry-run note §2). **Arm A's bias is a clean
q² term** (a₄ ≈ 0, so it does not depend on the step size and is exactly a diagonal curvature bias):
2.6–14 cm⁻¹ on the bare energy, **0.25–1.3 cm⁻¹ on the composite** — the frozen space loses a
q²-proportional piece of correlation as the geometry moves, and the full-space MP2 recovers most of it.
The bias is largest where the transported virtual space loses most (mode 6: s_min vir 0.82 at |q| = 1,
pre-Löwdin off-diagonal 0.16).

**2.2b The same scan at tight thresholds [10⁻⁶, 10⁻⁷]** (finished 2026-09-06 02:07; same truth line, same
estimator; the thresholds probe 4 timed):

| mode | arm | σ, bare (µE_h) | bias 2·a₂, bare (cm⁻¹) | σ, composite (µE_h) | bias 2·a₂, composite (cm⁻¹) | a₄ |
|---|---|---|---|---|---|---|
| 6 (865, CH-oop) | **A** | **0.002** | +0.95 | **0.003** | **+0.07** | ≈ 0 |
| | B | 0.05 | −0.05 | 0.05 | −0.10 | small |
| | C | 2.1 | +3.15 | 1.7 | +2.45 | large |
| 12 (1020, tot. sym.) | **A** | **0.003** | +0.17 | **0.003** | **+0.01** | ≈ 0 |
| | B | 1.2 | +1.75 | 0.6 | +1.10 | large |
| | C | 2.7 | +4.55 | 2.1 | +4.10 | large |
| 18 (1357, CC-stretch) | **A** | **0.056** | +0.53 | **0.056** | **+0.18** | ≈ 0 |
| | B | 0.9 | +2.10 | 0.4 | +1.20 | large |
| | C | 0.9 | +1.40 | 0.5 | +0.75 | large |

Reading: tightening the thresholds shrinks arm A's bias by an order of magnitude (bare 2.6–14 → 0.18–0.95
cm⁻¹; **composite 0.25–1.3 → 0.015–0.18 cm⁻¹**) at unchanged smoothness, and it also quietens the
re-selecting arms (B 0.05–1.2, C 0.9–2.7 µE_h, against 7–11 at normal thresholds) — the larger the
active space, the less there is to re-select. Arm A's σ is the same 0.002–0.06 µE_h at both threshold
settings, so it is not an LNO-size effect but the floor of the impurity solves themselves (the SCF's
σ is 0.002–0.015 µE_h on the same grid). Cost: 9.5 against 5.5 min per three-arm point.

**2.2c The anchor basis: cc-pVTZ, tight thresholds** (chain finished 2026-09-08 17:31; its own
canonical CCSD(T) truth line at cc-pVTZ, same DF-RHF reference, frozen core; same estimator; printed
by `m1_canonical_truth.py` into `benzene_cc-pvtz_tight/CANONICAL_COMPARISON[_composite].md`):

| mode | arm | σ, bare (µE_h) | bias 2·a₂, bare (cm⁻¹) | σ, composite (µE_h) | bias 2·a₂, composite (cm⁻¹) | a₄ (composite) |
|---|---|---|---|---|---|---|
| 6 (865, CH-oop) | **A** | **0.010** | +16.3 | **0.007** | **+0.47** | ≈ 0 |
| | B | 0.89 | +1.65 | 0.19 | +1.60 | small |
| | C | 0.94 | +2.80 | 1.47 | +2.60 | large |
| 12 (1020, tot. sym.) | **A** | **0.002** | +1.80 | **0.002** | **+0.03** | ≈ 0 |
| | B | 1.00 | −2.15 | 0.17 | −0.35 | small |
| | C | 3.41 | +5.70 | 3.41 | +4.75 | large |
| 18 (1357, CC-stretch) | **A** | **0.021** | +5.25 | **0.021** | **+0.79** | ≈ 0 |
| | B | 2.33 | +5.65 | 0.39 | −0.53 | large |
| | C | 1.32 | +9.30 | 0.68 | −0.25 | large |

Reading. (i) **Smoothness holds at the anchor basis**: arm A's σ is 0.002–0.021 µE_h, the same
floor as at cc-pVDZ and two orders under the re-selecting arms (B 0.17–0.39, C 0.68–3.4 µE_h
composite). (ii) **The composite bias grows with the basis**: cc-pVDZ tight +0.07 / +0.015 / +0.18
→ cc-pVTZ tight **+0.47 / +0.03 / +0.79 cm⁻¹** (modes 6 / 12 / 18), factors 6.7, 2 and 4.4. The bare
bias is far larger (+16.3 cm⁻¹ on the out-of-plane bend, +5.3 on the C–C stretch) and the
LNO-MP2 correction absorbs 85–97 % of it; what remains is a systematic curvature error of the
frozen object at the anchor, not noise, and it enters Δ₂ directly. (iii) **Where it is largest, the
transported virtual space overlaps the fresh one least**: s_min of the virtual overlap at |q| = 1 is
0.66 (mode 12), 0.57 (mode 18) and **0.36** (mode 6), against 0.81–0.87 at cc-pVDZ (§2.3); the
larger basis has more virtual space to lose. The occupied overlap is unchanged (≥ 0.988). (iv) The
raw A−C difference reaches +64 µE_h at the ends of mode 6 (bare), of which the LNO-MP2 piece is
+69; the composite A−C there is −5 µE_h. (v) The a₄ of arm A is ≈ 0 on every mode: the bias is a
pure curvature term, so a degree-2 correction per mode would remove it where a canonical reference
exists (R0–R1) — and only there.

What this means for the Ladder is a judgement at the pilot note, not here: the bias is judged
against τ and the R0 beat margins, which are not fixed yet. On benzene the NIST scoreboard's
resolution is 0.12 cm⁻¹ and u_band is expected below 1 cm⁻¹, so a +0.8 cm⁻¹ frequency bias on the
C–C stretch would be visible in a "beat" claim on that family. §3 adds proposal P10.

**2.2d Basis-set sensitivity of the canonical curvature, cc-pVDZ → cc-pVTZ** (decision 26, input i;
printed 2026-09-08 by `m1_basis_sensitivity.py` from the two existing truth lines and the arms'
full-space DF-MP2 energies, no new calculation; `results_m1/BASIS_SENSITIVITY_dz_tz.md`). The even
part of E(q) is fitted per basis; the table gives the change of the curvature 2·a₂ from DZ to TZ in
cm⁻¹, split by energy component. Absolute curvatures are not printed.

| mode | total CCSD(T) | SCF | CCSD(T) correlation | of which (T) | MP2 correlation | MP2 share of the correlation change |
|---|---|---|---|---|---|---|
| 6 (865, CH-oop) | **+66.8** | +44.2 | +22.6 | −2.60 | +14.8 | 0.65 |
| 12 (1020, tot. sym.) | **−33.2** | −22.4 | −10.8 | −0.40 | −11.8 | 1.09 |
| 18 (1357, CC-stretch) | **−72.7** | −50.6 | −22.1 | +2.70 | −16.1 | 0.73 |

Reading. (i) The curvature along the DFT modes at the DFT geometry — the quantity Δ₂ is built
from — changes by **33–73 cm⁻¹** between cc-pVDZ and cc-pVTZ, one to two orders more than the
frozen-space bias of §2.2c and six to thirteen times the only literature figure for the whole
CC−DFT effect (5.45 cm⁻¹ at benzene, item 45, at a near-limit reference). The DZ → TZ step is the
first step of a convergent series, so this is a lower bound on the anchor's distance from the
limit, not the distance; but it says the cold read's finding 4 (the anchor's basis-set error is
unbudgeted) is not a formality. (ii) **Two thirds of the change is the SCF part** (44 / 22 / 51
cm⁻¹), which is converged cheaply: DF-RHF at cc-pVQZ or cc-pV5Z along the same 27 points costs
minutes per point. (iii) Of the correlation part, **full-space MP2 captures 65–109 %**, i.e. an
MP2-level basis correction — the same device the composite of §2.2 uses for the LNO truncation —
would carry most of the correlation remainder at DF-MP2 cost. (iv) The (T) part of the change is
≤ 3 cm⁻¹. (v) σ of the total is 0.001–0.024 µE_h in both bases: the truth lines are smooth.
Consequence recorded under decision 26 in the plan README: a **basis-set line** exists now as a
measured number; the cheap next measurement is the same 27 points at DF-RHF and DF-MP2 in
cc-pVQZ (and DF-RHF in cc-pV5Z), which turns the lower bound into a converging series for the two
parts that carry ≈ 90 % of it and leaves only the CCSD(T)−MP2 remainder (≈ 5–8 cm⁻¹ DZ → TZ here)
for a cluster QZ line. Whether the anchor itself is then **redefined as a composite** —
LNO-CCSD(T)/TZ + [MP2/QZ − MP2/TZ] + [SCF/5Z − SCF/TZ] — is a new proposal (P18) for the user,
after that measurement, not before.

**2.3 Continuity diagnostics** (all runs agree): s_min of the occupied overlap ≥ 0.986 at |q| = 1 on
every mode; s_min of the virtual (LNO) overlap 0.81–0.89 at |q| = 1, 0.95–0.97 at |q| = 0.25; largest
pre-Löwdin off-diagonal ≤ 0.018 (occupied), ≤ 0.16 (virtual). The map is nonsingular throughout
|q| ≤ 1, as the Ladder assumed, and the virtual half is the soft one.

**2.4 The localiser's landing is arbitrary and, on benzene, energetically silent.** The fresh PM
localiser's functional equals the transported set's to 0.1–2 % (7.084 vs 6.926 at mode 18, q = −1),
yet the best-match overlap between the fresh and the transported set drops to 0.67–0.84 on some
points — and **at the same geometry the two runs landed differently** (mode 6, q = +0.25: match 0.667
in the first run, 1.000 in the rerun) while arm C's energies agreed to < 0.005 µE_h. On a D₆h molecule
symmetry-equivalent landings cost nothing; on a lower-symmetry molecule they would not be equivalent.
Round-9 Pass B's finding 2 (re-localise-and-assign would mix) is what this column shows.

**2.5 An implementation fact that cost one run.** pyscf-forge's `make_las` semicanonicalises the
active occupied and virtual blocks, and `impurity_solve` relies on it: its MP2 start amplitudes and
its (T) use diagonal orbital energies. The first arm-A override returned the transported vectors as
they were; at displaced geometries they are not Fock-diagonal, the LNO-MP2 piece came out thousands
of µE_h off (5,670 µE_h at mode 6, q = 1) and the (T) was silently wrong — the first run's arm-A bias
read +23/+46/+147 cm⁻¹. The fix diagonalises the Fock matrix within each transported active block
(a rotation **inside** the frozen space; the space, and therefore the object, is unchanged). The
built-in check is now printed per point: the LNO-MP2 piece of A − C, which reads 5–65 µE_h after the
fix. The frozen-space object must be read as "the space, semicanonicalised at x" — proposal P7.

**2.6 Cost.** At cc-pVDZ, normal thresholds, one point with all three arms takes 240–450 s; arm A
costs the same as arm C (the impurity solves are identical; only the LNO construction is skipped).
Peak resident memory 1.3 GB. At cc-pVTZ a local-CC energy costs 2,087 s (probe 4), so the three-arm
scan was estimated at ≈ 2 days and the truth line at 27 × 755 s ≈ 6 h. **Measured (§1 table):** the
three-arm cc-pVTZ point took 5,944–7,093 s (arm C alone at the reference 2,387 s), the scan 48 h; the
canonical cc-pVTZ point 850–1,272 s (mean ≈ 1,080 s, against 755 s in the timing probe — the laptop
was in use), the truth line 8.1 h; the whole chain 58 h on the 24/7 laptop, no failure.

## 3. What it asks (proposals; the Ladder stays as written until the user decides)

- **P7 (definition, no new rule):** the Ladder §3 object bullet gains the words "the transported
  active blocks are semicanonicalised at the displaced geometry (a rotation within the frozen space)".
  Without them the stated object cannot be evaluated by pyscf-forge's solver.
  **Accepted by the user 2026-09-06 (decision 14); the words are in the Ladder §3 object bullet.**
- **P8 (energy definition for arm A):** the local-CC energy the pipeline probes is the **composite**
  E_LNO-CCSD(T) + [E_MP2(full) − E_MP2(LNO)], MP2(full) computed canonically at every point. Measured
  effect: the diagonal curvature bias of arm A falls from 2.6–14 to 0.25–1.3 cm⁻¹ at no cost to
  smoothness and at seconds (cc-pVDZ) to minutes (cc-pVTZ) per point. The Q6 bias line then judges the
  composite, and Q6's arm B is compared on the same footing.
  **Accepted by the user 2026-09-06 (decision 15); written into the Ladder §3 object bullet and the
  bias-line sentence.**
- **P9 (next measurements, already scheduled or cheap):** (i) ~~tight thresholds at cc-pVDZ~~ — done
  (§2.2b: composite bias 0.015–0.18 cm⁻¹); (ii) the
  three-arm scan and the truth line at cc-pVTZ (≈ 2.5 days); (iii) the off-diagonal bias of arm A is
  unmeasured — single-mode scans see only Δ₂,ii — and is read from the R0 probe batch's two-mode pairs
  against canonical two-mode points, which the R0 pilot should include (a small deck number).
  **Accepted by the user 2026-09-06 (decision 16).** (ii) started 2026-09-06 07:31 (tight thresholds,
  27 points × three arms, then the cc-pVTZ truth line and both comparisons; expected end of the scan
  ≈ Tuesday 2026-09-08 midday, the truth line ≈ 6 h later; `results_m1/benzene_cc-pvtz_tight/`). (iii)
  becomes a deck number of the R0 pilot: canonical CCSD(T) at the two-mode ± points of the largest
  same-representation coupling pairs (the number frozen in the deck; 30 pairs = 60 points is the
  working figure: 45 min at cc-pVDZ, ≈ 12.6 h at cc-pVTZ), from which the off-diagonal bias of arm A
  is read as 2·a₂ of E_A − E_canonical along the pair, before the pilot note says anything about arm A.

**P10 (new, 2026-09-08, from §2.2c) — what to do with the anchor-basis curvature bias of arm A.**
The frozen object is smooth at cc-pVTZ but carries a composite frequency bias of +0.03 to +0.79 cm⁻¹
on benzene, largest where the transported virtual space overlaps the fresh one least. Three
options, none decided here: (a) **record it** as arm A's measured floor at R0 and print it beside
every Δ₂ in the pilot note — no change to the object; (b) **measure whether a larger frozen virtual
space removes it**: one more benzene cc-pVTZ scan with a reference whose LNO virtual space is the
union of the spaces selected at q = 0 and q = ±1 (or with thresholds one decade tighter), ≈ 2 days
plus the existing truth line; (c) **correct it per mode where a canonical reference exists**: the
canonical endpoints already budgeted for the off-diagonal bias (decision 16) give a₂ per mode, and
arm A's a₄ ≈ 0 means a degree-2 correction is complete — but this exists only at R0–R1 and says
nothing about R2+. (a) is honest and free; (b) is the only option that could make the object better
at every rung; (c) is a calibration, not a fix. The user decides; the Ladder stays as written.
**Decided 2026-09-08 (user): (b) — measure whether a larger frozen space removes the bias (decision
20).** Implementation chosen by the author from the two forms named under (b): **thresholds one decade
tighter** ("xtight", [10⁻⁷, 10⁻⁸]), not the union of the q = ±1 selections — because §2.2c shows arm
C's *fresh* selections at cc-pVTZ tight are themselves more biased than arm A (composite +2.6 / +4.7 /
−0.25 cm⁻¹ against A's +0.47 / +0.03 / +0.79), so adding fresh endpoint selections to the reference is
not the lever; more space is. At tight thresholds the reference already keeps 172 of 243 virtuals
per fragment active (frozen_spaces_reference.npz: 71 frozen virtuals), so one decade tighter moves
the object towards the full space, and the cc-pVDZ step normal → tight had cut the composite bias
tenfold (§2.2b). Only arm A is rerun (`--arms A`, new): arms B and C do not depend on the reference
and stand from the tight run; the cc-pVTZ truth line is reused (copied into the new directory; the
truth script skips done points). Smoke test of the new code path at cc-pVDZ tight, mode 12, three
points (`benzene_cc-pvdz_tight_smokeA/`, 17:42–17:56): round trip 0.0000 µE_h, arm A alone 168 s per
point against 570 s for three arms, the comparison tolerates the missing arms. **Started 2026-09-08
17:56** (`results_m1/benzene_cc-pvtz_xtight/`, log `benzene_ccpvtz_xtight.log`); expected ≈ 1.5–2
days (arm A per point ≈ 2–2.5× the tight arm-A cost of ≈ 2,200 s); measured after the start: reference 4,300 s
with 219 of 243 virtuals active per fragment, so ≈ 32 h for 27 points — end Wednesday 9 September, early morning.
What it decides: if the composite bias drops by about the cc-pVDZ factor (to ≲ 0.1 cm⁻¹) the anchor
object is run at xtight and the cost record carries the factor; if it does not, the bias is a
property of transport, not of space size, and (a) or (c) is the remaining choice.

**Result (2026-09-12, 11:48; the run died with its session on 2026-09-09 after 5 points and was
resumed detached on 2026-09-11 05:16, reference spaces reloaded, reload test −0.0000 µE_h;
`probes/results_m1/XTIGHT_READIN.md`, printed by `m1_xtight_readin.py` from the chain's comparison
files against the reused cc-pVTZ truth line).** Arm A at xtight [10⁻⁷, 10⁻⁸], 27 points:

| mode | family | σ tight → xtight (µE_h) | Δω bare tight → xtight (cm⁻¹) | Δω composite tight → xtight (cm⁻¹) |
|---|---|---|---|---|
| 6 | CH-oop 865 | 0.007 → 0.004 | +16.29 → +2.08 | **+0.47 → +0.11** |
| 12 | CH-ip-bend 1020 | 0.002 → 0.003 | +1.78 → +0.23 | **+0.03 → −0.01** |
| 18 | CC-stretch 1357 | 0.021 → 0.044 | +5.26 → +0.76 | **+0.79 → +0.23** |

The composite bias falls by a factor 3–4 on every mode (the bare bias by 7–8), the quartic
coefficients stay near zero, and the smoothness is unchanged: **the residual at tight was
local-correlation truncation, not transport — option (b) of P10 is confirmed and decision 20
closes.** The anchor object runs at xtight; the cost factor at benzene is ≈ 2 (4,576 s median per
frozen-arm point against ≈ 2,200 s at tight; the tight run's 6,441 s per point included arms B and
C), and the naphthalene xtight factor is owed as one timed energy before the R1 deck is priced
(the 11.5 h of the timing probe is the tight figure). What remains of the anchor's distance from
the truth is now at or below the 0.1–0.2 cm⁻¹ level on these modes — the basis-set line (§2.2d;
the QZ/5Z SCF+MP2 line launched 2026-09-12 11:54) is the next term to read.

## 4. What did not change

The three arms, the Q6 estimator, the sealed-energy rule and stop 1 are as the Ladder writes them.
The candidate code can freeze spaces (stop 1 is not triggered). No Δ₂ number is readable from this
note or its result files; the canonical truth line is sealed alongside the arm energies.

Printed by `probes/m1_frozen_spaces.py` (REPORT.md per run) and `probes/m1_canonical_truth.py`
(CANONICAL_COMPARISON.md and its `_composite` twin per run). Commits: b1e97a6 (smoke test), 5c0f6ea
(first run, truth line, resume, semicanonicalisation), this note's commit (rerun).
