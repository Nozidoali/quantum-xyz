#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2024-06-17 13:21:01
Last Modified by: Hanyu Wang
Last Modified time: 2024-06-19 00:08:52
'''

# @inproceedings{bartschi2022short,
#   title={Short-depth circuits for dicke state preparation},
#   author={B{\"a}rtschi, Andreas and Eidenbenz, Stephan},
#   booktitle={2022 IEEE International Conference on Quantum Computing and Engineering (QCE)},
#   pages={87--96},
#   year={2022},
#   organization={IEEE}
# }

# @article{aktar2022divide,
#   title={A divide-and-conquer approach to Dicke state preparation},
#   author={Aktar, Shamminuj and B{\"a}rtschi, Andreas and Badawy, Abdel-Hameed A and Eidenbenz, Stephan},
#   journal={IEEE Transactions on Quantum Engineering},
#   volume={3},
#   pages={1--16},
#   year={2022},
#   publisher={IEEE}
# }

from xyz.circuit import QCircuit

def hamming_weight_distribution(circuit: QCircuit, n: int, m: int, k: int, t: int):
    """ 
    Insert the WDB circuit to the quantum circuit.
    Args:
        circuit: The quantum circuit to insert the WDB circuit.
        n: The number of qubits.
        m: The number of qubits in the target state.
        k: The number of qubits in the WDB circuit.
        t: the offset
    """
    # 
    pass 