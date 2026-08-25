# Professor Review — 2026-08-25, Round 4, Pass A (cold read)

**Reviewer:** Grok, given only the plan-02 document set and
[the Pass A brief](Review_Brief_2026-08-25_Round4_PassA.md). No access to the conversation that
produced the documents — deliberately, since that is the defense situation.

**Verdict:** *Internally sound enough to proceed to Pass B, once three documentation-status
contradictions are cleaned so a cold reader cannot be misled about what is current.*

**Pass B has not yet been run.** This review covers internal consistency only, not the chemistry.

---

## Blocking findings

### 1. Stale rewrite-status note in the plan README's reading order

**Where:** `README.md`, "Reading order" item 3.

Told the reader "§1–§4 are rewritten, §5–§9 are still plan 01's text", while the rewrite-status table
three lines below and the Distilled Plan's own banner both said all nine sections were rewritten.

> A cold reader following the prescribed order is told that half the technical plan is still the
> superseded voxel plan.

**Status (2026-08-25): CLOSED.** Line corrected. The reading-order entry now states that all nine
sections are rewritten for R3. Cause: the rewrite-status table was updated section by section as the
work progressed; the prose line above it was not.

### 2. The Restructure Proposal still declared itself un-adopted

**Where:** `Restructure_Proposal_2026-08-23_Project12_in_Module08.md`, status block.

Said *"Not yet adopted. Nothing in Distilled…, Overarching_Goal… or Capstone_Mapping… has been
changed"* — while every other document treated the pivot as adopted and executed.

> The cold reader cannot tell whether the current documents are the adopted plan or a draft that
> still awaits a decision. This is the exact class of status drift the inheritance table was written
> to prevent.

**Status (2026-08-25): CLOSED.** Status block rewritten to **ADOPTED**, naming which decisions were
accepted, on which dates, and which document is deliberately still pending (`Capstone_Mapping.md`,
held for Round 4). The document is now explicitly labelled as the *argument of record* rather than a
live proposal, and §12's decision list as a historical record.

### 3. The inheritance-table arithmetic could not be audited

**Where:** `README.md`, inheritance table and its summary sentence.

The reviewer's fetch truncated the table and it therefore could not verify the summary
*"six superseded, one inverted, one resolved by construction, twelve carried forward, one still
open."*

**Status (2026-08-25): CLOSED, and the finding was worse than the reviewer could see.** The table in
the file is complete — the truncation was a fetch artifact. But counting it by hand shows **the
summary was wrong**:

| Fate | Claimed | Actual |
|---|---:|---:|
| Superseded | 6 | **4** (issues 1, 2, 14, R3-1) |
| Re-scoped to the dipole-surface leg | — | **2** (issues 7, 10) |
| Inverted | 1 | 1 |
| Resolved by construction | 1 | 1 |
| Carried forward | 12 | 12 |
| Still open | 1 | 1 |

Two issues had been silently folded into "superseded" that were in fact re-scoped, not dropped —
precisely the misrepresentation the table exists to prevent. Replaced with an **itemised tally** that
names the issue numbers in each category, so a reviewer can check it without recounting.

---

## Non-blocking findings

| # | Finding | Status |
|---|---|---|
| 1 | Open items are correctly flagged with closure gates, but no **template** was given for the required dated amendments, so a reader cannot see the form the missing documents must take | **CLOSED.** `Frozen_Ladder_and_Tolerances_2026-08-25.md` §7 now gives the amendment template and a worked example for the GVPT2 resonance criterion |
| 2 | Tolerance wording varies ("within a stated cm⁻¹", "≤ 10 cm⁻¹") but no numerical value drifts | **Accepted, no action.** Phrasing variation across documents with different registers |
| 3 | Bibliography claims are cited but the plan never shows a one-line verification that the cited claim appears in the referenced paper — "supported by a citation you could not verify" | **Open, acknowledged.** A fair criticism of every bibliography. Deferred to Pass B, which is asked to check specific numbers against the literature |
| 4 | References to plan 01 issue numbers and Horizon files are opaque to a reader who never saw plan 01 | **Accepted, no action.** The inheritance table is the intended bridge; making every reference self-contained would duplicate plan 01 into plan 02 |

## Questions the reviewer could not resolve

Recorded because several become Pass B or gate-time work:

- Whether the proposal's status block was simply never updated → **yes, it was an oversight** (blocking finding 2).
- The truncated inheritance rows → **resolved**, see blocking finding 3.
- The form of the G0 resonance amendment → **now specified**, non-blocking 1.
- Whether "published scatter" for the G0 PAHdb baseline reproduction has a numerical value →
  **open.** It does not yet. It must be fixed at G0, from the chosen PAHdb version, before the
  reproduction is scored.
- Exact experimental identifiers (NIST dataset ID, the pyrene IRMPD paper, the JWST/PAHdb product) →
  **open by design**, listed in `Frozen_Ladder_and_Tolerances_2026-08-25.md` §6 with their closure
  gates.

## What passed

Quoted rather than paraphrased, because a review that finds only faults is not calibrated:

- **R3 is defined once and held constant** across the prime directive, the README, Distilled §2/§3/§9
  and the frozen targets. The forbidden-quotes lists in two documents are identical in substance.
- **The four-term error budget is mandatory and non-poolable**, with "a single pooled number is a
  fail" appearing in four separate places.
- **Tolerances and the stop rule are frozen before any calculation**, in a document marked
  un-editable except by a dated superseding document, and declared authoritative by Distilled §5.0.
- **Gates G0–G6 are measurements with written verdicts, not milestones** — ordering rules,
  independent gating of positions versus intensities, three pre-registered bake-offs, "inconclusive
  is publishable", and the negative-control requirement all present and mutually consistent.
- **The central inversion is stated without contradiction**: borrow the representation, own the
  theory anchor and the nuclear motion; the voxel field demoted to one non-critical leg; classical MD
  demoted to a temperature diagnostic; Projects 10–12 absorbed.
- **Claim language is itself gated**, including the two "sentences most likely to be written by
  accident".

> The documents say what they think they say on the scientific content and the governance machinery.
> The remaining defects are documentation-status artefacts.

---

## Assessment of this review

All three blocking findings were real, and all three were **status drift**: documents describing an
earlier state of themselves. That is the predictable failure mode of a rewrite done section by
section over several days, and it is exactly what a cold reader catches and an author cannot.

Finding 3 is the one worth remembering. The reviewer could not verify a count and said so rather than
waving it through — and the count was wrong. A checkable claim that nobody checks is indistinguishable
from a false one.
