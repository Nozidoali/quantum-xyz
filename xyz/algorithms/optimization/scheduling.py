from xyz.circuit import *

def schedule_asap(circuit: QCircuit) -> int:
    assert circuit.map_gates == True, "mapping of gates is not enabled"
    num_qubits = circuit.get_num_qubits()
    
    late_qubit_time = [0] * num_qubits
    max_qubit_time = 0
    
    for gate in circuit.get_gates():
        assert issubclass(type(gate), BasicGate)
        assert not issubclass(type(gate), MultiControlledGate) # this needs to be decomposed
        qubits = []
        qubits.append(gate.target_qubit.index)
        if issubclass(type(gate), ControlledGate):
            qubits.append(gate.control_qubit.index)
        
        gate_time = max(late_qubit_time[q] for q in qubits)
        for q in qubits:
            late_qubit_time[q] = gate_time + 1
        
        max_qubit_time = max(max_qubit_time, gate_time + 1)
    
    return max_qubit_time