# Pre-registration S2b — the anharmonic shift's learning curve (DRAFT, 19 Oct 2026)

**Status: DRAFT — new spending, so it waits for the user's word** (servers, euros). Written before any S2b molecule is selected by script
or computed. The costing below read only sizes and SMILES of candidate scaffolds, never a label.

## Why

S2 (14 usable molecules, 9 Murcko scaffolds) and its amendments 2–4 reached line 2 (≤ 3.0 cm⁻¹ per family) in no family. Best: ring-ip
3.60 with GFN2-xTB as input. The curves run over 4, 6 and 8 training scaffolds, a factor two at the very start, and on that span 'flat'
says little (memory 'Scientific judgement': no verdict on tiny data — scale along a curve). The flexible models, kernel ridge and the
small network, are variance-limited at this size and cannot be judged at all. S2b asks the question S2 could not: **does the error of the
learned anharmonic shift keep falling when the number of scaffolds grows four-fold, and does it reach 3.0 cm⁻¹ per family?** If it does,
the pipeline's third component (band positions) needs no scale factor, which is the project's goal (the user, 19 Oct: replacing PAHdb's
scale factor is the point). If it does not, route A, computing the anharmonic step for the large targets, is what is left.

## Training set (rule)

1. **Universe:** corpus manifest rows done, ≤ 28 atoms, neutral, elements C, N, O besides H, not in hold-out (b), not already in S2.
2. **Rigid only:** no rotatable bond (RDKit), no CH₃, no H on N or O. All five of S2's NOISY molecules carried one of these (vinyl,
   methyl, N–H; the noise rule excluded them). The large targets are rigid C/H frameworks, so the rule matches the purpose.
3. **One molecule per new Murcko scaffold** (decision 52's breadth first): the smallest rigid member, ties by the sha1 of the id.
   S2's own scaffolds are not repeated. Counted 19 Oct: **24 new scaffolds** (sizes 9–26 atoms), giving 33 with S2's 9.
4. Script `probes/s2b_select.py` (to write), output `probes/results_m1/s2b_training_set_<date>/selection.json`; the rule above fixed now.

## Computation

As S2: GVPT2 at G (B3LYP/6-31G*, grid 75,302), full ± displacements, step 0.10, `dpir.qff` with its noise guard, runner
`probes/s2_batch.sh`, three molecules at a time, 5 threads each per CPX62, the SCF fallback of `probes/scf_converge.py` and pyscf's own
log. GFN2-xTB force fields for the same molecules on the laptop (`probes/xtb_anharmonic.sh`, under its memory cap) for amendment 4's
input. GVPT2 labels both sides with the same pyVPT2 solver (now upstream: PR #61 merged).

**Stop rule per molecule:** the first displaced Hessian takes longer than 1.5 × its predicted time → that molecule stops and is re-priced.
**Noise rule:** as S2, a NOISY molecule is excluded and named.

## Price (from S2's measured times)

S2's 18 timed molecules fit hours ≈ exp(−11.82) · n^5.04 (n = atoms; three at a time on one CPX62 at €0.208 per server-hour). For the
24 new scaffolds, smallest first: 8 → 188 slot-h (€13), 16 → 712 (€49), all 24 → **1,401 slot-hours = 467 server-hours ≈ €97**. The
fit is extrapolated from ≤ 20 to 26 atoms, and the stop rule guards that. Allow ≈ €100–130 with the idle tail of each server.

**Wall time:** 1,401 slot-h over 9 slots (three CPX62) ≈ 156 h ≈ 6.5 days; over 6 slots (two) ≈ 10 days. The largest single molecule
(26 atoms) is predicted at ≈ 40 h. The laptop's xtb fields: ±1–3 h each, in parallel.

## Planning (before the stop date of 15 Nov)

| when | what |
|---|---|
| on the user's word | `s2b_select.py` written and run; the list frozen and committed; the user creates the servers (2–3 CPX62) |
| +1 day | `probes/deploy_s2.sh` per server with its water smoke; the list split by predicted cost; launch through runspec |
| +6.5–10 days | molecules done; full fetch per server (sha256), the user deletes the servers |
| parallel, laptop | xtb force fields of the new molecules |
| +1–2 days | labels and the read; outcome appended here |

From a start on 21 Oct the read lands about 29 Oct – 2 Nov, two weeks before the stop date.

## Read (fixed now)

GVPT2 labels, scope 'no-large-amplitude' (amendment 3) as the main read, 'all' also reported. Models: route (b) and (c), the search's
configurations (ridge, kernel ridge, network on F1–F3), and amendment 4's x1/x2 with Δ_xtb. Nested leave-one-scaffold-out as amendment 2
§3. **The learning curve** over k ∈ {4, 6, 8, 12, 16, 24, 32} training scaffolds, 20 random subsets each (amendment 1's rules), for the
best model per family.

**Lines.** Line 2 per family: ≤ 3.0 cm⁻¹ at the full set → licensed. **Still learning:** the rms at 'all' below the rms at k = 16 by more
than twice the combined SE → the curve is extrapolated (a + b·k^(−c)) to the scaffolds needed. If that number is affordable, it sizes S2c
(after the stop date: the laptop or the PC). **Flat at 16 → 32 with the line missed:** learning from small molecules at this feature set does
not reach the line. Route A for the large targets is then the registered next step.

**Predictions (before any number).** Ring-ip reaches 3.0 with Δ_xtb between 24 and 32 scaffolds (one in two). CH-oop stays above 4.5
(two in three). 'other' is still learning at 32 (one in two).
