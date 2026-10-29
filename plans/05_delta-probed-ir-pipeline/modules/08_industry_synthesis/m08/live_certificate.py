"""The certificate of a live pipeline result (`m08/pipeline.py`; build step 4 of TASKS 146): the network's spectrum band by band with the
seeds' spread, the measured error of the network version that ran — read from its own evaluation records per mode family and hold-out and
set against the registered target — the B3LYP level and the scaled-B3LYP baseline beside it, the laboratory tolerance of each band's region,
the run's hours and the provenance. Every number names its source. `certify.py` certifies the corpus's recorded molecules from the website
export; this module certifies a molecule the pipeline computed, from the files in its result folder alone (no network is re-run).
Written beside the result as certificate.json and certificate.md.

    python -m m08.live_certificate <pipeline result folder>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import pipeline as P
from . import prices
from .catalog import FAMILY_SOURCE, Catalog
from .catalog import family as lab_region
from .certify import commit_hash
from .licence import state as licence_state
from .spectrum import cheap_apt, shape_accuracy

# isort: split
# module 05's code and probes/, on the path through m08.pipeline
import rungC_intensities as RINT
from chain35_read import T1_FAMILY_LINE, T1_RATIO_LINE
from learning_curve_layerA import molecule_features
from promotion_read import QUANTITIES, RATIO, load_eval_arm, reported

M05_OUT = P.M05 / "out"
TARGETS = {"ring-ip": T1_FAMILY_LINE, "CH-oop": T1_FAMILY_LINE, "other": T1_FAMILY_LINE, RATIO: T1_RATIO_LINE}
TARGET_SOURCE = ("decision 53 (≤ 3 cm⁻¹ for ring-ip, CH-oop and 'other'; CH-stretch has no registered line) and the coupling ratio ≤ 0.25 of "
                 "chain 35's T1 line (probes/chain35_read.py)")
HOLDOUTS = {"a": "hold-out (a): the parent PAHs of layer A held out on 19 Sep 2026, never trained",
            "b": "hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the network never saw"}
HIGHER_LEVEL = "ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians)"
CC_NOTE = ("not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing "
           "anchors wait for the anchor decision of November 2026")
STICK_TOL_CM = 0.051                   # the record rounds positions to 0.1 cm⁻¹


@dataclass(frozen=True)
class Result:
    """A pipeline result folder's record and arrays: the B3LYP Hessian and APT, and the network's ΔH (seed mean and each seed's)."""
    folder: Path
    record: dict
    masses: np.ndarray
    H_low: np.ndarray
    apt: np.ndarray
    dH: np.ndarray
    models: tuple[str, ...]


def load_result(folder: Path) -> Result:
    rec = json.loads((folder / "pipeline.json").read_text(encoding="utf-8"))
    masses = np.asarray(json.loads((folder / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    apt_file = cheap_apt(folder)
    if apt_file is None:
        raise RuntimeError(f"{folder}: no passed B3LYP APT")
    with np.load(folder / P.RI.LOW_HESSIAN) as z:
        H_low = z["H_projected"]
    with np.load(apt_file) as z:
        apt = np.asarray(z["apt"], float)
    with np.load(folder / P.CORRECTION) as z:
        dH, models = z["dH"], tuple(str(m) for m in z["models"])
    if models != tuple(Path(m["path"]).name for m in rec["admission"]["models"]):
        raise RuntimeError(f"{folder}: {P.CORRECTION} names other models than pipeline.json")
    return Result(folder, rec, masses, H_low, apt, dH, models)


def evaluation_records(models: tuple[str, ...]) -> list[Path]:
    """Each model's evaluation record: the `rungC_eval_saved.py` JSON beside it that names it (…_model_n750_seed0.pt → …_eval_*seed0.json).
    None or several is refused: the certificate states the error of the files that ran."""
    out = []
    for name in models:
        stem, sep, tail = name.partition("_model_")
        if not sep:
            raise ValueError(f"{name}: not a rung-C model file name (…_model_…)")
        seed = tail.removesuffix(".pt").rsplit("_", 1)[-1]
        hits = [p for p in sorted(M05_OUT.glob(f"{stem}_eval_*{seed}.json")) if _model_of(p) == name]
        if len(hits) != 1:
            raise ValueError(f"{name}: {len(hits)} evaluation records in {M05_OUT} name it; the certificate needs exactly one")
        out.append(hits[0])
    return out


def _model_of(record: Path) -> str:
    with open(record, encoding="utf-8") as f:
        return Path(json.load(f)["model"]).name


def network_accuracy(records: list[Path]) -> dict:
    """Per hold-out: each read-out's seed mean and seed values as reported, the registered target where one exists, and the spectral shape
    (overlap and height error, uncorrected → corrected) over the molecules with an APT."""
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
            target = TARGETS.get(q)
            rows[q] = dict(mean=mean, seeds=[reported(x, q) for x in arm.values[h][q]], target=target,
                           within_target=None if target is None else mean <= target)
        holdouts[h] = dict(description=description, n_molecules=len(recs[0][h]["per_molecule"]), readouts=rows, shape=shape_accuracy(recs, h))
    return dict(higher_level=HIGHER_LEVEL, holdouts=holdouts, target_source=TARGET_SOURCE, sources=[p.name for p in records],
                definitions=dict(family="rms over the family's modes of the corrected frequency's error against the higher level (cm⁻¹); "
                                        "families by module 05's rule (m05/learning_curve_layerA.molecule_features)",
                                 coupling_ratio="rms of the predicted mode couplings' error over the rms of the couplings themselves; "
                                                "0 = exact, 1 = no better than none"),
                coupled_cluster=CC_NOTE)


def mode_families(r: Result, w_low: np.ndarray) -> list[str]:
    """The family of each B3LYP mode by the rule the network's error is measured in (`molecule_features`, which also reads the folder's
    geometry); its modes must be the spectrum's."""
    feats = molecule_features(r.folder, lo=r.H_low, hi=r.H_low)
    if len(feats["freq"]) != len(w_low) or np.abs(np.asarray(feats["freq"]) - w_low).max() > 1e-6:
        raise RuntimeError(f"{r.folder.name}: the family rule's modes are not the spectrum's")
    return list(feats["family"])


def bands(r: Result, accuracy: dict, tolerance: dict[str, dict]) -> list[dict]:
    """One row per corrected mode, sorted by position, paired with the B3LYP mode of largest overlap (`rungC_intensities.match_modes`, the
    evaluation's pairing): its family, the B3LYP, baseline and network positions, the height, the seeds' range as the record holds it, the
    measured error of its family on both hold-outs, and the laboratory tolerance of its region."""
    w_low, _, L_low = RINT.mode_intensities(r.H_low, r.masses, r.apt, return_modes=True)
    w_net, k_net, L_net = RINT.mode_intensities(r.H_low + r.dH, r.masses, r.apt, return_modes=True)
    sticks = r.record["spectra"]["network"]["sticks"]
    if len(sticks) != len(w_net) or max(abs(s["omega_cm"] - w) for s, w in zip(sticks, np.sort(w_net), strict=True)) > STICK_TOL_CM:
        raise RuntimeError(f"{r.folder.name}: the recorded network spectrum is not the one H_low + ΔH gives")
    families = mode_families(r, w_low)
    baseline = r.record["spectra"]["baseline"]["sticks"]           # in the B3LYP modes' order (ascending), as the pipeline scaled them
    if len(baseline) != len(w_low):
        raise RuntimeError(f"{r.folder.name}: the recorded baseline has {len(baseline)} bands, the B3LYP Hessian {len(w_low)}")
    rank = np.argsort(np.argsort(w_net))
    readouts = {h: accuracy["holdouts"][h]["readouts"] for h in HOLDOUTS}
    rows = []
    for i, j in enumerate(RINT.match_modes(L_low, L_net)):
        fam, region = families[i], lab_region(float(w_net[j]))
        rows.append(dict(network_cm=round(float(w_net[j]), 1), km_mol=round(float(k_net[j]), 2), seed_range_cm=sticks[rank[j]]["seed_range_cm"],
                         b3lyp_cm=round(float(w_low[i]), 1), baseline_cm=baseline[i]["omega_cm"], family=fam,
                         error_cm={h: readouts[h][fam]["mean"] for h in HOLDOUTS}, lab_region=region,
                         u_band_cm=tolerance.get(region, {}).get("u_band")))
    return sorted(rows, key=lambda b: b["network_cm"])


def listing(smiles: str, b3lyp_cm: list[float], catalog: Catalog) -> dict | None:
    """The catalogue's row of the same molecule (canonical SMILES), with how far the B3LYP positions its export lists lie from this run's."""
    row = catalog.find(smiles)
    if row is None:
        return None
    mol = catalog.molecule(row["id"])
    out = dict(id=row["id"], name=row["name"], rung=int(row["rung"]), source=f"website export catalog.json, molecules/{row['id']}.json")
    listed = sorted(float(v) for v in mol["frequencies_cm"]["b3lyp"]["vibrational"]) if mol else []
    if len(listed) == len(b3lyp_cm):
        out["b3lyp_max_abs_diff_cm"] = round(max(abs(a - b) for a, b in zip(listed, sorted(b3lyp_cm), strict=True)), 1)
    return out


def certificate(folder: Path, catalog: Catalog) -> dict:
    r = load_result(folder)
    rec, adm = r.record, r.record["admission"]
    accuracy = network_accuracy(evaluation_records(r.models))
    w_low = RINT.mode_intensities(r.H_low, r.masses, r.apt)[0]
    listed = listing(adm["smiles"], [float(w) for w in w_low], catalog)
    tolerance = catalog.u_band(listed["name"] if listed else rec["name"])
    version = {m["version"] for m in adm["models"]}.pop()
    lic = licence_state()
    return dict(
        kind="live certificate", date=time.strftime("%Y-%m-%d %H:%M"), pipeline_version=rec["pipeline_version"],
        molecule=dict(name=rec["name"], smiles=adm["smiles"], formula=adm["formula"], n_atoms=adm["n_atoms"], elements=adm["elements"],
                      training_atoms=adm["training_atoms"], inside_training_sizes=adm["inside_training_sizes"], listed=listed),
        network=dict(name=P.NETWORK, version=version, models=adm["models"], predicts=HIGHER_LEVEL),
        accuracy=accuracy, bands=bands(r, accuracy, tolerance),
        tolerance=dict(per_region=tolerance, rule=FAMILY_SOURCE),
        licence=dict(statement=lic["statement"], rule_source=lic["rule_source"], licensed_families=lic["licensed_families"]),
        cost=dict(steps_s=rec["seconds"], **prices.price_of_run(sum(rec["seconds"].values()), rec["provenance"]["host"])),
        provenance=dict(result=str(folder), run_commit=rec["provenance"]["commit"], run_dirty=rec["provenance"]["dirty"],
                        certificate_commit=commit_hash(), deck_sha16=rec["deck"]["sha16"], low_level_software=rec["low_level"]["b3lyp"].get("software"),
                        host=rec["provenance"]["host"], note=rec["spectra"]["note"]),
        statement=(f"{rec['name']}: the harmonic infrared spectrum of {P.NETWORK} v{version} ({len(r.models)} seeds) — B3LYP/6-31G* corrected "
                   f"toward {HIGHER_LEVEL.split(' (')[0]} — with the error measured on molecules the network never saw; at the coupled-cluster "
                   f"level {CC_NOTE}. The scaled B3LYP spectrum is shown as the baseline only."))


def _band_lines(c: dict) -> list[str]:
    L = ["| network ω (cm⁻¹) | height (km/mol) | seeds' range | B3LYP ω | baseline ω | family | measured error (a) / (b), cm⁻¹ | "
         "laboratory region | u_band (cm⁻¹) |", "|---|---|---|---|---|---|---|---|---|"]
    for b in c["bands"]:
        lo, hi = b["seed_range_cm"]
        L.append(f"| {b['network_cm']} | {b['km_mol']} | {lo}–{hi} | {b['b3lyp_cm']} | {b['baseline_cm']} | {b['family']} | "
                 f"{b['error_cm']['a']} / {b['error_cm']['b']} | {b['lab_region']} | {b['u_band_cm'] if b['u_band_cm'] is not None else '—'} |")
    return L


def _accuracy_lines(a: dict) -> list[str]:
    hs = a["holdouts"]
    L = [f"Against {a['higher_level']}, seed means (each seed's value in brackets); targets: {a['target_source']}.", "",
         "| read-out | " + " | ".join(f"({h}), {v['n_molecules']} molecules" for h, v in hs.items()) + " | target |", "|---|---|---|---|"]
    for q in QUANTITIES:
        cells = [f"{v['readouts'][q]['mean']} ({', '.join(str(x) for x in v['readouts'][q]['seeds'])})" for v in hs.values()]
        target = next(iter(hs.values()))["readouts"][q]["target"]
        L.append(f"| {q} | " + " | ".join(cells) + f" | {target if target is not None else '—'} |")
    L += ["", "| spectral shape | " + " | ".join(f"({h}), {v['shape']['n_molecules']} with an APT" for h, v in hs.items()) + " |", "|---|---|---|"]
    for k, label in (("spectrum_overlap", "overlap, uncorrected → corrected"), ("intensity_error", "height error, uncorrected → corrected")):
        L.append(f"| {label} | " + " | ".join(f"{v['shape']['cheap'][k]} → {v['shape']['corrected'][k]}" for v in hs.values()) + " |")
    return [*L, "", f"*Hold-outs:* {hs['a']['description']}; {hs['b']['description']}. *Coupled cluster:* {a['coupled_cluster']}.",
            f"*Sources:* {'; '.join(a['sources'])}."]


def to_markdown(c: dict) -> str:
    m, n, k, p = c["molecule"], c["network"], c["cost"], c["provenance"]
    listed = m["listed"]
    L = [f"# Certificate — {m['name']} · pipeline {c['pipeline_version']} · {c['date']}", "", c["statement"], "", "## Molecule", "",
         f"- {m['smiles']}, {m['formula']}, {m['n_atoms']} atoms ({', '.join(m['elements'])}); the network's training set spans "
         f"{m['training_atoms'][0]}–{m['training_atoms'][1]} atoms: {'inside' if m['inside_training_sizes'] else 'OUTSIDE'}",
         "- catalogue: " + (f"listed as {listed['id']} ({listed['name']}, rung {listed['rung']}); its export's B3LYP positions lie within "
                            f"{listed.get('b3lyp_max_abs_diff_cm', '—')} cm⁻¹ of this run's ({listed['source']})" if listed else "not listed"),
         "", f"## Spectrum, band by band ({n['name']} v{n['version']}, {len(n['models'])} seeds)", "", *_band_lines(c), "",
         f"*Laboratory region and u_band:* {c['tolerance']['rule']}. *Positions:* {p['note']}.", "",
         "## How well the network is known (its own evaluation records)", "", *_accuracy_lines(c["accuracy"]), "",
         f"*Licence:* {c['licence']['statement']} ({c['licence']['rule_source']}).", "", "## Cost", "",
         f"- {k['machine']} ({k['machine_class']}): {k['seconds']} s = {k['hours']} h, € {k['eur_ex_vat']:.2f} ex VAT ({k['source']}); steps "
         + ", ".join(f"{s} {v} s" for s, v in k["steps_s"].items()), "", "## Provenance", "",
         f"- result {p['result']}; run at commit {p['run_commit'][:8]} (uncommitted changes: {p['run_dirty']}); certificate at {p['certificate_commit']}",
         f"- deck {p['deck_sha16']}; low level {json.dumps(p['low_level_software'], ensure_ascii=False)}; host {p['host']}",
         "- models: " + "; ".join(f"{Path(x['path']).name} ({x['status']}, sha16 {x['sha16']})" for x in n["models"]), ""]
    return "\n".join(L)


def write(c: dict, folder: Path) -> tuple[Path, Path]:
    pj, pm = folder / "certificate.json", folder / "certificate.md"
    P.write_json(pj, c)
    tmp = pm.with_suffix(".md.tmp")
    tmp.write_text(to_markdown(c), encoding="utf-8", newline="\n")
    os.replace(tmp, pm)
    return pj, pm


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("result", type=Path, help="a pipeline result folder (pipeline.json, correction.npz, the B3LYP Hessian and APT)")
    folder = ap.parse_args(argv).result.resolve()
    _, pm = write(certificate(folder, Catalog()), folder)
    print(f"[certificate] {pm}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
