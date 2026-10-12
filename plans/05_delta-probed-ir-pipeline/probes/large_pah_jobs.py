"""Lever 5 (TASKS 49, 12 Oct 2026): psi4_worker jobs for the selected large PAHs (`probes/large_pah_select.py` → selection.json). Each job is the
corpus deck's B3LYP/6-31G* optimisation from PAHdb's B3LYP/4-31G geometry, without the FD Hessians ("hessians": false). The folder's labels
then come from `corpus/analytic_hessians.py`. Training molecules get layer D and test molecules layer T, which `E6.splits` never pools. The
id is the layer and the sha1 of the carbon skeleton (first 10 hex digits). The test ids also go to an id file for
`rungC_eval_saved --eval-ids-file`.

    python probes/large_pah_jobs.py <out_root> [--selection …/selection.json] [--threads 8] [--memory-gb 24]
        → <out_root>/<id>/job.json, <out_root>/test_ids.txt, <out_root>/train_ids.txt
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.dirname(HERE)
SELECTION = os.path.join(HERE, "results_m1", "large_labels_price_2026-10-12", "selection.json")
DECK = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "decks", "deck_v1.json")


def mol_id(layer: str, skeleton: str) -> str:
    return f"{layer}_{hashlib.sha1(skeleton.encode()).hexdigest()[:10]}"


def job(sp: dict, layer: str, out_root: str, deck: dict) -> dict:
    """One psi4_worker job: optimise at the deck's low functional, no Hessians; the PAHdb uid and name kept for the record."""
    i = mol_id(layer, sp["skeleton"])
    return {"id": i, "layer": layer, "xyz_angstrom": [[s, *xyz] for s, xyz in zip(sp["symbols"], sp["xyz"], strict=True)], "deck": deck,
            "out_dir": os.path.join(out_root, i), "optimise": True, "grid_check": False, "hessians": False,
            "source": {"pahdb_uid": sp["uid"], "formula": sp["formula"], "name": sp.get("name", ""), "skeleton": sp["skeleton"]}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_root")
    ap.add_argument("--selection", default=SELECTION)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--memory-gb", type=int, default=24)
    a = ap.parse_args()
    sel = json.load(open(a.selection, encoding="utf-8"))
    deck = dict(json.load(open(DECK, encoding="utf-8")), threads=a.threads, memory_gb=a.memory_gb)
    ids = {"T": [], "D": []}
    for layer, group in (("T", sel["test"]), ("D", sel["train"])):
        for key, sp in group.items():
            j = job(dict(sp, name=key if layer == "T" else ""), layer, a.out_root, deck)
            os.makedirs(j["out_dir"], exist_ok=True)
            json.dump(j, open(os.path.join(j["out_dir"], "job.json"), "w"), indent=1)
            ids[layer].append(j["id"])
            print(f"{j['id']}  {sp['formula']:8s} PAHdb {sp['uid']:5d}  {key}")
    for layer, name in (("T", "test_ids.txt"), ("D", "train_ids.txt")):
        with open(os.path.join(a.out_root, name), "w") as fh:
            fh.write(f"# lever 5 (TASKS 49): layer {layer}, from {os.path.basename(a.selection)}\n" + "".join(i + "\n" for i in ids[layer]))


if __name__ == "__main__":
    main()
