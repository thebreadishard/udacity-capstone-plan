# Running calculations without me watching

The laptop is free roughly 168 hours a week; human attention is roughly 8. This
folder is how the large budget gets spent without drawing on the small one, and
without a chat session sitting open burning tokens while a Hessian runs.

See [Compute_Budget_2026-08-27.md](../GoalGathering/Compute_Budget_2026-08-27.md)
for why those two numbers are different and what follows from it.

## The three commands

```powershell
cd plans\02_coupled-cluster-anharmonic-ir\probes

.\run_queue.ps1      # start, then close everything
.\stop_queue.ps1     # finish the running job, then stop
.\stop_queue.ps1 -Now  # kill the running job too
```

After `run_queue.ps1` the calculation is detached. **Close VS Code, close the
terminal, log out — it keeps going.** Only a reboot stops it, and then you just
run the script again: finished jobs are skipped, so nothing is ever repeated.

## Where to look when you come back

| file | what it tells you |
|---|---|
| `batch_results/STATUS.md` | every job, its state, its wall time, its headline number |
| `batch_results/run.log` | timestamped start / finish / failure, append-only |
| `batch_results/heartbeat.json` | pid and the job in flight, so you can tell alive from stuck |
| `batch_results/<job>.json` | the actual result, or the recorded failure |

**Start with STATUS.md.** It is regenerated after every job and is meant to answer
"where is it" in one glance, without opening anything else.

If the heartbeat timestamp is old and its pid is gone, the runner died. That is
not a problem: run `.\run_queue.ps1` again.

## Adding work

Edit `jobs.json`. It is read fresh on every pass, so **you can append jobs while
the queue is running** and they will be picked up without a restart.

Each job needs four things, and the third is not decoration:

```json
{
  "id": "10_freq_ovalene",
  "kind": "freq",
  "why": "36 -> 46 atoms extends the size trend past coronene, and re-fits the
          scaling exponent that currently rests on three points.",
  "params": { "name": "ovalene", "smiles": "...", "formula": [32, 14], "bays": 0 }
}
```

`why` exists because a queue that runs for days accumulates jobs whose purpose
nobody remembers. A job that cannot be justified in a sentence should not cost a
night.

**Order matters.** Jobs run top to bottom, so put the one that *decides something*
first. Sorting this queue by molecule size once pushed the decisive bay
measurement eleven hours out; reordering it by what each job settles brought that
back to four.

### Job kinds

| kind | what it does | params |
|---|---|---|
| `freq` | B3LYP/6-31G\* optimise + Hessian + IR intensities | `name`, `smiles`, `formula`, `bays` |
| `cc_timing` | times a coupled-cluster single point | `name`, `method`, `basis`, `geometry`, `memory_gb`, `threads` |

## Things learned the hard way

Each of these cost something before it became a rule.

**Every job runs in its own process.** Psi4 keeps global state, and a job that
dies mid-calculation leaves it inconsistent. The first version produced a
`Timer FNOCC: CC energy is already on` failure in the job *after* a genuine
out-of-memory one. A spurious failure that looks exactly like a real one is the
worst thing that can happen overnight.

**A failure is a result.** It is written to `<job>.json` with the stderr tail and
the queue continues. One non-converging geometry must not cost a night.

**Partial artefacts are deleted.** A job counts as done only when its complete set
of files exists, so a half-written result can never be mistaken for a finished one.

**Expensive intermediates are stored.** A `freq` job saves the Hessian as `.npz`
next to its JSON. Re-deriving a number from a stored Hessian takes a second; the
Hessian itself took an hour.

**Smoke-test on the cheapest molecule first.** A missing psi4 option once made
every frequency job die in two seconds on "unable to find a basis set" — fast
enough and plausible enough to have been read as a real result.

## Rebuilding the environment

```powershell
conda create -n qc -c conda-forge psi4 rdkit -y
```

Nothing else is needed. Psi4 1.11 and RDKit both have native Windows builds; this
was discovered after concluding, wrongly, that no quantum chemistry could run on
this machine at all. That conclusion came from testing `pip` and generalising to
the computer, while Anaconda sat in the shell prompt the whole time.
