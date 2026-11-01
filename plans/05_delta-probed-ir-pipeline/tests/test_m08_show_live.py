"""The pipeline show's live server (`modules/08_industry_synthesis/m08/show_live.py`, TASKS 146) on this machine only: the page with its
Live button on, the newest run's progress with each station's text, the result once the run is finished (a recorded run's copy), and
refusals for an unfinished run and a folder name that is not a plain name."""
from __future__ import annotations

import json
import os
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import show as S
from m08 import show_live as L
from m08.progress import Progress

CINNOLINE = S.RESULTS / "pipeline_rehearsal_2026-10-30" / "cinnoline"


@pytest.fixture
def server(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    done = runs / "cinnoline"
    shutil.copytree(CINNOLINE, done)
    p = Progress(done, "cinnoline", "0.9", {"smiles": "c1ccc2nnccc2c1", "formula": "C8H6N2", "n_atoms": 16})
    for s in L.STEPS:
        p.start(s)
        p.done(s)
    p.finish()
    running = runs / "benzene"
    running.mkdir()
    q = Progress(running, "benzene", "0.9", {"smiles": "c1ccccc1", "formula": "C6H6", "n_atoms": 12})
    q.start("molecule")
    q.done("molecule")
    q.start("geometry")
    q.done("geometry")
    q.reused("optimise", 30.5)
    q.reused("hessian", 3212)
    q.start("network")
    now = time.time()
    os.utime(done / "progress.json", (now - 60, now - 60))           # the running one is the newest
    httpd = ThreadingHTTPServer((L.HOST, 0), L.make_handler(L.live_page((CINNOLINE,)), runs))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://{L.HOST}:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.status, r.read().decode("utf-8")


def test_the_page_has_its_live_button_on(server):
    status, page = get(server + "/")
    assert status == 200 and '"live": true' in page and 'id="modeLive"' in page


def test_the_newest_run_s_progress_names_each_station(server):
    _, body = get(server + "/progress")
    p = json.loads(body)
    assert p["folder"] == "benzene" and p["route"] == "reused" and not p["finished"]
    assert [s["state"] for s in p["stations"]] == ["done", "done", "reused", "reused", "active", "pending"]
    assert p["stations"][2]["time"] == "from the corpus · 30 s" and p["stations"][3]["time"] == "from the corpus · 54 min"
    assert p["stations"][4]["time"] == "running…" and p["stations"][0]["time"] == "checked before any computation"
    assert "currentColor" in p["molecule"]["depiction"]


def test_a_finished_run_gives_its_result_and_an_unfinished_one_waits(server):
    _, body = get(server + "/result?folder=cinnoline")
    m = json.loads(body)
    assert m["name"] == "cinnoline" and m["real_time"] == "Real time: 21 min on the laptop in all"
    with pytest.raises(urllib.error.HTTPError) as e:
        get(server + "/result?folder=benzene")
    assert e.value.code == 409


@pytest.mark.parametrize("name", ["..%2F..%2Fsecrets", "a%20b", "missing"])
def test_a_folder_that_is_not_a_run_s_plain_name_is_refused(server, name):
    with pytest.raises(urllib.error.HTTPError) as e:
        get(server + f"/result?folder={name}")
    assert e.value.code == 404
