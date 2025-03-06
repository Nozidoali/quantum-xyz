import numpy as np
import xyz
import pytest

# skip
@pytest.mark.skip(reason="Takes too long")
def test_qsp_1():
    state = "0.41*|001000> + 0.41*|010001> + 0.41*|010100> + 0.41*|011100> + 0.41*|101111> + 0.41*|111100>"
    target_state = xyz.quantize_state(state)
    state_vector = target_state.to_vector()

    circuit = xyz.prepare_state(target_state, map_gates=True)
    state_vector_act = xyz.simulate_circuit(circuit)

    assert np.linalg.norm(abs(state_vector_act) - abs(state_vector)) < 1e-6


def test_qsp_2():
    state = "0.71*|0010> + 0.41*|0101> + 0.41*|0111> + 0.41*|1111>"
    target_state = xyz.quantize_state(state)
    state_vector = target_state.to_vector()

    circuit = xyz.prepare_state(target_state, map_gates=True)
    state_vector_act = xyz.simulate_circuit(circuit)

    assert np.linalg.norm(abs(state_vector_act) - abs(state_vector)) < 1e-6
