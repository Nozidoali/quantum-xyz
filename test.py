from QuantumXYZ import *

state = QState(
    [
        0b000, 
        0b011, 
        0b111, 
    ], 3, True
)


canonical_state, _ = get_representative(state, 3, True, True)

print(str(canonical_state))