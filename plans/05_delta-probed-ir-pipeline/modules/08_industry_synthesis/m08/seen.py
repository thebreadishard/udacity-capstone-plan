"""Has the network seen this molecule? (TASKS 155: the demo's molecule must be unseen, and a molecule the network trained on must not be read
by the hold-out error.) The carried models' training ids — every molecule a seed fitted or stopped on — come from the checkpoints
(`pipeline.train_ids`), the hold-outs from the models' evaluation records, the SMILES from the corpus manifest. A molecule is matched by its
canonical SMILES, not by its id, so the same molecule under another id is caught. Where the corpus holds the molecule's ωB97X Hessian the
truth is set beside the network's spectrum without an atom mapping: positions paired by rank and the overlap of the broadened spectra, both
independent of the atom order and the frame."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import accuracy as A
from . import pipeline as P
from .molecule import canonical, without_stereo
from .spectrum import cheap_apt, overlap, series

MANIFEST = P.M05 / "corpus" / "manifest.csv"
CATION_LAYER = "P3c"                   # a cation row carries its neutral parent's SMILES; a cation is not its parent
TEXT = {
    "trained": "in the network's training set ({ids}): the hold-out error is not this molecule's measure",
    "trained_and_held_out": "in the network's training set ({ids}) and also in hold-out ({h}) as {held}: that hold-out was not clean for it, "
                            "and the hold-out error is not this molecule's measure",
    "a": "held out, hold-out (a) ({ids}): never trained on; the measured error includes it",
    "b": "held out, hold-out (b) ({ids}): never trained on; the measured error includes it",
    "catalogue": "in the catalogue ({ids}) but not among the molecules the network trained on",
    "unseen": "not in the catalogue: the network has not seen it",
    # aromir's sentence (certificate.py): an xyz request names its sulfoxide's configuration, the training SMILES leave it open
    "stereoisomer": "a stereoisomer of it, or the molecule itself written with other stereo labels, is in the network's training set ({ids})",
    "stereoisomer_held_out": "a stereoisomer of it, or the molecule itself written with other stereo labels, is held out, hold-out "
                             "({h}) ({ids}): never trained on",
    "unseen_neutral": "not in the catalogue as a neutral molecule: the network has not seen it as one",
    # decision 66 (design note of 17 Nov 2026, §3): the line for a molecule the release networks trained on
    "release_trained": "in the release networks' training data: the error bars are not an out-of-sample error for this molecule; "
                       "expect it to be smaller",
    # the clause for a neutral molecule whose radical cation the networks trained on (TASKS 253, 257, 264): seed 0 of v1.4's recipe,
    # benzene's corrected-frequency rms 5.37 cm-1 with the whole P3c layer (about 50 cations, benzene's among them) and 1.47 without it
    # (probes/results_m1/v14_data_read_2026-11-17/probe_nop3c.txt, cation_twins.txt): the layer was removed, not benzene's cation alone
    "cation_trained": "its radical cation ({ids}) is in the networks' training data; in a test on one network, training without the cation "
                      "layer (about 50 cations, benzene's among them) lowered neutral benzene's error from 5.4 to 1.5 cm⁻¹, so this "
                      "molecule's error may be larger than the measured one",
}


@dataclass(frozen=True)
class Seen:
    """Canonical SMILES → the ids the network trained on under it, → (hold-out, ids) for the hold-out molecules, and → the ids of that
    neutral molecule's radical cations the network trained on (a cation is not its parent: it never makes the parent 'trained')."""
    trained: dict[str, list[str]]
    holdout: dict[str, tuple[str, list[str]]]
    cations: dict[str, list[str]]


