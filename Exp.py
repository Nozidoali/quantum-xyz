from Algorithms import *
from StatePreparator import *


LOG_FILE = "test.log"
logging.basicConfig(filename = LOG_FILE, level = logging.DEBUG)
logger = logging.getLogger("test")

@add_log(logger)
def exp():
    num_qubits = 3
    with stopwatch("cnry_solver"):

        state = D_state(num_qubits, 1)
        print(state)
        solution = cnry_solver(state)

    circuit = solution_to_circuit(num_qubits, solution)

    circ = circuit.to_qiskit(with_measurement=True)
    print(circ)
    print(simulate(circ))

exp()