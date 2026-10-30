# The pipeline's backlog

Action items for `m08/pipeline.py` (decision 64, TASKS 146; the build note `PIPELINE_BUILD_NOTE_2026-10-29.md`). One line per item: what,
why (the evidence that asks for it), its TASKS row, and whether it comes before or after the demonstration of 25 November. A done item
leaves this list; the pipeline version that carries it is named in `modules/PIPELINE.md`.

| what | why | TASKS | when |
|---|---|---|---|
| The request officer runs the pipeline for a rung 2–3 request | it refuses and names the pipeline today (decision 65); the replay worker would start a pipeline run behind module 07's gate | 146 | after |
| Module 08's notebook and paper on decision 65 | both describe the licence of 28 Sep (layer B, no family) | 146 | after |
| The network's answer independent of the atom order | v1.3 moves bands by up to 2.9 cm⁻¹ between SMILES writings (0.2 fixes one order per molecule, not the spread) | 149 | before |
| An xyz input in the canonical order | 0.2 canonicalises a SMILES only; an xyz keeps its own order, so its answer depends on how it was written | 149 | after |
| Anharmonic shifts on the positions | the positions are harmonic; S1/S2 measure the anharmonic step | 53 | after |
| Cations and other open-shell molecules | refused today (charge, multiplicity); the 60 pool-3 cations have analytic UKS labels, the network has no carried cation rung | 98, 121 | after |
| The geometry without psi4 (pyscf + geomeTRIC) | one engine instead of two; only after a check that it gives the same Hessian and network read | 73 | after |
| v1.4 if chain 44 carries it | a new network version is a new pipeline version | 129 | after |
| The reach beyond about 40 atoms | the DFT step's measured reach (8–9 Oct) and the size penalty (chain 42) | 49 | after |
| The CC anchors' fine-tune | after November's anchor decision; the fine-tune is R2 (body1_es, cap 120), the anchor count's registered meaning | 82, 145 | after |
| The laptop's Hessian time for large molecules | the analytic Hessian is the step that grows fastest with size | 146 | after |
| Promotion into `src/dpir` and the product repository | the forkable product of 2027 | 73 | after |
| The run's commit stamped at launch | `pipeline.json` takes the commit when the run ends (candidate06: 94d8981e, launched at fe941b7f); a commit between launch and end would name code that did not run | 146 | before |
| The demo molecules re-run at the meeting's pipeline version | the page shows each molecule at the version that ran it (benzene 0.1, phenanthrene 0.2, the candidate 0.3); 0.3 reproduces the first two to the bit, but one version on the page reads cleaner; laptop: about 6 min, 77 min and 3.7 h | 146 | before |
