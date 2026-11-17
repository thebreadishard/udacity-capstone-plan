"""The certificate of a live pipeline result (`m08/pipeline.py`; build step 4 of TASKS 146): the network's spectrum band by band — each
band at its best estimate, the anharmonic position ν where the pipeline's step 6 gave one and the harmonic ω beside it, with the
sentence that says which it is and that ν carries no licence (`m08/positions.py`, TASKS 211) — with the
seeds' spread, the measured error of the network version that ran — per mode family and hold-out, the error of what the pipeline
delivers from its product-error record (the licence's quantity) and the first-order read-outs of its evaluation records, each under
its name and set against the registered target — the B3LYP level and the scaled-B3LYP baseline beside it, the laboratory tolerance of each band's region,
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
from pathlib import Path, PureWindowsPath

import numpy as np

from . import accuracy as A
from . import pipeline as P
from . import positions as POS
from . import prices
from . import seen as S
from .catalog import FAMILY_SOURCE, Catalog
from .catalog import family as lab_region
from .certify import commit_hash
from .licence import caveat_sentence
from .licence import state as licence_state
from .spectrum import cheap_apt, vib_min_cm

# isort: split
# module 05's code and probes/, on the path through m08.pipeline
import rungC_intensities as RINT
from anharmonic_step import NOT_MEASURED_TEXT, REASON_TEXT
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
    # the recorded paths are the laptop's (Windows); PureWindowsPath splits on both separators, so the names read alike on Linux (CI)
    if models != tuple(PureWindowsPath(m["path"]).name for m in rec["admission"]["models"]):
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
    range as the record holds it, the error of its family on both hold-outs in the quantity the licence reads (`A.stated_errors`), whether
    that family is licensed — a statement about the harmonic position ω — the position the band is printed at with the anharmonic
    step's Δ_anh and bar where it has one (`POS.band`, from the record's stick), and the laboratory
    tolerance of the printed position's region. The B3LYP partner is sought among the family rule's modes (`rule_modes`), so a corrected mode whose partner lies
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
    _, errors = A.stated_errors(accuracy)
    summary = POS.summary_of(r.record["spectra"])
    rows = []
    for j, k in enumerate(RINT.match_modes(L_net, V_rule)):
        position = POS.band(sticks[rank[j]], summary, REASON_TEXT, NOT_MEASURED_TEXT)
        fam, region = families[k], lab_region(float(w_net[j]) if position["nu_cm"] is None else position["nu_cm"])
        rows.append(dict(network_cm=round(float(w_net[j]), 1), km_mol=round(float(k_net[j]), 2), seed_range_cm=sticks[rank[j]]["seed_range_cm"],
                         b3lyp_cm=round(float(w_rule[k]), 1), baseline_cm=baseline[int(listed[k])]["omega_cm"] if above[k] else None,
                         family=fam, licensed=fam in licensed, error_cm=dict(errors[fam]), lab_region=region,
                         u_band_cm=tolerance.get(region, {}).get("u_band"), **position))
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


def licence_block(lic: dict) -> dict:
    """What a certificate keeps of the licence (`licence.state`): the statement, the rule's source, the licensed families, the quantity
    it is read on and its caveats."""
    return {k: lic[k] for k in ("statement", "rule_source", "licensed_families", "quantity", "quantity_name", "caveats")}


# design note of 17 Nov 2026, §3, word for word: what made the spectrum, how each network used the molecules, whose error is stated
RELEASE_MADE = "The spectrum is made by the release networks of version {version}, trained on all {n} molecules with labels"
RELEASE_FITTED = (": each of the {k} networks is fitted on a random {fitted} % of them and stopped on the other {stopped} %, a different "
                  "{stopped} % per seed, so a molecule is fitted by most of the networks and not by every one (rarely by none)")
RELEASE_MEASURED = (". Its error bars were measured on the measurement networks of the same version — the same recipe trained without the "
                    "hold-out molecules — on molecules those networks never saw; the release networks themselves have seen every molecule "
                    "we hold labels for, so they have no held-out error of their own.")
HELD_BACK_SENTENCE = ("Version {version} has release networks, and they did not make this spectrum: {reason}. It is made by the "
                      "measurement networks, whose error was measured on molecules they never saw.")


@dataclass(frozen=True)
class MadeBy:
    """Decision 66's part of a certificate: the number of molecules the release networks that made the spectrum trained on, or why
    the version's release networks did not make it. Neither: measurement networks made it and the version has no other."""

    release_trained_on: int | None = None
    held_back: str | None = None
    inner_validation: float = 0.0          # the share of the molecules each release network was stopped on, not fitted on


