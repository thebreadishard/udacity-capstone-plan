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
