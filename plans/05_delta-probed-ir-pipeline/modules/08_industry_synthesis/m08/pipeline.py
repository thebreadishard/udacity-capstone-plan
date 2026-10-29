"""The pipeline's first version (TASKS 146, decision 64; `PIPELINE_BUILD_NOTE_2026-10-29.md`): one neutral, closed-shell aromatic molecule in
— a SMILES or an xyz file — and its harmonic infrared spectrum out, band positions and heights, computed on the laptop alone.

Each step is one function on existing code:

1. `start_geometry` — the corpus's own start geometry (`corpus/run_corpus.start_geometry`: RDKit ETKDG + MMFF, seed 0), or the given xyz;
2. `optimise` — `corpus/psi4_worker.py` with deck v1 and "hessians": false, in the Windows conda env `qc` (psi4 1.11, the deck's engine);
3. `low_level` — `corpus/analytic_hessians.py --functionals b3lyp` in WSL pyscf under `probes/wsl_capped.sh`: the analytic B3LYP Hessian
   and its APT;
4. `correction` — the carried ΔH network's seeds through `m05/rungC_infer.py`: their mean ΔH and each seed's;
5. `spectra` — `m08.spectrum.series` on H_low + ΔH with the B3LYP APT, each seed's positions beside it, and as the baseline only the
   B3LYP spectrum with PAHdb's factor per region (`probes/scale_factor_baseline.py`).

Every refusal — the charge state, a radical, no aromatic ring, an element the carried models never saw, a model that is not carried, an
output folder in use — comes before step 1. The positions are harmonic: no anharmonic shift (the backlog), and the record says so.

    python -m m08.pipeline --name benzene --smiles c1ccccc1 --out <folder> [--threads 4] [--psi4-python <qc env python>]
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .catalog import PLAN, Catalog
from .spectrum import cheap_apt, series

M05 = PLAN / "modules" / "05_support_predictor"
for _p in (M05 / "m05", M05 / "corpus", PLAN / "probes", PLAN / "src"):
    sys.path.insert(0, str(_p))
import model_registry as MR  # noqa: E402  (module 05's code is not a package)
import run_corpus as RC  # noqa: E402
import rungC_infer as RI  # noqa: E402
import rungC_train as RT  # noqa: E402
from anchor_registry import sha16  # noqa: E402
from rungC_equivariant import Z_OF  # noqa: E402
from scale_factor_baseline import PAHDB_FACTORS, pahdb_region  # noqa: E402

from dpir.provenance import provenance  # noqa: E402

PIPELINE_VERSION = "0.1.dev"           # v0.1 once it runs end to end (modules/PIPELINE.md)
NETWORK = "ΔH-network"
CORPUS = M05 / "corpus" / "molecules"
PSI4_WORKER = M05 / "corpus" / "psi4_worker.py"
ANALYTIC = M05 / "corpus" / "analytic_hessians.py"
WSL_CAPPED = PLAN / "probes" / "wsl_capped.sh"
WSL_PYSCF = "~/qc05/bin/python"
PYSCF_HEADROOM_MB = 584                # pyscf's max_memory below the cap: probes/cation_analytic_all.sh's measured margin (19 Oct 2026)
KILLED_AT_CAP = (137, 143)             # wsl_capped.sh's kill, and the systemd scope's (probes/cation_oom_check.sh)
APT_FAILED = 3                         # analytic_hessians.py: the Hessian is written, the APT failed its checks
CORRECTION = "correction.npz"
HARMONIC_NOTE = "harmonic positions: the anharmonic shift is not in this version (backlog; TASKS 53)"


class Refused(Exception):
    """The molecule or the settings are refused before any computation; `reasons` names each."""

    def __init__(self, reasons: list[str]) -> None:
        super().__init__("; ".join(reasons))
        self.reasons = reasons


def carried_models() -> tuple[Path, ...]:
    """The ΔH network's carried checkpoints in the model registry (decision 55), one file per seed."""
    status = MR.read_status(MR.STATUS_FILE)
    return tuple(sorted(MR.OUT / k for k, e in status.items() if e["network"] == NETWORK and e["status"] == "carried"))


def default_psi4_python() -> Path | None:
    """The qc env's interpreter as run_corpus.py takes it: CORPUS_QC_PYTHON, no personal default path."""
    return RC.QC_PYTHON


