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

## Registration 2 — the stepping stone: MP2 against ωB97X

**The question.** The network pretrains on the correction B3LYP → stepping stone; the anchors then tune α and the head (T3). The better stepping
stone is the one after which the anchors have *less* to do — read as T3's 'network as is' and 'head tuned' numbers on the four CC anchors. ωB97X is the
current stone (one DFT functional against another: cheap, smooth, but a DFT-to-DFT correction may carry little of what CC adds); MP2 is the
candidate (a correlated method whose basis step tracked CC's to 89–97 %, but known to over-soften some out-of-plane PAH modes).

**Step 0 — the price (first, five molecules).** MP2 has no analytic Hessian in pyscf: the stone's Hessians would be finite differences of analytic MP2
gradients (6N gradients, or 6 × representative atoms with symmetry), each gradient 40–850 s for benzene at cc-pVDZ/TZ on 4 threads. On five pool
molecules of 12–26 atoms at the corpus basis (6-31G*) the cost per molecule is measured; above 2 h per molecule on 8 threads the stone is priced out for
the whole pool and tried on the 46 parents only.

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
