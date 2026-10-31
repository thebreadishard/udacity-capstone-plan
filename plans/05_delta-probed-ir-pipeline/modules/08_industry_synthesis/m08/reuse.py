"""The corpus's B3LYP Hessian and APT reused for a molecule the corpus already computed (TASKS 150): steps 2–3 of the pipeline are its cost
(candidate06: 3.6 of 3.7 h), and about 400 corpus folders hold both as the pipeline would compute them (`probes/pipeline_reuse_survey.py`).

A folder is reused only when every one of these holds, else the pipeline computes and its record says why:
- its manifest SMILES is the request's molecule (the same RDKit canonical form); of several such folders the first by id that passes;
- its optimisation ran deck v1's numerics (the deck's text was corrected on 21 Sep 2026 without a numeric change, so the hash is not the test);
- its analytic Hessian is neutral and closed shell on the pipeline's grid, with no imaginary mode;
- its APT is the refined response route, passed, its CPHF residual within `apt.CPHF_BOUND` and its sum rule within `apt.SUM_RULE_LIMIT` —
  the checks a computed APT meets today (the APTs of early October predate the residual check and are not reused);
- its atoms are in its own SMILES's AddHs order with that SMILES's bonds, and its optimisation started where the pipeline's does: the same
  optimiser options and, after the best rigid fit, the same start geometry (job.json) — then psi4 reaches the same minimum.

The network's answer depends on the atom order (TASKS 149), so geometry, Hessian and APT are written in the order the pipeline's own start
geometry has: RDKit's AddHs order of the canonical SMILES. That order is derived exactly — the heavy atoms in the order RDKit writes the
folder's SMILES canonically, each hydrogen after its heavy atom — not fitted: a near-symmetric start fits a mirrored order as well as the
true one, and v1.3 moves bands by 0.02 cm⁻¹ between such orders (phenanthrene, 31 Oct 2026). The frame stays the corpus's: the network's
spectrum does not depend on it (`probes/pipeline_reuse_check.py`).
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np

BOHR_ANGSTROM = 0.529177210903
GEOMETRY, HESSIAN, APT, CHECK, RESULT, JOB = ("geometry.json", "hessian_b3lyp_analytic.npz", "dipole_b3lyp_cphf.npz",
                                              "analytic_check.json", "result.json", "job.json")
SOURCE_FILES = (GEOMETRY, HESSIAN, APT, CHECK, RESULT, JOB)
DECK_NUMERICS = ("deck", "basis", "low_functional", "dft_radial_points", "dft_spherical_points", "scf_type", "e_convergence",
                 "d_convergence", "reference", "charge", "multiplicity")
APT_ROUTE = "hessian_response_refined"     # analytic_hessians.py since 13 Oct 2026: the response with its residual checked and refined
SAME_START_ANGSTROM = 0.01                 # two MMFF-converged starts of one conformer, after the best rigid fit (survey record)


@dataclass(frozen=True)
class Start:
    """The pipeline's own start of the optimisation: geometry in the canonical AddHs order (Å) and optimiser options."""

    xyz_angstrom: np.ndarray
    opt_options: dict | None


@dataclass(frozen=True)
class Settings:
    """What a reused folder must match: the pipeline's deck file and its analytic grid, and the APT bounds of `corpus/apt.py`."""

    deck: Path
    grid: tuple[int, int]
    cphf_bound: float
    sum_rule_limit: float


@dataclass(frozen=True)
class Found:
    """The corpus folders whose SMILES is the request's molecule, each with its manifest SMILES (sorted by id), or none with the reason."""

    folders: tuple[tuple[Path, str], ...]
    reasons: tuple[str, ...]


def corpus_folders(canonical: str, corpus: Path) -> Found:
    """The done folders of the corpus manifest whose SMILES has the request's canonical form — a molecule can sit in two layers, and a
    cation row (P3c) carries its neutral parent's SMILES; the Hessian's charge tells them apart."""
    from rdkit import Chem

    manifest = corpus / "manifest.csv"
    if not manifest.is_file():
        return Found((), (f"no corpus manifest at {manifest}",))
    with manifest.open(encoding="utf-8", newline="") as fh:
        hits = sorted((r["id"], r["smiles"]) for r in csv.DictReader(fh)
                      if ("status" not in r or r["status"] == "done") and (m := Chem.MolFromSmiles(r["smiles"])) is not None
                      and Chem.MolToSmiles(m) == canonical)
    if not hits:
        return Found((), ("the corpus has no folder of this molecule",))
    return Found(tuple((corpus / "molecules" / i, s) for i, s in hits), ())


def _numeric_deck(deck: dict) -> dict:
    return {k: deck.get(k) for k in DECK_NUMERICS}


