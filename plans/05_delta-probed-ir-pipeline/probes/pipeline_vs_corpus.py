"""A pipeline result (`m08/pipeline.py`, TASKS 146) against the corpus folder of the same molecule, step by step: the optimised geometry,
the analytic B3LYP frequencies, and the network's spectrum computed on the corpus folder with the same models — so a difference is located
in the step that makes it. Where the corpus holds the ωB97X analytic Hessian (the network's training target), the pipeline's spectra are
also read against it — the network and B3LYP itself, per family — with the evaluation's own read-outs, and the
evaluation's value for the molecule, when it is in one of the network's hold-outs, beside it. Writes <result>/vs_corpus.json and .md.

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
from m08 import accuracy as A  # noqa: E402
from m08 import live_certificate as LC  # noqa: E402
from m08 import pipeline as P  # noqa: E402
from rungC_intensities import MATCHED, intensity_readout, match_modes, mode_intensities  # noqa: E402  (on the path through m08.pipeline)

TRUTH = "hessian_wb97x_analytic.npz"
SAME_FRAME_BOHR = 1e-3                 # above it the atoms are in another order or frame than the corpus folder's


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


def _rms(x: np.ndarray) -> float:
    return round(float(np.sqrt(np.mean(x ** 2))), 2)


def against_truth(result: Path, corpus: Path) -> dict:
    """The pipeline's spectra against the corpus's ωB97X Hessian with the pipeline's B3LYP APT. Every B3LYP mode is paired by its shape with a
    truth mode and a network mode (`match_modes`); the position errors are split by the network's families; overlap and heights are
    `rungC_intensities.intensity_readout`, the evaluation's function."""
    r = LC.load_result(result)
    with np.load(corpus / TRUTH) as z:
        H_true = z["H_projected"]
    read = intensity_readout(r.H_low, H_true - r.H_low, r.dH, r.masses, r.apt)
    ft, _, Lt = mode_intensities(H_true, r.masses, r.apt, return_modes=True)
    fp, _, Lp = mode_intensities(r.H_low + r.dH, r.masses, r.apt, return_modes=True)
    f0, _, L0 = mode_intensities(r.H_low, r.masses, r.apt, return_modes=True)
    truth = ft[match_modes(L0, Lt)]
    errors = {"network": fp[match_modes(L0, Lp)] - truth, "B3LYP": f0 - truth}
    fam = np.array(LC.mode_families(r, f0))
    per_family = {f: {"n_modes": int((fam == f).sum()), **{k: _rms(e[fam == f]) for k, e in errors.items()}} for f in sorted(set(fam))}
    return {"truth": f"{corpus.name}/{TRUTH}", "all_modes": {k: _rms(e) for k, e in errors.items()}, "per_family": per_family,
            "spectrum_overlap": {"network": round(read["spectrum_overlap"], 4), "B3LYP": round(read["spectrum_overlap_zero_rule"], 4)},
            "height_error": {"network": round(read[MATCHED], 3), "B3LYP": round(read["intensity_rel_rms_zero_rule_matched"], 3)},
            "evaluation": evaluation_value(r.models, corpus.name)}


def evaluation_value(models: tuple[str, ...], mol_id: str) -> dict | None:
    """The network's evaluation of the same molecule (seed means of its per-molecule read-outs), when the molecule is in a hold-out."""
    for h in A.HOLDOUTS:
        rows = []
        for p in A.evaluation_records(models):
            pm = json.loads(p.read_text(encoding="utf-8"))[h]["per_molecule"]
            if mol_id in pm:
                rows.append(pm[mol_id])
        if rows:
            return {"holdout": h, **{k: round(float(np.mean([x[k] for x in rows])), 4)
                                     for k in ("corrected_freq_rms", "spectrum_overlap", MATCHED)}}
    return None


def truth_report(t: dict) -> str:
    rows = "".join(f"| {f} | {v['n_modes']} | {v['network']} | {v['B3LYP']} |\n" for f, v in t["per_family"].items())
    a, o, h, e = t["all_modes"], t["spectrum_overlap"], t["height_error"], t["evaluation"]
    ev = (f"\nThe network's own evaluation of this molecule (hold-out ({e['holdout']}), seed means): corrected-frequency rms {e['corrected_freq_rms']} "
          f"cm⁻¹, overlap {e['spectrum_overlap']}, height error {e[MATCHED]}.\n" if e else "\nThe molecule is in none of the network's hold-outs.\n")
    return (f"\n## Against the ωB97X truth ({t['truth']})\n\n"
            "Position error, rms over the modes (cm⁻¹), each B3LYP mode paired by its shape with its truth mode:\n\n"
            "| family | modes | network | B3LYP |\n|---|---|---|---|\n" + rows
            + f"| all | {sum(v['n_modes'] for v in t['per_family'].values())} | {a['network']} | {a['B3LYP']} |\n\n"
            f"Spectrum overlap with the truth (1 = the same shape): network {o['network']}, B3LYP {o['B3LYP']}. "
            f"Height error (0 = the same heights): network {h['network']}, B3LYP {h['B3LYP']}.\n" + ev
            + "\nThe scaled-B3LYP baseline is not read against this truth: PAHdb's factors aim at measured band positions, the "
              "anharmonic shift folded in, while the truth here is harmonic ωB97X; the baseline is compared where a laboratory record exists.\n")


def report(c: dict) -> str:
    n, b = c["network_spectrum"], c["baseline_spectrum"]
    return (f"# {Path(c['result']).name} against the corpus folder {Path(c['corpus']).name}\n\n"
            f"- optimised geometry: largest coordinate difference {c['geometry_max_abs_bohr']:.2e} bohr\n"
            f"- analytic B3LYP frequencies: largest difference {c['b3lyp_freq_max_abs_cm']} cm⁻¹\n"
            f"- network spectrum ({', '.join(c['models'])}): {n['n']} bands, positions within {n['max_abs_omega_cm']} cm⁻¹, "
            f"heights within {n['max_abs_km_mol']} km/mol\n"
            f"- scaled B3LYP baseline: positions within {b['max_abs_omega_cm']} cm⁻¹, heights within {b['max_abs_km_mol']} km/mol\n"
            + (truth_report(c["against_truth"]) if c.get("against_truth") else ""))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("result", type=Path)
    ap.add_argument("corpus_id")
    a = ap.parse_args(argv)
    c = compare(a.result.resolve(), P.CORPUS / a.corpus_id)
    if c["geometry_max_abs_bohr"] > SAME_FRAME_BOHR:
        print(f"no truth read: the atoms differ from the corpus folder's by {c['geometry_max_abs_bohr']:.2g} bohr — another order or frame "
              "(pipeline 0.2 starts from the canonical SMILES)", flush=True)
    elif (P.CORPUS / a.corpus_id / TRUTH).exists():
        c["against_truth"] = against_truth(a.result.resolve(), P.CORPUS / a.corpus_id)
    P.write_json(a.result / "vs_corpus.json", c)
    text = report(c)
    tmp = a.result / "vs_corpus.md.tmp"
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(a.result / "vs_corpus.md")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
