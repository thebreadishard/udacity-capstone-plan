"""A candidate from module 06 for the out-of-corpus scenario (S3): one sample drawn from the trained SMILES Transformer (seed 0 of the
26 September run) at temperature 1.0 with a fixed seed; the first valid, fused-aromatic, corpus-novel string is the request. Recorded with its
draw index so that the same candidate comes back on every run."""
from __future__ import annotations

import csv
import json
import sys

from .catalog import PLAN, canonical

M06 = PLAN / "modules" / "06_generative_candidates"
MANIFEST = PLAN / "modules" / "05_support_predictor" / "corpus" / "manifest.csv"


def corpus_canonicals() -> set[str]:
    out = set()
    for r in csv.DictReader(open(MANIFEST, encoding="utf-8")):
        c = canonical(r.get("smiles"))
        if c:
            out.add(c)
    return out


def draw_candidate(seed: int = 0, n: int = 200, temperature: float = 1.0, max_heavy: int = 26) -> dict:
    sys.path.insert(0, str(M06 / "m06"))                       # module 06 imports its files flat (train.py: `from data import Vocab`)
    import torch
    from data import Vocab
    from model import SmilesTransformer
    from rdkit import Chem, RDLogger
    from rdkit.Chem import rdMolDescriptors
    from train import generate
    RDLogger.DisableLog("rdApp.*")
    run_dir = M06 / "notebook" / "out" / "seed0"
    log = json.load(open(run_dir / "train_log_seed0.json", encoding="utf-8"))
    vocab = Vocab(log["vocab"])
    model = SmilesTransformer(len(vocab.itos), max_len=log["max_len"])
    model.load_state_dict(torch.load(run_dir / "model_seed0.pt", map_location="cpu")); model.eval()
    torch.set_num_threads(2)
    samples = generate(model, vocab, n=n, temperature=temperature, seed=seed)
    corpus = corpus_canonicals()
    n_valid = 0
    for k, s in enumerate(samples):
        m = Chem.MolFromSmiles(s)
        if m is None:
            continue
        n_valid += 1
        if m.GetNumHeavyAtoms() > max_heavy or rdMolDescriptors.CalcNumAromaticRings(m) < 2:
            continue
        c = Chem.MolToSmiles(m)
        if c in corpus:
            continue
        return dict(smiles=c, heavy_atoms=m.GetNumHeavyAtoms(), aromatic_rings=rdMolDescriptors.CalcNumAromaticRings(m), draw_index=k, n_drawn=n, n_valid=n_valid,
                    source=f"module 06 {run_dir.relative_to(PLAN).as_posix()}/model_seed0.pt (run of 25–26 Sep 2026), generate(n={n}, T={temperature}, seed={seed}); first valid fused-aromatic string not in the corpus")
    raise RuntimeError("no valid corpus-novel fused-aromatic sample among the draws")
