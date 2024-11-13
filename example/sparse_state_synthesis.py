from xyz import *

state = D_state(5, 2)
qstate = quantize_state(state)
circuit = sparse_state_synthesis(qstate, verbose_level=3)

qc = to_qiskit(circuit)
print(qc)