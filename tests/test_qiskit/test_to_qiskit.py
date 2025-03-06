import xyz


def test_to_qiskit():
    circuit = xyz.QCircuit(2)
    circuit.add_gate(xyz.X(circuit.qubit_at(0)))
    qc = xyz.to_qiskit(circuit)
    assert qc.num_qubits == 2
