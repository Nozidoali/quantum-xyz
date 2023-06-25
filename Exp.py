from Algorithms import *
from StatePreparator import *

num_qubits = 3

# solution = cnry_solver(W_state(num_qubits))
solution = cnry_solver(D_state(num_qubits, 2))

circuit = solution_to_circuit(num_qubits, solution)

circ = circuit.to_qiskit(with_measurement=True)
print(circ)
print(simulate(circ))
