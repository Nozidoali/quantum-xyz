from typing import Dict, List

PERM_INVARIANT: bool = False


class StabilizerState:
    def __init__(self, num_qubits: int, num_stabilizers: int, patterns: List[int]):
        self.num_qubits: int = num_qubits
        self.num_stabilizers: int = num_stabilizers
        self.patterns: List[int] = patterns[:]
        if PERM_INVARIANT:
            self.regularize()

    def __hash__(self) -> int:
        return hash("".join(map(str, self.patterns)))

    def is_final(self) -> bool:
        for i, p in enumerate(self.patterns):
            if p != (1 << (self.num_stabilizers - i - 1)):
                return False
            if i == self.num_stabilizers:
                break
        return True

    def lower_bound(self) -> int:
        return 0

    def regularize(self) -> None:
        self.patterns = sorted(self.patterns)

    def __str__(self):
        return str(self.patterns)

    def __lt__(self, other: "StabilizerState") -> bool:
        return hash(self) < hash(other)

    def apply_cx(self, cx: dict) -> "StabilizerState":
        next_state = StabilizerState(
            self.num_qubits, self.num_stabilizers, self.patterns
        )
        next_state.patterns[cx["target"]] ^= next_state.patterns[cx["control"]]
        if PERM_INVARIANT:
            next_state.regularize()
        return next_state


def _to_int(pattern: str) -> int:
    return int(pattern.replace("-", "0"), 2)


from queue import PriorityQueue

if __name__ == "__main__":
    # patterns = list(map(
    #     lambda x: _to_int(x), [
    #         '11-------',
    #         '1--------',
    #         '11-1-----',
    #         '1--1-----',
    #         '-11------',
    #         '-111-----',
    #         '--1--1---',
    #         '--11-1---',
    #         '---11----',
    #         '----1--1-',
    #         '---1--1--',
    #         '----1-11-',
    #         '-----1--1',
    #         '---1-1--1',
    #         '---1--1-1',
    #         '------111',
    #         '-------11',
    # ]))

    # perm =  [
    #     '-1-',
    #     '--1',
    #     '1--',
    # ]

    perm = [
        "-1--",
        "--1-",
        "---1",
        "1---",
    ]

    patterns = list(map(lambda x: _to_int(x), perm))

    state: StabilizerState
    state_init = StabilizerState(len(perm), len(perm), patterns)
    q = PriorityQueue()
    visited = set()
    enqueued = {}
    prev_state = {}
    q.put((0, state_init))
    enqueued[state_init] = 0
    prev_state[state_init] = None
    while q.qsize() > 0:
        cost, state = q.get()
        if state.is_final():
            print(cost)
            path = []
            while state is not None:
                path.append(state)
                state = prev_state[state]
            path.reverse()
            for s in path:
                print(s)
            break
        if hash(state) in visited:
            continue
        visited.add(hash(state))
        for i in range(state.num_qubits):
            for j in range(state.num_qubits):
                if i == j:
                    continue
                next_state = state.apply_cx({"control": i, "target": j})
                if (
                    hash(next_state) in visited
                    or next_state in enqueued
                    and enqueued[next_state] <= cost + 1
                ):
                    continue
                q.put((cost + 1, next_state))
                enqueued[next_state] = cost + 1
                prev_state[next_state] = state
