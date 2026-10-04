"""Step (a) of the candidate generator's batch route (TASKS row 22; `GoalGathering/notes/PreRegistration_2026-10-04_Candidate_Generator_Batch_Route.md`).

Samples the trained generator and writes every sample with its canonical SMILES, the run and request that produced it, and the checkpoint's
SHA-256 and registry status. The gate is a separate step (`m06/gate.py`), so the raw proposals stay on record. The models are `experimental` in the
registry (decision 59), so the registry guard is passed only with `--allow-any-model`, and the record names that use.

    python m06/propose.py out/proposals_2026-10-04 --runs seed0,seed1 --n 10000 --temperature 1.0 --allow-any-model
    python m06/propose.py out/proposals_2026-10-04 --runs cond_seed0 --requests "<r3> <hnone>,<r4+> <hnone>,<r3> <hN>,<r4+> <hN>" --n 2500 --allow-any-model --append
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
PLAN = MOD.parents[1]
RUNS = MOD / "notebook" / "out"
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))   # model_registry; m05 also has model.py and data.py, so m06 goes first
sys.path.insert(0, str(HERE))
import model_registry as MR  # noqa: E402
from data import Vocab  # noqa: E402
from evaluate import canonical  # noqa: E402
from model import SmilesTransformer  # noqa: E402
from train import generate  # noqa: E402

FIELDS = ["run", "request", "temperature", "index", "smiles_raw", "smiles"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_run(run: str, allow_any_model: bool = False, runs_dir: Path = RUNS):
    """A trained run by folder name (`seed0`, `seed1`, `cond_seed0`): the model with its weights, the vocabulary and the run's log; the registry guard
    on the checkpoint (decision 55/59)."""
    import torch
    d = runs_dir / run
    seed = int(run.rsplit("seed", 1)[1])
    log = json.loads((d / f"train_log_seed{seed}.json").read_text(encoding="utf-8"))
    ck = d / f"model_seed{seed}.pt"
    status = MR.require_carried(ck, allow=allow_any_model)
    vocab = Vocab(log["vocab"])
    model = SmilesTransformer(len(vocab.itos), max_len=log["max_len"])
    model.load_state_dict(torch.load(ck, map_location="cpu"))
    model.eval()
    return model, vocab, dict(run=run, seed=seed, conditioning=bool(log["conditioning"]), checkpoint=str(ck.relative_to(MOD)), sha256=sha256(ck),
                              status=status["status"], version=status.get("version", ""), params=model.n_params())


def propose(run: str, n: int, temperature: float, requests: list[str], allow_any_model: bool, runs_dir: Path = RUNS) -> tuple[list[dict], dict]:
    model, vocab, meta = load_run(run, allow_any_model, runs_dir)
    reqs = requests or [""]
    if requests and not meta["conditioning"]:
        raise SystemExit(f"{run} was trained without conditioning; requests need cond_seed*")
    rows = []
    for ri, req in enumerate(reqs):
        prefix = tuple(req.split()) if req else ()
        for p in prefix:
            if p not in vocab.stoi:
                raise SystemExit(f"request token {p!r} is not in {run}'s vocabulary")
        raw = generate(model, vocab, n=n, temperature=temperature, prefix=prefix, seed=meta["seed"] * 10 + ri)
        rows += [dict(run=run, request=req, temperature=temperature, index=i, smiles_raw=s, smiles=canonical(s) or "") for i, s in enumerate(raw)]
    meta.update(n_per_request=n, temperature=temperature, requests=reqs, n_rows=len(rows), n_parsed=sum(1 for r in rows if r["smiles"]))
    return rows, meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_prefix")
    ap.add_argument("--runs", default="seed0,seed1", help="run folders under notebook/out")
    ap.add_argument("--n", type=int, default=10000, help="samples per run, or per request for a conditioned run")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--requests", default="", help="comma list of conditioning prefixes, e.g. '<r3> <hN>,<r4+> <hnone>' (conditioned runs only)")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--allow-any-model", action="store_true", help="decision 55 override: the generator's checkpoints are 'experimental' (name this in the record)")
    ap.add_argument("--append", action="store_true", help="add to an existing proposals file instead of refusing to overwrite it")
    a = ap.parse_args(argv)
    import torch
    torch.set_num_threads(a.threads)
    out_csv, out_json = Path(a.out_prefix + ".csv"), Path(a.out_prefix + ".json")
    if out_csv.exists() and not a.append:
        raise SystemExit(f"{out_csv} exists; pass --append to add runs to it")
    requests = [r.strip() for r in a.requests.split(",") if r.strip()]
    t0 = time.time()
    metas = json.loads(out_json.read_text(encoding="utf-8"))["runs"] if (a.append and out_json.exists()) else []
    new_rows = []
    for run in [r.strip() for r in a.runs.split(",") if r.strip()]:
        rows, meta = propose(run, a.n, a.temperature, requests, a.allow_any_model)
        meta["seconds"] = round(time.time() - t0)
        print(f"{run}: {meta['n_rows']} samples, {meta['n_parsed']} parse ({100 * meta['n_parsed'] / max(meta['n_rows'], 1):.1f} %), "
              f"status {meta['status']} v{meta['version'] or '—'}, sha {meta['sha256'][:12]}, {meta['seconds']} s")
        new_rows += rows
        metas.append(meta)
    mode = "a" if (a.append and out_csv.exists()) else "w"
    with open(out_csv, mode, newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if mode == "w":
            w.writeheader()
        w.writerows(new_rows)
    out_json.write_text(json.dumps(dict(date=time.strftime("%Y-%m-%d %H:%M"), proposals_csv=out_csv.name, runs=metas), indent=1), encoding="utf-8")
    print(f"→ {out_csv} ({sum(m['n_rows'] for m in metas)} rows in {len(metas)} run(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
