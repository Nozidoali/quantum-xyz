#!/usr/bin/env python
import xyz

if __name__ == "__main__":
    state_vector = [
        1,
        1,
        1,
        -1,
        1,
        1,
        -1,
        1,
        1,
        1,
        1,
        1,
        -1,
        -1,
        -1,
        -1,
    ]
    state = xyz.quantize_state(state_vector)
    param = xyz.StatePreparationParameters(
        enable_exact_synthesis=True, n_qubits_max=100
    )
    circuit = xyz.prepare_state(state, param=param, verbose_level=0)
    new_circuit = xyz.resynthesis(circuit)
    state_vector_act = xyz.simulate_circuit(new_circuit)

    qc = xyz.to_qiskit(new_circuit)
    print(qc)
    print("target state: ", xyz.quantize_state(state_vector))
    print("actual state: ", xyz.quantize_state(state_vector_act))
