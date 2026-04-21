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


from xyz.gates.single import RX, RY, RZ, U, X, Z  # noqa: F401
from xyz.gates.controlled import CRX, CRY, CRZ, CU, CX  # noqa: F401

from xyz.decomposition.mcry import (
    map_muxy,
    map_mcry,
    map_mcmy,
    map_mcry_linear,
    theta_to_unitary,
    unitary_convert,
)
