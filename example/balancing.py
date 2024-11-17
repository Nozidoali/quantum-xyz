from xyz import *
import pydot

if __name__ == "__main__":
    state_vector = D_state(7, 5)
    state = quantize_state(state_vector)
    qc = sparse_state_synthesis(state, map_gates=False)
    
    qc_map = mapping_debug(qc, reorder=False)
    level_init = schedule_asap(qc_map)
    
    # verify the correctness of the synthesized circuit
    state_vector0 = simulate_circuit(qc_map)
    
    while True:
        new_qc = mapping_debug(qc, reorder=True)
        level = schedule_asap(new_qc)
        
        state_vector1 = simulate_circuit(new_qc)
        if not np.allclose(state_vector0, state_vector1):
            print("state vectors are not equal")
            print(f"state_vector0 = {quantize_state(state_vector0)}")
            print(f"state_vector1 = {quantize_state(state_vector1)}")
            break
        if level < level_init:
            print(f"[i] level = {level}, level_init = {level_init}")
            break
        else:
            print(f"[w] level = {level}, level_init = {level_init}")
        
