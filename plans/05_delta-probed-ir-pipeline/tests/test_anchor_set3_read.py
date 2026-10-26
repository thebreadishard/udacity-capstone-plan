"""probes/anchor_set3_read.py on synthetic records, before any number of set three is read (CLAUDE.md: a registration's read script runs
on synthetic records with the regime's edge cases first): R-A's four branches (>= 20 %, < 5 % still learning, < 5 % flat, between) and a
pool that makes things worse; R-B's 2-of-3 line and its two fail branches; arm M's adopt, its block by a passing R-B, its 'other' and
intensity conditions, fails-out-of-sample and data-limited; arm C read only after R-B fails and arm M is not adopted, its 1.0 cm-1 edge;
the plan from the registry, with an anchor that failed promotion."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import anchor_set3_read as S3

pytest.importorskip("torch")                  # the plan imports rungC_cc_transfer

NEW_IDS = list(S3.NEW)
SEED_NOISE = (-1.0, 0.0, 1.0)


def column(oop: float, other: float = 5.0, inten: float | None = None) -> dict:
    c = {"freq_rms_by_family": {"ring-ip": 1.0, "CH-stretch": 1.0, "CH-oop": oop, "other": other}}
    if inten is not None:
        c["intensity"] = {S3.MATCHED: inten}
    return c


def ra_records(oop_at, inten_at=lambda k, j, s: 0.30, zero_inten: float = 0.40, n_new: int = 5, protocol=S3.REGISTERED) -> list:
    """R-A runs as the plan makes them; the protocol's standard column's CH-oop and the low-symmetry anchors' intensity from (k, subset,
    seed); the column beside it (if any) one wave number above."""
    out = []
    for r in S3.plan_runs(NEW_IDS[:n_new], "out/x", protocol.arms):
        if r.arm != "RA":
            continue
        folds = {i: {protocol.standard: column(oop_at(r.k, r.subset, r.seed), inten=inten_at(r.k, r.subset, r.seed)),
                     S3.ZERO: column(20.0, inten=zero_inten)} for i in S3.ORIGINALS}
        if protocol.beside:
            for i in S3.ORIGINALS:
                folds[i][protocol.beside] = column(oop_at(r.k, r.subset, r.seed) + 1.0, inten=0.5)
        out.append((r, {"folds": folds}))
    return out


def noisy(base: dict, sd: float):
    return lambda k, j, s: base[k] + sd * SEED_NOISE[s] + sd * 0.1 * j


@pytest.mark.parametrize(("base", "sd", "branch", "learning"), [
    ({0: 10.0, 2: 9.0, 4: 8.0, 5: 7.5}, 0.05, "more anchors move T3", True),                 # -25 %
    ({0: 10.0, 2: 10.3, 4: 10.2, 5: 9.7}, 0.01, "data-limited", True),                        # -3 %, the last step clearly down
    ({0: 10.0, 2: 9.9, 4: 9.8, 5: 9.75}, 0.30, "flat", False),                                # -2.5 % inside the noise
    ({0: 10.0, 2: 10.2, 4: 10.4, 5: 10.5}, 0.05, "flat", False),                              # worse with more anchors
    ({0: 10.0, 2: 9.5, 4: 9.2, 5: 8.8}, 0.05, "between", True),                               # -12 %
])
def test_ra_branches(base, sd, branch, learning):
    res = S3.ra_read(ra_records(noisy(base, sd)))
    assert res["verdict"].startswith(branch) and res["still_learning"] is learning
    assert res["reduction"] == pytest.approx(1 - base[5] / base[0], abs=1e-9)
    assert [p.k for p in res["curves"][f"{S3.STANDARD} CH-oop"]] == [0, 2, 4, 5]
    assert [p.n for p in res["curves"][f"{S3.STANDARD} CH-oop"]] == [3, 15, 15, 3]             # subsets x seeds


def test_ra_standard_error_is_over_subsets_and_seeds():
    c = S3.ra_read(ra_records(noisy({0: 10.0, 2: 9.0, 4: 8.0, 5: 7.5}, 0.3)))["curves"][f"{S3.STANDARD} CH-oop"]
    assert c[0].se == pytest.approx(np.std([9.7, 10.0, 10.3], ddof=1) / np.sqrt(3))


def test_ra_without_the_baseline_is_refused():
    recs = [(r, rec) for r, rec in ra_records(noisy({0: 10.0, 2: 9.0, 4: 8.0, 5: 7.5}, 0.05)) if r.k != 0]
    with pytest.raises(ValueError, match="baseline"):
        S3.ra_read(recs)


def test_a_missing_or_nan_value_stops_the_read():
    recs = ra_records(noisy({0: 10.0, 2: 9.0, 4: 8.0, 5: 7.5}, 0.05))
    recs[0][1]["folds"]["A_8448043181"][S3.STANDARD]["freq_rms_by_family"]["CH-oop"] = float("nan")
    with pytest.raises(ValueError, match="CH-oop"):
        S3.ra_read(recs)
    del recs[0][1]["folds"]["A_8448043181"][S3.STANDARD]["freq_rms_by_family"]["CH-oop"]
    with pytest.raises(KeyError):
        S3.ra_read(recs)


def test_rb_passes_on_two_of_three():
    recs = ra_records(noisy({0: 10.0, 2: 9.0, 4: 8.0, 5: 7.5}, 0.05))
    for r, rec in recs:
        if r.k == 5:
            rec["folds"]["A_3100da3761"][S3.STANDARD]["intensity"][S3.MATCHED] = 0.45     # benzonitrile above the zero rule's 0.40
    res = S3.rb_read(recs)
    assert res["passed"] and res["below_zero_rule"] == 2 and res["verdict"] == "anchors repair the shapes"


@pytest.mark.parametrize(("inten", "sd", "waits"), [
    ({0: 0.70, 2: 0.60, 4: 0.55, 5: 0.45}, 0.001, True),            # above the zero rule, still falling
    ({0: 0.50, 2: 0.50, 4: 0.50, 5: 0.50}, 0.02, False),            # above it and flat
])
def test_rb_fail_branches(inten, sd, waits):
    res = S3.rb_read(ra_records(noisy({0: 10.0, 2: 9.0, 4: 8.0, 5: 7.5}, 0.05), inten_at=noisy(inten, sd)))
    assert not res["passed"] and res["below_zero_rule"] == 0
    assert res["still_falling"] is waits
    assert ("waits for anchor set four" in res["verdict"]) is waits and ("re-choose lambda" in res["verdict"]) is not waits


def m_records(arm_oop: dict, arm_other: float = 5.0, arm_inten=(0.25,) * 5, c_oop: float = 10.0, c_inten=(0.25,) * 5, sd: float = 0.01) -> list:
    """Arm M runs: the standard at CH-oop 10, 'other' 5, intensity 0.30 on every new anchor; the arm's CH-oop per k_t ('4', '8', 'all')."""
    out = []
    for r in S3.plan_runs(NEW_IDS, "out/x"):
        if r.arm != "M":
            continue
        folds = {}
        for n, i in enumerate(NEW_IDS):
            subsets = {k: [{"read": column(arm_oop[k] + sd * (SEED_NOISE[r.seed] + j - 2))} for j in range(5)] for k in ("4", "8")}
            folds[i] = {"train": [x for x in r.anchors if x != i], "oop_fit_subsets": subsets,
                        S3.STANDARD: column(10.0, 5.0, 0.30), S3.ZERO: column(20.0, inten=0.40),
                        S3.ARM_M: column(arm_oop["all"] + sd * SEED_NOISE[r.seed], arm_other, arm_inten[n]),
                        S3.ARM_C: column(c_oop, 5.0, c_inten[n])}
        out.append((r, {"folds": folds}))
    return out


