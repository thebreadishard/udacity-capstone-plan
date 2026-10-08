"""The model registry (decision 55, 3 Oct 2026; the user: "leg de regel vast dat we toekomstig werk doen met model-versies waar we tevreden mee zijn,
waarin de ontwerpkeuzes zitten waartoe we besloten hebben"; extended to every trained network with names and version numbers by decision 59, 4 Oct 2026).

Four networks are trained in this project, each with its own checkpoint folder and reviewed status file (MODULES below): the ΔH-network of module 05
(the correction network, rung C), the order scorer P1 and the learned order scorer P2 of the standout module, and the candidate generator of module 06.
One row per saved checkpoint: network, version, kind, reviewed status, chain, the recipe read from the checkpoint itself, the hold-out numbers and
the git commit from the result record beside it, and a note. Mechanical: nothing here is typed by hand except the reviewed status files — a checkpoint
without an entry stops the generator (a model that nobody has judged is not silently listed), and a status outside STATUSES is refused.

Versions (decision 59): a version number names a recipe, not a seed (three seeds share one). `1.x` is reserved for a network in production: every
`carried` entry has one, and the minor number counts the promotions (decision 57). A network that is not in production carries `0.x`, one number per
registered recipe that was read (status `experimental`). Candidates, search cells, smokes and invalid runs keep their chain name and no number.

The rule the loaders enforce (`require_carried`): future work runs on a model whose status is `carried`; a read made with any other status is not
evidence. `rungC_cc_transfer.py`, `probes/rungC_eval_saved.py` and `probes/anchor_deck_rehearsal.py` refuse such a model unless `--allow-any-model`
is passed, and that use is named in the record.

    python m05/model_registry.py            # writes every module's MODELS.md and the overview modules/MODELS.md
    python m05/model_registry.py --check    # exit 1 when a committed registry differs from what the checkpoints say (tests/test_model_registry.py runs it)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import torch

M05 = Path(__file__).resolve().parents[1]
PLAN = M05.parents[1]
MODULES_DIR = PLAN / "modules"
OUT = M05 / "out"
STATUS_FILE = OUT / "MODELS_STATUS.json"
REGISTRY = M05 / "MODELS.md"
OVERVIEW = MODULES_DIR / "MODELS.md"
STATUSES = ("carried", "superseded", "invalid", "smoke", "pretrained", "candidate", "experimental")
NETWORKS = (
    # name in text, where the code lives, module key
    ("ΔH-network", "module 05, rung C: `m05/rungC_equivariant.py` (body) + `m05/rungC_hybrid.py` (head), trained by `m05/rungC_train.py`", "05"),
    ("order scorer (P1)", "standout: `pp/scorer.py`, an MLP on 21 hand-made pair features", "standout"),
    ("learned order scorer (P2)", "standout: `pp/embed_scorer.py`, the ΔH-network's body with a pair head", "standout"),
    ("candidate generator", "module 06: `m06/model.py`, a decoder-only SMILES Transformer", "06"),
)
NETWORK_NAMES = tuple(n for n, _, _ in NETWORKS)
MODULES = {
    "05": dict(title="module 05 — the ΔH-network", out=OUT, status=STATUS_FILE, registry=REGISTRY, generator="m05/model_registry.py"),
    "standout": dict(title="standout — the order scorers P1 and P2", out=MODULES_DIR / "standout_pattern_proposer" / "out",
                     status=MODULES_DIR / "standout_pattern_proposer" / "out" / "MODELS_STATUS.json",
                     registry=MODULES_DIR / "standout_pattern_proposer" / "MODELS.md", generator="../05_support_predictor/m05/model_registry.py"),
    "06": dict(title="module 06 — the candidate generator", out=MODULES_DIR / "06_generative_candidates" / "notebook" / "out",
               status=MODULES_DIR / "06_generative_candidates" / "notebook" / "out" / "MODELS_STATUS.json",
               registry=MODULES_DIR / "06_generative_candidates" / "MODELS.md", generator="../05_support_predictor/m05/model_registry.py"),
}
RULE = ("**Rule (decision 55):** future work runs on a model whose status is `carried` — a version we are satisfied with, carrying the design decisions "
        "taken. A read made with a `superseded`, `smoke`, `pretrained`, `candidate` (saved by a registered chain, not yet read), `experimental` (a registered "
        "experiment's network, not in production) or `invalid` model is not evidence; the loaders refuse such a model unless `--allow-any-model` is given, "
        "and that use is named in the record. **Versions (decision 59):** a number names a recipe (seeds share it); `1.x` only for a network in production, "
        "the minor number counting promotions; `0.x` for a network outside production, one per registered recipe that was read; candidates, search cells, "
        "smokes and invalid runs keep their chain name.")
HEADER = """# Saved networks — the model registry, {title} (decision 55, 3 October 2026; names and versions by decision 59, 4 October 2026)

