from xyz import *


def test_rand_state():
    n: int = 6
    m: int = 30

    state_vector: np.ndarray = rand_state(n, m, uniform=True)
    state = quantize_state(state_vector)
    # circuit = parallel_sparse_state_synthesis(state, verbose_level=0)
    circuit = sparse_state_synthesis(state, map_gates=True, verbose_level=0)

    qc = to_qiskit(circuit)
    print(qc)

    state_vector_act = simulate_circuit(circuit)
    if np.linalg.norm(state_vector_act - state_vector) > 1e-6:
        print("Error: state vector not equal")

    n_cnot = circuit.get_cnot_cost()
    print(f"n_cnot: {n_cnot}")
    l_cnot = circuit.get_level()
    print(f"l_cnot: {l_cnot}")

    circuit = resynthesis(circuit, verbose_level=0)
    print(to_qiskit(circuit))

    n_cnot = circuit.get_cnot_cost()
    print(f"n_cnot: {n_cnot}")
    l_cnot = circuit.get_level()
    print(f"l_cnot: {l_cnot}")


if __name__ == "__main__":
    test_rand_state()
