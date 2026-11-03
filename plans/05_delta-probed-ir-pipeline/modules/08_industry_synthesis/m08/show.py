"""The pipeline show (TASKS 146; the user's design of 1 Nov 2026): one landscape page for a large monitor — a molecule chosen on the left by
its carbon count, the pipeline in the middle as a metro map whose stations light up while the molecule travels through it, its spectrum
and certificate on the right. Replay mode: every run on the page is a pipeline result folder, and every number is read from its records
(`pipeline.json`, `certificate.json`) or computed from its arrays; the page types none in. The page is `show_template.html` with the data
put in. A molecule the Spectrum Atlas lists links to its Atlas page from the certificate (TASKS 161); --check-links asks the live site for
every such page after the build and fails when one is missing.

    python -m m08.show [--runs <result folder> ...] [--out modules/08_industry_synthesis/out/pipeline_show.html] [--check-links]
"""
from __future__ import annotations

import argparse
import functools
import json
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path, PureWindowsPath

import numpy as np

from . import live_certificate as LC
from . import pipeline as P
from .spectrum import GRID, broadened

# isort: split
from rungC_intensities import mode_intensities  # module 05's code, on the path through m08.pipeline

RESULTS = P.PLAN / "probes" / "results_m1"
M05 = P.PLAN / "modules" / "05_support_predictor"
TEMPLATE = Path(__file__).with_name("show_template.html")
OUT = P.PLAN / "modules" / "08_industry_synthesis" / "out" / "pipeline_show.html"
DEFAULT_RUNS = (RESULTS / "pipeline_demo_v04_2026-10-30" / "benzene", RESULTS / "pipeline_demo_v04_2026-10-30" / "phenanthrene",
                RESULTS / "pipeline_demo_v04_2026-10-30" / "candidate06", RESULTS / "pipeline_rehearsal_2026-10-30" / "cinnoline",
                RESULTS / "pipeline_reuse_demo_2026-10-31" / "carbazole")
FAMILY_ORDER = ("CH-stretch", "ring-ip", "CH-oop", "other")
PLOT_STEP_CM = 4.0                    # the drawn curve's step (a 720-unit-wide plot); the read-outs use module 05's 1 cm⁻¹ grid
DATA_MARK = "/*__DATA__*/null"
ATLAS_URL = "https://thebreadishard.github.io/spectrum-atlas"   # website/site/astro.config.mjs: site + base
ATLAS_PAGE_RUNG = 1                   # the Atlas builds a page for every catalogue row from this rung (pages/molecule/[id].astro)
STATIONS = (
    {"icon": "molecule", "title": "Molecule", "tool": "RDKit · canonical SMILES"},
    {"icon": "geometry", "title": "Start geometry", "tool": "RDKit ETKDG + MMFF"},
    {"icon": "optimise", "title": "Optimisation", "tool": "psi4 1.11 · B3LYP/6-31G*"},
    {"icon": "hessian", "title": "Hessian + APT", "tool": "pyscf 2.14 · analytic"},
    {"icon": "network", "title": "ΔH network", "tool": "three seeds"},
    {"icon": "spectrum", "title": "Spectrum + certificate", "tool": "double harmonic · licence"},
)


def duration(seconds: float) -> str:
    """A recorded duration as people read it."""
    if seconds < 60:
        return f"{seconds:.1f} s" if seconds < 10 else f"{seconds:.0f} s"
    if seconds < 3600:
        return f"{seconds / 60:.0f} min"
    return f"{seconds / 3600:.1f} h"


def depiction(smiles: str) -> str:
    """A 2D drawing of the molecule that takes the page's text colour (RDKit's black-and-white palette, black made currentColor)."""
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"{smiles}: does not parse")
    d = rdMolDraw2D.MolDraw2DSVG(200, 160)
    o = d.drawOptions()
    o.useBWAtomPalette()
    o.clearBackground = False
    o.bondLineWidth = 2
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    svg = d.GetDrawingText()
    svg = svg[svg.index("<svg"):].replace("#000000", "currentColor").replace("#000", "currentColor")
    return re.sub(r"\s*\n\s*", " ", svg)


