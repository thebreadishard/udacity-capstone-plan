# Probes — Plan 03

Nothing in this folder is a result until a script has printed a number and the command line that produced it is recorded.

Minimum set before any Module 05 training run:

| Script | Prints |
|---|---|
| `grid_hash.py` | SHA256 of generator + spacing + box |
| `electron_count.py` | \(\int\rho_-\) on frame 0 vs nominal \(N\) |
| `dipole_identity.py` | residual of \(\boldsymbol\mu+\int\mathbf{r}\,\rho_-\,dV\) |
| `p0_fixed_point.py` | relative \(N\) drift after \(T_0\) field-free steps of the *untrained* linear stencil and, later, of the trained rule |
| `split_overlap.py` | 0 if train/test hashes disjoint |
| `teacher_cost.py` | wall-clock of H / H₂ / H₂O Maxwell windows vs the 168 h cap, or an honest “not run” exit |

Do not type those numbers into a markdown file by hand. Caps are in `GoalGathering/Compute_Budget_2026-09-01.md`.