def settings_refusals(folder: Path, settings: Settings) -> list[str]:
    """Every reason the folder's files are not what the pipeline would compute; empty when they are."""
    missing = [f for f in SOURCE_FILES if not (folder / f).is_file()]
    if missing:
        return [f"{folder.name} lacks {', '.join(missing)}"]
    reasons = []
    res = json.loads((folder / RESULT).read_text(encoding="utf-8"))
    want = _numeric_deck(json.loads(settings.deck.read_text(encoding="utf-8")))
    if res.get("status") != "done" or _numeric_deck(res.get("deck", {})) != want:
        reasons.append(f"{folder.name}: the optimisation is not deck {want['deck']}'s numerics or not done")
    if res.get("n_imaginary_b3lyp") != 0:
        reasons.append(f"{folder.name}: {res.get('n_imaginary_b3lyp')} imaginary B3LYP mode(s) recorded")
    with np.load(folder / HESSIAN) as z:
        if not {"charge", "spin", "grid", "H_projected"} <= set(z.files):
            reasons.append(f"{folder.name}: the Hessian file predates the charge, spin and grid fields")
        elif (int(z["charge"]), int(z["spin"])) != (0, 0) or tuple(z["grid"].tolist()) != settings.grid:
            reasons.append(f"{folder.name}: the Hessian is charge {int(z['charge'])}, 2S {int(z['spin'])} on grid {tuple(z['grid'].tolist())}, "
                           f"not neutral closed shell on {settings.grid}")
    reasons += apt_refusals(folder, settings)
    return reasons


def apt_refusals(folder: Path, settings: Settings) -> list[str]:
    """The APT checks a computed APT meets today."""
    with np.load(folder / APT) as z:
        route = str(z["route"])
        if route != APT_ROUTE or "cphf_residual_after" not in z.files:
            return [f"{folder.name}: the APT's route is '{route}', computed before the residual check ({APT_ROUTE} is reused)"]
        reasons = []
        if not bool(z["passed"]):
            reasons.append(f"{folder.name}: the APT failed its checks")
        if float(z["cphf_residual_after"]) > settings.cphf_bound:
            reasons.append(f"{folder.name}: CPHF residual {float(z['cphf_residual_after']):.1e} > {settings.cphf_bound:g}")
        if float(z["sum_rule_max"]) > settings.sum_rule_limit:
            reasons.append(f"{folder.name}: APT sum rule {float(z['sum_rule_max']):.1e} > {settings.sum_rule_limit:g}")
        if (str(z["xc"]), str(z["basis"]).lower(), tuple(z["grid"].tolist())) != ("b3lyp", "6-31g*", settings.grid):
            reasons.append(f"{folder.name}: the APT is not B3LYP/6-31G* on {settings.grid}")
    return reasons


def _kabsch_rmsd(a: np.ndarray, b: np.ndarray) -> float:
    """RMSD of b onto a after the best proper rotation and translation."""
    a, b = a - a.mean(0), b - b.mean(0)
    u, _, vt = np.linalg.svd(b.T @ a)
    d = np.sign(np.linalg.det(u @ vt))
    r = u @ np.diag([1.0, 1.0, d]) @ vt
    return float(np.sqrt(np.mean(np.sum((b @ r - a) ** 2, axis=1))))


def _geometry_bonds(symbols: list[str], coords_bohr: np.ndarray) -> set[frozenset[int]]:
    from rdkit import Chem
    from rdkit.Chem import rdDetermineBonds

    xyz = f"{len(symbols)}\n\n" + "\n".join(f"{s.capitalize()} {x:.8f} {y:.8f} {z:.8f}"     # psi4's geometry files write 'CL'
                                            for s, (x, y, z) in zip(symbols, coords_bohr * BOHR_ANGSTROM, strict=True))
    geo = Chem.MolFromXYZBlock(xyz)
    rdDetermineBonds.DetermineConnectivity(geo)
    return {frozenset((b.GetBeginAtomIdx(), b.GetEndAtomIdx())) for b in geo.GetBonds()}


def _written(smiles: str):
    """(the parsed molecule, its heavy atoms in the order RDKit's canonical SMILES writes them)."""
    from rdkit import Chem

    m = Chem.MolFromSmiles(smiles)
    Chem.MolToSmiles(m)
    return m, [int(i) for i in m.GetProp("_smilesAtomOutputOrder").strip("[],").split(",")]


def atom_order(source_smiles: str, canonical: str, symbols: list[str], coords_bohr: np.ndarray) -> np.ndarray:
    """order[i] = the folder's atom that is atom i of the canonical SMILES's AddHs order, for a folder whose atoms are in its own SMILES's
    AddHs order: two heavy atoms correspond when RDKit's canonical SMILES writes them at the same place (one SMILES parsed as the folder's,
    one as the canonical; equal strings give the identity), each hydrogen in turn after its heavy atom. Raises ValueError when the folder's
    atoms or its geometry's bonds are not its SMILES's."""
    from rdkit import Chem

    heavy, written_src = _written(source_smiles)
    can_heavy, written_can = _written(canonical)
    if Chem.MolToSmiles(heavy) != canonical:
        raise ValueError(f"its SMILES {source_smiles} is not {canonical}")
    written = [0] * len(written_src)              # canonical atom → the folder's heavy atom at the same place of the canonical string
    for place, atom in enumerate(written_can):
        written[atom] = written_src[place]
    src = Chem.AddHs(heavy)
    if [a.GetSymbol().upper() for a in src.GetAtoms()] != [s.upper() for s in symbols]:
        raise ValueError("its atoms are not in its SMILES's AddHs order: the canonical order cannot be derived exactly")
    if _geometry_bonds(symbols, coords_bohr) != {frozenset((b.GetBeginAtomIdx(), b.GetEndAtomIdx())) for b in src.GetBonds()}:
        raise ValueError("its geometry's bonds are not its SMILES's")
    hydrogens = {i: [n.GetIdx() for n in src.GetAtomWithIdx(i).GetNeighbors() if n.GetAtomicNum() == 1] for i in written}
    can = Chem.AddHs(can_heavy)
    order = list(written)
    for k in range(len(written), can.GetNumAtoms()):           # AddHs appends the hydrogens after the heavy atoms
        order.append(hydrogens[written[can.GetAtomWithIdx(k).GetNeighbors()[0].GetIdx()]].pop(0))
    if sorted(order) != list(range(src.GetNumAtoms())):
        raise ValueError("the derived order is not a permutation of the folder's atoms")
    return np.asarray(order, int)


