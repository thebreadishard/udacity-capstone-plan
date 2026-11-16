"""What the probes that compare this repository with aromir (`thebreadishard/aromir`, TASKS 73) share."""
from __future__ import annotations


def aromir_symbol(symbol: str) -> str:
    """An element symbol as aromir's table keys it ('Cl'); the corpus writes 'CL'."""
    return symbol[0].upper() + symbol[1:].lower()
