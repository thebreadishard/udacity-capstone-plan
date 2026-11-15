"""The regression pins of aromir's network port (TASKS 73): the trainer's own inference path on fixed molecules and seeded random models.

aromir (`thebreadishard/aromir`, `src/aromir/network/`) rewrites module 05's inference path — the internal coordinates, the pair pattern
with rung B's pair features, the equivariant body and the hybrid head. Its tests compare its ΔH with the numbers this script writes, so
the two codes are held to the same output without aromir importing this repository.

Each pin is one configuration of the head (a seeded random model, every parameter and buffer drawn, so no zero-initialised row hides a
wiring error) and a handful of molecules that between them meet every pair class, every hinge class but ring4, a linear group and a
non-planar dihedral. The geometries are RDKit's (no quantum chemistry) and the low-level Hessian is a seeded random symmetric matrix
with the rigid motions projected out: the network's arithmetic does not care that it is not a real Hessian, and the pin needs no pyscf.

    python probes/aromir_network_golden.py <out folder>      # run under an environment with torch, geomeTRIC, RDKit and safetensors
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
for _p in (M05 / "m05", M05 / "corpus", PLAN / "probes", PLAN / "src"):
    sys.path.insert(0, str(_p))
import internal_coords as IC  # noqa: E402  (module 05's code is not a package)
import rungC_infer as RI  # noqa: E402
import vibrations as VIB  # noqa: E402
from rungC_hybrid import HybridDeltaFModel  # noqa: E402
from rungC_train import TensorSettings  # noqa: E402
from safetensors.torch import save_file  # noqa: E402

MOLECULES = {"benzene": "c1ccccc1", "phenanthrene": "c1ccc2c(c1)ccc1ccccc12", "toluene": "Cc1ccccc1", "benzonitrile": "N#Cc1ccccc1",
             "biphenyl": "c1ccc(cc1)-c1ccccc1", "chlorophenol": "Oc1ccc(Cl)cc1", "benzothiophene": "c1ccc2sccc2c1",
             "fluoropyridine": "Fc1ccncc1"}
SMALL = dict(n_s=16, n_v=16, n_blocks=2, hidden=24, tensor_input=False)   # the body's update needs n_s == n_v
WEIGHT_SPREAD = 0.1                  # small enough that a sum-pooled random body stays within float32's reach
SIDE_MOLECULES = ("benzene", "toluene", "benzonitrile", "biphenyl")   # the two side configurations pin these four
N_PAIR_FEATURES = 66                 # rung B's pair vector under the raw and cos encodings (2 × 29 + 8)
CONFIGS = {
    "carried_shape": dict(molecules=tuple(MOLECULES), ctor=SMALL | dict(aggregation="sum", sqm_scale=True, n_pair_features=N_PAIR_FEATURES, parity_odd=False),
                          pattern="f", primitives=IC.PrimitiveSettings()),
    "order_free": dict(molecules=SIDE_MOLECULES, ctor=SMALL | dict(aggregation="sum", sqm_scale=True, n_pair_features=N_PAIR_FEATURES, parity_odd=False),
                       pattern="f", primitives=IC.PrimitiveSettings(angle_choice="canonical", dihedral_encoding="cos")),
    "parity_odd": dict(molecules=SIDE_MOLECULES, ctor=SMALL | dict(aggregation="mean", sqm_scale=False, n_pair_features=0, parity_odd=True),
                       pattern="d", primitives=IC.PrimitiveSettings()),
}
MASSES = {"H": 1.00782503223, "C": 12.0, "N": 14.00307400443, "O": 15.99491461957, "F": 18.99840316273, "S": 31.9720711744,
          "Cl": 34.968852682}
BOHR = 0.529177210903


def start_geometry(smiles: str) -> tuple[list[str], np.ndarray]:
    """RDKit ETKDG + MMFF, seed 0, atoms as RDKit numbers them: (symbols, coordinates in bohr)."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    m = Chem.AddHs(Chem.MolFromSmiles(Chem.MolToSmiles(Chem.MolFromSmiles(smiles))))
    if AllChem.EmbedMolecule(m, randomSeed=0) != 0:
        raise RuntimeError(f"{smiles}: no embedding")
    AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
    return [a.GetSymbol() for a in m.GetAtoms()], np.asarray(m.GetConformer().GetPositions(), float) / BOHR


