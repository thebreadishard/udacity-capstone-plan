"""Rung C, variant C2 — pretrain the equivariant Δ-Hessian body on Hessian QM9 (pre-registration
`PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md`: "C2 pretrained on Hessian QM9 (41,645 ωB97x/6-31G* Hessians, `data/hessian_qm9`)
to predict the *full* Hessian from geometry, then the output head re-initialised and the whole network fine-tuned on ΔH"). Built 27 September 2026
(evening) as stage 3 of the fair-chance search registered at 20:0x.

What it does: reads the vacuum split's Arrow shards (positions Å, Hessian eV/Å², atomic numbers — Williams et al. 2025, Table 1, read 12 September),
converts to atomic units (bohr, hartree/bohr²), feeds the model geometry only (the H_low channel is zero: "from geometry"), scales its output per entry
class (own block / bonded / non-bonded, the training set's RMS per class, estimated on the first molecules), and minimises the mass-weighted MSE on
the full Hessian. Translations and rotations are *not* projected out of the QM9 Hessians (they are numerical, unprojected — PROVENANCE, 12 Sep);
the model's own sum rule leaves that part as an irreducible floor of the loss, which is recorded, not hidden. Checkpoint: the body's state dict,
the class scales, the shard hashes, the molecule count and the command line — `rungC_train.py --pretrained <file>` loads the body, re-initialises
the head and fine-tunes on ΔH.

    python m05/rungC_pretrain.py out/rungC_pretrained_<date> [--epochs 2] [--max-molecules N] [--val-fraction 0.02] [--threads 8] [--lr 1e-3]
    python m05/rungC_pretrain.py out/_smoke_pretrain --smoke        # 40 molecules, 1 epoch: mechanics only, never a result

Cost: measured per molecule and printed; the registration's estimate is 2–4 CPU-hours for one pass over the 41,645 molecules."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rungC_equivariant import AMU2AU, BOHR2ANG, LOSS_SCALE, DeltaHessianModel  # noqa: E402
from rungC_train import Scaled, entry_classes, load_pretrained_body  # noqa: E402, F401

HARTREE_EV = 27.211386245988
EV_PER_ANG2_TO_AU = BOHR2ANG**2 / HARTREE_EV          # (eV/Å²) × (Å/bohr)² / (eV/hartree) = hartree/bohr²
MASS_AMU = {1: 1.00782503, 6: 12.0, 7: 14.00307401, 8: 15.99491462, 9: 18.99840316}
QM9_DIR = HERE.parent / "data" / "hessian_qm9" / "hessian_qm9_DatasetDict" / "vacuum"


def record_to_molecule(row: dict) -> dict:
    """One Arrow row (positions Å, atomic_numbers, hessian [n,3,n,3] eV/Å²) → the loader's molecule dict in atomic units, with H_low = 0."""
    Z = np.asarray(row["atomic_numbers"], dtype=int)
    n = len(Z)
    pos = np.asarray(row["positions"], dtype=float) / BOHR2ANG
    H = np.asarray(row["hessian"], dtype=float).reshape(3 * n, 3 * n) * EV_PER_ANG2_TO_AU
    H = 0.5 * (H + H.T)
    return dict(id=str(row["label"]), Z=Z, pos=pos, masses=np.array([MASS_AMU[int(z)] for z in Z]), H_low=np.zeros_like(H), dH_true=H)


def molecule_to_tensors(m: dict) -> dict:
    """The tensors the training step needs (a subset of `rungC_equivariant.to_torch`, plus the entry classes)."""
    t = {"id": m["id"], "Z": torch.as_tensor(m["Z"], dtype=torch.long)}
    for k in ("pos", "H_low", "dH_true"):
        t[k] = torch.as_tensor(np.asarray(m[k]), dtype=torch.float32)
    mm = np.repeat(m["masses"] * AMU2AU, 3)
    t["mw"] = torch.as_tensor(1.0 / np.sqrt(np.outer(mm, mm)), dtype=torch.float32)
    t["cls"] = entry_classes(m)
    return t


def iter_qm9(shards: list[Path], max_molecules: int | None = None, batch_rows: int = 256):
    """Yield molecule dicts shard by shard without loading a whole shard's Python objects at once."""
    import pyarrow as pa
    import pyarrow.ipc as ipc

    count = 0
    for shard in shards:
        table = ipc.open_stream(pa.memory_map(str(shard))).read_all()
        for start in range(0, table.num_rows, batch_rows):
            for row in table.slice(start, batch_rows).to_pylist():
                yield record_to_molecule(row)
                count += 1
                if max_molecules is not None and count >= max_molecules:
                    return


