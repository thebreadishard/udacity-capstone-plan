# QC for philipmnel/pyvpt2#58 (30 Sep 2026, laptop WSL; the user: "If it doesn't disturb a run, sure")

Environment replicated from hel1-14's `vpt2` env: Python 3.13, psi4 1.10.2, qcelemental 0.30.1, qcengine 0.34.2, optking 0.5.0,
libxc-c pinned to 7.0.0 (conda first resolved 7.1.2, with which psi4 1.10.2 cannot build its functionals); pyVPT2 = branch
`quartic-route-consistency` (055e8c9) installed editable (`setup_env.sh`).

1. pyVPT2's suite (`pytest pyvpt2/tests`, 8 threads, nothing else running; `suite_both.log`): branch **27 passed, 10 skipped**; upstream main
   (2eae571) **24 passed, 10 skipped** — the difference is the three new tests. A first run with a psi4 job running alongside failed
   `test_h2o_multilevel.py::test_h2o_multi_vpt2[ENERGY]` at MAX 0.53 against atol 0.5 (`pytest_first_run_concurrent.log`); alone the file passes
   on the branch twice and on main once, and the clean full runs pass — a tolerance-edge test under load, not the change.
2. Real data through pyVPT2's normal path (`vpt2_benzene.py` copy in the scratchpad, output kept out of the repo; benzene B3LYP/6-31G*, the
   61 psi4 FD Hessians of 21 Sep copied read-only from hel1-14; a cache miss was made fatal): **cache hits 61, computed 0**; the new report prints
   **median 22.40 / p90 107.04 / max 1264.46 cm⁻¹**, equal to the independent `probes/qff_from_hessians.py` (22.4 / 107.0 / 1264.5), followed by
   `check_quartic`'s "No inconsistencies found". Against the unpatched 0.1.2 results of 21 Sep: ω and φ_ijk bitwise equal, φ_iijj 2.3e-10 cm⁻¹,
   ν 9.6e-11 cm⁻¹, χ 5.7e-11 cm⁻¹ (averaging the two routes instead of one combined sum).
