"""What the submitted texts and records read instead of typing (20 November 2026).

The module's notebook, paper and certificates had drifted from the project's state because numbers and statuses were typed where a
record holds them: S6 "not run", a benzene anchor run the registry marks invalid, a rule count. Each test here holds one of those
reads in place.

    python -m pytest modules/08_industry_synthesis/tests/test_m08_submission.py -q
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import nbformat
import pytest

MODULE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE))
import run_scenarios  # noqa: E402
from m08 import paths, stored_run  # noqa: E402
from m08.catalog import Catalog  # noqa: E402
from m08.certify import ANCHOR_REGISTRY, anchor_cost_lines, carried_anchor, certificate, to_markdown  # noqa: E402
from m08.officer import CATION_NEEDED, Request, decide  # noqa: E402
from m08.replay import execute_run_order  # noqa: E402
from m08.seen import CATION_LAYER  # noqa: E402


@pytest.fixture(scope="module")
def cat() -> Catalog:
    return Catalog()


def test_s6_status_is_the_verdict_of_its_record() -> None:
    record = json.loads(run_scenarios.S6_RECORD.read_text(encoding="utf-8"))
    status = run_scenarios.s6_status()
    assert record["published_site_after_fixes"]["verdict"] in status["status"]
    assert record["date"] in status["status"]
    assert status["pass_line"] == record["pass_line"]
    assert status["record"] == "out/s6_accessibility_2026-10-11.json"


def test_s6_status_follows_another_record_and_refuses_without_one(tmp_path: Path) -> None:
    other = tmp_path / "s6.json"
    other.write_text(json.dumps(dict(date="2030-01-01", pass_line="none", published_site_after_fixes=dict(verdict="S6 fails here"))),
                     encoding="utf-8")
    assert run_scenarios.s6_status(other)["status"].startswith("S6 fails here (run 2030-01-01")
    with pytest.raises(FileNotFoundError, match="never typed"):
        run_scenarios.s6_status(tmp_path / "absent.json")


def test_the_anchor_cost_line_quotes_the_registry_entry(cat: Catalog) -> None:
    row = cat.find("benzene")
    entry = carried_anchor(row["id"], row["name"])
    lines = anchor_cost_lines("benzene", entry)
    assert len(lines) == 1
    line = lines[0]
    assert entry["level"] in line["step"] and entry["date"] in line["step"] and entry["kind"] in line["step"]
    assert line["eur_ex_vat"] is None and line["hours"] is None
    assert ANCHOR_REGISTRY in line["source"] and entry["path"] in line["source"]


def test_a_molecule_without_an_entry_gets_no_anchor_line() -> None:
    assert anchor_cost_lines("biphenyl", None) == []


def test_naphthalene_keeps_its_priced_family_readings_beside_the_registry_line(cat: Catalog) -> None:
    row = cat.find("naphthalene")
    readings, in_force = anchor_cost_lines("naphthalene", carried_anchor(row["id"], row["name"]))
    assert readings["eur_ex_vat"] is not None and "registry" in readings["note"]
    assert in_force["step"].startswith("anchor in force: ")


@pytest.mark.parametrize("name", ["benzene", "naphthalene"])
def test_a_certificate_names_no_september_anchor_run_and_no_replaced_rule(cat: Catalog, name: str) -> None:
    cert = certificate(cat.find(name), cat)
    text = json.dumps(cert, ensure_ascii=False) + to_markdown(cert)
    for stale in ("72 gradients", "is computing", "Proof_of_Learning_Layer_B", "| None |"):
        assert stale not in text, f"{name}'s certificate still says {stale!r}"
    assert cert["provenance"]["pre_registrations"] == ["modules/08_industry_synthesis/PRE_REGISTRATION.md"]
    assert cert["provenance"]["licence"]["rule_source"].startswith("README.md, decision 65")
    honesty = run_scenarios.cost_honesty([cert])
    assert honesty["lines_traced"] == honesty["lines_checked"] == len(cert["cost_record"]) and not honesty["misses"]


def test_the_worker_promises_no_live_worker(cat: Catalog) -> None:
    done = execute_run_order(dict(molecule_id=None, gate=dict(approved=True)), cat)
    assert done["queued"] and not done["executed"] and done["machine_touched"] is False
    assert "would provision" not in done["reason"] and "no live worker" in done["reason"]


def test_the_cation_refusal_says_what_is_true_today(cat: Catalog) -> None:
    refusal = decide(Request(molecule="naphthalene", target_rung=4, charge=1, multiplicity=2), cat)
    assert refusal.kind == "refusal" and "cation rung closed" in refusal.gate_named
    assert refusal.what_would_be_needed == CATION_NEEDED
    assert f"layer {CATION_LAYER} of its manifest" in refusal.reasons[0]
    assert "anchor plan" not in refusal.ledger_line


def test_the_facts_the_cation_refusal_states_hold() -> None:
    """The sentence says the corpus holds cation rows and the registry carries no cation anchor; both are read here."""
    with paths.resolve("modules/05_support_predictor/corpus/manifest.csv").open(encoding="utf-8", newline="") as fh:
        layers = {row["layer"] for row in csv.DictReader(fh)}
    assert CATION_LAYER in layers
    registry = json.loads(paths.resolve(ANCHOR_REGISTRY).read_text(encoding="utf-8"))["anchors"]
    carried = [e["name"] for e in registry if e["status"] == "carried"]
    assert carried and not [n for n in carried if "+" in n or "⁺" in n or "cation" in n]


def test_the_stored_run_is_a_pipeline_certificate_of_the_carried_network() -> None:
    record = stored_run.certificate()
    assert record["kind"] == stored_run.KIND and record["pipeline_version"]
    assert record["network"]["kind"] == "release"
    rows = stored_run.band_rows(record, strongest=5)
    assert len(rows) == 5
    assert [r["printed (cm⁻¹)"] for r in rows] == sorted(r["printed (cm⁻¹)"] for r in rows)
    strongest = max(b["km_mol"] for b in record["bands"])
    assert strongest in [r["height (km/mol)"] for r in rows]


def test_the_stored_run_refuses_another_kind_of_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / stored_run.CERTIFICATE).write_text(json.dumps(dict(kind="certificate")), encoding="utf-8")
    monkeypatch.setattr(paths, "resolve", lambda relative: tmp_path / Path(relative).name)
    with pytest.raises(ValueError, match="not a pipeline certificate"):
        stored_run.certificate("anywhere")


def test_band_rows_refuses_no_bands() -> None:
    with pytest.raises(ValueError, match="at least one band"):
        stored_run.band_rows(dict(bands=[]), strongest=0)


def _builder(name: str, path: Path) -> ModuleType:
    """A builder script loaded as a module: neither is a package, and neither runs anything on import."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def summary() -> ModuleType:
    return _builder("m08_make_summary", MODULE / "make_summary.py")


