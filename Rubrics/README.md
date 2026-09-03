# Udacity capstone rubrics

Scraped requirements for Udacity capstone modules 01–09, extracted with the tooling in
[`../scraper/`](../scraper/).

**Shared between all project plans**, and treated as **fixed** within this repository. These files
are the constraint every plan is designed against; they are not project work and contain no
plan-specific content. Do not overwrite the scraped Udacity wording. Workspace reading notes
(blockquotes at the top of a file, or this README) are how this repo records how to *read* that
wording; they are not Udacity text.

| | |
|---|---|
| Course | `cd001-capstone` |
| Rubric version | **1.5.1** (recorded in the classroom URLs inside `01_APA_Resources.md`) |
| Files | 01–09, one per module |

## Dataset rule (do not re-litigate this)

The load-bearing dataset rule in Modules 03–06 is: the data must be **publicly available before that
project starts**, appropriate for academic use, not synthetic or AI-generated, and not reused from
an earlier capstone project.

Modules 03 and 04 also print an *Accepted Sources* bullet list (Kaggle, UCI, Data.gov,
FiveThirtyEight / open-government portals). **That list is not a closed gate.** It is a set of
examples of public sources. Module 05 has **no** such list and explicitly allows “standard
benchmark datasets or curated real-world datasets.” Module 02 says “or use your own dataset.”
Module 06 says “publicly available or clearly documented.”

A self-computed corpus (Octopus cubes, psi4 Hessians, …) can satisfy the rule **if it is published
and reachable before the module begins** (public GitHub or a Zenodo DOI). It cannot if it is
generated during the module and only then called “the dataset.” “Must come from Kaggle or the US
government” is a misreading that already blocked plan 03’s Module 03 dataset; do not repeat it for
04/05 or for plan 04.

The “not synthetic or AI-generated” clause still forbids fabricated or model-generated *training
data*. Ab initio / TDDFT labels are computed science data, not that clause — say so in the report
so a grader does not equate “computed” with “AI-generated.”

## If the rubric ever changes

Do **not** overwrite these files. Add a sibling folder — `Rubrics_v1.6/` — and repoint the plan that
was designed against the new version. Several planning decisions turn on exact rubric wording
(dataset publicity, the synthetic/AI-generated clause, Module 04’s *Accepted Sources* bullets as
examples not a gate). Silently replacing the text underneath a finished analysis would invalidate
it without leaving a trace.

## What is not here

Documents 10–12 used to sit alongside these rubrics. They are **not** rubrics — they are the
project's own horizon-planning documents, and they differ between plans. Plan 03 kept them in
its `GoalGathering/Horizon/` (git history since 2026-09-02); plans 04 and 05 have no horizon
documents by design — the sequence ends at Module 09.
