# Patch for `plans/README.md` (apply by hand in the real repo)

Replace the opening sentence “planned twice” with “planned three times.”

Replace the comparison table header and add a third column. Suggested table:

| | [01 — Voxel Field PES](01_voxel-field-pes/) | [02 — Coupled-Cluster Anharmonic IR](02_coupled-cluster-anharmonic-ir/) | [03 — Presence-Update-Rule](03_presence-update-rule/) |
|---|---|---|---|
| **Status** | Superseded 2026-08-23. Complete; not developed. | Superseded 2026-08-29. Complete as a plan; blocked on measurement. | **Current.** Complete as a plan; not executed. |
| **Deliverable** | Vibrational band positions / IR envelopes, H₂O–benzene | Anharmonic IR families, benzene and naphthalene, four-term error budget | A shared local presence-update rule with P0–P4 gates on H₂ and H₂O |
| **Where precision comes from** | Own CCSD(T)/cc-pVTZ labels | A measured CC rung | A named teacher (exact 2-e or RT-TDDFT) on a **frozen** grid |
| **The model** | Hybrid FNO-NCA, \(E=\mathcal{E}[\rho,R]\) | Fine-tuned equivariant MLIP as cheap QFF half | 3-D conv stencil on \((\rho_\pm,\mathbf{j},\mathbf{E},\mathbf{B})\) |
| **Nuclear motion** | Classical MD + dipole-ACF | GVPT2 / hybrid QFF | Frozen nuclei on the scored window |
| **Central question** | Field vs GNN transfer on vibrations | Does a CC anchor beat DFT-anchored PAH IR? | Does one local field rule transfer H₂ → H₂O and stay a fixed point? |
| **Horizon** | Projects 10–12 | Absorbed / none | Projects 10–12 (phase, pair density, scale) |
| **Reviews survived** | Rounds 1–3 | Round 4 | None yet |

Add a section **Why there are three** pointing at `03_presence-update-rule/GoalGathering/Why_03_Supersedes_02.md`.

Keep the paragraph that 01 was not wrong. Add: 02 was not wrong; it is blocked on a label factory the rubric sequence cannot wait for.

Under “Adding a version 04”, keep the same copy-folder rule.
