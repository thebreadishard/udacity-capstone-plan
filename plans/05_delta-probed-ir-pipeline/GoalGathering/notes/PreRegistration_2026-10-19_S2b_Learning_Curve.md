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
   Neutral is the deck in the molecule's `job.json` (charge 0, multiplicity 1): a pool 3 cation's manifest SMILES is its neutral
   parent's, and S2's runner has no charge input.
2. **Rigid only:** no rotatable bond (RDKit), no acyclic linker between ring systems, no CH₃, no H on N or O. The linker clause
   catches what RDKit's count misses next to a triple bond (diphenylacetylene's rings turn almost freely about the C≡C axis). All five of S2's NOISY molecules carried one of these (vinyl,
   methyl, N–H; the noise rule excluded them). The large targets are rigid C/H frameworks, so the rule matches the purpose.
3. **One molecule per new Murcko scaffold** (decision 52's breadth first): the smallest rigid member, ties by the sha1 of the id.
   S2's own scaffolds are not repeated. **23 new scaffolds** (9–26 atoms), giving 32 with S2's 9.
4. Script `probes/s2b_select.py` (tests/test_s2b_select.py), run 19 Oct 20:27; the list frozen in
   `probes/results_m1/s2b_training_set_2026-10-19/` (selection.json, s2b_ids.tsv). No label was read.

## Computation

As S2: GVPT2 at G (B3LYP/6-31G*, grid 75,302), full ± displacements, step 0.10, `dpir.qff` with its noise guard, runner
`probes/s2_batch.sh`, three molecules at a time, 5 threads each per CPX62, the SCF fallback of `probes/scf_converge.py` and pyscf's own
log. GFN2-xTB force fields for the same molecules on the laptop (`probes/xtb_anharmonic.sh`, under its memory cap) for amendment 4's
input. GVPT2 labels both sides with the same pyVPT2 solver (now upstream: PR #61 merged).

**Stop rule per molecule:** the first displaced Hessian takes longer than 1.5 × its predicted time, at least 300 s → that molecule stops
and is re-priced. The prediction is S2's measured per-Hessian fit, seconds ≈ exp(−4.92) · n^3.89 (median displaced Hessian of 19 S2
molecules); below S2's smallest timed molecule (12 atoms) the fit extrapolates, hence the floor. `probes/s2b_plan.py` writes each
server's list with the molecule's MAX_FIRST as a third column, which `probes/s2_batch.sh` hands to that molecule.
**Noise rule:** as S2, a NOISY molecule is excluded and named.

## Price (from S2's measured times)

S2's 18 timed molecules fit hours ≈ exp(−11.82) · n^5.04 (n = atoms; three at a time on one CPX62 at €0.208 per server-hour;
`probes/s2b_plan.py` refits it from the fetched logs and gets the same constants). The 23 molecules split longest first over the servers'
slots (`probes/results_m1/s2b_training_set_2026-10-19/plan/`): **two servers end after 233 h and 221 h, 453 server-hours ≈ €94; three
after 162, 147 and 158 h, 467 server-hours ≈ €97.** The fit is extrapolated from ≤ 20 to 26 atoms, and the stop rule guards that.
Allow ≈ €100–130 with the idle tail of each server.

**Wall time:** three CPX62 ≈ 162 h ≈ 6.8 days; two ≈ 233 h ≈ 9.7 days. The largest single molecules (26 atoms) are predicted at
≈ 99 h each at three a time. The laptop's xtb fields: ±1–3 h each, in parallel.

## Planning (before the stop date of 15 Nov)

| when | what |
|---|---|
| on the user's word | `s2b_select.py` written and run; the list frozen and committed; the user creates the servers (2–3 CPX62) |
| +1 day | `probes/bootstrap_s1_cpx62.sh` step 1 per server, then `DEST=/root/dpir_s2b IDS=<plan>/s2b_ids_<k>of<N>.tsv probes/deploy_s2.sh`
  (water smoke against the committed reference); one run spec per server through runspec |
