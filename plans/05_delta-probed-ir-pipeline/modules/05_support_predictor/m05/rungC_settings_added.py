"""Settings the rung-C trainer began to record at some point, each with the value it trained with before then, unrecorded.

A training record or a checkpoint written before a setting existed does not hold it; whoever compares an old one with a new one reads
the absent setting as the value below, and says so — `probes/epoch_repeat_check.py` (a re-run against the run it repeats) and
`probes/release_checks.py` check 1 (a release training against its measurement training). One table: a setting that is not in it and
is absent on one side is a difference, never a silent default. No import: the stdlib-only probes read it."""
from __future__ import annotations

from collections.abc import Iterable

RUN_ONLY = ("out_prefix", "threads", "seeds")     # the run's own: where it wrote, its threads, how the seeds were grouped into runs
SETTINGS_ADDED: dict[str, object] = {
    "weight_decay": 1e-4,             # AdamW's literal at chain 35's commit 4cb6140ad1, before it became a setting (26 Oct 2026)
    "holdout_twins": "keep",          # until be80cea0 (30 Oct 2026, TASKS 157) a hold-out molecule's twin stayed in the pool
    "lr_schedule": "constant",        # until 72352f3f (15 Nov 2026) every epoch trained at --lr
    "network_kind": "measurement",    # decision 66 (17 Nov 2026): every training until then left the hold-outs out
}


def with_absent_settings(settings: dict) -> tuple[dict, dict]:
    """(the settings with every absent one of the table filled in, the ones that were filled in): the second is for the record."""
    filled = {k: v for k, v in SETTINGS_ADDED.items() if k not in settings}
    return filled | settings, filled


def setting_differences(old: dict, new: dict, ignored: Iterable[str] = RUN_ONLY) -> tuple[dict[str, tuple[object, object]], dict, dict]:
    """({setting: (old value, new value)} for every setting outside `ignored` that differs once both sides have the table's absent
    settings filled in, what was filled in on the old side, on the new side): two trainings' saved settings compared one way, by
    `probes/release_checks.py` check 1 and `probes/v14_search.py`'s clean arm."""
    (old_full, old_filled), (new_full, new_filled) = with_absent_settings(old), with_absent_settings(new)
    keys = sorted((set(old_full) | set(new_full)) - set(ignored))
    return {k: (old_full.get(k), new_full.get(k)) for k in keys if old_full.get(k) != new_full.get(k)}, old_filled, new_filled
