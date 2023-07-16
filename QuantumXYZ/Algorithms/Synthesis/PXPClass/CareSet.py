from QuantumXYZ.Circuit import *

def get_care_set(state: QState):
    """get the care set of the state

    Args:
        state (QState): the state
    """
    
    one_counts = state.count_ones()
    
    care_set = set()
    
    for qubit in range(state.num_qubits):
        # this qubit is a dont care qubit.
        if one_counts[qubit] == 0 or one_counts[qubit] == len(state):
            continue
        
        care_set.add(qubit)
        
    return care_set