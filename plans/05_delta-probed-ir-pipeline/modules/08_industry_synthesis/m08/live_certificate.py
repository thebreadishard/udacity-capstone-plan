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

from . import accuracy as A
from . import pipeline as P
from . import prices
from . import seen as S
from .catalog import FAMILY_SOURCE, Catalog
from .catalog import family as lab_region
from .certify import commit_hash
from .licence import state as licence_state
from .spectrum import cheap_apt, vib_min_cm

# isort: split
# module 05's code and probes/, on the path through m08.pipeline
import rungC_intensities as RINT
from learning_curve_layerA import molecule_features, normal_modes
from promotion_read import QUANTITIES

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


def rule_modes(r: Result, w_low: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[str], np.ndarray]:
    """The B3LYP vibrational modes of the rule the network's error is measured in (`normal_modes`: all but the six of smallest |ω|) —
    positions, mass-weighted shapes, each one's family (`molecule_features`, which also reads the folder's geometry) — and which of them the
    spectrum lists (above the line of `mode_intensities`); those must be the spectrum's modes `w_low`."""
    _, w_rule, V_rule, _ = normal_modes(r.H_low, r.masses)
    feats = molecule_features(r.folder, lo=r.H_low, hi=r.H_low)
    if np.abs(np.asarray(feats["freq"]) - w_rule).max() > 1e-6:
        raise RuntimeError(f"{r.folder.name}: the family rule's modes are not its normal modes")
    above = np.abs(w_rule) > vib_min_cm()
    if above.sum() != len(w_low) or np.abs(w_rule[above] - w_low).max() > 1e-6:
        raise RuntimeError(f"{r.folder.name}: the family rule's modes above the line are not the spectrum's")
    return w_rule, V_rule, list(feats["family"]), above


def mode_families(r: Result, w_low: np.ndarray) -> list[str]:
    """The family of each listed B3LYP mode `w_low` by the rule the network's error is measured in."""
    _, _, families, above = rule_modes(r, w_low)
    return [f for f, a in zip(families, above, strict=True) if a]


def bands(r: Result, accuracy: dict, tolerance: dict[str, dict], licensed: list[str]) -> list[dict]:
    """One row per corrected mode, sorted by position, paired with the B3LYP mode of largest overlap among all its modes
    (`rungC_intensities.match_modes`, the evaluation's pairing): its family, the B3LYP, baseline and network positions, the height, the seeds'
    range as the record holds it, the measured error of its family on both hold-outs, whether that family is licensed, and the laboratory
    tolerance of its region. The B3LYP partner is sought among the family rule's modes (`rule_modes`), so a corrected mode whose partner lies
    under the line of `mode_intensities` (a near-free rotor the network stiffens) keeps its family; it has no baseline, which lists the B3LYP
    spectrum's bands."""
    w_low = RINT.mode_intensities(r.H_low, r.masses, r.apt)[0]
    w_rule, V_rule, families, above = rule_modes(r, w_low)
    listed = np.cumsum(above) - 1                                  # a mode's index among the listed B3LYP modes, where it is one
    w_net, k_net, L_net = RINT.mode_intensities(r.H_low + r.dH, r.masses, r.apt, return_modes=True)
    sticks = r.record["spectra"]["network"]["sticks"]
    if len(sticks) != len(w_net) or max(abs(s["omega_cm"] - w) for s, w in zip(sticks, np.sort(w_net), strict=True)) > STICK_TOL_CM:
        raise RuntimeError(f"{r.folder.name}: the recorded network spectrum is not the one H_low + ΔH gives")
    baseline = r.record["spectra"]["baseline"]["sticks"]           # in the B3LYP modes' order (ascending), as the pipeline scaled them
    if len(baseline) != len(w_low):
        raise RuntimeError(f"{r.folder.name}: the recorded baseline has {len(baseline)} bands, the B3LYP Hessian {len(w_low)}")
    rank = np.argsort(np.argsort(w_net))
    readouts = {h: accuracy["holdouts"][h]["readouts"] for h in A.HOLDOUTS}
    rows = []
    for j, k in enumerate(RINT.match_modes(L_net, V_rule)):
        fam, region = families[k], lab_region(float(w_net[j]))
        rows.append(dict(network_cm=round(float(w_net[j]), 1), km_mol=round(float(k_net[j]), 2), seed_range_cm=sticks[rank[j]]["seed_range_cm"],
                         b3lyp_cm=round(float(w_rule[k]), 1), baseline_cm=baseline[int(listed[k])]["omega_cm"] if above[k] else None,
                         family=fam, licensed=fam in licensed, error_cm={h: readouts[h][fam]["mean"] for h in A.HOLDOUTS}, lab_region=region,
                         u_band_cm=tolerance.get(region, {}).get("u_band")))
    return [row for _, row in sorted(zip(rank, rows, strict=True), key=lambda t: t[0])]      # the record's stick order


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
    accuracy = A.network_accuracy(A.evaluation_records(r.models))
    w_low = RINT.mode_intensities(r.H_low, r.masses, r.apt)[0]
    listed = listing(adm["smiles"], [float(w) for w in w_low], catalog)
    tolerance = catalog.u_band(listed["name"] if listed else rec["name"])
    version = {m["version"] for m in adm["models"]}.pop()
    lic = licence_state(accuracy)
    seen = S.status(adm["smiles"], S.load(tuple(Path(m["path"]) for m in adm["models"])), listed["id"] if listed else None)
    truth = S.truth_beside(listed["id"], rec["spectra"]["network"]["sticks"]) if listed else None
    return dict(
        kind="live certificate", date=time.strftime("%Y-%m-%d %H:%M"), pipeline_version=rec["pipeline_version"],
        molecule=dict(name=rec["name"], smiles=adm["smiles"], formula=adm["formula"], n_atoms=adm["n_atoms"], elements=adm["elements"],
                      training_atoms=adm["training_atoms"], inside_training_sizes=adm["inside_training_sizes"], listed=listed,
                      seen=seen, truth=truth),
        network=dict(name=P.NETWORK, version=version, models=adm["models"], predicts=A.HIGHER_LEVEL),
        accuracy=accuracy, bands=bands(r, accuracy, tolerance, lic["licensed_families"]),
        tolerance=dict(per_region=tolerance, rule=FAMILY_SOURCE),
        licence=dict(statement=lic["statement"], rule_source=lic["rule_source"], licensed_families=lic["licensed_families"]),
        cost=dict(steps_s=rec["seconds"], **prices.price_of_run(sum(rec["seconds"].values()), rec["provenance"]["host"])),
        provenance=dict(result=str(folder), run_commit=rec["provenance"]["commit"], run_dirty=rec["provenance"]["dirty"],
                        certificate_commit=commit_hash(), deck_sha16=rec["deck"]["sha16"], low_level_software=rec["low_level"]["b3lyp"].get("software"),
                        host=rec["provenance"]["host"], note=rec["spectra"]["note"]),
        statement=(f"{rec['name']}: the harmonic infrared spectrum of {P.NETWORK} v{version} ({len(r.models)} seeds) — B3LYP/6-31G* corrected "
                   f"toward {A.HIGHER_LEVEL.split(' (')[0]} — with the error measured on molecules the network never saw; licensed for "
                   f"{', '.join(lic['licensed_families']) or 'no family'} (decision 65), each band marked; at the coupled-cluster level "
                   f"{A.CC_NOTE}. The scaled B3LYP spectrum is shown as the baseline only. This molecule: {seen['text']}."))


