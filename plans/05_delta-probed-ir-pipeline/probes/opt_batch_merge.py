"""An optimisation batch's finished molecules into the corpus (22 Nov 2026; TASKS 291): the folders that
`probes/labels_batch_ccx53.sh` filled on a server from the jobs of `probes/corpus_opt_jobs.py` — psi4 optimisation at the corpus deck,
then analytic B3LYP and ωB97X labels — fetched whole by `tools/fetch_server_full.sh`, for manifest rows that exist and are pending.
The counterpart of `probes/large_pah_merge.py` (which appended rows for ten molecules new to the manifest) and of
`probes/labels_merge_checked.py` (labels for folders the corpus already holds).

Each source is `<host>=<fetched batch folder>` with the batch's `ids.txt` and `molecules/<id>/`. Checked before anything is written:
- an id is in one source only, has a manifest row, and its job is that row's molecule (id and SMILES);
- the job ran the corpus deck apart from threads and memory (`large_pah_merge.deck_hash`), so the row gets that file's hash;
- the optimised geometry is the SMILES's molecule: the same atoms bonded the same way (bonds found by distance, bond orders left out),
  so an optimisation that rearranged or broke the molecule is refused;
- the folder is ready by the trainer's own test (`large_pah_ready.state`: geometry, both analytic Hessians, the CPHF dipole file,
  result.json 'analytic_only', no imaginary mode at either functional) — a molecule that is not, or whose files cannot be read, is
  named and left out, not merged;
- a folder already in the corpus must be ready there and hold the same geometry (then only its row is brought up to date).
`--write` copies each folder beside corpus/molecules and moves it in whole, then rewrites the manifest (a dated copy kept beside it):
status done, the server's name, the deck hash, the note extended. Folders first: a folder whose row still says pending is seen by the
loader either way, while a row saying done without its folder would be wrong; a second run finishes an interrupted one.

Two guards on `--write`, looked for among this machine's processes, WSL's included:
- another writer of the manifest (`run_corpus.py`, which holds it in memory and rewrites it per molecule, or a merge; corpus.lock):
  refused, always — the rows written here would be lost, and a runner taking such a row removes its folder;
- a reader of corpus/molecules (a chain, a training, an evaluation or a fine-tune: they take every folder, so the pool of whatever
  starts after the merge changes, every size cut of a hashed pool included): refused unless `--beside-training "<why>"` names why
  that is right. Say in the ledger which runs started before and after a merge.

    python probes/opt_batch_merge.py --source anc1=probes/results_m1/anchor_dft_fetch_2026-11/anc1/dft1 [--source …] [--write]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import large_pah_merge as LM  # noqa: E402  deck_hash; its imports put module 05 and src on the path
import large_pah_ready as LR  # noqa: E402

CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus"
NOTE_MARK = "anchor-plan DFT batch of 21 Nov 2026"
NOTE = NOTE_MARK + " on {host}: psi4 optimisation, analytic labels only (TASKS 291)"
MANIFEST_WRITERS = ("run_corpus.py", "merge_shards.py", "cation_fill_manifest.py", "large_pah_merge.py")
CORPUS_READERS = ("chain_runner.py", "rungC_train.py", "rungC_eval_saved.py", "rungC_cc_transfer.py", "proxy_transfer_check.py",
                  "new_anchor_table.py")
STAGING = "opt_batch_merge_staging"
BOHR = 0.529177210903


@dataclass(frozen=True)
class Item:
    """One molecule to merge: its id, the server it ran on, its fetched folder and the deck hash its row gets."""

    mol_id: str
    host: str
    folder: Path
    deck: str


@dataclass(frozen=True)
class Plan:
    """What a merge will do: the folders to copy, the rows to bring up to date, and the molecules left out with their reason."""

    copy: tuple[Item, ...]
    rows: tuple[Item, ...]
    not_ready: dict[str, str]


def batch_ids(folder: Path) -> list[str]:
    return [x.strip() for x in (folder / "ids.txt").read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]


def connectivity(mol) -> str:
    """A canonical string of a molecule's atoms and which are bonded, bond orders and aromaticity left out (hydrogens explicit)."""
    from rdkit import Chem
    rw = Chem.RWMol(mol)
    for atom in rw.GetAtoms():
        atom.SetIsAromatic(False)
        atom.SetFormalCharge(0)
        atom.SetNoImplicit(True)
        atom.SetNumExplicitHs(0)
        atom.SetNumRadicalElectrons(0)
    for bond in rw.GetBonds():
        bond.SetIsAromatic(False)
        bond.SetBondType(Chem.BondType.SINGLE)
    return Chem.MolToSmiles(rw, canonical=True, isomericSmiles=False)


