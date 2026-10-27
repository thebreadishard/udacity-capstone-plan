"""tools/ruff_gate.py: the diff parser, the line filter, the function rule, whole files, syntax errors and the command line's three modes."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import ruff_gate as RG

pytest.importorskip("ruff")

DIFF = """\
diff --git a/plans/p/x.py b/plans/p/x.py
--- a/plans/p/x.py
+++ b/plans/p/x.py
@@ -3,0 +4,2 @@ def f():
+a
+b
@@ -10 +12 @@
-old
+new
@@ -20,3 +22,0 @@
-gone
diff --git a/other/y.py b/other/y.py
--- /dev/null
+++ b/other/y.py
@@ -0,0 +1,3 @@
"""


def write(tmp_path: Path, text: str, name: str = "m.py") -> Path:
    f = tmp_path / name
    f.write_text(text, encoding="utf-8", newline="\n")
    return f


def test_parse_diff_keeps_added_and_changed_lines_under_the_plan(tmp_path):
    within = tmp_path / "plans" / "p"
    # a pure deletion (+22,0) adds no line; a file outside `within` is left out
    assert RG.parse_diff(DIFF, tmp_path, within) == {(within / "x.py").resolve(): {4, 5, 12}}


def test_findings_only_on_the_given_lines(tmp_path):
    f = write(tmp_path, "import os\nimport sys\n\nprint(sys.argv)\n")      # F401 on line 1
    assert RG.findings({f: {4}}) == []
    got = RG.findings({f: {1}})
    assert len(got) == 1 and ":1:" in got[0] and " F401 " in got[0]


def test_a_file_without_a_span_is_checked_whole(tmp_path):
    f = write(tmp_path, "import os\n")
    assert any(" F401 " in x for x in RG.findings({f: None}))


def test_a_function_rule_counts_for_every_line_of_its_function(tmp_path):
    f = write(tmp_path, "def f(a, b, c, d, e, g, h):\n    x = a + b\n    return x + c + d + e + g + h\n\n\nprint(f(1, 2, 3, 4, 5, 6, 7))\n")
    assert any(" PLR0913 " in x for x in RG.findings({f: {2}}))          # a body line changed: seven arguments, the set allows six
    assert not any(" PLR0913 " in x for x in RG.findings({f: {6}}))      # a line outside the function


def test_a_syntax_error_is_reported(tmp_path):
    f = write(tmp_path, "def f(:\n")
    assert RG.findings({f: {1}})


def test_parse_span():
    assert RG.parse_span("a/b.py:3-5") == (Path("a/b.py"), {3, 4, 5})
    assert RG.parse_span(r"C:\x\b.py") == (Path(r"C:\x\b.py"), None)


def test_main_needs_exactly_one_mode():
    for argv in ([], ["--staged", "x.py"], ["--staged", "--range", "a..b"]):
        with pytest.raises(SystemExit):
            RG.main(argv)


def test_main_staged_and_range_read_the_diff_they_name(monkeypatch):
    seen = []
    monkeypatch.setattr(RG, "changed_lines", lambda args: seen.append(args) or {})
    assert RG.main(["--staged"]) == 0 and RG.main(["--range", "a1..b2"]) == 0
    assert seen == [["--cached"], ["a1..b2"]]


def test_main_exit_code_follows_the_findings(tmp_path, capsys):
    bad, good = write(tmp_path, "import os\n", "bad.py"), write(tmp_path, "print(1)\n", "good.py")
    assert RG.main([f"{bad}:1-1"]) == 1 and " F401 " in capsys.readouterr().out
    assert RG.main([str(good)]) == 0
