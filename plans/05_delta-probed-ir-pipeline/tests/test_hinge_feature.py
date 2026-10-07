"""Chain 36 / TASKS 23 (7 Oct 2026): the hinge class per atom and its embedding. The classes on molecules whose hinges are known; the embedding is built
without a random draw (so a run without the feature initialises every other parameter as before); a model saved before the feature loads with the
embedding at zero and gives the same body output with or without the classes."""
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
Chem = pytest.importorskip("rdkit.Chem")
from rdkit.Chem import AllChem  # noqa: E402

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import rungC_equivariant as RE  # noqa: E402

CLS = {c: k for k, c in enumerate(RE.HINGE_CLASSES)}


def _geom(smiles):
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    assert AllChem.EmbedMolecule(m, randomSeed=7) == 0
    AllChem.MMFFOptimizeMolecule(m)
    sym = [a.GetSymbol() for a in m.GetAtoms()]
    return sym, m.GetConformer().GetPositions() / RE.BOHR2ANG


def _counts(smiles):
    sym, x = _geom(smiles)
    h = RE.hinge_classes(sym, x)
    return {c: int((h == k).sum()) for c, k in CLS.items()}, h, sym


def test_classes_on_known_hinges():
    c, _, _ = _counts("c1ccccc1")
    assert c["none"] == 12
    c, _, _ = _counts("c1ccc(cc1)-c1ccccc1")                       # biphenyl: the two carbons of the inter-ring bond
    assert c["rotor"] == 2 and c["ring5"] == c["ring4"] == 0
    c, h, sym = _counts("N#Cc1ccccc1")                               # benzonitrile: C≡N linear, the ipso carbon a rotor
    assert c["linear"] == 2 and c["rotor"] == 1
    c, _, _ = _counts("C1c2ccccc2-c2ccccc12")                       # fluorene: the five-ring's five atoms (CH2 included: ring5 before sp3)
    assert c["ring5"] == 5 and c["sp3"] == 0
    c, _, _ = _counts("c1ccc2c(c1)-c1ccccc1-2")                     # biphenylene: the four-ring's four atoms
    assert c["ring4"] == 4
    c, _, _ = _counts("Cc1ccccc1")                                  # toluene: the methyl is sp3; a terminal methyl makes no rotor
    assert c["sp3"] == 1 and c["rotor"] == 0
    c, _, _ = _counts("O=C(c1ccccc1)c1ccccc1")                      # benzophenone: carbonyl carbon and both ipso carbons
    assert c["rotor"] == 3


def test_embedding_draws_no_random_numbers():
    torch.manual_seed(0)
    a = torch.rand(3)
    torch.manual_seed(0)
    torch.nn.Embedding.from_pretrained(torch.zeros(6, 64), freeze=False)
    assert torch.equal(torch.rand(3), a)


def test_old_checkpoint_loads_with_zero_hinge_rows_and_unchanged_output():
    p = PLAN / "modules" / "05_support_predictor" / "out" / "E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt"
    if not p.exists():
        pytest.skip("chain 34's model is not on this machine")
    from rungC_train import load_hybrid_model
    model, _ = load_hybrid_model(p)
    assert float(model.body.h_emb.weight.abs().max()) == 0.0
    d = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / "A_8448043181"
    m = RE.load_molecule(d, use_analytic=True)
    t = RE.to_torch(m)
    with torch.no_grad():
        s0 = model.body.encode(t["Z"], t["pos"], t["H_low"])[0]
        s1 = model.body.encode(t["Z"], t["pos"], t["H_low"], None, torch.as_tensor(m["hidx"], dtype=torch.long))[0]
    assert torch.equal(s0, s1)