def carbon_count(formula: str) -> int:
    m = re.match(r"C(\d*)(?![a-z])", formula)
    if m is None:
        raise ValueError(f"{formula}: no carbon")
    return int(m.group(1) or 1)


REUSE_SINCE = (0, 6)                 # pipeline 0.6 took steps 2–3 from the corpus first; earlier records computed every step
# the corpus APTs redone on the residual-checked route after their Hessian pass (12 Oct and 1 Nov 2026): the pass's time does not hold them
APT_RECOMPUTE_LOGS = (RESULTS / "apt_refine_install_2026-10-12" / "recompute" / "recompute.jsonl",
                      RESULTS / "holdout_a_apt_2026-11-01" / "recompute.jsonl")
HESSIAN_TIMED_FROM_S = 1.0           # a pass that read a saved Hessian instead of computing one records ≈ 0 s (benzene, A_8448043181)


def reused(rec: dict) -> bool:
    """Whether the run took steps 2–3 from the corpus: its record's reuse entry, or False for a record older than the reuse step."""
    if "reuse" in rec:
        return bool(rec["reuse"]["reused"])
    if tuple(int(x) for x in rec["pipeline_version"].split(".")[:2]) < REUSE_SINCE:
        return False
    raise ValueError(f"{rec['name']}: pipeline {rec['pipeline_version']} record without its reuse entry")


@functools.cache
def apt_recomputes() -> dict[str, float]:
    """Corpus folder → the seconds of its APT's recompute. A folder computed twice keeps its last row: the later run wrote the file installed."""
    out = {}
    for log in APT_RECOMPUTE_LOGS:
        for line in log.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                out[row["id"]] = float(row["seconds"])
    return out


def corpus_low_level_seconds(rec: dict) -> tuple[float | None, float | None]:
    """A reused run's corpus seconds for the B3LYP Hessian pass (None when the pass timed nothing) and for its APT when that was recomputed
    later (None when the pass wrote it, its time then inside the pass's)."""
    hessian = rec["low_level"]["b3lyp"]["seconds"]
    folder = PureWindowsPath(rec["reuse"]["source"]).name
    return (hessian if hessian >= HESSIAN_TIMED_FROM_S else None), apt_recomputes().get(folder)


def corpus_low_level_text(rec: dict) -> str:
    """The 'Hessian + APT' card's time on the corpus line."""
    hessian, apt = corpus_low_level_seconds(rec)
    if apt is None:
        return f"from the corpus · {duration(hessian)}" if hessian is not None else "from the corpus · time not recorded"
    return f"from the corpus · Hessian {duration(hessian) if hessian is not None else 'time not recorded'}, APT {duration(apt)}"


def stations(rec: dict) -> list[dict]:
    """The six stations with each one's recorded time: the laptop's for a computed step, the corpus record's for a reused one."""
    sec = rec["seconds"]
    from_corpus = reused(rec)
    corpus = rec["optimisation"]["timings_s"] if from_corpus else {}
    times = ["checked before any computation", "with the optimisation",
             f"from the corpus · {duration(corpus['optimise'])}" if from_corpus else f"{duration(sec['optimise'])} on the laptop",
             corpus_low_level_text(rec) if from_corpus else f"{duration(sec['low_level'])} on the laptop",
             f"{duration(sec['correction_and_spectra'])} with the spectrum", "certified"]
    adm = rec["admission"]
    details = [f"{adm['formula']} · {adm['n_atoms']} atoms · neutral and closed-shell, every element seen in training; canonical SMILES {adm['smiles']}",
               "the corpus's own start: RDKit ETKDG and MMFF from the canonical SMILES, seed 0",
               "B3LYP/6-31G* minimum with psi4 1.11, deck v1" + (" — taken from the corpus folder, which computed it at these settings"
                                                                 if from_corpus else ""),
               "analytic B3LYP Hessian and the atomic polar tensor (band heights) with pyscf 2.14, grid 99/590"
               + (" — taken from the corpus folder" if from_corpus else ""),
               f"the carried ΔH network v{adm['models'][0]['version']}: three seeds, their mean ΔH added to the B3LYP Hessian",
               "positions from the corrected Hessian, heights from the B3LYP APT (double harmonic); each band's family and licence"]
    return [{**s, "time": times[i], "detail": details[i]} for i, s in enumerate(STATIONS)]


