import numpy as np
from qiskit import qasm2
from qiskit.quantum_info import Statevector
from xyz import quantize_state
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--filename", "-f", type=str, help="The filename of the qasm file to load")
parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")

if __name__ == "__main__":
    
    args = parser.parse_args()
    filename: str = args.filename

    # qc = resynthesis(qc, verbose_level=0)
    qc = qasm2.load(filename)
    state_vector_act = Statevector(qc).data
    state_vector_act[np.abs(state_vector_act) < 1e-10] = 0
    print(f"actual state: {quantize_state(state_vector_act)}")
    
    if args.verbose:
        print(qc)
