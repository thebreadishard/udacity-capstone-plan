"""The DFT repeat: does motif locality survive the arrival of electrons?

Companion to probe_band_locality_2026-08-26.ipynb, which measured the same thing
with MMFF94 and reached a positive but non-decisive answer. Its stated limitation
was blunt: a classical force field has no electrons, so the mechanism most likely
to break locality in a real PAH -- coupling carried by the delocalised pi system --
could not appear in that calculation at all.

This replaces the Hessian with B3LYP/6-31G* and changes nothing else. Same SMILES,
same seed, same local-basis construction, same adjacency and bay detection, same
three tests. Any difference in the result is therefore attributable to electrons
and not to a change of method.

WHAT IT DECIDES

  Condition 1 of the plan-03 trigger, written down before any of this was
  measured, requires that effective dimension not grow with molecular size. The
  MMFF run met it at force-field level. This run either upgrades that to a real
  result or kills it.

  The sharpest single number is the bay penalty. MMFF puts bay-containing CH
  out-of-plane runs 11.2 cm-1 below the same class without a bay, and that shift
  scales with how many bays a molecule has. Two outcomes, two meanings:

      penalty stays near 11 cm-1  ->  the bay effect is mechanical, and a motif
                                      atlas needs bays as separate motifs, full stop
      penalty grows substantially ->  pi-mediated coupling is adding to it, and
                                      locality is weaker than the force field says

  Phenanthrene carries one bay, triphenylene three. That is why both are here.

COST, MEASURED FIRST (see hardware_capability_2026-08-26.py)

  benzene 3.3 min, naphthalene 12.7 min per Hessian on this laptop; the full set
  is roughly 3-4 hours. Geometry optimisation adds 1-3 minutes per molecule.

  This script is RESUMABLE. Each molecule's result is written to results/ as soon
  as it finishes, and an existing file is reused rather than recomputed. Killing
  the run and restarting it costs nothing.

Run:  & "$env:USERPROFILE\\.conda\\envs\\qc\\python.exe" dft_locality_2026-08-26.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import psi4
from rdkit import Chem
from rdkit.Chem import AllChem

# ---------------------------------------------------------------- configuration

FUNCTIONAL = "b3lyp"
BASIS = "6-31G*"
MEMORY_GB = 12
THREADS = 8
SEED = 0xC0FFEE

TOLERANCE_CM = 10.0   # the project's frozen band-centre tolerance
BAY_HH_ANG = 2.5      # non-neighbouring CH pair closer than this sits across a bay

RESULTS = Path(__file__).parent / "results_dft_locality"

# (name, SMILES, (n_C, n_H), bays) -- bay count is documentation, not used in logic
#
# Chosen for TWO things, because the first pass was chosen for only one and the
# transfer test came back void. A class must appear in at least two different host
# molecules or its spread measures symmetry, not transferability.
#   bays      : phenanthrene 1, triphenylene 3, chrysene 1 -> does the penalty scale?
#   transfer  : solo in anthracene + tetracene; quartet in naphthalene + anthracene
#               + tetracene; duo in phenanthrene + pyrene + chrysene
MOLECULES = [
    ("benzene",      "c1ccccc1",                     (6, 6),   0),
    ("naphthalene",  "c1ccc2ccccc2c1",               (10, 8),  0),
    ("anthracene",   "c1ccc2cc3ccccc3cc2c1",         (14, 10), 0),
    ("phenanthrene", "c1ccc2c(c1)ccc1ccccc12",       (14, 10), 1),
    ("pyrene",       "c1cc2ccc3cccc4ccc(c1)c2c34",   (16, 10), 0),
    ("tetracene",    "c1ccc2cc3cc4ccccc4cc3cc2c1",   (18, 12), 0),
    ("chrysene",     "c1ccc2c(c1)ccc1c2ccc2ccccc21", (18, 12), 1),
    ("triphenylene", "c1ccc2c(c1)c1ccccc1c1ccccc21", (18, 12), 3),
]

CLASS_NAME = {1: "solo", 2: "duo", 3: "trio", 4: "quartet", 5: "quintet", 6: "sextet"}
LITERATURE_OOP = {1: 890.0, 2: 833.0, 3: 787.0, 4: 745.0}

# MMFF result being tested, from the notebook. Quoted so the comparison is explicit.
MMFF_OOP = {1: 964.9, 2: 854.8, 3: 793.8, 4: 764.1}

# Bay penalty PER CLASS from the MMFF run (bay-free mean minus with-bay mean).
# Per class, not pooled: the two runs cover different molecule sets, so a pooled
# average would compare different mixtures and attribute the difference to physics.
MMFF_BAY_BY_CLASS = {2: 857.7 - 842.1, 3: 800.5 - 790.5, 4: 768.5 - 760.4}

# --------------------------------------------------------------------- constants

_HARTREE_J = 4.3597447222071e-18
_BOHR_M = 5.29177210903e-11
_AMU_KG = 1.66053906660e-27
_C_CMS = 2.99792458e10
BOHR_TO_ANG = _BOHR_M * 1e10

# nu[cm^-1] = K_AU * sqrt(lambda), lambda in Hartree / (bohr^2 amu)
K_AU = np.sqrt(_HARTREE_J / (_BOHR_M**2 * _AMU_KG)) / (2.0 * np.pi * _C_CMS)


# ------------------------------------------------------------------- geometry in

def rdkit_molecule(name, smiles, expect):
    """Same construction as the MMFF notebook, so atom ordering is identical."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"{name}: SMILES did not parse")
    mol = Chem.AddHs(mol)

    n_c = sum(1 for a in mol.GetAtoms() if a.GetSymbol() == "C")
    n_h = sum(1 for a in mol.GetAtoms() if a.GetSymbol() == "H")
    if (n_c, n_h) != expect:
        raise ValueError(f"{name}: built C{n_c}H{n_h}, expected C{expect[0]}H{expect[1]}")

    params = AllChem.ETKDGv3()
    params.randomSeed = SEED
    if AllChem.EmbedMolecule(mol, params) != 0:
        raise RuntimeError(f"{name}: embedding failed")
    AllChem.MMFFOptimizeMolecule(mol, maxIters=20000)  # cheap head start for the SCF
    return mol


