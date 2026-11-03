"""The show's replay draws the lit line along the route (the user's screenshot, 3 Nov 2026: on the corpus line it cut from the start geometry
straight to the corpus stop, past the bend). `ride()` is taken from the template and run in node with stubs for the page: every path it
draws must be the route up to some point plus one point on the next leg."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

TEMPLATE = Path(__file__).resolve().parents[1] / "modules" / "08_industry_synthesis" / "m08" / "show_template.html"
# a corpus-line route with bends, as geometryDown() lays it out: main 0, main 1, bend, stop, bend, main 4, main 5
CORPUS_ROUTE = [[100, 0], [100, 100], [20, 180], [20, 300], [20, 420], [100, 500], [100, 600]]
MAIN_ROUTE = [[100, 100 * i] for i in range(6)]
HARNESS = """
const drawn = [];
const STEP_DWELL = 3, STEP_TRAVEL = 2, CORPUS_DWELL = 2;
const state = {running: false, finished: false, timers: []};
const el = () => ({ disabled: false, textContent: "", setAttribute(k, v) { if (k === "d") drawn.push(v); } });
const els = {};
const $ = (sel) => (els[sel] = els[sel] || el());
const ROUTES = %s;
const geometry = () => ({ main: ROUTES.main, corpus: ROUTES.corpus });
function later(fn, ms) { setTimeout(fn, ms); }
function setStation() {}
function resetResult() {}
function follow() {}
function pathD(pts) { return pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" "); }
function animateTo(from, to, ms, run, done) {
  /* three frames per leg; the finishing timer comes later than the leg's nominal end, as in the page (ms + 30) */
  [0.25, 0.5, 0.75].forEach((e, i) => setTimeout(() => run([from[0] + (to[0] - from[0]) * e, from[1] + (to[1] - from[1]) * e]), i));
  setTimeout(() => { run(to); done(); }, ms + 30);
}
function showResult() { console.log(JSON.stringify(drawn)); }
%s
const stations = Array(6).fill({ time: "1 s" });
ride({ route: "%s", stations, real_time: "" });
"""


def ride_source() -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"^function ride\(m\) \{.*?^\}$", text, re.M | re.S)
    if not m:
        raise AssertionError("no ride() in the template")
    return m.group(0)


def points(d: str) -> list[list[float]]:
    return [[float(x), float(y)] for x, y in re.findall(r"[ML](-?[\d.]+) (-?[\d.]+)", d)]


def on_segment(p, a, b) -> bool:
    cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    inside = min(a[0], b[0]) - 1e-6 <= p[0] <= max(a[0], b[0]) + 1e-6 and min(a[1], b[1]) - 1e-6 <= p[1] <= max(a[1], b[1]) + 1e-6
    return abs(cross) < 1e-6 and inside


def drawn_paths(route_kind: str, tmp_path: Path) -> list[str]:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    js = tmp_path / "ride.js"
    js.write_text(HARNESS % (json.dumps({"main": MAIN_ROUTE, "corpus": CORPUS_ROUTE}), ride_source(), route_kind), encoding="utf-8")
    out = subprocess.run([node, str(js)], capture_output=True, text=True, check=False, timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize(("kind", "route"), [("reused", CORPUS_ROUTE), ("computed", MAIN_ROUTE)])
def test_the_lit_line_follows_the_route_through_every_bend(kind, route, tmp_path):
    paths = [points(d) for d in drawn_paths(kind, tmp_path) if d]
    assert paths, "ride() drew nothing"
    for pts in paths:
        k = len(pts) - 2                      # the route points passed; the last point is the token on the leg from route[k]
        assert pts[:-1] == [[float(x), float(y)] for x, y in route[:k + 1]], f"a drawn path left the route: {pts}"
        assert on_segment(pts[-1], route[k], route[k + 1]) or pts[-1] == [float(c) for c in route[k + 1]], f"the token is off its leg: {pts}"
    assert paths[-1] == [[float(x), float(y)] for x, y in route], "the finished line is not the whole route"