def geometry_connectivity(geometry: dict) -> str:
    """`connectivity` of an optimised geometry (symbols, coords_bohr), its bonds found by distance."""
    from rdkit import Chem
    from rdkit.Chem import rdDetermineBonds
    lines = [f"{s.capitalize()} {x * BOHR:.6f} {y * BOHR:.6f} {z * BOHR:.6f}"       # psi4 writes 'CL', RDKit reads 'Cl'
             for s, (x, y, z) in zip(geometry["symbols"], geometry["coords_bohr"], strict=True)]
    mol = Chem.MolFromXYZBlock(f"{len(lines)}\n\n" + "\n".join(lines))
    rdDetermineBonds.DetermineConnectivity(mol)
    return connectivity(mol)


def smiles_connectivity(smiles: str) -> str:
    from rdkit import Chem
    return connectivity(Chem.AddHs(Chem.MolFromSmiles(smiles)))


def check_molecule(mol_id: str, folder: Path, row: dict, deck_file: Path) -> str:
    """The deck hash of a molecule whose job is the row's molecule at the corpus deck and whose geometry is that molecule; anything
    else is refused by name."""
    if not (folder / "job.json").is_file():
        raise ValueError(f"{mol_id}: no job.json in {folder}")
    job = json.loads((folder / "job.json").read_text(encoding="utf-8"))
    if job["id"] != mol_id or job["source"]["smiles"] != row["smiles"]:
        raise ValueError(f"{mol_id}: its job is {job['id']} {job['source']['smiles']!r}, the manifest row is {row['smiles']!r}")
    try:
        deck = LM.deck_hash(job["deck"], deck_file)
    except ValueError as e:
        raise ValueError(f"{mol_id}: {e}") from e
    if (folder / "geometry.json").exists():
        geometry = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
        if geometry_connectivity(geometry) != smiles_connectivity(row["smiles"]):
            raise ValueError(f"{mol_id}: the optimised geometry is not the molecule {row['smiles']} (other atoms, or bonded otherwise)")
    return deck


def state_of(folder: Path) -> str:
    """`large_pah_ready.state`, with a folder whose files cannot be read (a fetch cut short) reported, not raised."""
    try:
        return LR.state(str(folder))
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as e:
        return f"unreadable ({type(e).__name__}: {e})"


def plan(sources: dict[str, Path], corpus: Path) -> Plan:
    """Every listed molecule checked; refusals raise, molecules that are not ready are named."""
    with (corpus / "manifest.csv").open(newline="", encoding="utf-8") as f:
        rows = {r["id"]: r for r in csv.DictReader(f)}
    listed = [(i, host) for host, folder in sources.items() for i in batch_ids(folder)]
    twice = sorted(i for i, n in Counter(i for i, _ in listed).items() if n > 1)
    if twice:
        raise ValueError(f"listed in more than one source, or twice: {twice}")
    copy, upto, not_ready = [], [], {}
    for mol_id, host in listed:
        folder = sources[host] / "molecules" / mol_id
        if mol_id not in rows:
            raise ValueError(f"{mol_id}: no manifest row")
        row = rows[mol_id]
        deck = check_molecule(mol_id, folder, row, corpus / "decks" / "deck_v1.json")
        state = state_of(folder)
        if state != "ready":
            not_ready[mol_id] = state
            continue
        item = Item(mol_id, host, folder, deck)
        dst = corpus / "molecules" / mol_id
        if dst.exists():
            if state_of(dst) != "ready" or (dst / "geometry.json").read_bytes() != (folder / "geometry.json").read_bytes():
                raise ValueError(f"{mol_id}: {dst} exists and is not this batch's ready folder")
        else:
            copy.append(item)
        if row["status"] not in ("pending", "failed", "done") or (row["status"] == "done" and row["deck"] != deck):
            raise ValueError(f"{mol_id}: its manifest row is {row['status']!r} with deck {row['deck']!r}")
        if row["status"] != "done" or NOTE_MARK not in row["note"]:
            upto.append(item)
    return Plan(tuple(copy), tuple(upto), not_ready)


def copy_folders(items: tuple[Item, ...], corpus: Path) -> None:
    """Each folder copied beside corpus/molecules and moved in whole: a loader never sees half a molecule."""
    staging = corpus / STAGING
    if staging.exists():
        raise FileExistsError(f"{staging} is left from an interrupted merge: look at it and remove it first")
    staging.mkdir()
    for item in items:
        shutil.copytree(item.folder, staging / item.mol_id)
        if state_of(staging / item.mol_id) != "ready":
            raise RuntimeError(f"{item.mol_id}: the copy in {staging} is not ready")
        (staging / item.mol_id).rename(corpus / "molecules" / item.mol_id)
    staging.rmdir()


