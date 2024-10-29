#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-06-11 21:29:55
Last Modified by: Hanyu Wang
Last Modified time: 2024-06-11 21:52:54
"""

import numpy as np
from enum import Enum, auto
from xyz.circuit import QCircuit, CX, CRY, MCRY, X, RY


# Reference:
# @inproceedings{bartschi2019deterministic,
#     title={Deterministic preparation of Dicke states},
#     author={B{\"a}rtschi, Andreas and Eidenbenz, Stephan},
#     booktitle={International Symposium on Fundamentals of Computation Theory},
#     pages={126--139},
#     year={2019},
#     organization={Springer}
# }

# @article{sekhar2020actual,
#     title={On Actual Preparation of Dicke State on a Quantum Computer},
#     author={Sekhar Mukherjee, Chandra and Maitra, Subhamoy and Gaurav, Vineet and Roy, Dibyendu},
#     journal={arXiv e-prints},
#     pages={arXiv--2007},
#     year={2020}
# }


class TriState(Enum):
    """This method is used to set the auto - TriState type for TriState type ."""

    FALSE = auto()
    TRUE = auto()
    UNDEFINED = auto()


def _x(state: TriState) -> TriState:
    if state == TriState.TRUE:
        return TriState.FALSE
    if state == TriState.FALSE:
        return TriState.TRUE
    return TriState.UNDEFINED


class SCSManager:
    def __init__(self, n: int, k: int):
        self.n = n
        self.k = k
        self.n_cnots = 0
        self.hasVal = [TriState.FALSE for i in range(n)]

    def print_hasVal(self):
        print("hasVal: ", end="")
        for i in range(self.n):
            print(self.hasVal[i], end=" ")
        print()

    def add_cx(self, circuit: QCircuit, control: int, target: int):
        if self.hasVal[control] == TriState.FALSE:
            # if the control qubit is 0, we do not need to add a CNOT gate
            return
        if self.hasVal[control] == TriState.TRUE:
            # if the control qubit is 1, we need to add a X gate
            circuit.add_gate(X(circuit.qubit_at(target)))
            self.hasVal[target] = _x(self.hasVal[target])
        else:
            self.n_cnots += 1
            circuit.add_gate(
                CX(circuit.qubit_at(control), True, circuit.qubit_at(target))
            )
            self.hasVal[target] = TriState.UNDEFINED

    def add_ry(self, circuit: QCircuit, target: int, theta: float):
        circuit.add_gate(RY(theta, circuit.qubit_at(target)))
        self.hasVal[target] = TriState.UNDEFINED

    def add_x(self, circuit: QCircuit, target: int):
        circuit.add_gate(X(circuit.qubit_at(target)))
        self.hasVal[target] = _x(self.hasVal[target])

    def add_cry(self, circuit: QCircuit, control: int, target: int, theta: float):
        if self.hasVal[control] == TriState.FALSE:
            # if the control qubit is 0, we do not need to add a CRY gate
            return
        if self.hasVal[control] == TriState.TRUE:
            # if the control qubit is 1, we need to add a RY gate
            self.add_ry(circuit, target, theta)
        else:
            self.n_cnots += 2
            circuit.add_gate(
                CRY(theta, circuit.qubit_at(control), True, circuit.qubit_at(target))
            )
            self.hasVal[target] = TriState.UNDEFINED

    def add_mcry(
        self, circuit: QCircuit, control1: int, control2: int, target: int, theta: float
    ):
        if self.hasVal[control1] == TriState.FALSE:
            # if the control qubit is 0, we do not need to add a CRY gate
            return
        if self.hasVal[control2] == TriState.FALSE:
            # if the control qubit is 0, we do not need to add a CRY gate
            return
        if self.hasVal[control1] == TriState.TRUE:
            self.add_cry(circuit, control2, target, theta)
            return
        if self.hasVal[control2] == TriState.TRUE:
            self.add_cry(circuit, control1, target, theta)
            return
        control_qubits = [circuit.qubit_at(control1), circuit.qubit_at(control2)]
        phases = [True, True]
        target_qubit = circuit.qubit_at(target)
        circuit.add_gate(MCRY(theta, control_qubits, phases, target_qubit))
        self.hasVal[target] = TriState.UNDEFINED

    def insert_mu(self, circuit: QCircuit, n: int, k: int, j: int):
        theta = 2 * np.arccos(np.sqrt(1 / (n - j)))
        self.add_cx(circuit, j + 1, j)
        self.add_cry(circuit, j, j + 1, theta)
        self.add_cx(circuit, j + 1, j)

    def insert_M(self, circuit: QCircuit, n: int, k: int, j: int, i: int):
        theta = 2 * np.arccos(np.sqrt((i + 1) / (n - j)))

        self.add_cx(circuit, j + i + 1, j)

        self.add_mcry(circuit, j + i, j, j + i + 1, theta)

        self.add_cx(circuit, j + i + 1, j)

    def insert_scs(self, circuit: QCircuit, n: int, k: int, j: int):
        """
        insert_scs insert the split and cyclic shift gates into the circuit.
        """
        assert k >= 1, "k should be greater than or equal to 1"

        # if j >= k - 1:
        self.insert_mu(circuit, n, k, j)
        for i in range(1, k):
            if j + i + 1 >= n:
                break
            # if (i - 1) < k - j - 2:
            #     continue
            self.insert_M(circuit, n, k, j, i)


def prepare_dicke_state(n: int, k: int, map_gates: bool = True):
    circuit = QCircuit(n, map_gates=map_gates)

    manager = SCSManager(n, k)

    # prepare seed
    for i in range(k):
        manager.add_x(circuit, i)

    # prepare the dicke state
    for i in range(n - 1):
        # manager.print_hasVal()
        manager.insert_scs(circuit, n, k, i)

    return circuit
