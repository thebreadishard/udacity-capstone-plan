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
from docx import Document

MODULE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE))
import run_scenarios  # noqa: E402
from m08 import paths, prices, stored_run  # noqa: E402
from m08 import pipeline as P  # noqa: E402
from m08.catalog import Catalog  # noqa: E402
from m08.certify import ANCHOR_REGISTRY, PRICED_ANCHORS, PRICED_EVIDENCE, anchor_cost_lines, carried_anchor, certificate, to_markdown  # noqa: E402
from m08.officer import CATION_NEEDED, Request, decide  # noqa: E402
from m08.replay import execute_run_order  # noqa: E402
from m08.scenario_kinds import ADDED_CASES, MECHANICAL_CHECKS, PRE_REGISTERED_REQUESTS, request_kinds  # noqa: E402
from m08.seen import CATION_LAYER  # noqa: E402


@pytest.fixture(scope="module")
def cat() -> Catalog:
    return Catalog()


def test_s5_is_recorded_from_what_the_catalogue_builder_reports() -> None:
    """A clean build has an empty list of problems and its molecule count; a broken invariant is its INVARIANT lines; a build
    that stopped without one names its last stderr line; a build that exits 0 without a readable summary, or beside an
    INVARIANT line, is refused (20 Nov 2026: the record held problems=null)."""
    record = run_scenarios.s5_record
    clean = record(0, 'note\n{"n_molecules": 14258, "built_utc": "x"}', "", 42)
    assert clean["problems"] == [] and clean["n_molecules"] == 14258 and clean["exit_code"] == 0
    broken = record(1, "", "INVARIANT: rung counts do not add up\nINVARIANT: catalog id without a manifest row\nother", 3)
    assert broken["problems"] == ["rung counts do not add up", "catalog id without a manifest row"] and broken["n_molecules"] is None
    crashed = record(1, "", "Traceback (most recent call last):\n  File x\nSystemExit: evidence file missing a.json\n\n", 2)
    assert crashed["problems"] == ["build_catalog.py stopped with exit code 1: SystemExit: evidence file missing a.json"]
    assert record(3, "", "", 1)["problems"] == ["build_catalog.py stopped with exit code 3: nothing on stderr"]
    with pytest.raises(RuntimeError, match="without printing its summary"):
        record(0, "no json here", "", 1)
    with pytest.raises(RuntimeError, match="exited 0 beside 1 INVARIANT"):
        record(0, '{"n_molecules": 1}', "INVARIANT: x", 1)
    for unreadable in ('{"built_utc": "x"}', '{"n_molecules": 1} trailing', "{not json"):
        with pytest.raises(RuntimeError, match="printed summary cannot be read"):
            record(0, unreadable, "", 1)


def test_a_failing_s5_fails_the_run_and_is_never_the_submitted_record(tmp_path: Path) -> None:
    """The request scenarios can all pass while the catalogue's check fails: that run is a failing run."""
    s5 = run_scenarios.s5_record(1, "", "INVARIANT: rung counts do not add up", 3)
    rec = dict(n_pass=8, n_scenarios=8, mechanical={"S5": s5})
    assert run_scenarios.run_failure(rec) == "S5 failed (build_catalog.py exit 1, 1 problem(s))"
    with pytest.raises(RuntimeError, match=r"S5 failed .*is not written from a failing run"):
        run_scenarios.write_records(rec, tmp_path, submitted=True)
    assert not (tmp_path / run_scenarios.SUBMITTED).exists() and len(list(tmp_path.glob("scenario_results_2*.json"))) == 1
    assert run_scenarios.run_failure(dict(n_pass=8, n_scenarios=8, mechanical={})) is None
    assert run_scenarios.run_failure(dict(n_pass=7, n_scenarios=8, mechanical={})) == "7 of 8 scenarios pass"
    assert run_scenarios.run_failure(dict(n_pass=8, n_scenarios=8, mechanical={"S5": run_scenarios.s5_record(0, '{"n_molecules": 2}', "", 1)})) is None


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
    lines = anchor_cost_lines("benzene", row["evidence"], entry)
    assert len(lines) == 1
    line = lines[0]
    assert entry["level"] in line["step"] and entry["date"] in line["step"] and entry["kind"] in line["step"]
    assert line["eur_ex_vat"] is None and line["hours"] is None
    assert ANCHOR_REGISTRY in line["source"] and entry["path"] in line["source"]