NO_RELEASE = MadeBy()


def release_sentence(version: str, n_seeds: int, made_by: MadeBy) -> str:
    """Design note §3's sentence for a spectrum the release networks made. 'Trained on all N' is said with what each network did
    with the N: under inner validation it is fitted on a part and stopped on the rest."""
    fitted = ""
    if made_by.inner_validation:
        fitted = RELEASE_FITTED.format(k=n_seeds, fitted=f"{100 * (1 - made_by.inner_validation):g}", stopped=f"{100 * made_by.inner_validation:g}")
    return RELEASE_MADE.format(version=version, n=made_by.release_trained_on) + fitted + RELEASE_MEASURED


def statement(name: str, version: str, n_seeds: int, lic: dict, seen_text: str, made_by: MadeBy = NO_RELEASE) -> str:
    """The certificate's opening sentence; it names the licensed families, so the licence's caveat follows it. It says what the
    licence is a statement about — the harmonic position ω; which position each band is printed at is the paragraph after it
    (`positions.note`). When release networks made the spectrum, design note §3's sentence stands in place of 'with the error
    measured on molecules the network never saw', and the error is named as the measurement networks'."""
    opening = f"{name}: the infrared spectrum of {P.NETWORK} v{version} ({n_seeds} seeds) — B3LYP/6-31G* corrected toward {A.HIGHER_LEVEL.split(' (')[0]}"
    if made_by.release_trained_on is None:
        measured = f" — with the {lic['quantity_name']} measured on molecules the network never saw; the "
    else:
        measured = (f". {release_sentence(version, n_seeds, made_by)} The error stated is the measurement networks' "
                    f"{lic['quantity_name']}; the ")
    return " ".join(filter(None, [
        f"{opening}{measured}"
        f"harmonic positions ω are licensed for {', '.join(lic['licensed_families']) or 'no family'} (decision 65), each band marked; at "
        f"the coupled-cluster level {A.CC_NOTE}. The scaled B3LYP spectrum is shown as the baseline only. This molecule and the "
        f"ΔH network: {seen_text}.",
        HELD_BACK_SENTENCE.format(version=version, reason=made_by.held_back) if made_by.held_back else None,
        caveat_sentence(lic)]))


def error_bar_models(adm: dict) -> list[dict]:
    """The registry entries of the networks whose records give the error: the measurement networks beside release networks that ran
    (decision 66), else the models that ran — every record written before the decision, and every run of measurement networks."""
    return adm.get("measurement_models") or adm["models"]


def certificate(folder: Path, catalog: Catalog) -> dict:
    r = load_result(folder)
    rec, adm = r.record, r.record["admission"]
    measured = error_bar_models(adm)
    released = bool(adm.get("measurement_models"))
    ran = tuple(Path(m["path"]) for m in adm["models"])
    sha16 = {PureWindowsPath(m["path"]).name: m["sha16"] for m in measured}
    accuracy = A.accuracy_of(tuple(sha16), sha16)
    w_low = RINT.mode_intensities(r.H_low, r.masses, r.apt)[0]
    listed = listing(adm["smiles"], [float(w) for w in w_low], catalog)
    tolerance = catalog.u_band(listed["name"] if listed else rec["name"])
    version = {m["version"] for m in adm["models"]}.pop()
    lic = licence_state(accuracy)
    seen = S.status(adm["smiles"], S.load(tuple(Path(m["path"]) for m in measured)), listed["id"] if listed else None,
                    S.release_index(ran) if released else None)
    made_by = MadeBy(len(P.train_ids(ran)) if released else None, adm.get("release_held_back"),
                     P.inner_validation_share(ran) if released else 0.0)
    truth = S.truth_beside(listed["id"], rec["spectra"]["network"]["sticks"]) if listed else None
    summary = POS.summary_of(rec["spectra"])
    return dict(
        kind="live certificate", date=time.strftime("%Y-%m-%d %H:%M"), pipeline_version=rec["pipeline_version"],
        molecule=dict(name=rec["name"], smiles=adm["smiles"], formula=adm["formula"], n_atoms=adm["n_atoms"], elements=adm["elements"],
                      training_atoms=adm["training_atoms"], inside_training_sizes=adm["inside_training_sizes"], listed=listed,
                      seen=seen, truth=truth),
        network=dict(name=P.NETWORK, version=version, models=adm["models"], predicts=A.HIGHER_LEVEL)
        | ({"kind": P.NK.RELEASE, "trained_on_molecules": made_by.release_trained_on, "inner_validation": made_by.inner_validation,
            "measurement_models": measured} if released else {})
        | ({"release_held_back": made_by.held_back} if made_by.held_back else {}),
        accuracy=accuracy, bands=bands(r, accuracy, tolerance, lic["licensed_families"]),
        tolerance=dict(per_region=tolerance, rule=FAMILY_SOURCE),
        licence=licence_block(lic) | {"concerns": POS.LICENCE_SCOPE},
        positions=dict(note=POS.note(summary), cautions=POS.cautions(summary), anharmonic=summary, drawn=POS.DRAWN),
        deliveries=rec.get("deliveries", []), delivery=len(rec.get("deliveries", [])) or None,
        cost=dict(steps_s=rec["seconds"], **prices.price_of_run(sum(rec["seconds"].values()), rec["provenance"]["host"])),
        provenance=dict(result=str(folder), run_commit=rec["provenance"]["commit"], run_dirty=rec["provenance"]["dirty"],
                        certificate_commit=commit_hash(), deck_sha16=rec["deck"]["sha16"], low_level_software=rec["low_level"]["b3lyp"].get("software"),
                        host=rec["provenance"]["host"], note=POS.note(summary),
                        reused_from=rec["reuse"]["source"] if "reuse" in rec and rec["reuse"]["reused"] else None),
        statement=statement(rec["name"], version, len(r.models), lic, seen["text"], made_by))


