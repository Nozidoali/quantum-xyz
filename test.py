from QuantumXYZ import *

num_qubits: int = 5

weighted_state = D_state(num_qubits, 1)
    
quantized_state = QState(
    weighted_state,
    num_qubits=num_qubits,
    is_quantized=False
)

canonical_state, _ = get_representative(quantized_state, num_qubits)

with stopwatch("synthesis"):
    transitions = SparseStateSynthesis(quantized_state).run(verbose=True)

with stopwatch("recover circuit"):
    circuit = transitions.recover_circuit(weighted_state, verbose=False)

simulation_result = simulate(circuit)
print(simulation_result)

print(circuit.to_qiskit_circuit())

print(circuit.num_gates(QGateType.CX))

canonicalization_time: float = get_time("get_representative")
print(f"get representative: {canonicalization_time:0.02f} sec")