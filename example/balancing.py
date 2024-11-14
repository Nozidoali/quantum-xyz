from xyz import *
import pydot

if __name__ == "__main__":
    state_vector = D_state(10, 2)
    state = quantize_state(state_vector)
    qc = sparse_state_synthesis(state, map_gates=True)
    qc = mapping(qc)
    print(to_qiskit(qc))