def test_an_anchored_molecule_without_a_registry_entry_is_refused_by_name() -> None:
    with pytest.raises(ValueError, match="biphenyl is at the anchored rung, but the anchor registry"):
        anchor_cost_lines("biphenyl", [], None)


def test_a_priced_evidence_page_gives_one_line_with_the_price_tables_numbers(cat: Catalog) -> None:
    """The line's label, hours and source are one reading's: the page the export names and the price table's entry for it."""
    row = cat.find("naphthalene")
    priced = [page for page in row["evidence"] if page in PRICED_EVIDENCE]
    assert len(priced) == 1, "naphthalene's export names one M3 reading page today; the test reads its line"
    reading, *in_force = anchor_cost_lines("naphthalene", row["evidence"], carried_anchor(row["id"], row["name"]))
    step = prices.step_price(PRICED_EVIDENCE[priced[0]])
    assert reading["step"].endswith(Path(priced[0]).name) and "one family" in reading["step"] and "two families" not in reading["step"]
    assert reading["hours"] == step["hours"] and reading["eur_ex_vat"] == step["eur_ex_vat"] and reading["source"] == step["source"]
    assert in_force and all(line["step"].startswith("anchor in force: ") for line in in_force)


def test_the_priced_line_follows_the_evidence_not_the_molecules_name(cat: Catalog) -> None:
    row = cat.find("benzene")
    entry = carried_anchor(row["id"], row["name"])
    page = next(iter(PRICED_EVIDENCE))
    assert len(anchor_cost_lines("benzene", [*row["evidence"], page], entry)) == 2
    naphthalene = cat.find("naphthalene")
    without = [p for p in naphthalene["evidence"] if p not in PRICED_EVIDENCE]
    assert len(anchor_cost_lines("naphthalene", without, carried_anchor(naphthalene["id"], naphthalene["name"]))) == len(prices.ANCHOR_PARTS)


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


def test_the_facts_the_cation_refusal_states_hold(tmp_path: Path) -> None:
    """Each clause of the refusal is read from where it is true, so the sentence fails here the day a fact changes: the corpus
    holds cation rows, not all of them are computed, the pipeline takes neutral closed-shell input only, and the registry carries
    no cation anchor."""
    with paths.resolve("modules/05_support_predictor/corpus/manifest.csv").open(encoding="utf-8", newline="") as fh:
        cations = [row for row in csv.DictReader(fh) if row["layer"] == CATION_LAYER]
    assert cations, "the corpus holds cation rows"
    assert [row for row in cations if row["status"] != "done"], "'not all computed yet' (CATION_NEEDED)"
    with pytest.raises(ValueError, match="neutral closed-shell"):
        P.PipelineConfig(name="cation", out_root=tmp_path, smiles="c1ccccc1", charge=1, multiplicity=2, psi4_python=Path(sys.executable))
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
    # the licence is about ω; a band printed as ν shows the step's own bar beside it, read from the record
    stepped = next(b for b in record["bands"] if b["step_bar_cm"] is not None and b["km_mol"] == strongest)
    row = next(r for r in rows if r["height (km/mol)"] == strongest)
    assert row["ν: the step's error bar"] == stepped["step_bar_cm"] and "ω licensed" in row


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
    """The record on disk, with the price table as it stands: the paper's price sentences are tested on today's table, and
    test_the_record_on_disk_holds_the_tables_prices says whether the record is behind it."""
    record = json.loads((MODULE / "notebook" / "results.json").read_text(encoding="utf-8"))
    record["prices"] = json.loads(json.dumps(prices.table_record()))
    return record


def test_the_record_on_disk_holds_the_tables_prices() -> None:
    on_disk = json.loads((MODULE / "notebook" / "results.json").read_text(encoding="utf-8"))["prices"]
    assert on_disk == json.loads(json.dumps(prices.table_record())), \
        "the price table changed after the notebook wrote results.json: rebuild the notebook, then the paper"