def real_time(rec: dict) -> str:
    """The run's total real time from its record: the laptop's seconds, and for a reused run the corpus's for steps 3–4 beside them."""
    sec = rec["seconds"]
    if reused(rec):
        lead = f"Real time: {duration(sec['reuse'] + sec['correction_and_spectra'])} on the laptop, steps 3–4 from the corpus"
        hessian, apt = corpus_low_level_seconds(rec)
        if hessian is None:
            return f"{lead} (their time is not recorded)"
        corpus = rec["optimisation"]["timings_s"]["optimise"] + hessian + (apt or 0.0)
        return f"{lead} ({duration(corpus)} when they were computed)"
    return f"Real time: {duration(sum(sec.values()))} on the laptop in all"


def _sticks(H: np.ndarray, masses: np.ndarray, apt: np.ndarray) -> list[dict]:
    w, a = mode_intensities(H, masses, apt)
    return [{"omega_cm": float(x), "km_mol": float(y)} for x, y in zip(w, a, strict=True)]


def spectrum(r: LC.Result, cert: dict) -> dict:
    """The network's curve from its recorded sticks, B3LYP's and (where the corpus holds it) ωB97X's from the Hessians with the folder's
    B3LYP APT, broadened as the read-outs are; all divided by the largest value of the three."""
    sticks = {"network": r.record["spectra"]["network"]["sticks"], "b3lyp": _sticks(r.H_low, r.masses, r.apt)}
    truth = cert["molecule"].get("truth")
    if truth:
        with np.load(M05 / truth["source"]) as z:
            sticks["truth"] = _sticks(z["H_projected"], r.masses, r.apt)
    curves = {k: broadened(s, step=PLOT_STEP_CM) for k, s in sticks.items()}
    top = max(float(c[1].max()) for c in curves.values())
    if top <= 0.0:
        raise ValueError(f"{r.folder}: every curve is zero")
    grid = next(iter(curves.values()))[0]
    return {"start": float(grid[0]), "step": PLOT_STEP_CM, "x_lo": GRID[0], "x_hi": GRID[1],
            "curves": {k: [round(float(v) / top, 4) for v in c[1]] for k, c in curves.items()}}


def families(bands: list[dict]) -> list[dict]:
    """Per family the certificate's band count, licence and the network's measured error on hold-outs (a) and (b)."""
    rows = []
    for fam in FAMILY_ORDER:
        mine = [b for b in bands if b["family"] == fam]
        if not mine:
            continue
        errors = {(b["error_cm"]["a"], b["error_cm"]["b"]) for b in mine}
        licensed = {b["licensed"] for b in mine}
        if len(errors) != 1 or len(licensed) != 1:
            raise ValueError(f"{fam}: the certificate's bands disagree on the family's error or licence")
        (a, b), = errors
        rows.append({"family": fam, "bands": len(mine), "error_a": a, "error_b": b, "licensed": licensed.pop()})
    return rows


def atlas_link(listed: dict | None) -> str | None:
    """The Atlas page of the catalogue row the certificate found, or None when the molecule is not listed or listed without a page."""
    if listed is None or int(listed["rung"]) < ATLAS_PAGE_RUNG:
        return None
    return f"{ATLAS_URL}/molecule/{listed['id']}/"


def http_status(url: str) -> int:
    """The live site's answer to a HEAD request for the page."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def dead_links(data: dict, status: Callable[[str], int] = http_status) -> list[str]:
    """Every Atlas link of the page's molecules that the live site does not serve, with its answer."""
    return [f"{m['name']}: {m['atlas']} answered {code}" for m in data["molecules"] if m["atlas"] and (code := status(m["atlas"])) != 200]


