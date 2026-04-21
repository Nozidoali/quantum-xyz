import numpy as np
import xyz


def test_get_cry_angles_1():
    state_vector = "0.5*|00>+0.5*|01>+0.5*|10>+0.5*|11>"
    state = xyz.quantize_state(state_vector)
    cry_angle = xyz.get_ap_cry_angles(state, 0, 1)
    assert np.isclose(cry_angle, np.pi / 2), "cry_angle = %s" % cry_angle


def test_get_cry_angles_2():
    state_vector = "0.5*|00>+0.5*|01>+0.5*|11>"
    state = xyz.quantize_state(state_vector)
    cry_angle = xyz.get_ap_cry_angles(state, 1, 0, True)
    assert cry_angle is None, "cry_angle = %s" % cry_angle
    cry_angle = xyz.get_ap_cry_angles(state, 1, 0, False)
    assert np.isclose(cry_angle, np.pi / 2), "cry_angle = %s" % cry_angle
