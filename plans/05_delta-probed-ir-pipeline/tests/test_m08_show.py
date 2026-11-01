"""The pipeline show (`modules/08_industry_synthesis/m08/show.py`, TASKS 146): every number on the page comes from a result folder's records
— the stations' times from `pipeline.json`, the families' errors and licences from `certificate.json`, the curves from the folder's arrays
— and the page carries the data once. The two runs without a corpus truth (module 06's candidate, cinnoline) are read on every machine;
the whole default set where the corpus holds the truth Hessians."""
from __future__ import annotations

import json
import sys

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import show as S

NO_TRUTH = (S.RESULTS / "pipeline_demo_v04_2026-10-30" / "candidate06", S.RESULTS / "pipeline_rehearsal_2026-10-30" / "cinnoline")


def record(folder):
    return json.loads((folder / "pipeline.json").read_text(encoding="utf-8")), json.loads((folder / "certificate.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("seconds, text", [(2.8, "2.8 s"), (30.5, "30 s"), (61, "1 min"), (3212, "54 min"), (4700, "1.3 h")])
def test_durations_read_as_people_read_them(seconds, text):
    assert S.duration(seconds) == text


@pytest.mark.parametrize("formula, n", [("C6H6", 6), ("C14H10", 14), ("C13H10F3NO3", 13), ("CH4", 1), ("C12H9N", 12)])
def test_carbon_count(formula, n):
    assert S.carbon_count(formula) == n


def test_a_record_before_the_reuse_step_computed_every_step_and_a_later_one_must_say():
    assert S.reused({"name": "x", "pipeline_version": "0.4"}) is False
    assert S.reused({"name": "x", "pipeline_version": "0.6", "reuse": {"reused": True}}) is True
    with pytest.raises(ValueError, match="without its reuse entry"):
        S.reused({"name": "x", "pipeline_version": "0.6"})


@pytest.mark.parametrize("folder", NO_TRUTH, ids=lambda f: f.name)
def test_the_stations_and_the_certificate_come_from_the_records(folder):
    m = S.molecule(folder)
    rec, cert = record(folder)
    assert [s["title"] for s in m["stations"]] == [s["title"] for s in S.STATIONS]
    assert m["stations"][2]["time"] == f"{S.duration(rec['seconds']['optimise'])} on the laptop"
    assert m["stations"][3]["time"] == f"{S.duration(rec['seconds']['low_level'])} on the laptop"
    assert m["stations"][4]["time"] == f"{S.duration(rec['seconds']['correction_and_spectra'])} with the spectrum"
    for row in m["families"]:
        bands = [b for b in cert["bands"] if b["family"] == row["family"]]
        assert row["bands"] == len(bands)
        assert (row["error_a"], row["error_b"], row["licensed"]) == (bands[0]["error_cm"]["a"], bands[0]["error_cm"]["b"], bands[0]["licensed"])
    assert m["status"]["role"] == cert["molecule"]["seen"]["role"] and m["truth"] is None
    assert m["n_c"] == S.carbon_count(rec["admission"]["formula"]) and m["route"] == "computed"


@pytest.mark.parametrize("folder", NO_TRUTH, ids=lambda f: f.name)
def test_the_curves_share_one_scale_and_the_drawing_takes_the_text_colour(folder):
    m = S.molecule(folder)
    curves = m["spectrum"]["curves"]
    assert set(curves) == {"network", "b3lyp"}
    assert max(max(c) for c in curves.values()) == 1.0 and min(min(c) for c in curves.values()) >= 0.0
    assert "currentColor" in m["depiction"] and "#000000" not in m["depiction"] and m["depiction"].startswith("<svg")


def test_the_page_carries_the_data_once_and_reads_back():
    data = S.payload(NO_TRUTH)
    html = S.page(data)
    assert S.DATA_MARK not in html and html.count("const DATA = ") == 1
    start = html.index("const DATA = ") + len("const DATA = ")
    back = json.loads(html[start:html.index(";\n", start)].replace("<\\/", "</"))
    assert back == json.loads(json.dumps(data))


def test_the_whole_default_set_where_the_corpus_holds_the_truth():
    truth_files = [S.M05 / record(f)[1]["molecule"]["truth"]["source"] for f in S.DEFAULT_RUNS if record(f)[1]["molecule"].get("truth")]
    if not all(p.exists() for p in truth_files):
        pytest.skip("the corpus's truth Hessians are not on this machine")
    data = S.payload(S.DEFAULT_RUNS)
    assert len(data["molecules"]) == len(S.DEFAULT_RUNS) and data["network"] == "ΔH network v1.3"
    reused = [m for m in data["molecules"] if m["route"] == "reused"]
    assert [m["name"] for m in reused] == ["carbazole"] and reused[0]["stations"][2]["time"].startswith("from the corpus")
    for m in data["molecules"]:
        assert ("truth" in m["spectrum"]["curves"]) == (m["truth"] is not None)