def psi4_geometry(mol):
    """XYZ block in RDKit atom order, with reorientation disabled so indices survive."""
    conf = mol.GetConformer()
    lines = [
        f" {a.GetSymbol()} {p.x:14.8f} {p.y:14.8f} {p.z:14.8f}"
        for a, p in ((a, conf.GetAtomPosition(a.GetIdx())) for a in mol.GetAtoms())
    ]
    lines += ["symmetry c1", "no_reorient", "no_com"]
    return psi4.geometry("\n".join(lines) + "\n")


# ------------------------------------------------------------------- vibrations

def rigid_body_projector(masses, coords):
    n = len(masses)
    msqrt = np.sqrt(masses)
    com = (masses[:, None] * coords).sum(axis=0) / masses.sum()
    rel = coords - com

    basis = np.zeros((6, 3 * n))
    for axis in range(3):
        basis[axis, axis::3] = msqrt
    for axis in range(3):
        unit = np.zeros(3)
        unit[axis] = 1.0
        basis[3 + axis] = (msqrt[:, None] * np.cross(unit, rel)).ravel()

    left, sing, _ = np.linalg.svd(basis.T, full_matrices=False)
    keep = left[:, sing > 1e-8]
    return np.eye(3 * n) - keep @ keep.T


def mass_weighted(hess_au, masses, coords_bohr):
    msqrt = np.repeat(np.sqrt(masses), 3)
    hmw = hess_au / np.outer(msqrt, msqrt)
    proj = rigid_body_projector(masses, coords_bohr)
    return proj @ hmw @ proj


def frequencies(hmw):
    eigvals, eigvecs = np.linalg.eigh(hmw)
    return np.sign(eigvals) * K_AU * np.sqrt(np.abs(eigvals)), eigvecs


# ------------------------------------------------------------- local CH analysis

def ch_pairs(mol):
    pairs = []
    for atom in mol.GetAtoms():
        if atom.GetSymbol() != "H":
            continue
        nbrs = atom.GetNeighbors()
        if len(nbrs) == 1 and nbrs[0].GetSymbol() == "C":
            pairs.append((nbrs[0].GetIdx(), atom.GetIdx()))
    return sorted(pairs)


def local_basis(pairs, coords, masses, direction):
    """Mass-weighted, COM-preserving local CH displacements.

    direction(i_c, i_h) returns the unit vector the hydrogen moves along:
    the bond axis for a stretch, the molecular normal for an out-of-plane wag.
    """
    n = len(masses)
    basis = np.zeros((3 * n, len(pairs)))
    for col, (i_c, i_h) in enumerate(pairs):
        u = direction(i_c, i_h)
        m_c, m_h = masses[i_c], masses[i_h]
        vec = np.zeros(3 * n)
        vec[3 * i_h:3 * i_h + 3] = np.sqrt(m_h) * u * (m_c / (m_c + m_h))
        vec[3 * i_c:3 * i_c + 3] = -np.sqrt(m_c) * u * (m_h / (m_c + m_h))
        basis[:, col] = vec / np.linalg.norm(vec)
    return basis