def _cartesian(order: np.ndarray) -> np.ndarray:
    return (3 * order[:, None] + np.arange(3)[None, :]).ravel()


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _save_npz(path: Path, arrays: dict) -> None:
    tmp = path.with_name(path.name + ".tmp.npz")
    np.savez(tmp, **arrays)
    os.replace(tmp, path)


def _save_json(path: Path, rec: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def write_reused(src: Path, dst: Path, order: np.ndarray) -> None:
    """The source folder's geometry, Hessian and APT in `order` (geometry atoms, Hessian rows and columns, APT columns), its analytic check and
    its optimisation's result as they are (frequencies and energies do not depend on the order)."""
    g = json.loads((src / GEOMETRY).read_text(encoding="utf-8"))
    pick = order.tolist()
    _save_json(dst / GEOMETRY, g | {k: [g[k][i] for i in pick] for k in ("symbols", "coords_bohr", "masses_amu")}
               | {"charge": 0, "multiplicity": 1})
    c = _cartesian(order)
    with np.load(src / HESSIAN) as z:
        _save_npz(dst / HESSIAN, {k: (z[k][np.ix_(c, c)] if k in ("H_raw", "H_projected") else z[k]) for k in z.files})
    with np.load(src / APT) as z:
        _save_npz(dst / APT, {k: (z[k][:, c] if k == "apt" else z[k]) for k in z.files})
    for name in (CHECK, RESULT):
        _save_json(dst / name, json.loads((src / name).read_text(encoding="utf-8")))


def same_start(src: Path, source_smiles: str, canonical: str, start: Start) -> dict:
    """Whether the folder's optimisation started where the pipeline's would: {order, start_rmsd_angstrom}, with `why` when it did not."""
    job = json.loads((src / JOB).read_text(encoding="utf-8"))
    if job.get("opt_options") != start.opt_options:
        return {"why": [f"{src.name}: optimised with options {job.get('opt_options')}, the pipeline uses {start.opt_options}"]}
    g = json.loads((src / GEOMETRY).read_text(encoding="utf-8"))
    try:
        order = atom_order(source_smiles, canonical, g["symbols"], np.asarray(g["coords_bohr"], float))
    except ValueError as e:
        return {"why": [f"{src.name}: {e}"]}
    folder_start = np.asarray([row[1:] for row in job["xyz_angstrom"]], float)
    rmsd = _kabsch_rmsd(start.xyz_angstrom, folder_start[order])
    rec = {"order": order.tolist(), "start_rmsd_angstrom": round(rmsd, 6)}
    if rmsd > SAME_START_ANGSTROM:
        rec["why"] = [f"{src.name}: its start geometry lies {rmsd:.3f} Å from the pipeline's (> {SAME_START_ANGSTROM}): it may reach "
                      "another minimum"]
    return rec


def assess(canonical: str, start: Start, corpus: Path, settings: Settings) -> dict:
    """Whether the corpus holds this molecule as the pipeline would compute it, nothing written: {reused: True, source, order,
    start_rmsd_angstrom} from the first folder (by id) that passes every check, or {reused: False, why: [each folder's reasons]}."""
    found = corpus_folders(canonical, corpus)
    if not found.folders:
        return {"reused": False, "why": list(found.reasons)}
    why: list[str] = []
    for src, smiles in found.folders:
        refused = settings_refusals(src, settings)
        rec = {} if refused else same_start(src, smiles, canonical, start)
        refused += rec.pop("why", [])
        if not refused:
            return {"reused": True, "source": str(src)} | rec
        why += refused
    return {"reused": False, "why": why}


def reuse(canonical: str, start: Start, dst: Path, corpus: Path, settings: Settings) -> dict:
    """Steps 2–3 from the corpus when `assess` allows it: the files written into `dst` and the record with each source file's sha256;
    otherwise `assess`'s refusal and nothing written."""
    rec = assess(canonical, start, corpus, settings)
    if not rec["reused"]:
        return rec
    src = Path(rec["source"])
    write_reused(src, dst, np.asarray(rec["order"], int))
    return rec | {"sha256": {f: _sha256(src / f) for f in SOURCE_FILES}}
