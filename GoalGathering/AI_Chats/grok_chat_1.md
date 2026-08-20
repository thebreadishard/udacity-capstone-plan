# Quantum Computing for IR Spectra of Aromatic Molecules

Source: https://grok.com/share/c2hhcmQtNQ_b705d630-1541-4501-bdfb-decfa6b1f156

---

### You said

You are a quantum chemistry professor. Just for the sake of argument, you want to try and predict the infrared spectral lines of aromatic molecules using quantum computing in its current state. How far could you get?

### Grok said

Not very far for a full, quantitative, chemically useful prediction of the infrared spectrum of a typical aromatic molecule—but farther than many people assume, particularly if we focus on anharmonic effects and carefully chosen reduced models.

As a quantum chemistry professor, I would frame the problem this way. Predicting IR spectral lines means computing vibrational transition frequencies and intensities. In the harmonic approximation this reduces to the nuclear Hessian (second derivatives of the electronic energy) plus dipole derivatives at a stationary point. For accurate band positions and intensities—especially overtones, combination bands, and systems with strong mode coupling or large-amplitude motion—we need anharmonic treatments (VPT2, variational vibrational methods, or explicit quantum nuclear dynamics on a multi-dimensional potential energy surface). Aromatic molecules (benzene and larger) have 30+ vibrational modes, making the full anharmonic problem high-dimensional.

#### Current quantum computing landscape (2025–2026)

Quantum hardware remains firmly in the NISQ regime or early logical-qubit experiments. Useful chemistry algorithms are mostly hybrid variational methods (VQE and variants), quantum phase estimation resource estimates for fault-tolerant devices, and specialized photonic or ion-trap demonstrations.

Two routes exist:

1. **Electronic-structure route to the PES/Hessian.** Analytic second derivatives within a VQE framework have been demonstrated and match full configuration interaction for small systems. Geometry optimization and harmonic frequencies are therefore possible in principle. However, for a realistic aromatic the electronic problem itself is already large. Benzene has 42 electrons; even a modest active space quickly exceeds what noisy devices can handle with chemical accuracy without heavy classical assistance or fragmentation. Hybrid quantum-centric supercomputing has pushed electronic properties of much larger systems (thousands of atoms via fragmentation), but that is not the same as a high-accuracy, fully quantum nuclear Hessian for an aromatic.

2. **Direct vibrational (bosonic) route.** This is more promising for eventual advantage. The vibrational Hamiltonian is bosonic; encodings into qubits exist, and the operator structure is often more local with fewer Pauli terms than the electronic Hamiltonian. Variational algorithms (unitary vibrational coupled-cluster and compact heuristic circuits), Trotterized time evolution, grid-based split-operator methods, and qubitization have all been developed for vibrational energies, spectra, and dynamics.

Concrete results include:

- Accurate harmonic and low-lying anharmonic levels for small molecules (H₂O, CO₂, CH₄ with 9 modes, formic acid, etc.).
- Resource estimates showing that an anharmonic 12-mode molecule (e.g., azidoacetylene for near-IR) can be treated with on the order of 170 logical qubits and ~10⁸–10⁹ T-gates under optimized algorithms.
- Photonic quantum chips that have simulated vibronic spectra (Franck–Condon factors under Condon or limited non-Condon approximations) for selected modes of formic acid, thymine, and even benzene/naphthalene-type systems.
- Classical emulations and early hardware runs of time-dependent dipole autocorrelation functions that recover fundamentals, overtones, and combination bands for water-like models.

Resource estimates for fault-tolerant algorithms now reach molecules with ~100 vibrational modes under two- and three-mode coupling approximations, with 1 cm⁻¹ resolution as a target. Mode localization and tensor decompositions help keep the cost manageable.

#### What this means for aromatic molecules

- **Harmonic IR spectrum of benzene or a substituted aromatic:** Classical DFT (or even good semi-empirical/ML potentials) is faster, cheaper, and already accurate enough for most practical purposes after empirical scaling. Quantum computing adds nothing competitive today.
- **Selected-mode anharmonic treatment:** Feasible as a demonstration. One can freeze most modes, keep a chemically relevant subspace (CH stretches, ring-breathing modes, out-of-plane bends that couple strongly), generate a high-quality PES classically or with a hybrid method, and solve the vibrational problem quantumly. Photonic and gate-based experiments have already touched benzene modes under approximations. Intensities via dipole surfaces are harder but algorithmically addressed.
- **Full anharmonic spectrum with extensive mode coupling:** Still out of reach on present hardware for a quantitative prediction that improves on the best classical variational or VPT2 calculations. Classical specialized methods have computed hundreds of thousands of vibrational states of benzene itself. Quantum methods shine when the classical exponential wall is hit hard—strong multimode anharmonicity, large-amplitude motions, or the need for many highly excited states—but current qubit counts, gate fidelities, and measurement overheads limit us to reduced models.
- **Vibronic spectra** (relevant if one is thinking of the vibrational structure that accompanies electronic transitions): Photonic boson-sampling-style approaches have produced proof-of-principle results for aromatic chromophores under harmonic or limited anharmonic models. These are closer to experimental vibronic band shapes than pure IR work, but still heavily approximated.

#### Realistic near-term workflow I would actually try

Generate a high-quality PES (or property surfaces) with classical electronic structure or modern ML potentials, map a reduced set of important modes onto a vibrational Hamiltonian that includes cubic/quartic couplings, encode it, and run a variational or short-time dynamical simulation on the best available quantum hardware (or a high-fidelity classical emulator of that hardware). Extract frequencies and intensities from the resulting eigenvalues or dipole autocorrelation function. Error mitigation, symmetry adaptation, and active-space/mode selection are essential. The result would be a scientifically interesting benchmark or a modestly improved description of a few key bands, not a replacement for a well-run classical anharmonic calculation of the full spectrum.

#### Bottom line

In its current state, quantum computing lets us explore algorithms, validate reduced models of aromatic vibrations, and produce high-quality results for systems of roughly 5–12 modes with controlled anharmonicity. It does not yet deliver a practical, full IR spectrum of a real aromatic molecule that is more accurate or useful than what classical quantum chemistry already provides routinely. The vibrational problem is widely regarded as a more favorable early target for quantum advantage than the electronic structure problem, so the trajectory is encouraging. With continued progress toward logical qubits and better encodings, molecules the size of benzene or naphthalene in a chemically relevant reduced-dimensional anharmonic treatment could become realistic within the next generation of fault-tolerant machines. Until then, the intellectually honest answer is: we can get far enough to write interesting papers and train the next generation of methods, but not far enough to retire the classical codes.

*(75 sources cited in the original conversation)*
