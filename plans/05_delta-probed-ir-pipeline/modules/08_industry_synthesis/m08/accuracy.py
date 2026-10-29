"""The measured error of a ΔH-network version, read from its own evaluation records (`probes/rungC_eval_saved.py`, one JSON per seed): per
mode family and hold-out against the 3 cm⁻¹ line, the coupling ratio, and the spectral shape. One implementation for the licence (decision
65), the live certificate and the export certificate."""
from __future__ import annotations

import json
from pathlib import Path

from . import pipeline as P
from .spectrum import shape_accuracy

# isort: split
# probes/, on the path through m08.pipeline
from chain35_read import T1_FAMILY_LINE, T1_RATIO_LINE
from promotion_read import FAMILIES, QUANTITIES, RATIO, load_eval_arm, reported

M05_OUT = P.M05 / "out"
LICENCE_LINE_CM = T1_FAMILY_LINE        # decision 53's 3 cm⁻¹, every family's line under decision 65
TARGETS = {**dict.fromkeys(FAMILIES, LICENCE_LINE_CM), RATIO: T1_RATIO_LINE}
TARGET_SOURCE = ("3 cm⁻¹ per family — decision 53's line for ring-ip, CH-oop and 'other', every family's under decision 65 (the licence) — "
                 "and the coupling ratio ≤ 0.25 of chain 35's T1 line (probes/chain35_read.py)")
HOLDOUTS = {"a": "hold-out (a): the parent PAHs of layer A held out on 19 Sep 2026, never trained",
            "b": "hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the network never saw"}
HIGHER_LEVEL = "ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians)"
CC_NOTE = ("not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing "
           "anchors wait for the anchor decision of November 2026")
DEFINITIONS = dict(
    family="rms over the family's modes of the corrected frequency's error against the higher level (cm⁻¹); families by module 05's rule "
           "(m05/learning_curve_layerA.molecule_features)",
    coupling_ratio="rms of the predicted mode couplings' error over the rms of the couplings themselves; 0 = exact, 1 = no better than none",
    spectrum_overlap="cosine similarity of the two Lorentzian-broadened spectra (FWHM 10 cm⁻¹, 500–3500 cm⁻¹); 1 = identical shape",
    intensity_error="intensity-weighted rms of the relative height error per band, bands paired by the shape of the motion (eigenvector "
                    "overlap); 0 = identical heights")
APT_OPEN = "the APT itself is computed at the cheap level; its CC-minus-B3LYP difference (≈ 20 % on benzene) is not corrected by any rung yet"


def evaluation_records(models: tuple[str, ...]) -> list[Path]:
    """Each model's evaluation record: the `rungC_eval_saved.py` JSON beside it that names it (…_model_n750_seed0.pt → …_eval_*seed0.json).
    None or several is refused: the error stated is that of the files that ran."""
    out = []
    for name in models:
        stem, sep, tail = name.partition("_model_")
        if not sep:
            raise ValueError(f"{name}: not a rung-C model file name (…_model_…)")
        seed = tail.removesuffix(".pt").rsplit("_", 1)[-1]
        hits = [p for p in sorted(M05_OUT.glob(f"{stem}_eval_*{seed}.json")) if _model_of(p) == name]
        if len(hits) != 1:
            raise ValueError(f"{name}: {len(hits)} evaluation records in {M05_OUT} name it; exactly one is needed")
        out.append(hits[0])
    return out


def _model_of(record: Path) -> str:
    with open(record, encoding="utf-8") as f:
        return Path(json.load(f)["model"]).name


def network_accuracy(records: list[Path]) -> dict:
    """Per hold-out: each read-out's seed mean and seed values as reported, its target and whether the mean is within it, and the spectral
    shape (overlap and height error, uncorrected → corrected) over the molecules with an APT."""
    arm = load_eval_arm(records)
    recs = []
    for p in records:
        with open(p, encoding="utf-8") as f:
            recs.append(json.load(f))
    holdouts = {}
    for h, description in HOLDOUTS.items():
        rows = {}
        for q in QUANTITIES:
            mean = reported(arm.mean(h, q), q)
            rows[q] = dict(mean=mean, seeds=[reported(x, q) for x in arm.values[h][q]], target=TARGETS[q], within_target=mean <= TARGETS[q])
        holdouts[h] = dict(description=description, n_molecules=len(recs[0][h]["per_molecule"]), readouts=rows, shape=shape_accuracy(recs, h))
    return dict(higher_level=HIGHER_LEVEL, holdouts=holdouts, target_source=TARGET_SOURCE, sources=[p.name for p in records],
                definitions=DEFINITIONS, coupled_cluster=CC_NOTE)


def carried_version() -> str:
    status = P.MR.read_status(P.MR.STATUS_FILE)
    versions = {status[m.name]["version"] for m in P.carried_models()}
    if len(versions) != 1:
        raise RuntimeError(f"the carried ΔH-network files are of {len(versions)} versions: {sorted(versions)}")
    return versions.pop()


def carried_accuracy() -> dict:
    """The error of the carried version: the evaluation records of the registry's carried ΔH-network files."""
    return network_accuracy(evaluation_records(tuple(m.name for m in P.carried_models()))) | {"version": carried_version()}
