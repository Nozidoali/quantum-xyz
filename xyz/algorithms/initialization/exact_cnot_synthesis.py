from queue import PriorityQueue
import pickle
import numpy as np
from xyz.circuit import QState, from_set, QCircuit, CX, CRY, get_ap_cry_angles
from .support_reduction import support_reduction


class QSPDatabase:
    N_QUBIT_MAX: int = 4

    def __init__(self, verbose_level: int = 0) -> None:
        self.verbose_level = verbose_level
        self.databases = {}

    @staticmethod
    def get_db_filename(n_qubits: int):
        return f"qsp_db_{n_qubits}.pkl"

    def load_database(self, n_qubits: int):
        try:
            with open(self.get_db_filename(n_qubits), "rb") as f:
                self.databases[n_qubits] = pickle.load(f)
        except FileNotFoundError:
            self.init_database(n_qubits)
            self.save_database(n_qubits)

    def lookup(self, state: QState):
        num_qubits = state.num_qubits
        if num_qubits > self.N_QUBIT_MAX:
            return 0
        if num_qubits not in self.databases:
            # load the database
            self.load_database(state.num_qubits)
        assert num_qubits in self.databases
        assert state.repr() in self.databases[num_qubits], f"{state.repr()}"
        return self.databases[num_qubits][state.repr()]

    def save_database(self, n_qubits: int):
        with open(self.get_db_filename(n_qubits), "wb") as f:
            pickle.dump(self.databases[n_qubits], f)

    @staticmethod
    def get_repr(index_set: set, n_qubits: int):
        qstate = from_set(index_set, n_qubits)
        return qstate.repr()

    @staticmethod
    def get_next_set(index_set: set, n_qubits: int):
        ret = []

        # try X gate
        for qubit in range(n_qubits):
            new_set = set()
            for index in index_set:
                new_set.add(index ^ (1 << qubit))
            ret.append([new_set, 0])

        # try Ry gate
        for qubit in range(n_qubits):
            new_set = set()
            is_valid: bool = True
            for index in index_set:
                ridx = index ^ (1 << qubit)
                if ridx in index_set:
                    # this is not an AP transition
                    is_valid = False
                    break
                new_set.add(index)
                new_set.add(index ^ (1 << qubit))
            if is_valid:
                ret.append([new_set, 0])

        # try CX gate
        for control_qubit in range(n_qubits):
            for target_qubit in range(n_qubits):
                if control_qubit == target_qubit:
                    continue
                for phase in [True, False]:
                    new_set = set()
                    for index in index_set:
                        if (index >> control_qubit) & 1 == phase:
                            new_set.add(index ^ (1 << target_qubit))
                        else:
                            new_set.add(index)
                    ret.append([new_set, 1])

        # try CRY gate
        for control_qubit in range(n_qubits):
            for target_qubit in range(n_qubits):
                if control_qubit == target_qubit:
                    continue
                for phase in [True, False]:
                    new_set = set()
                    is_valid = True
                    for index in index_set:
                        if (index >> control_qubit) & 1 == phase:
                            ridx = index ^ (1 << target_qubit)
                            if ridx in index_set:
                                # this is not an AP transition
                                is_valid = False
                                break
                            new_set.add(index)
                            new_set.add(index ^ (1 << target_qubit))
                        else:
                            new_set.add(index)
                    if is_valid:
                        ret.append([new_set, 2])
        return ret

    def init_database(self, n_qubits: int):
        database = {}

        if self.verbose_level >= 1:
            print("Initializing database...")

        enqueued_set = {}
        visited_repr = set()
        queue = PriorityQueue()
        queue.put([0, set([0])])

        while not queue.empty():
            if self.verbose_level >= 1:
                if len(database) % 100 == 0:
                    print(
                        f"Database size: {len(database)}, Queue size: {queue.qsize()}, Enqueued size: {len(enqueued_set)}"
                    )

            curr_cost, curr_set = queue.get()
            curr_repr = self.get_repr(curr_set, n_qubits)

            visited_repr.add(curr_repr)

            if curr_repr in database:
                continue

            if curr_repr not in database:
                database[curr_repr] = curr_cost

            for next_set, cnot_cost in self.get_next_set(curr_set, n_qubits):
                next_repr = self.get_repr(next_set, n_qubits)
                if next_repr in visited_repr:
                    continue
                if next_repr in enqueued_set:
                    if enqueued_set[next_repr] <= curr_cost:
                        continue
                enqueued_set[next_repr] = curr_cost + cnot_cost
                queue.put([curr_cost + cnot_cost, next_set])

        if self.verbose_level >= 1:
            print("Database initialized.")
            print(f"Database size: {len(database)}")

        self.databases[n_qubits] = database


