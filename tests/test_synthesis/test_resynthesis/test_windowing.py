#!/usr/bin/env python
# -*- encoding=utf8 -*-
"""
Author: Hanyu Wang
Created time: 2024-04-23 15:26:47
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 15:56:09
"""

import numpy as np
import xyz
from xyz.gates import CRY, MCRY, QBit, RY, X
from xyz.passes.resynthesis import extract_windows_naive, resynthesize_window


def test_windowing_1():
    """
          ┌─────────┐
    q0_0: ┤ Ry(π/2) ├───o────────────────o─────────────────────────────
          ├─────────┴┐┌─┴─┐┌──────────┐  │
    q0_1: ┤ Ry(3π/4) ├┤ X ├┤ Ry(-π/4) ├──┼───────────────o─────────────
          ├─────────┬┘└───┘└──────────┘┌─┴─┐┌─────────┐┌─┴─┐┌─────────┐
    q0_2: ┤ Ry(π/4) ├──────────────────┤ X ├┤ Ry(π/2) ├┤ X ├┤ Ry(π/4) ├
          └─────────┘                  └───┘└─────────┘└───┘└─────────┘
    """
    circuit = xyz.QCircuit(3, map_gates=True)

    circuit.add_gate(RY(np.pi / 2, QBit(0)))
    circuit.add_gate(CRY(np.pi / 2, QBit(0), True, QBit(1)))
    circuit.add_gate(CRY(np.pi / 4, QBit(0), True, QBit(2)))
    circuit.add_gate(CRY(np.pi / 4, QBit(1), True, QBit(2)))

    assert circuit.get_cnot_cost() == 6  # 2 + 2 + 2

    windows = extract_windows_naive(circuit)

    assert len(windows) == 3  # 3 windows
    new_circuit = xyz.QCircuit(3, map_gates=True)

    _, gates, _, _ = windows[0]
    assert len(gates) == 1  # 1 gate in the first window
    new_window = resynthesize_window(*windows[0])
    assert len(new_window) == 1  # 1 gate in the first window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[1]
    assert len(gates) == 4  # 4 gates in the second window
    new_window = resynthesize_window(*windows[1])
    assert len(new_window) == 3  # 3 gates in the second window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[2]
    assert len(gates) == 8  # 8 gate in the third window
    new_window = resynthesize_window(*windows[2])
    assert len(new_window) == 5  # 3 gates in the third window
    new_circuit.add_gates(new_window)


"""
      ┌─────────┐                                                                 
q0_0: ┤ Ry(π/2) ├───o────────────────o────────────────────────────────────────────
      ├─────────┴┐┌─┴─┐┌──────────┐  │      ┌───┐                                 
q0_1: ┤ Ry(3π/4) ├┤ X ├┤ Ry(-π/4) ├──┼──────┤ X ├──────────────────o──────────────
      ├──────────┤└───┘└──────────┘┌─┴─┐┌───┴───┴───┐┌──────────┐┌─┴─┐┌──────────┐
q0_2: ┤ Ry(5π/8) ├─────────────────┤ X ├┤ Ry(-3π/8) ├┤ Ry(3π/8) ├┤ X ├┤ Ry(-π/8) ├
      └──────────┘                 └───┘└───────────┘└──────────┘└───┘└──────────┘
"""