| +6.5–10 days | molecules done; full fetch per server (sha256), the user deletes the servers |
| parallel, laptop | xtb force fields of the new molecules |
| +1–2 days | labels and the read; outcome appended here |

From a start on 21 Oct the read lands about 29 Oct – 2 Nov, two weeks before the stop date.

## Read (fixed now)

GVPT2 labels, scope 'no-large-amplitude' (amendment 3) as the main read, 'all' also reported; S2's and S2b's molecules read together
(`probes/s2b_read.py --sets`). Models: route (b) and (c), the search's configurations (ridge, kernel ridge, network on F1–F3, nested
leave-one-scaffold-out as amendment 2 §3), and amendment 4's x0/x1/x2 with Δ_xtb. **The learning curve** over k ∈ {4, 6, 8, 12, 16, 24}
and 'all' (every other usable scaffold: 31 if none is lost), 20 random subsets each with the same subsets for every model (amendment 1's
rules), for four models — (c), (b), x1 and x2* (kernel ridge on FX at the configuration the nested x2 read chose most often for the
family). The network is in the nested read only (a curve of nested fits is out of reach on the laptop). **The best model per family** is
the curve model with the lowest rms at 'all'.

**Lines.** Line 2 per family: ≤ 3.0 cm⁻¹ at the full set by any of the reads (x0; (c), (b), x1 at 'all'; x2 and the search nested) →
licensed, to be confirmed on tetracene in S3 (any of six reads is lenient; S3 is the check). **Still learning:** the best curve model's
rms at 'all' below its rms at k = 16 by more than twice that row's SE (with fewer than 17 training scaffolds, the largest k at most half of
them, named) → the curve is extrapolated (a + b·k^(−c)) to the scaffolds needed; a fitted asymptote at or above the line reads as flat. If that number is affordable, it sizes S2c
(after the stop date: the laptop or the PC). **Flat at 16 → 32 with the line missed:** learning from small molecules at this feature set does
not reach the line. Route A for the large targets is then the registered next step.

**Predictions (before any number).** Ring-ip reaches 3.0 with Δ_xtb between 24 and 32 scaffolds (one in two). CH-oop stays above 4.5
(two in three). 'other' is still learning at 32 (one in two).

## Draft revisions (19 Oct 2026, 20:2x–20:4x — before any S2b molecule was computed and before any S2b label existed)

Making S2b launch-ready (the user, 20:1x: 'Ja, begin met 1-3') turned up four things, each changed above:
1. **Cations slipped through 'neutral'.** The first selector run took phenanthrene⁺ and fluoranthene⁺ (P3c_541c53d1a5, P3c_428228e5a5):
   pool 3's cations carry their neutral parent's SMILES in the manifest, and S2's runner has no charge input, so it would have computed a
   cation geometry as a neutral closed shell. Neutral is now read from `job.json`'s deck; the neutral parents take those scaffolds. S2's own
   20 molecules were checked: all charge 0, multiplicity 1.
2. **Diphenylacetylene passed 'rigid'.** RDKit counts no rotatable bond next to a triple bond; its rings turn almost freely, the
   large-amplitude motion the rule exists to keep out. The linker clause removes it, and its scaffold has no other rigid member: 24 → 23.
3. **The stop rule per molecule** had no carrier in `s2_batch.sh` (one MAX_FIRST for the batch); now a third list column, with a 300 s floor.
4. **`probes/deploy_s2.sh` was stale:** it did not ship `library_log.py` and `scf_converge.py`, which the runner imports since 19 Oct, and its
   smoke compared with a folder only s1 has. Fixed (DEST and IDS settable, a fresh smoke folder, a committed water reference).
The read section now states what `probes/s2b_read.py` does (tests/test_s2b_read.py: the verdict rules on crafted curves, refused inputs, and
the whole read on exact-slope and pure-noise synthetic molecules). The k list ends at 24 because 32 scaffolds leave at most 31 to train on.
