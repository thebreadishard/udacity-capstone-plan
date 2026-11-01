"""A pipeline run's progress for the live show (TASKS 146): one small JSON beside the result, `progress.json`, rewritten at every step, so
that a page can follow a run while it computes. The six steps are the show's stations; a step is pending, active, done (with its seconds
on this machine) or reused (taken from the corpus, with the seconds it took when the corpus computed it). The file is written to a temp
file and moved over the old one, so a reader never sees half of it."""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

STEPS = ("molecule", "geometry", "optimise", "hessian", "network", "spectrum")
FILE = "progress.json"


class Progress:
    """The progress record of one run folder."""

    def __init__(self, folder: Path, name: str, version: str, molecule: dict) -> None:
        self.path = folder / FILE
        self.started: dict[str, float] = {}
        self.record = {"name": name, "pipeline_version": version, "molecule": molecule, "finished": False,
                       "steps": {s: {"state": "pending"} for s in STEPS}, "updated": ""}
        self._write()

    @classmethod
    def load(cls, folder: Path) -> Progress:
        """A folder's record as it was last written (the certificate, written after the run returns, finishes it)."""
        self = cls.__new__(cls)
        self.path = folder / FILE
        self.started = {}
        self.record = json.loads(self.path.read_text(encoding="utf-8"))
        return self

    def _step(self, step: str) -> dict:
        if step not in STEPS:
            raise ValueError(f"unknown step {step!r}: one of {STEPS}")
        return self.record["steps"][step]

    def start(self, step: str) -> None:
        self._step(step).update(state="active")
        self.started[step] = time.time()
        self._write()

    def done(self, step: str) -> None:
        if step not in self.started:
            raise ValueError(f"{step} is done but never started")
        self._step(step).update(state="done", seconds=round(time.time() - self.started[step], 1))
        self._write()

    def reused(self, step: str, seconds_then: float) -> None:
        self._step(step).update(state="reused", seconds_then=float(seconds_then))
        self._write()

    def finish(self) -> None:
        unfinished = [s for s, v in self.record["steps"].items() if v["state"] not in ("done", "reused")]
        if unfinished:
            raise ValueError(f"the run finishes with steps not done: {unfinished}")
        self.record["finished"] = True
        self._write()

    def _write(self) -> None:
        self.record["updated"] = datetime.now().isoformat(timespec="seconds")
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.record, indent=1), encoding="utf-8")
        tmp.replace(self.path)
