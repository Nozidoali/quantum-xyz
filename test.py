from QuantumXYZ import *

state = QState(
    [
        0b000, 
        0b011, 
        0b111, 
    ], 3, True
)


canonical_state = canonicalize(state)

print(canonical_state)