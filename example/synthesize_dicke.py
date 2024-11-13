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
    # state_vector = D_state(5, 2)
    # target_state = quantize_state(state_vector)
    
    qc = qasm2.load('dicke.qasm')
    # qc = resynthesis(qc, verbose_level=0)
    state_vector_act = Statevector(qc).data
    state_vector_act[np.abs(state_vector_act) < 1e-10] = 0
    print(f"actual state: {quantize_state(state_vector_act)}")
    # print(qc)
    exit()

    # synthesize the state
    state_vector = D_state(5, 2)
    with stopwatch("synthesis", verbose=True) as timer:
        circuit = prepare_dicke_state(5, 2, map_gates=False)
        # circuit = prepare_state(state_vector, map_gates=False, verbose_level=0)
        # circuit = resynthesis(circuit, verbose_level=0)
    n_cnot = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(abs(state_vector_act) - abs(state_vector))
    assert dist < 1e-6

    qc = to_qiskit(circuit)
    print("CNOT count: ", n_cnot)
    print(qc)
    qasm2.dump(qc, 'dicke.qasm')
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))
