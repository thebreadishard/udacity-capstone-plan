# Readers' figures

Figures made for a reader — the supervisor, the paper, the model card — live here, each as a PNG with a CSV of the same numbers beside it.
One script per figure under `probes/figures/`; a script reads records, writes the PNG and the CSV, and prints its row for the table
below. A figure is made again by running its script on the records its row names; nothing in a figure is typed by hand.

The curves of a single training are not here: every training writes a TensorBoard event log beside its record
(`<out_prefix>_tb/`, `m05/rungC_history.py`), and `probes/figures/history_to_tensorboard.py` makes the logs of the trainings stored
before 17 November 2026 from their records. The logs are output, not in git.

## Scripts

| script | figure |
|---|---|
| `probes/figures/training_curves.py` | one trainer record: per seed, training and validation of each loss term against the epoch, best epoch and early stop marked |
| `probes/figures/per_seed_molecule.py` | one hold-out molecule: an error per seed for two arms, from eval records |

## Figures

| figure (numbers) | script | records read | made |
|---|---|---|---|
