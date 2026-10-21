"""How much memory the system can still commit, in GB — one implementation for the run door (`runspec.memory_problems`) and the pins
(`tests/pin_tools.require_free_memory`). On 20–21 Oct 2026 the laptop's commit limit ran out with 3.5–3.7 GB still free by this measure: the
cation run's wsl.exe connections were closed and a read step failed ('not enough memory'), while the stated peaks fitted the 13 GB budget."""
from __future__ import annotations

import os
from pathlib import Path


def free_commit_gb() -> float | None:
    """Windows: the commit limit minus the charge (GlobalMemoryStatusEx); elsewhere MemAvailable; None if unknown."""
    if os.name == "nt":
        import ctypes

        class _Status(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total_phys", ctypes.c_ulonglong),
                        ("avail_phys", ctypes.c_ulonglong), ("total_commit", ctypes.c_ulonglong), ("avail_commit", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong), ("avail_extended", ctypes.c_ulonglong)]
        status = _Status()
        status.length = ctypes.sizeof(_Status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return None
        return status.avail_commit / 1e9
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1e6
    return None