def _position_lines(bands: list[dict]) -> list[str]:
    """Which position each band is printed at, one line per kind — an anharmonic estimate with its family's bar, one without a
    bar, a harmonic position with its reason — naming the bands by their printed positions."""
    kinds: dict[str, list[str]] = {}
    for b in bands:
        kinds.setdefault(b["position_note"], []).append(str(b["printed_cm"]))
    return [f"- {note} — {len(at)} band(s): {', '.join(at)} cm⁻¹" for note, at in kinds.items()]


def _band_lines(c: dict) -> list[str]:
    """The band table: the printed position first, named ν or ω, the harmonic ω and the step beside it; 'ω licensed' is the
    licence of the harmonic position, never of ν. A certificate without the step keeps one sentence instead of a line per kind."""
    L = [f"| best estimate (cm⁻¹) | printed | harmonic ω, network | Δ_anh | {POS.BAR_HEADER} | height (km/mol) | "
         f"seeds' range of ω | B3LYP ω | baseline ω | family | ω licensed | {c['licence']['quantity_name']} of ω on (a) / (b), cm⁻¹ | "
         "laboratory region | u_band (cm⁻¹) |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in c["bands"]:
        lo, hi = b["seed_range_cm"]
        baseline = b["baseline_cm"] if b["baseline_cm"] is not None else f"— (B3LYP under {vib_min_cm():g} cm⁻¹)"
        step = "—" if b["delta_anh_cm"] is None else f"{b['delta_anh_cm']:+}"
        bar = "—" if b["delta_anh_cm"] is None else ("not measured" if b["step_bar_cm"] is None else b["step_bar_cm"])
        L.append(f"| {b['printed_cm']} | {b['printed']} | {b['network_cm']} | {step} | {bar} | {b['km_mol']} | {lo}–{hi} | {b['b3lyp_cm']} | "
                 f"{baseline} | {b['family']} | {'yes' if b['licensed'] else 'no'} | {b['error_cm']['a']} / {b['error_cm']['b']} | "
                 f"{b['lab_region']} | {b['u_band_cm'] if b['u_band_cm'] is not None else '—'} |")
    caveat = caveat_sentence(c["licence"])
    L += ["", f"*{caveat}*"] if caveat else []
    if c["positions"]["anharmonic"]["status"] == POS.APPLIED:
        L += ["", f"Which position each band is printed at ({POS.LICENCE_SCOPE}):", "", *_position_lines(c["bands"])]
    return L


def _product_lines(a: dict) -> list[str]:
    """The quantity the licence reads, per family and hold-out, with what each value rests on."""
    hs = a["holdouts"]
    L = [f"The licence reads the {a['quantities'][A.PRODUCT]} ({a['definitions'][A.PRODUCT]}).", "",
         "| family | " + " | ".join(f"({h}), {v['n_molecules']} molecules" for h, v in hs.items()) + " | line |", "|---|---|---|---|"]
    for f in A.FAMILIES:
        cells = [f"{p['rms']} (95 % interval over molecules {p['interval'][0]}–{p['interval'][1]}; {p['n_modes']} bands)"
                 for p in (v[A.PRODUCT][f] for v in hs.values())]
        L.append(f"| {f} | " + " | ".join(cells) + f" | {A.LICENCE_LINE_CM:g} |")
    return L


def _accuracy_lines(a: dict) -> list[str]:
    hs = a["holdouts"]
    L = [f"Against {a['higher_level']}; two quantities, each under its name.", "", *_product_lines(a), "",
         f"Beside it the evaluation records' read-outs — the {a['quantities']['readouts']} (each seed's value in brackets), which the "
         f"licence read until {A.AMENDED} — and the coupling ratio; targets: {a['target_source']}.", "",
         "| read-out | " + " | ".join(f"({h}), {v['n_molecules']} molecules" for h, v in hs.items()) + " | target |", "|---|---|---|---|"]
    for q in QUANTITIES:
        cells = [f"{v['readouts'][q]['mean']} ({', '.join(str(x) for x in v['readouts'][q]['seeds'])})" for v in hs.values()]
        target = next(iter(hs.values()))["readouts"][q]["target"]
        L.append(f"| {q} | " + " | ".join(cells) + f" | {target if target is not None else '—'} |")
    L += ["", "| spectral shape | " + " | ".join(f"({h}), {v['shape']['n_molecules']} with an APT" for h, v in hs.items()) + " |", "|---|---|---|"]
    for k, label in (("spectrum_overlap", "overlap, uncorrected → corrected"), ("intensity_error", "height error, uncorrected → corrected")):
        L.append(f"| {label} | " + " | ".join(f"{v['shape']['cheap'][k]} → {v['shape']['corrected'][k]}" for v in hs.values()) + " |")
    return [*L, "", f"*Read-outs:* {a['definitions']['family']}.",
            f"*Hold-outs:* {hs['a']['description']}; {hs['b']['description']}. *Coupled cluster:* {a['coupled_cluster']}.",
            f"*Sources:* {'; '.join(a['sources'])}."]


def _truth_lines(t: dict | None) -> list[str]:
    if t is None:
        return []
    rank = f"positions paired by rank, rms {t['rms_by_rank_cm']} cm⁻¹" if t["rms_by_rank_cm"] is not None else "band counts differ, no rank pairing"
    shape = f"spectrum overlap {t['overlap']}" if t["overlap"] is not None else "no APT in the corpus folder, no overlap"
    return [f"- the ωB97X truth is in the corpus ({t['source']}, {t['n_bands']} bands): the network against it, {shape}; {rank} "
            "(both independent of the atom order)"]


CAUTION_LABELS = (("nu_error", "What the bar is, and what ν's error is"), ("targets", "What the bars rest on"),
                  ("composition", "This molecule's elements in the anharmonic model's table"))


def _sentence(text: str) -> str:
    return f"{text[0].upper()}{text[1:]}."


def _position_paragraphs(c: dict) -> list[str]:
    """Under the statement: the positions sentence, then — once per certificate with the step — what the bar is and what ν's
    error is, what the bars rest on, and where it applies how few molecules of these elements the model's table holds."""
    said = c["positions"].get("cautions") or {}
    L = [f"**Positions.** {_sentence(c['positions']['note'])}", ""]
    for key, label in CAUTION_LABELS:
        if said.get(key):
            L += [f"**{label}.** {_sentence(said[key])}", ""]
    return L


def _delivery_lines(c: dict) -> list[str]:
    """The pipeline's deliveries of this result with their times, the first with its deadline; a certificate of an older record
    has none to list."""
    return [f"- delivery {x.get('number', i)} — {x['delivery']}: {x['at']}, {x['seconds_since_start']} s after the start"
            + (f"; final by {x['final_by']}, and if no later delivery stands here by then, this one is final" if x.get("final_by") else "")
            for i, x in enumerate(c.get("deliveries", []), 1)]


DELIVERY_MARK = "<!-- delivery {} -->"          # in certificate.md; certificate.json holds the same number under 'delivery'


class MismatchedPair(ValueError):
    """certificate.json and certificate.md of a folder are not of the same delivery."""


def read_certificate(folder: Path) -> dict:
    """A result folder's certificate record, refused where certificate.md beside it is of another delivery: the two files are
    replaced one after the other, and a page must not show one delivery's numbers beside a link to the other's text. A record
    written before the deliveries were numbered has no number to compare."""
    c = json.loads((folder / "certificate.json").read_text(encoding="utf-8"))
    number = c.get("delivery")
    if number is not None:
        page = folder / "certificate.md"
        if not page.is_file() or DELIVERY_MARK.format(number) not in page.read_text(encoding="utf-8"):
            raise MismatchedPair(f"{folder}: certificate.json is delivery {number} and certificate.md is not; a delivery was "
                                 "interrupted between the two files — write the pair again with python -m m08.live_certificate")
    return c


def to_markdown(c: dict) -> str:
    m, n, k, p = c["molecule"], c["network"], c["cost"], c["provenance"]
    listed = m["listed"]
    model_seen = (c["positions"].get("cautions") or {}).get("seen")
    mark = [DELIVERY_MARK.format(c["delivery"]), ""] if c.get("delivery") else []
    L = [f"# Certificate — {m['name']} · pipeline {c['pipeline_version']} · {c['date']}", "", *mark, c["statement"], "",
         *_position_paragraphs(c), "## Molecule", "",
         f"- {m['smiles']}, {m['formula']}, {m['n_atoms']} atoms ({', '.join(m['elements'])}); the network's training set spans "
         f"{m['training_atoms'][0]}–{m['training_atoms'][1]} atoms: {'inside' if m['inside_training_sizes'] else 'OUTSIDE'}",
         "- catalogue: " + (f"listed as {listed['id']} ({listed['name']}, rung {listed['rung']}); its export's B3LYP positions lie within "
                            f"{listed.get('b3lyp_max_abs_diff_cm', '—')} cm⁻¹ of this run's ({listed['source']})" if listed else "not listed"),
         f"- the ΔH network: {m['seen']['text']}", *([f"- {model_seen}"] if model_seen else []), *_truth_lines(m["truth"]),
         *_delivery_lines(c),
         "", f"## Spectrum, band by band ({n['name']} v{n['version']}, {len(n['models'])} seeds)", "", *_band_lines(c), "",
         f"*Laboratory region and u_band:* {c['tolerance']['rule']}, read at the printed position.", "",
         "## How well the network is known (its product-error record and its evaluation records)", "", *_accuracy_lines(c["accuracy"]), "",
         f"*Licence:* {c['licence']['statement']} ({c['licence']['rule_source']}).", "", "## Cost", "",
         f"- {k['machine']} ({k['machine_class']}): {k['seconds']} s = {k['hours']} h, € {k['eur_ex_vat']:.2f} ex VAT ({k['source']}); steps "
         + ", ".join(f"{s} {v} s" for s, v in k["steps_s"].items()), "", "## Provenance", "",
         f"- result {p['result']}; run at commit {p['run_commit'][:8]} (uncommitted changes: {p['run_dirty']}); certificate at {p['certificate_commit']}",
         f"- deck {p['deck_sha16']}; low level {json.dumps(p['low_level_software'], ensure_ascii=False)}; host {p['host']}",
         "- models: " + "; ".join(f"{Path(x['path']).name} ({x['status']}, sha16 {x['sha16']})" for x in n["models"]),
         *_measurement_lines(n), ""]
    return "\n".join(L)


def _measurement_lines(network: dict) -> list[str]:
    """Under release networks: the measurement networks whose records give the error bars; nothing otherwise."""
    if "measurement_models" not in network:
        return []
    return [f"- the models above are release networks, trained on {network['trained_on_molecules']} molecules (each fitted on "
            f"{100 * (1 - network['inner_validation']):g} % of them and stopped on the rest); the error bars are those of the "
            "measurement networks: " + "; ".join(f"{Path(x['path']).name} (sha16 {x['sha16']})" for x in network["measurement_models"])]


def write(c: dict, folder: Path) -> tuple[Path, Path]:
    """The certificate's two files as a pair: both written whole to temp files first, then moved over the old ones, the record
    before the page. Each carries the delivery's number, so a pair cut between the two moves is detectable (`read_certificate`)."""
    pj, pm = folder / "certificate.json", folder / "certificate.md"
    tj, tm = pj.with_suffix(".json.tmp"), pm.with_suffix(".md.tmp")
    tj.write_text(json.dumps(c, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    tm.write_text(to_markdown(c), encoding="utf-8", newline="\n")
    os.replace(tj, pj)
    os.replace(tm, pm)
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
