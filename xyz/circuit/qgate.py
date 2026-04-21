from collections import namedtuple
from typing import Dict, List, Tuple

import numpy as np
import scipy as sp

from .qstate import QState
from xyz.gates.types import (
    QGateType as QGateType,
    QBit as QBit,
    RotationTrait,
    UnitaryTrait,
    ControlledTrait,
    MultiControlledTrait,
)
from xyz.decomposition.zyz import (
    to_special_unitary,
    unitary_zyz_decomposition,
)
from xyz.decomposition.gray_code import (
    find_thetas,
    decompose_mcry,
    control_sequence_to_gates,
)
from xyz.gates.base import Gate

# Phase 2: legacy trait class names. Phase 3 deletes these once all
# concrete gates reference the Trait names directly.
UnitaryGate = UnitaryTrait
RotationGate = RotationTrait
ControlledGate = ControlledTrait
MultiControlledGate = MultiControlledTrait


# Phase 2: QGate becomes an alias for the new ABC; Phase 3 deletes the
# alias and updates callers to Gate directly.
QGate = Gate




class MultiRotationGate:
    """Class method for creating a new rotation gate ."""

    def __init__(self, thetas: List[float]) -> None:
        self.thetas = thetas






class BasicGate(QGate):
    def __init__(self, qgate_type: QGateType, target_qubit: QBit) -> None:
        QGate.__init__(self, qgate_type)
        if not isinstance(target_qubit, QBit):
            print(f"WARNING: target_qubit {target_qubit} is not a QBit")
        assert isinstance(target_qubit, QBit)
        self.target_qubit: QBit = target_qubit

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("This method is not implemented")

    def cnot_cost(self) -> int:
        raise NotImplementedError("This method is not implemented")

    def qubits(self) -> List[QBit]:
        raise NotImplementedError("This method is not implemented")


class AdvancedGate(QGate):

    def __init__(self, qgate_type: QGateType) -> None:
        QGate.__init__(self, qgate_type)

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("This method is not implemented")


class CRX(RotationGate, BasicGate, ControlledGate):
    def __init__(
        self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CRX, target_qubit)
        RotationGate.__init__(self, theta)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        return f"CRX({self.theta:0.02f}, {self.control_qubits[0]}[{self.phase}])"

    def cnot_cost(self) -> int:
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def apply(self, qstate: "QState") -> "QState":
        scale = float(np.cos(self.theta / 2))
        out = {}
        for idx, weight in qstate.index_to_weight.items():
            out[idx] = weight * scale if self.is_enabled(idx) else weight
        return QState(out, qstate.num_qubits)


