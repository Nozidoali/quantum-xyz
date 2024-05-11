#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-24 10:11:56
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-24 12:48:38
"""

import numpy as np
from .qcircuit import QCircuit
from .gate import QGateType, CX, RY, CRY, MCRY


def to_figure(circuit_str: str) -> str:
    return (
        """
\\begin{figure}[h]
\\centering
\\mbox{
\\small
    \\Qcircuit @C=.4em @R=.3em {
"""
        + circuit_str
        + """
    }
}
\\caption{}
\\end{figure}
"""
    )


PLACEHOLDER = "\\qw"


def theta_to_str(theta: float) -> str:
    theta_str = f"{theta:.2f}"
    if np.isclose(theta, np.pi):
        theta_str = "\\pi"
    elif np.isclose(theta, np.pi / 2):
        theta_str = "\\pi/2"
    elif np.isclose(theta, -np.pi / 2):
        theta_str = "-\\pi/2"
    elif np.isclose(theta, np.pi / 4):
        theta_str = "\\pi/4"
    elif np.isclose(theta, np.pi / 4 * 3):
        theta_str = "3\\pi/4"
    elif np.isclose(theta, -np.pi / 4):
        theta_str = "-\\pi/4"
    elif np.isclose(theta, -np.pi / 4 * 3):
        theta_str = "-3\\pi/4"
    elif np.isclose(theta, -np.pi / 8):
        theta_str = "-\\pi/8"
    elif np.isclose(theta, np.pi / 8):
        theta_str = "\\pi/8"
    return theta_str


def ry_box(theta: float) -> str:
    theta_str = theta_to_str(theta)
    return f"\\gate{{\\parbox{{0.6cm}}{{\\centering \\footnotesize $R_y$\\\\${theta_str}$}}}}"


def to_tikz(circuit: QCircuit) -> str:
    """
    to_tikz:
    convert the circuit to tikz code
    """
    tikz_str = ""

    n_gates = len(circuit.get_gates())
    n_qubits = circuit.get_num_qubits()

    qubit_str = [
        [PLACEHOLDER for i in range(n_gates + 2)]
        for _ in range(circuit.get_num_qubits())
    ]

    for i in range(n_qubits):
        qubit_str[i][0] = f"\\lstick{{q_{i}}}"

    for j, gate in enumerate(circuit.get_gates()):
        i = j + 1
        match gate.get_qgate_type():
            case QGateType.X:
                qubit_str[gate.target_qubit.index][i] = "\\gate{{X}}"
            case QGateType.RY:
                gate: RY
                qubit_str[gate.target_qubit.index][i] = ry_box(theta=gate.theta)
            case QGateType.CX:
                gate: CX
                control_type = "ctrl" if gate.phase else "ctrlo"
                control_dist = -gate.control_qubit.index + gate.target_qubit.index
                qubit_str[gate.control_qubit.index][
                    i
                ] = f"\\{control_type}{{{control_dist}}}"
                qubit_str[gate.target_qubit.index][i] = "\\targ"
            case QGateType.CRY:
                gate: CRY
                control_type = "ctrl" if gate.phase else "ctrlo"
                control_dist = -gate.control_qubit.index + gate.target_qubit.index
                qubit_str[gate.control_qubit.index][
                    i
                ] = f"\\{control_type}{{{control_dist}}}"
                qubit_str[gate.target_qubit.index][i] = ry_box(theta=gate.theta)
            case QGateType.MCRY:
                gate: MCRY
                for control_qubit, control_phase in zip(
                    gate.control_qubits, gate.phases
                ):
                    control_type = "ctrl" if control_phase else "ctrlo"
                    control_dist = -control_qubit.index + gate.target_qubit.index
                    qubit_str[control_qubit.index][
                        i
                    ] = f"\\{control_type}{{{control_dist}}}"
                qubit_str[gate.target_qubit.index][i] = ry_box(theta=gate.theta)
            case _:
                raise ValueError(f"Unsupported gate type {gate.get_qgate_type()}")

    tikz_str = " \\\\\n".join([" & ".join(qubit) for qubit in qubit_str])
    return to_figure(tikz_str)
