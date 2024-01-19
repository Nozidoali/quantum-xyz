import numpy as np

from xyz import QCircuit, RY, CRY, simulate_circuit, quantize_state

if __name__ == "__main__":
    circ = QCircuit(3)
    circ.add_gate(RY(2 * np.arccos(np.sqrt(2) / np.sqrt(12)), circ.qubit_at(0)))
    circ.add_gate(RY(np.pi / 2, circ.qubit_at(1)))
    circ.add_gate(
        CRY(
            2 * np.arccos(np.sqrt(6) / np.sqrt(10)),
            circ.qubit_at(0),
            1,
            circ.qubit_at(2),
        )
    )
    circ.add_gate(
        CRY(-2 * np.arccos(1 / np.sqrt(4)), circ.qubit_at(1), 1, circ.qubit_at(0))
    )

    state_vector_act = simulate_circuit(circ).data
    print("actual state: ", quantize_state(state_vector_act))
    circuit = circ.to_qiskit()
    print(circuit)
