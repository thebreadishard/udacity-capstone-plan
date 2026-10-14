# S1-TZ — does the basis of the anharmonic part matter? Δ_anh at triple-ζ on three hydrocarbons, not on benzene alone (registered 14 Oct 2026, 18:3x, before any triple-ζ computation)

*TASKS 56 and 60. The user, 14 Oct, evening (after 17:5x): 'De registratie voor een triple-ζ Δ_anh-set voor benzeen mag je schrijven, maar blijf voorzichtig
met het gebruiken van benzeen als representant van wat dan ook. Het molecuul wijkt best wat af van zo ongeveer alle andere moleculen in onze
sets.' That caution shapes this design: benzene is computed because it alone has an external reference, but no decision is taken on it.*

## Why

S1 (outcome 14 Oct 00:1x) made G — B3LYP/6-31G*, grid 75/302 — the anharmonic level: G against R (same basis, grid 99/590) differs by 0.19 /
0.35 cm⁻¹ (rms / max Δ_anh). S1 tested the grid and a smaller basis, never a larger one. The benzene hybrid check (outcome 14 Oct 13:0x)
then found our Δ_anh(G) 7.16 cm⁻¹ rms from the semi-experimental ν_MCP − ω_CCSD(T)/spdf, with two modes carrying most of it: ν19 (e2u, C–H
out of plane: ours −4.5, semi-experimental −17, B3LYP/TZ2P −20, B97-1/TZ2P −23) and ν9 (b2u, Kekulé: ours −34.5, semi −17, TZ2P −28).
Against the paper's own B3LYP/TZ2P — the same functional at a larger basis — our 6-31G* shifts are less negative by ≈ 2–5 cm⁻¹ on most
modes (mean +2.4 without ν3 and ν19). That points at the basis, but it does not show it: the TZ2P column also differs from ours in program,
grid, step and geometry. This test changes only the basis.

## Why benzene alone would decide nothing

Benzene differs from the molecules the pipeline is for in exactly the respects that matter here:
- **Its C–H out-of-plane modes are of a kind no PAH has.** PAH C–H wags are classed by the number of adjacent hydrogens on a ring — solo,
  duo, trio, quartet — and the class sets their frequency and band strength (the 11–14 µm region). Benzene's six adjacent hydrogens form a
  class of their own. ν19, the mode that carries the hybrid check's miss, is one of benzene's sextet wags.
- **Its two outlier modes are benzene's own:** e2u and the b2u Kekulé mode exist as such only at D6h; every other molecule in our sets has
  lower symmetry, no degenerate pairs and no isolated Kekulé mode.
- **No ring fusion, no quaternary carbons, one scaffold.** The corpus and the mandate's targets (tetracene, coronene, peropyrene, ovalene,
  HBC) are fused.

So benzene is computed for one reason — it is the only molecule with a published semi-experimental Δ for every fundamental — and its read
against that reference is reported for benzene only. The decision on the anharmonic level rests on the two other molecules as much as on
benzene, and a result that holds for benzene but not for them decides for them.

## Molecules (fixed by rule now)

From the S2 training set (`probes/results_m1/s2_training_set_2026-10-14/selection.json`), whose G force fields exist or are being computed,
so the G side of every comparison is already paid for:
1. **Benzene** (A_8448043181; G from S1) — the reference molecule; sextet C–H.
2. **Naphthalene** (A_01f3186607; G from S2) — the smallest fused hydrocarbon, the corpus' core scaffold; quartet C–H.
3. **Acenaphthylene** (A_45187bb7c8; G from S2) — the smallest S2 hydrocarbon with trio and duo C–H, the classes of the mandate's large
   PAHs, and a five-membered ring; also an anchor of set three (its CCSD(T) Hessian is being computed on `anchors3`).

Hydrocarbons only: the mandate's targets are hydrocarbons, and adding a nitrogen axis would double the cost of a question that is about the
basis. Solo C–H is not covered by any S2 hydrocarbon (it first appears in tetracene); see the scale clause.

## Computation

**T = B3LYP/def2-TZVP, grid 75/302**: triple-ζ valence with polarisation (C [5s3p2d1f], H [3s1p]), pyscf's `def2-tzvp`. The grid is G's, so
T against G changes the basis and nothing else. Boese & Martin's TZ2P is the nearest published B3LYP route but has no f functions; def2-TZVP
is chosen as a standard triple-ζ basis that pyscf carries, not to reproduce TZ2P.

Per molecule, at its own T minimum: GVPT2 from full ± displacements along every mode (2M+1 analytic Hessians: 61, 97 and 109), step 0.10,
`python -m dpir.qff` with its noise guard — the computation of S1 and S2 at a different basis. No symmetry saving (the ± saving passed S1
but is a probe, not production). Runner: `probes/s2_batch.sh <list> <root> 3 5 T:def2-tzvp:75,302`, three molecules at a time, 5 threads
each, on `s1`; the list file is LF-only (14 Oct CRLF incident). Smoke: water at T through the same runner before the three.

**Grid gate at T (before the displacements):** at each molecule's T minimum, harmonic ω with grid 75/302 and with 99/590. If the largest
|Δω| over the modes with ω in 550–2,000 cm⁻¹ exceeds **1.0 cm⁻¹** — three times the 0.33 cm⁻¹ measured between G and R at 6-31G* (S1's benzene
reports) — that molecule's T set runs at 99/590 and is re-priced before it starts.

