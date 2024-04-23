#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-12 03:02:33
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-19 13:40:18
"""

import json

from typing import List, Tuple
import numpy as np

# the merge uncertainty, if the difference between the two angles is less than
# this value, we consider them to be the same
MERGE_UNCERTAINTY = 1e-12

N_DIGITS = 2

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

    def __deepcopy__(self, memo):
        return QState(self.index_to_weight, self.num_qubits)

    def get_supports(self) -> List[int]:
        """Return the support of the state .
        """
        signatures = self.get_qubit_signatures()
        qubit_indices = []
        for qubit, pattern in enumerate(signatures):
            if pattern != 0:
                qubit_indices.append(qubit)
        return qubit_indices

    def get_sparsity(self) -> int:
        """Return the sparsity of the state .
        """
        return len(self.index_set)

    def to_value(self) -> int:
        """Return the value of the state .
        """
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
        """Returns the number of signed unsigned signatures .
        """
        return (1 << len(self.index_set)) - 1

    def cofactors(self, pivot_qubit: int) -> Tuple["QState", "QState"]:
        """Returns the cofactors of the given qubit .
        """

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
        """Return the ground state .
        """
        state = QState({0: 1.0}, num_qubits)
        return state

    def get_lower_bound(self) -> int:
        """Returns the lower bound of the state .
        """
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
        """Return a hex representation of the bitmap .
        """
        # self.index_set = sorted(self.index_set)
        # signatures = self.get_qubit_signatures()
        # return hash(tuple(sorted(signatures, key=lambda x: bin(x).count("1"))))
        return hash(self)

    def to_vector(self) -> np.ndarray:
        """Return the vector representation of the state .
        """
        vector = np.zeros(2**self.num_qubits)
        for idx, weight in self.index_to_weight.items():
            vector[idx] = np.sqrt(weight)

        # normalize the vector
        vector /= np.linalg.norm(vector)

        return vector

    def to_file(self, filename: str):
        """Writes the benchmark to a file .
        """

        # we format the index as a string
        index_to_weight = {
            f"{index:0{self.num_qubits}b}": weight
            for index, weight in self.index_to_weight.items()
        }
        benchmark_str = json.dumps(index_to_weight)
        # lets be safe here

        with open(filename, "w", encoding="utf-8") as file:
            file.write(benchmark_str)

