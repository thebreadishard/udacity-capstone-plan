"""The candidate generator's batch route (TASKS 22, pre-registration of 4 Oct 2026): every gate stage on hand-made molecules, the niche test (largest
fused aromatic ring system) against a small manifest and the listed cores, the PubChem column, the frozen list's order and hash determinism, and the
loader of a trained run (skipped when the checkpoints are not present, as in CI)."""
import csv
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
PLAN = Path(__file__).resolve().parents[1]
M06 = PLAN / "modules" / "06_generative_candidates"
sys.path.insert(0, str(M06 / "m06"))
import gate as G  # noqa: E402

NAPH = "c1ccc2ccccc2c1"
PHEN = "c1ccc2c(c1)ccc1ccccc12"                      # phenanthrene: a new ring system against a manifest of naphthalene children
ANTH = "c1ccc2cc3ccccc3cc2c1"
CORES = {"benzene": "c1ccccc1", "naphthalene": NAPH}


def _manifest(tmp_path: Path, smiles: list[str]) -> Path:
    p = tmp_path / "manifest.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "layer", "smiles", "qm9_label"])
        w.writeheader()
        for i, s in enumerate(smiles):
            w.writerow(dict(id=f"X_{i}", layer="B", smiles=s, qm9_label=""))
        w.writerow(dict(id="C_1", layer="C", smiles="", qm9_label="dsgdb9nsd_000001"))   # a QM9 row without SMILES is skipped
    return p


def _rows(smiles: list[str], run="seed0", request=""):
    return [dict(run=run, request=request, index=i, smiles_raw=s, smiles=G.canonical(s) or "") for i, s in enumerate(smiles)]


def test_ring_system_is_the_largest_fused_aromatic_system():
    assert G.ring_system("OC(=O)c1ccc2ccccc2c1") == G.canonical(NAPH)                       # substituent removed
    assert G.ring_system("c1ccc(cc1)-c1ccccc1") == G.canonical("c1ccccc1")                   # biphenyl: not fused → benzene
    assert G.ring_system("c1ccc2ccccc2c1-c1ccccc1") == G.canonical(NAPH)                     # the larger of two systems
    assert G.ring_system(PHEN) == G.canonical(PHEN) and G.ring_system("Cc1ccncc1") == G.canonical("c1ccncc1")
    assert G.ring_system("CCCC") == ""


def test_every_stage_is_the_first_failed_gate(tmp_path):
    man_s, man_sys = G.manifest_sets(_manifest(tmp_path, [NAPH, "OC(=O)c1ccc2ccccc2c1"]), CORES)
    assert G.canonical(NAPH) in man_s and G.canonical(NAPH) in man_sys and G.canonical("c1ccccc1") in man_sys and len(man_sys) == 2
    cases = {
        "c1ccc": "parses",
        "[NH3+]c1ccc2ccccc2c1": "neutral_closed_shell",
        "[CH2]c1ccc2ccccc2c1": "neutral_closed_shell",
        "Brc1ccc2ccccc2c1": "elements",
        "CCCCCCCCCCCCCCCCCCCCCCCc1ccc2ccccc2c1": "heavy_le_30",
        "c1ccccc1": "fused_aromatic_2plus",
        "c1ccc(cc1)-c1ccccc1": "fused_aromatic_2plus",            # two aromatic rings, not fused
        NAPH: "not_in_manifest",
        "Cc1ccc2ccccc2c1": "new_ring_system",                      # a substituent on a known core: the enumeration can make it
        "c1ccc2ccccc2c1-c1ccccc1": "new_ring_system",              # a known system with a side ring: still naphthalene's skeleton
        PHEN: "pass",
        ANTH: "pass",
        "Cc1ccc2cc3ccccc3cc2c1": "pass",                           # a substituted new system passes on its system
    }
    for smi, expected in cases.items():
        stage, _ = G.stage_of(G.canonical(smi) or "", man_s, man_sys)
        assert stage == expected, (smi, stage, expected)


def test_gate_table_summary_and_frozen_list(tmp_path):
    man_s, man_sys = G.manifest_sets(_manifest(tmp_path, [NAPH]), CORES)
    known = {G.canonical(PHEN)}                                               # phenanthrene 'in the PubChem set', anthracene not
    rows = _rows([PHEN, PHEN, ANTH, NAPH, "c1ccc", "Cc1ccc2ccccc2c1", "Cc1ccc2cc3ccccc3cc2c1"]) + _rows([ANTH], run="cond_seed0", request="<r3> <hnone>")
    table, s = G.gate(rows, man_s, man_sys, known)
    assert s["n_samples"] == 8 and s["n_distinct"] == 6                        # PHEN ×2 and ANTH ×2 collapse; the unparsed one is its own key
    assert s["by_stage"] == {"parses": 1, "neutral_closed_shell": 0, "elements": 0, "heavy_le_30": 0, "fused_aromatic_2plus": 0,
                             "not_in_manifest": 1, "new_ring_system": 1}
    assert s["n_pass"] == 3 and s["n_new_ring_systems"] == 2                   # methyl-anthracene shares anthracene's system
    assert s["n_new_ring_systems_in_pubchem_set"] == 1 and s["n_pass_in_pubchem_set"] == 1
    assert s["per_class"] == {"r3 none": dict(molecules=3, ring_systems=2)}
    assert s["per_run"] == {"cond_seed0 <r3> <hnone>": dict(samples=1), "seed0": dict(samples=7)}
    anth = next(t for t in table if t["smiles"] == G.canonical(ANTH))
    assert anth["occurrences"] == 2 and anth["runs"] == "cond_seed0 <r3> <hnone>; seed0"
    assert anth["ring_class"] == "r3" and anth["hetero_class"] == "none" and anth["ring_system"] == G.canonical(ANTH)
    fl = G.frozen_list(table)
    assert fl[0]["smiles"] == G.canonical(PHEN) and fl[1]["smiles"] == anth["smiles"]    # PubChem-known first, then occurrences
    meta = dict(date="d", proposals="p.csv", n_manifest_smiles=1, n_known_systems=2, n_cores=2, n_pubchem=1, seconds=0)
    s1 = G.write_outputs(str(tmp_path / "a"), table, s, meta)
    s2 = G.write_outputs(str(tmp_path / "b"), table, s, meta)
    assert s1["gated_sha256"] == s2["gated_sha256"]
    gated = list(csv.DictReader(open(tmp_path / "a_gated.csv", encoding="utf-8")))
    assert [g["smiles"] for g in gated] == [t["smiles"] for t in fl] and gated[0]["in_pubchem_set"] == "True" and "ring_system" in gated[0]
    assert "**pass** | **3**" in (tmp_path / "a.md").read_text(encoding="utf-8")


def test_cores_are_read_from_the_manifest_builder():
    cores = G.cores_of_manifest_builder()
    assert "naphthalene" in cores and len(cores) >= 19


@pytest.mark.skipif(not (M06 / "notebook" / "out" / "seed0" / "model_seed0.pt").exists(), reason="module 06 checkpoints not present (CI)")
def test_load_run_reads_vocab_and_weights():
    pytest.importorskip("torch")
    import propose as P
    model, vocab, meta = P.load_run("seed0", allow_any_model=True)
    assert meta["params"] == 3_201_024 and len(vocab.itos) == 33 and meta["status"] == "experimental" and meta["version"] == "0.1"
    with pytest.raises(SystemExit):
        P.load_run("seed0", allow_any_model=False)                             # decision 55: experimental is not a base without the override
