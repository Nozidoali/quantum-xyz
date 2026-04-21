"""Public gate API: re-exports every concrete gate and the Gate ABC."""

from xyz.gates.base import AdvancedGate, BasicGate, Gate, MultiRotationGate
from xyz.gates.controlled import CRX, CRY, CRZ, CU, CX
from xyz.gates.multi_controlled import MCMY, MCRY, MULTIPLEXY
from xyz.gates.single import RX, RY, RZ, U, X, Z
from xyz.gates.types import (
    ControlledTrait,
    MultiControlledTrait,
    QBit,
    QGateType,
    RotationTrait,
    UnitaryTrait,
)

# Backwards-compat legacy names (Phase 2 aliased these; external scripts
# may still import them).
QGate = Gate
UnitaryGate = UnitaryTrait
RotationGate = RotationTrait
ControlledGate = ControlledTrait
MultiControlledGate = MultiControlledTrait

__all__ = [
    "AdvancedGate", "BasicGate", "Gate", "MultiRotationGate",
    "CRX", "CRY", "CRZ", "CU", "CX",
    "MCMY", "MCRY", "MULTIPLEXY",
    "RX", "RY", "RZ", "U", "X", "Z",
    "ControlledTrait", "MultiControlledTrait",
    "QBit", "QGateType",
    "RotationTrait", "UnitaryTrait",
    # legacy aliases
    "QGate",
    "UnitaryGate", "RotationGate", "ControlledGate", "MultiControlledGate",
]
