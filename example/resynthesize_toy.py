import xyz
import numpy as np

if __name__ == "__main__":
    
    # initial circuit
    circuit = xyz.QCircuit(3, map_gates=True)
    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(0)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(0), True, xyz.QBit(1)))
    circuit.add_gate(
        xyz.MCRY(np.pi, [xyz.QBit(0), xyz.QBit(1)], [True, False], xyz.QBit(2))
    )
    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(1)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(1), True, xyz.QBit(2)))
    print(xyz.to_qiskit(circuit))

    # resynthesize the circuit
    new_circuit = xyz.resynthesis(circuit, verbose_level=2)
    print(xyz.to_qiskit(new_circuit))
