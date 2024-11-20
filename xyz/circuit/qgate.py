from enum import Enum, auto
import numpy as np
from typing import List, Tuple, Dict
from .qstate import QState
from numpy.linalg import det
import scipy as sp
from collections import namedtuple


class QGateType(Enum):

    U = auto()
    CU = auto()
    MCU = auto()

    X = auto()
    Y = auto()
    Z = auto()

    CY = auto()
    CZ = auto()
    CX = auto()

    # single qubit rotation gates
    RX = auto()
    RY = auto()
    RZ = auto()

    # controlled rotation gates
    CRX = auto()
    CRY = auto()
    CRZ = auto()

    MCRY = auto()

    MULTIPLEX_Y = auto()

    MCMY = auto()

    NONE = auto()


class QBit:
    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self) -> str:
        return f"q{self.index}"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, QBit):
            return self.index == __value.index
        return False

    def __hash__(self) -> int:
        return hash(self.index)


def to_special_unitary(matrix: np.ndarray) -> np.ndarray:
    """Convert gate tensor to the special unitary group."""
    rank = matrix.shape[0]
    matrix_ = matrix / det(matrix) ** (1 / rank)
    return matrix_


def unitary_zyz_decomposition(matrix: np.ndarray):
    """
    Returns the Euler Z-Y-Z decomposition of a local 1-qubit gate.
    """
    U = to_special_unitary(matrix)
    if abs(U[0, 0]) > abs(U[1, 0]):
        theta1 = 2 * np.arccos(min(abs(U[0, 0]), 1))
    else:
        theta1 = 2 * np.arcsin(min(abs(U[1, 0]), 1))
    cos_halftheta1 = np.cos(theta1 / 2)
    if not np.isclose(cos_halftheta1, 0.0):
        phase = U[1, 1] / cos_halftheta1
        theta0_plus_theta2 = 2 * np.arctan2(np.imag(phase), np.real(phase))
    else:
        theta0_plus_theta2 = 0.0
    sin_halftheta1 = np.sin(theta1 / 2)
    if not np.isclose(sin_halftheta1, 0.0):
        phase = U[1, 0] / sin_halftheta1
        theta0_sub_theta2 = 2 * np.arctan2(np.imag(phase), np.real(phase))
    else:
        theta0_sub_theta2 = 0.0
    theta0 = (theta0_plus_theta2 + theta0_sub_theta2) / 2
    theta2 = (theta0_plus_theta2 - theta0_sub_theta2) / 2
    # this is very important, otherwise the result will be wrong
    if np.isclose(theta1, 0.0, atol=1e-6):
        theta2 = theta0 + theta2
        theta1 = 0.0
        theta0 = 0.0
    if theta0 < 0:
        theta0 += 2 * np.pi
    if theta1 < 0:
        theta1 += 2 * np.pi
    if theta2 < 0:
        theta2 += 2 * np.pi

    return theta0, theta1, theta2


class UnitaryGate:
    def __init__(self, unitary: np.ndarray) -> None:
        self.unitary = unitary
        self.alpha, self.beta, self.gamma = unitary_zyz_decomposition(unitary)

    def get_unitary(self) -> float:
        return self.unitary

    def get_alpha(self) -> float:
        return self.alpha

    def get_beta(self) -> float:
        return self.beta

    def get_gamma(self) -> float:

        return self.gamma

    def is_z_trivial(self) -> bool:
        is_alpha_trivial = np.isclose(self.alpha, 0) or np.isclose(
            self.alpha, 2 * np.pi
        )
        is_gamma_trivial = np.isclose(self.gamma, 0) or np.isclose(
            self.gamma, 2 * np.pi
        )
        return is_alpha_trivial and is_gamma_trivial

    def is_z_trivial_not(self) -> bool:
        is_alpha_trivial = np.isclose(self.alpha, np.pi)
        is_gamma_trivial = np.isclose(self.gamma, np.pi)
        return is_alpha_trivial and is_gamma_trivial


class QGate:
    def __init__(self, qgate_type: QGateType) -> None:
        self.qgate_type = qgate_type

    def __str__(self) -> str:
        return self.qgate_type.name

    def get_qgate_type(self) -> QGateType:
        return self.qgate_type


class RotationGate:
    def __init__(self, theta: float) -> None:
        self.theta = theta

    def is_trivial(self) -> bool:
        return np.isclose(self.theta, 0) or np.isclose(self.theta, 2 * np.pi)

    def is_pi(self) -> bool:
        return np.isclose(self.theta, np.pi) or np.isclose(self.theta, -np.pi)

    def get_theta(self) -> float:
        return self.theta


class MultiRotationGate:
    """Class method for creating a new rotation gate ."""

    def __init__(self, thetas: List[float]) -> None:
        self.thetas = thetas


