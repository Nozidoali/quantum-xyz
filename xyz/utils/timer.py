#!/usr/bin/env python
# -*- encoding=utf8 -*-
"""
Author: Hanyu Wang
Created time: 2023-02-28 07:43:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-03-11 20:53:23
"""

#
# reference: https://realpython.com/python-with-statement/#writing-a-sample-class-based-context-manager
#
import time

from .colors import print_green


class stopwatch:
    """
    Create a new Stopwatch class .

    :return: [description]
    :rtype: [type]

    """

    # name the functions run inside this context
    def __init__(self, name: str, verbose: bool = False):
        """
        @brief Initialize a : class : ` Stopwatch `. This is the constructor for : class : ` Stopwatch `.
        @param name The name of the stopwatch. Must be at least 25 characters
        """
        assert len(name) <= 25 and "stopwatch name is too long"
        self.name = name
        self.tic = None
        self.toc = None
        self.verbose = verbose
        self.duration = None

    def __enter__(self):
        """
        @brief Called when the thread enters. Stores the time in self. tic and returns it to __
        """
        self.tic = time.perf_counter()
        return self

    # reference: https://realpython.com/python-timer/#your-first-python-timer
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        @brief Called when the process exits. Prints information about the process to the console. This is a no - op in this case.
        @param exc_type The type of exception that was raised.
        @param exc_val The value of the exception that was raised.
        @param exc_tb The traceback of the exception that was raised
        """
        self.toc = time.perf_counter()
        self.duration = self.toc - self.tic
        if self.name is not None and self.verbose:
            print_green(f"{self.name:<25}: {self.duration:>8.02f} sec")

    def time(self):
        """
        @brief Time since last call to start (). This is useful for measuring how long we've been in the middle of a test to run.
        @return The number of seconds since the start () call that took place in the test's run () method
        """
        return float(time.perf_counter() - self.tic)


GLOBAL_STOPWATCHES = {}


class GlobalStopwatch:
    """
    A class decorator that creates a global stopwatch .

    :return: [description]
    :rtype: [type]

    """

    # name the functions run inside this context
    def __init__(self, name: str):
        """
        @brief Initialize a : class : ` Stopwatch `. This is the constructor for : class : ` Stopwatch `.
        @param name The name of the stopwatch. Must be at least 25 characters
        """
        assert len(name) <= 25 and "stopwatch name is too long"
        self.name = name
        self.tic = None
        self.toc = None

    def __enter__(self):
        """
        @brief Called when the thread enters. Stores the time in self. tic and returns it to __
        """
        self.tic = time.perf_counter()

    # reference: https://realpython.com/python-timer/#your-first-python-timer
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        @brief Called when the process exits. Prints information about the process to the console. This is a no - op in this case.
        @param exc_type The type of exception that was raised.
        @param exc_val The value of the exception that was raised.
        @param exc_tb The traceback of the exception that was raised
        """
        self.toc = time.perf_counter()
        if self.name not in GLOBAL_STOPWATCHES:
            GLOBAL_STOPWATCHES[self.name] = 0
        GLOBAL_STOPWATCHES[self.name] += self.toc - self.tic
        # print_green("{:<25}: {:>8.02f} sec".format(self.name, self.toc - self.tic))

    def time(self):
        """
        @brief Time since last call to start (). This is useful for measuring how long we've been in the middle of a test to run.
        @return The number of seconds since the start () call that took place in the test's run () method
        """
        return GLOBAL_STOPWATCHES[self.name]


def call_with_global_timer(func):
    """
    Call function with global timer .

    :param func: [description]
    :type func: [type]

    """

    def timed_func(*args, **kwargs):
        with GlobalStopwatch(func.__name__):
            return func(*args, **kwargs)

    return timed_func


def get_time(name: str):
    """
    Get the current stop time for a given name .

    :param name: [description]
    :type name: str
    :return: [description]
    :rtype: [type]

    """
    if name not in GLOBAL_STOPWATCHES:
        return 0
    return GLOBAL_STOPWATCHES[name]


def global_stopwatch_report():
    """Report the global stopwatch ."""
    for name, current_time in GLOBAL_STOPWATCHES.items():
        print_green(f"{name:<25}: {current_time:>8.02f} sec")
