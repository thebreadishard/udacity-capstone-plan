# Pre-registration E8 — is the coupled-cluster correction as local as the proxy? (written 23 September 2026, 14:3x, before any CC gradient of the deck ran; the user: "Zal ik er een bij doen zodat je E8 kan doen?" → CPX62 `ubuntu-32gb-hel1-16`)

## What we want to know

E7 (same day) showed on the DFT–DFT proxy (ΔH = H(ωB97X) − H(B3LYP), 224 molecules) that the correction of the force field is local: projected onto the
primitive internals, the diagonal carries almost nothing of the couplings, pairs sharing an atom about 40 % of ΔH, and the bond–bond pairs inside a ring
bring the explained part to three quarters — and that a network asked for *that* object learns the couplings from 175 molecules (ring coupling ratio
0.43 / 0.47, corrected frequencies 4.7 / 5.1 cm⁻¹). The pipeline's real correction is coupled cluster minus DFT. Whether it lives in the same pattern
decides whether the learned layer transfers with a few dozen CC-labelled molecules (affordable) or needs something else. Chemistry says yes: the
correlation correction to a conjugated system acts on bond stiffness and on the interaction constants between ring bonds, the same place. It has not been
measured; the project holds two real CC points, none of them a full Hessian.

## Measurement

Molecule: benzene at the corpus B3LYP/6-31G\* geometry (D6h to 10⁻⁴ Å; the geometry every corpus Hessian uses). Level: CCSD(T)/cc-pVDZ, frozen core,
pyscf 2.14 (RHF conv 10⁻¹¹, CCSD conv 10⁻⁹). **Hessian by central finite differences of analytic CCSD(T) gradients**, all 36 Cartesian coordinates,
step 0.005 bohr (72 gradients + the reference; every gradient checkpointed to disk, the run resumable). Reference DFT Hessians at the *same* basis and
geometry: B3LYP/cc-pVDZ and ωB97X/cc-pVDZ, pyscf analytic, grid 99/590. ΔH_CC = H_CCSD(T) − H_B3LYP; ΔH_proxy = H_ωB97X − H_B3LYP (both cc-pVDZ, so the
comparison is like for like and separate from the 6-31G\* corpus).

The FD Hessian is itself a finite-difference object, so it gets the two-route treatment before it is read: (i) its degenerate pairs must be degenerate
(D6h): a split above 3 cm⁻¹ on any e-pair fails the Hessian and the step is halved; (ii) translations must be a null space to 1 cm⁻¹ after projection;
(iii) the reference CCSD(T) energy and gradient are compared with the R0 deck's canonical numbers where the basis allows.

Read-outs, exactly as E7 post-hoc (vii)–(ix): the minimum-norm internal ΔF = B⁺ᵀ ΔH B⁺ in geomeTRIC's primitives, zeroed outside the pattern, back to
Cartesian; for each pattern the ΔH residual ratio and the ring coupling ratio (K read in the B3LYP/cc-pVDZ mode basis); plus the corrected-frequency
RMS after diagonalisation. Patterns: (a) diagonal only; (b) + pairs sharing an atom; (c) + bond–bond pairs in the same ring. Same three numbers for the
proxy ΔH at the same basis, side by side. Exploratory (no criterion): the element-wise correlation of ΔF_CC and ΔF_proxy on pattern (c), and the ratio of
their norms — how much of the CC correction the DFT proxy already "knows".

## Predictions (fixed now)

- Pattern (c) explains **≥ 70 %** of ΔH_CC (residual ratio ≤ 0.30) and takes the ring coupling ratio to **≤ 0.45**; the diagonal alone explains ≤ 35 %
  and leaves the coupling ratio ≥ 0.9 — the same shape as the proxy (proxy on the corpus: 0.27 / 0.38 and 0.77 / 0.98).
- **Win:** residual ≤ 0.35 and coupling ratio ≤ 0.5 on pattern (c). The learned layer of E7 applies to the CC correction as it stands; the label plan for
  the naphthalene class counts CC Hessians in the tens, and E8 continues with naphthalene at the same level (≈ 4 days on the CPX62) to read transfer
  between cores.
