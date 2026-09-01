# Probes — Plan 03

Nothing in this folder is a result until a script has printed a number and the command line that produced it is recorded. Missing teacher files print `NOT_RUN` and exit 2. Do not type those numbers into a markdown file by hand. Caps are in [`../GoalGathering/Compute_Budget_2026-09-01.md`](../GoalGathering/Compute_Budget_2026-09-01.md).

Run from this folder. No Octopus job is started here.

| Script | Prints |
|---|---|
| `grid_hash.py` | SHA256 of generator + \(0.20\,a_0\) + box + refinement (Q0). Re-run must match while `grid_spec.py` is frozen. |
| `electron_count.py` | \(\int\rho_-\,dV\) on frame 0 vs `--n-electrons` (Q1) |
| `dipole_identity.py` | grid moment \(M=\int\mathbf{r}\,\rho_-\,dV\) and, with `--mu`, residual \(\boldsymbol\mu+M\) (Q2) |
| `p0_fixed_point.py` | relative \(N\) drift after \(T_0=200\) steps of the *untrained* linear stencil (Q3 / P0). Learned rule is `NOT_RUN` until hashed. |
| `split_overlap.py` | overlap count; `0` if disjoint (Q4). `--label q5` for no water in the H₂ train hash. |
| `teacher_cost.py` | H / H₂ / H₂O seconds vs 168 h, or honest `NOT_RUN` |
| `b_numerically_zero.py` | \(\max\|B\|\). Drop-\(B\) stays forbidden until this prints ~0 **and** a §4 note. |
| `linear_stencil.py` | library; P4 / P0 baseline (continuity + Maxwell, no learned coefficients) |

Helpers: `grid_spec.py` (frozen constants; part of the Q0 digest), `cube_io.py` (cube / npz).

Q6 (one training step = one conv over the volume) is not a file yet; it waits on a hashed PyTorch op.
