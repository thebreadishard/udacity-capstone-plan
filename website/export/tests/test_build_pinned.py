"""Pinned output of the Spectrum Atlas export on nine molecules of the real corpus (TASKS 272): the regression test that guards a
restructuring of `build_catalog.build()`.

The fixture covers every branch of the export loop: benzene (anchored, validated, second route, screen flag, replaced by the second
route), naphthalene (anchored), a healed and a genuine imaginary mode, an analytic-only D molecule with heights and the analytic-only
coronene whose APT failed, a cation, a pending generator row and a failed row. The golden holds `catalog.json`, every molecule file and
`summary.json` as the build wrote them; the summary keys read from sources outside the fixture (the time stamp, the source hashes, the
changelog, the carried network's accuracy, licence and pair) move with every finished run, so they are compared with their sources here
rather than pinned.

When the corpus itself changes one of these molecules, record the golden again from a commit whose export is trusted:
    python website/export/tests/test_build_pinned.py --record
"""
import argparse
import csv
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build_catalog as bc  # noqa: E402

REPO = os.environ.get("ATLAS_REPO") or str(HERE.parents[2])
PLAN = os.path.join(REPO, "plans", "05_delta-probed-ir-pipeline")
CORPUS = os.path.join(PLAN, "modules", "05_support_predictor", "corpus")
GOLDEN = HERE / "golden" / "pinned_export.json"
PINNED_IDS = ("A_8448043181", "A_01f3186607", "A2_13eea56ee5", "A2_0420908ebe", "D_210c3076e6", "T_94b3a9d13a", "P3c_8448043181",
              "G_b0c5495a20", "A2_12c940207d")
UNPINNED_SUMMARY_KEYS = ("built_utc", "sources", "n_changelog", "shape_accuracy", "licence", "networks")
LEDGER_MD = os.path.join(PLAN, "GoalGathering", "notes", "Mandate_2026-09-13_Affordable_Plan_Obstacle_Ledger.md")


def _read(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def export_of(out: Path, summary: dict) -> dict:
    """The pinned part of one build's output: its catalogue, every molecule file and the summary without the unpinned keys."""
    return dict(ids=list(PINNED_IDS), catalog=_read(out / "catalog.json"),
                molecules={p.stem: _read(p) for p in sorted((out / "molecules").glob("*.json"))},
                summary={k: v for k, v in summary.items() if k not in UNPINNED_SUMMARY_KEYS})


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    if not os.path.isdir(os.path.join(CORPUS, "molecules", PINNED_IDS[0])):
        pytest.skip("no corpus data in this checkout (set ATLAS_REPO)")
    out = tmp_path_factory.mktemp("atlas_pinned")
    return out, bc.build(REPO, str(out), ids=set(PINNED_IDS))


def test_export_matches_the_golden(built):
    out, summary = built
    golden = _read(GOLDEN)
    assert golden["ids"] == list(PINNED_IDS), "the golden was recorded for another fixture; record it again"
    got = export_of(out, summary)
    assert got["catalog"] == golden["catalog"]
    assert sorted(got["molecules"]) == sorted(golden["molecules"])
    for mid, mol in golden["molecules"].items():
        assert got["molecules"][mid] == mol, mid
    assert got["summary"] == golden["summary"]
    on_disk = _read(out / "summary.json")
    assert {k: v for k, v in on_disk.items() if k not in UNPINNED_SUMMARY_KEYS} == golden["summary"]


def test_unpinned_summary_keys_come_from_their_sources(built):
    from m08 import pipeline
    from m08.accuracy import carried_accuracy
    from m08.licence import state
    _, summary = built
    assert set(summary) == set(_read(GOLDEN)["summary"]) | set(UNPINNED_SUMMARY_KEYS)
    assert summary["sources"] == dict(manifest=bc.sha256(os.path.join(CORPUS, "manifest.csv")),
                                      ledger=bc.sha256(os.path.join(CORPUS, "ledger.csv")))
    assert summary["n_changelog"] == len(bc.read_changelog(LEDGER_MD))
    accuracy = carried_accuracy()
    licence = state(accuracy)
    assert summary["shape_accuracy"] == accuracy
    assert summary["licence"] == {k: licence[k] for k in ("licensed_families", "statement", "rule_source")} | {
        "line_cm": bc.licence_line(accuracy)}
    with open(os.path.join(CORPUS, "manifest.csv"), encoding="utf-8") as f:
        manifest = list(csv.DictReader(f))
    assert summary["networks"] == bc.network_pair(pipeline, manifest)


def record() -> None:
    """Build the fixture and write its pinned part as the golden (a temp file moved over the old one)."""
    with tempfile.TemporaryDirectory() as tmp:
        summary = bc.build(REPO, tmp, ids=set(PINNED_IDS))
        text = json.dumps(export_of(Path(tmp), summary), ensure_ascii=False, indent=0, sort_keys=True)
    GOLDEN.parent.mkdir(exist_ok=True)
    fd, part = tempfile.mkstemp(dir=GOLDEN.parent, suffix=".part")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    os.replace(part, GOLDEN)
    print(f"recorded {GOLDEN} ({len(text)} characters)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", action="store_true", required=True, help="write the golden from this checkout's export")
    ap.parse_args()
    record()
