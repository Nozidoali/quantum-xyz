quantum circuit implementation
------------------------------

Highlights: our implementation of quantum circuits leverages the following features:
- Sparse matrix representation (see `qstate.py`)
- Fast simulation of quantum circuits (see `gate/<gate>.py`)
- On-the-fly gate decomposition (see `qgate.py`)
- On-the-fly redundant gate removal (see `qcircuit.py`)
