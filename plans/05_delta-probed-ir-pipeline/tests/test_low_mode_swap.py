"""The label swap's registered criteria (TASKS 201, 14 November 2026), on synthetic label and patch files.

`GoalGathering/notes/PreRegistration_2026-11-14_Low_Mode_Label_Swap.md` with its amendment fixes what these pin: the patch's Hessian
and frequencies replace the label's while the label's own settings are carried over, the modes the patch does not target stay within
0.5 cm-1, a molecule's two labels move together or not at all, and a targeted mode that turns imaginary is accepted and counted while
an untargeted one refuses the file.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import low_mode_swap as LMS

GRID = np.array([99, 590])
VIB = np.array([40.0, 120.0, 300.0])      # three vibrational modes; the first is the one the patch targets


def write_pair(root: Path, mol_id: str, tag: str, patched_vib: np.ndarray, *, grid: np.ndarray = GRID,
               directions: int = 1) -> tuple[Path, Path]:
    """One molecule's label file and the patch beside it, with the patch moving the label's modes to `patched_vib`."""
    below_cm = 20.0
    label_dir, patch_dir = root / "molecules" / mol_id, root / "results" / mol_id
    label_dir.mkdir(parents=True, exist_ok=True)
    patch_dir.mkdir(parents=True, exist_ok=True)
    label_path = label_dir / f"hessian_{tag}_analytic.npz"
    patch_path = patch_dir / f"hessian_{tag}_analytic_grfpatch.npz"
    freq = np.concatenate([VIB, np.zeros(6)])
    np.savez(label_path, H_raw=np.eye(9), H_projected=np.eye(9), freq_cm=freq, energy=np.asarray(-1.5), grid=GRID,
             charge=np.asarray(0), spin=np.asarray(0), reference=np.asarray("RKS"), software=np.asarray('{"pyscf": "2.14.0"}'))
    np.savez(patch_path, H_raw=2 * np.eye(9), H_projected=2 * np.eye(9), freq_cm=np.concatenate([patched_vib, np.zeros(6)]),
             directions=np.ones((9, directions)), columns=np.ones((9, directions)), freq_label_vib_cm=VIB,
             freq_patched_vib_cm=patched_vib, below_cm=np.asarray(below_cm), step_bohr=np.asarray(0.01), grid=grid,
             software=np.asarray('{"pyscf": "2.15.0"}'))
    return label_path, patch_path


def config(root: Path, **kw: Any) -> LMS.SwapConfig:
    return LMS.SwapConfig(root / "molecules", root / "results", root / "superseded", root / "record", **kw)


def test_a_clean_pair_swaps_and_keeps_the_labels_own_settings(tmp_path: Path) -> None:
    for tag in LMS.LABEL_TAGS:
        write_pair(tmp_path, "M1", tag, np.array([55.0, 120.0, 300.0]))
    rows = LMS.swap_molecule("M1", config(tmp_path))
    assert all(r["swapped"] for r in rows)
    with np.load(tmp_path / "molecules/M1/hessian_b3lyp_analytic.npz", allow_pickle=False) as z:
        assert np.array_equal(z["H_projected"], 2 * np.eye(9))      # the patch's Hessian
        assert float(z["energy"]) == -1.5 and str(z["reference"]) == "RKS"   # the label's own settings
        assert "2.15.0" in str(z["software"]) and "2.14.0" in str(z["low_mode_patch"])
    assert (tmp_path / "superseded/M1/hessian_b3lyp_analytic.npz").is_file()
    assert rows[0]["sha256_before"] != rows[0]["sha256_after"]


def test_the_targeted_mode_may_move_far_and_the_others_may_not(tmp_path: Path) -> None:
    for tag in LMS.LABEL_TAGS:
        write_pair(tmp_path, "M1", tag, np.array([55.0, 120.0, 300.0]))
    rows = LMS.swap_molecule("M1", config(tmp_path, dry_run=True))
    assert rows[0]["targeted_change_cm"] == [15.0] and rows[0]["max_collateral_cm"] == 0.0
    for tag in LMS.LABEL_TAGS:
        write_pair(tmp_path, "M2", tag, np.array([55.0, 121.0, 300.0]))
    refused = LMS.swap_molecule("M2", config(tmp_path, dry_run=True))
    assert all("does not target" in r["reason"] for r in refused)


def test_a_molecules_two_labels_move_together_or_not_at_all(tmp_path: Path) -> None:
    write_pair(tmp_path, "M1", "b3lyp", np.array([55.0, 120.0, 300.0]))
    write_pair(tmp_path, "M1", "wb97x", np.array([55.0, 121.0, 300.0]))      # refused: an untargeted mode moved
    rows = LMS.swap_molecule("M1", config(tmp_path))
    assert not any(r["swapped"] for r in rows)
    assert "other label was refused" in rows[0]["reason"]
    with np.load(tmp_path / "molecules/M1/hessian_b3lyp_analytic.npz", allow_pickle=False) as z:
        assert np.array_equal(z["H_projected"], np.eye(9))
    assert not (tmp_path / "superseded").exists()


def test_a_targeted_mode_that_turns_imaginary_is_accepted_and_counted(tmp_path: Path) -> None:
    for tag in LMS.LABEL_TAGS:
        write_pair(tmp_path, "M1", tag, np.array([-5.0, 120.0, 300.0]))
    read = LMS.run(["M1"], config(tmp_path, dry_run=True))
    assert read["refused"] == [] and read["imaginary_gained"] == ["M1"]
    assert read["rows"][0]["targeted_turned_imaginary"] == 1


def rewrite_patch(root: Path, mol_id: str, tag: str, **arrays: np.ndarray) -> None:
    """Replace entries of a written patch file, for the cases write_pair's own frequencies cannot express."""
    path = root / "results" / mol_id / f"hessian_{tag}_analytic_grfpatch.npz"
    with np.load(path, allow_pickle=False) as z:
        kept = {k: z[k] for k in z.files}
    np.savez(path, **(kept | arrays))


