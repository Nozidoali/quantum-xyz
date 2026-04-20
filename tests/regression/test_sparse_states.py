"""Regression: sparse target states (incl. cardinality-1 trivial cases)."""

from __future__ import annotations

import numpy as np
import pytest

import xyz
from tests.regression.builders import sparse_cases
from tests.regression.conftest import SEED, STATEVECTOR_ATOL


@pytest.fixture(scope="module")
def case_map():
    rng = np.random.default_rng(SEED)
    return dict(sparse_cases(rng))


@pytest.mark.parametrize(
    "case_id",
    [cid for cid, _ in sparse_cases(np.random.default_rng(SEED))],
)
def test_sparse(case_id, case_map, golden_bounds):
    target_vec = case_map[case_id]
    circuit = xyz.prepare_state(target_vec, map_gates=True)

    sim_vec = xyz.simulate_circuit(circuit)
    assert np.linalg.norm(np.abs(sim_vec) - np.abs(target_vec)) < STATEVECTOR_ATOL, (
        f"{case_id}: statevector mismatch"
    )

    bound = golden_bounds[case_id]
    actual = circuit.get_cnot_cost()
    assert actual <= bound, f"{case_id}: CNOT {actual} > bound {bound}"
