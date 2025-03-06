import numpy as np
from qiskit import qasm2
import argparse
from xyz import (
    D_state,
    quantize_state,
    prepare_state,
    stopwatch,
    simulate_circuit,
    to_qiskit
)

parser = argparse.ArgumentParser(description='Synthesize Dicke state.')
parser.add_argument('--num_qubits', type=int, default=4, help='Number of qubits')
parser.add_argument('--k', type=int, default=2, help='Number of excitations')
args = parser.parse_args()

if __name__ == "__main__":

    # synthesize the state
    state_vector = D_state(args.num_qubits, args.k)
    
    with stopwatch("synthesis", verbose=True) as timer:
        circuit = prepare_state(state_vector, verbose_level=0)
    n_cnot = circuit.get_cnot_cost()
    l_cnot = circuit.get_level()
    print(f"cnot cost: {n_cnot}, level: {l_cnot}")

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(abs(state_vector_act) - abs(state_vector))
    assert dist < 1e-6
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))
    
    # write the circuit to a file
    qc = to_qiskit(circuit)
    print(qc)
    print("writing dicke.qasm")
    qasm2.dump(qc, 'dicke.qasm')