def coupling_cm(block):
    """Local frequencies and pairwise couplings, both in cm^-1."""
    nu = K_AU * np.sqrt(np.abs(np.diag(block)))
    coup = K_AU**2 * block / (nu[:, None] + nu[None, :])
    np.fill_diagonal(coup, 0.0)
    return nu, coup


def adjacency_runs(mol, pairs):
    index = {c: k for k, (c, _) in enumerate(pairs)}
    carbons = set(index)
    seen, runs = set(), []
    for start in index:
        if start in seen:
            continue
        component, stack = [], [start]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            component.append(node)
            for nb in mol.GetAtomWithIdx(node).GetNeighbors():
                if nb.GetIdx() in carbons and nb.GetIdx() not in seen:
                    stack.append(nb.GetIdx())
        runs.append([index[c] for c in sorted(component)])
    return runs


def bay_members(mol, pairs, coords_ang):
    topo = Chem.GetDistanceMatrix(mol)
    flagged = set()
    for k, (c_k, h_k) in enumerate(pairs):
        for l, (c_l, h_l) in enumerate(pairs):
            if k >= l or topo[c_k, c_l] < 3:
                continue
            if np.linalg.norm(coords_ang[h_k] - coords_ang[h_l]) < BAY_HH_ANG:
                flagged.update((k, l))
    return flagged


def perplexity(weights):
    w = np.asarray(weights, dtype=float)
    w = w[w > 0]
    if w.size == 0:
        return 0.0
    w = w / w.sum()
    return float(np.exp(-np.sum(w * np.log(w))))


# ------------------------------------------------------------------ one molecule

def run_molecule(name, smiles, expect, n_bays):
    mol = rdkit_molecule(name, smiles, expect)
    pmol = psi4_geometry(mol)

    if [a.GetSymbol() for a in mol.GetAtoms()] != [pmol.symbol(i) for i in range(pmol.natom())]:
        raise RuntimeError(f"{name}: atom order diverged between RDKit and Psi4")

    t0 = time.perf_counter()
    try:
        psi4.optimize(FUNCTIONAL, molecule=pmol)
    except psi4.OptimizationConvergenceError:
        # Triphenylene's three bays make the internal-coordinate step ill-behaved;
        # Cartesian coordinates converge it where redundant internals stall.
        psi4.core.clean()
        psi4.set_options({"opt_coordinates": "cartesian", "geom_maxiter": 300})
        psi4.optimize(FUNCTIONAL, molecule=pmol)
        psi4.set_options({"opt_coordinates": "internal", "geom_maxiter": 200})
    t_opt = time.perf_counter() - t0

    t0 = time.perf_counter()
    hess = np.array(psi4.hessian(FUNCTIONAL, molecule=pmol))
    t_hess = time.perf_counter() - t0

    coords_bohr = np.array(pmol.geometry())
    coords_ang = coords_bohr * BOHR_TO_ANG
    masses = np.array([pmol.mass(i) for i in range(pmol.natom())])

    hmw = mass_weighted(hess, masses, coords_bohr)
    nu_all, _ = frequencies(hmw)

    pairs = ch_pairs(mol)
    bays = bay_members(mol, pairs, coords_ang)

    def bond_axis(i_c, i_h):
        u = coords_ang[i_h] - coords_ang[i_c]
        return u / np.linalg.norm(u)

    centred = coords_ang - coords_ang.mean(axis=0)
    _, sing, vt = np.linalg.svd(centred)
    normal, flatness = vt[2], float(sing[2])

    v_str = local_basis(pairs, coords_ang, masses, bond_axis)
    v_oop = local_basis(pairs, coords_ang, masses, lambda c, h: normal)
    nu_str, coup_str = coupling_cm(v_str.T @ hmw @ v_str)
    w_oop = v_oop.T @ hmw @ v_oop
    nu_oop, coup_oop = coupling_cm(w_oop)

    runs = []
    for run in adjacency_runs(mol, pairs):
        block = w_oop[np.ix_(run, run)]
        eigvals, eigvecs = np.linalg.eigh(block)
        bright = int(np.argmax(np.abs(eigvecs.sum(axis=0))))
        runs.append(dict(
            size=len(run),
            bay=bool(bays & set(run)),
            nu0=float(nu_oop[run].mean()),
            beta=(float(K_AU**2 * block[0, 1] / (2 * nu_oop[run[0]]))
                  if len(run) > 1 else None),
            bright=float(K_AU * np.sqrt(abs(eigvals[bright]))),
        ))

    topo = Chem.GetDistanceMatrix(mol)
    decay = [
        dict(bonds=int(topo[pairs[k][0], pairs[l][0]]), coupling=abs(float(coup_str[k, l])))
        for k in range(len(pairs)) for l in range(k + 1, len(pairs))
    ]

    return dict(
        molecule=name, n_c=expect[0], n_h=expect[1], n_bays_expected=n_bays,
        functional=FUNCTIONAL, basis=BASIS,
        seconds_optimize=t_opt, seconds_hessian=t_hess,
        planarity_residual_ang=flatness,
        n_imaginary=int(np.sum(nu_all < -1.0)),
        n_near_zero=int(np.sum(np.abs(nu_all) < 1.0)),
        frequencies_cm=[float(x) for x in np.sort(nu_all)],
        ch_stretch_local_cm=[float(x) for x in nu_str],
        ch_oop_local_cm=[float(x) for x in nu_oop],
        stretch_perplexity=1.0 + float(np.mean([perplexity(np.abs(r)) for r in coup_str])),
        stretch_decay=decay,
        oop_runs=runs,
    )


