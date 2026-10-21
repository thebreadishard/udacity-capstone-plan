"""The proxy check's planner and read (`probes/proxy_check_plan.py`) on synthetic inputs: the slopes from a decomposition, the hash-order
split, the chain's steps, and the read with its edge cases (a clear gap, no gap, a missing value, a missing record)."""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import proxy_check_plan as X  # noqa: E402


def test_slopes_are_the_median_over_anchors_with_two_modes_or_more(tmp_path):
    def fam(slope, n):
        return {"total": {"slope": slope, "corr": 0.0, "rms": 1.0}, "proxy rms": 1.0, "n": n}
    d = {"x": {f: fam(-1.0, 3) for f in X.FAMILIES}, "y": {f: fam(-0.5, 3) for f in X.FAMILIES}, "z": {f: fam(9.0, 1) for f in X.FAMILIES}}
    d["w"] = {f: fam(-0.2, 2) for f in X.FAMILIES}
    p = tmp_path / "decompose.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    slopes = X.cc_slopes(p)
    assert slopes == dict.fromkeys(X.FAMILIES, -0.5)                         # z (one mode) left out
    assert X.family_scale_text(slopes) == "ring-ip=-0.5,CH-stretch=-0.5,CH-oop=-0.5,other=-0.5"


def test_the_real_slopes_exist_and_are_negative_out_of_plane():
    if not X.DECOMPOSE.exists():
        pytest.skip("the diagnosis' decomposition is a local result (mirrored to capstone-data), not in the repository")
    slopes = X.cc_slopes()
    assert slopes["CH-oop"] < 0 and slopes["other"] < 0


def test_the_split_is_in_hash_order_and_disjoint():
    elig = {f"A_{i:03d}": ("A2" if i % 3 == 0 else "B") for i in range(400)}
    ids = X.split_ids(elig)
    assert len(ids["a_reservoir"]) == 200 and len(ids["a_read"]) == 200 and len(ids["b_reservoir"]) == 40
    assert not set(ids["a_reservoir"]) & set(ids["a_read"]) and not set(ids["b_reservoir"]) & set(ids["b_read"])
    assert all(elig[i] == "A2" for i in ids["b_reservoir"] + ids["b_read"])
    assert ids == X.split_ids(dict(reversed(list(elig.items()))))
    with pytest.raises(SystemExit, match="too few"):
        X.split_ids(dict(list(elig.items())[:100]))


def test_the_chain_trains_both_bases_registers_then_fine_tunes(tmp_path):
    manifest = {"slopes": {"CH-oop": -0.43, "other": -1.16}, "recipe": ["--sizes", "all", "--save-model"], "pool": {"a": 980, "b": 800}}
    out_dir = X.M05 / "out" / "proxy_check_test"
    st = X.steps(out_dir, manifest)
    assert [s["label"] for s in st[:3]] == ["base_b", "base_a", "register"]
    assert st[0]["argv"][-2:] == ["--exclude-ids-file", "out/proxy_check_test/b_exclude.txt"]
    assert st[1]["argv"][-2:] == ["--family-scale", "CH-oop=-0.43,other=-1.16"]
    ft = [s for s in st if s["label"].startswith("ft_")]
    assert len(ft) == 3 * 4 + 3 * 6
    first_a = next(s["argv"] for s in ft if s["label"] == "ft_a_k200_seed1")
    assert first_a[3] == "out/proxy_check_test/base_a_model_n980_seed1.pt" and first_a[first_a.index("--subsets") + 1] == "1"
    assert "--allow-any-model" in first_a and first_a[first_a.index("--k") + 1] == "200"


def record(oop: dict, inten: float = 0.2, draws: int = 3, modes=("head_l2", "head", "head_all", "scratch")) -> dict:
    def r(x):
        return {"family_mean": {"CH-oop": x, "other": x, "ring-ip": 1.0, "CH-stretch": 1.0}, "intensity_matched_mean": inten}
    return {"modes": list(modes), "zero_rule": r(20.0), "none": r(12.0),
            "draws": [{"modes": {m: {"read": r(oop[m] + 0.01 * j)} for m in modes}} for j in range(draws)]}


def test_the_read_finds_a_clear_gap_and_no_gap():
    by_k = {5: [record({"head_l2": 12.0, "head": 10.0, "head_all": 6.0, "scratch": 15.0}) for _ in X.SEEDS],
            200: [record({"head_l2": 6.0, "head": 6.0, "head_all": 6.0, "scratch": 6.0}, draws=1) for _ in X.SEEDS]}
    res = X.read_arm(by_k)
    gap = res[5]["comparisons"]
    assert gap["whole head below the last layer (λ 1)"]["CH-oop"] and gap["whole head below scratch (the base helps)"]["other"]
    assert not gap["whole head below the last layer (λ 1)"]["intensity"]                     # equal intensities: no gap
    assert not any(res[200]["comparisons"]["whole head below scratch (the base helps)"].values())
    assert res[5]["columns"]["head_all"]["CH-oop"][2] == 9 and res[200]["columns"]["none"]["CH-oop"][2] == 3


def test_a_missing_value_stops_the_read():
    rec = record({"head_l2": 12.0, "head": 10.0, "head_all": 6.0, "scratch": 15.0})
    rec["draws"][0]["modes"]["head_all"]["read"]["intensity_matched_mean"] = None
    with pytest.raises(SystemExit, match="non-finite"):
        X.read_arm({5: [rec]})


def test_a_missing_record_stops_the_read(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"slopes": {}, "pool": {}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="missing records"):
        X.read(tmp_path)
