"""Shared fixtures and constants for the regression suite.

The suite is the safety net for the refactor: every test in this package
must keep passing through every refactor phase. Functional correctness is
measured by statevector comparison; resource non-regression is measured by
a per-case CNOT-count bound loaded from golden_bounds.json.
"""

import numpy as np
import pytest

from tests.regression.bounds import load_bounds

# The random seed used for every synthetic case. Do not change it lightly:
# bumping the seed invalidates golden_bounds.json.
SEED = 20260419

# Statevector comparison tolerance, matching the existing tests in the repo.
STATEVECTOR_ATOL = 1e-6

# Margin above measured CNOT count when freezing bounds (10%).
BOUND_SLACK = 1.10


@pytest.fixture(scope="session")
def rng() -> np.random.Generator:
    return np.random.default_rng(SEED)


@pytest.fixture(scope="session")
def golden_bounds() -> dict[str, int]:
    """Read-only view of golden_bounds.json."""
    return load_bounds()