def test_arm_m_adopts_at_its_edges():
    res = S3.arm_m_read(m_records({"4": 9.0, "8": 8.5, "all": 8.0}, arm_other=5.5, arm_inten=(0.30, 0.30, 0.30, 0.30, 0.9)), rb_passed=False)
    assert res["reduction"] == pytest.approx(0.20) and res["other_rise"] == pytest.approx(0.10)    # both exactly on their lines
    assert res["intensity_at_or_below"] and res["adopted"] and res["verdict"].startswith("adopt")
    assert [p.k for p in res["curve"]] == [4, 8, 10]


def test_arm_m_is_not_adopted_as_it_stands_when_rb_passed():
    res = S3.arm_m_read(m_records({"4": 9.0, "8": 8.0, "all": 7.0}), rb_passed=True)
    assert not res["adopted"] and "R-B passed" in res["verdict"]


@pytest.mark.parametrize(("kwargs", "branch"), [
    ({"arm_other": 5.6}, "between"),                                                  # 'other' 12 % above
    ({"arm_inten": (0.2, 0.2, 0.2, 0.9, 0.9)}, "between"),                            # intensity on 3 of 5 only
])
def test_arm_m_needs_all_three_conditions(kwargs, branch):
    res = S3.arm_m_read(m_records({"4": 9.0, "8": 8.0, "all": 7.0}, **kwargs), rb_passed=False)
    assert not res["adopted"] and res["verdict"].startswith(branch)


@pytest.mark.parametrize(("oop", "sd", "branch"), [
    ({"4": 9.8, "8": 9.8, "all": 9.8}, 0.2, "fails out of sample"),
    ({"4": 11.0, "8": 10.2, "all": 9.7}, 0.01, "data-limited"),
])
def test_arm_m_small_gains_split_on_the_curve(oop, sd, branch):
    res = S3.arm_m_read(m_records(oop, sd=sd), rb_passed=False)
    assert res["reduction"] < S3.FLAT and res["verdict"].startswith(branch)