@pytest.fixture(scope="module")
def results() -> dict:
    return json.loads((MODULE / "notebook" / "results.json").read_text(encoding="utf-8"))


def test_the_notebook_on_disk_is_the_builders_and_ran_whole() -> None:
    builder = _builder("m08_make_notebook", MODULE / "notebook" / "make_notebook.py")
    on_disk = nbformat.read(builder.NOTEBOOK, as_version=4)
    kinds = {"md": "markdown", "code": "code"}
    assert [(c.cell_type, c.source) for c in on_disk.cells] == [(kinds[kind], text) for kind, text in builder.CELLS], \
        "the notebook was not rebuilt after its builder changed: python notebook/make_notebook.py"
    for cell in on_disk.cells:
        if cell.cell_type == "code":
            assert cell.execution_count is not None, "a code cell was not executed"
            assert not [o for o in cell.outputs if o.output_type == "error"]


def test_the_notebook_names_the_scenarios_molecule_from_the_scenario_file() -> None:
    """S2's molecule changed on 14 Nov 2026 (azulene was anchored) and the notebook kept asking for azulene, typed in a cell."""
    builder = _builder("m08_make_notebook", MODULE / "notebook" / "make_notebook.py")
    scenarios = json.loads((MODULE / "scenarios" / "scenarios.json").read_text(encoding="utf-8"))["scenarios"]
    molecule = next(s for s in scenarios if s["id"] == "S2")["request"]["molecule"]
    cells = "\n".join(text for _, text in builder.CELLS)
    assert molecule not in cells and "azulene" not in cells


def test_the_paper_builds_from_todays_results_inside_the_word_range(summary: ModuleType, results: dict) -> None:
    paper = summary.blocks(results)
    assert summary.WORD_RANGE[0] <= summary.checked_words(paper) <= summary.WORD_RANGE[1]
    text = " ".join(block[1] for block in paper if block[0] == "para")
    assert f"rule table of {results['n_rules']} rules" in text
    assert results["s2"]["request"]["molecule"] in text
    assert f"version {results['pipeline_version']}" in text
    for stale in ("1,200", "layer-B", "live worker would", "azulene", "this week"):
        assert stale not in text


def test_the_papers_numbers_follow_the_record(summary: ModuleType, results: dict) -> None:
    changed = json.loads(json.dumps(results))
    changed["n_rules"] = 7
    changed["licence"]["licensed_families"] = [f for f in changed["licence"]["licensed_families"] if f != "other"]
    changed["licence"]["errors"]["other"] = {"a": 3.5, "b": 3.9}
    text = " ".join(block[1] for block in summary.blocks(changed) if block[0] == "para")
    n_families = len(changed["licence"]["errors"])
    assert "rule table of 7 rules" in text
    assert f"{n_families - 1} of {n_families} families are licensed" in text and "other is not" in text


def test_the_licence_sentence_says_when_nothing_is_licensed(summary: ModuleType) -> None:
    sentence = summary.licence_sentence(dict(licensed_families=[], errors={"other": {"a": 4.0, "b": 4.0}}), "9.9")
    assert "no family is licensed" in sentence and "9.9" in sentence


def test_the_paper_refuses_a_body_outside_the_range(summary: ModuleType) -> None:
    with pytest.raises(ValueError, match="not written"):
        summary.checked_words([("para", "too short")])


def test_the_paper_refuses_to_describe_a_failure_case_that_is_gone(summary: ModuleType) -> None:
    with pytest.raises(ValueError, match="failure case"):
        summary.failure_sentence([dict(family="CH-oop", wider_than_tolerance=False)])
