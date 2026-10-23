"""compute_prices (TASKS 92/86/96): the parsers read the records the 23 Oct prices came from, rows that do not say how they ran are
left out, and the cation candidates are exactly the twins a short cell can use."""
import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import compute_prices as cp  # noqa: E402  (after the sys.path insert)

TIME_V = """\tCommand being timed: "python dfmp2_rows.py rows"
\tElapsed (wall clock) time (h:mm:ss or m:ss): {wall}
\tMaximum resident set size (kbytes): {kb}
"""


def test_machine_class_needs_the_thread_count_for_servers():
    assert cp.machine_class({"machine": "Asus18", "note": ""}) == "laptop"
    assert cp.machine_class({"machine": "ubuntu-32gb-hel1-2", "note": "threads=8 memory_gb=12"}) == "CPX62, 8 threads"
    assert cp.machine_class({"machine": "ubuntu-32gb-hel1-9", "note": ""}) is None          # Sep rows: threads not recorded
    assert cp.machine_class({"machine": "somewhere-else", "note": "threads=8"}) is None


def test_wall_seconds_reads_both_time_formats():
    assert cp.wall_seconds(TIME_V.format(wall="1:57:24", kb=1)) == 7044.0
    assert cp.wall_seconds(TIME_V.format(wall="26:30.60", kb=1)) == pytest.approx(1590.6)
    with pytest.raises(ValueError):
        cp.wall_seconds("no timing here")


def test_mp2_records_per_gradient_inputs(tmp_path):
    (tmp_path / "time_quinoline_ccpvtz.txt").write_text(TIME_V.format(wall="1:57:24", kb=3063828), encoding="utf-8")
    (tmp_path / "dfmp2_rows_quinoline_ccpvtz.psi4.log").write_text("  NBF =   398, NAUX =  1020\n" + "  -Total Gradient:\n" * 102,
                                                                     encoding="utf-8")
    (rec,) = cp.mp2_records(tmp_path)
    assert (rec["name"], rec["basis"], rec["nbf"], rec["gradients"], rec["seconds"]) == ("quinoline", "ccpvtz", 398, 102, 7044.0)
    assert rec["peak_gb"] == pytest.approx(3063828 / 1024 ** 2)


def test_lane_points_take_the_ok_lines_only(tmp_path):
    (tmp_path / "lane_0.log").write_text(
        "[2026-10-22 23:41:53] lane 0 B_498c225e05 ok 14618 s (174 ok, 0 failed, 0 skipped of 174)\n"
        "[2026-10-22 23:50:00] lane 0 B_0000000001 FAILED scf (174 ok, 1 failed)\n", encoding="utf-8")
    assert cp.lane_points(tmp_path, {"B_498c225e05": 27, "B_0000000001": 20}) == [(27, 14618.0)]


def test_cation_runs_read_peak_and_wall(tmp_path):
    log = tmp_path / "a.log"
    log.write_bytes(b"noise \x00\n(CA) P3c_20332edd59 max RSS 9213932 kB, wall 14559.37 s\n")
    runs = cp.cation_runs(log)
    assert list(runs) == ["P3c_20332edd59"] and runs["P3c_20332edd59"][1] == 14559.37


def test_cation_candidates_are_computed_neutral_twins_not_yet_listed():
    cell = ("quartet", "two", False, 1)                                  # naphthalene: four C-H in a row per ring
    rows = {
        "B_aaaaaaaaaa": {"name": "naphthalene", "smiles": "c1ccc2ccccc2c1", "layer": "B", "n_atoms": 18},        # computed, no twin: a candidate
        "B_bbbbbbbbbb": {"name": "naphthalene again", "smiles": "c1ccc2ccccc2c1", "layer": "B", "n_atoms": 18},  # its twin is listed
        "B_cccccccccc": {"name": "pending", "smiles": "c1ccc2ccccc2c1", "layer": "B", "n_atoms": 18},            # not computed
    }
    manifest = {i: {} for i in [*rows, "P3c_bbbbbbbbbb"]}
    computed = {"B_aaaaaaaaaa", "B_bbbbbbbbbb"}
    got = cp.cation_candidates(rows, manifest, computed, {cell: 5})
    assert list(got) == ["P3c_aaaaaaaaaa"]
    assert [*cell] in got["P3c_aaaaaaaaaa"]["cells"]
    assert cp.cation_candidates(rows, manifest, computed, {("solo", "one", False, 1): 5}) == {}    # touches no short cell


