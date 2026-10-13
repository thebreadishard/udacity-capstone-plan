# The residual-checked route-C APT: install, recompute and second route (registered 12 October 2026, before the runs)

*On the user's word (12 Oct, 11:2x): 'Ja, doe a, b en c zoals je adviseert.' Design note `GoalGathering/notes/Design_2026-10-12_Residual_Checked_APT.md`;
TASKS 44. Code: `corpus/apt.py` (`solve_response`, `refine_response`, `CPHF_BOUND` = 1e-6), `corpus/analytic_hessians.py` (`write_apt`,
`labels_mol`, `labels_scf`), `probes/apt_recompute_refined.py`, `tools/install_labels_code.sh`. Tests on water (WSL, 12 Oct 11:3x–11:4x):
19 pass, among them the refined APT against the field route 7.5e-6 e (unrefined 6e-5), a perturbed response repaired, and a residual above
the bound giving passed=False and exit 3.*

## Lines, fixed before each run

**L1 — the production code on benzene** (`../krylov_report_2026-10-12/refine_production_benzene.py`; labels settings, no Hessian):
residual after ≤ 1e-6 in one round, and the refined APT within 5e-5 e of the field route (`benzene_field.npz`, with grid response; agrees with FD
of the dipole to 3.9e-5). Reference: `refine_batched.py` gave 7.8e-8 and 3.75e-5. Fails → no install.

**L2 — the server smoke** (`tools/install_labels_code.sh`): water in `/root/labels/staging_apt` at grid (50, 194) exits 0, its APT file says
passed, route `hessian_response_refined`, and carries the sha256 of the two files sent. Fails → no install (the script stops itself).

**L3 — the recompute (b)** of every APT file on the server whose route is `hessian_response` at the install (47 at 11:4x, all ≤ 22 atoms):
every molecule passes (residual ≤ 1e-6, sum rule ≤ 5e-4 e). Expected: the APT changes by ≤ 1e-3 e and the band heights by ≤ 1 % of the
strongest band (benzene: 4.3e-4 e, ≤ 0.6 %). A molecule beyond either is examined before its file goes to the server. The old files are kept
on the server in `/root/labels/apt_unrefined_2026-10-12/`; a new file replaces an old one by cp + mv.

**L4 — second route on a sample** (`probes/apt_field_route.py`, F = 1e-3, labels settings): five of the recomputed molecules — the two with
the largest APT change, and the first, middle and last of the rest by sorted id — the refined APT within **1e-4 e** of the field route without
grid response (the derivative the analytic Hessian takes); the field route with grid response is reported beside it. Water measured 7.5e-6
(without) and 1.7e-5 (with).

## Outcome

*(appended after the runs)*

**The guard's two failures, diagnosed (13 Oct 09:2x).** Two of the first 20 refined labels APTs stayed above the 1e-6 bound after three batched
rounds: B_1194d7a42a at 1.1e-6 and B_127dd8c4ed at 2.1e-6. The bound was not moved. The diagnosis on B_127dd8c4ed (`diagnose_floor.py`, rule fixed
in its docstring before the run → `floor_B_127dd8c4ed/diagnose_floor.{log,json}`):
- the batched rounds are flat: 1.7e-6 (1 round), 2.1e-6 (2), 2.1e-6 (3), 2.1e-6 (5);
- 46 of 66 columns stayed above 1e-7;
- the operator is deterministic (two applications differ by 1.0e-15);
- scipy GMRES on each of the worst twelve columns alone reaches 2.1e-12 to 1.2e-11 (gmres info 0 in all twelve).

**Reading: solver (1)**, max 1.2e-11 against the line ≤ 1e-7. The batched multi-root `lib.krylov` stalls where a single right-hand side
converges — pyscf #2702's early stop again; upstream's remedy in #3384 is per right-hand side too.

**Action, as the rule says.**
- `apt.refine_response` gained the per-column GMRES fallback after the batched rounds (commit 3eb7cd0f; test: with no batched round allowed,
  the fallback alone brings a perturbed water response below the bound to the refined APT within 1e-6 e). It is recorded as
  `cphf_fallback_columns`.
- Installed on the labels server 13 Oct 09:22 local (`tools/install_labels_code.sh`: water smoke passed, residual 1.4e-7; sha 35bb49dfb46f /
  fcd373fcd45c).
- The two molecules are recomputed first in recompute lane 2 (`apt_recompute_refined.py` now also takes a failed refined file).

The script's own '≈ 2 h' was unmeasured; it took 7.4 h (26,585 s), because its loop re-ran the refinement from scratch for 1, 2, 3 and 5 rounds.
