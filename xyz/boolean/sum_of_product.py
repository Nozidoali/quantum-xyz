#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-31 14:07:02
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-31 16:45:33
"""

from curses import nonl
from typing import List
from queue import PriorityQueue

from itertools import chain, combinations


from .truth_table import (
    TruthTable,
    const1_truth_table,
    create_truth_table,
    const0_truth_table,
)


class Lit:
    """Class method to create a literal ."""

    def __init__(self, lit, phase: bool) -> None:
        self.lit = lit
        self.phase = phase

    def __str__(self) -> str:
        return f"{'~' if not self.phase else ''}{self.lit}"

    def __eq__(self, __value: object) -> bool:
        return self.lit == __value.lit and self.phase == __value.phase

    def __hash__(self) -> int:
        return hash(self.lit << 1 | self.phase)

    def to_value(self):
        return self.lit << 1 | self.phase

    def __lt__(self, other):
        return self.to_value() < other.to_value()

    def __le__(self, other):
        return self.to_value() <= other.to_value()


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def term_to_str(term: List[Lit]):
    """Convert a list of terms to a string .

    :param term: [description]
    :type term: List[Lit]
    :return: [description]
    :rtype: [type]
    """
    return "*".join([str(lit) for lit in term])


def sop_to_str(sop: List[List[Lit]]):
    """Convert a list of expressions into a string .

    :param sop: [description]
    :type sop: List[List[Lit]]
    :return: [description]
    :rtype: [type]
    """
    return " + ".join([term_to_str(term) for term in sop])


def convert_tt_to_sop(tt: TruthTable):
    """Convert a truth table to a sum of product .

    :param tt: [description]
    :type tt: TruthTable
    :return: [description]
    :rtype: [type]
    """

    sum_terms = []

    num_lits = len(tt)

    print(f"tt = {tt}")

    # apply a BFS
    q = PriorityQueue()
    enqueued = {}
    prev = {}

    def visit(new_cost: int, new_tt: TruthTable, curr_tt: TruthTable, lit: Lit):
        """Visit a new truth table .

        :param new_cost: [description]
        :type new_cost: int
        :param new_tt: [description]
        :type new_tt: TruthTable
        """
        if str(new_tt) in enqueued and enqueued[str(new_tt)] <= new_cost:
            return False
        enqueued[str(new_tt)] = new_cost
        prev[str(new_tt)] = (curr_tt, lit)
        q.put((new_cost, new_tt))
        return True

    # record the current cost and the current truth table
    curr_tt = None

    visit(0, const0_truth_table(num_lits), None, None)

    lit_to_tt = {}
    unate_terms = []
    binate_terms = []
    for lit in range(num_lits):
        tt_lit_pos = create_truth_table(num_lits, lit)
        tt_lit_neg = ~tt_lit_pos
        lit_to_tt[Lit(lit, True)] = tt_lit_pos
        lit_to_tt[Lit(lit, False)] = tt_lit_neg

        print(f"tt_lit_pos = {tt_lit_pos}, tt_lit_neg = {tt_lit_neg}")

        if tt_lit_pos < tt:
            unate_terms.append([Lit(lit, True)])

        if tt_lit_neg < tt:
            unate_terms.append([Lit(lit, False)])

        if not tt_lit_pos < ~tt:
            binate_terms.append(Lit(lit, True))

        if not tt_lit_neg < ~tt:
            binate_terms.append(Lit(lit, False))

    # we can do a DFS here to find all the unate terms
    def dfs(curr_tt: TruthTable, curr_term: List[Lit]):
        """Perform a DFS to find all the unate terms .

        :param curr_tt: [description]
        :type curr_tt: TruthTable
        :param curr_term: [description]
        :type curr_term: List[Lit]
        """
        nonlocal unate_terms
        nonlocal tt

        if curr_tt == const0_truth_table(num_lits):
            return

        if len(curr_term) > 0:
            unate_terms.append(curr_term[:])

        # keep adding the literals would not make the truth table smaller
        if curr_tt < tt:
            return

        for lit in binate_terms:
            if len(curr_term) > 0 and lit <= curr_term[-1]:
                continue
            next_tt = curr_tt & lit_to_tt[lit]
            curr_term.append(lit)
            dfs(next_tt, curr_term)
            curr_term.pop()

    dfs(const1_truth_table(num_lits), [])

    while not q.empty():
        curr_cost, curr_tt = q.get()

        if curr_tt == tt:
            break

        for term in unate_terms:
            # we skip the empty term
            if len(term) == 0:
                continue
            term_cost = 1 << (len(term) - 1)

            term_tt = None
            for lit in term:
                if term_tt is None:
                    term_tt = lit_to_tt[lit]
                else:
                    term_tt = term_tt & lit_to_tt[lit]

            if not term_tt < curr_tt:
                next_cost = curr_cost + term_cost
                next_tt = curr_tt | term_tt
                visit(next_cost, next_tt, curr_tt, term)

    if not curr_tt == tt:
        return None

    prev_tt = curr_tt
    while prev_tt is not None:
        prev_tt, term = prev[str(prev_tt)]

        if prev_tt is None:
            break

        sum_terms.append(term)

    # we return a list of list
    return sum_terms