*Generated by `{generator}` from the checkpoints under `{out}` and the result records beside them; the status, network, version, chain and note
columns are the reviewed file `{status}` (a checkpoint without an entry stops the generator). {rule} The overview of all four networks is
`modules/MODELS.md`; `python m05/model_registry.py --check` fails when a registry is stale.*

| model | network | version | kind | status | chain | recipe (from the checkpoint) | hold-out (a) ratio / ω | hold-out (b) ratio / ω | commit | saved | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
"""
OVERVIEW_HEADER = """# The trained networks — names, versions and current versions (decision 59, 4 October 2026)

*Generated by `05_support_predictor/m05/model_registry.py` from the three reviewed status files; one row per network. {rule} The per-module
registries list every checkpoint: `05_support_predictor/MODELS.md`, `standout_pattern_proposer/MODELS.md`, `06_generative_candidates/MODELS.md`.
Lay descriptions of the four networks are in `GLOSSARY.md`.*

| network (name in text) | code | current version (in production) | versions on record | checkpoints |
|---|---|---|---|---|
"""


def load_checkpoint(path: Path) -> dict:
    return torch.load(path, map_location="cpu", weights_only=False)


def kind_of(ck) -> str:
    if isinstance(ck, dict) and "ctor" in ck and "args" in ck:
        return "hybrid"
    if isinstance(ck, dict) and "body_state" in ck:
        return "pretrained body"
    if isinstance(ck, dict) and "cfg" in ck and "states" in ck:
        return "embedding scorer"
    if isinstance(ck, dict) and ck and all(torch.is_tensor(v) for v in ck.values()):
        return "state dict"
    return "unknown"


def _params(states) -> int:
    return int(sum(int(v.numel()) for sd in states for v in sd.values() if torch.is_tensor(v)))


def recipe_of(ck) -> str:
    """The design choices as the checkpoint carries them (nothing inferred from the file name)."""
    kind = kind_of(ck)
    if kind == "hybrid":
        c, a = ck["ctor"], ck["args"]
        return (f"{ck.get('head', a.get('head'))} head, pattern {ck.get('pattern')}, target {ck.get('aux_target')} (λ {ck.get('ls_lam')}), aux {ck.get('aux_mode')} "
                f"(kring {ck.get('kring_weight')}, kdiag {ck.get('kdiag_weight')} {ck.get('kdiag_mode', 'all')}), body {c.get('n_blocks')}×{c.get('n_s')} {c.get('aggregation')}"
                f"{', tensor input' if c.get('tensor_input') else ''}, sqm α {'on' if c.get('sqm_scale') else 'off'}, pair features {c.get('n_pair_features', 0)}, "
                f"hidden {c.get('hidden')}, pool {a.get('pool_layers')}, analytic {'on' if a.get('use_analytic') else 'off'}, epochs {a.get('epochs')} / patience "
                f"{a.get('patience')}, lr {a.get('lr')}, n {ck.get('n')}, seed {ck.get('seed')}")
    if kind == "pretrained body":
        keys = [k for k in ("aggregation", "epochs", "lr", "n_molecules", "elements", "tensor_input") if k in ck]
        return "pretrained body: " + ", ".join(f"{k} {ck[k]}" for k in keys)
    if kind == "embedding scorer":
        return "embedding scorer: " + ", ".join(f"{k} {v}" for k, v in ck["cfg"].items()) + f"; {_params(ck['states']):,} parameters"
    if kind == "state dict":
        first = next(iter(ck.items()))
        return f"{_params([ck]):,} parameters in {len(ck)} tensors; first tensor {first[0]} {tuple(first[1].shape)}"
    return "unknown checkpoint layout: " + ", ".join(sorted(ck)[:8] if isinstance(ck, dict) else [type(ck).__name__])


def result_record(path: Path) -> dict | None:
    """The result json written by the run that saved the model: `<prefix>.json` for `<prefix>_model_n<n>_seed<s>.pt`, else `<stem>.json`."""
    prefix = path.name.split("_model_")[0] if "_model_" in path.name else path.stem
    p = path.parent / f"{prefix}.json"
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def commit_of(rec: dict | None, ck) -> str:
    prov = ck.get("provenance") if isinstance(ck, dict) else None
    for src in (prov if isinstance(prov, dict) else None, (rec or {}).get("provenance")):
        if isinstance(src, dict):
            c = next((str(v) for k, v in src.items() if "commit" in k), "")
            dirty = next((v for k, v in src.items() if "dirty" in k), None)
            if c:
                return c[:9] + (" (dirty)" if dirty in (True, "True", "true", 1) else "")
    return "—"


def holdout_numbers(rec: dict | None, ck, split: str) -> str:
    try:
        r = rec["curve"][str(ck["n"])]["per_seed"][int(ck["seed"])][split]
        return f"{r['coupling_ratio']:.2f} / {r['corrected_freq_rms']:.2f}"
    except (KeyError, IndexError, TypeError):
        return "—"


def check_entry(name: str, e: dict, status_file: Path) -> None:
    """The reviewed facts must be consistent with the rules: a known status; a known network; versions as decision 59 says."""
    if e.get("status") not in STATUSES:
        raise ValueError(f"{status_file}: {name} has status {e.get('status')!r}; allowed {STATUSES}")
    if e.get("network") not in NETWORK_NAMES:
        raise ValueError(f"{status_file}: {name} names network {e.get('network')!r}; allowed {NETWORK_NAMES}")
    v = str(e.get("version", "") or "")
    if e["status"] == "carried" and not (v and not v.startswith("0.")):
        raise ValueError(f"{status_file}: {name} is carried and needs a production version (1.x), has {v!r}")
    if e["status"] == "experimental" and v and not v.startswith("0."):
        raise ValueError(f"{status_file}: {name} is experimental (not in production) and its version must be 0.x, has {v!r}")


def read_status(status_file: Path) -> dict:
    if not status_file.exists():
        return {}
    with open(status_file, encoding="utf-8") as f:
        s = json.load(f)
    for name, e in s.items():
        check_entry(name, e, status_file)
    return s


def checkpoint_key(path: Path, out_dir: Path) -> str:
    return path.resolve().relative_to(out_dir.resolve()).as_posix()


def rows(out_dir: Path = OUT, status_file: Path = STATUS_FILE) -> tuple[list[dict], list[str]]:
    status = read_status(status_file)
    out, missing = [], []
    for p in sorted(out_dir.rglob("*.pt")):
        key = checkpoint_key(p, out_dir)
        if key not in status:
            missing.append(key)
            continue
        ck = load_checkpoint(p)
        rec = result_record(p)
        e = status[key]
        out.append(dict(model=key, network=e["network"], version=str(e.get("version", "") or "—"), kind=kind_of(ck), status=e["status"], chain=e.get("chain", ""),
                        recipe=recipe_of(ck), a=holdout_numbers(rec, ck, "a"), b=holdout_numbers(rec, ck, "b"), commit=commit_of(rec, ck),
                        saved=(rec or {}).get("date") or time.strftime("%Y-%m-%d %H:%M", time.localtime(p.stat().st_mtime)), note=e.get("note", "")))
    return out, missing


def render(table: list[dict], module: dict | None = None) -> str:
    m = module or MODULES["05"]
    head = HEADER.format(title=m["title"], generator=m["generator"], out=m["out"].relative_to(PLAN).as_posix(), status=m["status"].relative_to(PLAN).as_posix(), rule=RULE)
    body = "".join(f"| `{r['model']}` | {r['network']} | {r['version']} | {r['kind']} | **{r['status']}** | {r['chain']} | {r['recipe']} | {r['a']} | {r['b']} | "
                   f"{r['commit']} | {r['saved']} | {r['note']} |\n" for r in table)
    return head + body


def render_overview(tables: dict[str, list[dict]]) -> str:
    lines = [OVERVIEW_HEADER.format(rule=RULE)]
    for name, code, key in NETWORKS:
        rs = [r for r in tables.get(key, []) if r["network"] == name]
        carried = sorted({r["version"] for r in rs if r["status"] == "carried"})
        chains = sorted({r["chain"] for r in rs if r["status"] == "carried"})
        current = ", ".join(f"v{v}" for v in carried) + (f" ({', '.join(chains)}; {sum(r['status'] == 'carried' for r in rs)} seeds)" if chains else "") if carried \
            else "none in production (0.x)"
        seen: dict[tuple, int] = {}
        for r in rs:
            if r["version"] != "—":
                seen[(r["version"], r["status"], r["chain"])] = seen.get((r["version"], r["status"], r["chain"]), 0) + 1
        versions = "; ".join(f"v{v} — {s}{(' (' + c + ')') if c else ''}, {n} seed{'s' if n != 1 else ''}" for (v, s, c), n in sorted(seen.items())) or "—"
        counts = ", ".join(f"{s} {sum(r['status'] == s for r in rs)}" for s in STATUSES if any(r["status"] == s for r in rs)) or "none"
        lines.append(f"| {name} | {code} | {current} | {versions} | {len(rs)}: {counts} |\n")
    return "".join(lines)


def status_file_for(path: Path) -> tuple[Path, str]:
    """The reviewed status file that covers a checkpoint path, and the checkpoint's key in it."""
    p = Path(path).resolve()
    for m in MODULES.values():
        try:
            return m["status"], p.relative_to(m["out"].resolve()).as_posix()
        except ValueError:
            continue
    raise SystemExit(f"{path} lies under no registered checkpoint folder ({', '.join(str(m['out'].relative_to(PLAN)) for m in MODULES.values())}); decision 55")