class ControlledGate:
    def __init__(self, control_qubit: QBit, phase: int = 1) -> None:
        self.phase = phase

        assert isinstance(control_qubit, QBit)
        self.control_qubit = control_qubit

    def get_control_qubit(self) -> QBit:
        """Returns the control qubit ."""
        return self.control_qubit

    def get_control_qubits(self) -> List[QBit]:
        """Returns the control qubits ."""
        return [self.control_qubit]

    def get_phase(self) -> int:
        """Returns the phase ."""
        return self.phase

    def is_enabled(self, index: int):
        """Returns True if the control qubit is enabled ."""
        return (index >> self.control_qubit.index) & 1 == self.phase


class MultiControlledGate:
    def __init__(self, control_qubits: List[QBit], phases: List[int]) -> None:
        self.control_qubits = control_qubits[:]
        self.phases = list(phases)[:]

    def has_zero_controls(self) -> bool:
        """Returns True if any control qubits are zero ."""
        return len(self.control_qubits) == 0

    def has_one_control(self) -> bool:
        """Returns True if this instruction has one control ."""
        return len(self.control_qubits) == 1

    def get_control_qubits(self) -> List[QBit]:
        """Returns the control qubits ."""
        return self.control_qubits

    def get_phases(self) -> List[int]:
        """Returns the phases ."""
        return self.phases

    def is_enabled(self, index: int) -> bool:
        """Returns True if the control qubits are enabled ."""
        for control_qubit, phase in zip(self.control_qubits, self.phases):
            if (index >> control_qubit.index) & 1 != phase:
                return False
        return True
    
    def set_control_qubits(self, control_qubits: List[QBit]) -> None:
        self.control_qubits = list(control_qubits)
    
    def set_phases(self, phases: List[int]) -> None:
        self.phases = list(phases)

class BasicGate(QGate):
    def __init__(self, qgate_type: QGateType, target_qubit: QBit) -> None:
        QGate.__init__(self, qgate_type)
        if not isinstance(target_qubit, QBit):
            print(f"WARNING: target_qubit {target_qubit} is not a QBit")
        assert isinstance(target_qubit, QBit)
        self.target_qubit: QBit = target_qubit

    def get_target_qubit(self) -> QBit:
        return self.target_qubit

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("This method is not implemented")

    def get_cnot_cost(self) -> int:
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
        return f"CRX({self.theta:0.02f}, {self.control_qubit}[{self.phase}])"

    def get_cnot_cost(self) -> int:
        return 2

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("CRX gate is not implemented yet")


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
        return f"C({control_str}{self.control_qubit})RY({self.target_qubit}:{self.theta:0.02f})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate."""
        return 2

    def conjugate(self) -> "CRY":
        return CRY(-self.theta, self.control_qubit, self.phase, self.target_qubit)

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
        return f"CRZ({self.theta:0.02f}, {self.control_qubit}[{self.phase}])"

    def get_cnot_cost(self) -> int:
        return 2

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("CRZ gate is not implemented yet")


class CU(BasicGate, UnitaryGate, ControlledGate):

    def __init__(
        self, unitary: np.ndarray, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CU, target_qubit)
        UnitaryGate.__init__(self, unitary)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        phase_str = "" if self.phase == 1 else "~"
        return f"C({phase_str}{self.control_qubit})U({self.target_qubit})"

    def get_cnot_cost(self) -> int:
        return 2

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("CU gate is not implemented yet")


class CX(BasicGate, ControlledGate):

    def __init__(self, control_qubit: QBit, phase: int, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.CX, target_qubit)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        phase_str = "" if self.phase == 1 else "~"
        return f"C({phase_str}{self.control_qubit})X({self.target_qubit})"

    def get_cnot_cost(self) -> int:
        return 1

    def conjugate(self) -> "CX":
        return CX(self.control_qubit, self.phase, self.target_qubit)

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

    def get_cnot_cost(self) -> int:
        return 1 << len(self.control_qubits)

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("MCMY gate is not implemented yet")


