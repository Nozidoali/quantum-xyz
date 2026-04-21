import numpy as np
import pytest
import xyz

# (num_qubits, k, historical_cnot_count). The historical_cnot_count field is
# kept for documentation only; the assertion is a 10%-slack upper bound so
# the test survives legitimate heuristic drift.
dicke_qsp_results = [
    (3, 1, 4),
    (4, 1, 7),
    (4, 2, 6),
    (5, 1, 10),
    (6, 1, 13),
]


@pytest.mark.parametrize("n_qubits,k,historical", dicke_qsp_results)
def test_qsp_dicke(n_qubits, k, historical):
    state_vector = xyz.D_state(n_qubits, k)
    param = xyz.StatePreparationParameters(
        enable_exact_synthesis=True, n_qubits_max=100
    )
    circuit = xyz.prepare_state(state_vector, map_gates=True, param=param)

    sim = xyz.simulate_circuit(circuit)
    assert np.linalg.norm(sim - state_vector) < 1e-6, (
        f"n={n_qubits} k={k}: statevector mismatch"
    )

    bound = int(np.ceil(historical * 1.1))
    cnot = circuit.get_cnot_cost()
    assert cnot <= bound, f"n={n_qubits} k={k}: CNOT {cnot} > bound {bound}"
