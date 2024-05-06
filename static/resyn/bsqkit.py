import numpy as np
import xyz

def run_bqskit_flow(circuit: xyz.QCircuit, data = {}):

    from bqskit.compiler import Workflow
    from bqskit.passes import QuickPartitioner, ForEachBlockPass, ScanningGateRemovalPass, UnfoldPass, QSearchSynthesisPass

    basic_gate_deletion_workflow = Workflow([
        QuickPartitioner(3),  # Partition into 3-qubit blocks
        ForEachBlockPass(ScanningGateRemovalPass()),  # Apply gate deletion to each block (in parallel)
        UnfoldPass(),  # Unfold the blocks back into the original circuit
    ])
    
    workflow = [
        QuickPartitioner(),
        ForEachBlockPass([
            QSearchSynthesisPass(),
            ScanningGateRemovalPass()
        ]),
        UnfoldPass()
    ]
    
    from bqskit.compiler import Compiler
    from bqskit.ext.qiskit import bqskit_to_qiskit, qiskit_to_bqskit

    qc = xyz.to_qiskit(circuit)
    with xyz.stopwatch("bqskit_flow") as timer_bqskit:
        with Compiler() as compiler:
            # opt_circuit = compiler.compile(qiskit_to_bqskit(qc), workflow=basic_gate_deletion_workflow)
            opt_circuit = compiler.compile(qiskit_to_bqskit(qc), workflow=workflow)

    qc_opt = bqskit_to_qiskit(opt_circuit)
    print(qc_opt)

def run_bqskit(state_vector: np.ndarray, data = {}):
    from bqskit import compile 
    from bqskit.qis import StateVector 
    from bqskit.qis import StateSystem 
    from bqskit.ext.qiskit import bqskit_to_qiskit
    from bqskit.ir.lang.qasm2 import OPENQASM2Language

    state = xyz.quantize_state(state_vector)
    n = state.num_qubits

    in1 = StateVector(xyz.ground_state(n))
    out1 = StateVector(state_vector) 
    system = StateSystem({in1:out1})
    with xyz.stopwatch("bqskit") as timer_bqskit:
        c = compile(system, optimization_level=3)
        
    qc_opt = bqskit_to_qiskit(c)
    print(f"Optimized circuit: ")
    print(qc_opt)
    
if __name__ == "__main__":
    circuit = xyz.QCircuit(3, map_gates=False)

    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(0)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(0), True, xyz.QBit(1)))
    circuit.add_gate(
        xyz.MCRY(np.pi, [xyz.QBit(0), xyz.QBit(1)], [True, False], xyz.QBit(2))
    )
    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(1)))
    # circuit.add_gate(xyz.X(xyz.QBit(1)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(1), True, xyz.QBit(2)))
    
    data = {}
    run_bqskit_flow(circuit, data)
    state_vector = xyz.simulate_circuit(circuit)
    run_bqskit(state_vector, data)