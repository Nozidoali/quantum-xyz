"""Regression: Dicke target states."""

from __future__ import annotations

import numpy as np
import pytest

import xyz
from tests.regression.builders import dicke_cases
from tests.regression.conftest import STATEVECTOR_ATOL


@pytest.fixture(scope="module")
def case_map():
    return dict(dicke_cases())


@pytest.mark.parametrize("case_id", [cid for cid, _ in dicke_cases()])
def test_dicke(case_id, case_map, golden_bounds):
    target_vec = case_map[case_id]

    param = xyz.StatePreparationParameters(
        enable_exact_synthesis=True, n_qubits_max=100
    )
    circuit = xyz.prepare_state(target_vec, map_gates=True, param=param)

    sim_vec = xyz.simulate_circuit(circuit)
    assert np.linalg.norm(sim_vec - target_vec) < STATEVECTOR_ATOL, (
        f"{case_id}: statevector mismatch"
    )

    bound = golden_bounds[case_id]
    actual = circuit.get_cnot_cost()
    assert actual <= bound, f"{case_id}: CNOT {actual} > bound {bound}"
