"""probes/rungC_chain_lines_read.py (4 Oct 2026): the line parser, the seed summary and the decision-51 cap check on a synthetic record."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SCRIPT = HERE / "probes" / "rungC_chain_lines_read.py"


def _record(path: Path, others=(2.5, 3.4), ratios=(0.20, 0.24), best=(90, 150)):
    seeds = []
    for i, (o, r, b) in enumerate(zip(others, ratios, best, strict=True)):
        hold = {"diag_rms": {"ring-ip": 2.0 + i * 0.1, "CH-stretch": 1.0, "CH-oop": 3.0, "other": o}, "coupling_ratio": r,
                "corrected_freq_rms": 2.6, "dH_residual_ratio": 0.14}
        seeds.append({"seed": i, "best_epoch": b, "a": hold, "b": dict(hold)})
    path.write_text(json.dumps({"date": "2026-10-04 02:00", "model": {"kdiag_mode": "family"}, "curve": {"750": {"per_seed": seeds}}}), encoding="utf-8")
    return path


def _run(out, rec, *extra):
    r = subprocess.run([sys.executable, str(SCRIPT), str(out), str(rec), *extra], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       check=False)
    assert r.returncode == 0, r.stderr
    return json.load(open(str(out) + ".json", encoding="utf-8")), (Path(str(out) + ".md")).read_text(encoding="utf-8")


def test_lines_are_read_on_seed_means(tmp_path):
    rec = _record(tmp_path / "r.json")
    res, md = _run(tmp_path / "read", rec, "--line", "other<=3", "--line", "ring-ip<=3", "--line", "ratio<=0.25")
    by = {ln["line"]: ln for ln in res["lines"]}
    assert abs(by["other<=3"]["value"] - 2.95) < 1e-9 and by["other<=3"]["met"] is True        # mean of 2.5 and 3.4
    assert by["ring-ip<=3"]["met"] is True and abs(by["ratio<=0.25"]["value"] - 0.22) < 1e-9
    assert res["all_met"] is True and "All lines met: yes" in md and res["record"]["kdiag_mode"] == "family"


def test_a_failed_line_and_the_cap_check(tmp_path):
    rec = _record(tmp_path / "r.json", others=(3.5, 3.6), best=(90, 185))
    res, md = _run(tmp_path / "read", rec, "--line", "other<=3", "--cap", "200")
    assert res["all_met"] is False and "not met" in md
    assert res["near_cap_seeds"] == [185] and "Decision 51" in md


def test_against_record_gives_differences(tmp_path):
    rec = _record(tmp_path / "r.json")
    ref = _record(tmp_path / "ref.json", others=(4.0, 4.2))
    res, md = _run(tmp_path / "read", rec, "--against", str(ref), "--line", "other<=3")
    assert res["against"]["a"]["other"]["mean"] == 4.1 and "| other | 2.95" in md and "-1.15" in md
