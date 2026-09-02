# Planning conversations

Cleaned transcripts of the conversations that produced this project, parsed from shared-chat pages
with the tooling in [`../scraper/`](../scraper/).

**A shared dump of primary sources, not plan documents.** They predate the splits and belong to
no plan: `gemini_chat_1.md` contains the original ambition — chemically precise IR spectra of large
aromatic molecules — which plan 01 deliberately downgraded and plan 02 partly restored. Filing them
under plan 03 would misrepresent whose idea they were. Plans 01 and 02 are git history only.
Plan 04 is incoming and will replace 03; these chats still belong to no plan.

| File | What it is |
|---|---|
| `chat_urls.md` | The source share links |
| `gemini_chat_1.md` | Origin: the graph-cellular-automaton framing, before the switch to a grid |
| `gemini_chat_2.md` | The long one. Grid-over-graph, the rejected Ehrenfest design, and the ground-up restructuring after the 23-point external review |
| `grok_chat_1.md` | First "strict professor" pass; also where quantum computing was investigated and rejected for the NISQ era |
| `grok_chat_2.md` | Second professor pass, ending one step before the final Gemini revision |
| `grok_chat_4.md` | HAVO/VWO walkthrough: CC energy → PES → IR lines; why a full CC surface fails for coronene |

## Provenance caveat

These are **parsed** transcripts, not verbatim exports. The raw scrape they were derived from is kept
in [`../scraper/gemini_context.txt`](../scraper/gemini_context.txt) precisely so the parse can be
re-checked: accessibility-tree dumps put formula subscripts in bare leaf nodes, and a parser that
only reads labelled text lines will silently drop digits from chemical formulas. If a quoted formula
in a plan document looks wrong, check the raw dump before trusting the transcript.

The share URLs may expire. The raw dump is the backstop.
