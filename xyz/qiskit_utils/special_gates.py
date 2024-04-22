#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 14:14:19
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:01:37
"""

# pylint: disable=C0103

from qiskit.circuit.library.standard_gates import RYGate
from qiskit.circuit.library import UnitaryGate

from ..circuit.basic_gates import U, CU, MCRY


class SpecialGates:
    """SpecialGates class ."""

    def __init__(self):
        pass

    @staticmethod
    def mcry(gate: MCRY):
        """Convert a MCRY gate into a RYZ gate .

        :param gate: [description]
        :type gate: MCRY
        :return: [description]
        :rtype: [type]
        """
        num_control_qubits = len(gate.control_qubits)

        # we need to reverse the order of the control qubits
        # because the qiskit's control gate is in the reverse order
        control_str = "".join([str(int(phase)) for phase in gate.phases])[::-1]

        return RYGate(gate.get_theta()).control(
            num_control_qubits, ctrl_state=control_str
        )

    @staticmethod
    def u(gate: U):
        """Creates a CU gate .

        :param gate: [description]
        :type gate: U
        :return: [description]
        :rtype: [type]
        """

        return UnitaryGate(gate.get_unitary())

    @staticmethod
    def cu(gate: CU):
        """Creates a CU gate .

        :param gate: [description]
        :type gate: CU
        """

        num_control_qubits = 1

        # we need to reverse the order of the control qubits
        # because the qiskit's control gate is in the reverse order
        control_str = str(int(gate.phase))

        return UnitaryGate(gate.get_unitary()).control(
            num_control_qubits, ctrl_state=control_str
        )