@pytest.mark.parametrize(("c_oop", "adopted"), [(11.0, True), (8.99, False)])
def test_arm_c_is_read_only_after_rb_fails_and_m_is_not_adopted(c_oop, adopted):
    recs = m_records({"4": 9.8, "8": 9.8, "all": 9.8}, c_oop=c_oop, c_inten=(0.2, 0.2, 0.2, 0.2, 0.5))
    assert not S3.arm_c_read(recs, rb_passed=True, m_adopted=False)["read"]
    assert not S3.arm_c_read(recs, rb_passed=False, m_adopted=True)["read"]
    res = S3.arm_c_read(recs, rb_passed=False, m_adopted=False)
    assert res["read"] and res["intensity_below"] == 4 and res["adopted"] is adopted         # within 1.0 cm-1 of lambda = 1's 10.0


def test_two_thirds_of_the_new_anchors():
    assert S3.two_thirds(4, 5) and not S3.two_thirds(3, 5) and S3.two_thirds(3, 4) and not S3.two_thirds(2, 4)


def test_still_learning_needs_a_clear_downward_last_step():
    P = S3.Point
    assert S3.still_learning([P(4, 10.0, 0.1, 15), P(5, 9.5, 0.1, 3)])                 # 0.5 > 2 * 0.14
    assert not S3.still_learning([P(4, 10.0, 0.2, 15), P(5, 9.5, 0.2, 3)])             # 0.5 < 2 * 0.28
    assert not S3.still_learning([P(4, 10.0, 0.0, 15), P(5, 10.5, 0.0, 3)])            # upward
    assert not S3.still_learning([P(5, 9.5, 0.0, 3)])


def entries(skip: tuple[str, ...] = (), tier: str = "TZ", failed: tuple[str, ...] = ()) -> list[dict]:
    return [{"mol_id": i, "status": "experimental" if i in failed else "carried", "tier": tier, "path": f"x/{i}.npz"}
            for i in (*S3.ORIGINALS, *S3.NEW) if i not in skip]


def test_the_plan_from_the_registry(tmp_path):
    m = S3.plan(tmp_path / "out", entries(), check=False, runs_dir=tmp_path)
    assert m["new_carried"] == NEW_IDS and m["left_the_read"] == {}
    runs = m["runs"]
    assert sum(r["arm"] == "RA" for r in runs) == 3 * (1 + 5 + 5 + 1) and sum(r["arm"] == "M" for r in runs) == 3
    first = json.loads((tmp_path / "anchor_set3_first.json").read_text(encoding="utf-8"))
    rest = json.loads((tmp_path / "anchor_set3_rest.json").read_text(encoding="utf-8"))
    assert len(first["steps"]) == 1 and len(rest["steps"]) == len(runs) - 1
    ra = rest["steps"][5]["argv"]
    assert [ra[n + 1] for n, x in enumerate(ra) if x == "--held"] == list(S3.ORIGINALS)
    assert {ra[n + 1].split("=")[0] for n, x in enumerate(ra) if x == "--apt"} >= {"A_8448043181", *S3.LOW_SYMMETRY}
    assert ra[:6] == ["{python}", "m05/rungC_cc_transfer.py", "corpus/molecules", S3.MODEL.format(seed=0), runs[6]["prefix"],
                      *S3.TRANSFER_ARGS[:1]]
    arm_m = rest["steps"][-1]["argv"]
    assert arm_m[arm_m.index("--oop-fit-sizes") + 1] == "4,8" and "--oop-couplings-low" in arm_m and "--oop-diagonal-model" in arm_m
    assert sum(x == "--anchor" for x in arm_m) == 11 and sum(x == "--held" for x in arm_m) == 5
    assert S3.MODEL.format(seed=2) in arm_m


def test_an_anchor_that_failed_promotion_leaves_by_name(tmp_path):
    m = S3.plan(tmp_path / "out", entries(failed=("A_d9139359ab",)), check=False, runs_dir=tmp_path)
    assert m["left_the_read"] == {"A_d9139359ab": "azulene"} and len(m["new_carried"]) == 4
    ks = sorted({r["k"] for r in m["runs"] if r["arm"] == "RA"})
    assert ks == [0, 2, 4]                                                     # 'all' is four
    assert sum(r["arm"] == "RA" for r in m["runs"]) == 3 * (1 + 5 + 1)        # C(4, 2) = 6 > 5: five subsets; C(4, 4) = 1