def test_the_paper_states_the_anchors_price_as_the_table_has_it(summary: ModuleType, results: dict) -> None:
    anchor = prices.anchor_price()
    text = _text(summary, results)
    assert f"took {anchor['hours']:.1f} machine-hours on rented servers ({anchor['eur_ex_vat']:.0f} € before tax)" in text
    assert "42.5" not in text and "28 September. The cheap" not in text and "one run in September" not in text


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


def _text(summary: ModuleType, record: dict) -> str:
    return " ".join(block[1] for block in summary.blocks(record) if block[0] == "para")


def test_the_paper_builds_from_todays_results_with_headroom(summary: ModuleType, results: dict) -> None:
    """Thirty words of headroom: the final run's record has a longer S3 source line and an S5 sentence."""
    paper = summary.blocks(results)
    assert summary.WORD_RANGE[0] <= summary.checked_words(paper) <= summary.WORD_RANGE[1] - 30
    text = _text(summary, results)
    assert f"rule table of {results['n_rules']} rules" in text
    assert results["s2"]["request"]["molecule"] in text
    assert f"version {results['pipeline_version']}" in text
    for stale in ("1,200", "layer-B", "live worker would", "azulene", "this week", "honest", "transferable", "not yet run"):
        assert stale not in text


def test_the_paper_says_which_requests_passed_and_reports_the_mechanical_checks_apart(summary: ModuleType, results: dict) -> None:
    scenarios = results["scenarios"]
    sentence = summary.scenario_sentences(scenarios, results["outcome"])
    assert f"{len(scenarios['registered_ids'])} pre-registered ({', '.join(scenarios['registered_ids'])})" in sentence
    assert f"{len(scenarios['added_ids'])} added cases ({', '.join(scenarios['added_ids'])})" in sentence
    assert not {"S5", "S6", "S7"} & set(scenarios["registered_ids"] + scenarios["added_ids"])
    assert f"{results['outcome']['n_unpriced']} anchor line" in sentence and "shown as not priced" in sentence
    assert "1 anchor line is shown as not priced" in summary.scenario_sentences(scenarios, results["outcome"] | dict(n_unpriced=1))
    assert "2 anchor lines are shown as not priced" in summary.scenario_sentences(scenarios, results["outcome"] | dict(n_unpriced=2))
    assert scenarios["mechanical"]["S6"]["status"] in sentence
    with_s5 = json.loads(json.dumps(scenarios))
    with_s5["mechanical"]["S5"] = dict(exit_code=0, problems=[])
    clean = summary.scenario_sentences(with_s5, results["outcome"])
    assert "S5, the catalogue's consistency check, found no problems." in clean and "[" not in clean
    for failing in (dict(exit_code=1, problems=[]), dict(exit_code=0, problems=["a", "b"]), dict(exit_code=0, problems=None)):
        with pytest.raises(ValueError, match="S5 did not pass"):
            summary.s5_sentence({"S5": failing})
    assert "was not part of this run" in summary.scenario_sentences({**with_s5, "mechanical": {k: v for k, v in with_s5["mechanical"].items()
                                                                                             if k != "S5"}}, results["outcome"])


def test_the_request_kinds_are_named_and_a_record_with_other_requests_is_refused(results: dict) -> None:
    ids = list(PRE_REGISTERED_REQUESTS + ADDED_CASES)
    assert request_kinds(ids) == (list(PRE_REGISTERED_REQUESTS), list(ADDED_CASES))
    assert (results["scenarios"]["registered_ids"], results["scenarios"]["added_ids"]) == request_kinds(
        [row["id"] for row in results["scenarios"]["table"]])
    with pytest.raises(ValueError, match=r"missing \['S4c'\]"):
        request_kinds(ids[:-1])
    with pytest.raises(ValueError, match=r"neither pre-registered nor added \['S9'\]"):
        request_kinds([*ids, "S9"])
    scenarios = json.loads((MODULE / "scenarios" / "scenarios.json").read_text(encoding="utf-8"))
    assert request_kinds([s["id"] for s in scenarios["scenarios"]])[1] == list(ADDED_CASES)
    assert {m["id"] for m in scenarios["mechanical"]} == set(MECHANICAL_CHECKS)
    assert "S2b, S4b and S4c are added cases" in (MODULE / "PRE_REGISTRATION.md").read_text(encoding="utf-8").splitlines()[10]


