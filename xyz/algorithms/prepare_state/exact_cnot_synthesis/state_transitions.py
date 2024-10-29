import numpy as np

from xyz.circuit import QCircuit, QState, CX, CRY
from ..support_reduction import support_reduction
from ..rotation_angles import get_ap_cry_angles


def get_state_transitions(circuit: QCircuit, curr_state: QState, supports: list = None):
    if supports is None:
        supports = curr_state.get_supports()

    # try dependency analysis
    new_state, gates = support_reduction(circuit, curr_state)
    if len(gates) > 0:
        return [[new_state, gates]]

    # apply CRY
    transitions = []
    for target_qubit in supports:
        for control_qubit in supports:
            if control_qubit == target_qubit:
                continue
            for phase in [True, False]:
                cry_angle = get_ap_cry_angles(
                    curr_state, control_qubit, target_qubit, phase
                )
                if cry_angle is None:
                    continue
                transitions.append(
                    [
                        None,
                        [
                            CRY(
                                cry_angle,
                                circuit.qubit_at(control_qubit),
                                phase,
                                circuit.qubit_at(target_qubit),
                            )
                        ],
                    ]
                )

                transitions.append(
                    [
                        None,
                        [
                            CRY(
                                cry_angle - np.pi,
                                circuit.qubit_at(control_qubit),
                                phase,
                                circuit.qubit_at(target_qubit),
                            )
                        ],
                    ]
                )

    if len(transitions) > 0 and curr_state.num_qubits > 4:
        # To speed up the search, we only consider the first CRY gate
        return transitions

    for target_qubit in supports:
        # apply CNOT
        for target_qubit in supports:
            for control_qubit in supports:
                if control_qubit == target_qubit:
                    continue
                for phase in [True, False]:
                    gate = CX(
                        circuit.qubit_at(control_qubit),
                        phase,
                        circuit.qubit_at(target_qubit),
                    )
                    transitions.append([None, [gate]])
    return transitions