def test_windowing_2():
    circuit = xyz.QCircuit(3, map_gates=True)

    circuit.add_gate(RY(np.pi / 2, QBit(0)))
    circuit.add_gate(CRY(np.pi / 2, QBit(0), True, QBit(1)))
    circuit.add_gate(CRY(np.pi / 4, QBit(0), True, QBit(2)))
    circuit.add_gate(X(QBit(1)))
    circuit.add_gate(CRY(np.pi / 4, QBit(1), True, QBit(2)))

    assert circuit.get_cnot_cost() == 6  # 2 + 2 + 2

    windows = extract_windows_naive(circuit)

    assert len(windows) == 5  # 5 windows
    new_circuit = xyz.QCircuit(3, map_gates=True)

    _, gates, _, _ = windows[0]
    assert len(gates) == 1  # 1 gate in the first window
    new_window = resynthesize_window(*windows[0])
    assert len(new_window) == 1  # 1 gate in the first window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[1]
    assert len(gates) == 4  # 4 gates in the second window
    new_window = resynthesize_window(*windows[1])
    assert len(new_window) == 3  # 3 gates in the second window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[2]
    assert len(gates) == 4  # 4 gate in the third window
    new_window = resynthesize_window(*windows[2])
    assert len(new_window) == 3  # 3 gates in the third window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[3]
    assert len(gates) == 1  # 1 gate in the third window
    new_window = resynthesize_window(*windows[3])
    assert len(new_window) == 1  # 1 gates in the third window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[4]
    assert len(gates) == 4  # 4 gate in the third window
    new_window = resynthesize_window(*windows[4])
    assert len(new_window) == 3  # 3 gates in the third window
    new_circuit.add_gates(new_window)

    print(xyz.to_qiskit(new_circuit))


"""
      ┌─────────┐                                                                                  
q0_0: ┤ Ry(π/2) ├───o────────────────o─────────────────────────────o───────────────────────────────
      ├─────────┴┐┌─┴─┐┌──────────┐  │      ┌───┐                  │                               
q0_1: ┤ Ry(3π/4) ├┤ X ├┤ Ry(-π/4) ├──┼──────┤ X ├──────────────────┼────────────────o──────────────
      ├──────────┤└───┘└──────────┘┌─┴─┐┌───┴───┴───┐┌──────────┐┌─┴─┐┌──────────┐┌─┴─┐┌──────────┐
q0_2: ┤ Ry(5π/8) ├─────────────────┤ X ├┤ Ry(-3π/8) ├┤ Ry(5π/8) ├┤ X ├┤ Ry(-π/4) ├┤ X ├┤ Ry(-π/8) ├
      └──────────┘                 └───┘└───────────┘└──────────┘└───┘└──────────┘└───┘└──────────┘
"""


def test_windowing_3():
    circuit = xyz.QCircuit(3, map_gates=True)

    circuit.add_gate(RY(np.pi / 2, QBit(0)))
    circuit.add_gate(CRY(np.pi / 2, QBit(0), True, QBit(1)))
    circuit.add_gate(CRY(np.pi / 4, QBit(0), True, QBit(2)))
    circuit.add_gate(X(QBit(1)))
    circuit.add_gate(
        MCRY(np.pi / 4, [QBit(0), QBit(1)], [True, True], QBit(2))
    )

    assert circuit.get_cnot_cost() == 8  # 2 + 2 + 4

    windows = extract_windows_naive(circuit)

    assert len(windows) == 5  # 5 windows
    new_circuit = xyz.QCircuit(3, map_gates=True)

    _, gates, _, _ = windows[0]
    assert len(gates) == 1  # 1 gate in the first window
    new_window = resynthesize_window(*windows[0])
    assert len(new_window) == 1  # 1 gate in the first window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[1]
    assert len(gates) == 4  # 4 gates in the second window
    new_window = resynthesize_window(*windows[1])
    assert len(new_window) == 3  # 3 gates in the second window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[2]
    assert len(gates) == 4  # 4 gate in the third window
    new_window = resynthesize_window(*windows[2])
    assert len(new_window) == 3  # 3 gates in the third window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[3]
    assert len(gates) == 1  # 1 gate in the third window
    new_window = resynthesize_window(*windows[3])
    assert len(new_window) == 1  # 1 gates in the third window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[4]
    assert len(gates) == 8  # 8 gate in the third window
    new_window = resynthesize_window(*windows[4])
    assert len(new_window) == 5  # 8 gates in the third window
    new_circuit.add_gates(new_window)

    print(xyz.to_qiskit(new_circuit))


