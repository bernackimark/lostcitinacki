# constants.py
"""Contains enums"""

from enum import StrEnum, auto


class Color(StrEnum):
    YELLOW = auto()
    BLUE = auto()
    WHITE = auto()
    GREEN = auto()
    RED = auto()


class PlayToStack(StrEnum):
    EXPEDITION = auto()
    DISCARD = auto()


class DrawFromStack(StrEnum):
    DECK = auto()
    DISCARD = auto()
