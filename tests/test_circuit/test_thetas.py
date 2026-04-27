#!/usr/bin/env python
import numpy as np
import xyz
from xyz.state import get_most_frequent_theta, get_ry_angles


def test_thetas():
    """Test theta of the state ."""
    state_vector = np.array([1, -1])

    state = xyz.quantize_state(state_vector)

    thetas = get_ry_angles(state, 0)
    best_theta = get_most_frequent_theta(state, 0)

    assert np.isclose(thetas[0], -np.pi / 2)
    assert best_theta == -np.pi / 2
