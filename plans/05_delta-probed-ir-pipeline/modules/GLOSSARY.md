# Glossary for readers without chemistry or astrophysics

*One line per term, written for the school's reviewer (4 October 2026). The module READMEs, notebooks and reports link here; where a term first
appears in a module it is also explained in place.*

**Molecule, PAH.** A molecule is a small group of atoms bound together. A polycyclic aromatic hydrocarbon (PAH) is a flat molecule of carbon rings
with hydrogen atoms on the rim, like a tiny piece of graphene — the family this project is about. Benzene (one ring), naphthalene (two) and anthracene
(three) are the smallest.

**Infrared spectrum, band, position, intensity.** Molecules vibrate, and each vibration absorbs or emits infrared light at one colour. A spectrum is
the list of those colours with their strengths; one entry is a *band*. Its *position* is the colour, its *intensity* the strength (how bright).
Astronomers see these bands coming from space and use them to tell which molecules are out there.

**cm⁻¹ and µm.** Two units for the colour (position) of a band. Wavenumbers (cm⁻¹) are the spectroscopist's unit: larger means bluer; 3,000 cm⁻¹ is
the C–H stretch, 700 cm⁻¹ a slow rocking of the whole ring. Micrometres (µm) are the astronomer's unit: 3.3 µm equals 3,000 cm⁻¹. One cm⁻¹ is a
very small shift; the computed spectra in this project are off by tens of cm⁻¹, and the goal is to bring that to a few.

**Vibration (mode), family.** A mode is one way the molecule can vibrate. Modes come in families named after the motion: C–H stretch (a hydrogen
moving in and out), C–H in-plane or out-of-plane bend (a hydrogen moving sideways or above and below the flat molecule), ring modes (the carbon
skeleton breathing or twisting), and a rest group of soft, slow motions.

**Harmonic, anharmonic.** The simplest model of a vibration treats the molecule as balls on perfect springs (*harmonic*). Real springs stiffen or
soften when stretched (*anharmonic*); this project corrects the harmonic picture at one level of accuracy and leaves anharmonic effects to others.

**Force constant, Hessian, coupling.** The stiffness of a spring is a *force constant*. The table of all stiffnesses, including how moving one atom
tugs on another (*coupling*), is the *Hessian* (a square table, one row and column per atom coordinate). All vibration positions follow from it; a
better Hessian means better positions.

**DFT, B3LYP, ωB97X.** Density functional theory (DFT) is the cheap way of computing a molecule's properties on a computer; B3LYP and ωB97X are two
recipes within it. Cheap enough for thousands of molecules, but systematically off by tens of cm⁻¹.

**Coupled cluster, CCSD(T).** The expensive, accurate way of computing the same quantities; CCSD(T) is its standard flavour, often called the gold
standard. It costs thousands of times more than DFT and is affordable only for small molecules, which is why this project computes it for a few
molecules (the *anchors*) and learns the correction from them.

**Basis set, cc-pVDZ, cc-pVTZ, 6-31G*, 4-31G.** The size of the mathematical description a calculation uses for each atom, like the resolution of a
photo. A larger basis (cc-pVTZ) is more accurate and more expensive than a smaller one (cc-pVDZ, 6-31G*, 4-31G). Results computed in different bases are
not directly comparable.

**Scale factor.** Because the harmonic DFT positions are systematically too high, people multiply them by a number slightly below one (for example
0.97) to bring them closer to measurements. It is a patch, not a correction of the physics.

**Charge: neutral, cation, anion, dication.** A molecule can carry no electric charge (neutral), one positive charge (cation, +), one negative (anion,
−) or two positive (dication, +2). Charged PAHs have noticeably different spectra and are common in space.

**Isomers.** Molecules with the same atoms arranged differently; same formula, different molecule.

**Symmetry (point group).** How a molecule can be rotated or mirrored onto itself; a symmetric molecule needs fewer calculations.

**Hold-out, leave-one-out, scaffold.** In machine learning a *hold-out* is a set of examples kept away from training to test the model honestly.
*Leave-one-molecule-out* keeps one molecule out at a time. A *scaffold* is the ring skeleton of a molecule without its side groups; holding out whole
scaffolds tests whether the model generalises to ring systems it has never seen.

**Ladder, rungs, comparison lines.** The project's own list of test molecules from small to large (the *ladder*, each molecule a *rung*), and the
published predictions it compares itself against (*lines* A, B, C, …: the NASA library, anharmonic calculations, machine-learning predictions).

**Proxy level, CC level.** A *proxy* result compares two cheap methods with each other (DFT against DFT) to rehearse a method; a *CC-level* result
compares against the expensive, accurate calculation and is the one that counts.

**Pre-registration.** Writing down what will be computed, how it will be read and what counts as success *before* the numbers exist, so that the
outcome cannot be bent afterwards. Every experiment in this project has one.

**Network, model, version.** A *network* (neural network) is a computer program with millions of adjustable numbers that learns a mapping from examples; *training* sets those numbers, a *checkpoint* is the saved result, and a *seed* is one training run (the project trains three per recipe and reports their spread). A *version* names a recipe, not a seed: `1.x` means the network is used in the pipeline, `0.x` that it is an experiment. Four networks are trained here, each with its own list of versions (`modules/MODELS.md`):

- the **ΔH-network** (module 05): takes the cheap calculation of a molecule and predicts the correction towards the expensive one — the heart of the end product; current version 1.1;
- the **order scorer** (standout, P1): decides in which order the pieces of an expensive calculation are computed, so the most informative come first; version 1.0, in use since decision 58;
- the **learned order scorer** (standout, P2): the same task, learned from the ΔH-network's internal representation instead of hand-made features; an experiment (0.x) that has not yet beaten the hand-made one;
- the **candidate generator** (module 06): writes down new molecules worth computing next, as text strings; an experiment (0.x) outside the pipeline.