"""
      ┌─────────┐                                                   
q0_0: ┤ Ry(π/2) ├───o────────────────o──────────────────────────────
      ├─────────┴┐┌─┴─┐┌──────────┐  │                              
q0_1: ┤ Ry(3π/4) ├┤ X ├┤ Ry(-π/4) ├──┼───────────────o──────────────
      ├──────────┤└───┘└──────────┘┌─┴─┐┌─────────┐┌─┴─┐┌──────────┐
q0_2: ┤ Ry(3π/8) ├─────────────────┤ X ├┤ Ry(π/4) ├┤ X ├┤ Ry(-π/8) ├
      └──────────┘                 └───┘└─────────┘└───┘└──────────┘
"""


def test_windowing_4():
    circuit = xyz.QCircuit(3, map_gates=True)

    circuit.add_gate(RY(np.pi / 2, QBit(0)))
    circuit.add_gate(CRY(np.pi / 2, QBit(0), True, QBit(1)))
    circuit.add_gate(CRY(np.pi / 4, QBit(0), True, QBit(2)))
    circuit.add_gate(
        MCRY(np.pi / 4, [QBit(0), QBit(1)], [True, True], QBit(2))
    )

    assert circuit.get_cnot_cost() == 8  # 2 + 2 + 4

    windows = extract_windows_naive(circuit)

    assert len(windows) == 3  # 3 windows
    new_circuit = xyz.QCircuit(3, map_gates=True)

    _, gates, _, _ = windows[0]
    assert len(gates) == 1  # 1 gate in the first window
    new_window = resynthesize_window(*windows[0])
    assert len(new_window) == 1  # 1 gate in the first window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[1]
    assert len(gates) == 4  # 4 gates in the second window
    new_window = resynthesize_window(*windows[1])
    assert len(new_window) == 3  # 3 gates in the second window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[2]
    assert len(gates) == 12  # 12 gate in the third window
    new_window = resynthesize_window(*windows[2])
    assert len(new_window) == 5  # 3 gates in the third window
    new_circuit.add_gates(new_window)

    print(xyz.to_qiskit(new_circuit))


"""
      ┌─────────┐                                                   
q0_0: ┤ Ry(π/2) ├───o────────────────o──────────────────────────────
      ├─────────┴┐┌─┴─┐┌──────────┐  │                              
q0_1: ┤ Ry(3π/4) ├┤ X ├┤ Ry(-π/4) ├──┼───────────────o──────────────
      ├─────────┬┘└───┘└──────────┘┌─┴─┐┌─────────┐┌─┴─┐┌──────────┐
q0_2: ┤ Ry(π/4) ├──────────────────┤ X ├┤ Ry(π/8) ├┤ X ├┤ Ry(-π/8) ├
      └─────────┘                  └───┘└─────────┘└───┘└──────────┘
"""


def test_windowing_5():
    circuit = xyz.QCircuit(3, map_gates=True)

    circuit.add_gate(RY(np.pi / 2, QBit(0)))
    circuit.add_gate(CRY(np.pi / 2, QBit(0), True, QBit(1)))
    circuit.add_gate(CRY(np.pi / 4, QBit(0), True, QBit(2)))
    circuit.add_gate(
        MCRY(np.pi / 4, [QBit(0), QBit(1)], [True, False], QBit(2))
    )

    assert circuit.get_cnot_cost() == 8  # 2 + 2 + 4

    windows = extract_windows_naive(circuit)

    assert len(windows) == 3  # 3 windows
    new_circuit = xyz.QCircuit(3, map_gates=True)

    _, gates, _, _ = windows[0]
    assert len(gates) == 1  # 1 gate in the first window
    new_window = resynthesize_window(*windows[0])
    assert len(new_window) == 1  # 1 gate in the first window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[1]
    assert len(gates) == 4  # 4 gates in the second window
    new_window = resynthesize_window(*windows[1])
    assert len(new_window) == 3  # 3 gates in the second window
    new_circuit.add_gates(new_window)

    _, gates, _, _ = windows[2]
    assert len(gates) == 12  # 12 gate in the third window
    new_window = resynthesize_window(*windows[2])
    assert len(new_window) == 5  # 3 gates in the third window
    new_circuit.add_gates(new_window)

    print(xyz.to_qiskit(new_circuit))
