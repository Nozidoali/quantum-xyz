import pickle
from queue import PriorityQueue
from xyz.circuit import QState, from_set


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
