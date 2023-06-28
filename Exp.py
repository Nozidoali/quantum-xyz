from Algorithms import *
from StatePreparator import *


from Algorithms import *
from StatePreparator import *

num_qubits = 4
state = D_state(num_qubits, 1)
database = CnRyDataBase(num_qubits)
database.construct(to_state_list(state))

circuit = database.lookup(to_state_list(state))

circ = circuit.to_qiskit(with_measurement=True)
print(circ)
print(simulate(circ))