def update_manifest(items: tuple[Item, ...], manifest: Path) -> Path:
    """The rows of `items` set to done with their server, deck and note, in the manifest's own columns and line ending; the previous
    manifest kept as a dated copy (never written over), whose path is returned."""
    backup = manifest.with_name(f"{manifest.name}.pre_opt_batch_merge_{time.strftime('%Y-%m-%d_%H%M%S')}")
    if backup.exists():
        raise FileExistsError(f"{backup} exists: a merge wrote it this very second; run again")
    shutil.copy2(manifest, backup)
    term = "\r\n" if b"\r\n" in manifest.read_bytes()[:4096] else "\n"
    by_id = {i.mol_id: i for i in items}
    tmp = manifest.with_suffix(".csv.tmp")
    with manifest.open(newline="", encoding="utf-8") as src, tmp.open("w", newline="", encoding="utf-8") as dst:
        reader = csv.DictReader(src)
        w = csv.DictWriter(dst, fieldnames=reader.fieldnames, lineterminator=term)
        w.writeheader()
        for row in reader:
            item = by_id.get(row["id"])
            if item is not None:
                note = NOTE.format(host=item.host)
                row = {**row, "status": "done", "machine": item.host, "deck": item.deck,
                       "note": note if not row["note"] else f"{row['note']}; {note}"}
            w.writerow(row)
    os.replace(tmp, manifest)
    return backup


def command_lines() -> list[str]:
    """The command lines of this machine's other processes: Windows' (or this system's) by psutil, and WSL's where there is one —
    a job started inside WSL shows here only as its shell."""
    import psutil
    lines = [" ".join(p.info["cmdline"] or []) for p in psutil.process_iter(["pid", "cmdline"]) if p.info["pid"] != os.getpid()]
    wsl = shutil.which("wsl.exe")
    if wsl:
        inside = subprocess.run([wsl, "-e", "ps", "-eo", "args"], capture_output=True, text=True, timeout=60, check=False)
        if inside.returncode != 0:
            raise RuntimeError(f"WSL's process list could not be read ({inside.stderr.strip()[:120]}); the guards cannot see its jobs")
        lines += inside.stdout.replace("\x00", "").splitlines()
    return lines


def at_work(marks: tuple[str, ...], lines: list[str]) -> list[str]:
    return [line[:160] for line in lines if any(mark in line for mark in marks)]


def refuse_unsafe_write(corpus: Path, beside_training: str) -> list[str]:
    """Stop when the manifest has another writer, or the corpus a reader without a stated reason; the readers found are returned."""
    if (corpus / "corpus.lock").exists():
        raise SystemExit(f"refused, nothing written: {corpus / 'corpus.lock'} — a corpus runner holds the manifest")
    lines = command_lines()
    writers = at_work(MANIFEST_WRITERS, lines)
    if writers:
        raise SystemExit(f"refused, nothing written: another writer of the manifest runs here: {writers[0]}")
    readers = at_work(CORPUS_READERS, lines)
    if readers and not beside_training:
        raise SystemExit("refused, nothing written: a chain, training or evaluation runs here and whatever it starts next would see "
                         f"another pool — wait for its end or give --beside-training \"<why>\": {readers[0]}")
    return readers


def parse_sources(pairs: list[str]) -> dict[str, Path]:
    sources = {}
    for pair in pairs:
        host, _, folder = pair.partition("=")
        if not host or not folder or host in sources:
            raise SystemExit(f"--source {pair!r}: give <host>=<fetched batch folder>, each host once")
        if not (Path(folder) / "ids.txt").is_file() or not (Path(folder) / "molecules").is_dir():
            raise SystemExit(f"--source {pair!r}: no ids.txt and molecules/ under {folder}")
        sources[host] = Path(folder)
    return sources


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", action="append", required=True, help="<host>=<fetched batch folder>; repeat per server")
    ap.add_argument("--corpus", type=Path, default=CORPUS)
    ap.add_argument("--write", action="store_true", help="copy the folders and bring the rows up to date")
    ap.add_argument("--beside-training", default="", help="with --write: why merging while a chain or training runs here is right")
    a = ap.parse_args(argv)
    if a.beside_training and not a.write:
        raise SystemExit("--beside-training belongs to --write")
    try:
        p = plan(parse_sources(a.source), a.corpus)
    except ValueError as e:
        raise SystemExit(f"refused, nothing written: {e}") from e
    for mol_id, why in sorted(p.not_ready.items()):
        print(f"left out  {mol_id}: {why}")
    print(f"{len(p.copy)} folders to copy, {len(p.rows)} rows to bring up to date, {len(p.not_ready)} molecules left out")
    if not a.write:
        return 0
    readers = refuse_unsafe_write(a.corpus, a.beside_training)
    copy_folders(p.copy, a.corpus)
    print(f"copied {len(p.copy)} folders into {a.corpus / 'molecules'}")
    if p.rows:
        backup = update_manifest(p.rows, a.corpus / "manifest.csv")
        print(f"{len(p.rows)} manifest rows are done; the previous manifest kept as {backup.name}"
              + (f"; merged beside a running reader of the corpus: {a.beside_training}" if readers else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