def class_scales(tensors: list[dict]) -> list[float]:
    """RMS of the target per entry class over the given molecules (the pair model's per-class standardisation, for a Hessian)."""
    sq, cnt = np.zeros(3), np.zeros(3)
    for t in tensors:
        c = t["cls"].repeat_interleave(3, 0).repeat_interleave(3, 1).numpy()
        d2 = (t["dH_true"] ** 2).numpy()
        for k in range(3):
            sq[k] += d2[c == k].sum()
            cnt[k] += (c == k).sum()
    return [float(x) for x in np.sqrt(sq / np.maximum(cnt, 1))]


def mw_loss(model: Scaled, t: dict) -> torch.Tensor:
    pred = model(t["Z"], t["pos"], t["H_low"], t)
    return ((pred - t["dH_true"]) * t["mw"] * LOSS_SCALE).pow(2).mean()


def sha16(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()[:16]


def save_checkpoint(path: Path, model: Scaled, meta: dict) -> None:
    torch.save({"body_state": model.model.state_dict(), "class_scale": model.class_scale, "scale": model.scale, "meta": meta}, path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_prefix")
    ap.add_argument("--qm9-dir", default=str(QM9_DIR))
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--max-molecules", type=int, default=None)
    ap.add_argument("--val-fraction", type=float, default=0.02, help="every k-th molecule (k = 1/fraction) is held out for a validation loss")
    ap.add_argument("--scale-sample", type=int, default=2000, help="molecules used to estimate the per-class output scales")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--checkpoint-every", type=int, default=5000)
    ap.add_argument("--smoke", action="store_true", help="40 molecules, 1 epoch, 2 threads: mechanics only, never a result")
    a = ap.parse_args(argv)
    if a.smoke:
        a.max_molecules, a.epochs, a.threads, a.scale_sample, a.checkpoint_every = 40, 1, 2, 20, 20
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    log = lambda s: print(s, flush=True)  # noqa: E731

    shards = sorted(Path(a.qm9_dir).glob("data-*.arrow"))
    if not shards:
        log(f"no Arrow shards under {a.qm9_dir}")
        return 1
    t_start = time.time()
    hashes = {s.name: sha16(s) for s in shards}
    log(f"{len(shards)} shards ({', '.join(f'{k} {v}' for k, v in hashes.items())}); epochs {a.epochs}; threads {a.threads}" + (" — SMOKE" if a.smoke else ""))

    # pass 0: the per-class output scale from the first molecules
    sample = [molecule_to_tensors(m) for m in iter_qm9(shards, a.scale_sample)]
    scales = class_scales(sample)
    log(f"class scales (own block, bonded, non-bonded) from {len(sample)} molecules: {scales}")
    model = Scaled(DeltaHessianModel(), 1.0, scales)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    every = int(round(1.0 / a.val_fraction)) if a.val_fraction > 0 else 0
    meta = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), command=" ".join(sys.argv), shards=hashes, epochs=a.epochs, lr=a.lr,
                class_scale=scales, val_every=every, smoke=a.smoke, history=[])
    ck_path = Path(a.out_prefix + ".pt")
    n_seen = 0
    for ep in range(a.epochs):
        tot, n_tr, val_tot, n_val, t0 = 0.0, 0, 0.0, 0, time.time()
        for k, m in enumerate(iter_qm9(shards, a.max_molecules)):
            t = molecule_to_tensors(m)
            if every and k % every == 0:
                model.eval()
                with torch.no_grad():
                    val_tot += float(mw_loss(model, t))
                n_val += 1
                continue
            model.train()
            opt.zero_grad()
            loss = mw_loss(model, t)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot += float(loss.detach())
            n_tr += 1
            n_seen += 1
            if n_tr % 500 == 0:
                log(f"  epoch {ep + 1} molecule {n_tr}: train loss {tot / n_tr:.4g} ({(time.time() - t0) / n_tr:.2f} s per molecule)")
            if a.checkpoint_every and n_seen % a.checkpoint_every == 0:
                meta["molecules_seen"] = n_seen
                save_checkpoint(ck_path, model, meta)
        rec = dict(epoch=ep + 1, train_loss=tot / max(n_tr, 1), val_loss=val_tot / max(n_val, 1), n_train=n_tr, n_val=n_val,
                   seconds=round(time.time() - t0, 1))
        meta["history"].append(rec)
        meta["molecules_seen"] = n_seen
        save_checkpoint(ck_path, model, meta)
        log(f"epoch {ep + 1}/{a.epochs}: train {rec['train_loss']:.4g} val {rec['val_loss']:.4g} on {n_tr} / {n_val} molecules, "
            f"{rec['seconds']:.0f} s; checkpoint {ck_path}")
    meta["seconds"] = round(time.time() - t_start, 1)
    Path(a.out_prefix + ".json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    log(f"wrote {ck_path} and {a.out_prefix}.json in {meta['seconds']:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
