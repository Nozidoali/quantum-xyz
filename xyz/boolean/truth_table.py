#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-31 14:05:07
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-31 16:34:17
"""

from enum import Enum, auto
from math import log
from re import sub
import types
from typing import Any

from sympy import false


class TruthTableEntry(Enum):
    """Class method .

    :param enum: [description]
    :type enum: [type]
    """

    ZERO = auto()
    ONE = auto()
    DONT_CARE = auto()


TT_STR = {
    TruthTableEntry.ZERO: "0",
    TruthTableEntry.ONE: "1",
    TruthTableEntry.DONT_CARE: "-",
}


class TruthTable:
    """Class method ."""

    def __init__(self, num_lits: int) -> None:
        """Initialize a truth table with the given number of qubits .

        :param num_lits: [description]
        :type num_lits: int
        """
        self._num_lits = num_lits
        self._table = [TruthTableEntry.DONT_CARE for i in range(2**num_lits)]

    def __str__(self) -> str:
        return "".join([TT_STR[entry] for entry in self._table])

    def __len__(self):
        return self._num_lits

    def set_true(self, bit):
        """Set the given bit to true .

        :param bit: [description]
        :type bit: [type]
        """
        self._table[bit] = TruthTableEntry.ONE

    def set_false(self, bit):
        """Set the given bit to false .

        :param bit: [description]
        :type bit: [type]
        """
        self._table[bit] = TruthTableEntry.ZERO

    def set_bit(self, bit, value):
        """Set the given bit to the given value .

        :param bit: [description]
        :type bit: [type]
        :param value: [description]
        :type value: [type]
        """
        if value:
            self.set_true(bit)
        else:
            self.set_false(bit)

    def __lt__(self, other):
        """Compare two truth tables .

        :param other: [description]
        :type other: [type]
        :return: [description]
        :rtype: [type]
        """
        for i in range(2**self._num_lits):
            if self._table[i] == TruthTableEntry.DONT_CARE:
                continue
            if other._table[i] == TruthTableEntry.DONT_CARE:
                continue
            if (
                self._table[i] == TruthTableEntry.ONE
                and other._table[i] == TruthTableEntry.ZERO
            ):
                return false

        return True

    def __or__(self, __value: Any) -> "TruthTable":
        """Compute the disjunction of two truth tables .

        :param __value: [description]
        :type __value: Any
        :return: [description]
        :rtype: TruthTable
        """
        tt_or = TruthTable(self._num_lits)
        for i in range(2**self._num_lits):
            if (
                self._table[i] == TruthTableEntry.ONE
                or __value._table[i] == TruthTableEntry.ONE
            ):
                tt_or._table[i] = TruthTableEntry.ONE
            elif (
                self._table[i] == TruthTableEntry.ZERO
                and __value._table[i] == TruthTableEntry.ZERO
            ):
                tt_or._table[i] = TruthTableEntry.ZERO
            else:
                tt_or._table[i] = TruthTableEntry.DONT_CARE

        return tt_or

    def __and__(self, __value: Any) -> "TruthTable":
        """Compute the conjunction of two truth tables .

        :param __value: [description]
        :type __value: Any
        :return: [description]
        :rtype: TruthTable
        """
        tt_and = TruthTable(self._num_lits)
        for i in range(2**self._num_lits):
            if (
                self._table[i] == TruthTableEntry.ZERO
                or __value._table[i] == TruthTableEntry.ZERO
            ):
                tt_and._table[i] = TruthTableEntry.ZERO
            elif (
                self._table[i] == TruthTableEntry.ONE
                and __value._table[i] == TruthTableEntry.ONE
            ):
                tt_and._table[i] = TruthTableEntry.ONE
            else:
                tt_and._table[i] = TruthTableEntry.DONT_CARE

        return tt_and

    def __invert__(self):
        """Negate a truth table .

        :return: [description]
        :rtype: [type]
        """
        negated = TruthTable(self._num_lits)
        for i in range(2**self._num_lits):
            if self._table[i] == TruthTableEntry.DONT_CARE:
                continue
            if self._table[i] == TruthTableEntry.ONE:
                negated.set_false(i)
            else:
                negated.set_true(i)
        return negated

    def __add__(self, other):
        """Compute the sum of two truth tables .

        :param other: [description]
        :type other: [type]
        :return: [description]
        :rtype: [type]
        """
        sum_tt = TruthTable(self._num_lits)
        for i in range(2**self._num_lits):
            if self._table[i] == TruthTableEntry.ONE:
                sum_tt._table[i] = other._table[i]
            elif other._table[i] == TruthTableEntry.ZERO:
                sum_tt._table[i] = TruthTableEntry.ZERO
        return sum_tt

    def __sub__(self, other):
        """Compute the difference of two truth tables .

        :param other: [description]
        :type other: [type]
        :return: [description]
        :rtype: [type]
        """
        sub_tt = TruthTable(self._num_lits)
        for i in range(2**self._num_lits):
            if self._table[i] == TruthTableEntry.ONE:
                assert other._table[i] == TruthTableEntry.ONE
                sub_tt._table[i] = TruthTableEntry.ONE
            elif self._table[i] == TruthTableEntry.ZERO:
                if other._table[i] == TruthTableEntry.ONE:
                    sub_tt._table[i] = TruthTableEntry.ZERO
                else:
                    sub_tt._table[i] = TruthTableEntry.DONT_CARE
        return sub_tt

    def is_dont_care(self):
        """Check if the truth table is a don't care .

        :return: [description]
        :rtype: [type]
        """
        for entry in self._table:
            if entry != TruthTableEntry.DONT_CARE:
                return False
        return True

    def __eq__(self, __value: object) -> bool:
        for i in range(2**self._num_lits):
            if self._table[i] == TruthTableEntry.DONT_CARE:
                continue
            if __value._table[i] == TruthTableEntry.DONT_CARE:
                continue
            if self._table[i] != __value._table[i]:
                return False
        return True


def create_truth_table(num_lits: int, idx: int):
    """Create a truth table with the given number of literals and the given index .

    :param num_lits: [description]
    :type num_lits: int
    :param idx: [description]
    :type idx: int
    :return: [description]
    :rtype: [type]
    """
    truth_table = TruthTable(num_lits)

    for i in range(1 << num_lits):
        if (i >> idx) & 1:
            truth_table.set_true(i)
        else:
            truth_table.set_false(i)
    return truth_table


def const0_truth_table(num_lits: int):
    """Create a truth table with the given number of literals and the given index .

    :param num_lits: [description]
    :type num_lits: int
    :param idx: [description]
    :type idx: int
    :return: [description]
    :rtype: [type]
    """
    truth_table = TruthTable(num_lits)

    for i in range(1 << num_lits):
        truth_table.set_false(i)
    return truth_table


def const1_truth_table(num_lits: int):
    """Create a truth table with the given number of literals and the given index .

    :param num_lits: [description]
    :type num_lits: int
    :param idx: [description]
    :type idx: int
    :return: [description]
    :rtype: [type]
    """
    truth_table = TruthTable(num_lits)

    for i in range(1 << num_lits):
        truth_table.set_true(i)
    return truth_table


def read_truth_table(truth_table_str: str):
    """Reads a truth table from a truth table .

    :param truth_table_str: [description]
    :type truth_table_str: str
    """

    num_lits = int(log(len(truth_table_str), 2))

    truth_table = TruthTable(num_lits)

    for index, char in enumerate(truth_table_str):
        if char == "0":
            truth_table.set_false(index)
        elif char == "1":
            truth_table.set_true(index)

        # the other cases are don't care

    return truth_table
