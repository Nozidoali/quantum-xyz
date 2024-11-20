import numpy as np
from qiskit import qasm2
from qiskit.quantum_info import Statevector
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

    # synthesize the state
    state_vector = D_state(4, 2)
    with stopwatch("synthesis", verbose=True) as timer:
        circuit = prepare_state(state_vector, verbose_level=0)
        # circuit = resynthesis(circuit, verbose_level=0)
    n_cnot = circuit.get_cnot_cost()
    l_cnot = circuit.get_level()
    print(f"cnot cost: {n_cnot}, level: {l_cnot}")

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(abs(state_vector_act) - abs(state_vector))
    assert dist < 1e-6

    qc = to_qiskit(circuit)
print(qc)
    qasm2.dump(qc, 'dicke.qasm')
    print("CNOT count: ", n_cnot)
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))
