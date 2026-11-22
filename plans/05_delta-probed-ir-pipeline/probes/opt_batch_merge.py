"""An optimisation batch's finished molecules into the corpus (22 Nov 2026; TASKS 291): the folders that
`probes/labels_batch_ccx53.sh` filled on a server from the jobs of `probes/corpus_opt_jobs.py` — psi4 optimisation at the corpus deck,
then analytic B3LYP and ωB97X labels — fetched whole by `tools/fetch_server_full.sh`, for manifest rows that exist and are pending.
The counterpart of `probes/large_pah_merge.py` (which appended rows for ten molecules new to the manifest) and of
`probes/labels_merge_checked.py` (labels for folders the corpus already holds).

Each source is `<host>=<fetched batch folder>` with the batch's `ids.txt` and `molecules/<id>/`. Checked before anything is written:
- an id is in one source only, has a manifest row, and its job is that row's molecule (id and SMILES);
- the job ran the corpus deck apart from threads and memory (`large_pah_merge.deck_hash`), so the row gets that file's hash;
- the optimised geometry holds the SMILES's atoms, element by element;
- the folder is ready by the trainer's own test (`large_pah_ready.state`: geometry, both analytic Hessians, the CPHF dipole file,
  result.json 'analytic_only', no imaginary mode at either functional) — a molecule that is not is named and left out, not merged;
- a folder already in the corpus must be ready there and hold the same geometry (then only its row is brought up to date).
`--write` copies each folder beside corpus/molecules and moves it in whole, then rewrites the manifest (a dated copy kept beside it):
status done, the server's name, the deck hash, the note extended. Folders first: a folder whose row still says pending is seen by the
loader either way, while a row saying done without its folder would be wrong.

The trainer reads every folder of corpus/molecules, so a merge changes the pool of every training that starts after it. `--write`
is refused while a chain or a training runs on this machine, unless `--beside-training "<why>"` names the reason.

    python probes/opt_batch_merge.py --source anc1=probes/results_m1/anchor_dft_fetch_2026-11/anc1/dft1 [--source …] [--write]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import large_pah_merge as LM  # noqa: E402  deck_hash; its imports put module 05 and src on the path
import large_pah_ready as LR  # noqa: E402

CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus"
NOTE = "anchor-plan DFT batch of 21 Nov 2026 on {host}: psi4 optimisation, analytic labels only (TASKS 291)"
TRAINING_MARKS = ("chain_runner.py", "rungC_train.py")
STAGING = "opt_batch_merge_staging"


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


def atoms_of_smiles(smiles: str) -> Counter:
    from rdkit import Chem
    return Counter(a.GetSymbol() for a in Chem.AddHs(Chem.MolFromSmiles(smiles)).GetAtoms())


def check_molecule(mol_id: str, folder: Path, row: dict, deck_file: Path) -> str:
    """The deck hash of a molecule whose job is the row's molecule at the corpus deck and whose geometry holds the SMILES's atoms;
    anything else is refused by name."""
    job = json.loads((folder / "job.json").read_text(encoding="utf-8"))
    if job["id"] != mol_id or job["source"]["smiles"] != row["smiles"]:
        raise ValueError(f"{mol_id}: its job is {job['id']} {job['source']['smiles']!r}, the manifest row is {row['smiles']!r}")
    try:
        deck = LM.deck_hash(job["deck"], deck_file)
    except ValueError as e:
        raise ValueError(f"{mol_id}: {e}") from e
    if (folder / "geometry.json").exists():
        # psi4 writes two-letter elements in capitals ('CL'), RDKit as 'Cl'
        symbols = Counter(s.capitalize() for s in json.loads((folder / "geometry.json").read_text(encoding="utf-8"))["symbols"])
        if symbols != atoms_of_smiles(row["smiles"]):
            raise ValueError(f"{mol_id}: the optimised geometry's atoms {dict(symbols)} are not those of {row['smiles']}")
    return deck


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
        deck = check_molecule(mol_id, folder, rows[mol_id], corpus / "decks" / "deck_v1.json")
        state = LR.state(str(folder))
        if state != "ready":
            not_ready[mol_id] = state
            continue
        item = Item(mol_id, host, folder, deck)
        dst = corpus / "molecules" / mol_id
        if dst.exists():
            if LR.state(str(dst)) != "ready" or (dst / "geometry.json").read_bytes() != (folder / "geometry.json").read_bytes():
                raise ValueError(f"{mol_id}: {dst} exists and is not this batch's ready folder")
        else:
            copy.append(item)
        if (rows[mol_id]["status"], rows[mol_id]["deck"]) != ("done", deck):
            if rows[mol_id]["status"] not in ("pending", "failed"):
                raise ValueError(f"{mol_id}: its manifest row is {rows[mol_id]['status']!r} with another deck")
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
        if LR.state(str(staging / item.mol_id)) != "ready":
            raise RuntimeError(f"{item.mol_id}: the copy in {staging} is not ready")
        (staging / item.mol_id).rename(corpus / "molecules" / item.mol_id)
    staging.rmdir()


def update_manifest(items: tuple[Item, ...], manifest: Path) -> Path:
    """The rows of `items` set to done with their server, deck and note, in the manifest's own columns and line ending; the previous
    manifest kept as a dated copy, whose path is returned."""
    backup = manifest.with_name(f"{manifest.name}.pre_opt_batch_merge_{time.strftime('%Y-%m-%d_%H%M')}")
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


def training_at_work() -> list[str]:
    """Command lines of this machine's processes that are a chain or a training (they read corpus/molecules when a step starts)."""
    import psutil
    found = []
    for p in psutil.process_iter(["cmdline"]):
        line = " ".join(p.info["cmdline"] or [])
        if any(mark in line for mark in TRAINING_MARKS):
            found.append(line[:160])
    return found


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
    running = training_at_work()
    if running and not a.beside_training:
        raise SystemExit("refused, nothing written: a chain or training runs here and would see another pool at its next step — "
                         f"wait for its end or give --beside-training \"<why>\": {running[0]}")
    copy_folders(p.copy, a.corpus)
    print(f"copied {len(p.copy)} folders into {a.corpus / 'molecules'}")
    if p.rows:
        backup = update_manifest(p.rows, a.corpus / "manifest.csv")
        print(f"{len(p.rows)} manifest rows are done; the previous manifest kept as {backup.name}"
              + (f"; merged beside a running training: {a.beside_training}" if running else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