def by_smiles(ids: set[str], smiles_of: dict[str, str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for i in sorted(ids):
        if i not in smiles_of:
            raise KeyError(f"{i} is not a neutral row of the corpus manifest")
        c = canonical(smiles_of[i])
        if c is None:
            raise ValueError(f"{i}: its manifest SMILES does not parse")
        out.setdefault(c, []).append(i)
    return out


def build(trained_ids: set[str], holdout_ids: dict[str, set[str]], smiles_of: dict[str, str],
          cation_smiles: dict[str, str] | None = None) -> Seen:
    """The index. A molecule may be both trained on and held out, under two ids (a hold-out molecule's twin in another layer); `status`
    names it, and `leaks` lists them. A trained id that is a cation row (`cation_smiles`: id → its parent's SMILES) is indexed under its
    parent, apart from the neutral ones; every other trained id must be a neutral row."""
    cation_ids = {i for i in trained_ids if i in (cation_smiles or {})}
    holdout = {c: (h, ids) for h, these in holdout_ids.items() for c, ids in by_smiles(these, smiles_of).items()}
    return Seen(by_smiles(trained_ids - cation_ids, smiles_of), holdout, by_smiles(cation_ids, cation_smiles or {}))


def leaks(seen: Seen) -> dict[str, tuple[str, list[str], list[str]]]:
    """Canonical SMILES → (hold-out, its ids there, its ids in the training set) for every hold-out molecule the network also trained on.
    A hold-out molecule's cation twin is not listed here: the training (`--holdout-twins drop-any-charge`) and the readers (rungC_eval_saved,
    release_checks) refuse it upstream (TASKS 253, m05/holdout_twins.py); `status` still names it."""
    return {c: (seen.holdout[c][0], seen.holdout[c][1], seen.trained[c]) for c in sorted(set(seen.trained) & set(seen.holdout))}


def manifest_smiles() -> tuple[dict[str, str], dict[str, str]]:
    """The manifest's rows, id → SMILES: the neutral rows, and the cation rows (which carry their neutral parent's SMILES)."""
    neutral: dict[str, str] = {}
    cation: dict[str, str] = {}
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            (cation if r["layer"] == CATION_LAYER else neutral)[r["id"]] = r["smiles"]
    return neutral, cation


def release_index(models: tuple[Path, ...]) -> Seen:
    """The index of the release networks' training data (decision 66); they hold nothing out. The pipeline's molecules are neutral and a
    cation is not its parent, so the cation rows the networks trained on are indexed apart, under their parent."""
    return build(P.train_ids(models), {}, *manifest_smiles())


def load(models: tuple[Path, ...]) -> Seen:
    """The index for the measurement networks whose records give the error: the models that ran, or — when release networks ran —
    their version's measurement networks."""
    neutral, cation = manifest_smiles()
    holdout_ids: dict[str, set[str]] = {h: set() for h in A.HOLDOUTS}
    for record in A.evaluation_records(tuple(A.model_key(p) for p in models)):
        rec = json.loads(record.read_text(encoding="utf-8"))
        for h, ids in holdout_ids.items():
            ids |= set(rec[h]["per_molecule"])
    return build(P.train_ids(models), holdout_ids, neutral, cation)


def status(smiles: str, seen: Seen, listed_id: str | None, release: Seen | None = None) -> dict:
    """Trained on, held out, in the catalogue only, or unseen; with the ids and the certificate's sentence. `release` (`release_index`) is
    given when release networks made the spectrum: a molecule in their training data gets decision 66's line, whatever it is to the
    measurement networks; any other molecule is read as always. A molecule whose radical cation the networks that made the spectrum
    (the release networks when `release` is given, else the measurement networks) trained on, while they did not train on the molecule
    itself, keeps its role and gains `cation_trained` and a clause saying so: networks that fitted the molecule's own answer are not
    what the cation test measured. For every other molecule the record is as it was. Release networks that lack a molecule the
    measurement networks trained on are refused: decision 66's release set holds the measurement set."""
    c = covering_key(canonical(smiles), seen, release)
    if release is not None and c in seen.trained and c not in release.trained:
        raise ValueError(f"{smiles}: the measurement networks trained on it ({', '.join(seen.trained[c])}) and the release networks did "
                         "not; a release set holds its measurement set (decision 66)")
    got = role_of(c, seen, listed_id, release)
    ran = seen if release is None else release
    cations = [] if c in ran.trained else ran.cations.get(c, [])
    if not cations:
        return got
    head = TEXT["unseen_neutral"] if got["role"] == "unseen" else got["text"]        # its parent row is the corpus's, the catalogue lacks it
    return got | {"cation_trained": cations, "text": f"{head}; {TEXT['cation_trained'].format(ids=', '.join(cations))}"}


def covering_key(c: str | None, seen: Seen, release: Seen | None) -> str | None:
    """The key the molecule is looked up under: its own canonical SMILES when an index holds it, else that SMILES without stereo
    labels when an index holds that — a row without stereo marks covers every configuration (an xyz sulfoxide names its
    configuration, the training SMILES leave it open)."""
    if c is None:
        return None
    indexes = [seen.trained, seen.holdout, seen.cations] + ([release.trained, release.cations] if release is not None else [])
    if any(c in index for index in indexes):
        return c
    plain = without_stereo(c)
    return plain if any(plain in index for index in indexes) else c


def stereoisomer_keys(c: str | None, keys) -> list[str]:
    """The keys that are `c` with other stereo labels, both sides specifying stereo (a stereo-free key is `covering_key`'s)."""
    if c is None or (plain := without_stereo(c)) == c:
        return []
    return sorted(k for k in keys if k not in (c, plain) and without_stereo(k) == plain)


def role_of(c: str | None, seen: Seen, listed_id: str | None, release: Seen | None) -> dict:
    """The role of the molecule of canonical SMILES `c` (`covering_key`), with its ids and sentence (`status`, without the cation clause).
    A molecule found under no key of its own but trained on, or held out, as a stereoisomer — both sides naming the stereo — says so."""
    if release is not None and c in release.trained:
        return {"role": "release_trained", "ids": release.trained[c], "text": TEXT["release_trained"]}
    if c in seen.trained and c in seen.holdout:
        h, held = seen.holdout[c]
        ids = seen.trained[c]
        return {"role": "trained_and_held_out", "ids": ids,
                "text": TEXT["trained_and_held_out"].format(ids=", ".join(ids), h=h, held=", ".join(held))}
    if c in seen.trained:
        role, ids = "trained", seen.trained[c]
    elif c in seen.holdout:
        role, ids = seen.holdout[c]
    elif stereo := stereoisomer_keys(c, (trained := (seen if release is None else release).trained)):
        role, ids = "stereoisomer", sorted(i for k in stereo for i in trained[k])
    elif stereo := stereoisomer_keys(c, seen.holdout):
        h = seen.holdout[stereo[0]][0]
        ids = sorted(i for k in stereo for i in seen.holdout[k][1])
        return {"role": "stereoisomer_held_out", "ids": ids, "text": TEXT["stereoisomer_held_out"].format(h=h, ids=", ".join(ids))}
    elif listed_id is not None:
        role, ids = "catalogue", [listed_id]
    else:
        role, ids = "unseen", []
    return {"role": role, "ids": ids, "text": TEXT[role].format(ids=", ".join(ids))}


def truth_beside(corpus_id: str, network_sticks: list[dict]) -> dict | None:
    """The corpus's ωB97X spectrum against the network's: the overlap (with the corpus's own B3LYP APT) and the positions paired by rank;
    None where the corpus holds no ωB97X Hessian. Ranks pair only when both list the same number of bands."""
    d = P.CORPUS / corpus_id
    if not (d / P.TRUTH_HESSIAN).exists():
        return None
    masses = np.asarray(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    truth = series(d / P.TRUTH_HESSIAN, masses, cheap_apt(d))
    t = np.array([s["omega_cm"] for s in truth["sticks"]])
    n = np.sort([s["omega_cm"] for s in network_sticks])
    rms = round(float(np.sqrt(np.mean((n - t) ** 2))), 2) if len(t) == len(n) else None
    heights = truth["kind"] == "positions and heights"
    return {"source": f"corpus/molecules/{corpus_id}/{P.TRUTH_HESSIAN}", "n_bands": len(t), "rms_by_rank_cm": rms,
            "overlap": overlap(network_sticks, truth["sticks"]) if heights else None}
