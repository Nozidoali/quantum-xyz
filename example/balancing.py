from xyz import *
import pydot

if __name__ == "__main__":
    state_vector = D_state(10, 5)
    state = quantize_state(state_vector)
    qc = sparse_state_synthesis(state, map_gates=False)
        
    new_qc = mapping_debug(qc)
    
    # verify the correctness of the synthesized circuit
    state_vector0 = simulate_circuit(qc)
    state_vector1 = simulate_circuit(qc)
    
    if not np.allclose(state_vector0, state_vector1):
        print("state vectors are not equal")
        print(f"state_vector0 = {quantize_state(state_vector0)}")
        print(f"state_vector1 = {quantize_state(state_vector1)}")

    write_qasm(new_qc, "circuit.qasm")