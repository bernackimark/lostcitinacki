from dataclasses import dataclass, field

from lostcitinacki.models import GameState
from lostcitinacki.models.cards import Card
from lostcitinacki.models.constants import PlayToStack, DrawFromStack
from lostcitinacki.models.stack import Stack


@dataclass
class Move:
    player_idx: int
    card: Card
    played_card_to: PlayToStack
    picked_up_from: DrawFromStack
    prior_game_state: "GameState"
    after_game_state: "GameState"


@dataclass
class GameLog(Stack):
    moves: list[Move] = field(default_factory=list)

    def log_move(self, move: Move) -> None:
        self.moves.append(move)
