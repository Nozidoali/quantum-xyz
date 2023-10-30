#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-07 23:13:16
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-07 23:28:09
"""

import json
import os

from xyz import D_state, quantize_state


def generate_benchmarks():
    """Generates benchmarks for the D_state ."""
    for num_qubits in range(2, 21):
        for sparsity in range(1, int((num_qubits + 1) / 2)):
            state = D_state(num_qubits, sparsity)
            state = quantize_state(state)

            # we format the index as a string
            index_to_weight = {
                f"{index:0{state.num_qubits}b}": weight
                for index, weight in state.index_to_weight.items()
            }
            benchmark_str = json.dumps(index_to_weight)

            # lets be safe here
            if os.path.exists(f"./d_{num_qubits}_{sparsity}.json"):
                print(f"[WARNING] ./d_{num_qubits}_{sparsity}.json already exists.")
                continue

            with open(f"./d_{num_qubits}_{sparsity}.json", "w") as f:
                f.write(benchmark_str)


if __name__ == "__main__":
    generate_benchmarks()
