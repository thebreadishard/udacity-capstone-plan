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


def run_scenarios_here(out: Path) -> dict[str, Any]:
    """The scenarios in this process, writing into `out` rather than the module's own folder, and their results record."""
    import run_scenarios as scenarios

    scenarios.main(["--no-candidate", "--out", str(out)])
    records = sorted(out.glob("scenario_results_*.json"))
    if not records or not any((out / "certificates").iterdir()):
        pytest.fail(f"run_scenarios --out {out} wrote no results record or no certificate there")
    return json.loads(records[-1].read_text(encoding="utf-8"))


def tree_bytes(folder: Path) -> dict[str, bytes]:
    """Every file under `folder` with its bytes: two calls compare equal only when nothing was written, added or removed."""
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def test_the_submitted_module_decides_what_the_plan_module_decides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from m08.make_snapshot import main as build

    module_out = tree_bytes(MODULE / "out")
    build_out = tmp_path / "build_out"
    assert build(["--snapshot", str(tmp_path / "snapshot"), "--out", str(build_out)]) == 0, \
        "the builder refuses while the scenarios fail"
    assert sorted(build_out.glob("scenario_results_*.json")), "the builder's scenarios did not write into --out"
    in_plan = decisions(run_scenarios_here(tmp_path / "plan_out"))

    monkeypatch.setattr(paths, "SNAPSHOT", tmp_path / "snapshot")
    monkeypatch.setenv(paths.MODE_ENV, "1")
    assert paths.snapshot_mode()
    in_snapshot = decisions(run_scenarios_here(tmp_path / "snapshot_out"))

    assert set(in_snapshot) == set(in_plan)
    for scenario_id, decision in in_plan.items():
        assert in_snapshot[scenario_id] == decision, f"{scenario_id} differs between the plan and the snapshot"
    assert tree_bytes(MODULE / "out") == module_out, "the suite wrote into the module's tracked out/"


def test_the_output_folder_does_not_change_what_the_snapshot_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The snapshot holds what the scenarios read; moving where they write must not add, drop or move a recorded file.

    The run without `--out` takes run_scenarios' default route, with that default pointed at a temporary folder so the module's
    tracked out/ stays as it is."""
    import run_scenarios as scenarios
    from m08.make_snapshot import Recorder, run_scenarios

    monkeypatch.setattr(scenarios, "OUT", tmp_path / "default_out")
    by_default = Recorder()
    assert run_scenarios(by_default) == 0
    by_default_plan, by_default_repo = set(by_default.plan), set(by_default.repo)
    assert sorted((tmp_path / "default_out").glob("scenario_results_*.json")), "the default route did not write its record"

    module_out = tree_bytes(MODULE / "out")
    with_option = Recorder()
    assert run_scenarios(with_option, tmp_path / "option_out") == 0
    assert tree_bytes(MODULE / "out") == module_out, "with an output folder given, the scenarios still wrote into the module's out/"
    assert with_option.plan == by_default_plan
    assert with_option.repo == by_default_repo
    assert by_default_plan, "the recorder saw no plan file: the comparison would hold vacuously"
