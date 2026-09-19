"""Merge the corpus state of several sharded runners back into this directory (2026-09-19).

Each rented machine ran `run_corpus.py --layer L --shard i/K` on its own copy of this directory and wrote its own
manifest.csv, ledger.csv and molecules/<id>/. Fetch each machine's corpus dir to shards/<name>/ (tar over ssh), then:

    python merge_shards.py shards/*/

Rules: a row is taken from a shard when the shard's status is done/failed and ours is pending (or ours is failed and the
shard's is done); molecule folders are copied for rows taken; ledger rows of the shards that are not yet in ours (by
id+start) are appended in start order. The local manifest and ledger are backed up first. Nothing is deleted.
"""
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ["id", "layer", "priority", "name", "smiles", "qm9_label", "n_heavy", "n_atoms", "status", "machine", "deck", "note"]


def read_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f); return list(r), r.fieldnames


def write_csv(p, rows, fields):
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    tmp.replace(p)


def main():
    shards = [Path(a) for a in sys.argv[1:]]
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    man_p, led_p = HERE / "manifest.csv", HERE / "ledger.csv"
    shutil.copy(man_p, HERE / f"manifest.csv.pre_merge_{stamp}"); shutil.copy(led_p, HERE / f"ledger.csv.pre_merge_{stamp}")
    rows, fields = read_csv(man_p); by_id = {r["id"]: r for r in rows}
    led, lfields = read_csv(led_p); seen = {(r["id"], r["start"]) for r in led}
    taken, appended = 0, 0
    for sh in shards:
        srows, _ = read_csv(sh / "manifest.csv")
        for r in srows:
            mine = by_id.get(r["id"])
            if mine is None: continue
            take = (r["status"] in ("done", "failed") and mine["status"] == "pending") or (r["status"] == "done" and mine["status"] == "failed")
            if take:
                src = sh / "molecules" / r["id"]
                if r["status"] == "done" and not (src / "result.json").exists():
                    print(f"  {sh.name}: {r['id']} marked done but no result.json — skipped"); continue
                if src.exists():
                    dst = HERE / "molecules" / r["id"]
                    if dst.exists(): shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                mine.update({k: r[k] for k in ("status", "machine", "deck", "note")}); taken += 1
        if (sh / "ledger.csv").exists():
            sled, _ = read_csv(sh / "ledger.csv")
            for r in sled:
                if (r["id"], r["start"]) not in seen:
                    led.append(r); seen.add((r["id"], r["start"])); appended += 1
    led.sort(key=lambda r: r["start"])
    write_csv(man_p, rows, fields); write_csv(led_p, led, lfields)
    print(f"merged {len(shards)} shard(s): {taken} manifest rows taken, {appended} ledger rows appended")


if __name__ == "__main__":
    main()