def status_of(path: Path, status_file: Path | None = None) -> dict | None:
    if status_file is None:
        status_file, key = status_file_for(path)
        return read_status(status_file).get(key)
    s = read_status(status_file)
    return s.get(Path(path).name)


def require_carried(path: Path, allow: bool = False, status_file: Path | None = None) -> dict:
    """Decision 55: a read runs on a `carried` model. Stops with the reason otherwise; `allow` lets a named exception through (the record must say so)."""
    s = status_of(path, status_file)
    if s is None:
        raise SystemExit(f"{Path(path).name} is not in the model registry: give it a reviewed status first (decision 55)")
    if s["status"] != "carried" and not allow:
        raise SystemExit(f"{Path(path).name} has status {s['status']!r} in the model registry — not a base for a read (decision 55); "
                         "pass --allow-any-model to use it anyway and name that in the record")
    return s


def add_candidates(paths: list, chain: str, note: str, network: str, status_file: Path | None = None) -> list[str]:
    """Enter saved models of a registered chain as `candidate` (decision 55: saved, not yet read). Refuses a model that already has a status, so a
    reviewed entry is never overwritten. Returns the keys added."""
    if not paths:
        raise SystemExit("--add-candidates: no checkpoint matches")
    sf = Path(status_file) if status_file else status_file_for(paths[0])[0]
    s = read_status(sf)
    keys = [Path(p).name if status_file else status_file_for(p)[1] for p in paths]
    taken = [k for k in keys if k in s]
    if taken:
        raise SystemExit(f"--add-candidates: already in the registry, not overwritten: {', '.join(taken)}")
    for k in keys:
        s[k] = {"status": "candidate", "network": network, "version": "", "chain": chain, "note": note}
        check_entry(k, s[k], sf)
    with open(sf, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=1, ensure_ascii=False)
    return keys


