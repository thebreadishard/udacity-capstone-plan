"""tests/pin_tools.py, the regression pins' shared tools (16 Oct 2026), on small synthetic inputs."""
import json

import pytest

from pin_tools import corpus_changes, digest, environment_mismatch, first_difference, sha256, stable


def test_a_changed_or_added_file_is_named(tmp_path):
    (tmp_path / "molecules" / "m1").mkdir(parents=True)
    f = tmp_path / "molecules" / "m1" / "geometry.json"
    f.write_text("{}", encoding="utf-8")
    record = {"sha256": {"m1/geometry.json": sha256(f), "m1/result.json": "0"}, "molecules": [{"id": "m1"}]}
    assert corpus_changes(tmp_path, record) == ["m1/result.json: missing"]
    f.write_text("{ }", encoding="utf-8")
    (tmp_path / "molecules" / "m2").mkdir()
    assert corpus_changes(tmp_path, record) == ["m1/geometry.json: changed", "m1/result.json: missing", "m2/: not in the record"]


def test_an_other_environment_is_named():
    here = {"system": "Windows", "torch": "2.14.0+cpu"}
    assert environment_mismatch(here, dict(here)) is None
    msg = environment_mismatch(here, {"system": "Linux", "torch": "2.14.0+cpu"})
    assert "'system': ('Windows', 'Linux')" in msg and "torch" not in msg


def test_stable_drops_the_given_fields_at_any_depth():
    rec = {"date": "x", "a": [{"seconds": 1.0, "b": 2}], "provenance": {}, "c": {"seconds": 3, "d": None}}
    assert stable(rec, frozenset({"date", "seconds", "provenance"})) == {"a": [{"b": 2}], "c": {"d": None}}


def test_first_difference_names_the_path():
    assert first_difference({"a": [1, 2.0]}, {"a": [1, 2.0]}) is None
    assert first_difference({"a": [1, 2.0]}, {"a": [1, 2.5]}) == "$.a[1]: 2.0 vs 2.5"
    assert first_difference({"a": float("nan")}, json.loads('{"a": NaN}')) is None
    assert first_difference({"a": 1}, {"b": 1}).startswith("$: keys")


def test_the_digest_sees_one_bit_and_is_the_same_for_torch_and_numpy():
    torch = pytest.importorskip("torch")
    x = torch.tensor([1.0, 2.0])
    y = x.clone()
    y[1] = torch.nextafter(y[1], torch.tensor(3.0))
    assert digest(x) == digest(x.clone()) == digest(x.numpy()) != digest(y)
