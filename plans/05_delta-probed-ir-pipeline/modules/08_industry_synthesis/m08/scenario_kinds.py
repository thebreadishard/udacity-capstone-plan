"""Which of the request scenarios were pre-registered and which were added (20 November 2026).

`PRE_REGISTRATION.md:11` says it in a sentence: "S2b, S4b and S4c are added cases of the same kind". The notebook and the paper
state the two groups, so the ids are named here once, and a results record that does not hold exactly these requests is refused:
a renamed or new case must be placed in one group by hand, not counted into one by default.
"""
from __future__ import annotations

PRE_REGISTERED_REQUESTS = ("S1", "S2", "S3", "S4a", "S8")   # PRE_REGISTRATION.md's table: S1–S4 and S8 (S4 runs as S4a)
ADDED_CASES = ("S2b", "S4b", "S4c")                          # PRE_REGISTRATION.md:11
MECHANICAL_CHECKS = ("S5", "S6", "S7")                       # not requests: reported apart


def request_kinds(ids: list[str]) -> tuple[list[str], list[str]]:
    """(pre-registered ids, added ids) of a results record's request scenarios, in the record's order."""
    missing = [i for i in PRE_REGISTERED_REQUESTS + ADDED_CASES if i not in ids]
    unknown = [i for i in ids if i not in PRE_REGISTERED_REQUESTS + ADDED_CASES]
    if missing or unknown:
        raise ValueError(f"the results record's requests are not the registered ones: missing {missing or 'none'}, neither "
                         f"pre-registered nor added {unknown or 'none'} (m08/scenario_kinds.py, from PRE_REGISTRATION.md:11)")
    return [i for i in ids if i in PRE_REGISTERED_REQUESTS], [i for i in ids if i in ADDED_CASES]
