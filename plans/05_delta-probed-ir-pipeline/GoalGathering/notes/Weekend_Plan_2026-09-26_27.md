# Weekend plan, 26–27 September 2026 (written 25 September 16:4x, the user leaving: "werk zelfstandig door richting het doel … de lange termijn kansen willen we naar 90+ procent")

**Standing instruction (the user, 25 Sep 16:4x):** work autonomously towards proving to the supervisor that the network learns the right things, and do
every task that raises the odds; the long-term line (a versioned ΔH network the field uses, ≈ 2030; 60 % on 25 Sep 07:0x) is to be driven towards 90 %+.
Contact stays open through remote control; a ping only when Helsinki needs the user's hands.

## Fixed appointments
| when | what | who |
|---|---|---|
| Fri ≈ 18:00 | route 2 naphthalene done on hel1-14 → cation chain starts by itself; fetch the 97 Hessians, QFF + two-route noise read-out locally (`dpir.qff --disp 0.10`, `route_noise_structure.py`); record | me |
| Fri ≈ 19:00 | tuned protocol stage 2 read (100 / 175); stage 3 (read-out-aligned loss) implemented, smoked, launched | me |
| Fri ≈ 21:10 | module 06 seed 0: 20 epochs done (or early stop) → `train_log_seed0.json` written; copy weights + log to the laptop | me |
| Sat morning | naphthalene E8 (CCX53) read-out expected: `E8_locality_naphthalene` / `E8_between_naphthalene`; verdict recorded; L2b benzene tiers launched on the CCX53 while it still exists | me |
| Sat evening | **the user:** delete the CCX53 (after E8 + L2b are fetched) and create a CPX62 for layer-B shard 3 → I bootstrap it (`bootstrap_shardB.sh <ip> 3 5`) — **ping** | user + me |
| Sun (after cations) | hel1-14 → layer-B shard 4 (`bootstrap` recipe on the existing machine; cations' results fetched first) | me |
| Sun 20:00 | interim learning-curve reading on shards 0–2 (pre-declared, labelled interim); the tuned and fixed curves both | me |
| Sun evening | decision with the user: rang C timing; inputs: stage 1–3 curves, interim reading, E8 naphthalene | user |
| Mon morning | 100-table if all five shards have their first 20; conversation package final | me |

## Levers for the long-term line (each with its test, in the order I will work them when the machines are quiet)
1. **Proof of learning, made unassailable:** tuned protocol stages 2–3 on the 175 pool; both curves in every layer-B table; the interim point Sunday; class breakdown per point. Test: registered slopes.
2. **The label price, measured not estimated:** L2b tiers on benzene (accuracy vs cost) while the CCX53 lives; cation ULNO prices from hel1-14; affordability table lines updated. Test: a tier with |Δω′| ≤ 2.5 cm⁻¹ under 30 min per energy.
3. **The asset's infrastructure (what makes 2030 plausible)** — *started 25 Sep evening: `REPRODUCE.md` written (one line per number, command, output file); the rebuild-and-diff script `tools/rebuild_check.py` landed 25 Sep 22:5x (audit + per-row rerun with HEAD comparison); the release procedure exercised 23:0x on the local layer-B interim (60 molecules; `m05/release_index.py` → `data/corpus_release/RELEASES.md`, one row per manifest with deck hashes and archive SHA-256); still owed:* a versioned corpus release procedure (release notes, hashes, the manifest's deck hashes) exercised on layer B's first 100 (`build_release.py`), and the Zenodo deposit texts ready for the user; a `REPRODUCE.md` that rebuilds every number of the Monday package from the repository on a fresh machine. Test: a dry rebuild on a rented machine reproduces the E7/E11 numbers.
3b. **Module 07 build (authorised 25 Sep 17:5x, "zodra het rustig is"):** LangGraph run steward on the rule table `rules_v1.json`, replay harness for the eight scenarios (logs of 25 Sep as fixtures), deterministic gate with tests, then the live LLM step when the user supplies the Anthropic key; report and diagram last. Test: S1–S8 pass three times at temperature 0; the gate's tests fail without each guard.
4. **Rung C readiness without pre-empting Sunday's decision** — *done 23:1x: `m05/rungC_equivariant.py` + 5 tests, equivariance 1.5e-15 relative on water and benzene; no training* — the data loader and the equivariant model's tensor head written and unit-tested on water/benzene *without training on the pool* (the pre-registration allows building; the test run waits for the decision). Test: equivariance unit test (rotate input → rotated output to 1e-6).
5. **Robustness of the machines:** every runner with a heartbeat and a resume; the stale-lock guard deployed to shards 3/4 by bootstrap; monitor re-armed every 30 min; incidents → guards the same day.
6. **Communication:** the Monday package updated after each reading; blog only on the user's word; PushNotification only for Helsinki actions.

## What I will not do without the user
Create or delete servers; spend beyond the credit; publish; replace the pair model inside the running layer-B curve; start rang C training before Sunday's decision.
