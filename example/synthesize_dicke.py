import numpy as np
from xyz import (
    D_state,
    quantize_state,
    prepare_state,
    stopwatch,
    simulate_circuit,
    resynthesis,
    to_qiskit,
    prepare_dicke_state,
)

if __name__ == "__main__":
    state_vector = D_state(8, 2)
    target_state = quantize_state(state_vector)

    # synthesize the state
    with stopwatch("synthesis", verbose=True) as timer:
        circuit = prepare_state(target_state, map_gates=True, verbose_level=0)
        # circuit = prepare_dicke_state(8, 2)
        circuit = resynthesis(circuit, verbose_level=0)
    n_cnot = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(abs(state_vector_act) - abs(state_vector))
    assert dist < 1e-6

    qc = to_qiskit(circuit)
    print("CNOT count: ", n_cnot)
    # print("target state: ", quantize_state(state_vector))
    # print("actual state: ", quantize_state(state_vector_act))