- **Lose:** residual ≥ 0.55 on pattern (c). The CC correction is not local in the pairwise pattern; the representation question reopens for the real
  target before any label is bought (candidates: longer-range pairs, atom-pair Cartesian blocks with an equivariant model, or a different coordinate set).
- **Between:** 0.35–0.55: the pattern is extended (pairs two bonds apart; all pairs inside a ring) and the projection repeated; the extension that reaches
  0.35 sets the target of the CC-trained model.

## Cost and safety

CPX62 `ubuntu-32gb-hel1-16` (46.62.227.91), created by the user 23 September 14:2x; env `qc05` (pyscf 2.14, geomeTRIC 1.1.1). One CCSD(T)/cc-pVDZ gradient
of benzene: measured by the smoke test before the launch (expected 5–15 min at 16 threads); 73 gradients ≈ 6–18 h, ≈ €1–2. Nothing on the laptop; the
CCX53 keeps its own queue. Scripts `probes/e8_cc_hessian_fd.py` (gradients, checkpointed) and `probes/e8_cc_locality.py` (DFT references, projections,
report); results `probes/results_m1/e8/benzene_ccpvdz/`; outcome appended here.

## What this does not decide

The basis dependence of the CC correction (cc-pVDZ here; the anchor's TZ increments per family are M3's business); anharmonic terms; intensities; anything
about molecules with heteroatoms until naphthalene and one heteroaromatic follow.

**Added 15:2x — naphthalene pre-authorised.** The user: "Als E8 wint, mag naftaleen er op hetzelfde niveau meteen achteraan op hel1-16." The chain on hel1-16
reads benzene automatically against the win criterion above and, on a win, smoke-tests one naphthalene CCSD(T)/cc-pVDZ gradient (memory is the risk on 32 GB)
before the 108-gradient run; on "between" or "lose" it stops after the read-out. Naphthalene's read-out is the same table plus the transfer question: does the
pattern that carries benzene's ΔH_CC carry naphthalene's, and does the E7 model trained on the DFT proxy predict any of ΔH_CC (exploratory).

## Outcome — benzene, read 24 September 2026 02:19 UTC (04:19 local), recorded 04:2x

Run: 72 CCSD(T)/cc-pVDZ frozen-core gradients + reference on hel1-16, 663–692 s each, Hessian written 02:12 UTC; FD asymmetry max 2.7e-4 a.u.;
two-route checks passed (degenerate pairs 377.7/377.7, 605.6/605.6, 631.7/633.3 — the e2u pair split 1.7 cm⁻¹, under the 3 cm⁻¹ limit; six ~0 after
projection). Files: `probes/results_m1/e8_benzene_ccpvdz/` (`E8_locality_benzene.{json,md}`, `hessian_ccsd_t.npz`, `e8_fd.log`, `chain.log`).

| pattern | ΔH residual ratio CC / proxy | ring coupling ratio CC / proxy | corrected ω RMS CC / proxy (zero rule 38.0 / 22.4) |
|---|---|---|---|
| (a) diagonal | 0.54 / 0.78 | 1.08 / 0.95 | 19.2 / 11.5 |
| (b) + atom-sharing pairs | 0.27 / 0.58 | 0.93 / 0.67 | 8.4 / 7.3 |
| (c) + ring bond–bond pairs | **0.08** / 0.06 | **0.80** / 0.15 | 6.2 / 2.2 |

Exploratory: element-wise correlation of ΔF_CC and ΔF_proxy on pattern (c) 0.78; norm ratio CC/proxy 1.61. CC − B3LYP frequency shifts run from −88
(the 721 cm⁻¹ mode) to +61 cm⁻¹ (C–H stretches); RMS 38.

**Verdict by the pre-registered rule: between** — the residual criterion is met with room (0.08 against ≤ 0.35; the prediction said ≤ 0.30), the
coupling criterion is not (0.80 against ≤ 0.5). Strictly the case falls in none of the three bands, which were written on the residual alone; the
script's fallback "between" is the honest label and the pre-registered between-branch applies: *extend the pattern and repeat the projection; the
extension that reaches the win numbers sets the target of the CC-trained model.* The chain stopped as armed; naphthalene did not start.

