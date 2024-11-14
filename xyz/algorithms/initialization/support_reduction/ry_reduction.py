import copy
from xyz.circuit import RY, QCircuit, QState, get_ap_ry_angles


def ry_reduction(circuit: QCircuit, state: QState):
    signatures = state.get_qubit_signatures()
    gates = []
    new_state = copy.deepcopy(state)

    for qubit_index, _ in enumerate(signatures):
        theta = get_ap_ry_angles(state, qubit_index)
        if theta is not None:
            # we can use the Y gate
            gate = RY(theta, circuit.qubit_at(qubit_index))
            gates.append(gate)
            new_state = gate.conjugate().apply(new_state)

    return new_state, gates
