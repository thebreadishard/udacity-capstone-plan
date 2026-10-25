"""Shared test inputs for the Mai et al. 2026 readers (TASKS 111/112): a planar CnHn ring and an archive entry in their .xyz layout."""
import numpy as np

BOHR = 0.529177210903


def ring(n_c: int) -> tuple[list[str], np.ndarray]:
    """A planar CnHn ring in bohr (C–C 1.40 Å, C–H 1.08 Å) — benzene for n = 6, another skeleton for n = 8."""
    r_c = 1.40 / (2 * np.sin(np.pi / n_c)) / BOHR
    t = 2 * np.pi * np.arange(n_c) / n_c
    unit = np.stack([np.cos(t), np.sin(t), 0 * t], 1)
    return ["C"] * n_c + ["H"] * n_c, np.concatenate([r_c * unit, (r_c + 1.08 / BOHR) * unit])


def archive_entry(formula: str, n_c: int, first: float = 1000.0) -> str:
    """One neutral entry as their .xyz files lay it out: count, header, geometry in Å, then scaled frequency, intensity, factor per mode."""
    symbols, coords = ring(n_c)
    rows = "\n".join(f"{s} {x * BOHR:.6f} {y * BOHR:.6f} {z * BOHR:.6f}" for s, (x, y, z) in zip(symbols, coords, strict=True))
    return (f"{len(symbols)}\nSource=COMPAS1 Formula={formula} Charge=0 JSD=0.01\n{rows}\n\n"
            f"scaled_Freq(cm^-1) Inten(KM/mol) scale_factor\n{first} 1.0 0.956\n3000.0 2.0 0.960\n")
