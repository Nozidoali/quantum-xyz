"""Golden CNOT-count bounds persistence.

`golden_bounds.json` maps case_id -> int. It is generated once by
`generate_bounds.py` and treated as read-only by the test suite. A phase
that deliberately changes CNOT counts re-runs the generator and commits
the updated JSON together with the code change.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

BOUNDS_PATH = Path(__file__).with_name("golden_bounds.json")


def load_bounds() -> dict[str, int]:
    if not BOUNDS_PATH.exists():
        raise FileNotFoundError(
            f"{BOUNDS_PATH} not found. Run "
            "`python -m tests.regression.generate_bounds` from the repo root."
        )
    return json.loads(BOUNDS_PATH.read_text())


def write_bounds(measured: dict[str, int], slack: float = 1.10) -> None:
    """Freeze `measured` CNOT counts as bounds, inflated by `slack` and
    rounded up. Writes to BOUNDS_PATH."""
    bounds = {case_id: math.ceil(count * slack) for case_id, count in measured.items()}
    BOUNDS_PATH.write_text(json.dumps(bounds, indent=2, sort_keys=True) + "\n")