# ------------------------------------------------------------------- the report

def report(results):
    print("\n" + "=" * 72)
    print("DFT RESULT  --  B3LYP/6-31G*")
    print("=" * 72)

    print("\nVALIDATION (a Hessian at a non-stationary point is not a spectrum)")
    print(f"{'molecule':<14}{'imaginary':>11}{'near-zero':>11}{'planarity':>12}{'opt':>8}{'hessian':>10}")
    print("-" * 66)
    for r in results:
        print(f"{r['molecule']:<14}{r['n_imaginary']:>11}{r['n_near_zero']:>11}"
              f"{r['planarity_residual_ang']:>12.1e}"
              f"{r['seconds_optimize'] / 60:>7.1f}m{r['seconds_hessian'] / 60:>9.1f}m")
    bad = [r["molecule"] for r in results if r["n_imaginary"] > 0 or r["n_near_zero"] != 6]
    print("\n  clean" if not bad else f"\n  NOT A MINIMUM: {bad} -- their numbers below are void")

    print("\n\nSTRETCH COUPLING DECAY, worst case by C-C separation (cm^-1)")
    seps = sorted({d["bonds"] for r in results for d in r["stretch_decay"]})
    print(f"{'molecule':<14}" + "".join(f"{s:>9}" for s in seps))
    print("-" * (14 + 9 * len(seps)))
    for r in results:
        line = f"{r['molecule']:<14}"
        for s in seps:
            vals = [d["coupling"] for d in r["stretch_decay"] if d["bonds"] == s]
            line += f"{max(vals):>9.2f}" if vals else f"{'-':>9}"
        print(line)

    print("\nEffective neighbours (perplexity, threshold-free):")
    for r in results:
        print(f"  {r['molecule']:<14} N_C={r['n_c']:>3}   {r['stretch_perplexity']:.2f}")

    runs = [run | {"molecule": r["molecule"]} for r in results for run in r["oop_runs"]]
    by_class = {}
    for run in runs:
        by_class.setdefault(run["size"], []).append(run)

    print("\n\nTEST 1 -- the CH out-of-plane ladder")
    print(f"{'class':>9}{'n':>4}{'DFT':>10}{'MMFF':>10}{'literature':>12}{'DFT-lit':>10}")
    print("-" * 55)
    for size in sorted(by_class):
        vals = [r["bright"] for r in by_class[size]]
        lit, mmff = LITERATURE_OOP.get(size), MMFF_OOP.get(size)
        print(f"{CLASS_NAME[size]:>9}{len(vals):>4}{np.mean(vals):>10.1f}"
              f"{(f'{mmff:.1f}' if mmff else '-'):>10}"
              f"{(f'{lit:.0f}' if lit else '-'):>12}"
              f"{(f'{np.mean(vals)-lit:+.0f}' if lit else '-'):>10}")

    print("\n\nTEST 2 -- does a motif transfer between host molecules?")
    print("A group spanning only one molecule is symmetry-equivalent copies, not a")
    print("transfer test, and is marked VOID however small its spread.\n")
    print(f"{'class':>9}{'group':>11}{'n':>4}{'hosts':>7}{'mean':>9}{'spread':>9}   verdict")
    print("-" * 69)
    for size in sorted(by_class):
        for label, subset in (("bay-free", [r for r in by_class[size] if not r["bay"]]),
                              ("with bay", [r for r in by_class[size] if r["bay"]])):
            if not subset:
                continue
            vals = np.array([r["bright"] for r in subset])
            hosts = len({r["molecule"] for r in subset})
            spread = float(np.ptp(vals))
            if hosts < 2:
                verdict = "VOID -- one host only"
            elif spread < TOLERANCE_CM:
                verdict = "transfers"
            else:
                verdict = "EXCEEDS TOLERANCE"
            print(f"{CLASS_NAME[size]:>9}{label:>11}{len(vals):>4}{hosts:>7}"
                  f"{vals.mean():>9.1f}{spread:>9.1f}   {verdict}")

    print("\n\nTEST 3 -- THE ONE THAT DECIDES IT: the bay penalty, class by class")
    print("Pooling classes would compare different molecule mixtures between the two")
    print("runs and blame the difference on electrons. So: like for like only.\n")
    print(f"{'class':>9}{'bay-free':>10}{'with bay':>10}{'DFT':>9}{'MMFF':>9}{'change':>9}")
    print("-" * 56)
    comparable = []
    for size in sorted(by_class):
        free = [r["bright"] for r in by_class[size] if not r["bay"]]
        bayed = [r["bright"] for r in by_class[size] if r["bay"]]
        if not (free and bayed):
            continue
        dft_pen = float(np.mean(bayed) - np.mean(free))
        mmff_pen = -MMFF_BAY_BY_CLASS.get(size, np.nan)
        comparable.append((size, dft_pen, mmff_pen))
        print(f"{CLASS_NAME[size]:>9}{np.mean(free):>10.1f}{np.mean(bayed):>10.1f}"
              f"{dft_pen:>+9.1f}{mmff_pen:>+9.1f}{dft_pen - mmff_pen:>+9.1f}")

    if comparable:
        changes = [abs(d - m) for _, d, m in comparable if np.isfinite(m)]
        print(f"\n  largest like-for-like change on adding electrons: {max(changes):.1f} cm^-1")
        if max(changes) < 5.0:
            print("  The penalty survived. The bay effect is MECHANICAL, and the atlas fix")
            print("  is simply that bays are their own motifs.")
        else:
            print("  The penalty moved. Electrons contribute to the bay, so it is not")
            print("  merely a steric clash and locality is weaker than MMFF said.")
        print(f"\n  Classes with both a bay-free and a bay-bearing run: {len(comparable)}.")
        if len(comparable) < 2:
            print("  One class is one data point. This does not yet separate the two")
            print("  explanations; triphenylene (3 bays) is what would.")
    else:
        print("  No class contained both a bay-free and a bay-bearing run: nothing to compare.")

    print("\n" + "=" * 72)


