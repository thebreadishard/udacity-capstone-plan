"""Lever 5's merge (TASKS 49): the ten large-PAH folders of the size test, fetched from the labels server in three parts, into
corpus/molecules, each with a manifest row. The rows are needed: the trainer's twin check (`m05/holdout_twins.py`) refuses a pool or
hold-out id without a manifest SMILES, so chain 42's arm D would stop on its six layer-D molecules.

Checked before anything is written:
- an id has exactly one fetched folder that `large_pah_ready.state` calls ready;
- its SMILES is read from the optimised geometry (bonds by distance, every carbon aromatic, RDKit finds the Kekulé structure). It must
  have the job's formula and the folder's atom count, its carbon skeleton must hash to the id, and for a test molecule it must be the
  selection's PubChem structure;
- the job's deck is the corpus deck file apart from threads and memory, so the row carries that file's hash as `run_corpus.py` writes it;
- no other manifest row is the same molecule: a twin of a test molecule in the pool would be trained on.
The manifest is written first (a dated copy beside it), the folders after it, each copied outside corpus/molecules and moved in whole.
`large_pah_ready.py`, chain 42's wait condition, passes only once the last folder is in place. A second run skips what is there.

    python probes/large_pah_merge.py            # the checks and the rows, nothing written
    python probes/large_pah_merge.py --write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import rdDetermineBonds

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor"))
import cation_fill_manifest as CF  # noqa: E402
import large_pah_jobs as LJ  # noqa: E402
import large_pah_ready as LR  # noqa: E402
import large_pah_select as LS  # noqa: E402
import pool3_candidates as P3  # noqa: E402
from m05 import holdout_twins as HT  # noqa: E402

RESULTS = PLAN / "probes" / "results_m1"
SOURCES = ("l5b_2026-11-01", "l5b_hbc_2026-11-09", "l5b_d8a_2026-11-10")   # the three fetches of /root/l5b/molecules
CORPUS = P3.M05 / "corpus"
MACHINE = "ubuntu-128gb-hel1-2"                 # the labels CCX53 (tools/hosts.tsv)
RUN_SETTINGS = ("threads", "memory_gb")         # a job's own settings; the manifest's deck hash is the deck file's
BOHR = 0.529177210903                           # Å, CODATA 2018
TEST_LAYER, TRAIN_LAYER = "T", "D"
NOTE = "lever 5 size test (TASKS 49); layer {layer}; PAHdb uid {uid}; analytic labels only"


@dataclass(frozen=True)
class Target:
    """Where the merge reads and writes."""
    sources: tuple[Path, ...]          # folders that hold one fetched folder per molecule id
    corpus: Path                       # manifest.csv, molecules/ and decks/deck_v1.json

    @property
    def manifest(self) -> Path:
        return self.corpus / "manifest.csv"

    @property
    def molecules(self) -> Path:
        return self.corpus / "molecules"

    @property
    def deck(self) -> Path:
        return self.corpus / "decks" / "deck_v1.json"


@dataclass(frozen=True)
class Plan:
    """The rows to append, the folders to copy (id → source), and the ids whose row or folder is in place already."""
    rows: list[dict]
    folders: dict[str, Path]
    rows_written: list[str]
    folders_in_place: list[str]


def default_target() -> Target:
    return Target(tuple(RESULTS / s / "l5b" / "molecules" for s in SOURCES), CORPUS)


def selection_structures() -> dict[str, tuple[str, str]]:
    """The four test molecules by id: (name, canonical SMILES of the selection's PubChem structure)."""
    out = {}
    for name, (_cid, smiles) in LS.TEST.items():
        out[LJ.mol_id(TEST_LAYER, LS.skeleton(Chem.MolFromSmiles(smiles)))] = (name, HT.canonical(smiles))
    return out


def source_folder(mol_id: str, sources: tuple[Path, ...]) -> Path:
    """The one fetched folder of the molecule that is ready; none or several is refused."""
    states = {s / mol_id: LR.state(str(s / mol_id)) for s in sources if (s / mol_id).is_dir()}
    ready = [d for d, state in states.items() if state == "ready"]
    if len(ready) != 1:
        found = "; ".join(f"{d}: {state}" for d, state in states.items()) or "no folder"
        raise ValueError(f"{mol_id}: {len(ready)} ready fetched folders ({found})")
    return ready[0]


def geometry_angstrom(folder: Path) -> tuple[list[str], list[list[float]]]:
    g = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    if g["charge"] != 0 or g["multiplicity"] != 1:
        raise ValueError(f"{folder.name}: charge {g['charge']}, multiplicity {g['multiplicity']} — the size test is neutral closed-shell")
    return g["symbols"], [[x * BOHR for x in atom] for atom in g["coords_bohr"]]


def aromatic_smiles(symbols: list[str], xyz: list[list[float]]) -> str:
    """Canonical SMILES of an all-sp2 hydrocarbon from its geometry (Å). A carbon without three neighbours or a carbon graph without a
    Kekulé structure is refused."""
    block = f"{len(symbols)}\n\n" + "\n".join(f"{s} {x:.6f} {y:.6f} {z:.6f}" for s, (x, y, z) in zip(symbols, xyz, strict=True))
    mol = Chem.MolFromXYZBlock(block)
    rdDetermineBonds.DetermineConnectivity(mol)
    for atom in mol.GetAtoms():
        if atom.GetSymbol() not in ("C", "H"):
            raise ValueError(f"atom {atom.GetIdx()} is {atom.GetSymbol()}: a hydrocarbon is expected")
        if atom.GetSymbol() == "C":
            if atom.GetDegree() != 3:
                raise ValueError(f"carbon {atom.GetIdx()} has {atom.GetDegree()} neighbours: not an all-sp2 hydrocarbon")
            atom.SetIsAromatic(True)
    for bond in mol.GetBonds():
        if bond.GetBeginAtom().GetSymbol() == "C" and bond.GetEndAtom().GetSymbol() == "C":
            bond.SetBondType(Chem.BondType.AROMATIC)
            bond.SetIsAromatic(True)
    try:
        Chem.SanitizeMol(mol)
    except Chem.rdchem.MolSanitizeException as e:
        raise ValueError(f"no Kekulé structure for the carbon graph: {e}") from e
    return HT.canonical(Chem.MolToSmiles(Chem.RemoveHs(mol)))


def deck_hash(job_deck: dict, deck_file: Path) -> str:
    """The deck file's hash, as `run_corpus.py` writes it into the manifest, after checking that the job ran that deck."""
    on_file = json.loads(deck_file.read_text(encoding="utf-8"))
    differs = sorted(k for k in {*on_file, *job_deck} - set(RUN_SETTINGS) if on_file.get(k) != job_deck.get(k))
    if differs:
        raise ValueError(f"the job's deck differs from {deck_file.name} in {', '.join(differs)}")
    return hashlib.sha256(deck_file.read_bytes()).hexdigest()[:12]


def manifest_row(mol_id: str, folder: Path, deck_file: Path, expected: dict[str, tuple[str, str]]) -> dict:
    """A molecule's manifest row after its checks; any failure raises."""
    layer = mol_id.split("_")[0]
    if layer not in (TEST_LAYER, TRAIN_LAYER):
        raise ValueError(f"{mol_id}: layer {layer} is not the size test's")
    job = json.loads((folder / "job.json").read_text(encoding="utf-8"))
    source = job["source"]
    symbols, xyz = geometry_angstrom(folder)
    smiles = aromatic_smiles(symbols, xyz)
    if LJ.mol_id(layer, LS.skeleton_from_xyz(symbols, xyz)) != mol_id or job["id"] != mol_id or job["layer"] != layer:
        raise ValueError(f"{mol_id}: the optimised geometry's carbon skeleton or the job file is another molecule's")
    n_heavy, n_atoms = P3.atom_counts(smiles)
    if n_atoms != len(symbols) or P3.formula(smiles) != source["formula"]:
        raise ValueError(f"{mol_id}: {smiles} is {P3.formula(smiles)} with {n_atoms} atoms, the job says {source['formula']} and the "
                         f"geometry has {len(symbols)}")
    name = f"PAHdb {source['pahdb_uid']} {source['formula']}"
    if layer == TEST_LAYER:
        if mol_id not in expected or expected[mol_id][1] != smiles:
            raise ValueError(f"{mol_id}: {smiles} is not the selection's structure for this id")
        name = expected[mol_id][0]
    row = P3.manifest_row({"id": mol_id, "layer": layer, "name": name, "smiles": smiles, "n_heavy": n_heavy, "n_atoms": n_atoms,
                           "note": NOTE.format(layer=layer, uid=source["pahdb_uid"])})
    return dict(row, status="done", machine=MACHINE, deck=deck_hash(job["deck"], deck_file))


def refuse_twins(rows: list[dict], molecules: Path) -> None:
    """No manifest row outside the merge is one of its molecules, and the trainer's twin check accepts the merged ids."""
    ours = {r["id"] for r in rows}
    keys = HT.manifest_keys(molecules)
    new = {r["id"]: (HT.canonical(r["smiles"]), 0) for r in rows}
    same = sorted(i for i, key in keys.items() if i not in ours and key in set(new.values()))
    if same or len(set(new.values())) != len(new):
        raise ValueError(f"the merge's molecules are not all new and distinct; manifest rows with the same molecule: {', '.join(same) or 'none'}")
    held = sorted(i for i in ours if i.startswith(TEST_LAYER + "_"))
    found = HT.twins(sorted(ours - set(held)), held, {**keys, **new})
    if found:
        raise ValueError(f"the twin check finds {', '.join(found)}")


def plan(ids: list[str], target: Target, expected: dict[str, tuple[str, str]]) -> Plan:
    """Every id checked; what is still to write apart from what is in place."""
    manifest = P3.manifest_rows(target.manifest)
    by_id = {r["id"]: r for r in manifest}
    all_rows, rows, folders, rows_written, folders_in_place = [], [], {}, [], []
    for mol_id in ids:
        folder = source_folder(mol_id, target.sources)
        row = manifest_row(mol_id, folder, target.deck, expected)
        all_rows.append(row)
        if mol_id in by_id:
            if {k: str(v) for k, v in row.items()} != by_id[mol_id]:
                raise ValueError(f"{mol_id}: in the manifest with other values")
            rows_written.append(mol_id)
        else:
            rows.append(row)
        dst = target.molecules / mol_id
        if dst.exists():
            if LR.state(str(dst)) != "ready":
                raise ValueError(f"{mol_id}: {dst} exists and is not ready ({LR.state(str(dst))})")
            folders_in_place.append(mol_id)
        else:
            folders[mol_id] = folder
    refuse_twins(all_rows, target.molecules)
    return Plan(rows, folders, rows_written, folders_in_place)


def copy_folders(folders: dict[str, Path], target: Target) -> None:
    """Each folder copied beside corpus/molecules and moved in whole: a loader never sees half a molecule."""
    staging = target.corpus / "large_pah_merge_staging"
    if staging.exists():
        raise FileExistsError(f"{staging} is left from an interrupted merge: look at it and remove it first")
    staging.mkdir()
    for mol_id, src in folders.items():
        shutil.copytree(src, staging / mol_id)
        if LR.state(str(staging / mol_id)) != "ready":
            raise RuntimeError(f"{mol_id}: the copy in {staging} is not ready")
        (staging / mol_id).rename(target.molecules / mol_id)
    staging.rmdir()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="append the rows and copy the folders")
    a = ap.parse_args(argv)
    target = default_target()
    p = plan(LR.ids(), target, selection_structures())
    for r in p.rows:
        print(f"row  {r['id']}  {r['layer']}  {r['n_atoms']:>2} atoms  {r['name']:<28s} {r['smiles']}")
    print(f"{len(p.rows)} rows to append ({len(p.rows_written)} written already), {len(p.folders)} folders to copy "
          f"({len(p.folders_in_place)} in place already); machine {MACHINE}")
    if not a.write:
        return 0
    if p.rows:
        backup = CF.write(p.rows, target.manifest, label="large_pah_merge")
        print(f"appended {len(p.rows)} rows to {target.manifest}; the previous manifest kept as {backup.name}")
    copy_folders(p.folders, target)
    print(f"copied {len(p.folders)} folders into {target.molecules}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