NEUTRALS = {"A_1111111111": ("benzene", "c1ccccc1", 12), "A_2222222222": ("naphthalene", "c1ccc2ccccc2c1", 18),
            "A_3333333333": ("anthracene", "c1ccc2cc3ccccc3cc2c1", 24), "A_4444444444": ("1-methylnaphthalene", "Cc1cccc2ccccc12", 21)}


def _sources(tmp_path) -> cp.Sources:
    """A four-molecule corpus: every neutral computed, the first three with a measured cation twin, all with timed records."""
    rows = [{"id": i, "layer": "A", "name": n, "smiles": s, "n_atoms": a, "status": "done"} for i, (n, s, a) in NEUTRALS.items()]
    rows += [{"id": "P3c_" + i[2:], "layer": "P3c", "name": n + "+", "smiles": s, "n_atoms": a, "status": "done"}
             for i, (n, s, a) in list(NEUTRALS.items())[:3]]
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    with (tmp_path / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with (corpus / "ledger.csv").open("w", encoding="utf-8", newline="") as f:
        f.write("id,layer,machine,start,seconds_total,status,note\n")
        for k, (i, (_, _, a)) in enumerate(NEUTRALS.items()):
            f.write(f"{i},A,Asus18,2026-10-0{k + 1},{a ** 3},done,threads=8\n")
    lanes = tmp_path / "lanes"
    lanes.mkdir()
    (lanes / "lane_0.log").write_text("".join(f"[t] lane 0 {i} ok {a ** 3} s (1 ok)\n" for i, (_, _, a) in NEUTRALS.items()), encoding="utf-8")
    dfmp2 = tmp_path / "dfmp2"
    dfmp2.mkdir()
    for name, nbf in [("m1", 170), ("m2", 200), ("m3", 240)]:
        for basis, scale in [("ccpvdz", 1), ("ccpvtz", 3)]:
            (dfmp2 / f"time_{name}_{basis}.txt").write_text(TIME_V.format(wall=f"{nbf * scale}:00", kb=nbf * 10000), encoding="utf-8")
            (dfmp2 / f"dfmp2_rows_{name}_{basis}.psi4.log").write_text(f"  NBF = {nbf * scale}\n" + "Total Gradient\n" * 10, encoding="utf-8")
    cation_log = tmp_path / "cation.log"
    cation_log.write_text("".join(f"(CA) P3c_{i[2:]} max RSS {a * 100000} kB, wall {a ** 2} s\n" for i, (_, _, a) in list(NEUTRALS.items())[:3]),
                          encoding="utf-8")
    (tmp_path / "fill.json").write_text(json.dumps({"chosen": ["A_2222222222", "A_3333333333"]}), encoding="utf-8")
    (tmp_path / "cover.json").write_text(json.dumps({"chosen": ["A_2222222222", "P3c_2222222222"]}), encoding="utf-8")
    return cp.Sources(manifest=tmp_path / "manifest.csv", corpus=corpus, lane_logs=lanes, dfmp2=dfmp2, cation_log=cation_log,
                      fill=tmp_path / "fill.json", cover=tmp_path / "cover.json")


def test_action_fill_prices_the_list_per_machine_class(tmp_path):
    out, lines = cp.fill_price(_sources(tmp_path))
    assert out["molecules"] == 2 and list(out["deck"]) == ["laptop"] and out["deck"]["laptop"]["rows"] == 4
    assert out["analytic_lane"]["rows"] == 4 and out["analytic_lane"]["lane_hours"] > 0
    assert any("analytic labels" in line for line in lines)


def test_action_mp2_counts_six_n_gradients_and_flags_cations(tmp_path):
    out, lines = cp.mp2_price(_sources(tmp_path))
    assert set(out["per_molecule"]) == {"A_2222222222", "P3c_2222222222"}
    assert out["per_molecule"]["P3c_2222222222"]["cation"] and not out["per_molecule"]["A_2222222222"]["cation"]
    assert out["hours"] == pytest.approx(sum(v["hours"] for v in out["per_molecule"].values()))
    assert "1 cations need the open-shell DF-MP2 gradient" in lines[-1]


def test_action_cations_proposes_the_unlisted_twin_only(tmp_path):
    out, _ = cp.cation_price(_sources(tmp_path), target=30)
    assert out["chosen"] == ["P3c_4444444444"]          # computed, no cation twin yet, and its quartet cell is short (naphthalene⁺ only)
    assert out["short_cells"] > 0 and out["hours"] > 0
