# Review brief — Round 10, Pass B: did the Round-9 closures hold?

**Give this only after Round-10 Pass A's findings are written down and addressed.**

---

## Your role

The hostile domain examiner of Rounds 7–9, or a colleague of equal hostility. Round-9 Pass B
returned *conditional* with six blocking findings that were all closed in spec the same day, and
three of those closures are design changes, not wording: the symmetrised mode-E response, the
projection-only frozen space, and R1 scored per family with a temperature floor. Your job: for
each of Round-9 Pass B's twelve findings decide **closed / re-worded / open** with the deciding
sentence; then attack what the closures themselves introduced. Do not re-open Round 7 or 8
items unless a Round-9 closure re-broke them.

Your verdict must be one of: **green light** (for which scope, under which written conditions),
**conditional** (name the conditions and whether each is in-spec or a measurement), or **no
green light**. Give separate verdicts for the R0–R1 programme and for the promised set beyond R1
if they differ.

## Standing context

Everything in the Round-9 Pass B brief still holds. Since then: Round-9 Pass A (28 closures)
and Pass B (12 closures) landed; Round-10 Pass A has run and been addressed. Web access is
allowed; cite what you open; mark what you recall.

## What to read

Round-10 Pass A's findings first (`Professor_Review_2026-09-04_Round10_PassA.md`). Then the
plan-05 set in the README's reading order (Goal glossary first), then
`Professor_Review_2026-09-04_Round9_PassB.md` for the twelve items you are checking.

## Part 1 — the twelve Round-9 closures

For each of Round-9 Pass B's findings 1–12: closed / re-worded / open, with the sentence that
decides it. Where "re-worded", say what a closed version would say.

## Part 2 — attacks on what the closures introduced

### A. The symmetrised response R_s

R_s(p) = ½[ΔE(+p) + ΔE(−p)] − ΔE(0) = ½ pᵀΔ₂p + (1/24)Δ₄[p⁴] + …. (i) At q_s = 1 along a C–C
stretch, how large is the quartic term relative to the quadratic signal for a CC−DFT
*difference* (not the surface)? Does it bias the recovered Δ₂ by more than τ₇, and should the
deck carry a second amplitude per pattern or accept the bias as a labelled term? (ii) The Q6
mode-E line was derived for E₊ − 2E₀ + E₋ with σ = σ_E·√6/q_s²; R_s uses the same three energies
— is σ(R_s) = σ_E/√2 the right per-response sigma for ρ_noise, or should it be σ_E·√(3/2) (the
ΔE(0) term is shared across all patterns: correlated, not independent)? Say what the noise floor
should be. (iii) Cost: every off-diagonal pattern now costs two energies; does this change the
literature comparison in Budget §3 (O1NumHess counts gradients, CMA counts energies) and the
plausibility of K_off ≪ M²? (iv) The by-products: Δ₁ from R_a of the single-mode block is the
CC−DFT force at the DFT geometry — is it worth printing as a diagnostic of the DFT geometry's
quality, and does the plan risk being read as "correcting the geometry"?

### B. Transported occupied orbitals

C_occ(x) = Löwdin[P_occ(x) C_occ(0)]. (i) The LNO construction defines fragments on localized
occupied orbitals; the transported set is the reference LMOs projected, then symmetrically
orthonormalised — not re-localised. For |q| ≤ 1 how far does the transported set drift from a
localized set (locality measured by the Boys or Pipek–Mezey functional), and does the LNO
truncation at the displaced geometry then become a different truncation than at the reference?
(ii) Does the pyscf-forge LNO code accept an externally supplied occupied set and per-fragment
LNO vectors, or does it re-derive them (if you can open `pyscf/lno/` and say what the API takes,
do; otherwise say what M1 must print to answer it). (iii) The "fresh" arm: E(displaced, fresh)
uses a fresh localiser whose landing is arbitrary on the D₆h molecules — is E(frozen) − E(fresh)
then a meaningful column, or should the fresh arm be defined as "fresh LNO spaces on the
*transported* LMOs" (freezing only the virtual half) so the difference isolates the virtual
freezing? Recommend a definition of both arms. (iv) Near-singularity: at what q does the
smallest singular value of S_oo fall below, say, 0.9 for a C–H stretch at q = 1 (Δr ≈ 0.1 Å)?

### C. The R1 temperature floor and the sources

