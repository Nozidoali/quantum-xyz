import numpy as np
from qiskit import qasm2
from qiskit.quantum_info import Statevector
from xyz import quantize_state

if __name__ == "__main__":

    qc = qasm2.load('tmp.qasm')
    # qc = resynthesis(qc, verbose_level=0)
    state_vector_act = Statevector(qc).data
    state_vector_act[np.abs(state_vector_act) < 1e-10] = 0
    print(f"actual state: {quantize_state(state_vector_act)}")
    print(qc)
    exit()
