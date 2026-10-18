"""Per-mode features for S2's search (amendment 2 §3, 18 Oct 2026), from what a cheap harmonic calculation gives: the geometry, the
mass-weighted normal modes and the harmonic frequencies — never the cubic or quartic constants, which the target molecules will not have.

Local environment (shares of the mode's kinetic energy, each in [0, 1]):
- the hydrogens by their C–H adjacency class: the number of hydrogen-bearing ring carbons in the connected run that holds the hydrogen's
  carbon (solo 1, duo 2, trio 3, quartet 4, five or more), and class 0 for hydrogens not on a ring carbon;
- the fusion atoms (in two or more rings), the heteroatoms (N, O) with their hydrogens, and the substituent atoms (in no ring).
Resonance proximity, from ω alone: the smallest |2ω_j − ω_i| and |ω_j + ω_k − ω_i| over the other modes, as log10(1 + Δ/cm⁻¹).
"""
import numpy as np

COVALENT_RADIUS = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "S": 1.05, "Cl": 1.02}   # Å (Cordero et al. 2008)
BOND_TOLERANCE = 1.2
BOHR_PER_ANGSTROM = 1.8897261246
ADJACENCY_CLASSES = (0, 1, 2, 3, 4, 5)        # 5 = five or more
HETERO = ("N", "O")
LOCAL_NAMES = [f"h_class_{c}" for c in ADJACENCY_CLASSES] + ["fusion", "hetero", "substituent"]
PROXIMITY_NAMES = ["prox_overtone", "prox_combination"]


def bonds(symbols, coords_bohr):
    """Bonded atom pairs by covalent radii (distance below BOND_TOLERANCE × the sum)."""
    x = np.asarray(coords_bohr, float) / BOHR_PER_ANGSTROM
    r = np.array([COVALENT_RADIUS[s] for s in symbols])
    d = np.linalg.norm(x[:, None, :] - x[None, :, :], axis=2)
    lim = BOND_TOLERANCE * (r[:, None] + r[None, :])
    i, j = np.where(np.triu(d < lim, 1))
    return list(zip(i.tolist(), j.tolist(), strict=True))


def ring_counts(n_atoms, bond_list):
    """Per atom, the number of smallest rings (RDKit's symmetrised SSSR on the bond graph) that contain it."""
    from rdkit import Chem
    mol = Chem.RWMol()
    for _ in range(n_atoms):
        mol.AddAtom(Chem.Atom(6))
    for i, j in bond_list:
        mol.AddBond(i, j, Chem.BondType.SINGLE)
    m = mol.GetMol()
    m.UpdatePropertyCache(strict=False)
    counts = np.zeros(n_atoms, int)
    for ring in Chem.GetSymmSSSR(m):
        counts[list(ring)] += 1
    return counts


def hydrogen_classes(symbols, bond_list, rings):
    """Per atom: for a hydrogen, its C–H adjacency class (0 when its carbon is in no ring; capped at 5); −1 for every other atom."""
    sym = np.array(symbols)
    n = len(sym)
    nbr = [[] for _ in range(n)]
    for i, j in bond_list:
        nbr[i].append(j)
        nbr[j].append(i)
    carbon_of = {h: next((a for a in nbr[h] if sym[a] == "C"), None) for h in range(n) if sym[h] == "H"}
    ring_ch = {c for c in carbon_of.values() if c is not None and rings[c] > 0}
    size = {}
    for start in ring_ch:
        if start in size:
            continue
        group, stack = set(), [start]
        while stack:
            c = stack.pop()
            if c in group:
                continue
            group.add(c)
            stack += [a for a in nbr[c] if a in ring_ch and a not in group]
        for c in group:
            size[c] = len(group)
    cls = np.full(n, -1)
    for h, c in carbon_of.items():
        cls[h] = min(size.get(c, 0), 5) if c in ring_ch else 0
    return cls


def local_environment(q, symbols, coords_bohr):
    """The local-environment shares of every mode: an (M × len(LOCAL_NAMES)) array."""
    sym = np.array(symbols)
    n = len(sym)
    bl = bonds(symbols, coords_bohr)
    rings = ring_counts(n, bl)
    cls = hydrogen_classes(symbols, bl, rings)
    a = (np.asarray(q).reshape(n, 3, -1) ** 2).sum(axis=1)          # kinetic-energy share per atom and mode
    a = a / a.sum(axis=0, keepdims=True)
    nbr_hetero = np.zeros(n, bool)
    for i, j in bl:
        nbr_hetero[i] |= sym[j] in HETERO and sym[i] == "H"
        nbr_hetero[j] |= sym[i] in HETERO and sym[j] == "H"
    hetero = np.isin(sym, HETERO) | nbr_hetero
    heavy_in_ring = rings > 0
    on_ring_atom = heavy_in_ring.copy()
    for i, j in bl:                                                   # a hydrogen belongs to its carbon's ring status
        if sym[i] == "H":
            on_ring_atom[i] = heavy_in_ring[j]
        if sym[j] == "H":
            on_ring_atom[j] = heavy_in_ring[i]
    cols = [a[cls == c].sum(axis=0) for c in ADJACENCY_CLASSES]
    cols += [a[rings >= 2].sum(axis=0), a[hetero].sum(axis=0), a[~on_ring_atom].sum(axis=0)]
    return np.stack(cols, axis=1)


def resonance_proximity(omega):
    """Per mode i: log10(1 + min_j |2ω_j − ω_i|) and log10(1 + min_{j≤k} |ω_j + ω_k − ω_i|), j, k ≠ i (cm⁻¹)."""
    w = np.asarray(omega, float)
    n = len(w)
    out = np.zeros((n, 2))
    for i in range(n):
        others = np.delete(w, i)
        out[i, 0] = np.abs(2 * others - w[i]).min()
        pair = others[:, None] + others[None, :]
        out[i, 1] = np.abs(pair[np.triu_indices(n - 1, 1)] - w[i]).min()
    return np.log10(1.0 + out)
