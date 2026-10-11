"""tools/run_test_suites.py (11 Oct 2026): parsing pytest's closing line, the verdict rule, the pyscf file discovery and the state.sh line;
no suite is run here."""
import datetime
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
from run_test_suites import counts, pyscf_tests, summary, verdict  # noqa: E402


def test_counts_read_the_closing_line():
    assert counts("3 failed, 327 passed, 7 skipped, 1 deselected, 4 warnings in 118.42s") == {
        "failed": 3, "passed": 327, "skipped": 7, "deselected": 1}
    assert counts("26 skipped, 9 deselected, 5 errors in 14.48s")["error"] == 5
    assert counts("timeout after 1800 s") == {}


def test_a_pass_needs_exit_zero_and_a_passed_test():
    assert verdict(0, {"passed": 4}) == "pass"
    assert verdict(1, {"passed": 4, "failed": 1}) == "FAIL"
    assert verdict(5, {}) == "FAIL"                              # nothing collected
    assert verdict(0, {"skipped": 3}) == "FAIL"                  # everything skipped is not a check


def test_pyscf_tests_are_found_by_their_importorskip(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text('pytest.importorskip("pyscf")\n', encoding="utf-8")
    (tmp_path / "tests" / "test_b.py").write_text("import numpy\n", encoding="utf-8")
    assert pyscf_tests(str(tmp_path)) == ["tests/test_a.py"]
    assert "tests/test_apt_route_c.py" in pyscf_tests()


def test_summary_flags_failures_and_a_stale_result():
    now = datetime.datetime(2026, 10, 12, 4, 0)
    rows = [dict(suite="module 08", verdict="pass", counts={"passed": 11}), dict(suite="module 07", verdict="FAIL", counts={"passed": 28, "failed": 1})]
    line = summary(dict(finished="2026-10-12T03:34:00", suites=rows), now)
    assert "1/2 pass, 39 tests" in line and "FAILED: module 07" in line and "STALE" not in line
    assert "STALE" in summary(dict(finished="2026-10-09T03:34:00", suites=rows[:1]), now)
    assert "never run" in summary(None)
