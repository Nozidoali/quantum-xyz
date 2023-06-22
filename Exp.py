from Algorithms import *
from StatePreparator import *

num_qubits = 6

solution = cnry_solver(W_state(num_qubits))

circuit = solution_to_circuit(num_qubits, solution)

circ = circuit.to_qiskit(with_measurement=True)
print(circ)
print(simulate(circ))
