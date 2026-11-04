"""probes/anharmonic_route_rule.py on synthetic S2b and S3 reads, before either read exists (PreRegistration_2026-11-04_Anharmonic_Route_Rule.md):
the learned route when S3's line holds, the family mean when only it meets the line, no step otherwise, and the families S3 cannot judge."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
R = pytest.importorskip("anharmonic_route_rule")


def s3(n: int, **rms: float) -> dict:
    return {"n": n, "rms": rms}


def v(model: str) -> dict:
    return {"best_curve_model": model}


@pytest.mark.parametrize("verdict,entry,route", [
    (v("x1"), s3(10, c=4.0, x1=2.5), "x1"),                # the learned model carries
    (v("x1"), s3(10, c=4.0, x1=3.0), "x1"),                # exactly on the line
    (v("x1"), s3(10, c=2.8, x1=2.9), "c"),                 # under the line but not below (c): the mean carries
    (v("x1"), s3(10, c=2.9, x1=2.9), "c"),                 # equal to (c) is not below it
    (v("x1"), s3(10, c=2.5, x1=3.4), "c"),                 # the learned model misses, the mean meets the line
    (v("c"), s3(10, c=2.0), "c"),                          # S2b chose the mean itself
    (v("x2*"), s3(10, c=2.0, **{"x2*": math.nan}), "c"),   # the verdict model gave no prediction
    (v("x1"), s3(10, c=3.2, x1=3.1), None),                # neither carries
    (v("x1"), s3(5, c=1.0, x1=0.5), None),                 # too few target modes: not checked at size
    (None, s3(10, c=1.0), None),                           # no S2b verdict
])
def test_the_route_per_family(verdict, entry, route):
    got = R.route_for_family(verdict, entry)
    assert got["route"] == route
    if route is None:
        assert got["error_bar_cm"] is None
    else:
        assert got["error_bar_cm"] == entry["rms"][route]


def test_a_family_without_target_modes_gets_no_step():
    s2b = {"scopes": {R.MAIN_SCOPE: {"read": {"verdicts": {"CH-stretch": v("c"), "ring-ip": v("x1")}}}}}
    got = R.route_rule(s2b, {"read": {"families": {"ring-ip": s3(12, c=4.0, x1=2.0)}}})
    assert got["CH-stretch"]["route"] is None and "0 target mode" in got["CH-stretch"]["reason"]
    assert got["ring-ip"]["route"] == "x1"
