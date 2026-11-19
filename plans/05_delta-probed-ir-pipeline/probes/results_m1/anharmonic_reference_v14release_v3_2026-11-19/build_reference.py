"""The stored-field reference of benzene rebuilt on the run of 19 Nov 2026 (TASKS 255, 211).

    python build_reference.py --out <folder>

The reference that `../anharmonic_step_2026-11-17/first_run_checks.py` reads by default
(`../anharmonic_step_2026-11-16/stored_field_demo/benzene`) was built on a pipeline result of 3 Nov whose steps 4-5 ran ΔH network
v1.3, with artefact format 2. The run of 19 Nov (`../pipeline_benzene_anharmonic_v3_2026-11-19/benzene`) ran v1.4's release networks
and format 3, so its corrected harmonic positions differ by up to 2.30 cm-1 and the checks refuse to compare. This script runs the same
code as `stored_field_demo.py` (one stand-in: S2's stored GFN2-xTB force field rotated onto the pipeline's frame) on a copy of the
run's own steps 1-5 files instead of the 3 Nov result. The two results then differ in one thing only, the force field, which is what
the checks were written to compare. The tolerances of the checks are not touched.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "anharmonic_step_2026-11-16"))
import stored_field_demo as SFD  # noqa: E402

RUN = "probes/results_m1/pipeline_benzene_anharmonic_v3_2026-11-19/benzene"

if __name__ == "__main__":
    SFD.RESULT = RUN      # the only change against stored_field_demo.py: the run's own steps 1-5 as the base
    sys.exit(SFD.main())
