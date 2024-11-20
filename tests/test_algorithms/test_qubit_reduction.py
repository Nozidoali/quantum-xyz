import random

import numpy as np
import pytest

from xyz import *
N_TESTS = 10


@pytest.fixture
def state_vectors():
    """Generate a random state vector for testing ."""
    all_state_vectors = []
    while len(all_state_vectors) < N_TESTS:
        num_qubit = random.randint(3, 6)
        sparsity = random.randint(num_qubit, 2 ** (num_qubit - 1) - 1)
        # sparsity = random.randint(2 ** (num_qubit - 1) - 1, 2 ** (num_qubit - 1) - 1)
        state = rand_state(num_qubit, sparsity, uniform=False)

        # check if the state is valid
        all_state_vectors.append(state)

    return all_state_vectors


def test_one_state(state_vectors):
    for state_vector in state_vectors:
        state_vector_exp = state_vector
        target_state = quantize_state(state_vector_exp)
        # print("target state: ", target_state)
        circuit = prepare_state(
            target_state,
            verbose_level=0
        )
        # now we measure the distance between the target state and the actual state
        state_vector_act = simulate_circuit(circuit)
        dist = np.linalg.norm(np.abs(state_vector_act) - np.abs(state_vector_exp))
        dist_strict = np.linalg.norm(state_vector_act - state_vector_exp)
        if dist_strict**2 >= 1e-4:
            # we raise a warning if the distance is large
            print(
                f"distance is {dist_strict**2}, state_exp = {state_vector_exp}, state_act = {state_vector_act}"
            )
            assert False
        assert dist**2 < 1e-4  # make sure the distance is small
