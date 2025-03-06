QASM_DIR: str = "example/benchmarks/qasm/"

import os
import xyz


def test_qasm_io():
    for filename in os.listdir(QASM_DIR):
        if filename.endswith(".qasm"):
            circuit = xyz.read_qasm(os.path.join(QASM_DIR, filename))
