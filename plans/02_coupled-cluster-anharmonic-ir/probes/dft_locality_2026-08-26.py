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
OOP_WINDOW = (600.0, 1000.0)   # where CH out-of-plane bands live
MIN_IR_KM_MOL = 1.0            # below this a mode is not a band anyone measures

RESULTS = Path(__file__).parent / "results_dft_locality"

# (name, SMILES, (n_C, n_H), bays) -- bay count is documentation, not used in logic
#
# ORDERED BY WHAT EACH ONE DECIDES, not by size. With IR intensities a Hessian
# costs about 2.3x a bare one, so the full set is ~11 hours and the order is the
# difference between an answer this afternoon and an answer tomorrow.
#
#   1-3  done: the three with measured NIST spectra, which fixed the method
#   4    phenanthrene  1 bay   -> re-measures the bay penalty against naphthalene
#                                 and anthracene, whose quartets are bay-free
#   5    triphenylene  3 bays  -> does the penalty scale with bay count?
#   6    chrysene      1 bay   -> second independent single-bay point
#   7-8  pyrene, tetracene     -> transfer coverage for duo/trio/solo, no bays
MOLECULES = [
    ("benzene",      "c1ccccc1",                     (6, 6),   0),
    ("naphthalene",  "c1ccc2ccccc2c1",               (10, 8),  0),
    ("anthracene",   "c1ccc2cc3ccccc3cc2c1",         (14, 10), 0),
    ("phenanthrene", "c1ccc2c(c1)ccc1ccccc12",       (14, 10), 1),
    ("triphenylene", "c1ccc2c(c1)c1ccccc1c1ccccc21", (18, 12), 3),
    ("chrysene",     "c1ccc2c(c1)ccc1c2ccc2ccccc21", (18, 12), 1),
    ("pyrene",       "c1cc2ccc3cccc4ccc(c1)c2c34",   (16, 10), 0),
    ("tetracene",    "c1ccc2cc3cc4ccccc4cc3cc2c1",   (18, 12), 0),
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

def band_from_normal_modes(run, basis, hmw):
    """Where the observable band sits, using the whole molecule rather than a frozen ring.

    The local-basis 'bright' frequency freezes every atom outside the run, and
    measurement against NIST spectra showed that throws away most of the
    molecule-to-molecule variation: naphthalene and anthracene quartets differ by
    56 cm-1 in the lab and by 6 cm-1 in the frozen model.

    So instead: build the in-phase combination of the run's local wags, and ask how
    the real normal modes carry it.

    Returns the best-matching mode, the overlap-weighted centroid, and the overlap
    itself. A low overlap means the in-phase character is smeared over many modes
    and 'the band' is not one mode at all -- which is itself worth reporting.
    """
    in_phase = basis[:, run].sum(axis=1)
    in_phase /= np.linalg.norm(in_phase)

    nu, modes = frequencies(hmw)
    overlaps = (modes.T @ in_phase) ** 2
    real = nu > 1.0
    overlaps = np.where(real, overlaps, 0.0)

    best = int(np.argmax(overlaps))
    total = overlaps.sum()
    centroid = float((overlaps * nu).sum() / total) if total > 0 else float("nan")
    return dict(
        band_best_mode=float(nu[best]),
        band_centroid=float(centroid),
        max_overlap=float(overlaps[best]),
        overlap_captured=float(total),
    )


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
    # frequency() rather than hessian(): it also produces dipole derivatives, and
    # therefore IR intensities, which is what lets the band be picked the way a
    # spectrometer picks it instead of by a hand-built assignment rule.
    _, wfn = psi4.frequency(FUNCTIONAL, molecule=pmol, return_wfn=True)
    t_hess = time.perf_counter() - t0
    hess = np.array(wfn.hessian())

    vib = wfn.frequency_analysis
    omega = np.asarray(vib["omega"].data).real
    ir_int = np.asarray(vib["IR_intensity"].data).real
    is_vib = np.asarray(vib["TRV"].data) == "V"
    spectrum = sorted(
        (float(f), float(i)) for f, i in zip(omega[is_vib], ir_int[is_vib])
        if i >= MIN_IR_KM_MOL
    )
    in_window = [(f, i) for f, i in spectrum if OOP_WINDOW[0] < f < OOP_WINDOW[1]]
    strongest = max(in_window, key=lambda t: t[1]) if in_window else (float("nan"),) * 2

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
        entry = dict(
            size=len(run),
            bay=bool(bays & set(run)),
            nu0=float(nu_oop[run].mean()),
            beta=(float(K_AU**2 * block[0, 1] / (2 * nu_oop[run[0]]))
                  if len(run) > 1 else None),
            bright=float(K_AU * np.sqrt(abs(eigvals[bright]))),
        )
        entry.update(band_from_normal_modes(run, v_oop, hmw))
        runs.append(entry)

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
        ir_spectrum=[[f, i] for f, i in spectrum],
        oop_bands=[[f, i] for f, i in in_window],
        strongest_oop_cm=strongest[0],
        strongest_oop_km_mol=strongest[1],
        ch_stretch_local_cm=[float(x) for x in nu_str],
        ch_oop_local_cm=[float(x) for x in nu_oop],
        stretch_perplexity=1.0 + float(np.mean([perplexity(np.abs(r)) for r in coup_str])),
        stretch_decay=decay,
        oop_runs=runs,
    ), dict(hessian_au=hess, coords_bohr=coords_bohr, masses_amu=masses,
            pairs=np.array(pairs))


