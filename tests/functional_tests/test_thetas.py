#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-17 14:19:26
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-17 14:45:03
"""

import numpy as np
import xyz


def test_thetas():
    """Test theta of the state ."""
    state_vector = np.array([1, -1])

    state = xyz.quantize_state(state_vector)

    thetas = xyz.get_ry_angles(state, 0)
    best_theta = xyz.get_most_frequent_theta(state, 0)

    assert np.isclose(thetas[0], -np.pi / 2)
    assert best_theta == -np.pi / 2
