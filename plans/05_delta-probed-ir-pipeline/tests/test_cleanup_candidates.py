"""tools/cleanup_candidates.py (TASKS 42, 11 Oct 2026): the rules that decide a removal, on synthetic files; nothing is removed."""
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
from cleanup_candidates import candidates, code_lines, evidence, fixed_point, mention, referrers  # noqa: E402

R = "plans/05_delta-probed-ir-pipeline"


def test_dated_one_offs_and_superseded_tools_are_candidates():
    files = [f"{R}/probes/night_1003.sh", f"{R}/probes/night2_1003.sh", f"{R}/probes/watch.sh", f"{R}/tools/backup_loop.sh",
             f"{R}/probes/results_m1/x/run_1003.sh", "website/x_1003.sh"]
    assert set(candidates(files)) == {f"{R}/probes/night_1003.sh", f"{R}/probes/night2_1003.sh", f"{R}/tools/backup_loop.sh"}


def test_a_name_counts_only_as_a_whole_word():
    assert mention("night_1003.sh").search("bash probes/night_1003.sh &")
    assert not mention("night_1003.sh").search("bash probes/xnight_1003.sh.bak")


def test_comment_lines_keep_nothing_and_a_kept_referrer_keeps_its_target():
    a, b, c = f"{R}/probes/a_1003.sh", f"{R}/probes/b_1003.sh", f"{R}/probes/keep.sh"
    texts = {a: "bash probes/b_1003.sh\n", b: "echo b\n", c: "# was: probes/a_1003.sh\nrem probes/a_1003.sh\n",
             f"{R}/probes/results_m1/run/copy.sh": "bash probes/a_1003.sh\n"}
    refs = referrers([a, b], texts)
    assert refs[a] == [] and refs[b] == [a]                      # c's mentions are comments; the run record is not kept code
    assert fixed_point([a, b], refs) == {a, b}                   # b is named only by a, which goes too
    texts[c] = "bash probes/a_1003.sh\n"
    refs = referrers([a, b], texts)
    assert fixed_point([a, b], refs) == set()                    # c keeps a, and a keeps b
    assert "x" == code_lines("# y\nx")


def test_evidence_by_name_by_chain_or_lever_or_by_output(tmp_path):
    docs = {"GoalGathering/notes/ledger.md": "chain 24 read: 0.33. Lever 5 stopped.", "x/TASKS.md": "probes/named_1003.sh ran",
            "GoalGathering/Papers.md": "lever 7 of the review"}
    assert evidence("probes/named_1003.sh", "", docs)[0] == "named"
    assert evidence("probes/c_1003.sh", "#!/bin/bash\n# Chain 24, 2 Oct 2026\n", docs) == ("chain 24 recorded", "GoalGathering/notes/ledger.md")
    assert evidence("probes/p_1003.sh", "#!/bin/bash\n# Lever 7\n", docs) is None              # a reading list is not a record
    assert evidence("probes/l_1003.sh", "#!/bin/bash\n# Lever 5 (2 Oct)\n", docs)[0] == "lever 5 recorded"
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "r.log").write_text("done", encoding="utf-8")
    assert evidence("probes/o_1003.sh", "python x.py > out/r.log\n", {}, plan=str(tmp_path)) == ("output on disk", "out/r.log")
    assert evidence("probes/n_1003.sh", "echo\n", {}, plan=str(tmp_path)) is None
