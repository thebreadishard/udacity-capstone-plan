"""The shared strict-JSON writer (`probes/json_records.py`, TASKS 276): NaN and ±inf become null at any depth, numpy scalars and arrays
become Python values, the text always passes a strict reader, every other value is written as `json.dumps` writes it, `allow_nan` is
refused, and the record reaches its path through a temp file that does not stay behind on a failure."""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
import json_records as J


def strict_load(text: str) -> object:
    """Parse as RFC 8259 does: a bare NaN or Infinity is an error."""
    def refuse(constant: str) -> None:
        raise ValueError(f"non-JSON constant {constant}")
    return json.loads(text, parse_constant=refuse)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, np.float64("nan"), np.float32("inf"), np.float64("-inf")])
def test_a_non_finite_float_becomes_null(value):
    assert strict_load(J.dumps({"x": value})) == {"x": None}


def test_non_finite_values_nested_in_dicts_lists_and_tuples():
    record = {"a": [1.0, math.nan, {"b": (math.inf, 2)}], "c": {"d": {"e": -math.inf}}}
    assert strict_load(J.dumps(record)) == {"a": [1.0, None, {"b": [None, 2]}], "c": {"d": {"e": None}}}


def test_numpy_scalars_and_arrays_become_python_values():
    record = {"i": np.int64(3), "f": np.float32(0.5), "b": np.bool_(True), "arr": np.array([[1.0, np.nan], [np.inf, 4.0]]),
              "ints": np.arange(3)}
    loaded = strict_load(J.dumps(record))
    assert loaded == {"i": 3, "f": 0.5, "b": True, "arr": [[1.0, None], [None, 4.0]], "ints": [0, 1, 2]}
    assert isinstance(loaded["i"], int) and isinstance(loaded["b"], bool)


def test_finite_records_are_written_exactly_as_json_dumps_writes_them():
    record = {"name": "Δν", "n": 7, "x": 0.1 + 0.2, "tiny": 5e-324, "big": 1.7976931348623157e308, "flag": False, "none": None,
              "nested": [{"k": [1, 2.5, "s"]}], "np_float": np.float64(2.25)}
    reference = dict(record, np_float=2.25)
    assert J.dumps(record) == json.dumps(reference, indent=1)
    assert J.dumps(record, indent=None, ensure_ascii=False) == json.dumps(reference, ensure_ascii=False)
    assert strict_load(J.dumps(record)) == reference


def test_json_safe_leaves_its_input_unchanged():
    record = {"a": [math.nan], "b": np.array([1.0, np.inf])}
    J.json_safe(record)
    assert math.isnan(record["a"][0]) and np.isinf(record["b"][1])


def test_allow_nan_is_refused_not_ignored():
    with pytest.raises(TypeError, match="allow_nan"):
        J.dumps({"x": 1.0}, allow_nan=True)


def test_an_object_json_cannot_write_still_raises_and_default_still_applies():
    with pytest.raises(TypeError):
        J.dumps({"x": object()})
    assert strict_load(J.dumps({"x": complex(1, 0)}, default=lambda c: c.real)) == {"x": 1.0}


def test_write_puts_strict_json_at_the_path_and_leaves_no_temp_file(tmp_path):
    target = tmp_path / "record.json"
    target.write_text("old", encoding="utf-8")
    J.write(target, {"v": [math.nan, 1.5]})
    assert strict_load(target.read_text(encoding="utf-8")) == {"v": [None, 1.5]}
    assert sorted(p.name for p in tmp_path.iterdir()) == ["record.json"]


def test_write_accepts_a_string_path(tmp_path):
    J.write(str(tmp_path / "r.json"), {"v": 1})
    assert strict_load((tmp_path / "r.json").read_text(encoding="utf-8")) == {"v": 1}


def test_a_failed_write_keeps_the_old_record_and_leaves_no_temp_file(tmp_path):
    target = tmp_path / "record.json"
    target.write_text('{"old": 1}', encoding="utf-8")
    with pytest.raises(TypeError):
        J.write(target, {"x": object()})
    assert target.read_text(encoding="utf-8") == '{"old": 1}'
    assert sorted(p.name for p in tmp_path.iterdir()) == ["record.json"]


def test_a_failed_move_removes_the_temp_file(tmp_path, monkeypatch):
    target = tmp_path / "record.json"

    def fail(src: str, dst: object) -> None:
        raise OSError("move refused")
    monkeypatch.setattr(J.os, "replace", fail)
    with pytest.raises(OSError, match="move refused"):
        J.write(target, {"v": 1})
    assert list(tmp_path.iterdir()) == []
