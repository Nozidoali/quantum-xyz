import json

from typing import List, Tuple
import numpy as np
import random
from itertools import combinations

# the merge uncertainty, if the difference between the two angles is less than
# this value, we consider them to be the same
MERGE_UNCERTAINTY = 1e-12

N_DIGITS = 2

DISABLE_ASTAR = True


class QState:
    """Class method for QState"""

    def __init__(self, index_to_weight: dict, num_qubit: int) -> None:
        self.num_qubits = num_qubit

        self.index_to_weight = {}
        for index, weight in index_to_weight.items():
            if not np.isclose(weight, 0, atol=MERGE_UNCERTAINTY):
                self.index_to_weight[index] = weight
        self.index_set = self.index_to_weight.keys()

        self.sparsity: int = len(index_to_weight)
        self.supports: list = None

    def __deepcopy__(self, memo):
        return QState(self.index_to_weight, self.num_qubits)

    def get_supports(self) -> List[int]:
        """Return the support of the state ."""
        if self.supports is not None:
            return self.supports[:]
        signatures = self.get_qubit_signatures()
        qubit_indices = []
        for qubit, pattern in enumerate(signatures):
            if pattern != 0:
                qubit_indices.append(qubit)
        self.supports = qubit_indices
        return qubit_indices

    def get_sparsity(self) -> int:
        """Return the sparsity of the state ."""
        return len(self.index_set)

    def to_value(self) -> int:
        """Return the value of the state ."""
        value = 0
        for basis in self.index_set:
            value |= 1 << basis
        return value

    def get_qubit_signatures(self) -> List[int]:
        """Transpose the state array ."""
        signatures = [0 for i in range(self.num_qubits)]
        for _, value in enumerate(self.index_set):
            for j in range(self.num_qubits):
                signatures[j] = signatures[j] << 1 | (value >> j & 1)
        return signatures

    def get_const1_signature(self) -> int:
        """Returns the number of signed unsigned signatures ."""
        return (1 << len(self.index_set)) - 1

    def cofactors(self, pivot_qubit: int) -> Tuple["QState", "QState"]:
        """Returns the cofactors of the given qubit ."""

        index_to_weight0 = {}
        index_to_weight1 = {}

        total_weights0 = 0
        total_weights1 = 0

        for idx in self.index_set:
            if (idx >> pivot_qubit) & 1 == 0:
                index_to_weight0[idx] = self.index_to_weight[idx]
                total_weights0 += self.index_to_weight[idx]
            else:
                index_to_weight1[idx ^ (1 << pivot_qubit)] = self.index_to_weight[idx]
                total_weights1 += self.index_to_weight[idx]

        return (
            QState(index_to_weight0, self.num_qubits),
            QState(index_to_weight1, self.num_qubits),
            total_weights0,
            total_weights1,
        )

    @staticmethod
    def ground_state(num_qubits: int) -> "QState":
        """Return the ground state ."""
        state = QState({0: 1.0}, num_qubits)
        return state

    def get_lower_bound(self) -> int:
        """Returns the lower bound of the state ."""
        if DISABLE_ASTAR:
            return 0
        lower_bound: int = 0
        signatures = self.get_qubit_signatures()
        for pattern in signatures:
            if pattern != 0:
                lower_bound += 1
        return int(lower_bound / 2)

    def __str__(self) -> str:
        return " + ".join(
            [
                f"{weight.real:0.0{N_DIGITS}f}*|{idx:0{self.num_qubits}b}>".zfill(
                    self.num_qubits
                )
                for idx, weight in self.index_to_weight.items()
            ]
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QState):
            return False
        return self.__hash__() == other.__hash__()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, QState):
            return False
        sorted_index_set = sorted(self.index_set, reverse=True)
        sorted_o_index_set = sorted(other.index_set, reverse=True)
        for i, index in enumerate(sorted_index_set):
            if i >= len(sorted_o_index_set):
                return False
            if index < sorted_o_index_set[i]:
                return True
            if index > sorted_o_index_set[i]:
                return False
        return False

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.index_set)))
        # return hash(str(self))

    def repr(self) -> int:
        """Return a hex representation of the bitmap ."""
        self.index_set = sorted(self.index_set)
        signatures = self.get_qubit_signatures()
        return hash(tuple(sorted(signatures, key=lambda x: bin(x).count("1"))))
        # return hash(self)

    def to_vector(self) -> np.ndarray:
        """Return the vector representation of the state ."""
        vector = np.zeros(2**self.num_qubits)
        for idx, weight in self.index_to_weight.items():
            vector[idx] = weight

        # normalize the vector
        vector /= np.linalg.norm(vector)

        return vector

    def to_file(self, filename: str):
        """Writes the benchmark to a file ."""

        # we format the index as a string
        index_to_weight = {
            f"{index:0{self.num_qubits}b}": weight
            for index, weight in self.index_to_weight.items()
        }
        benchmark_str = json.dumps(index_to_weight)
        # lets be safe here

        with open(filename, "w", encoding="utf-8") as file:
            file.write(benchmark_str)


