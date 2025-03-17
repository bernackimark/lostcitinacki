# piles.py
"""A module for collections of cards"""

import random
from dataclasses import dataclass, field

from lostcitinacki.models.cards import Card, Handshake, ExpeditionCard
from lostcitinacki.models.constants import Color
from lostcitinacki.models.stack import Stack


@dataclass
class CardStack(Stack):
    """This subclass' purpose is to have callers use the attribute 'cards' instead of the generic 'items'.
    If something subclasses CardStack & wants to initialize with cards, it will still need to use '_items --
     ex: _items: list[Card] = field(default_factory=build_deck)"""
    _items: list[Card] = field(default_factory=list)

    @property
    def cards(self) -> list:
        return self._items

    @cards.setter
    def cards(self, value: list):
        if not isinstance(value, list):
            raise ValueError("cards must be a list")
        for item in value:
            self.push(item)  # Ensure each item is of type Card when setting cards
        self._items = value


@dataclass
class Expedition(CardStack):
    color: Color = None

    def __post_init__(self):
        if not self.color:
            raise ValueError("Color must be provided")

    def __repr__(self) -> str:
        return f'{self.color.value} {self.cards}'

    @property
    def card_cnt(self) -> int:
        return len(self)

    @property
    def handshake_cnt(self) -> int:
        return sum([1 for c in self if isinstance(c, Handshake)])

    @property
    def points(self) -> int:
        if not self.card_cnt:
            return 0
        plus_minus = sum([c.value for c in self]) - 20
        multiplier = 1 + self.handshake_cnt
        bonus = 20 if self.card_cnt >= 8 else 0
        return plus_minus * multiplier + bonus


def create_board() -> list[Expedition]:
    return [Expedition([], c) for c in list(Color)]


@dataclass
class ExpeditionBoard:
    expeditions: list[Expedition] = field(default_factory=create_board)

    def __repr__(self) -> str:
        return 'Expeditions: ' + ' '.join([ep.__repr__() for ep in self.expeditions])

    def __iter__(self):
        return iter(self.expeditions)

    @property
    def points(self) -> int:
        return sum([p.points for p in self.expeditions])

    def get_max_card_in_color(self, color: Color) -> int:
        numbered_cards = [c.value for p in self for c in p if p.color == color and isinstance(c, ExpeditionCard)]
        return max(numbered_cards) if numbered_cards else 0

    def clear(self) -> None:
        [pile.clear() for pile in self.expeditions]


@dataclass
class Hand(CardStack):
    ...


@dataclass
class Discard(CardStack):
    ...


def build_deck() -> list[Card]:
    # handshakes: list[Handshake] = [Handshake(c) for c in list(Color) for _ in range(3)]
    expeditions: list[ExpeditionCard] = [ExpeditionCard(c, v) for c in list(Color) for v in range(6, 11)]
    # return handshakes + expeditions
    return expeditions


@dataclass
class Deck(CardStack):
    _items: list[Card] = field(default_factory=build_deck)
    start_shuffled: bool = True

    def __post_init__(self):
        if self.start_shuffled:
            random.shuffle(self._items)
