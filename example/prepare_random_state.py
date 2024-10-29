import numpy as np
from xyz import (
    rand_state,
    quantize_state,
    prepare_state,
    stopwatch,
    simulate_circuit,
    sparse_state_synthesis,
    to_qiskit,
)
from xyz import StatePreparationParameters as Param

if __name__ == "__main__":
    # state_vector = rand_state(4, 6, uniform=False)
    # target_state = quantize_state("0.41*|001000> + 0.41*|010001> + 0.41*|010100> + 0.41*|011100> + 0.41*|101111> + 0.41*|111100>")
    target_state = quantize_state(
        "0.71*|0010> + 0.41*|0101> + 0.41*|0111> + 0.41*|1111>"
    )
    state_vector = target_state.to_vector()

    # synthesize the state
    with stopwatch("synthesis", verbose=True) as timer:
        # circuit = sparse_state_synthesis(target_state, verbose_level=3)
        circuit = prepare_state(
            target_state,
            map_gates=True,
            verbose_level=3,
            param=Param(
                enable_exact_synthesis=False, enable_m_flow=True, enable_n_flow=False
            ),
        )
        # circuit = resynthesis(circuit)

    n_cnot = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(abs(state_vector_act) - abs(state_vector))

    qc = to_qiskit(circuit)
    print(qc)
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))
    assert dist < 1e-6