def molecule(folder: Path) -> dict:
    r = LC.load_result(folder)
    cert = json.loads((folder / "certificate.json").read_text(encoding="utf-8"))
    rec, adm = r.record, r.record["admission"]
    seen = cert["molecule"]["seen"]
    truth = cert["molecule"].get("truth")
    return {"key": folder.parent.name + "/" + folder.name, "name": rec["name"], "formula": adm["formula"], "smiles": adm["smiles"],
            "n_atoms": adm["n_atoms"], "n_c": carbon_count(adm["formula"]),
            "hetero": sorted(e for e in adm["elements"] if e not in ("C", "H")),
            "status": {"role": seen["role"], "text": seen["text"]}, "depiction": depiction(adm["smiles"]),
            "atlas": atlas_link(cert["molecule"]["listed"]),
            "route": "reused" if reused(rec) else "computed", "pipeline_version": rec["pipeline_version"],
            "stations": stations(rec), "real_time": real_time(rec), "spectrum": spectrum(r, cert), "families": families(cert["bands"]),
            "truth": {"rms_cm": truth["rms_by_rank_cm"], "overlap": truth["overlap"]} if truth else None,
            "seed_spread_cm": max(b["seed_range_cm"][1] - b["seed_range_cm"][0] for b in cert["bands"])}


def payload(runs: tuple[Path, ...]) -> dict:
    mols = [molecule(f) for f in runs]
    networks = {f"ΔH network v{json.loads((f / 'pipeline.json').read_text(encoding='utf-8'))['admission']['models'][0]['version']}"
                for f in runs}
    if len(networks) != 1:
        raise ValueError(f"the runs carry different network versions: {sorted(networks)}")
    return {"molecules": sorted(mols, key=lambda m: (m["n_c"], m["name"])), "network": networks.pop(),
            "licence_line_cm": 3, "station_titles": [dict(s) for s in STATIONS], "live": False}


def atlas_index(data: dict) -> dict[str, str]:
    """Per Atlas page the show links to, the show key the page's 'see it go through the pipeline' opens: the run of the newest
    pipeline version, the last key on a tie (benzene is both a demo run and a hold-out (a) run)."""
    best: dict[str, tuple[tuple[int, ...], str]] = {}
    for m in data["molecules"]:
        if not m["atlas"]:
            continue
        atlas_id = m["atlas"].rstrip("/").rsplit("/", 1)[1]
        candidate = (tuple(int(x) for x in m["pipeline_version"].split(".")), m["key"])
        if atlas_id not in best or candidate > best[atlas_id]:
            best[atlas_id] = candidate
    return {atlas_id: key for atlas_id, (_, key) in sorted(best.items())}


def page(data: dict) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(DATA_MARK) != 1:
        raise ValueError(f"{TEMPLATE}: the data mark must appear once")
    return template.replace(DATA_MARK, json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--runs", nargs="*", type=Path, default=list(DEFAULT_RUNS))
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--check-links", action="store_true", help="after the build, ask the live Atlas for every page the show links to")
    a = ap.parse_args(argv)
    data = payload(tuple(a.runs))
    html_text = page(data)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = a.out.with_suffix(".tmp")
    tmp.write_text(html_text, encoding="utf-8")
    tmp.replace(a.out)
    index = a.out.with_name(a.out.stem + "_index.json")       # the Atlas reads it (website/export/pipeline_show.py)
    tmp = index.with_suffix(".tmp")
    tmp.write_text(json.dumps({"network": data["network"], "molecules": atlas_index(data)}, indent=1), encoding="utf-8")
    tmp.replace(index)
    print(f"wrote {a.out} ({len(html_text) / 1024:.0f} KB, {len(a.runs)} runs) and {index.name}")
    if a.check_links:
        dead = dead_links(data)
        if dead:
            raise SystemExit("Atlas links the live site does not serve:\n  " + "\n  ".join(dead))
        print(f"every Atlas link answers 200 ({sum(bool(m['atlas']) for m in data['molecules'])} links)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