def _write_or_check(path: Path, text: str, check: bool) -> bool:
    if check:
        return path.exists() and path.read_text(encoding="utf-8") == text
    path.write_text(text, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--module", default="all", choices=["all", *MODULES], help="which registry to write (default: all three and the overview)")
    ap.add_argument("--out-dir", default=None, help="ad-hoc single folder (tests): with --status-file and --registry")
    ap.add_argument("--status-file", default=None)
    ap.add_argument("--registry", default=None)
    ap.add_argument("--check", action="store_true", help="exit 1 if a committed registry differs from what the checkpoints say")
    ap.add_argument("--add-candidates", nargs="+", default=None, help="checkpoints of a registered chain to enter as `candidate` (then the registry is rewritten)")
    ap.add_argument("--chain", default=None, help="with --add-candidates: the chain name")
    ap.add_argument("--note", default="", help="with --add-candidates: what the chain is and where it is registered")
    ap.add_argument("--network", default=None, help="with --add-candidates: the network name (default: the ΔH network)")
    a = ap.parse_args(argv)
    if a.add_candidates:
        if not a.chain:
            raise SystemExit("--add-candidates needs --chain")
        added = add_candidates([Path(p) for p in a.add_candidates], a.chain, a.note, a.network or NETWORK_NAMES[0],
                               Path(a.status_file) if a.status_file else None)
        print(f"registered as candidate: {', '.join(added)}")
    if a.out_dir or a.status_file or a.registry:
        mods = {"adhoc": dict(title="ad hoc", out=Path(a.out_dir or OUT), status=Path(a.status_file or STATUS_FILE), registry=Path(a.registry or REGISTRY),
                              generator="m05/model_registry.py")}
    else:
        mods = MODULES if a.module == "all" else {a.module: MODULES[a.module]}
    tables, stale = {}, []
    for key, m in mods.items():
        table, missing = rows(m["out"], m["status"])
        if missing:
            print("model registry STOPPED: no reviewed status for " + ", ".join(missing) + f" — add them to {m['status']}", file=sys.stderr)
            return 1
        tables[key] = table
        try:
            text = render(table, m)
        except ValueError:                                                  # an ad-hoc folder outside the plan: header paths cannot be made relative
            text = render(table, dict(m, out=PLAN / m["out"].name, status=PLAN / m["status"].name))
        if not _write_or_check(m["registry"], text, a.check):
            stale.append(str(m["registry"]))
    if mods is MODULES and not _write_or_check(OVERVIEW, render_overview(tables), a.check):
        stale.append(str(OVERVIEW))
    if a.check:
        if stale:
            print("model registry STALE: " + ", ".join(stale) + " differ from the checkpoints — run m05/model_registry.py", file=sys.stderr)
            return 1
        print(f"model registry ok ({sum(len(t) for t in tables.values())} models in {len(tables)} folder(s))")
        return 0
    for key, t in tables.items():
        print(f"wrote {mods[key]['registry']} ({len(t)} models; carried: {sum(r['status'] == 'carried' for r in t)})")
    if mods is MODULES:
        print(f"wrote {OVERVIEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
