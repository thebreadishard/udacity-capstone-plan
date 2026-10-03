# Frozen environments

One listing per Python environment the plan runs in, written by `tools/freeze_environments.py` (3 October 2026, after the requirements audit found that
module 05's file lacked `geometric` and `rdkit` and that the compute environments had no frozen listing at all). Nothing here is typed by hand.

| file | what runs there | how it is listed |
|---|---|---|
| `windows-python314.txt` | modules 05/06, the Windows probes (torch, rdkit, geometric); identical to `modules/05_support_predictor/requirements.txt` | `pip freeze` |
| `windows-venv313.txt` | module 07 (LangGraph) | `pip freeze` in `.venv` |
| `wsl-qc05.txt` | our pyscf branch, the E8 anchors, gate 1, the LNO probes | `pip freeze` in `~/qc05` (WSL) |
| `wsl-vpt2.txt` | psi4 + pyVPT2 (route 2) | `conda list --export` (WSL miniforge) |
| `server-*.txt` | the rented servers' `qc` / `qc05` environments | copied by hand from the full-fetch waiters' `environment_*.txt` (`probes/fetch_*_full_*.sh`), dated |

Rules: regenerate after any install or environment rebuild (`python tools/freeze_environments.py`); `--check` says whether the committed listings
still match the machine it runs on (the header's date is ignored; an environment that cannot be reached from the machine is skipped, not failed).
Python versions follow the rule in the software ledger: per environment the newest version its heaviest dependency supports, pinned, raised only at
a rebuild — never mid-run.