**Stop rule:** a molecule whose first displaced Hessian takes longer than 1.5 × the time the price below assigns to it stops ('STOPPED') and
is re-priced; the others go on. **Noise rule:** as S2 — a force field that trips the noise guard (quartic route disagreement > 10 cm⁻¹) is
named in the outcome and not read; it is re-run once at 99/590 before the read is closed, so a molecule is not lost to the guard.

## Quantity

Per molecule, per mode: **d = Δ_anh(T) − Δ_anh(G)**, Δ_anh = ν − ω with dpir.qff's symmetry-averaged ν (`nu_sym`), modes matched between T
and G by eigenvector overlap (`probes/s1_anharmonic_level.py`'s matching: Hungarian assignment on squared overlaps, the minimum overlap
reported), over the modes with ω in 550–2,000 cm⁻¹ (the shape score's window, as S1 and S2). Modes are grouped by the corpus families
(`e8_cc_locality.families`: CH-stretch, CH-oop, ring-ip, other). Reported per molecule: rms(d), max |d|, mean(d), and the same per family;
pooled over the three molecules per family, with each molecule's modes counted once.

## Lines and what each decides (fixed now)

The scale is S2's: 3.0 cm⁻¹, a third of the shape score's Gaussian FWHM at 1,000 cm⁻¹.

- **(a) G holds:** rms(d) ≤ 1.5 cm⁻¹ on **each** of the three molecules **and** pooled CH-oop rms(d) ≤ 1.5. → G stays the anharmonic level
  for S2's labels and S3's route A. If benzene's ν19 still misses the reference by ≈ 15 cm⁻¹ at T, the miss is not the basis; it is the
  reference, the functional or VPT2, and is recorded as such.
- **(b) the basis matters:** rms(d) > 3.0 on **any** of the three, **or** pooled CH-oop rms(d) > 3.0. → S3's route-A numbers are computed at T
  (re-priced at T from this run's measured times, on the user's word); S2's relative read — route (b) against route (c) at one level —
  stands, but its line 2 (a route licensed at ≤ 3.0 against GVPT2) is read against T labels, or against G labels corrected by the per-family
  mean d measured here, whichever the user prices first; the certificate's anharmonic step names the level it was licensed at.
- **(c) between:** neither (a) nor (b). → G stays the level, the per-family mean d and rms(d) from these three are carried as a stated
  systematic error of the anharmonic step, and S3 adds one T force field on tetracene (priced first) to see whether the per-family mean d
  transfers to a larger fused molecule before it is used as a correction.

Benzene does not decide alone: in every branch, if benzene's numbers would place the result in a different branch from naphthalene's and
acenaphthylene's taken together, the branch of the two fused molecules is the one that decides, and the difference is reported.

## Benzene's reference read (reported, for benzene only)

rms and max of Δ_anh(T) − Δ_semi over the hybrid check's 14 modes (same window, same Fermi exclusions, same matching —
`probes/hybrid_check_benzene.py` with T's report beside G's). Line, as the hybrid check's outcome asked: the spread of the published DFT
routes against this reference — **T within 6.89 cm⁻¹ rms** (B3LYP/TZ2P), with B97-1/TZ2P's 5.19 beside it. Read per mode on ν19 and ν9:
does T move them toward −17 and −17? No line on a single mode; this read informs, and no conclusion is drawn from it about any other
molecule.

## Scale clause (the 'still learning' rule's counterpart for a convergence test)

This is not a learned model, so there is no curve along training size; the scale question here is coverage. Three molecules and four C–H
adjacency classes (sextet, quartet, trio, duo) are what this test can speak for.
- A result in (a) is not a proof that solo C–H behaves alike. If the three molecules' CH-oop mean d differ from one another by more than
  1.5 cm⁻¹ — the basis effect depends on the adjacency class — the solo class is measured before S3's numbers are used: one T force field on
  the smallest corpus hydrocarbon with a solo C–H (priced, on the user's word). If they agree, solo is assumed to follow, and S3's tetracene
  read states that assumption.
- A result in (b) or (c) is not narrowed afterwards: no branch is replaced by 'benzene only' or 'two molecules only'. If a molecule cannot be
  computed (cost, noise guard twice, a failed gate), the read waits for it, re-priced, and the user decides — the decision is never taken on
  fewer than the three.

## Price and place

Measured G costs per displaced Hessian on `s1` (5 threads, three molecules in parallel; median interval between Hessian files): benzene 112 s
(S1), naphthalene 550 s, acenaphthylene 967 s (S2, read 14 Oct 18:3x). The T/G factor is not measured: **benzene's first T Hessian prices
the run**, as S1's first Hessian did — price = Σ (2M+1) × t_G × (t_T / t_G at benzene), stated in TASKS before naphthalene and acenaphthylene
start. The factor for the larger molecules may differ from benzene's (the grid's share of a Hessian falls as the basis grows); their own
first Hessians re-check it against the stop rule.

Place: `s1` after S2 ends (≈ 18 Oct), only if the user keeps the server for it — that is spending and the user's decision; or another
server, also on the user's word. Nothing runs before then.

## My prediction (before any number)

Branch (c) or (b), not (a). On naphthalene and acenaphthylene: mean d ≈ −2 to −3 cm⁻¹ (T more negative), rms(d) 2–4 cm⁻¹, from the TZ2P
comparison above. CH-oop: |d| smaller than benzene's ν19 — I expect benzene's sextet wag to overstate the effect, but I rate the
direction of that at no better than 60 %. Benzene: T moves ν19 by ≥ 8 cm⁻¹ toward the reference (the basis explains most of the gap);
benzene's rms against Δ_semi falls but stays above 3.0, inside the published routes' spread.

## Outcome

*(empty until all three T force fields are read)*
