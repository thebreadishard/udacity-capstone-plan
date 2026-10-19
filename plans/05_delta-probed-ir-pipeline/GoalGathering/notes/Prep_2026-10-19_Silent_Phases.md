# Preparation for 19 Oct 2026: software that writes no log line for hours

The user, 18 Oct 22:3x: 'Laten we morgen bespreken hoe we nooit meer software starten die urenlang geen logregel schrijft.' TASKS, fixed
appointments. This note gives the facts and the options. The decision is the user's.

## What happened (TASKS 60)

- S1-TZ acenaphthylene was relaunched on s1 at 16:31 after the SCF fallback. Its first step is a geometry optimisation at def2-TZVP. In
  `probes/s1_anharmonic_level.py`, `optimise()` writes one line, when BFGS ends. At 22:04 the process had run 5 h 33 min at 505 % CPU with
  no line. From the log alone, slow and stuck look the same.
- The run's contract (`probes/runspecs/s1tz_acenaphthylene.json`) counts progress from file growth (`progress_on_growth.sh`: `*.json` under
  the run folder) with a 120 min gap. The optimisation writes no json, so the contract was bound to fail. It was written for the Hessian
  phase, not the optimisation before it.
- **Second finding:** the anomaly was due from 18:31 and reached the session at 22:02. At 21:43, `ps` showed no `watch.sh`. After it
  was re-armed, it first reported four start lines from 14:31 and 16:26, one per wake, and only then the anomaly. So no watch ran from
  before 16:26 until 21:4x. When it stopped is not known, and nothing reported that it had stopped. The watcher has the same fault as the
  program.

## Inventory of 18 Oct (16 run specs; `scratchpad/runspec_inventory.py`)

| run spec | host | allowed gap | where the progress comes from | known silent phase |
|---|---|---|---|---|
| s1tz_benzene / _naphthalene / _acenaphthylene | s1 | 120 min | file growth (`progress_on_growth.sh`) | **the T optimisation**: one line at its end. Naphthalene 13:03 → 16:43 (3 h 40 min); acenaphthylene > 5.5 h |
| anchors3_wave2 | anchors3 | 120 min | file growth (`anchor_wave_progress.sh`) | one CC gradient per file. Its length is set by the 50 h estimate, not by the code |
| fivering_half_a / _b | pool3 | 120 min | file growth + per-molecule lines | per molecule; to check |
| chain35h2, chain41–44 | laptop | 90–120 min, `start_regex` yes | `chain_runner.py` + training lines | training writes every 10 epochs (`rungC_train.py`: chain 41 ≈ 100 s per epoch → ≈ 15 min). The data loading before the first epoch has not been measured |
| apt_l4, apt_l4_diag | laptop | 90 min | lines per field component | one CC field step per line |
| s2_xtb | laptop | 30 min | per-molecule lines (`[hh:mm:ss] k/n`) | one dxtb molecule per line |
| hybrid_floor, m06_pahdb_samples | laptop | 30 / 120 min | progress lines in the code | — |

Code lines found: `pyscf_hessians_for_qff.py` writes one line per Hessian (≈ 600 s each for benzene at T). `optimise()` writes only at its
end; `newton_polish()` writes one line per step.

## Found the next morning (19 Oct 04:5x)

Acenaphthylene's optimiser was not only silent by design. Its RSS rose from 0.26 to 4.3 GB, the size of a T Hessian, so it had most likely left BFGS for Newton polish. The 'BFGS:' line had been printed but sat in Python's stdout buffer: `print` to a file is block-buffered. Naphthalene's optimisation lines also appeared only when its process ended. A line the program writes is no use if it reaches the log hours later. Rule 1 therefore includes `flush=True`, and launchers run Python with `-u` or `PYTHONUNBUFFERED=1`.

## Candidate rules, each with its cost

1. **A heartbeat in the code.** Any loop that can run longer than about 10 min writes a line per iteration: elapsed time, the quantity
   that converges, and the solver used. A single long call writes a line before it starts and one when it ends, with the expected
   duration. *Cost:* one edit per script, never to a running one. Tests check that the line appears. `optimise()` is the first case.
2. **The contract measured on the smoke run.** `tools/runspec.py launch` refuses a spec whose `max_gap_minutes` is smaller than the longest
   gap between progress lines in the spec's smoke log × a margin. It also refuses a spec without a smoke log at a size that covers every
   phase. *Cost:* the smoke runs become part of the launch, and the largest phase must be measured, or scaled from a smaller molecule with
   the scaling stated.
3. **Phases in the contract.** The spec lists phases (optimisation, Hessians, …), each with its own regex and its own gap, and the check
   reports which phase is silent. `start_regex` already does this for one phase. *Cost:* a change to `runspec.py` and its tests.
4. **Liveness without the log.** When the log is silent, the check reads the process's CPU time and, where it is installed, a stack sample
   (`py-spy dump`). Rising CPU in a solver means slow; flat CPU or a wait means stuck. *Cost:* small, and it needs no change to running
   code; py-spy on the servers.
5. **A heartbeat for the watcher.** `state.sh` and the resume task report when `watch.sh` is not running while a run spec is live. That is
   the fault of 18 Oct between ≈ 16:30 and 21:49. *Cost:* small.

My proposal, for the conversation: 1 and 5 as rules (in CLAUDE.md and the hook list), 2 as the launch check, 4 as the fallback diagnosis.
Rule 3 only if 2 turns out too coarse.
