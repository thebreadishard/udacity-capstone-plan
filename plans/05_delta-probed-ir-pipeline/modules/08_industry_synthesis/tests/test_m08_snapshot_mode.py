"""The submitted module gives the same answers as the one in the plan (the standalone plan of 18 October 2026, step 2's last item).

A snapshot is only worth anything if the module reading it decides what the module reading the plan decides. So: build a snapshot into
a temporary folder, run the eight scenarios against it with nothing but that folder to read from, and compare the decisions with the
ones the plan-mode run just made. Everything is compared except the fields that are allowed to differ - the date, and the provenance
paths, which name where a file was read from and so differ by construction.

It builds a snapshot and runs the scenarios twice, in about twelve seconds, so it runs with the rest of the module's suite:

    python -m pytest modules/08_industry_synthesis/tests -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
sys.path.insert(0, str(MODULE))
from m08 import paths  # noqa: E402

# what two honest runs may differ in: when they ran, and where each file came from
VARYING = frozenset({"date", "built", "provenance", "evidence", "path", "paths", "source_path", "files"})


def decisions(record: dict[str, Any]) -> dict[str, Any]:
    """Each scenario's decision by id, with the fields that are allowed to differ removed."""
    return {s["id"]: strip(s.get("decision")) for s in record["results"]}


def strip(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: strip(v) for k, v in value.items() if k not in VARYING}
    if isinstance(value, list):
        return [strip(v) for v in value]
    return value


def run_scenarios_here(out: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """The scenarios in this process, writing into `out` rather than the module's own folder, and their results record."""
    import run_scenarios as scenarios

    out.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(scenarios, "OUT", out)
    scenarios.main(["--no-candidate"])
    return json.loads(sorted(out.glob("scenario_results_*.json"))[-1].read_text(encoding="utf-8"))


def test_the_submitted_module_decides_what_the_plan_module_decides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from m08.make_snapshot import main as build

    assert build(["--snapshot", str(tmp_path / "snapshot")]) == 0, "the builder refuses while the scenarios fail"
    in_plan = decisions(run_scenarios_here(tmp_path / "plan_out", monkeypatch))

    monkeypatch.setattr(paths, "SNAPSHOT", tmp_path / "snapshot")
    monkeypatch.setenv(paths.MODE_ENV, "1")
    assert paths.snapshot_mode()
    in_snapshot = decisions(run_scenarios_here(tmp_path / "snapshot_out", monkeypatch))

    assert set(in_snapshot) == set(in_plan)
    for scenario_id, decision in in_plan.items():
        assert in_snapshot[scenario_id] == decision, f"{scenario_id} differs between the plan and the snapshot"
