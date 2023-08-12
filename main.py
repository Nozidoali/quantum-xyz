#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 15:49:27
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-11 23:56:48
"""

from xyz import cnot_synthesis, recover_circuit, stopwatch, D_state, QState

num_qubits = 4

state_array = D_state(num_qubits, 2)
print("".join(["1" if x > 0 else "0" for x in state_array]))

# state_array = GHZ_state(num_qubits)

state = QState(state_array, num_qubits, False)

with stopwatch("SparseStateSynthesis"):
    transitions = cnot_synthesis(state)

with stopwatch("transitions"):
    circuit = recover_circuit(transitions, state_array)

circ = circuit.to_qiskit(with_measurement=False, with_tomography=True)

print(circ)
exit(0)

# print(simulate(circ))
# print(f"cnot = {circuit.num_gates(QGateType.CX)}")

from qiskit_ibm_provider import IBMProvider
from qiskit.providers.ibmq import least_busy

provider = IBMProvider()

small_devices = provider.backends(
    filters=lambda x: x.configuration().n_qubits == 5
    and not x.configuration().simulator
)
backend = least_busy(small_devices)


# backend = provider.get_backend('ibmq_quito')

print(f"running on {backend.name}")
# print(f"queue position: {backend.status().queue_position}")
# print(f"pending jobs: {backend.status().pending_jobs}")

# QST Experiment
qstexp1 = StateTomography(circ)
qstdata1 = qstexp1.run(backend, shots=5000).block_for_results()

from time import sleep

while True:
    print(f"running on {backend.name}")
    print(f"queue position: {backend.status().queue_position}")
    print(f"pending jobs: {backend.status().pending_jobs}")

    sleep(1)

# Print results
for result in qstdata1.analysis_results():
    print(result)

exit(0)

from qiskit.tools.monitor import job_monitor


from qiskit import IBMQ
import qiskit

IBMQ.load_account()

provider = IBMQ.load_account()
backend = provider.get_backend("ibmq_quito")
job = qiskit.execute(circ, backend=backend, shots=1024)
job_monitor(job)

result = job.result()
counts = result.get_counts(circuit)

print(counts)

plot_histogram([counts])
