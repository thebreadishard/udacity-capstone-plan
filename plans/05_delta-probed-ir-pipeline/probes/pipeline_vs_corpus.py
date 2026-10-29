"""A pipeline result (`m08/pipeline.py`, TASKS 146) against the corpus folder of the same molecule, step by step: the optimised geometry,
the analytic B3LYP frequencies, and the network's spectrum computed on the corpus folder with the same models — so a difference is located
in the step that makes it. Writes <result>/vs_corpus.json and .md.

    python probes/pipeline_vs_corpus.py <pipeline result folder> <corpus id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P  # noqa: E402
from rungC_intensities import mode_intensities  # noqa: E402  (on the path through m08.pipeline)


def geometry(d: Path) -> tuple[list[str], np.ndarray]:
    g = json.loads((d / "geometry.json").read_text(encoding="utf-8"))
    return g["symbols"], np.asarray(g["coords_bohr"], float)


def frequencies(d: Path) -> np.ndarray:
    """The vibrational frequencies of the stored H_projected, as the spectrum computes them: the stored freq_cm field of eight files written
    before the software stamp (11 Oct 2026) differs from its own Hessian by up to 0.77 cm⁻¹ (29 Oct)."""
    with np.load(d / P.RI.LOW_HESSIAN) as z:
        H = z["H_projected"]
    masses = np.asarray(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    return np.sort(mode_intensities(H, masses, np.zeros((3, H.shape[0])))[0])


def stick_differences(a: list[dict], b: list[dict]) -> dict:
    if len(a) != len(b):
        raise ValueError(f"{len(a)} against {len(b)} sticks")
    dw = [abs(x["omega_cm"] - y["omega_cm"]) for x, y in zip(a, b, strict=True)]
    dk = [abs(x["km_mol"] - y["km_mol"]) for x, y in zip(a, b, strict=True)]
    return {"n": len(a), "max_abs_omega_cm": round(max(dw), 2), "max_abs_km_mol": round(max(dk), 3)}


def compare(result: Path, corpus: Path) -> dict:
    rec = json.loads((result / "pipeline.json").read_text(encoding="utf-8"))
    models = tuple(Path(m["path"]) for m in rec["admission"]["models"])
    sym_r, x_r = geometry(result)
    sym_c, x_c = geometry(corpus)
    if sym_r != sym_c:
        raise ValueError("the atoms differ in kind or order")
    fr, fc = frequencies(result), frequencies(corpus)
    dH, seeds = P.correction(models, corpus)
    on_corpus = P.spectra(corpus, dH, seeds)
    return {"result": str(result), "corpus": str(corpus), "models": [m.name for m in models],
            "geometry_max_abs_bohr": float(np.abs(x_r - x_c).max()),
            "b3lyp_freq_max_abs_cm": round(float(np.abs(fr - fc).max()), 4),
            "network_spectrum": stick_differences(rec["spectra"]["network"]["sticks"], on_corpus["network"]["sticks"]),
            "baseline_spectrum": stick_differences(rec["spectra"]["baseline"]["sticks"], on_corpus["baseline"]["sticks"])}


def report(c: dict) -> str:
    n, b = c["network_spectrum"], c["baseline_spectrum"]
    return (f"# {Path(c['result']).name} against the corpus folder {Path(c['corpus']).name}\n\n"
            f"- optimised geometry: largest coordinate difference {c['geometry_max_abs_bohr']:.2e} bohr\n"
            f"- analytic B3LYP frequencies: largest difference {c['b3lyp_freq_max_abs_cm']} cm⁻¹\n"
            f"- network spectrum ({', '.join(c['models'])}): {n['n']} bands, positions within {n['max_abs_omega_cm']} cm⁻¹, "
            f"heights within {n['max_abs_km_mol']} km/mol\n"
            f"- scaled B3LYP baseline: positions within {b['max_abs_omega_cm']} cm⁻¹, heights within {b['max_abs_km_mol']} km/mol\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("result", type=Path)
    ap.add_argument("corpus_id")
    a = ap.parse_args(argv)
    c = compare(a.result.resolve(), P.CORPUS / a.corpus_id)
    P.write_json(a.result / "vs_corpus.json", c)
    text = report(c)
    tmp = a.result / "vs_corpus.md.tmp"
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(a.result / "vs_corpus.md")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
