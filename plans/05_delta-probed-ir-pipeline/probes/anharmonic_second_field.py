"""A second GFN2-xTB force field of a molecule the pipeline has run, for check 1 of the anharmonic step's first-run checks
(TASKS 211; GoalGathering/notes/PreRegistration_2026-11-20_Anharmonic_Step_Substituted_Molecule.md, part A).

    python anharmonic_second_field.py start --run <pipeline result folder> --candidates <geometry.json> [...] --out <folder>
    python anharmonic_second_field.py reference --run <pipeline result folder> --x-dir <X folder> --label <gvpt2 json> --out <folder>

`start`: of the stored B3LYP minima named as candidates, the one farthest from the run's own (rms after rotation) becomes the
start of the second force field: <out>/ref.json, the record probes/xtb_field_for_step.sh starts from, and <out>/start.json
with every candidate's distance.

`reference`: the same-network, same-artefact reference the checks compare a run with, as the benzene reference of 19 Nov 2026
was built (results_m1/anharmonic_step_2026-11-16/stored_field_demo.py on the run's own steps 1-5, by
results_m1/anharmonic_reference_v14release_v3_2026-11-19/build_reference.py): a copy of the run's steps 1-5 files, the
pipeline's own step 6 on them, and one stand-in — the force field is the stored second one, its modes rotated onto the run's
frame, instead of a new WSL run. Run and reference then differ in the force field only. Writes <out>/<name>/{pipeline.json,
anharmonic.json, certificate.json, certificate.md}; an existing folder is never overwritten.

Check 1 itself is read by the unchanged results_m1/anharmonic_step_2026-11-17/first_run_checks.py <run> --reference
<out>/<name> --out <a file outside the run folder>.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import anharmonic as AN  # noqa: E402
from m08 import live_certificate as LC  # noqa: E402
from m08 import pipeline as P  # noqa: E402
from m08.catalog import Catalog  # noqa: E402

# isort: split
import anharmonic_step as AS  # noqa: E402
from frame_match import Frame, frame_onto  # noqa: E402
from s2_read import write_atomic  # noqa: E402

# what steps 1-5 of a run leave and step 6 reads or the certificate cites
COPIED = ("pipeline.json", "geometry.json", "hessian_b3lyp_analytic.npz", "correction.npz", "dipole_b3lyp_cphf.npz", "analytic_check.json",
          "result.json")
SETTINGS = (4, 2, 1536, 120)      # threads, shards, cap in MB, minutes: the record's settings of a step whose force field is not run here


@dataclass(frozen=True)
class ReferenceConfig:
    """One reference: the run it is built on, the stored second force field (its X folder and GVPT2 file), and where it goes."""
    run: Path
    x_dir: Path
    label: Path
    out: Path

    def __post_init__(self) -> None:
        for needed in (*(self.run / name for name in COPIED), self.x_dir / "ref.json", self.x_dir / "qff_report.npz", self.label):
            if not needed.is_file():
                raise ValueError(f"{needed} is missing")
        if (self.x_dir / "NOISY").exists():
            raise ValueError(f"{self.x_dir} is NOISY (dpir.qff's noise guard): a field the pipeline would not use is no reference")


def stored_geometry(path: Path) -> tuple[list[str], np.ndarray]:
    """A stored minimum's atoms and coordinates in bohr (a corpus or pipeline geometry.json)."""
    record = json.loads(path.read_text(encoding="utf-8"))
    return [s.capitalize() for s in record["symbols"]], np.asarray(record["coords_bohr"], float).reshape(-1, 3)


def start(run: Path, candidates: list[Path], out: Path) -> dict[str, Any]:
    """Write the second field's start record from the candidate farthest from the run's minimum; the record of the choice."""
    target = out / "ref.json"
    if target.exists():
        raise ValueError(f"{target} exists: a start record is never overwritten")
    symbols, coords, _ = AN.geometry(run)
    frames: dict[Path, Frame] = {c: frame_onto(stored_geometry(c), (symbols, coords), str(c)) for c in candidates}
    chosen = max(frames, key=lambda c: frames[c].rms_bohr)
    chosen_symbols, chosen_coords = stored_geometry(chosen)
    record = {"run": run.as_posix(), "chosen": chosen.as_posix(), "rule": "the stored B3LYP minimum farthest from the run's, rms after rotation",
              "rms_bohr_from_the_run": {c.as_posix(): frames[c].rms_bohr for c in candidates}}
    out.mkdir(parents=True, exist_ok=True)
    write_atomic(str(target), json.dumps({"driver": "hessian", "model": {"method": "b3lyp", "basis": "6-31g*"},
                                          "molecule": {"symbols": chosen_symbols, "geometry": chosen_coords.ravel().tolist()},
                                          "start_of": "a second GFN2-xTB force field; no Hessian is stored here", "source": chosen.as_posix()}))
    write_atomic(str(out / "start.json"), json.dumps(record, indent=1))
    return record


