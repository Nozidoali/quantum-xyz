import os

import pytest

from xyz.io import read_qasm

QASM_DIR: str = "example/benchmarks/qasm/"


@pytest.mark.skipif(
    not os.path.isdir(QASM_DIR),
    reason=f"benchmark directory {QASM_DIR} not present in this checkout",
)
def test_qasm_io():
    for filename in os.listdir(QASM_DIR):
        if filename.endswith(".qasm"):
            circuit = read_qasm(os.path.join(QASM_DIR, filename))
