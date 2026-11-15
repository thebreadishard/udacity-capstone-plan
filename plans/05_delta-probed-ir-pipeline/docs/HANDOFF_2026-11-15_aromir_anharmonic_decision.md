# Handoff — aromir and the anharmonic step: researched, and decided for 0.2 (15 November 2026)

Follows `HANDOFF_2026-11-15_aromir_stage3.md`. Written from the same cloud session. TASKS 73, 211, 219.

## The decision (the user, 15 Nov, after the research below: 'B')

**aromir 0.1 prints harmonic positions and its certificate says so. The anharmonic step comes in aromir 0.2 as an optional extra,
after it is built and accepted here first (TASKS 211), with the CH-stretch read (TASKS 219).** This replaces the user's choice of that
morning ('anharmonisch meenemen') for 0.1 only; the registration of 14 November (`PreRegistration_2026-11-14_Printed_Band_Position.md`)
stands for the pipeline here. The interim of one family-mean shift per family (route (c): 8.47 / 4.34 / 9.27 cm⁻¹ on the targets) was
offered and not chosen.

Proposed for TASKS (not edited from the cloud): row 73 — 0.1 is harmonic, 0.2 carries the step; row 211 — its *Next* now also feeds
aromir 0.2, and names the two open questions below.

## What the research found (read-only; nothing was run)

- The step is registered, not built: `m08/pipeline.py` still carries `HARMONIC_NOTE`, and TASKS 211's *Next* is 'build it'. No fitted
  `x2*` artefact exists.
- Per molecule it needs a GFN2-xTB quartic force field (coronene: 102 Hessians in 136.6 min on the laptop, ledger 11 Nov), the GVPT2
  solve through pyVPT2 — the fork `polyad-assignment-and-merge`, because upstream 2eae571 fails on S2's molecules, and pyVPT2 imports
  psi4 — the xtb-to-B3LYP mode match (`s2_xtb_read.MIN_OVERLAP` 0.5), the domain marks, and the fitted model.
- For a public package that means xtb (conda only) and psi4 behind an optional extra: the design's one pip-installable engine
  (`docs/product_repo_design.md`, point 1) does not stretch to it.
- The acceptance test of the registration (the per-family rms of `route_rule.md` to 0.01 cm⁻¹ on coronene and tetracene) needs the
  force fields of the 37 training molecules. In git: the GVPT2 labels (S2 14, S2b 23, the two targets), 44 `ref.json`, and 10
  `qff_report.npz` (benzene, water, tetracene, one styrene). Whether that suffices to refit `x2*` was not established.

## Two questions the registration leaves open, to settle before the step is built

1. **Which modes carry the model's inputs for a new molecule** — the B3LYP modes (as in training, where ω, h and o are the G
   setting's) or the ΔH-corrected ones that ν = ω(ΔH network) + Δ_anh is added to?
2. **How a mode of a new molecule is marked.** `vpt2_domain`'s strain is |ν − ω| / ω of the B3LYP label, which a new molecule does not
   have; only its xtb force field can be marked ('a G mode whose xtb partner is marked is marked too'). Whether the xtb marks alone
   catch what the G marks catch (coronene's 24 and 36) is a read on the labels in hand.