class CRY(RotationGate, BasicGate, ControlledGate):
    """Controlled Y Rotation."""

    def __init__(
        self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CRY, target_qubit)
        RotationGate.__init__(self, theta)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        control_str = "" if self.phase == 1 else "~"
        return f"C({control_str}{self.control_qubits[0]})RY({self.target_qubit}:{self.theta:0.02f})"

    def cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate."""
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def conjugate(self) -> "CRY":
        return CRY(-self.theta, self.control_qubits[0], self.phase, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {idx: 0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            # no rotation
            if not self.is_enabled(idx):
                index_to_weight[idx] = qstate.index_to_weight[idx]
                continue
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0

            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] += weight * np.sin(self.theta / 2)
            else:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] -= weight * np.sin(self.theta / 2)
        return QState(index_to_weight, qstate.num_qubits)


class CRZ(RotationGate, BasicGate, ControlledGate):

    def __init__(
        self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CRZ, target_qubit)
        RotationGate.__init__(self, theta)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        return f"CRZ({self.theta:0.02f}, {self.control_qubits[0]}[{self.phase}])"

    def cnot_cost(self) -> int:
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def apply(self, qstate: "QState") -> "QState":
        scale = float(np.cos(self.theta / 2))
        out = {}
        for idx, weight in qstate.index_to_weight.items():
            out[idx] = weight * scale if self.is_enabled(idx) else weight
        return QState(out, qstate.num_qubits)


class CU(BasicGate, UnitaryGate, ControlledGate):

    def __init__(
        self, unitary: np.ndarray, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CU, target_qubit)
        UnitaryGate.__init__(self, unitary)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        phase_str = "" if self.phase == 1 else "~"
        return f"C({phase_str}{self.control_qubits[0]})U({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def apply(self, qstate: "QState") -> "QState":
        m = np.real(self.unitary)
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            if not self.is_enabled(idx):
                index_to_weight[idx] += weight
                continue
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * m[0, 0]
                index_to_weight[rdx] += weight * m[1, 0]
            else:
                index_to_weight[idx] += weight * m[1, 1]
                index_to_weight[rdx] += weight * m[0, 1]
        return QState(index_to_weight, qstate.num_qubits)


class CX(BasicGate, ControlledGate):

    def __init__(self, control_qubit: QBit, phase: int, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.CX, target_qubit)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        phase_str = "" if self.phase == 1 else "~"
        return f"C({phase_str}{self.control_qubits[0]})X({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 1

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def conjugate(self) -> "CX":
        return CX(self.control_qubits[0], self.phase, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx, weight in qstate.index_to_weight.items():
            reversed_idx = idx ^ (1 << self.target_qubit.index)
            if self.is_enabled(idx):
                index_to_weight[reversed_idx] = weight
            else:
                index_to_weight[idx] = weight
        return QState(index_to_weight, qstate.num_qubits)


class MCMY(AdvancedGate):

    def __init__(
        self,
        rotation_table: List[float],
        control_qubits: List[QBit],
        target_qubit: QBit,
    ) -> None:
        AdvancedGate.__init__(self, QGateType.MCMY)

        assert isinstance(target_qubit, QBit)
        assert isinstance(control_qubits, list)

        self.target_qubit: QBit = target_qubit
        self.control_qubits: QBit = control_qubits
        self.rotation_table: List[float] = rotation_table

    def __str__(self) -> str:
        control_qubit_str = ",".join([str(qubit) for qubit in self.control_qubits])
        return f"MCMY({control_qubit_str})"

    def cnot_cost(self) -> int:
        return 1 << len(self.control_qubits)

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def apply(self, qstate: "QState") -> "QState":
        # Pattern k (binary over controls) triggers RY(rotation_table[k])
        # on the target qubit.
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            pattern = 0
            for i, ctrl in enumerate(self.control_qubits):
                pattern |= ((idx >> ctrl.index) & 1) << i
            theta = self.rotation_table[pattern]
            c = np.cos(theta / 2)
            s = np.sin(theta / 2)
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * c
                index_to_weight[rdx] += weight * s
            else:
                index_to_weight[idx] += weight * c
                index_to_weight[rdx] += -weight * s
        return QState(index_to_weight, qstate.num_qubits)


class MCRY(RotationGate, BasicGate, MultiControlledGate):

    def __init__(
        self,
        theta: float,
        control_qubits: List[QBit],
        phases: List[int],
        target_qubit: QBit,
    ) -> None:
        BasicGate.__init__(self, QGateType.MCRY, target_qubit)
        RotationGate.__init__(self, theta)
        MultiControlledGate.__init__(self, control_qubits, phases)

    def __str__(self) -> str:
        control_str = "+".join(
            [
                str(qubit) + f"[{phase}]"
                for qubit, phase in zip(self.control_qubits, self.phases)
            ]
        )
        return f"MCRY({self.target_qubit.index},{self.theta:0.02f}, {control_str})"

    def cnot_cost(self) -> int:
        """Returns the CNOT cost of the gate."""
        from xyz.gates.cost_tables import MCRY_CNOT_COST
        n = len(self.control_qubits)
        if n not in MCRY_CNOT_COST:
            raise ValueError(
                f"MCRY cost table has no entry for n_controls={n}"
            )
        return MCRY_CNOT_COST[n]

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def conjugate(self) -> "MCRY":
        """Conjugate the gate ."""
        return MCRY(-self.theta, self.control_qubits, self.phases, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        """Apply the gate to the state."""
        index_to_weight = {idx: 0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            # no rotation
            if not self.is_enabled(idx):
                index_to_weight[idx] = qstate.index_to_weight[idx]
                continue
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0

            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] += weight * np.sin(self.theta / 2)
            else:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] -= weight * np.sin(self.theta / 2)
        return QState(index_to_weight, qstate.num_qubits)


class MULTIPLEXY(AdvancedGate):

    def __init__(
        self, theta0: float, theta1: float, control_qubit: QBit, target_qubit: QBit
    ) -> None:
        AdvancedGate.__init__(self, QGateType.MULTIPLEX_Y)

        assert isinstance(target_qubit, QBit)
        assert isinstance(control_qubit, QBit)

        self.target_qubit: QBit = target_qubit
        self.control_qubit: QBit = control_qubit
        self.control_qubits: List[QBit] = [control_qubit]
        self.theta0: float = theta0
        self.theta1: float = theta1

    def __str__(self) -> str:
        return f"MULTIPLEXY({self.theta0}, {self.theta1}, {self.control_qubit}, {self.target_qubit})"

    def cnot_cost(self) -> int:
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def apply(self, qstate: "QState") -> "QState":
        ctrl = self.control_qubits[0]
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            theta = self.theta1 if (idx >> ctrl.index) & 1 else self.theta0
            c = np.cos(theta / 2)
            s = np.sin(theta / 2)
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * c
                index_to_weight[rdx] += weight * s
            else:
                index_to_weight[idx] += weight * c
                index_to_weight[rdx] += -weight * s
        return QState(index_to_weight, qstate.num_qubits)


class RX(RotationGate, BasicGate):

    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RX, target_qubit)
        RotationGate.__init__(self, theta)

    def __str__(self) -> str:
        return f"RX({self.theta:0.02f})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: "QState") -> "QState":
        # Real projection of RX(θ) on a real-amplitude state is scalar
        # multiplication by cos(θ/2). See Phase 2 plan Task 5 math note.
        scale = float(np.cos(self.theta / 2))
        return QState(
            {idx: w * scale for idx, w in qstate.index_to_weight.items()},
            qstate.num_qubits,
        )


class RY(RotationGate, BasicGate):

    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RY, target_qubit)
        RotationGate.__init__(self, theta)

    def __str__(self) -> str:
        return f"RY({self.target_qubit}, {self.theta:0.02f})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def conjugate(self) -> "RY":
        return RY(-self.theta, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {idx: 0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] += weight * np.sin(self.theta / 2)
            else:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] -= weight * np.sin(self.theta / 2)
        return QState(index_to_weight, qstate.num_qubits)


class RZ(RotationGate, BasicGate):
    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RZ, target_qubit)
        RotationGate.__init__(self, theta)

    def __str__(self) -> str:
        return f"RZ({self.theta:0.02f})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: "QState") -> "QState":
        # RZ's real projection on a real-amplitude state matches RX's:
        # both reduce to cos(θ/2)·ψ. See Phase 2 plan Task 5 math note.
        scale = float(np.cos(self.theta / 2))
        return QState(
            {idx: w * scale for idx, w in qstate.index_to_weight.items()},
            qstate.num_qubits,
        )


class U(UnitaryGate, BasicGate):
    def __init__(self, unitary: np.ndarray, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.U, target_qubit)
        UnitaryGate.__init__(self, unitary)

    def __str__(self) -> str:
        return "U"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: "QState") -> "QState":
        # Apply Re(U) as a 2×2 real matrix on the two-amplitude subspace
        # indexed by the target qubit's bit.
        m = np.real(self.unitary)
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * m[0, 0]
                index_to_weight[rdx] += weight * m[1, 0]
            else:
                index_to_weight[idx] += weight * m[1, 1]
                index_to_weight[rdx] += weight * m[0, 1]
        return QState(index_to_weight, qstate.num_qubits)


class X(BasicGate):
    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.X, target_qubit)

    def __str__(self) -> str:
        return f"X({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx in qstate.index_set:
            reversed_idx = idx ^ (1 << self.target_qubit.index)
            index_to_weight[reversed_idx] = qstate.index_to_weight[idx]
        return QState(index_to_weight, qstate.num_qubits)


class Z(BasicGate):

    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.Z, target_qubit)

    def __str__(self) -> str:
        return f"Z({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx, weight in qstate.index_to_weight.items():
            if idx & (1 << self.target_qubit.index):
                index_to_weight[idx] = -weight
            else:
                index_to_weight[idx] = weight
        return QState(index_to_weight, qstate.num_qubits)


def map_muxy(gate: MULTIPLEXY) -> List[QGate]:
    assert gate.qgate_type == QGateType.MULTIPLEX_Y
    rotation_table = [gate.theta0, gate.theta1]
    control_sequence = decompose_mcry(rotation_table)
    gates = control_sequence_to_gates(
        control_sequence, [gate.control_qubit], gate.target_qubit
    )
    return gates


def map_mcry(gate: QGate) -> List[QGate]:
    match gate.qgate_type:
        case QGateType.MCRY:
            control_qubits = gate.control_qubits
            phases = gate.phases
            target_qubit = gate.target_qubit

        case QGateType.CRY:
            control_qubits = [gate.control_qubits[0]]
            phases = [gate.phase]
            target_qubit = gate.target_qubit

        case _:
            raise ValueError("Not a MCRY gate")
    # we prepare the rotation table
    rotation_table = np.zeros(2 ** (len(control_qubits)))
    rotated_index = 0
    for i, controlled_by_one in enumerate(phases):
        if controlled_by_one is True:
            rotated_index += 2**i

    # only rotate the target qubit if the control qubits are in the positive phase
    rotation_table[rotated_index] = gate.theta
    control_sequence = decompose_mcry(rotation_table)
    gates = control_sequence_to_gates(control_sequence, control_qubits, target_qubit)
    return gates




def map_mcmy(gate: MCMY) -> List[QGate]:
    """Convert a MCMY gate into a list of gates ."""
    rotation_table = gate.rotation_table
    control_sequence = decompose_mcry(rotation_table=rotation_table)
    gates = control_sequence_to_gates(
        control_sequence,
        gate.control_qubits,
        gate.target_qubit,
    )
    return gates


def theta_to_unitary(theta: float):
    """Converts theta to a unitary unitary gate ."""
    raw_matrix = np.array(
        [
            [np.cos(theta / 2), -np.sin(theta / 2)],
            [np.sin(theta / 2), np.cos(theta / 2)],
        ]
    )
    return raw_matrix




def unitary_convert(unitary: np.ndarray, coef: float, signal: int):
    param = 1 / np.abs(coef)
    values, vectors = np.linalg.eig(unitary)
    updated_unitary = (
        np.power(values[0] + 0j, param) * vectors[:, [0]] @ vectors[:, [0]].conj().T
    )
    updated_unitary = (
        updated_unitary
        + np.power(values[1] + 0j, param) * vectors[:, [1]] @ vectors[:, [1]].conj().T
    )
    if signal < 0:
        updated_unitary = np.linalg.inv(updated_unitary)
    return updated_unitary


def map_mcry_linear(mcry_gate: MCRY) -> List[QGate]:
    assert mcry_gate.qgate_type == QGateType.MCRY

    # we first preprocess the relavant qubits
    qubit_list = mcry_gate.control_qubits + [mcry_gate.target_qubit]
    num_qubits = len(qubit_list)

    # special case for single qubit
    if num_qubits == 1:
        gates = []
        gate = RY(mcry_gate.theta, qubit_list[0])
        gates.append(gate)
        return gates

    # special case for two qubits
    # if num_qubits == 2:
    #     gates = __map_mcry(mcry_gate)
    #     return gates

    # now we handle the general case
    def convert_rec(
        unitary: np.ndarray, num_qubits: int, is_first: bool = True, step: int = 1
    ):
        nonlocal qubit_list
        pairs = namedtuple("pairs", ["control", "target"])
        if step == 1:
            start = 0
            reverse = True
        else:
            start = 1
            reverse = False
        qubit_pairs = [
            pairs(control, target)
            for target in range(num_qubits)
            for control in range(start, target)
        ]
        qubit_pairs.sort(key=lambda e: e.control + e.target, reverse=reverse)
        gates = []
        for pair in qubit_pairs:
            exponent = pair.target - pair.control
            if pair.control == 0:
                exponent = exponent - 1
            param = 2**exponent
            signal = -1 if (pair.control == 0 and not is_first) else 1
            signal = signal * step

            if pair.target == num_qubits - 1 and is_first:
                updated_unitary = unitary_convert(unitary, param, signal)
                gate = CU(
                    updated_unitary,
                    qubit_list[pair.control],
                    True,
                    qubit_list[pair.target],
                )
                gates.append(gate)
            else:
                gate = CRX(
                    signal * np.pi / param,
                    qubit_list[pair.control],
                    True,
                    qubit_list[pair.target],
                )
                gates.append(gate)

        return gates

    unitary = theta_to_unitary(mcry_gate.theta)

    gates = []
    # frist we consider the control phases
    for phase, control_qubit in zip(mcry_gate.phases, mcry_gate.control_qubits):
        if phase == 0:
            gate = X(control_qubit)
            gates.append(gate)

    gates_c1 = convert_rec(unitary, num_qubits)
    gates_c2 = convert_rec(unitary, num_qubits, step=-1)
    gates_c3 = convert_rec(unitary, num_qubits - 1, is_first=False)
    gates_c4 = convert_rec(unitary, num_qubits - 1, is_first=False, step=-1)

    for gate in gates_c1:
        gates.append(gate)
    for gate in gates_c2:
        gates.append(gate)
    for gate in gates_c3:
        gates.append(gate)
    for gate in gates_c4:
        gates.append(gate)

    # frist we consider the control phases
    for phase, control_qubit in zip(mcry_gate.phases, mcry_gate.control_qubits):
        if phase == 0:
            gate = X(control_qubit)
            gates.append(gate)
    return gates
