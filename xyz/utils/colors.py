#!/usr/bin/env python
__all__ = [
    "print_green",
    "print_red",
    "print_yellow",
    "text_red",
    "text_yellow",
    "print_blue",
    "print_orange",
    "text_orange",
]

# text colors
# reference: https://www.codeproject.com/Articles/5329247/How-to-change-text-color-in-a-Linux-terminal


def print_green(text: str, **kwargs):
    """
    Print a green green .

    :param text: [description]
    :type text: str

    """
    print(f"\033[92m{text}\033[39m", **kwargs)


def print_red(text: str, **kwargs):
    """
    Print a red message with red .

    :param text: [description]
    :type text: str

    """
    print(f"\033[91m{text}\033[39m", **kwargs)


def print_yellow(text: str, **kwargs):
    """
    Print a yellow color.

    :param text: [description]
    :type text: str

    """
    print(f"\033[93m{text}\033[39m", **kwargs)


def text_red(text: str):
    """
    Return a text representation of text .

    :param text: [description]
    :type text: str
    :return: [description]
    :rtype: [type]

    """
    return f"\033[91m{text}\033[39m"


def text_yellow(text: str):
    """
    Return a pretty printed text for text .

    :param text: [description]
    :type text: str
    :return: [description]
    :rtype: [type]

    """
    return f"\033[93m{text}\033[39m"


def print_blue(text: str, **kwargs):
    """
    Print a blue color .

    :param text: [description]
    :type text: str

    """
    print(f"\033[94m{text}\033[39m", **kwargs)


def print_orange(text: str, **kwargs):
    """
    Print an Orange color .

    :param text: [description]
    :type text: str

    """
    print(f"\033[93m{text}\033[39m", **kwargs)


def text_orange(text: str):
    return f"\033[93m{text}\033[39m"
