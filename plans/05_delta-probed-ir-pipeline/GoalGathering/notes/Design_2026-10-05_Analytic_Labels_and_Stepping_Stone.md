# Design and two pre-registrations, 5 October 2026, 08:0x — the corpus's labels made analytic (chain 35), and MP2 against ωB97X as the stepping stone (TASKS 25; the user: "Eens … De server: ja")

*Registered before anything runs. Two findings of 4–5 October set this up: (1) the finite-difference labels of the corpus carry a noise floor of 4.8 cm⁻¹
on the low modes (analytic against FD over the ten hold-out (a) molecules), the network trains on them, and on clean evaluation labels 'other' still
stands at 3.35 cm⁻¹ — the training labels are the next registered lever; (2) MP2 reproduces the CCSD(T) basis step on benzene's three measured
coordinates to 89–97 % where B3LYP reproduces none of it, which asks whether MP2 would be a better stepping stone than ωB97X. The user's question of
5 Oct 07:3x sits behind both: the stepping stone is the level the network pretrains on; the truth it is calibrated to is the anchors
(`notes/Note_2026-10-05_Layers_of_Truth.md`).*

## Registration 1 — analytic labels for the corpus, and chain 35

**What changes.** The corpus's two DFT Hessians per molecule (B3LYP, the input; ωB97X, the target; both 6-31G*, Cartesian d, grid 99,590) are made
analytically with pyscf (`corpus/analytic_hessians.py`, the second route of 23 Sep, run as the first route from now on) instead of by psi4 finite
differences of gradients. Scope: (a) the 811 done rows of layers A, A2 and B that have FD labels only (847 done, 36 already analytic) — on a rented
CCX53, four lanes of 8 threads; (b) every new row from pool 3 on is analytic from the start; (c) the 200 of the next pool finish as they run (psi4) and
are re-labelled afterwards. The FD files stay beside the analytic ones (nothing is deleted; the per-molecule analytic-vs-FD difference is recorded in
`analytic_check.json`, the corpus's noise ledger).

**Price, measured.** Step 3's timings at 12 shared laptop threads: 2,000–6,600 s per functional for molecules of 20–26 atoms; the pool's mean is 20.9
atoms (median 23, max 30). Per molecule both functionals on a dedicated 8-thread lane: ≈ 1.0–1.5 h → 811 molecules on four lanes ≈ 200–300 lane-hours
/ 4 ≈ **8–10 days**, at €0.855/h ≈ **€165–205**. A first-day read of the lane throughput (molecules per hour) corrects this estimate on record before
the second day; if the throughput is below 0.8 molecules per lane-hour, a second CCX53 is proposed, not assumed.

**Gate before the lanes start.** The server's pyscf reproduces one laptop analytic Hessian (benzene, `A_8448043181/hessian_b3lyp_analytic.npz`) to
max |ΔH| ≤ 1e-6 a.u. — same code, same grid, same answer; the lanes do not start without that number in the launch log.

**Chain 35 (the read).** Chain 34's recipe unchanged (family-balanced K-diagonal term, 750, three seeds, early stopping as before), trained and
evaluated with the analytic labels substituted everywhere they exist (`--use-analytic` on load; the loader records the count). Read against chain 34
on analytic evaluation labels (the 5 Oct 06:5x table: ring-ip 1.82, CH-stretch 1.25, CH-oop 2.36, other 3.35, other-low 3.21, ratio 0.192).

**Predictions.** The training noise of the low modes is the cause of most of what is left: other-low 3.21 → 2.0–2.5, 'other' 3.35 → 2.4–2.9; ring-ip
and CH-stretch move by less than their seed ranges; CH-oop 2.36 → 2.0–2.4; hold-out (b) 'other' 6.03 → 5.3–5.8 (its own labels become analytic too,
the scaffold gap stays). **Lines.** *'other' ≤ 3 on (a) with ring-ip ≤ 3, CH-oop ≤ 3 and ratio ≤ 0.25* → T1 met in every family at the proxy level;
chain 35 is carried (decision 57; version 1.2). *'other' falls by ≥ 0.3 but stays > 3* → labels were part of it; the low-mode input (TASKS 23) is
designed on the analytic labels. *'other' falls by < 0.3* → the labels were not it; the input design is the next lever and the FD labels were good
enough for the low modes.

**Dated amendment, 8 October 07:2x — smallest first, and a half read that measures without judging (the user, 07:0x: "Ja, doe maar" to the
smallest-first order; "Voorlopig wel meten, maar niet afkeuren").** The first-day read put the lanes at 0.41–0.53 molecules per lane-hour,
below the 0.8 line (16–21 days, €330–425); a second server is out. Since 07:1x the four lanes run smallest-first lists
(`probes/labels_lane_switch.sh`, `small_ids_<n>.txt`; the molecule each lane had in progress finished first, no lane ran two at once). The
smallest half (≤ 22 atoms, 405 molecules) is 22–28 % of the cost, ≈ 4–6 days. **Where the low modes are** (`probes/low_modes_by_size.py`,
`out/low_modes_by_size_2026-10-08.md`): the larger half holds 59 % of the labels list's other-low modes (20.3 per molecule against 14.0), and
on the molecules with both routes its FD-against-analytic other-low error is 2.16 cm⁻¹ against 1.28 (8 and 7 molecules; benzene's corpus
row, known noise since 29 Sep, left out) — ≈ 80 % of the low-mode label noise (count × error²) is in the larger half. **Hence:** *the half
read* (chain 35's recipe on the pool with the analytic labels that exist then, against the same pool and recipe with FD labels) is measured and
reported per family, other-low included, and **no line above applies to it — no rejection, no promotion**. One guard: a family other than
'other' worse than its seed range at the half read means the pipeline is checked (the substitution, the loader count) before the lanes go on.
*The full read* (every molecule of the list analytic) is the one the lines above apply to. Open, decided at the full read: the 200 merged on
8 Oct (≈ 160 new pool molecules) are not in the labels list and stay FD unless they get labels of their own.

## Registration 2 — the stepping stone: MP2 against ωB97X

**The question.** The network pretrains on the correction B3LYP → stepping stone; the anchors then tune α and the head (T3). The better stepping
stone is the one after which the anchors have *less* to do — read as T3's 'network as is' and 'head tuned' numbers on the four CC anchors. ωB97X is the
current stone (one DFT functional against another: cheap, smooth, but a DFT-to-DFT correction may carry little of what CC adds); MP2 is the
candidate (a correlated method whose basis step tracked CC's to 89–97 %, but known to over-soften some out-of-plane PAH modes).

**Step 0 — the price (first, five molecules).** MP2 has no analytic Hessian in pyscf: the stone's Hessians would be finite differences of analytic MP2
gradients (6N gradients, or 6 × representative atoms with symmetry), each gradient 40–850 s for benzene at cc-pVDZ/TZ on 4 threads. On five pool
molecules of 12–26 atoms at the corpus basis (6-31G*) the cost per molecule is measured; above 2 h per molecule on 8 threads the stone is priced out for
the whole pool and tried on the 46 parents only.

**Step 0 outcome (6 Oct 2026, 08:3x; `probes/results_m1/mp2_step0_2026-10-05.log`, `probes/mp2_price_step0_1005.sh`, `probes/mp2_price_step0b_1005.sh`).** MP2/6-31G* (cart) gradients at 2 threads, each run beside an 8-thread anchor job, so the per-thread price is an upper bound:

| molecule | atoms | unique displacements | measured | whole molecule at 2 threads | ≈ at 8 threads (÷ 3) |
|---|---|---|---|---|---|
| benzene | 12 | 12 | 277 s | 277 s | 0.03 h |
| naphthalene | 18 | 30 | 3,502 s | 3,502 s | 0.3 h |
| biphenyl | 22 | 33 | 18,149 s | 18,149 s | 1.7 h |
| fluoranthene | 26 | 42 | 4 displacements, 12,756 s | ≈ 133,900 s | ≈ 12 h |
| fluoranthene+vinyl | 28 | 90 | 4 displacements, 8,743 s | ≈ 196,700 s | ≈ 18 h |

The line (2 h per molecule at 8 threads) holds up to biphenyl and fails from 26 atoms on; 474 of the 847 computed pool molecules have 21–26 atoms and 49 more; the vinyl variant shows that low symmetry (90 displacements) costs more than size. **Verdict as registered: the stone is priced out for the whole pool; step 1 runs on the 46 parents only.** Their sum at the measured prices is ≈ 110 h of one 8-thread lane (the three-ring and fluoranthene parents carry most of it): five days on the laptop, or ≈ 1.5 days on the labels CCX53's four lanes after the labels (≈ €30). Which, and when, is the user's call (step 1 is 'on the user's word if it needs a server').

**Decision (the user, 6 Oct 2026, 09:0x): the DFT stepping stone stays.** Step 1 is parked; MP2 on the 46 parents is re-opened only if the 'other' family does not move once the pool has analytic labels (chain 35). The stone's price, not its quality, decided: on benzene MP2 followed the anchor's basis step better (test 1), but the pool cannot afford it.

**Step 1 — the read (after step 0, on the user's word if it needs a server).** The same 750-molecule recipe trained with MP2 targets (correction
B3LYP → MP2/6-31G*, same loss, same seeds), read on hold-out (a) against its own MP2 labels (learnability: ratio and families) and, the decisive
number, T3 on the four DZ anchors and on their composite level when test 2 has passed: *'network as is' ratio* and *'head tuned' per family* for the
ωB97X-trained and the MP2-trained network side by side.

**Predictions.** Learnability is similar (ratio 0.20–0.25 on (a)); 'network as is' on the anchors improves from ≈ 1.0 (ωB97X) to 0.5–0.8 (MP2) because
MP2's correction shares CC's basis-and-correlation character; 'head tuned' CH-stretch and ring-ip improve by ≥ 30 %, CH-oop does not (MP2's
out-of-plane weakness). **Lines.** *'network as is' ≤ 0.7 and 'head tuned' better in ≥ 3 of 4 families* → MP2 becomes the stepping stone for the next
pools and the analytic-label plan above is re-scoped (MP2 labels by FD for new rows; a Ladder amendment). *Better in 1–2 families* → a two-stone
design (ωB97X for out-of-plane, MP2 in plane) is registered, not assumed. *No improvement* → ωB97X stays; the anchors are the only lever on the CC
side, as now.

## Order and place

Registration 1 starts as soon as the user has created the CCX53 (bootstrap `probes/bootstrap_labels_ccx53.sh`, the gate, four lanes, a watcher with an
alarm file, a full fetch at the end). Registration 2's step 0 runs on the laptop on free lanes after the TZ anchor assembles (today evening) — five
molecules, hours; step 1 waits for step 0's price and the user's word. Chain 35 trains on the laptop when the fetch is complete (≈ 15 October).
