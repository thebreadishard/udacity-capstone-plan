"""Module 06 tests — seconds, no network, no real training: tokenizer round trip, deterministic scaffold split, model shapes, one training step
lowers the loss on a toy set, metrics on known samples."""
import os
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
from data import Vocab, hetero_class, murcko, split_of, tokenize  # noqa: E402
from evaluate import evaluate_samples, project_fit  # noqa: E402
from model import SmilesTransformer  # noqa: E402

TOY = ["c1ccc2ccccc2c1", "c1ccc2ncccc2c1", "Cc1ccc2ccccc2c1", "c1ccc2occc2c1", "Clc1ccc2ccccc2c1", "c1ccc2[nH]ccc2c1", "Oc1ccc2ccccc2c1", "c1ccc2sccc2c1"]


def test_tokenizer_round_trip():
    for s in TOY + ["Clc1ccc(Br)c2ccccc12", "c1cc[nH]c1"]:
        assert "".join(tokenize(s)) == s
    assert tokenize("Clc1ccccc1")[0] == "Cl"


def test_vocab_encode_decode():
    v = Vocab.build(TOY); ids = v.encode(TOY[0], max_len=32)
    assert ids[0] == v.stoi["<bos>"] and v.decode(ids) == TOY[0] and len(ids) == 32
    assert v.encode("c" * 100, max_len=32) is None


def test_split_is_deterministic_and_by_scaffold():
    assert split_of("c1ccc2ccccc2c1") == split_of("c1ccc2ccccc2c1") and split_of("c1ccc2ccccc2c1") in ("train", "val", "test")
    assert murcko("Cc1ccc2ccccc2c1") == murcko("Oc1ccc2ccccc2c1") == "c1ccc2ccccc2c1"


def test_model_shapes_and_sampling():
    v = Vocab.build(TOY); m = SmilesTransformer(len(v.itos), max_len=32, d=32, heads=2, layers=1, ff=64)
    X = torch.tensor([v.encode(s, 32) for s in TOY]); logits = m(X[:, :-1])
    assert logits.shape == (len(TOY), 31, len(v.itos)) and m.loss(X).item() > 0
    ids = m.sample(3, v.stoi["<bos>"], v.stoi["<eos>"], max_len=16, seed=0); assert ids.shape[0] == 3 and ids.shape[1] <= 16


def test_one_step_lowers_loss():
    torch.manual_seed(0); v = Vocab.build(TOY); m = SmilesTransformer(len(v.itos), max_len=32, d=32, heads=2, layers=1, ff=64, dropout=0.0)
    X = torch.tensor([v.encode(s, 32) for s in TOY]); opt = torch.optim.AdamW(m.parameters(), lr=1e-3)
    l0 = m.loss(X)
    for _ in range(20):
        loss = m.loss(X); opt.zero_grad(); loss.backward(); opt.step()
    assert m.loss(X).item() < l0.item()


def test_metrics_on_known_samples():
    train = TOY[:6]; scafs = [murcko(s) for s in train]
    test_rows = [dict(smiles=s) for s in TOY[6:]]
    samples = ["c1ccc2ccccc2c1", "c1ccc2ccccc2c1", "Fc1ccc2ccccc2c1", "not a smiles", "c1ccccc1", "[NH4+]"]
    res, extra = evaluate_samples(samples, train, scafs, test_rows, murcko)
    assert abs(res["validity"] - 5 / 6) < 1e-9 and res["uniqueness"] == 4 / 5 and 0 < res["novelty"] < 1
    assert project_fit("Fc1ccc2ccccc2c1") and not project_fit("c1ccccc1") and not project_fit("[NH4+]")
    assert hetero_class("c1ccc2ncccc2c1") == "N" and hetero_class("c1ccc2ccccc2c1") == "none"