class AStarCost:
    def __init__(self, cnot_cost: float, lower_bound: float) -> None:
        self.cnot_cost = cnot_cost
        self.lower_bound = lower_bound

    def __lt__(self, other: "AStarCost"):
        return self.cnot_cost + self.lower_bound < other.cnot_cost + other.lower_bound

    def __ge__(self, other: "AStarCost"):
        return not self < other

    def __str__(self) -> str:
        return f"{self.cnot_cost}(+{self.lower_bound})"


class Explorer:
    def __init__(self, verbose_level: int = 0):
        # now we start the search
        self.visited_states = set()
        self.state_queue = PriorityQueue()
        self.enqueued = {}
        self.record = {}
        self.verbose_level = verbose_level
        self.enqueued_states_of_cost = {}
        self.qsp_database = QSPDatabase(verbose_level)

    def get_lower_bound(self, state: QState):
        sub_index_to_weight = {}
        old_to_new_qubit_mapping = {}
        supports = state.get_supports()
        num_supports = len(supports)
        if num_supports != state.num_qubits:
            for new_index, old_index in enumerate(supports):
                old_to_new_qubit_mapping[old_index] = new_index
            for index, weight in state.index_to_weight.items():
                new_index: int = 0
                for i, support in enumerate(supports):
                    if index & (1 << support) != 0:
                        new_index |= 1 << i
                sub_index_to_weight[new_index] = weight
            new_state = QState(sub_index_to_weight, num_supports)
            return self.qsp_database.lookup(new_state)
        return self.qsp_database.lookup(state)

    def add_state(self, state: QState, cost: AStarCost = None):
        if cost is None:
            cost = AStarCost(0, self.get_lower_bound(state))
        self.state_queue.put((cost, state))
        self.enqueued[state.repr()] = cost

    def reset(self):
        self.state_queue = PriorityQueue()
        self.enqueued = {}
        self.visited_states = set()

    def visit_state(self, state: QState):
        self.visited_states.add(state.repr())

    def is_done(self):
        return self.state_queue.empty()

    def get_state(self):
        return self.state_queue.get()

    def get_n_front(self, n_cnot: int):
        if n_cnot not in self.enqueued_states_of_cost:
            return 0
        return self.enqueued_states_of_cost[n_cnot]

    def report(self):
        print(f"queue size: {self.state_queue.qsize()}")
        print(f"visited states: {len(self.visited_states)}")
        print(f"enqueued states: {len(self.enqueued)}")

    def explore_state(
        self,
        curr_state: QState,
        gates: list,
        curr_cost: AStarCost,
        next_state: QState = None,
    ) -> QState:
        """Explore a state in a transition graph."""

        if next_state is None:
            for gate in gates[::-1]:
                next_state = gate.conjugate().apply(curr_state)

        cnot_cost = sum([gate.get_cnot_cost() for gate in gates])
        next_cost = AStarCost(
            curr_cost.cnot_cost + cnot_cost,
            self.get_lower_bound(next_state),
        )
        repr_next = next_state.repr()

        # we skip the state if it is already visited
        if repr_next in self.visited_states:
            return None

        # we skip the state if it is already enquened and the cost is higher
        if repr_next in self.enqueued and next_cost >= self.enqueued[repr_next]:
            return None

        # now we add the state to the queue
        self.state_queue.put((next_cost, next_state))
        self.enqueued[repr_next] = next_cost

        if next_cost.cnot_cost not in self.enqueued_states_of_cost:
            self.enqueued_states_of_cost[next_cost.cnot_cost] = 0
        self.enqueued_states_of_cost[next_cost.cnot_cost] += 1

        # we record the gate
        gates_to_record: list = gates[:]

        # and record the quantum_operator
        if self.verbose_level >= 3:
            gates_str = ", ".join([str(gate) for gate in gates_to_record])
            print(f"recording [{next_state}] <- {curr_state}, gate: {gates_str}")
        self.record[hash(next_state)] = hash(curr_state), gates_to_record
        return next_state


