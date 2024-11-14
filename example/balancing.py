from xyz import *
import networkx as nx
import pydot

if __name__ == "__main__":
    state_vector = D_state(10, 2)
    state = quantize_state(state_vector)
    qc = sparse_state_synthesis(state, map_gates=True)
    print(to_qiskit(qc))
    qntk = to_dag(qc)
    graph = qntk.to_dot()
    graph.write('tmp.dot')