"""Digests of the ΔH network's per-molecule tensors and of its ΔH on the frozen corpus (TASKS 146), printed as JSON: by the training path
(`rungC_train.load_corpus` with the analytic labels, then `molecule_tensors`) and, with --inference, by the pipeline's inference path
(`rungC_infer`), which reads no truth. Run by `tests/test_rungC_infer.py` in a fresh single-threaded process.

    python tests/molecule_tensors_pin_runner.py <corpus/molecules> <model.pt> <cache dir> [--inference]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(TESTS.parent / "modules" / "05_support_predictor" / "m05"))
import rungC_infer as RI  # noqa: E402  (after the sys.path inserts, as every m05 import)
import torch  # noqa: E402
from rungC_equivariant import load_molecule  # noqa: E402
from rungC_train import load_corpus, load_hybrid_model, molecule_tensors, tensor_config  # noqa: E402

from pin_tools import digest  # noqa: E402


def tensor_digests(t: dict) -> dict[str, str]:
    return {k: digest(v) for k, v in sorted(t.items()) if torch.is_tensor(v)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("model")
    ap.add_argument("cache")
    ap.add_argument("--inference", action="store_true")
    a = ap.parse_args()
    model, ck = load_hybrid_model(Path(a.model))
    cfg = tensor_config(ck)
    mols, *_rest, substituted = load_corpus(a.molecules, use_analytic=True, log=lambda _s: None)
    out = {"training": {}}
    for i in sorted(substituted):
        d = Path(a.molecules) / i
        t = molecule_tensors(i, load_molecule(d, use_analytic=True), mols[i], d, cfg, Path(a.cache))
        out["training"][i] = {"tensors": tensor_digests(t), "dH": digest(RI.delta_H(model, t))}
    if a.inference:
        out["inference"] = {}
        for i in sorted(substituted):
            t = RI.input_tensors_of(Path(a.molecules) / i, cfg)
            out["inference"][i] = {"tensors": tensor_digests(t), "dH": digest(RI.delta_H(model, t))}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
