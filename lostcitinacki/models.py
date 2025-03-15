from dataclasses import dataclass, field
from enum import StrEnum, auto
import random

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

@dataclass
class Card:
    color: Color
    value: int

@dataclass
class Handshake(Card):
    value: int = 0

    def __repr__(self) -> str:
        return f'{self.color[0].upper()}H'

@dataclass
class Expedition(Card):
    def __repr__(self) -> str:
        return f'{self.color[0].upper()}{self.value}'

@dataclass
class Stack:
    cards: list[Card] = field(default_factory=list)

    def __iter__(self):
        return iter(self.cards)

    def __len__(self) -> int:
        return len(self.cards) if self.cards else 0

    def shuffle(self):
        random.shuffle(self.cards)

    def add_card(self, card: Card):
        if not isinstance(card, Card):
            raise ValueError("This is not a card")
        self.cards.append(card)

    def remove_card(self, card: Card):
        if card not in self.cards:
            raise ValueError(f"{card} not found")
        self.cards.remove(card)

    def pop(self) -> Card | None:
        return self.cards.pop() if self.cards else None

    def clear(self) -> None:
        self.cards.clear()

@dataclass
class ExpeditionPile(Stack):
    def __init__(self, cards: list[Card], color: Color):
        super().__init__(cards)
        self.color = color

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

def create_board() -> list[ExpeditionPile]:
    return [ExpeditionPile([], c) for c in list(Color)]

@dataclass
class ExpeditionBoard:
    expedition_piles: list[ExpeditionPile] = field(default_factory=create_board)

    def __repr__(self) -> str:
        return 'Expeditions: ' + ' '.join([ep.__repr__() for ep in self.expedition_piles])

    def __iter__(self):
        return iter(self.expedition_piles)

    @property
    def points(self) -> int:
        return sum([p.points for p in self.expedition_piles])

    def get_max_card_in_color(self, color: Color) -> int:
        numbered_cards = [c.value for p in self for c in p if p.color == color and isinstance(c, Expedition)]
        return max(numbered_cards) if numbered_cards else 0

    def clear(self) -> None:
        [pile.clear() for pile in self.expedition_piles]

@dataclass
class Hand(Stack):
    ...

@dataclass
class Discard(Stack):
    ...


def build_deck() -> list[Card]:
    handshakes: list[Handshake] = [Handshake(c) for c in list(Color) for _ in range(3)]
    expeditions: list[Expedition] = [Expedition(c, v) for c in list(Color) for v in range(2, 11)]
    return handshakes + expeditions

@dataclass
class Deck(Stack):
    cards: list[Card] = field(default_factory=build_deck)
    start_shuffled: bool = True

    def __post_init__(self):
        if self.start_shuffled:
            random.shuffle(self.cards)



