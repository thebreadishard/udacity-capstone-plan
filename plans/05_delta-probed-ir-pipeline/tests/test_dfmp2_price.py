"""probes/dfmp2_price.py on a synthetic run log before the real one: rows are attributed to the molecule and basis of the header above them,
a row of another basis under a header is refused, peak RSS is read from the markers, an exact power law is recovered and priced, and one
size alone gives no power law."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
P = pytest.importorskip("dfmp2_price")


def law(n, a, b):
    return math.exp(a) * n ** b


def synthetic_log(a_dz=-2.0, b_dz=3.5, a_tz=-1.0, b_tz=4.0):     # hundreds of seconds and more: the log's whole seconds round little
    lines = ["=== (DF) start: psi4 1.10.2, 16 cores 2026-10-19 22:25:40", "[22:26:00] water cc-pvdz: max |analytic - findif| 1.0e-08 Eh/bohr"]
    for mol, n in (("pyridine", 11), ("naphthalene", 18)):
        for basis, a, b in (("cc-pvdz", a_dz, b_dz), ("cc-pvtz", a_tz, b_tz)):
            short = basis.replace("-", "")
            lines.append(f"[22:30:00] 3 rows of /mnt/c/x/mp2_rows_{mol}_{short}.npz at {basis}, 0 already done")
            lines += [f"[22:31:00] df-mp2 {basis} k={k}: H_kk +0.5 ({round(law(n, a, b))} s)" for k in range(3)]
            lines.append(f"=== (DF) {mol} {short} done, peak RSS {2_000_000 if basis == 'cc-pvtz' else 900_000} kB 2026-10-19 23:00:00")
    return "\n".join(lines)


def test_rows_and_peaks_are_attributed_and_an_exact_law_is_priced():
    times, rss = P.parse(synthetic_log())
    assert sorted(times) == [("naphthalene", "cc-pvdz"), ("naphthalene", "cc-pvtz"), ("pyridine", "cc-pvdz"), ("pyridine", "cc-pvtz")]
    assert rss[("naphthalene", "cc-pvtz")] == 2_000_000 and len(times[("pyridine", "cc-pvdz")]) == 3
    res = P.price(times)
    assert abs(res["fits"]["cc-pvtz"]["b"] - 4.0) < 0.01 and abs(res["fits"]["cc-pvdz"]["b"] - 3.5) < 0.01
    quinoxaline = res["anchors"]["quinoxaline"]
    assert quinoxaline["rows"] == 24
    assert quinoxaline["hours"] == pytest.approx(24 * (law(16, -2.0, 3.5) + law(16, -1.0, 4.0)) / 3600, rel=0.02)


def test_a_row_of_another_basis_under_a_header_is_refused():
    bad = "[22:30:00] 3 rows of /x/mp2_rows_pyridine_ccpvdz.npz at cc-pvdz, 0 already done\n[22:31:00] df-mp2 cc-pvtz k=0: H_kk +0.5 (10 s)"
    with pytest.raises(SystemExit, match="under a cc-pvdz header"):
        P.parse(bad)


def test_one_size_gives_no_power_law():
    with pytest.raises(SystemExit, match="one size only"):
        P.power_law([(11, 10.0), (11, 12.0)])


def test_the_report_is_written(tmp_path):
    log = tmp_path / "run.log"
    log.write_text(synthetic_log(), encoding="utf-8")
    assert P.main([str(log), "--out", str(tmp_path / "price")]) == 0
    assert "All five" in (tmp_path / "price.md").read_text(encoding="utf-8")