def test_the_paper_states_the_anharmonic_bars_from_the_record(summary: ModuleType, results: dict) -> None:
    step = results["pipeline_run"]["anharmonic"]
    sentence = summary.anharmonic_sentence(step, results["licence"]["line_cm"])
    for family, bar in step["bars_cm"].items():
        assert f"{bar:.2f} ({family})" in sentence
    assert f"{len(step['bars_cm'])} families" in sentence and " and ".join(step["target_molecules"]) in sentence
    assert "no anharmonic position is claimed" in sentence
    one_passes = {**step, "bars_cm": {**step["bars_cm"], "ring-ip": 1.0}}
    assert "Only ring-ip is within" in summary.anharmonic_sentence(one_passes, results["licence"]["line_cm"])


def test_the_paper_says_what_the_stored_run_is_evidence_of(summary: ModuleType, results: dict) -> None:
    run = results["pipeline_run"]
    sentence = summary.stored_run_sentence(run)
    assert f"written by version {run['pipeline_version']}" in sentence
    assert ("was written before" if not run["has_own_spread"] else "carries") in sentence
    assert "release networks' training data" in summary.stored_run_sentence({**run, "seen": dict(role="release_trained", text="-")})
    assert "the text of the record" in summary.stored_run_sentence({**run, "seen": dict(role="unseen", text="the text of the record")})


@pytest.mark.parametrize("path", [("catalogue", "rung_counts", "anchored"), ("scenarios", "results_env_set"), ("outcome",),
                                  ("pipeline_run", "anharmonic", "bars_cm"), ("prices", "steps", "cheap_deck_v1")])
def test_a_record_without_a_key_fails_the_papers_build(summary: ModuleType, results: dict, path: tuple[str, ...]) -> None:
    broken = json.loads(json.dumps(results))
    inner = broken
    for key in path[:-1]:
        inner = inner[key]
    del inner[path[-1]]
    with pytest.raises(KeyError, match=path[-1]):
        summary.interim_reasons(broken)
        summary.blocks(broken)


def test_neither_builder_defaults_a_records_key() -> None:
    """A `.get(key, default)` on a record printed a zero for a count the export no longer had; the builders index instead."""
    builder = _builder("m08_make_notebook", MODULE / "notebook" / "make_notebook.py")
    for kind, text in builder.CELLS:
        if kind == "code":
            assert ".get(" not in text, text.splitlines()[0]
    assert ".get(" not in (MODULE / "make_summary.py").read_text(encoding="utf-8")


def test_an_outcome_the_record_does_not_show_stops_the_paper(summary: ModuleType, results: dict) -> None:
    for claim in results["outcome"]["claims"]:
        broken = json.loads(json.dumps(results))
        broken["outcome"]["claims"][claim] = False
        with pytest.raises(ValueError, match="outcomes the record does not show"):
            summary.blocks(broken)


