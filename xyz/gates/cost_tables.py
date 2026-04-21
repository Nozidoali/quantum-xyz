"""Hardcoded CNOT-count lookup for MCRY gates.

The values come from the prior literature's best-known decomposition
counts; the gate's `cnot_cost()` reads them directly. Keys are the
number of control qubits (int), not stringified ints like the original
table in qgate.py."""

from __future__ import annotations

MCRY_CNOT_COST: dict[int, int] = {
    0: 0,
    1: 2,
    2: 4,
    3: 8,
    4: 16,
    5: 32,
    6: 64,
    7: 128,
    8: 226,
    9: 290,
    10: 362,
    11: 442,
    12: 530,
    13: 626,
    14: 730,
    15: 842,
    16: 962,
    17: 1090,
    18: 1226,
    19: 1370,
    20: 1522,
    21: 1682,
    22: 1850,
    23: 2026,
    24: 2210,
    25: 2402,
    26: 2602,
    27: 2810,
    28: 3026,
}
