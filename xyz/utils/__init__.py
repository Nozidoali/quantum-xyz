"""Shared utilities: color printing, stopwatch."""

from xyz.utils.colors import (
    print_green,
    print_red,
    print_yellow,
    text_red,
    text_yellow,
    print_blue,
    print_orange,
    text_orange,
)
from xyz.utils.timer import (
    stopwatch,
    GlobalStopwatch,
    call_with_global_timer,
    get_time,
    global_stopwatch_report,
)

__all__ = [
    # colors
    "print_green", "print_red", "print_yellow",
    "text_red", "text_yellow",
    "print_blue", "print_orange", "text_orange",
    # timer
    "stopwatch", "GlobalStopwatch", "call_with_global_timer",
    "get_time", "global_stopwatch_report",
]