def test_an_anchor_not_yet_promoted_stops_the_plan(tmp_path):
    with pytest.raises(SystemExit, match=r"not promoted yet.*quinoline"):
        S3.plan(tmp_path / "out", entries(skip=("A_ff98e1160d",)), check=False, runs_dir=tmp_path)
    assert not (tmp_path / "anchor_set3_first.json").exists()


def test_an_original_without_a_carried_tz_entry_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="pyridine"):
        S3.plan(tmp_path / "out", entries(skip=("A_6e858b26e5",)), check=False, runs_dir=tmp_path)
    with pytest.raises(SystemExit, match="TZ"):
        S3.plan(tmp_path / "out", entries(tier="DZ"), check=False, runs_dir=tmp_path)


def test_the_head_all_plan(tmp_path):
    """The whole-head repeat: R-A only (no arms), its own run files and chain names, the transfer told to train every head layer, and
    the corpus folder it is given."""
    m = S3.plan(tmp_path / "out", entries(), check=False, runs_dir=tmp_path, protocol=S3.HEAD_ALL, molecules="../x/corpus/molecules")
    assert m["protocol"] == "head_all" and m["molecules"] == "../x/corpus/molecules"
    assert {r["arm"] for r in m["runs"]} == {"RA"} and len(m["runs"]) == 3 * (1 + 5 + 5 + 1)
    assert not (tmp_path / "anchor_set3_first.json").exists()
    first = json.loads((tmp_path / "anchor_set3_headall_first.json").read_text(encoding="utf-8"))
    rest = json.loads((tmp_path / "anchor_set3_headall_rest.json").read_text(encoding="utf-8"))
    assert first["name"] == "S3HF" and rest["name"] == "S3HR" and len(rest["steps"]) == len(m["runs"]) - 1
    argv = rest["steps"][0]["argv"]
    assert argv[2] == "../x/corpus/molecules" and argv[argv.index("--modes") + 1] == "head_all" and "--fit-mode" not in argv
    assert "--head-l2" not in argv


def test_the_registered_plan_records_its_protocol(tmp_path):
    m = S3.plan(tmp_path / "out", entries(), check=False, runs_dir=tmp_path)
    assert m["protocol"] == "registered" and m["molecules"] == "corpus/molecules"
    assert json.loads((tmp_path / "anchor_set3_rest.json").read_text(encoding="utf-8"))["name"] == "S3R"


def test_the_head_all_read_uses_its_column_and_texts():
    recs = ra_records(noisy({0: 10.0, 2: 9.95, 4: 9.9, 5: 9.85}, 0.05), inten_at=lambda k, j, s: 0.5, protocol=S3.HEAD_ALL)
    res = S3.read_all(recs, S3.HEAD_ALL)
    assert set(res["R-A"]["curves"]) == {"network_head_all CH-oop", "network_head_all other"}
    assert res["R-A"]["verdict"].startswith("flat") and res["arm M"] is None and res["arm C"] is None
    assert res["R-B"]["below_zero_rule"] == 0 and res["R-B"]["verdict"].startswith("the shape question stands")
    text = "\n".join(S3.report_lines(res, {"new_carried": NEW_IDS, "left_the_read": {}}, S3.HEAD_ALL))
    assert "protocol head_all (whole head)" in text and "lambda" not in text
    with pytest.raises(KeyError):
        S3.read_all(recs)                                                      # the registered column is not in these records


def test_the_full_read_from_files(tmp_path, monkeypatch):
    """The manifest names every run; each record is found by its prefix, its folds checked against the held-out list, and the report
    written."""
    out = tmp_path / "out"
    monkeypatch.setattr(S3, "M05", tmp_path)
    m = S3.plan(out, entries(), check=False, runs_dir=tmp_path)
    recs = {(r.arm, r.k, r.subset, r.seed): rec for r, rec in ra_records(noisy({0: 10.0, 2: 9.0, 4: 8.0, 5: 7.5}, 0.05))}
    recs.update({(r.arm, r.k, r.subset, r.seed): rec for r, rec in m_records({"4": 9.8, "8": 9.8, "all": 9.8}, sd=0.2)})
    for d in m["runs"]:
        p = tmp_path / f"{d['prefix']}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(recs[(d["arm"], d["k"], d["subset"], d["seed"])]), encoding="utf-8")
    res = S3.read(out)
    assert res["R-A"]["verdict"].startswith("more anchors") and res["arm M"]["verdict"].startswith("fails out of sample")
    assert res["arm C"]["read"] is False                                       # R-B passed (0.30 below the zero rule's 0.40)
    text = (out / "read_set3.md").read_text(encoding="utf-8")
    assert "R-A" in text and "quinoxaline" in text
    (tmp_path / f"{m['runs'][0]['prefix']}.json").unlink()
    with pytest.raises(SystemExit, match="missing"):
        S3.read(out)
