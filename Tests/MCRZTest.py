#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-18 15:57:09
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 17:37:27
'''

from Algorithms import *

def test_mcrz():

    # identity matrix
    c1 = np.array([[1, 0], [0, 0]])
    c2 = np.array([[0, 0], [0, 1]])

    d1 = np.array([[1, 0], [0, 0]])
    d2 = np.array([[0, 0], [0, 1]])

    u1 = BasicGate.ry(np.pi / 2)

    matrix = np.kron(np.identity(2), np.kron(c1, d1) + np.kron(c2, d1) + np.kron(c1, d2) ) + np.kron(u1, np.kron(c2, d2))

    print(matrix)

    half = matrix.shape[0] // 2
    S = matrix[:half, :half]

    alphas = -2 * -1j * np.log( S.diagonal() )
    thetas = find_thetas(alphas)

    num_qubits = 3
    new_matrix = np.identity(2**num_qubits)

    for i, theta in enumerate(thetas):

        # get the number of gray code 
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 2, 1, 2, 3, 2, 1, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        control_id = bin(i ^ (i>>1)).count('1') - 1

        # CNOT
        if control_id >= 0:

            op_matrix = np.zeros((2**num_qubits, 2**num_qubits))
            for op, cond in zip([np.identity(2), BasicGate.x()], [c1, c2]):
                curr_matrix = op
                for qubit_id in range(num_qubits-1):
                    if qubit_id == control_id:
                        curr_matrix = np.kron(curr_matrix, cond)
                    else:
                        curr_matrix = np.kron(curr_matrix, np.identity(2))
                op_matrix += curr_matrix
            
            new_matrix = new_matrix @ op_matrix

        # rotate the target qubit
        new_matrix = new_matrix @ np.kron(BasicGate.rz(theta), np.identity(2**(num_qubits-1))) 

    control_id = num_qubits - 1 # reset the control id
    op_matrix = np.zeros((2**num_qubits, 2**num_qubits))
    for op, cond in zip([np.identity(2), BasicGate.x()], [c1, c2]):
        curr_matrix = op
        for qubit_id in range(num_qubits-1):
            if qubit_id == control_id:
                curr_matrix = np.kron(curr_matrix, cond)
            else:
                curr_matrix = np.kron(curr_matrix, np.identity(2))
        op_matrix += curr_matrix
    
    new_matrix = new_matrix @ op_matrix

    print(new_matrix)

    assert np.allclose(matrix, new_matrix)


def test_mcrz_2():

    # identity matrix
    c1 = np.array([[1, 0], [0, 0]])
    c2 = np.array([[0, 0], [0, 1]])

    u1 = BasicGate.rz(np.pi / 2)

    matrix = np.kron(np.identity(2), c1 ) + np.kron(u1, c2)

    print(matrix)

    half = matrix.shape[0] // 2
    S = matrix[:half, :half]

    alphas = -2 * -1j * np.log( S.diagonal() )
    print(alphas)
    thetas = find_thetas(alphas)
    print(thetas)

    num_qubits = 2
    new_matrix = np.identity(2**num_qubits)

    for i, theta in enumerate(thetas):

        # get the number of gray code 
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 2, 1, 2, 3, 2, 1, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        control_id = bin(i ^ (i>>1)).count('1') - 1

        # CNOT
        if control_id >= 0:

            op_matrix = np.zeros((2**num_qubits, 2**num_qubits))
            for op, cond in zip([np.identity(2), BasicGate.x()], [c1, c2]):
                curr_matrix = op
                for qubit_id in range(num_qubits-1):
                    if qubit_id == control_id:
                        curr_matrix = np.kron(curr_matrix, cond)
                    else:
                        curr_matrix = np.kron(curr_matrix, np.identity(2))
                op_matrix += curr_matrix
            
            new_matrix = new_matrix @ op_matrix
            # print("op matrix = \n", op_matrix)

        # rotate the target qubit
        new_matrix = new_matrix @ np.kron(BasicGate.rz(theta), np.identity(2**(num_qubits-1))) 
        # print("new matrix = \n", new_matrix)

    control_id = num_qubits - 2 # reset the control id
    op_matrix = np.zeros((2**num_qubits, 2**num_qubits))
    for op, cond in zip([np.identity(2), BasicGate.x()], [c1, c2]):
        curr_matrix = op
        for qubit_id in range(num_qubits-1):
            if qubit_id == control_id:
                curr_matrix = np.kron(curr_matrix, cond)
            else:
                curr_matrix = np.kron(curr_matrix, np.identity(2))
        op_matrix += curr_matrix
    
    new_matrix = new_matrix @ op_matrix
    # print("op matrix = \n", op_matrix)
    # print(new_matrix)

    if not np.allclose(matrix, new_matrix):
        diff = matrix @ new_matrix.conj().T
        print("diff = \n" , diff)
    assert np.allclose(matrix, new_matrix)