"""tools/github_threads.py (TASKS 105): a maintainer's comment, review or review comment on our threads is reported once; ours and bots'
never; --seed records without reporting."""
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import github_threads as gt  # noqa: E402  (after the sys.path insert)

NOW = datetime(2026, 10, 24, 22, 0, tzinfo=UTC)
PR = {"repository_url": "https://api.github.com/repos/grimme-lab/dxtb", "number": 278, "html_url": "https://github.com/grimme-lab/dxtb/pull/278",
      "pull_request": {}}


def _api(comments: list[dict], reviews: list[dict] = ()):
    pages = {
        "search/issues?q=involves:thebreadishard+-user:thebreadishard+updated:>=2026-09-24&per_page=100": {"items": [PR]},
        "repos/grimme-lab/dxtb/issues/278/comments?per_page=100": comments,
        "repos/grimme-lab/dxtb/pulls/278/reviews?per_page=100": list(reviews),
        "repos/grimme-lab/dxtb/pulls/278/comments?per_page=100": [],
    }
    return pages.__getitem__


MAINTAINER = {"id": 1, "user": {"login": "marvinfriede", "type": "User"}, "created_at": "2026-10-18T17:50:00Z",
              "body": "Thanks! Can this be merged?", "html_url": "https://github.com/grimme-lab/dxtb/pull/278#issuecomment-1"}
OURS = {"id": 2, "user": {"login": "thebreadishard", "type": "User"}, "created_at": "2026-10-24T20:00:00Z", "body": "Thank you!"}
BOT = {"id": 3, "user": {"login": "codecov[bot]", "type": "Bot"}, "created_at": "2026-10-18T16:28:00Z", "body": "Coverage report"}


def test_a_maintainers_question_is_reported_once(tmp_path):
    seen = tmp_path / "seen.txt"
    first = gt.new(_api([MAINTAINER, OURS, BOT]), seen, now=NOW)
    assert first == ["grimme-lab/dxtb#278 marvinfriede 2026-10-18 17:50: Thanks! Can this be merged? — "
                     "https://github.com/grimme-lab/dxtb/pull/278#issuecomment-1"]
    assert gt.new(_api([MAINTAINER, OURS, BOT]), seen, now=NOW) == []


def test_a_review_counts_and_seed_reports_nothing(tmp_path):
    seen = tmp_path / "seen.txt"
    review = {"id": 9, "user": {"login": "sunqm", "type": "User"}, "submitted_at": "2026-10-06T19:00:00Z", "state": "APPROVED", "body": ""}
    assert gt.new(_api([MAINTAINER], [review]), seen, seed=True, now=NOW) == []
    assert set(seen.read_text(encoding="utf-8").split()) == {"comment:1", "review:9"}
    later = {**MAINTAINER, "id": 4, "body": "One more thing"}
    assert [x.split(": ", 1)[1].split(" —")[0] for x in gt.new(_api([MAINTAINER, later], [review]), seen, now=NOW)] == ["One more thing"]


def test_an_approval_without_text_shows_its_state(tmp_path):
    review = {"id": 9, "user": {"login": "sunqm", "type": "User"}, "submitted_at": "2026-10-06T19:00:00Z", "state": "APPROVED", "body": ""}
    (got,) = gt.new(_api([], [review]), tmp_path / "seen.txt", now=NOW)
    assert "sunqm 2026-10-06 19:00: APPROVED" in got