def _band_lines(c: dict) -> list[str]:
    L = ["| network ω (cm⁻¹) | height (km/mol) | seeds' range | B3LYP ω | baseline ω | family | licensed | measured error (a) / (b), cm⁻¹ | "
         "laboratory region | u_band (cm⁻¹) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for b in c["bands"]:
        lo, hi = b["seed_range_cm"]
        baseline = b["baseline_cm"] if b["baseline_cm"] is not None else f"— (B3LYP under {vib_min_cm():g} cm⁻¹)"
        L.append(f"| {b['network_cm']} | {b['km_mol']} | {lo}–{hi} | {b['b3lyp_cm']} | {baseline} | {b['family']} | "
                 f"{'yes' if b['licensed'] else 'no'} | {b['error_cm']['a']} / {b['error_cm']['b']} | {b['lab_region']} | "
                 f"{b['u_band_cm'] if b['u_band_cm'] is not None else '—'} |")
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


def _truth_lines(t: dict | None) -> list[str]:
    if t is None:
        return []
    rank = f"positions paired by rank, rms {t['rms_by_rank_cm']} cm⁻¹" if t["rms_by_rank_cm"] is not None else "band counts differ, no rank pairing"
    shape = f"spectrum overlap {t['overlap']}" if t["overlap"] is not None else "no APT in the corpus folder, no overlap"
    return [f"- the ωB97X truth is in the corpus ({t['source']}, {t['n_bands']} bands): the network against it, {shape}; {rank} "
            "(both independent of the atom order)"]


def to_markdown(c: dict) -> str:
    m, n, k, p = c["molecule"], c["network"], c["cost"], c["provenance"]
    listed = m["listed"]
    L = [f"# Certificate — {m['name']} · pipeline {c['pipeline_version']} · {c['date']}", "", c["statement"], "", "## Molecule", "",
         f"- {m['smiles']}, {m['formula']}, {m['n_atoms']} atoms ({', '.join(m['elements'])}); the network's training set spans "
         f"{m['training_atoms'][0]}–{m['training_atoms'][1]} atoms: {'inside' if m['inside_training_sizes'] else 'OUTSIDE'}",
         "- catalogue: " + (f"listed as {listed['id']} ({listed['name']}, rung {listed['rung']}); its export's B3LYP positions lie within "
                            f"{listed.get('b3lyp_max_abs_diff_cm', '—')} cm⁻¹ of this run's ({listed['source']})" if listed else "not listed"),
         f"- the network: {m['seen']['text']}", *_truth_lines(m["truth"]),
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