def test_an_untargeted_mode_that_turns_imaginary_refuses_the_file(tmp_path: Path) -> None:
    # the targeted mode moves 15 cm-1, and a second mode slips from +0.3 to -0.2: inside the collateral bound, outside the sign rule
    for tag in LMS.LABEL_TAGS:
        write_pair(tmp_path, "M1", tag, np.array([55.0, -0.2, 300.0]))
        rewrite_patch(tmp_path, "M1", tag, freq_label_vib_cm=np.array([40.0, 0.3, 300.0]))
    rows = LMS.swap_molecule("M1", config(tmp_path, dry_run=True))
    assert all("untargeted real mode" in r["reason"] for r in rows)


def test_a_molecule_whose_imaginary_mode_clears_is_counted(tmp_path: Path) -> None:
    for tag in LMS.LABEL_TAGS:
        write_pair(tmp_path, "M1", tag, np.array([7.0, 120.0, 300.0]))
    rewrite_patch(tmp_path, "M1", "b3lyp", freq_label_vib_cm=np.array([-7.0, 120.0, 300.0]))
    read = LMS.run(["M1"], config(tmp_path, dry_run=True))
    assert read["imaginary_cleared"] == ["M1"] and read["imaginary_gained"] == []


def test_a_different_grid_refuses_the_file(tmp_path: Path) -> None:
    for tag in LMS.LABEL_TAGS:
        write_pair(tmp_path, "M1", tag, np.array([55.0, 120.0, 300.0]), grid=np.array([75, 302]))
    rows = LMS.swap_molecule("M1", config(tmp_path, dry_run=True))
    assert all("grid" in r["reason"] for r in rows)


def test_a_dry_run_writes_no_label_and_keeps_nothing(tmp_path: Path) -> None:
    for tag in LMS.LABEL_TAGS:
        write_pair(tmp_path, "M1", tag, np.array([55.0, 120.0, 300.0]))
    rows = LMS.swap_molecule("M1", config(tmp_path, dry_run=True))
    assert not any(r["swapped"] for r in rows) and not any(r["reason"] for r in rows)
    with np.load(tmp_path / "molecules/M1/hessian_b3lyp_analytic.npz", allow_pickle=False) as z:
        assert np.array_equal(z["H_projected"], np.eye(9))
    assert not (tmp_path / "superseded").exists()


def test_the_config_refuses_a_threshold_outside_the_registration(tmp_path: Path) -> None:
    write_pair(tmp_path, "M1", "b3lyp", np.array([55.0, 120.0, 300.0]))
    with pytest.raises(ValueError, match="collateral_cm"):
        config(tmp_path, collateral_cm=3.0)
    with pytest.raises(ValueError, match="below_cm"):
        config(tmp_path, below_cm=0.0)