def rotated_field(cfg: ReferenceConfig, symbols: list[str], coords: np.ndarray) -> tuple[AS.XtbField, dict[str, Any]]:
    """The stored force field with its modes in the run's frame, and the record of where it came from."""
    field = AS.XtbField.from_folder(str(cfg.x_dir), str(cfg.label))
    molecule = json.loads((cfg.x_dir / "ref.json").read_text(encoding="utf-8"))["molecule"]
    frame = frame_onto((molecule["symbols"], np.asarray(molecule["geometry"], float)), (symbols, coords), str(cfg.x_dir))
    source = {"source": cfg.x_dir.as_posix(), "label": cfg.label.as_posix(), "geometry_rms_bohr": frame.rms_bohr,
              "note": "a stored field rotated onto the pipeline's frame, not the pipeline's own run"}
    return AS.XtbField(field.delta, field.marked, frame.modes(field.q)), source


@contextmanager
def stand_in_field(field: AS.XtbField, source: dict[str, Any]) -> Iterator[None]:
    """While open, the pipeline's step 6 takes this force field where it would start its WSL run; the step's own code is
    otherwise what runs. Restored on exit, also after an error."""
    real = AN.force_field
    AN.force_field = lambda name, folder, settings: (field, source)
    try:
        yield
    finally:
        AN.force_field = real


def build(cfg: ReferenceConfig) -> Path:
    """The reference's folder with its pipeline.json and anharmonic.json: step 6 on a copy of the run's steps 1-5."""
    name = json.loads((cfg.run / "pipeline.json").read_text(encoding="utf-8"))["name"]
    d = (cfg.out / name).resolve()
    if d.exists():
        raise ValueError(f"{d} exists: a result is never overwritten")
    d.mkdir(parents=True)
    for copied in COPIED:
        shutil.copy2(cfg.run / copied, d / copied)
    record = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))
    symbols, coords, _ = AN.geometry(d)
    field, source = rotated_field(cfg, symbols, coords)
    with np.load(d / P.CORRECTION) as z:
        dH = z["dH"]
    request = AN.Request(record["name"], d, record["admission"]["smiles"], AN.load_artefact(), AN.FieldSettings.of(*SETTINGS))
    with stand_in_field(field, source):
        record["spectra"] = AN.step(request, dH, record["spectra"])
    record["seconds"]["anharmonic"] = 0.0
    record["pipeline_version"] = f"{P.PIPELINE_VERSION} (step 6 from a stored force field, on steps 1-5 of a {record['pipeline_version']} result)"
    P.write_json(d / "pipeline.json", record)
    return d


def main(argv: list[str] | None = None) -> int:
    """Command line."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("start", help="the second field's start record, from the stored minimum farthest from the run's")
    s.add_argument("--candidates", type=Path, nargs="+", required=True)
    r = sub.add_parser("reference", help="the same-network reference built on the stored second field")
    r.add_argument("--x-dir", type=Path, required=True)
    r.add_argument("--label", type=Path, required=True)
    for parser in (s, r):
        parser.add_argument("--run", type=Path, required=True)
        parser.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.command == "start":
        record = start(a.run, a.candidates, a.out)
        print(f"[second field] start: {record['chosen']}; rms from the run's minimum (bohr): "
              + ", ".join(f"{Path(c).parent.name} {v:.5f}" for c, v in record["rms_bohr_from_the_run"].items()), flush=True)
        return 0
    d = build(ReferenceConfig(a.run, a.x_dir, a.label, a.out))
    _, md = LC.write(LC.certificate(d, Catalog()), d)
    bands = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))["spectra"]["anharmonic"]["bands"]
    print(f"[second field] reference: {md}; {bands}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
