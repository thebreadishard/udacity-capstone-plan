#!/usr/bin/env python3
"""Q0. Print SHA256 of generator + spacing + box + refinement rule.

Re-run must print the same digest while grid_spec.py is frozen.
This is not a teacher result. It is the grid identity.

Run from this folder:
  python grid_hash.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import grid_spec  # noqa: E402


def digest() -> str:
    gen = Path(grid_spec.__file__).read_bytes()
    payload = b"\n".join(
        [
            b"PLAN03_Q0",
            gen,
            f"OUTER_SPACING_A0={grid_spec.OUTER_SPACING_A0:.16e}".encode(),
            f"VACUUM_A0={grid_spec.VACUUM_A0:.16e}".encode(),
            f"BOX_RULE={grid_spec.BOX_RULE}".encode(),
            f"REFINEMENT_RULE={grid_spec.REFINEMENT_RULE}".encode(),
            f"DT_TEACHER_AU={grid_spec.DT_TEACHER_AU:.16e}".encode(),
            f"LEARNER_K={grid_spec.LEARNER_K}".encode(),
            f"PERIODIC_BOX={int(grid_spec.PERIODIC_BOX)}".encode(),
            f"MAXWELL_COURANT_SAFETY={grid_spec.MAXWELL_COURANT_SAFETY:.16e}".encode(),
            f"PLUS_CHANNEL={grid_spec.PLUS_CHANNEL}".encode(),
            f"CHANNEL_ORDER={','.join(grid_spec.CHANNEL_ORDER)}".encode(),
        ]
    )
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    h = digest()
    print(f"q0_sha256 {h}")
    print(f"outer_spacing_a0 {grid_spec.OUTER_SPACING_A0:.16e}")
    print(f"vacuum_a0 {grid_spec.VACUUM_A0:.16e}")
    print(f"box_rule {grid_spec.BOX_RULE}")
    print(f"refinement_rule {grid_spec.REFINEMENT_RULE}")
    print(f"dt_teacher_au {grid_spec.DT_TEACHER_AU:.16e}")
    print(f"learner_k {grid_spec.LEARNER_K}")
    print(f"n_channels {grid_spec.N_CHANNELS}")
    print(f"periodic_box {int(grid_spec.PERIODIC_BOX)}")
    print(f"generator {Path(grid_spec.__file__).as_posix()}")


if __name__ == "__main__":
    main()
