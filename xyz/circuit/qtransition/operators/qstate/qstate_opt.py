#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-08-12 03:02:33
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-12 10:32:00
'''

import numpy as np

class QStateOpt:
    """Class method for QStateOpt
    """
    def __init__(self, state_array: np.ndarray, num_qubits: int) -> None:
        self.patterns = [0 for i in range(num_qubits)]
        self.num_qubits = num_qubits
        self.length: int = 0
        for i in range(2**num_qubits):
            if state_array[i] != 0:
                for j in range(num_qubits):
                    self.patterns[j] = self.patterns[j] << 1 | (i >> j & 1)
                self.length += 1

    def __len__(self) -> int:
        return self.length
    
    def num_supports(self) -> int:
        """Returns the number of supported supports supports .

        :return: [description]
        :rtype: int
        """
        return 0

    def count_ones(self) -> int:
        """Returns the number of ones in the state array.

        :return: [description]
        :rtype: int
        """
        one_counts = {qubit_index: 0 for qubit_index in range(self.num_qubits)}
        for qubit_index in range(self.num_qubits):
            pattern = self.patterns[qubit_index]
            for _ in range(self.length):
                if pattern & 1 == 1:
                    one_counts[qubit_index] += 1
                pattern >>= 1

        return one_counts
    
    def apply_x(self, qubit_index: int) -> None:
        """Apply X gate to the qubit.

        :param qubit_index: [description]
        :type qubit_index: int
        """
        self.patterns[qubit_index] = ~self.patterns[qubit_index]

    def apply_cx(self, control_qubit_index: int, target_qubit_index: int) -> None:
        """Apply CX gate to the qubit.

        :param control_qubit_index: [description]
        :type control_qubit_index: int
        :param target_qubit_index: [description]
        :type target_qubit_index: int
        """
        self.patterns[target_qubit_index] ^= self.patterns[control_qubit_index]
    
    def apply_y(self, qubit_index: int) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        self.patterns[qubit_index] = 0
        