(i) The floor u_T ≥ χ_max·(T_source − 296 K) + 1 cm⁻¹ with χ_max = 0.03 cm⁻¹ K⁻¹: is a linear
model from room temperature defensible for a molecule whose low-frequency modes are already
populated at 296 K, and is 0.03 the right upper bound for the 6.2/7.7 µm families (item 52's
snippet says ≈ −0.02 for a C–C stretch)? (ii) **Search for a room-temperature gas-phase
naphthalene IR spectrum outside the WebBook** — the PNNL/NWIR quantitative database (vapour-phase
spectra at 5, 25, 50 °C for many volatile organics), the NIST Quantitative IR series, or a
published cell spectrum. If one exists with stated temperature and resolution, R1 may be
unconditional after all and the plan should name the source; if none, say so. Do the same for
pyrene if you can. (iii) Items 52 (Joblin 1995) and 53 (Pirali 2009): open what you can (ADS
blocked the author); state the measured shift rates per family if the abstract or a citing paper
gives them, at the grade you can support. Is Pirali 2009 a *high-resolution* study of a jet or a
hot cell, and does it give a room-temperature band list usable as a scoreboard entry?

### D. The fragment licence after Round 9

(i) "One comparison at one shell" at coronene: for the C–H and CH-oop families, is a capped
central benzene at coronene's interior geometry a plausible reproducer of coronene's interior
Δ₂ within τ₇ ≈ 5 cm⁻¹ — or is the licence, for the C–C families, only ever earnable through
(b′) and hence through B3? Say which outcome you expect and why. (ii) "Pending (b′)": can any R6
work proceed under a pending licence? Is there a route to a two-shell test without B3
(circumcoronene at cc-pVDZ on the laptop; a smaller two-shell molecule such as
dibenzo[bc,ef]coronene)? Recommend one if it exists. (iii) Part (c) at R6, ≈ 360 fragment
energies at two shells: is the 168 h classification realistic or is (c) simply B3?

### E. ρ\*_common and the size sentence

ρ\*_common = max(ρ\*(R_n), ρ\*(R_{n+1})). Both rungs reached it; but K_off at ρ\*_common is read
from a curve whose hold-out set differs per rung (fraction f_h of different decks). Is the
comparison then apples to apples, and would reading at a common *held-out χ² per point* (c²)
be better than a common ρ? Say whether the size sentence, so defined, can still be gamed by the
choice of deck.

### F. The pooled σ

One σ per arm pooled over four modes (ν = 16). The four modes have different Cartesian
amplitudes at q_s = 1 (a C–H stretch moves one atom ≈ 0.1 Å; a ring breathing mode moves twelve
atoms less); if frozen-space error grows with Cartesian displacement, the four σ's are not draws
from one distribution and pooling under-reads the worst mode. Is a per-mode line with ν = 4 or
a pooled line with ν = 16 the lesser evil, and should the pilot note carry both with a stated
rule (e.g. pooled decides, per-mode ≤ 2× pooled required)?

### G. 36 gradients per milestone and the feasibility probe's gradient

(i) M4 (pyrene) and M5 (coronene) at 36 frozen-space LNO-CCSD(T) gradients each: with the side
project's own memory sizing, are these B3 by construction, and does that move M4/M5's calendar
beyond the 12-week kill window in practice? (ii) The feasibility probe's one canonical CCSD(T)
gradient at benzene/cc-pVTZ: is PySCF's `ccsd_t` gradient in-core only, and does it fit 31.3 GB
(estimate the largest intermediate)? If it does not, the probe should say so now.

## Also worth your attention

- Whether the symmetrised response changes what the noise-injected dry run measures (it must
  add noise to each energy, not to R_s, or σ(R_s) is wrong by √2 or √(3/2)).
- Whether any closure introduced a new pilot-note input that leaks a local-CC Δ₂ number (M1's
  raw energies are now sealed; the feasibility gradient is at equilibrium — Δ₁ only; confirm).
- The change table rows 28, 29, 31 as amended.

## Output format

```
Verdict: [green light / conditional / no green light — and for what scope]

## Part 1 — Round-9 closures
1–12. [closed / re-worded / open — deciding sentence]

## Blocking findings
N. [Title] — Where / What / Evidence / Why it matters / What would close it

## Non-blocking findings
…

## Attack-by-attack disposition (A–G)

## What would settle it
```

Use **Round 10, issues 1–N**.
