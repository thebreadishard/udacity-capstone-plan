"""Shared fixtures: paths to the committed probe results used as ijk sets, and a model molecule for synthetic tests."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
PROBES = PLAN / "probes"
RESULTS_VPT2 = PROBES / "results_vpt2"

WATER_CACHE = RESULTS_VPT2 / "cache_water_testA"  # 7 psi4 B3LYP/6-31G* FD Hessians, step 0.05 (16 Sep 2026)
WATER_PYVPT2_JSON = RESULTS_VPT2 / "water_b3lyp_631gs_vpt2.json"  # pyVPT2 0.1.2 on the same Hessians
BENZENE_T2_DIR = RESULTS_VPT2 / "pyscf_hessians_d005_grid99_590"  # 61 analytic pyscf Hessians, step 0.05 (21 Sep 2026)
BENZENE_T2_NPZ = RESULTS_VPT2 / "qff_benzene_pyscf_analytic_2026-09-21.npz"  # the probe's arrays for that set (aligned analysis)


def _need(path: Path) -> Path:
    """Data tests skip on a machine without the committed results — except where DPIR_REQUIRE_DATA is set (CI), where a
    missing set is a failure, so that the suite can never be green vacuously (second-reader review, 21 Sep 2026)."""
    if not path.exists():
        if os.environ.get("DPIR_REQUIRE_DATA"):
            pytest.fail(f"required data set missing: {path}")
        pytest.skip(f"data not present: {path}")
    return path


@pytest.fixture
def water_cache() -> Path:
    return _need(WATER_CACHE)


@pytest.fixture
def water_pyvpt2() -> dict:
    import json

    with open(_need(WATER_PYVPT2_JSON), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def benzene_t2_dir() -> Path:
    return _need(BENZENE_T2_DIR)


@pytest.fixture
def benzene_t2_npz() -> dict:
    return dict(np.load(_need(BENZENE_T2_NPZ)))


@pytest.fixture
def model_molecule():
    """Four atoms, non-planar, fixed seed: symbols, geometry (bohr, flat) and masses in m_e."""
    from dpir.qff import atomic_masses_me

    rng = np.random.default_rng(7)
    symbols = ["C", "H", "H", "O"]
    geom = rng.normal(scale=1.5, size=(4, 3)).ravel()
    return symbols, geom, atomic_masses_me(symbols), rng
