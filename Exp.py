from Algorithms import *
from StatePreparator import *

num_qubits = 5

solution = cnry_solver(W_state(num_qubits))

circuit = solution_to_circuit(num_qubits, solution)
print(circuit.circuit.draw())
circuit.simulate()
