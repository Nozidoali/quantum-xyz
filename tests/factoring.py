#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 13:14:41
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 13:21:49
"""

from xyz import quantize_state, QState, QCircuit, D_state


def test_factorization():
    state = quantize_state(D_state(4, 2))
    pos_state, neg_state, weights0, weights1 = state.cofactors(1)

    print(f"pos_state = {pos_state}")
    print(f"neg_state = {neg_state}")


if __name__ == "__main__":
    test_factorization()
