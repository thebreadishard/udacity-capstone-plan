"""JSON result records that are JSON: an undefined value (NaN, +inf, -inf) is written as null.

Python's `json` writes NaN and Infinity by default (`allow_nan=True`). RFC 8259 has neither, so strict readers (jq, JavaScript's
JSON.parse, most other languages) refuse such a record; 62 records carried them by 19 Nov 2026 (TASKS 276). Here every non-finite float
becomes null, numpy scalars and arrays become their Python values, and the text is produced with `allow_nan=False`, so a value that slipped
through the conversion raises instead of being written. Everything else is written exactly as `json.dumps` would write it.

Library:  from json_records import dumps, write
    dumps(obj, indent=1, **json_kwargs) -> str
    write(path, obj, indent=1, **json_kwargs)   # temp file in the target's folder, moved over the target
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


def json_safe(value: Any) -> Any:
    """Return `value` with every non-finite float replaced by None and numpy scalars and arrays turned into Python values, recursively."""
    if isinstance(value, float):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, np.generic):
        return json_safe(value.item())
    return value


def dumps(obj: Any, indent: int | None = 1, **json_kwargs: Any) -> str:
    """Return `obj` as strict JSON text: non-finite floats as null; `json_kwargs` go to `json.dumps` (`allow_nan` is not one of them)."""
    if "allow_nan" in json_kwargs:
        raise TypeError("json_records always writes with allow_nan=False; the argument is refused, not ignored")
    return json.dumps(json_safe(obj), indent=indent, allow_nan=False, **json_kwargs)


def write(path: str | os.PathLike[str], obj: Any, indent: int | None = 1, **json_kwargs: Any) -> None:
    """Write `obj` to `path` as strict JSON through a temp file in the same folder, moved over the target; the text is built first."""
    target = Path(path)
    text = dumps(obj, indent=indent, **json_kwargs)
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=target.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, target)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
