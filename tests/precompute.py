#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-20 19:18:59
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-20 21:40:08
"""

from xyz import QState, precompute_representatives


def test_precompute():
    precompute_representatives(4)

if __name__ == "__main__":
    test_precompute()
