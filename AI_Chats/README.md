# Planning conversations

Cleaned transcripts of the conversations that produced this project, parsed from shared-chat pages
with the tooling in [`../scraper/`](../scraper/).

**A shared dump of primary sources, not plan documents.** They predate the splits and belong to
no plan: `gemini_chat_1.md` contains the original ambition — chemically precise IR spectra of large
aromatic molecules — which plan 01 deliberately downgraded and plan 02 partly restored. Filing them
under a plan folder would misrepresent whose idea they were. Plans 01, 02 and 03 are git history
only. Plan 04 is current; these chats still belong to no plan. Plan 04's Module 08 exit is again
an IR pipeline for an arbitrary individual aromatic (sequence ends at 09; no Projects 10–12) —
that is the original ambition returning as a scored product, not a reason to file these chats
under 04. `grok_chat_4.md` is plan 04's named source conversation, read in full when 04 was
created; it stays in this dump.

| File | What it is |
|---|---|
| `chat_urls.md` | The source share links |
| `gemini_chat_1.md` | Origin: the graph-cellular-automaton framing, before the switch to a grid |
| `gemini_chat_2.md` | The long one. Grid-over-graph, the rejected Ehrenfest design, and the ground-up restructuring after the 23-point external review |
| `grok_chat_1.md` | First "strict professor" pass; also where quantum computing was investigated and rejected for the NISQ era |
| `grok_chat_2.md` | Second professor pass, ending one step before the final Gemini revision |
| `grok_chat_3.md` | The motif-transfer counterproposal ("motif-local gold rungs + a transferable anharmonic correction", 2026-08-27); also the source of the third-hand Hudgins & Sandford matrix numbers that were later verified against PAHdb |
| `grok_chat_4.md` | HAVO/VWO walkthrough, in two halves: CC energy → PES → IR lines and why a full CC surface fails for coronene; then ORCA/DLPNO, the per-molecule Hessian + ML-anharmonic-correction recipe, its validation and its cluster cost — plan 04's named method seed |

## Provenance caveat

These are **parsed** transcripts, not verbatim exports. The raw scrape they were derived from is kept
in [`../scraper/gemini_context.txt`](../scraper/gemini_context.txt) precisely so the parse can be
re-checked: accessibility-tree dumps put formula subscripts in bare leaf nodes, and a parser that
only reads labelled text lines will silently drop digits from chemical formulas. If a quoted formula
in a plan document looks wrong, check the raw dump before trusting the transcript.

The share URLs may expire. The raw dump is the backstop.