def get_state_transitions(circuit: QCircuit, curr_state: QState, supports: list = None):
    if supports is None:
        supports = curr_state.get_supports()

    # try dependency analysis
    new_state, gates = support_reduction(circuit, curr_state)
    if len(gates) > 0:
        return [[new_state, gates]]

    # apply CRY
    transitions = []
    for target_qubit in supports:
        for control_qubit in supports:
            if control_qubit == target_qubit:
                continue
            for phase in [True, False]:
                cry_angle = get_ap_cry_angles(
                    curr_state, control_qubit, target_qubit, phase
                )
                if cry_angle is None:
                    continue
                transitions.append(
                    [
                        None,
                        [
                            CRY(
                                cry_angle,
                                circuit.qubit_at(control_qubit),
                                phase,
                                circuit.qubit_at(target_qubit),
                            )
                        ],
                    ]
                )

                transitions.append(
                    [
                        None,
                        [
                            CRY(
                                cry_angle - np.pi,
                                circuit.qubit_at(control_qubit),
                                phase,
                                circuit.qubit_at(target_qubit),
                            )
                        ],
                    ]
                )

    if len(transitions) > 0 and curr_state.num_qubits > 4:
        # To speed up the search, we only consider the first CRY gate
        return transitions

    for target_qubit in supports:
        # apply CNOT
        for target_qubit in supports:
            for control_qubit in supports:
                if control_qubit == target_qubit:
                    continue
                for phase in [True, False]:
                    gate = CX(
                        circuit.qubit_at(control_qubit),
                        phase,
                        circuit.qubit_at(target_qubit),
                    )
                    transitions.append([None, [gate]])
    return transitions


N_FRONT_MAX = 1e7
N_ENQUEUED_MAX = 1e6


def backtrace(state: QState, record: dict):
    gates = []
    backtraced_states: set = set()
    curr_hash = hash(state)
    while curr_hash in record:
        if curr_hash in backtraced_states:
            raise ValueError("Loop found")
        backtraced_states.add(curr_hash)
        prev_hash, _gates = record[curr_hash]
        gates += _gates
        curr_hash = prev_hash

    return gates


def exact_cnot_synthesis(
    circuit: QCircuit,
    target_state: QState,
    verbose_level: int = 0,
    cnot_limit: int = None,
):
    """This function prepares the state by finding the shortest path ."""

    explorer = Explorer(verbose_level)
    explorer.add_state(target_state)

    # begin of the exact synthesis algorithm
    initial_state = QState.ground_state(target_state.num_qubits)

    n_init, m_init = len(target_state.get_supports()), target_state.get_sparsity()
    best_state = target_state
    best_score = 0
    best_cost = AStarCost(0, explorer.get_lower_bound(target_state))

    # This function is called by the search loop.
    solution_reached: bool = False
    while not explorer.is_done():
        curr_state: QState
        curr_cost: AStarCost
        curr_cost, curr_state = explorer.get_state()
        n_cnot_at_front = explorer.get_n_front(curr_cost.cnot_cost)

        if verbose_level >= 2:
            print(f"curr_state: {curr_state}, cost: {curr_cost}")
            explorer.report()
            print(f"n_cnot_at_front: {n_cnot_at_front}")

        if n_cnot_at_front > N_FRONT_MAX or len(explorer.enqueued) > N_ENQUEUED_MAX:
            if best_score > 0:
                print(f"best_state: {best_state}, best_score: {best_score}")
                n_init, m_init = (
                    len(best_state.get_supports()),
                    best_state.get_sparsity(),
                )
                best_score = 0
                explorer.reset()
                explorer.add_state(best_state, best_cost)
                continue

        if cnot_limit is not None and curr_cost.cnot_cost > cnot_limit:
            # this will then raise an ValueError
            break

        if curr_state == initial_state:
            # then we have found the solution
            solution_reached = True
            break

        if curr_state.repr() in explorer.visited_states:
            continue

        explorer.visit_state(curr_state)

        supports = curr_state.get_supports()
        _curr_n, _curr_m = len(supports), curr_state.get_sparsity()
        curr_score = float(n_init * m_init - _curr_n * _curr_m) / (
            curr_cost.cnot_cost + 1
        )
        if curr_score > best_score:
            best_score = curr_score
            best_state = curr_state
            best_cost = curr_cost

        transitions = get_state_transitions(circuit, curr_state, supports)
        for next_state, gates in transitions:
            explorer.explore_state(curr_state, gates, curr_cost, next_state)

    if not solution_reached:
        raise ValueError("No solution found")
    return backtrace(curr_state, explorer.record)
