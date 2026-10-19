"""probes/s2b_plan.py and s2_batch.sh's per-molecule stop rule (S2b registration, 'Computation'): the log parsers read what S2's logs hold, a
power law is recovered exactly, the split balances three-slot servers deterministically, the lists carry MAX_FIRST = 1.5 × the predicted
Hessian with LF line ends, and s2_batch.sh hands a molecule its own MAX_FIRST from the third column (the batch's without one)."""
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROBES = Path(__file__).resolve().parents[1] / "probes"
sys.path.insert(0, str(PROBES))
pytest.importorskip("rdkit")
P = pytest.importorskip("s2b_plan")
BASH = shutil.which("bash")


def test_hessian_lines_give_the_median(tmp_path):
    (tmp_path / "A_x.log").write_text("[05:31:38] 1/1 ref.json E = -385.88 in 515 s\n[05:40:30] 1/97 mode00_m.json E = -385.8 in 531 s\n"
                                      "[05:49:16] 2/97 mode00_p.json E = -385.8 in 526 s\n[05:57:55] 3/97 mode01_m.json E = -385.8 in 519 s\n",
                                      encoding="utf-8")
    (tmp_path / "notes.txt").write_text("[05:40:30] 1/97 mode00_m.json E = -1 in 9999 s\n", encoding="utf-8")
    assert P.hessian_seconds(str(tmp_path)) == {"A_x": 526.0}         # the reference Hessian and other files are not displaced Hessians


def test_batch_markers_give_hours_and_skip_a_stopped_molecule(tmp_path):
    log = tmp_path / "s2.log"
    log.write_text("=== (S2) start: 3 molecules, 3 at a time 2026-10-14 05:02:19\n=== (S2) A_a: start 2026-10-14 05:00:00\n"
                   "=== (S2) A_b: start 2026-10-14 05:00:00\n=== (S2) A_c: start 2026-10-14 05:00:00\n"
                   "=== (S2) A_a: done 2026-10-14 07:30:00\n=== (S2) A_b: NOISY (excluded by the noise rule) 2026-10-15 06:00:00\n"
                   "=== (S2) A_c: STOPPED (first displaced Hessian over 1800 s) 2026-10-14 06:00:00\n", encoding="utf-8")
    assert P.molecule_hours(str(log)) == {"A_a": 2.5, "A_b": 25.0}


def test_power_fit_recovers_an_exact_law_and_refuses_too_few_points():
    a, b = P.power_fit([(n, math.exp(-11.82) * n ** 5.04) for n in (9, 12, 16, 20)])
    assert abs(a + 11.82) < 1e-9 and abs(b - 5.04) < 1e-12
    with pytest.raises(ValueError, match="too few"):
        P.power_fit([(12, 1.0), (12, 2.0), (12, 3.0)])


def test_split_balances_and_is_deterministic():
    hours = {"big": 40.0, "m1": 10.0, "m2": 10.0, "m3": 10.0, "m4": 10.0, "s1": 5.0, "s2": 5.0}
    lists, ends = P.split(hours, 2)
    assert lists[0][0] == "big" and sorted(i for ids in lists for i in ids) == sorted(hours)
    assert max(ends) == 40.0 and lists == P.split(dict(reversed(hours.items())), 2)[0]
    _, one = P.split(hours, 1)
    assert one == [40.0]                                        # three slots: 'big' alone outlasts the six others (10+10+5, 10+10+5)


def test_lists_carry_the_stop_rule_with_lf(tmp_path):
    selected = [{"id": "A_s", "n_atoms": 10}, {"id": "A_l", "n_atoms": 20}]
    result = P.plan(selected, (math.log(2.0), 1.0), (math.log(0.5), 1.0), [1, 2])
    assert result["molecules"]["A_l"]["hessian_s"] == pytest.approx(40.0) and result["molecules"]["A_l"]["max_first_s"] == P.MIN_MAX_FIRST_S
    big = P.plan([{"id": "A_b", "n_atoms": 20}], (math.log(400.0), 1.0), (0.0, 1.0), [1])["molecules"]["A_b"]
    assert big["max_first_s"] == 12000                          # 1.5 × 8,000 s, above the floor
    P.write_lists(str(tmp_path), result)
    assert (tmp_path / "s2b_ids_1of1.tsv").read_bytes().startswith(b"A_l\tmodules/05_support_predictor/corpus/molecules/A_l/geometry.json\t300\n")
    assert {p.name for p in tmp_path.iterdir()} == {"s2b_ids_1of1.tsv", "s2b_ids_1of2.tsv", "s2b_ids_2of2.tsv", "plan.json"}
    assert result["servers"]["2"]["eur"] == pytest.approx(sum(result["servers"]["2"]["end_h"]) * P.EUR_PER_SERVER_HOUR)


@pytest.mark.skipif(BASH is None, reason="needs bash")
def test_s2_batch_hands_each_molecule_its_own_max_first(tmp_path):
    probes = tmp_path / "probes"
    probes.mkdir()
    shutil.copy(PROBES / "s2_batch.sh", probes / "s2_batch.sh")
    (probes / "s1_anharmonic_level.sh").write_text('echo "MAX_FIRST=$MAX_FIRST"\n', encoding="utf-8", newline="\n")
    (tmp_path / "ids.tsv").write_text("A_own\tg1.json\t4321\nA_batch\tg2.json\n", encoding="utf-8", newline="\n")
    root = tmp_path / "root"
    r = subprocess.run([BASH, (probes / "s2_batch.sh").as_posix(), (tmp_path / "ids.tsv").as_posix(), root.as_posix(), "1", "1", "G:6-31g*:75,302"],
                       capture_output=True, text=True, encoding="utf-8", timeout=60, check=False, env={**os.environ, "MAX_FIRST": "999"})
    assert r.returncode == 0, r.stderr
    assert (root / "A_own.log").read_text(encoding="utf-8").strip() == "MAX_FIRST=4321"
    assert (root / "A_batch.log").read_text(encoding="utf-8").strip() == "MAX_FIRST=999"
