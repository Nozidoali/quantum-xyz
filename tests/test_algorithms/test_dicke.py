import numpy as np
import pytest
import xyz

# these are the results from the original implementation
# the heuristic synthesis algorithm is not guaranteed to produce the same results
dicke_qsp_results: list = [
    [3, 1, 4],
    [4, 1, 7],
    [4, 2, 6],
    [5, 1, 10],
    [5, 2, 16],
    [6, 1, 13],
    [6, 2, 22],
    [6, 3, 25],
]


@pytest.mark.skip(reason="no way of currently testing this")
def test_qsp_dicke():
    for n_qubits, k, golden in dicke_qsp_results:
        state_vector = xyz.D_state(n_qubits, k)
        dicke_qsp_results.append(
            {"num_qubits": n_qubits, "k": k, "state_vector": state_vector}
        )
        print(f"n_qubits: {n_qubits}, k: {k}")
        with xyz.stopwatch("resynthesis") as timer_new:
            # DATE24
            param = xyz.StatePreparationParameters(
                enable_exact_synthesis=True, n_qubits_max=100
            )
            new_circuit = xyz.prepare_state(
                state_vector, map_gates=True, verbose_level=0, param=param
            )
        n_cnot_new = new_circuit.get_cnot_cost()
        state_vector_act = xyz.simulate_circuit(new_circuit)
        assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
        print(xyz.to_qiskit(new_circuit))
        print(f"n_cnot_new: {n_cnot_new}")
        if n_cnot_new != golden:
            print(
                f"n_qubits: {n_qubits}, k: {k}, n_cnot_new: {n_cnot_new}, golden: {golden}"
            )
        # assert n_cnot_new == golden
