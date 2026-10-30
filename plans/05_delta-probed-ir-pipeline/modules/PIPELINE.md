# The pipeline — versions (decision 64)

The pipeline (`08_industry_synthesis/m08/pipeline.py`) takes one molecule in, as a SMILES or an xyz file, and puts its infrared spectrum
out, with a certificate (`m08/live_certificate.py`) that states how well each band is known. It carries its own version number, beside the
networks' in `MODELS.md`. A step's change raises the minor number; a change of what goes in or comes out raises the major; a new network
version is a new pipeline version; v1.0 is the version submitted with module 08. What it still needs is in
`08_industry_synthesis/PIPELINE_BACKLOG.md`; how it was built is in `08_industry_synthesis/PIPELINE_BUILD_NOTE_2026-10-29.md` (TASKS 146).

| version | date | network | steps and settings | certificates |
|---|---|---|---|---|
| **0.1** | 29 Oct 2026 | ΔH-network v1.3 (chain 35, 3 seeds; `MODELS.md`) | 1 start geometry: RDKit ETKDG + MMFF, seed 0 (`corpus/run_corpus.start_geometry`), or the xyz given · 2 optimisation: psi4 1.11, B3LYP/6-31G*, deck v1 (sha16 9e27bf8e934893f3), no Hessian · 3 the low level: pyscf 2.14.0's analytic B3LYP Hessian and its APT (`corpus/analytic_hessians.py --functionals b3lyp`, WSL, under `probes/wsl_capped.sh`) · 4 the correction: the mean ΔH of the three seeds, each seed's kept (`correction.npz`) · 5 the spectrum: double harmonic, Lorentzian FWHM 10 cm⁻¹; the baseline only: B3LYP scaled by PAHdb's factors per region · licence: decision 65 | benzene (`probes/results_m1/pipeline_benzene_certified_2026-10-29/benzene/certificate.md`); phenanthrene, hold-out (a) (`probes/results_m1/pipeline_demo_2026-10-29/phenanthrene/`) |
| **0.2** | 30 Oct 2026 | ΔH-network v1.3 | as 0.1, but step 1 builds the start geometry from the **canonical SMILES**: the network's answer depends on the atom order (two writings of phenanthrene moved its bands by up to 2.9 cm⁻¹, rms 0.65; `probes/network_invariance_check.py`), so every writing of a molecule now reaches it in one order (TASKS 149) | phenanthrene and the module 06 candidate (`probes/results_m1/pipeline_demo_2026-10-30/`; the candidate stopped in step 5, see 0.3) |
| **0.3** | 30 Oct 2026 | ΔH-network v1.3 | as 0.2, but the seeds' modes are paired with the mean's by rank among all 3N−6 vibrational modes (the family rule's `learning_curve_layerA.normal_modes`), not among those above the 20 cm⁻¹ line of `mode_intensities`: module 06's candidate has a B3LYP rotor at 6.9 cm⁻¹ that the network lifts to 24.0 and one seed to 19.6, so the seeds' ranges (step 5) and the certificate's bands lost their pairing. The certificate seeks each band's B3LYP partner among the family rule's modes (all but the six of smallest |ω|), so a band whose B3LYP mode lies under the line keeps its family by the rule and is listed without a baseline | the module 06 candidate (`probes/results_m1/pipeline_demo_2026-10-30/`) |
| **0.4** | 30 Oct 2026 | ΔH-network v1.3 | as 0.3, but the record's provenance is taken at launch, before the first step, and the commit at the end stands beside it (`commit_at_end`): 0.3 took the commit when the run ended, and module 06's candidate, launched at fe941b7f, was recorded at 94d8981e (no code changed between them); the computed numbers are 0.3's | — |

**What v0.1 takes and refuses.** Neutral, closed-shell molecules with an aromatic ring, made of the elements the network trained on (C, H,
N, O, F, S, Cl); everything else is refused before any computation, with the reason. The network trained on molecules of 8–30 atoms; a
larger one is computed and its certificate says it is outside those sizes.

**What its certificate claims.** Positions are harmonic (no anharmonic shift yet). The correction moves B3LYP toward ωB97X/6-31G* — the
DFT proxy the network was trained on — and the error per family is measured on molecules the network never saw. Under decision 65,
ring-ip, CH-stretch and CH-oop are licensed (error within 3 cm⁻¹ on both hold-outs) and 'other' is not. Nothing is claimed at the
coupled-cluster level for v1.3.

**Its version string.** Benzene's and phenanthrene's records were written while the code said 0.1.dev, on the same step code as 0.1
(commit 54fa017e and later; the certificates were rebuilt under decision 65); from this line on the pipeline writes 0.1.
