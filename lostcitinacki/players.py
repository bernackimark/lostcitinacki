from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import random

from models import Card, Color, Discard, DrawFromStack, ExpeditionBoard, Hand, PlayToStack

@dataclass
class Player(ABC):
    name: str
    hand: Hand = field(default_factory=Hand)
    expeditions: ExpeditionBoard = field(default_factory=ExpeditionBoard)
    round_scores: list[int] = field(default_factory=list)

    @property
    def points(self) -> int:
        return sum(self.round_scores) if self.round_scores else 0

    @abstractmethod
    def play_card(self, board_playable_cards: list[Card]) -> tuple[Card, PlayToStack]:
        ...

    @abstractmethod
    def pick_up_from(self, played_to: Color | Discard, discard_has_cards: bool) -> DrawFromStack:
        ...


@dataclass
class ConsolePlayer(Player):
    def play_card(self, board_playable_cards: list[Card]) -> tuple[Card, PlayToStack]:
        while True:
            sel_card = input('Select a card to play: ')
            card = next((c for c in self.hand if c.__repr__() == sel_card), None)
            if card is not None:
                break
        while True:
            value = input('Play to expedition or discard (e/d): ')
            if value in ('e', 'd'):
                return card, PlayToStack.EXPEDITION if value == 'e' else PlayToStack.DISCARD

    def pick_up_from(self, played_to: Color | Discard, discard_has_cards: bool) -> DrawFromStack:
        if played_to is Discard or not discard_has_cards:
            return DrawFromStack.DECK
        while True:
            value = input('Pick up from deck or discard (de/di): ')
            if value in ('de', 'di'):
                return DrawFromStack.DECK if value == 'de' else DrawFromStack.DISCARD

@dataclass
class BotPlayer(Player):
    def play_card(self, board_playable_cards: list[Card]) -> tuple[Card, PlayToStack]:
        playable_cards = [card for card in self.hand.cards if card in board_playable_cards]
        if not playable_cards:
            return random.choice(self.hand.cards), PlayToStack.DISCARD
        return random.choice(playable_cards), PlayToStack.EXPEDITION

    def pick_up_from(self, played_to: Color | Discard, discard_has_cards: bool) -> DrawFromStack:
        if played_to is Discard or not discard_has_cards:
            return DrawFromStack.DECK
        return DrawFromStack.DECK if random.randint(1, 10) > 8 else DrawFromStack.DISCARD