class PipelineConfig(BaseModel):
    """One request's settings, checked when built; refused combinations raise before anything is read."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    out_root: Path
    smiles: str | None = None
    xyz: Path | None = None
    charge: int = 0
    multiplicity: int = 1
    models: tuple[Path, ...] = Field(default_factory=lambda: carried_models())          # looked up at build time, so a test can
    psi4_python: Path | None = Field(default_factory=lambda: default_psi4_python())     # point it at a pin model
    pyscf_python: str = Field(WSL_PYSCF, pattern=r"^[~A-Za-z0-9_./-]+$")
    threads: int = Field(4, ge=1, le=32)
    psi4_memory_gb: int = Field(4, ge=1, le=64)
    wsl_cap_mb: int = Field(6144, ge=2048, le=65536)

    @field_validator("models")
    @classmethod
    def _some_models(cls, v: tuple[Path, ...]) -> tuple[Path, ...]:
        if not v:
            raise ValueError(f"no model: the registry lists no carried {NETWORK} checkpoint")
        return v

    @field_validator("out_root")
    @classmethod
    def _absolute(cls, v: Path) -> Path:
        return v.resolve()                 # psi4 (Windows) and pyscf (WSL) must name the same folder

    @model_validator(mode="after")
    def _one_closed_shell_input(self) -> PipelineConfig:
        if (self.smiles is None) == (self.xyz is None):
            raise ValueError("give exactly one of smiles and xyz")
        if (self.charge, self.multiplicity) != (0, 1):
            raise ValueError(f"charge {self.charge}, multiplicity {self.multiplicity}: this version is for neutral closed-shell molecules "
                             "(cations and other open shells are on the backlog; TASKS 98, 121)")
        if self.psi4_python is None or not self.psi4_python.is_file():
            raise ValueError(f"the qc env's python ({self.psi4_python}) is not a file: set CORPUS_QC_PYTHON or pass --psi4-python")
        if self.xyz is not None and not self.xyz.is_file():
            raise ValueError(f"{self.xyz}: no such xyz file")
        return self

    @property
    def folder(self) -> Path:
        return self.out_root / self.name


@dataclass(frozen=True)
class Admission:
    """What the refusal checks read — the molecule's elements and size against the carried models' training set, the models' registry
    entries — and the canonical SMILES and formula the certificate names the molecule by."""

    smiles: str
    formula: str
    elements: tuple[str, ...]
    n_atoms: int
    training_elements: tuple[str, ...]
    training_atoms: tuple[int, int]
    models: tuple[dict, ...]

    @property
    def inside_training_sizes(self) -> bool:
        return self.training_atoms[0] <= self.n_atoms <= self.training_atoms[1]


def rdkit_molecule(cfg: PipelineConfig):
    """The request as an RDKit molecule with explicit hydrogens (an xyz file's bonds from its geometry), or None when it does not parse."""
    from rdkit import Chem
    from rdkit.Chem import rdDetermineBonds

    if cfg.smiles is not None:
        m = Chem.MolFromSmiles(cfg.smiles)
        return None if m is None else Chem.AddHs(m)
    m = Chem.MolFromXYZFile(str(cfg.xyz))
    if m is None:
        return None
    try:
        rdDetermineBonds.DetermineBonds(m, charge=cfg.charge)
    except ValueError:
        return None
    return m


def training_set(models: tuple[Path, ...]) -> tuple[tuple[str, ...], tuple[int, int]]:
    """The elements and the atom-count range of the molecules the models were trained on, from each checkpoint's train_ids and the corpus."""
    import torch

    ids: set[str] = set()
    for p in models:
        ids |= set(torch.load(p, map_location="cpu", weights_only=False)["train_ids"])
    elements: set[str] = set()
    sizes = []
    for i in sorted(ids):
        g = CORPUS / i / "geometry.json"
        if not g.is_file():
            raise FileNotFoundError(f"{i}, a training molecule of the carried models, has no {g}")
        symbols = json.loads(g.read_text(encoding="utf-8"))["symbols"]
        elements |= {s.upper() for s in symbols}
        sizes.append(len(symbols))
    return tuple(sorted(elements)), (min(sizes), max(sizes))


def model_entries(models: tuple[Path, ...]) -> tuple[list[dict], list[str]]:
    """Each model's registry entry with its file hash, and the reasons to refuse: a model that is not carried (decision 55), or seeds of
    different versions."""
    entries, reasons = [], []
    for p in models:
        try:
            s = MR.require_carried(p)
        except SystemExit as e:
            reasons.append(str(e))
            continue
        entries.append({"path": str(p), "sha16": sha16(p), "network": s["network"], "version": s["version"], "status": s["status"]})
    if len({e["version"] for e in entries}) > 1:
        reasons.append(f"the models are of different versions: {sorted({e['version'] for e in entries})}")
    return entries, reasons


def admit(cfg: PipelineConfig) -> Admission:
    """Every refusal before any computation; raises Refused with all reasons found."""
    reasons = []
    if cfg.folder.exists() and any(cfg.folder.iterdir()):
        reasons.append(f"{cfg.folder} exists and is not empty: a result is never overwritten")
    entries, model_reasons = model_entries(cfg.models)
    reasons += model_reasons
    m = rdkit_molecule(cfg)
    if m is None:
        raise Refused([*reasons, f"the input ({cfg.smiles or cfg.xyz}) does not parse as a molecule"])
    elements = tuple(sorted({a.GetSymbol().upper() for a in m.GetAtoms()}))
    if sum(a.GetFormalCharge() for a in m.GetAtoms()) != 0:
        reasons.append("the molecule carries a net formal charge: this version is for neutral molecules")
    if any(a.GetNumRadicalElectrons() for a in m.GetAtoms()):
        reasons.append("the molecule has unpaired electrons: this version is for closed-shell molecules")
    if not any(a.GetIsAromatic() for a in m.GetAtoms()):
        reasons.append("no aromatic ring: the carried models were trained on aromatic molecules only")
    if model_reasons:
        raise Refused(reasons)
    training_elements, training_atoms = training_set(cfg.models)
    unseen = sorted(set(elements) - set(training_elements) | (set(elements) - set(Z_OF)))
    if unseen:
        reasons.append(f"element(s) {', '.join(unseen)} outside the carried models' training set ({', '.join(training_elements)})")
    if reasons:
        raise Refused(reasons)
    from rdkit import Chem
    from rdkit.Chem.rdMolDescriptors import CalcMolFormula

    return Admission(Chem.MolToSmiles(Chem.RemoveHs(m)), CalcMolFormula(m), elements, m.GetNumAtoms(), training_elements, training_atoms,
                     tuple(entries))


def start_geometry(cfg: PipelineConfig) -> tuple[list[list], dict | None]:
    """(atoms as [symbol, x, y, z] in Å, the optimiser options): the corpus's start geometry and options from a SMILES, or the xyz as given."""
    if cfg.smiles is not None:
        xyz, _optimise = RC.start_geometry({"layer": "A", "smiles": cfg.smiles})
        return xyz, RC.opt_options_for({"smiles": cfg.smiles})
    lines = cfg.xyz.read_text(encoding="utf-8").split("\n")
    n = int(lines[0])
    return [[w[0], float(w[1]), float(w[2]), float(w[3])] for w in (ln.split() for ln in lines[2:2 + n])], None


def _run(argv: list[str], log: Path, what: str) -> int:
    """One external step with its output in `log`; the exit code."""
    with log.open("w", encoding="utf-8") as fh:
        rc = subprocess.run(argv, stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, check=False).returncode
    print(f"[pipeline] {what}: exit {rc} ({log.name})", flush=True)
    return rc


def optimise(cfg: PipelineConfig, xyz: list[list], opt_options: dict | None) -> dict:
    """Step 2: the B3LYP/6-31G* optimisation of deck v1 (no Hessians); psi4's result.json."""
    d = cfg.folder
    deck = json.loads(RC.DECK.read_text(encoding="utf-8")) | {"threads": cfg.threads, "memory_gb": cfg.psi4_memory_gb}
    job = {"id": cfg.name, "layer": "pipeline", "xyz_angstrom": xyz, "deck": deck, "out_dir": str(d), "optimise": True, "grid_check": False,
           "hessians": False} | ({"opt_options": opt_options} if opt_options else {})
    (d / "job.json").write_text(json.dumps(job), encoding="utf-8")
    rc = _run([str(cfg.psi4_python), str(PSI4_WORKER), str(d / "job.json")], d / "psi4_worker.log", "optimisation (psi4)")
    res = json.loads((d / "result.json").read_text(encoding="utf-8")) if (d / "result.json").is_file() else {}
    if rc != 0 or res.get("status") != "done" or not (d / "geometry.json").is_file():
        raise RuntimeError(f"the optimisation failed (exit {rc}): {res.get('error', 'no result.json')[-800:]}")
    return res


def wsl_path(p: Path) -> str:
    """An absolute Windows path as WSL mounts it (C:\\x\\y → /mnt/c/x/y); the callers pass resolved paths."""
    w = PureWindowsPath(p)
    if not w.drive or not w.is_absolute():
        raise ValueError(f"{p}: not an absolute Windows drive path")
    return "/mnt/" + w.drive[0].lower() + "/" + "/".join(w.parts[1:])


def low_level_command(cfg: PipelineConfig) -> list[str]:
    """Step 3's command: analytic_hessians.py on the folder, B3LYP only, under the WSL memory cap."""
    q = shlex.quote
    inner = (f"export PYSCF_TMPDIR=$HOME/qc_tmp TMPDIR=$HOME/qc_tmp OMP_NUM_THREADS={cfg.threads} PYTHONUNBUFFERED=1; mkdir -p $HOME/qc_tmp; "
             f"cd {q(wsl_path(ANALYTIC.parent))} && bash {q(wsl_path(WSL_CAPPED))} {cfg.wsl_cap_mb} -- {cfg.pyscf_python} {ANALYTIC.name} "
             f"{q(wsl_path(cfg.folder))} --functionals b3lyp --threads {cfg.threads} --max-memory {cfg.wsl_cap_mb - PYSCF_HEADROOM_MB}")
    return ["wsl.exe", "-e", "bash", "-lc", inner]


def low_level(cfg: PipelineConfig) -> dict:
    """Step 3: the analytic B3LYP Hessian and APT; refuses a geometry with an imaginary mode. analytic_check.json's B3LYP entry."""
    d = cfg.folder
    rc = _run(low_level_command(cfg), d / "analytic.log", "analytic B3LYP Hessian and APT (WSL pyscf)")
    if rc in KILLED_AT_CAP:
        raise RuntimeError(f"the analytic Hessian was stopped at the WSL cap of {cfg.wsl_cap_mb} MB: raise --wsl-cap-mb")
    if rc == APT_FAILED:
        raise RuntimeError("the APT failed its checks (analytic.log): no heights can be drawn")
    if rc != 0 or not (d / RI.LOW_HESSIAN).is_file():
        raise RuntimeError(f"the analytic Hessian failed (exit {rc}; analytic.log)")
    n_imag = json.loads((d / "result.json").read_text(encoding="utf-8"))["n_imaginary_b3lyp"]
    if n_imag:
        raise RuntimeError(f"{n_imag} imaginary B3LYP mode(s): the optimised geometry is not a minimum, so no spectrum is drawn")
    return json.loads((d / "analytic_check.json").read_text(encoding="utf-8"))


def correction(models: tuple[Path, ...], d: Path) -> tuple[np.ndarray, list[np.ndarray]]:
    """Step 4: the seeds' mean ΔH and each seed's (Cartesian, hartree/bohr², the low level's frame)."""
    per_seed = []
    for p in models:
        model, ck = RT.load_hybrid_model(p)
        t = RI.input_tensors_of(d, RT.tensor_config(ck))
        per_seed.append(RI.delta_H(model, t).numpy().astype(float))
    return np.mean(per_seed, axis=0), per_seed


def save_correction(d: Path, dH: np.ndarray, dH_seeds: list[np.ndarray], models: tuple[Path, ...]) -> None:
    """The network's output beside its inputs — the seed mean and each seed's ΔH with the models' file names — so that the certificate
    reads the result instead of re-running the network."""
    tmp = d / f"{CORRECTION}.tmp.npz"
    np.savez(tmp, dH=dH, dH_seeds=np.stack(dH_seeds), models=np.array([m.name for m in models]))
    os.replace(tmp, d / CORRECTION)


def scaled_baseline(sticks: list[dict]) -> list[dict]:
    """The B3LYP sticks with PAHdb's factor of each stick's region: the baseline beside the network, never in its place."""
    w = np.array([s["omega_cm"] for s in sticks])
    f = np.array(PAHDB_FACTORS)[pahdb_region({"freq": w})]
    return [dict(s, omega_cm=round(float(x), 1)) for s, x in zip(sticks, f * w, strict=True)]


def spectra(d: Path, dH: np.ndarray, dH_seeds: list[np.ndarray]) -> dict:
    """Step 5: the network's spectrum (seed-mean ΔH) with each stick's range over the seeds, and the scaled B3LYP baseline."""
    hessian = d / RI.LOW_HESSIAN
    apt = cheap_apt(d)
    if apt is None:
        raise RuntimeError(f"{d.name}: no passed B3LYP APT, so no heights")
    masses = np.asarray(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    with np.load(hessian) as z:
        H_low = z["H_projected"]
    net = series(hessian, masses, apt, H=H_low + dH)
    seeds = [series(hessian, masses, apt, H=H_low + x)["sticks"] for x in dH_seeds]
    if any(len(s) != len(net["sticks"]) for s in seeds):
        raise RuntimeError("a seed's spectrum has a different number of vibrational modes than the mean's")
    for i, stick in enumerate(net["sticks"]):
        w = [s[i]["omega_cm"] for s in seeds]
        stick["seed_range_cm"] = [min(w), max(w)]
    b3lyp = series(hessian, masses, apt)
    baseline = dict(b3lyp, sticks=scaled_baseline(b3lyp["sticks"]),
                    label=f"baseline only: B3LYP/6-31G* scaled by PAHdb's factors {list(PAHDB_FACTORS)} per region (probes/scale_factor_baseline.py)")
    return {"network": net, "baseline": baseline, "note": HARMONIC_NOTE}


def write_json(path: Path, rec: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    os.replace(tmp, path)


def run(cfg: PipelineConfig) -> dict:
    """The whole pipeline for one molecule; the record is written to <folder>/pipeline.json and returned."""
    import torch

    adm = admit(cfg)
    torch.set_num_threads(cfg.threads)
    d = cfg.folder
    d.mkdir(parents=True, exist_ok=True)
    seconds: dict[str, float] = {}
    t = time.time()
    xyz, opt_options = start_geometry(cfg)
    psi4 = optimise(cfg, xyz, opt_options)
    seconds["optimise"] = round(time.time() - t, 1)
    t = time.time()
    check = low_level(cfg)
    seconds["low_level"] = round(time.time() - t, 1)
    t = time.time()
    dH, dH_seeds = correction(cfg.models, d)
    save_correction(d, dH, dH_seeds, cfg.models)
    out = spectra(d, dH, dH_seeds)
    seconds["correction_and_spectra"] = round(time.time() - t, 1)
    rec = {"pipeline_version": PIPELINE_VERSION, "name": cfg.name, "input": {"smiles": cfg.smiles, "xyz": cfg.xyz},
           "settings": cfg.model_dump(mode="json"), "admission": vars(adm) | {"inside_training_sizes": adm.inside_training_sizes},
           "deck": {"file": str(RC.DECK), "sha16": sha16(RC.DECK)}, "optimisation": {k: psi4.get(k) for k in ("e_opt", "timings_s", "opt_options")},
           "low_level": check, "seconds": seconds, "spectra": out, "provenance": provenance()}
    write_json(d / "pipeline.json", rec)
    return rec


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--name", required=True, help="the result folder's name under --out")
    ap.add_argument("--out", required=True, type=Path)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--smiles")
    src.add_argument("--xyz", type=Path, help="an xyz file in Å; its geometry is the optimisation's start")
    ap.add_argument("--psi4-python", type=Path, help="the qc env's python (default: CORPUS_QC_PYTHON)")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--psi4-memory-gb", type=int, default=4)
    ap.add_argument("--wsl-cap-mb", type=int, default=6144)
    ap.add_argument("--check-only", action="store_true", help="the refusal checks alone (a run spec's dry run): nothing is computed or written")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from .live_certificate import certificate, write  # that module imports this one

    a = parse_args(argv)
    given = {k: v for k, v in dict(smiles=a.smiles, xyz=a.xyz, psi4_python=a.psi4_python).items() if v is not None}
    cfg = PipelineConfig(name=a.name, out_root=a.out, threads=a.threads, psi4_memory_gb=a.psi4_memory_gb, wsl_cap_mb=a.wsl_cap_mb, **given)
    try:
        if a.check_only:
            adm = admit(cfg)
            print(f"[pipeline] admitted: {cfg.name}, {adm.n_atoms} atoms ({', '.join(adm.elements)}); models "
                  f"{', '.join(Path(m['path']).name for m in adm.models)}; training sizes {adm.training_atoms}", flush=True)
            return 0
        catalog = Catalog()             # the certificate's catalogue and tolerances: read before any computation
        rec = run(cfg)
    except Refused as r:
        print("REFUSED: " + "\n  ".join(["", *r.reasons]), flush=True)
        return 2
    n = len(rec["spectra"]["network"]["sticks"])
    print(f"[pipeline] done: {n} bands, {cfg.folder / 'pipeline.json'} ({sum(rec['seconds'].values()):.0f} s)", flush=True)
    _, md = write(certificate(cfg.folder, catalog), cfg.folder)
    print(f"[pipeline] certificate: {md}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