def load_state(filename: str):
    """Loads the state of a given file .

    :param filename: [description]
    :type filename: str
    """

    # read the dict from the file
    with open(filename, "r", encoding="utf-8") as file:
        state_dict = json.load(file)

    num_qubits: int = None
    index_to_weight = {}
    for index_str, weight in state_dict.items():
        if num_qubits is None:
            num_qubits = len(index_str)

        index = int(index_str, 2)
        index_to_weight[index] = weight

    # convert the dict to a QState
    return QState(index_to_weight, num_qubits)


def from_val(val: int, num_qubits: int) -> QState:
    """Return the state from the vector representation .

    :param state_vector: [description]
    :type state_vector: np.ndarray
    :return: [description]
    :rtype: QState
    """

    assert 0 < val < 2 ** (2**num_qubits)
    states = []
    for i in range(2**num_qubits):
        if val & 1 == 1:
            states.append(i)
        val >>= 1

    patterns = [0 for i in range(num_qubits)]
    for _, value in enumerate(states):
        for j in range(num_qubits):
            patterns[j] = patterns[j] << 1 | ((value >> j) & 1)
    return QState(patterns, len(states))


def from_set(index_set: set, num_qubits: int) -> QState:
    """Return the state from the set representation ."""

    index_to_weight = {index: 1 for index in index_set}
    return QState(index_to_weight, num_qubits)


def index_to_str(index_to_weight: dict, num_qubits: int):
    """Prints the index_to_weight dictionary.

    :param index_to_weight: [description]
    :type index_to_weight: dict
    """

    index_str = ""

    if len(index_to_weight) == 0:
        return index_str

    if index_to_weight is None:
        return index_str

    assert isinstance(
        index_to_weight, dict
    ), f"index_to_weight must be a dictionary, got {type(index_to_weight)}"

    for index, weight in index_to_weight.items():
        index_str += f"{index:0{num_qubits}b}: {weight:0.02f}, "

    return index_str


def is_equal(qstate1: QState, qstate2: QState) -> bool:
    """
    is_equal:
    return True if the two states are equal
    """
    for index, weight in qstate1.index_to_weight.items():
        if index not in qstate2.index_to_weight:
            return False
        if not np.isclose(weight, qstate2.index_to_weight[index]):
            return False

    for index, weight in qstate1.index_to_weight.items():
        if index not in qstate1.index_to_weight:
            return False
        if not np.isclose(weight, qstate1.index_to_weight[index]):
            return False

    return True


def quantize_state(state_vector: np.ndarray):
    """Quantize a state to the number of qubits .

    :param state_vector: a vector with 2**n entries, where n is the number of qubits.
    :type state_vector: np.ndarray
    """

    if isinstance(state_vector, QState):
        return state_vector

    if isinstance(state_vector, str):
        terms = state_vector.split("+")
        index_to_weight = {}
        for term in terms:
            coefficient, state = term.strip().split("*")
            coefficient = float(coefficient.strip())
            num_qubits = len(state.strip()[1:-1])
            index = int(state.strip()[1:-1], 2)
            index_to_weight[index] = coefficient
        return QState(index_to_weight, num_qubits)

    if not isinstance(state_vector, np.ndarray):
        state_vector = np.array(state_vector)

    # discard the imaginary part
    # state_vector = state_vector.real
    state_vector = np.real(state_vector)

    # normalize the vector
    state_vector = state_vector.astype(np.float64) / np.linalg.norm(
        state_vector.astype(np.float64)
    )

    index_to_weight = {}
    num_qubits = int(np.log2(len(state_vector)))
    for idx, coefficient in enumerate(state_vector):
        if not np.isclose(coefficient, 0):
            index_to_weight[idx] = coefficient
    return QState(index_to_weight, num_qubits)


def D_state(num_qubits: int, num_bits: int) -> np.ndarray:
    """dicke state."""
    state = np.zeros(2**num_qubits)

    ones: float = 0

    for i in range(2**num_qubits):
        num_ones = bin(i).count("1")
        if num_ones == num_bits:
            state[i] = 1
            ones += 1

    return 1 / np.sqrt(ones) * state


def GHZ_state(num_qubits: int) -> np.ndarray:

    state = np.zeros(2**num_qubits)

    state[0] = 1
    state[-1] = 1

    return state / np.sqrt(2)


def ground_state(num_qubits: int) -> np.array:
    state = np.zeros(2**num_qubits)
    state[0] = 1
    return np.array(state)


def QBA_state(num_qubits: int, threshold: int) -> np.ndarray:
    state = np.zeros(2**num_qubits)
    ones: float = 0
    for i in range(2**num_qubits):
        if i < threshold:
            state[i] = 1
            ones += 1

    return state / np.sqrt(ones)


def rand_state(num_qubit: int, sparsity: int, uniform: bool = False) -> np.ndarray:
    state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
        random.random() if not uniform else 1 for i in range(sparsity)
    ]
    np.random.shuffle(state_array)

    # normalize the state
    state_array = state_array / np.linalg.norm(state_array)

    return state_array


def place_ones(size, count):
    for positions in combinations(range(size), count):
        p = [0] * size
        for i in positions:
            p[i] = 1
        yield p


def all_states(num_qubit: int, sparsity: int):
    for perm in place_ones(2**num_qubit, sparsity):
        yield perm[:]


def W_state(num_qubits: int) -> np.ndarray:
    """W state"""
    state = np.zeros(2**num_qubits)

    for i in range(num_qubits):
        state[(2**i)] = 1

    return state / np.sqrt(num_qubits)
