# constants.py
"""Contains enums"""

from enum import StrEnum, auto

class Action(StrEnum):
    BEGIN_GAME = auto()
    BEGIN_ROUND = auto()
    PLAY_CARD = auto()
    PICKUP_CARD = auto()
    END_ROUND = auto()
    END_GAME = auto()


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
