from QuantumXYZ import *

num_qubits: int = 5

state = None

if num_qubits == 3:
    state = QState(
        [
            0b001, 
            0b010, 
            0b100, 
        ], num_qubits, True
    )

if num_qubits == 4:
    state = QState(
        [
            0b0001, 
            0b0010, 
            0b0100, 
            0b1000, 
        ], num_qubits, True
    )

if num_qubits == 5:
    state = QState(
        [
            0b00001, 
            0b00010, 
            0b00100, 
            0b01000, 
            0b10000, 
        ], num_qubits, True
    )

canonical_state, _ = get_representative(state, num_qubits)

transitions = SparseStateSynthesis(state).run(verbose=True)

circuit = transitions.recover_circuit(W_state(num_qubits), verbose=True)


simulation_result = simulate(circuit)
print(simulation_result)

print(circuit.to_qiskit_circuit())