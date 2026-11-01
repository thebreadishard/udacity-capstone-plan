"""The pipeline show's live mode (TASKS 146): a web server on this machine only (127.0.0.1) that serves the show page with its Live button
on, the progress of the newest run under --runs (pipeline 0.9's `progress.json`), and that run's molecule once its certificate is
written. The page starts no run: a run starts as every run does (a run spec, or `python -m m08.pipeline ... --out <runs>`), and the page
follows it.

    python -m m08.show_live --runs <folder> [--port 8765] [--replay <result folder> ...]
"""
from __future__ import annotations

import argparse
import json
import re
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import show as S
from .progress import FILE, STEPS

HOST = "127.0.0.1"                     # this machine only: the server reads result folders and must not be reachable from the network
FOLDER_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def newest(runs: Path) -> Path | None:
    """The run folder under `runs` whose progress record was written last, or None."""
    records = sorted(runs.glob(f"*/{FILE}"), key=lambda p: p.stat().st_mtime)
    return records[-1].parent if records else None


@lru_cache(maxsize=64)
def depiction(smiles: str) -> str:
    return S.depiction(smiles)


def station_time(step: str, entry: dict) -> str:
    """What a station says of its step: running, its seconds on this machine, or the corpus's seconds for a reused step."""
    if entry["state"] == "active":
        return "running…"
    if entry["state"] == "reused":
        return f"from the corpus · {S.duration(entry['seconds_then'])}"
    if entry["state"] == "done":
        return "checked before any computation" if step == "molecule" else f"{S.duration(entry['seconds'])} on this machine"
    return ""


def progress_view(folder: Path) -> dict:
    """The page's view of a run's progress record: each station's state and text, the route once the corpus has answered, the molecule."""
    rec = json.loads((folder / FILE).read_text(encoding="utf-8"))
    steps = rec["steps"]
    route = "reused" if steps["optimise"]["state"] == "reused" else ("computed" if steps["optimise"]["state"] != "pending" else "unknown")
    mol = rec["molecule"]
    return {"folder": folder.name, "name": rec["name"], "pipeline_version": rec["pipeline_version"], "finished": rec["finished"],
            "route": route, "molecule": {**mol, "depiction": depiction(mol["smiles"]) if mol.get("smiles") else ""},
            "stations": [{"state": steps[s]["state"], "time": station_time(s, steps[s])} for s in STEPS]}


def result_view(folder: Path) -> dict | None:
    """The run's molecule as the replay shows one, once the run is finished and its certificate written; None before."""
    rec = json.loads((folder / FILE).read_text(encoding="utf-8"))
    if not rec["finished"] or not (folder / "certificate.json").exists():
        return None
    return S.molecule(folder)


def make_handler(page: str, runs: Path) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: str, kind: str = "application/json") -> None:
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", f"{kind}; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            url = urlparse(self.path)
            if url.path == "/":
                self._send(200, page, "text/html")
            elif url.path == "/progress":
                folder = newest(runs)
                self._send(200, json.dumps(progress_view(folder) if folder else None))
            elif url.path == "/result":
                name = parse_qs(url.query).get("folder", [""])[0]
                if not FOLDER_NAME.match(name) or not (runs / name / FILE).exists():
                    self._send(404, json.dumps({"error": f"no run folder {name!r}"}))
                    return
                view = result_view(runs / name)
                self._send(200 if view else 409, json.dumps(view if view else {"error": "the run is not finished"}))
            else:
                self._send(404, json.dumps({"error": "not found"}))

        def log_message(self, format: str, *args: object) -> None:
            return                       # quiet: the page polls once a second

    return Handler


def live_page(replay: tuple[Path, ...]) -> str:
    """The show page with the replay runs and the Live button on."""
    return S.page({**S.payload(replay), "live": True})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--runs", type=Path, required=True, help="the folder the live runs write into (the pipeline's --out)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--replay", nargs="*", type=Path, default=list(S.DEFAULT_RUNS), help="result folders the page also replays")
    a = ap.parse_args(argv)
    if not a.runs.is_dir():
        raise SystemExit(f"{a.runs}: not a folder")
    server = ThreadingHTTPServer((HOST, a.port), make_handler(live_page(tuple(a.replay)), a.runs.resolve()))
    print(f"[show] live at http://{HOST}:{a.port}/ — following the newest run in {a.runs.resolve()} (Ctrl+C stops)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
