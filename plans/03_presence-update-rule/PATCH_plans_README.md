# Patch for `plans/README.md`

**Status: APPLIED 2026-09-01** to [`plans/README.md`](../README.md) and the root
[`README.md`](../../README.md). This file is the argument of what was applied, not a live
proposal. **Plan 03 remains draft. Do not call it complete as a plan.**

A later pass on **2026-09-01** removed the plan-01 and plan-02 folders from the tree. Live index
files now list **only plan 03**. The three-column comparison below is **historic**. It is not a
set of workspace links.

The applied opening was “planned three times.” The applied comparison table was:

| | 01 — Voxel Field PES | 02 — Coupled-Cluster Anharmonic IR | 03 — Presence-Update-Rule |
|---|---|---|---|
| **Status** | Superseded 2026-08-23. Complete; not developed. | Superseded 2026-08-29. Complete as a plan; blocked on measurement. | **Current.** Draft; not complete as a plan; not executed. |
| **Deliverable** | Vibrational band positions / IR envelopes, H₂O–benzene | Anharmonic IR families, benzene and naphthalene, four-term error budget | A shared local presence-update rule with P0–P4 gates on H₂ and H₂O |
| **Where precision comes from** | Own CCSD(T)/cc-pVTZ labels | A measured CC rung | Named Octopus RT-TDDFT (ALDA) on a **frozen** grid |
| **The model** | Hybrid FNO-NCA, \(E=\mathcal{E}[\rho,R]\) | Fine-tuned equivariant MLIP as cheap QFF half | 3-D conv stencil on \((\rho_\pm,\mathbf{j},\mathbf{E},\mathbf{B})\) |
| **Nuclear motion** | Classical MD + dipole-ACF | GVPT2 / hybrid QFF | Frozen nuclei on the scored window |
| **Central question** | Field vs GNN transfer on vibrations | Does a CC anchor beat DFT-anchored PAH IR? | Does one local field rule transfer H₂ → H₂O and stay a fixed point? |
| **Horizon** | Projects 10–12 | Absorbed / none | Projects 10–12 (phase, pair density, scale) |
| **Reviews survived** | Rounds 1–3 | Round 4 | None yet |

Applied also:

- section **Why there are three** pointing at [`GoalGathering/Why_03_Supersedes_02.md`](GoalGathering/Why_03_Supersedes_02.md)
- 01 was not wrong; 02 was not wrong — it is blocked on a label factory the rubric sequence cannot wait for
- “Adding a version 04” keeps the copy-folder rule (new versions; do not resurrect deleted 01/02 folders)

This patch does **not** make plan 03 complete. It was applied when root and `plans/README.md` said
**current / draft**. Live indexes as of 2026-09-02 say **04 incoming / 03 last written** instead;
this file is not the live index.
