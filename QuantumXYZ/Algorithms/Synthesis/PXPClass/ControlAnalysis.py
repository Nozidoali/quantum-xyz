from QuantumXYZ.Circuit import *
from typing import List

class ControlLit:
    
    def __init__(self, control_qubit_index: int, control_phase: bool):
        self.control_qubit_index = control_qubit_index
        self.control_phase = control_phase

def check_dont_care(state: QState, control_qubit_index) -> bool:
    return state.column_is_mixed(control_qubit_index)

def check_merge(state: QState, target_qubit_index: int, lit: ControlLit) -> bool:
    """we check if the merge is valid

    Args:
        state (QState): the initial state
        target_qubit_index (int): the target qubit index
        lit (ControlLit): the control literal

    Returns:
        bool: true if the merge is valid
    """
    
    target_column = state.column_at(target_qubit_index)
    control_column = state.column_at(
        lit.control_qubit_index,
        control_phase=lit.control_phase
    )
    
    control_value = target_column & control_column
    
    # here the ref 0 is the case where target qubit is always 0 
    # the ref 1 is the case where target qubit is always 1
    ref0: int = 0
    ref1: int = (1<<(len(state) + 1)) - 1
    
    if control_value == ref0 or control_value == ref1:
        return False
    
    return True
    
        
def get_controls(state: QState, target_qubit_index: int, rotation_type: QuantizedRotationType) -> List[ControlLit]:
    """get the useful controls of the state

    Args:
        state (QState): the initial state
        target_qubit_index (int): the index of the target qubit

    Returns:
        List[ControlLit]: the list of useful control literals
        
    The idea is, we need to make sure the following to ganrantee that the control is useful.
    
    1. the control literal is in the on-set of our state
    2. the control literal can separate the on-set of our state (should contain both 1 and 0)
    3. for merge operators, we need to check if both 0 and 1 are in the quantum state
    """
    
    for control_qubit_index in range(state.num_qubits):
        
        if control_qubit_index == target_qubit_index:
            continue
        
        if check_dont_care(state, control_qubit_index) is False:
            continue
        
        for control_phase in [False, True]:
            
            lit = ControlLit(control_qubit_index, control_phase)
        
            match rotation_type:
                
                case QuantizedRotationType.SWAP:
                    pass
                
                case QuantizedRotationType.MERGE0:
                    if check_merge(state, target_qubit_index, lit) == False:
                        continue
                    
                    pass
                
                case QuantizedRotationType.MERGE1:    
                    if check_merge(state, target_qubit_index, lit) == False:
                        continue
                    
                    pass             
                case _:
                    raise NotImplementedError
            
            yield lit