def test_an_interim_record_is_named_and_refused_without_the_flag(summary: ModuleType, results: dict, tmp_path: Path,
                                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    final = json.loads(json.dumps(results))
    final["scenarios"].update(written_by="run_scenarios.py --with-catalog --submitted", results_env_set=False, results_dir="out")
    final["scenarios"]["mechanical"]["S5"] = dict(exit_code=0, problems=[])
    assert summary.interim_reasons(final) == []
    for change, word in ((dict(written_by="run_scenarios.py --no-candidate"), "fixed candidate"), (dict(results_env_set=True), "M08_SCENARIO_RESULTS")):
        interim = json.loads(json.dumps(final))
        interim["scenarios"].update(change)
        assert word in " ".join(summary.interim_reasons(interim))
    no_s5 = json.loads(json.dumps(final))
    del no_s5["scenarios"]["mechanical"]["S5"]
    assert "no S5" in " ".join(summary.interim_reasons(no_s5))
    record = tmp_path / "results.json"
    record.write_text(json.dumps(no_s5), encoding="utf-8")
    monkeypatch.setattr(summary, "RESULTS", record)
    with pytest.raises(SystemExit, match="not the final run's record"):
        summary.main(["--no-pdf", "--out", str(tmp_path / "paper.docx")])
    record.write_text(json.dumps(final), encoding="utf-8")
    with pytest.raises(SystemExit, match="is the final run's record"):
        summary.main(["--interim", "--no-pdf", "--out", str(tmp_path / "paper.docx")])
    assert not list(tmp_path.glob("*.docx"))


def test_the_docx_is_written_whole_under_the_authors_name(summary: ModuleType, results: dict, tmp_path: Path) -> None:
    out = tmp_path / "paper.docx"
    summary.write_docx(summary.blocks(results), out)
    properties = Document(str(out)).core_properties
    assert properties.author == properties.last_modified_by == summary.AUTHOR
    assert summary.AUTHOR in summary.blocks(results)[2][1]
    assert [p.name for p in tmp_path.iterdir()] == ["paper.docx"], "a temp file was left beside the paper"


def test_the_notebook_builder_writes_through_a_temp_file_where_it_is_told(tmp_path: Path) -> None:
    builder = _builder("m08_make_notebook", MODULE / "notebook" / "make_notebook.py")
    before = (MODULE / "notebook" / "results.json").read_bytes()
    builder.build(tmp_path / "elsewhere.ipynb", run=False)
    assert [p.name for p in tmp_path.iterdir()] == ["elsewhere.ipynb"]
    assert len(nbformat.read(tmp_path / "elsewhere.ipynb", as_version=4).cells) == len(builder.CELLS)
    imports = next(text for kind, text in builder.CELLS if kind == "code")
    assert f'os.environ["{builder.OUT_ENV}"]' in imports, "the cells write results.json and figures where the builder says"
    assert (MODULE / "notebook" / "results.json").read_bytes() == before


def test_the_submitted_record_needs_the_whole_run() -> None:
    for argv in (["--submitted"], ["--submitted", "--with-catalog", "--no-candidate"]):
        with pytest.raises(SystemExit) as refused:
            run_scenarios.main(argv)
        assert refused.value.code == 2


def test_the_submitted_record_is_written_under_its_fixed_name_and_never_from_a_failing_run(tmp_path: Path) -> None:
    passing = dict(n_pass=8, n_scenarios=8, mechanical={})
    dated = run_scenarios.write_records(passing, tmp_path, submitted=True)
    assert json.loads((tmp_path / run_scenarios.SUBMITTED).read_text(encoding="utf-8")) == passing
    assert dated.name.startswith("scenario_results_2") and sorted(p.name for p in tmp_path.iterdir()) == sorted([dated.name, run_scenarios.SUBMITTED])
    failing = tmp_path / "failing"
    failing.mkdir()
    with pytest.raises(RuntimeError, match="not written from a failing run"):
        run_scenarios.write_records(dict(n_pass=7, n_scenarios=8, mechanical={}), failing, submitted=True)
    assert [p.name for p in failing.iterdir()] == [dated.name]
    plain = tmp_path / "plain"
    plain.mkdir()
    run_scenarios.write_records(passing, plain, submitted=False)
    assert [p.name for p in plain.iterdir()] == [dated.name]


def test_the_submission_list_names_the_submitted_record_as_an_entry() -> None:
    """A listed path the module does not hold stops tools/make_module_repo.sh, so the final run cannot be forgotten."""
    lines = [line.split("#")[0].strip() for line in (MODULE / "SUBMISSION.txt").read_text(encoding="utf-8").splitlines()]
    assert f"out/{run_scenarios.SUBMITTED}" in lines


def test_the_papers_numbers_follow_the_record(summary: ModuleType, results: dict) -> None:
    changed = json.loads(json.dumps(results))
    changed["n_rules"] = 7
    changed["licence"]["licensed_families"] = [f for f in changed["licence"]["licensed_families"] if f != "other"]
    changed["licence"]["errors"]["other"] = {"a": 3.5, "b": 3.9}
    text = _text(summary, changed)
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


def test_the_anchor_in_force_is_priced_where_the_table_priced_its_runs(cat: Catalog) -> None:
    """Naphthalene's composite is the run the table read from its logs: one line per part, each on its machine, summing to the table's anchor."""
    row = cat.find("naphthalene")
    entry = carried_anchor(row["id"], row["name"])
    in_force = [line for line in anchor_cost_lines("naphthalene", row["evidence"], entry) if line["step"].startswith("anchor in force")]
    parts = [prices.step_price(step) for _, step in prices.ANCHOR_PARTS]
    assert [(line["machine"], line["hours"], line["eur_ex_vat"]) for line in in_force] == [(p["machine"], p["hours"], p["eur_ex_vat"]) for p in parts]
    assert round(sum(line["eur_ex_vat"] for line in in_force), 2) == prices.anchor_price()["eur_ex_vat"]
    for line, part in zip(in_force, parts, strict=True):
        assert entry["level"] in line["step"] and line["note"] == part["note"]
        assert entry["path"] in line["source"] and entry["sha16"] in line["source"] and part["source"] in line["source"]
    honesty = run_scenarios.cost_honesty([dict(molecule=dict(name="naphthalene"), cost_record=in_force)])
    assert honesty["lines_traced"] == honesty["lines_checked"] == len(parts) and not honesty["misses"]


def test_every_priced_anchor_is_a_carried_composite_of_the_registry() -> None:
    """The price follows the registry's file: a key the registry does not carry, or carries for another route, would price the wrong run."""
    registry = json.loads((MODULE.parents[1] / ANCHOR_REGISTRY).read_text(encoding="utf-8"))["anchors"]
    assert list(PRICED_ANCHORS) == [(prices.ANCHOR_REGISTRY_ENTRY["path"], prices.ANCHOR_REGISTRY_ENTRY["sha16"])]
    for path, sha16 in PRICED_ANCHORS:
        entry = [e for e in registry if e["path"] == path and e["sha16"] == sha16]
        assert len(entry) == 1 and entry[0]["status"] == "carried" and entry[0]["kind"] == "composite", path
        assert entry[0]["level"] == "CCSD(T)/cc-pVDZ + [MP2/cc-pVTZ − MP2/cc-pVDZ]", "the table's parts are this route's"


def test_an_anchor_whose_runs_the_table_does_not_price_stays_unpriced(cat: Catalog) -> None:
    row = cat.find("benzene")
    entry = carried_anchor(row["id"], row["name"])
    (line,) = anchor_cost_lines("benzene", [], entry)
    assert (entry["path"], entry["sha16"]) not in PRICED_ANCHORS and line["eur_ex_vat"] is None and "not priced" in line["source"]
    same_route_other_run = entry | dict(level="CCSD(T)/cc-pVDZ + [MP2/cc-pVTZ − MP2/cc-pVDZ]", kind="composite")
    assert anchor_cost_lines("pyridine", [], same_route_other_run)[0]["eur_ex_vat"] is None, "a route is not a price: only the priced run is"


def test_a_file_rebuilt_under_the_priced_anchors_name_is_not_priced(cat: Catalog) -> None:
    """The price is of the runs behind one file: the same path with another digest is another anchor, and nobody read its logs."""
    row = cat.find("naphthalene")
    entry = carried_anchor(row["id"], row["name"])
    assert (entry["path"], entry["sha16"]) in PRICED_ANCHORS
    (line,) = anchor_cost_lines("naphthalene", [], entry | dict(sha16="0" * 16))
    assert line["eur_ex_vat"] is None and line["hours"] is None and "not priced" in line["source"]


def test_the_paper_says_which_certificate_carries_its_anchors_price(summary: ModuleType, results: dict, cat: Catalog) -> None:
    """On a record where naphthalene's line is priced and benzene's is not, and on one where neither is: the sentence follows the record."""
    row = cat.find("naphthalene")
    today = json.loads(json.dumps(results))
    today["s1"]["cost"] = anchor_cost_lines("naphthalene", row["evidence"], carried_anchor(row["id"], row["name"]))
    sentence = summary.anchor_price_sentence(today)
    assert "attempt; the certificate of naphthalene carries it, benzene shows its anchor unpriced." in sentence
    neither = json.loads(json.dumps(today))
    neither["s1"]["cost"] = [dict(step="anchor in force: x", eur_ex_vat=None)]
    assert "attempt; naphthalene and benzene show their anchors unpriced." in summary.anchor_price_sentence(neither)
    neither["s1"]["cost"] = []
    with pytest.raises(ValueError, match="no 'anchor in force' cost line for s1"):
        summary.anchor_price_sentence(neither)