**Reading (not a criterion).** The CC correction is *more* local than the proxy in norm — 92 % of it lives in the diagonal + atom-sharing + ring
bond–bond pattern — and the corrected frequencies recover 84 % of the shift (6.2 against 38 cm⁻¹). What the masked projection misses is the small
off-diagonal part inside the ring-in-plane family: for the CC correction those couplings are a smaller fraction of a larger matrix, so an 8 % residual
is of their size. Two things can be responsible and the extension separates them: (i) the pattern is too small for the CC correction (pairs two bonds
apart, angle–angle and bond–angle pairs inside a ring carry it), or (ii) the *masked minimum-norm projection* is the limit, not the pattern — in 54
redundant internals for 30 modes the minimum-norm ΔF is one of many, and masking it is not the best the pattern can do. E7's ceilings had both
read-outs (mask and least-squares fit); E8's script had only the mask.

## Between-branch, specified before it runs (04:2x)

Script `probes/e8_between_extension.py`, on hel1-16, minutes, no new gradients (the saved CC Hessian; the DFT references recomputed at cc-pVDZ, grid
99/590). For CC − B3LYP and the proxy side by side, the same three read-outs as above for:

- (c) as before (mask) — the control, must reproduce 0.08 / 0.80;
- (c-fit) the least-squares ΔF restricted to pattern (c) that best reproduces ΔH in Cartesian norm (E7 ceilings' "fit") — separates (i) from (ii);
- (d) pattern (c) + pairs of primitives two bonds apart (their atom sets connected by one bond) — mask and fit;
- (e) all pairs of primitives whose atoms lie inside the same ring (bonds, angles, dihedrals of one ring) — mask and fit;
- (f) all pairs (no pattern) — the sanity floor (residual 0, coupling ratio 0).

**Decision rule (fixed now):** the smallest pattern whose *fit* gives residual ≤ 0.35 **and** ring coupling ratio ≤ 0.5 on CC − B3LYP is the target of
the CC-trained pairwise model; if only (f) reaches it, the CC correction's couplings are not pairwise-local in these primitives and the representation
question reopens for the real target (E8 pre-registration's lose-branch candidates), before any label is bought. Naphthalene stays pre-authorised only
if a pattern ≤ (e) reaches the numbers — then it runs at the same level to read transfer; otherwise the user decides.

## Between-branch outcome — 24 September 2026 02:30 UTC, recorded 04:3x

`probes/results_m1/e8_benzene_ccpvdz/E8_between_benzene.{json,md}` (358 s on hel1-16; 54 primitives, 12 bonds; the DFT references recomputed identically —
the (c)-mask control reproduces 0.08 / 0.80 and 0.06 / 0.15 exactly).

| pattern (pairs) | CC − B3LYP mask: residual / coupling ratio / corrected ω RMS | proxy mask | CC fit | proxy fit |
|---|---|---|---|---|
| (c) diagonal + atom-sharing + ring bond–bond (978) | 0.08 / 0.80 / 6.2 | 0.06 / 0.15 / 2.2 | 0.00 / 0.01 / 0.13 | 0.00 / 0.00 / 0.07 |
| (d) (c) + pairs two bonds apart (1,365) | **0.02 / 0.34 / 4.1** | 0.04 / 0.17 / 1.9 | 0.00 / 0.00 / 0.06 | 0.00 / 0.00 / 0.03 |
| (e) all pairs inside a ring (984) | 0.08 / 0.80 / 6.2 (= (c) for benzene) | 0.06 / 0.15 / 2.2 | 0.00 / 0.01 / 0.13 | 0.00 / 0.00 / 0.07 |
| (f) all pairs (1,485) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

**The decision rule as written gives pattern (c) — and is vacuous for one molecule.** A 36 × 36 symmetric ΔH has 666 independent entries; pattern (c)
already has 978 free pair entries, so an exact least-squares fit is guaranteed for any pattern from (c) up, for any ΔH whatever. The fit ceiling
separates "pattern too small" from "projection is the limit" only across molecules with a shared model (as E7's ceilings did on the corpus); on a single
molecule it separates nothing. Recorded as a lesson: *a parameter count must be compared with the data count before a fit ceiling is read* — the rule
should have said so. The informative read-outs are therefore the masks:

- the masked minimum-norm projection onto (c) leaves the ring couplings at 0.80 for the CC correction (0.15 for the proxy);
- adding the pairs two bonds apart — pattern (d) — brings the CC correction to residual 0.02 and ring coupling ratio **0.34**, inside the win numbers
  (≤ 0.35 and ≤ 0.5), with corrected frequencies at 4.1 cm⁻¹ against 38 for no correction; the proxy barely moves (0.15 → 0.17), i.e. the proxy's
  couplings are nearest-neighbour and the CC correction's reach one bond further.

**Target of the CC-trained pairwise model, provisional: pattern (d)** — diagonal, atom-sharing pairs, ring bond–bond pairs, and pairs of primitives two
bonds apart. Provisional because it rests on one molecule and on the minimum-norm convention; it is confirmed or corrected by the same read-out on
naphthalene (two rings, 90 primitives; the pattern-vs-data count is then 4,005 entries against ≈ 2,700 pair entries in (d) — still not a fit ceiling,
but a second molecule for the masks and the transfer question). For E7's model this means one more pair class in the feature set (ring-path
distance 2 already exists as a feature; the pattern mask is what changes).

**Naphthalene.** The user's pre-authorisation was for a win; this is a between whose masked (d) reaches the win numbers. Started on hel1-16 at
04:3x: the smoke step only (one CCSD(T)/cc-pVDZ reference gradient of naphthalene — memory and time on 32 GB). The 108-gradient run (≈ 4 days at the
benzene rate scaled, ≈ €10) waits for the user's word in the morning; it would finish around 28 September.

## Symmetry-reduced finite differences — built and validated before naphthalene runs (06:4x)

The naphthalene smoke gradient showed the cost honestly: one CCSD(T)/cc-pVDZ gradient of naphthalene takes hours on the CPX62, not minutes, so 108
gradients would take weeks, not the "≈ 4 days" written above. The user authorised the run ("Doe maar") and asked whether to add a server; the answer
is first a cheaper lever. `probes/e8_symmetry.py`: a Hessian obeys H[P(i),P(k)] = R H[i,k] Rᵀ for every point-group operation, so the block rows of one
atom per orbit determine the whole matrix. The group is detected from the geometry alone (Kabsch maps of atom triples, refit over all atoms, closed
under products; improper partners through the molecular plane). Displace only the representatives (3 directions, ±), copy their rows onto the
equivalent atoms, average rows reached by several operations (their spread is a noise measure).

Validation (`probes/results_m1/e8_benzene_ccpvdz/symmetry_validation_2026-09-24.log`):
- benzene, the 72 CCSD(T) gradients already in hand: D6h found (24 operations, two orbits); 12 gradients reconstruct the full matrix to 2.5e-5 a.u. —
  below the full run's own FD asymmetry (2.7e-4) — and every frequency to 0.03 cm⁻¹; the e2u split is 1.66 against 1.67.
- naphthalene, the corpus B3LYP and ωB97X Hessians: D2h found (8 operations, five orbits → 30 gradients instead of 108); the reconstruction from five
  block rows differs from the group-averaged full matrix by 9e-5 / 7e-5 a.u., i.e. by the corpus Hessians' own asymmetry (3.4e-4 / 3.9e-4, deck v1's
  grid noise again); frequency differences 2.8 / 0.17 cm⁻¹ sit on the softest modes and are that noise, not the reconstruction.

`e8_cc_hessian_fd.py --symmetry` uses it; the npz records `symmetry_reduced` and the row spread. Plan: an end-to-end smoke of the new code path on
benzene at cc-pVDZ on the CCX53 when its second-route lanes finish (12 gradients, ≈ 1 h; must match the 72-gradient Hessian), then naphthalene there
(30 gradients at 32 threads); hel1-16 finishes the smoke gradient for the time-per-gradient number first.

**Added 09:0x — the naphthalene smoke gradient on the CPX62 hit its 4-hour limit.** One CCSD(T)/cc-pVDZ (frozen-core) gradient of naphthalene did
not finish in 4 h at 16 threads on hel1-16 (load stayed at 3–4: pyscf's CCSD(T) gradient is largely serial), against 11 min for benzene. So the
CPX62 cannot help with naphthalene; the 30 symmetry-reduced gradients run on the CCX53 alone (32 dedicated cores; per-gradient time to be read
from the benzene smoke there). hel1-16's E8 role is over; the reference gradient will be recomputed on the CCX53 as part of the run.
