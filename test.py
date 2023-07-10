from QuantumXYZ import *

state = QState(
    [
        0b001, 
        0b010, 
        0b100, 
    ], 3, True
)

canonical_state, _ = get_representative(state, 3, True, True)

transitions = SparseStateSynthesis(state).run(verbose=True)

circuit = transitions.recover_circuit(W_state(3))


simulation_result = simulate(circuit)
print(simulation_result)

print(circuit.to_qiskit_circuit())