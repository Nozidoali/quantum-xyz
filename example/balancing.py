from xyz import *
import pydot

if __name__ == "__main__":
    state_vector = rand_state(7, 7, uniform=True)
    state = quantize_state(state_vector)
    qc = sparse_state_synthesis(state, map_gates=False, depth_opt=False, verbose_level=0)
    qc_map = mapping_debug(qc, control_reorder=False)
    print(f"area = {qc_map.get_cnot_cost()}, depth = {qc_map.get_level()}")
    print(to_qiskit(qc_map))
    
    # verify the correctness of the synthesized circuit
    state_vector0 = simulate_circuit(qc_map)
    
    qc_ours = parallel_sparse_state_synthesis(state, verbose_level=0)
    qc_ours = resynthesis(qc_ours)

    print(f"area = {qc_ours.get_cnot_cost()}, depth = {qc_ours.get_level()}")
    
    qc_ours = schedule_commutable_gates(qc_ours)
    print(f"area = {qc_ours.get_cnot_cost()}, depth = {qc_ours.get_level()}")
    
    state_vector1 = simulate_circuit(qc_ours)
    if not np.allclose(state_vector0, state_vector1):
        print("state vectors are not equal")
        print(f"state_vector0 = {quantize_state(state_vector0)}")
        print(f"state_vector1 = {quantize_state(state_vector1)}")

    # print(qiskit_depth_evaluation(qc_map))
    print(to_qiskit(qc_ours))