# ------------------------------------------------------------------- the report

# Measured NIST gas-phase band positions, from verify_oop_bands_2026-08-27.py.
# These are what the calculation has to reproduce; the 890/833/787/745 set are
# interstellar feature centres, not molecular constants, and are not used here.
EXPERIMENT = {
    ("benzene", 6): 673.0,
    ("naphthalene", 4): 781.5,
    ("anthracene", 4): 725.6,
    ("anthracene", 1): 875.2,
}


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

    print("\n\nTEST 0 -- against measured spectra, band picked by IR intensity")
    print("No assignment rule: the band is the strongest absorption in the window,")
    print("which is how a spectrometer picks it too.\n")

    scale = None
    bench = [r for r in results if r["molecule"] == "benzene"]
    if bench and np.isfinite(bench[0].get("strongest_oop_cm", float("nan"))):
        # Fitted on benzene ALONE, so every other molecule below is a held-out test.
        scale = EXPERIMENT[("benzene", 6)] / bench[0]["strongest_oop_cm"]
        print(f"Harmonic scale factor fitted on benzene only: {scale:.4f}\n")

    print(f"{'molecule':<14}{'harmonic':>10}{'scaled':>9}{'experiment':>12}"
          f"{'error':>8}{'km/mol':>9}{'bands':>7}")
    print("-" * 69)
    residuals = []
    for r in results:
        band = r.get("strongest_oop_cm")
        if band is None or not np.isfinite(band):
            continue
        exp = next((v for (m, _), v in EXPERIMENT.items() if m == r["molecule"]), None)
        scaled = band * scale if scale else float("nan")
        err = f"{scaled - exp:+.1f}" if exp and scale else "-"
        if exp and scale and r["molecule"] != "benzene":
            residuals.append(scaled - exp)
        print(f"{r['molecule']:<14}{band:>10.1f}{scaled:>9.1f}"
              f"{(f'{exp:.1f}' if exp else '-'):>12}{err:>8}"
              f"{r.get('strongest_oop_km_mol', float('nan')):>9.1f}"
              f"{len(r.get('oop_bands', [])):>7}")
    if residuals:
        print(f"\n  held-out mean |error| after scaling: "
              f"{np.mean(np.abs(residuals)):.1f} cm^-1 over {len(residuals)} molecules")
        print("  Benzene is excluded: the scale factor was fitted on it, so its")
        print("  residual is zero by construction and would flatter the average.")

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

    print("\n\nTEST 3 -- THE BAY PENALTY, re-measured from the band that absorbs")
    print("The earlier -11.2 cm^-1 came from the frozen local basis, the same")
    print("discredited quantity as the withdrawn transfer claim. This is the")
    print("strongest IR band, molecule by molecule, which is what a spectrum shows.\n")
    scale_here = scale or 1.0
    print(f"{'molecule':<14}{'bays':>6}{'strongest band':>16}{'scaled':>9}{'km/mol':>9}")
    print("-" * 54)
    for r in sorted(results, key=lambda r: (r["n_bays_expected"], r["n_c"])):
        band = r.get("strongest_oop_cm")
        if band is None or not np.isfinite(band):
            continue
        print(f"{r['molecule']:<14}{r['n_bays_expected']:>6}{band:>16.1f}"
              f"{band * scale_here:>9.1f}{r.get('strongest_oop_km_mol', 0):>9.1f}")

    free = [r for r in results if r["n_bays_expected"] == 0
            and np.isfinite(r.get("strongest_oop_cm", float("nan")))]
    bayed = [r for r in results if r["n_bays_expected"] > 0
             and np.isfinite(r.get("strongest_oop_cm", float("nan")))]
    if bayed:
        print("\n  Bay-bearing molecules present. A penalty is only meaningful against")
        print("  a bay-free molecule of the SAME adjacency class and similar size,")
        print("  so read the table above rather than a single pooled number:")
        print("  naphthalene and anthracene are the bay-free quartet references.")
    else:
        print("\n  No bay-bearing molecule has finished yet, so the penalty is not")
        print("  re-measured and the old 11.2 cm^-1 figure stands WITHDRAWN, not")
        print("  replaced. Phenanthrene (1 bay) and triphenylene (3 bays) decide it.")

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
        raw = RESULTS / f"{name}.npz"
        # Both must exist: the .npz is what makes re-analysis free, and a result
        # without it would force another hour of Hessian to answer a new question.
        if path.exists() and raw.exists():
            print(f"{name:<14} cached")
            results.append(json.loads(path.read_text(encoding="utf-8")))
            continue

        print(f"{name:<14} running ...", end=" ", flush=True)
        started = time.perf_counter()
        try:
            data, arrays = run_molecule(name, smiles, expect, n_bays)
        except Exception as exc:
            print(f"FAILED after {(time.perf_counter()-started)/60:.1f}m: {type(exc).__name__}: {exc}")
            psi4.core.clean()
            continue
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        np.savez_compressed(raw, **arrays)
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