def random_hessian(n_atoms: int, seed: int) -> np.ndarray:
    """A seeded symmetric matrix with a stiff diagonal: (3N, 3N), the size of a Hessian in hartree/bohr²."""
    a = np.random.default_rng(seed).normal(scale=0.02, size=(3 * n_atoms, 3 * n_atoms))
    return a + a.T + 0.5 * np.eye(3 * n_atoms)


def projected(H: np.ndarray, masses: np.ndarray, coords: np.ndarray) -> np.ndarray:
    """`analytic_hessians.project_tr` (which imports pyscf) on the shared arithmetic of `corpus/vibrations.py`."""
    sm = VIB.mass_weights(masses)
    q = VIB.rigid_basis(masses, coords)
    P = np.eye(len(sm)) - q @ q.T
    return (P @ (H / np.outer(sm, sm)) @ P) * np.outer(sm, sm)


def random_model(ctor: dict, seed: int) -> HybridDeltaFModel:
    """The head with every parameter and buffer drawn: scales and spreads positive, the rest normal."""
    torch.manual_seed(seed)
    model = HybridDeltaFModel(**ctor)
    with torch.no_grad():
        for name, value in model.state_dict().items():
            if name == "body.rbf.centres":
                continue
            drawn = torch.randn_like(value) * WEIGHT_SPREAD
            if name in ("class_scale", "flow_scale", "pfeat_sd"):
                drawn = drawn.abs() + 0.5
            value.copy_(drawn)
    return model.eval()


def moved_into_place(tmp: Path, target: Path) -> None:
    """A pin is written beside its target and moved over it, so a stopped run leaves no half-written pin."""
    os.replace(tmp, target)


def pin(name: str, cfg: dict, out: Path, seed: int) -> None:
    model = random_model(cfg["ctor"], seed)
    save_file({k: v.contiguous() for k, v in model.state_dict().items()}, out / f"{name}.tmp.safetensors")
    moved_into_place(out / f"{name}.tmp.safetensors", out / f"{name}.safetensors")
    primitives: IC.PrimitiveSettings = cfg["primitives"]
    record = {"ctor": cfg["ctor"], "head": "hybrid", "pattern": cfg["pattern"], "seed": seed}
    if primitives != IC.CARRIED:
        record |= {"angle_choice": primitives.angle_choice, "dihedral_encoding": primitives.dihedral_encoding}
    (out / f"{name}.json.tmp").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    moved_into_place(out / f"{name}.json.tmp", out / f"{name}.json")
    settings = TensorSettings(aux="both", head="hybrid", pattern=cfg["pattern"], aux_target=None, ls_lam=None, primitives=primitives)
    for k, molecule in enumerate(cfg["molecules"]):
        symbols, coords = start_geometry(MOLECULES[molecule])
        masses = np.array([MASSES[s] for s in symbols])
        H = random_hessian(len(symbols), seed=100 + k)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / molecule
            d.mkdir()
            (d / "geometry.json").write_text(json.dumps({"symbols": [s.upper() for s in symbols], "coords_bohr": coords.tolist(),
                                                         "masses_amu": masses.tolist()}), encoding="utf-8")
            np.savez(d / RI.LOW_HESSIAN, H_projected=projected(H, masses, coords))
            t = RI.input_tensors_of(d, settings)
            dH = RI.delta_H(model, t).numpy()
        # the integers say where a mismatch starts; every float input reaches ΔH through a drawn weight, so ΔH pins those
        np.savez_compressed(out / f"{name}_{molecule}.tmp.npz", symbols=np.array(symbols), coords_bohr=coords, hessian=H, delta_h=dH,
                            pairs=t["pairs"].numpy().astype(np.int32), pair_classes=t["pcls"].numpy().astype(np.int8),
                            hinge_classes=t["hidx"].numpy().astype(np.int8), odd=t["podd"].numpy())
        moved_into_place(out / f"{name}_{molecule}.tmp.npz", out / f"{name}_{molecule}.npz")
        print(f"{name} {molecule}: {len(symbols)} atoms, {t['B'].shape[0]} primitives, {len(t['pairs'])} pairs, "
              f"classes {sorted(set(t['pcls'].tolist()))}, hinges {sorted(set(t['hidx'].tolist()))}, max |dH| {np.abs(dH).max():.3e}", flush=True)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python probes/aromir_network_golden.py <out folder>")
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(1)
    for seed, (name, cfg) in enumerate(CONFIGS.items()):
        pin(name, cfg, out, seed)


if __name__ == "__main__":
    main()
