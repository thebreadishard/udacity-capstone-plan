# The pipeline's first version — build note

29 October 2026. Decision 64, TASKS 146 (the user: 'Schrijf de bouwnotitie voor de pijplijn maar alvast'). Built after the CCX53's end
(≈ 9–10 Nov) and the conclusions of the runs that wait on it; demonstrated at the supervisor meeting (Wed 25 Nov, pencilled) as it stands.

## What the first version does

One neutral, closed-shell aromatic molecule in (SMILES or xyz), its infrared spectrum out — band positions and heights — with the accuracy
stated per band family from recorded reads, on the laptop alone. A molecule the carried network was not trained for (an element or charge
outside its training set, read from its record) is refused with the reason, as module 08's officer refuses today. Today module 08 answers
from recorded runs (the replay worker); this version computes a molecule that has never been computed.

## The steps and the code each runs

| # | step | code | state |
|---|---|---|---|
| 1 | start geometry from SMILES (or the given xyz) | rdkit ETKDG, system Python | new: a few lines |
| 2 | B3LYP/6-31G* optimisation, the corpus deck | `corpus/psi4_worker.py` with `"hessians": false` (lever 5's route), the Windows conda env `qc` (psi4 1.11, the deck's own engine) | exists; checked 29 Oct: corpus benzene re-optimised from its stored start geometry, largest coordinate difference 4.8e-7 bohr |
| 3 | cheap level: analytic B3LYP Hessian and APT | `corpus/analytic_hessians.py` (route `hessian_response_refined`), WSL `~/qc05` (pyscf 2.14.0) | exists; new: a B3LYP-only switch (it computes ωB97X too, which is the training label, not an input) |
| 4 | the learned correction ΔH | the carried ΔH network (`modules/MODELS.md`: v1.3, three seeds, read-only files) | new: an inference loader — `rungC_train.molecule_tensors` needs the truth `dH_true` today |
| 5 | spectrum: H_low + ΔH → positions; heights from the B3LYP APT (double harmonic); broadened | `m08/spectrum.series(hessian, masses, apt, H=...)` | exists |
| 6 | the certificate: spectrum, per-family error, the seeds' spread, rung, price (laptop hours), provenance, versions | `m08/certify.py` (reads the website export today); `src/dpir/provenance.py` | new: certify a live result |

Beside every spectrum, as the baseline only: the scaled B3LYP spectrum (PAHdb's factor). The positions are harmonic: the anharmonic shift
(S1/S2, TASKS 53) is not in the first version, and the certificate says so.

## Build order

1. **The inference loader**, with a regression test first: on a corpus molecule, the new path's ΔH equals the training path's predictor
   to the bit, for each of v1.3's seeds.
2. **The B3LYP-only switch** in `analytic_hessians.py`, with a test that the B3LYP files are unchanged to the bit.
3. **`m08/pipeline.py`**: one function per step, its settings one validated config object, refusals before any computation.
4. **A live certificate** in `m08/certify.py`, with a test on a recorded molecule against its export certificate.
5. **`modules/PIPELINE.md`** (the version, below) and **`modules/08_industry_synthesis/PIPELINE_BACKLOG.md`**.
6. **The demo runs**, timed: a hold-out molecule against its ωB97X truth and the baseline; benzene or naphthalene against its CC anchor and
   experiment; one molecule outside the corpus (module 06's fixed-seed candidate, if it passes step 1's checks). Large ones are computed
   before the meeting and shown from their certificate; a small one runs live.

Steps 1 and 2 are built (29 Oct 11:4x, branch pipeline-v01, 69e040a1); nothing here needs a rented machine.

## The version

`modules/PIPELINE.md`, beside `MODELS.md`: one line per version — number, date, the network version it carries, the commit, each step's
settings, the demo's certificates. **v0.1** is the first that runs end to end. A step's change raises the minor number; a change of what
goes in or comes out raises the major; v1.0 is the version submitted with module 08. A new network version is a new pipeline version.

## The backlog

One line per action item: what, why (the evidence that asks for it), the TASKS row, before or after the demo. To start with:

- anharmonic shifts on the positions (TASKS 53); cations and other open-shell molecules (TASKS 98, 121);
- the geometry without psi4, pyscf + geomeTRIC, after a check that it gives the same Hessian and network read (TASKS 73);
- v1.4 if chain 44 carries it (TASKS 129); the reach beyond ≈ 40 atoms (chain 42, TASKS 49);
- the CC anchors' fine-tune, after November's anchor decision ('Waiting'; TASKS 82, 145);
- the laptop's Hessian time for large molecules; promotion into `src/dpir` and the product repository (TASKS 73).