MCRY_CNOT_COST = {
    "0": 0,
    "1": 2,
    "2": 4,
    "3": 8,
    "4": 16,
    "5": 32,
    "6": 64,
    "7": 128,
    "8": 226,
    "9": 290,
    "10": 362,
    "11": 442,
    "12": 530,
    "13": 626,
    "14": 730,
    "15": 842,
    "16": 962,
    "17": 1090,
    "18": 1226,
    "19": 1370,
    "20": 1522,
    "21": 1682,
    "22": 1850,
    "23": 2026,
    "24": 2210,
    "25": 2402,
    "26": 2602,
    "27": 2810,
    "28": 3026,
}


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

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate."""
        index_str = str(len(self.control_qubits))
        if index_str not in MCRY_CNOT_COST:
            raise ValueError(
                f"len(self.control_qubits) = {len(self.control_qubits)} is not supported"
            )
        return MCRY_CNOT_COST[index_str]

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
        self.theta0: float = theta0
        self.theta1: float = theta1

    def __str__(self) -> str:
        return f"MULTIPLEXY({self.theta0}, {self.theta1}, {self.control_qubit}, {self.target_qubit})"

    def get_cnot_cost(self) -> int:
        return 2

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("MULTIPLEXY gate is not implemented yet")


class RX(RotationGate, BasicGate):

    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RX, target_qubit)
        RotationGate.__init__(self, theta)

    def __str__(self) -> str:
        return f"RX({self.theta:0.02f})"

    def get_cnot_cost(self) -> int:
        return 0

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("This method is not implemented")


class RY(RotationGate, BasicGate):

    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RY, target_qubit)
        RotationGate.__init__(self, theta)

    def __str__(self) -> str:
        return f"RY({self.target_qubit}, {self.theta:0.02f})"

    def get_cnot_cost(self) -> int:
        return 0

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

    def get_cnot_cost(self) -> int:
        return 0

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("This method is not implemented")


class U(UnitaryGate, BasicGate):
    def __init__(self, unitary: np.ndarray, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.U, target_qubit)
        UnitaryGate.__init__(self, unitary)

    def __str__(self) -> str:
        return "U"

    def get_cnot_cost(self) -> int:
        return 0

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("This method is not implemented")


class X(BasicGate):
    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.X, target_qubit)

    def __str__(self) -> str:
        return f"X({self.target_qubit})"

    def get_cnot_cost(self) -> int:
        return 0

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

    def get_cnot_cost(self) -> int:
        return 0

    def apply(self, qstate: "QState") -> "QState":
        index_to_weight = {}
        for idx in qstate.index_set:
            if idx & (1 << self.target_qubit.index):
                index_to_weight[idx] = -qstate.index_to_weight[idx]
        raise NotImplementedError("Z gate not implemented")


def map_muxy(gate: MULTIPLEXY) -> List[QGate]:
    assert gate.type == QGateType.MULTIPLEX_Y
    rotation_table = [gate.theta0, gate.theta1]
    control_sequence = decompose_mcry(rotation_table)
    gates = control_sequence_to_gates(
        control_sequence, [gate.control_qubit], gate.target_qubit
    )
    return gates


def map_mcry(gate: QGate) -> List[QGate]:
    match gate.get_qgate_type():
        case QGateType.MCRY:
            control_qubits = gate.control_qubits
            phases = gate.phases
            target_qubit = gate.target_qubit

        case QGateType.CRY:
            control_qubits = [gate.control_qubit]
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

# decomposition
def find_thetas(alphas):
    size = len(alphas)
    # for the gray code matrix
    gray_code_coefficient_matrix = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            #  The exponent is the bit-wise inner product of the binary vectors for the standard binary code representation of the integer i (bi) and the binary representation of the i th value of the gray code up to a value of 2) The j th value of the gray code is calculated using the bit-wise XOR of the unsigned binary j and a single shift right of the value of j , like so: ”j XOR (j>>1)” for C++ code
            bitwise_inner_product = bin(i & (j ^ (j >> 1))).count("1")
            gray_code_coefficient_matrix[i, j] = (-1) ** bitwise_inner_product

    thetas = sp.linalg.solve(gray_code_coefficient_matrix, alphas)

    return thetas


def decompose_mcry(rotation_table: list):
    num_controls = int(np.log2(len(rotation_table)))
    assert num_controls > 0, "The number of controls must be greater than 0"

    alphas = rotation_table[:]
    thetas = find_thetas(alphas)

    # return a list of control sequences
    control_sequence: list = []
    prev_gray_code = 0

    for i, theta in enumerate(thetas):
        # get the bit that changed in the i of gray code
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 0, 2, 0, 1, 0, 2, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        curr_gray_code = ((i + 1) ^ ((i + 1) >> 1)) if i < (2**num_controls) - 1 else 0
        diff = curr_gray_code ^ prev_gray_code
        # print(f"i: {i}, curr_gray_code: {curr_gray_code}, prev_gray_code: {prev_gray_code}, diff: {diff}")
        prev_gray_code = curr_gray_code
        control_id = int(np.log2(diff))
        control_sequence.append((theta, control_id))

    return control_sequence


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


def control_sequence_to_gates(
    control_sequence: list, control_qubits: List[QBit], target_qubit: QBit
) -> List[QGate]:
    gates: List[QGate] = []
    for control in control_sequence:
        rotation_theta, control_id = control
        gates.append(RY(rotation_theta, target_qubit))
        gates.append(CX(control_qubits[control_id], 1, target_qubit))
    return gates


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
    assert mcry_gate.get_qgate_type() == QGateType.MCRY

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

    unitary = theta_to_unitary(mcry_gate.get_theta())

    gates = []
    # frist we consider the control phases
    for phase, control_qubit in zip(mcry_gate.get_phases(), mcry_gate.control_qubits):
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
    for phase, control_qubit in zip(mcry_gate.get_phases(), mcry_gate.control_qubits):
        if phase == 0:
            gate = X(control_qubit)
            gates.append(gate)
    return gates