# -------------------------------------------------------------------------- main

def main():
    RESULTS.mkdir(exist_ok=True)
    psi4.set_output_file(str(RESULTS / "psi4.log"), False)  # be_quiet() needs /dev/null
    psi4.set_memory(f"{MEMORY_GB} GB")
    psi4.set_num_threads(THREADS)
    psi4.set_options({"scf_type": "df", "basis": BASIS,
                      "g_convergence": "gau", "geom_maxiter": 200})

    print(f"{FUNCTIONAL.upper()}/{BASIS}, {THREADS} threads, {MEMORY_GB} GB")
    print(f"results -> {RESULTS}\n")

    results = []
    for name, smiles, expect, n_bays in MOLECULES:
        path = RESULTS / f"{name}.json"
        if path.exists():
            print(f"{name:<14} cached")
            results.append(json.loads(path.read_text(encoding="utf-8")))
            continue

        print(f"{name:<14} running ...", end=" ", flush=True)
        started = time.perf_counter()
        try:
            data = run_molecule(name, smiles, expect, n_bays)
        except Exception as exc:
            print(f"FAILED after {(time.perf_counter()-started)/60:.1f}m: {type(exc).__name__}: {exc}")
            psi4.core.clean()
            continue
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"done in {(time.perf_counter()-started)/60:.1f}m "
              f"({data['n_imaginary']} imaginary)")
        results.append(data)
        psi4.core.clean()

    if results:
        report(results)
    else:
        print("\nNothing completed.")


if __name__ == "__main__":
    main()
