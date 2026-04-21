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






from xyz.gates.single import RX, RY, RZ, U, X, Z  # noqa: F401
from xyz.gates.controlled import CRX, CRY, CRZ, CU, CX  # noqa: F401
from xyz.gates.multi_controlled import MCMY, MCRY, MULTIPLEXY  # noqa: F401

from xyz.decomposition.mcry import (
    map_muxy,
    map_mcry,
    map_mcmy,
    map_mcry_linear,
    theta_to_unitary,
    unitary_convert,
)
