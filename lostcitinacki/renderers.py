import abc
import time

from players import Player
from engine import LostCities


class Renderer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def render(self, game_state: LostCities, players: list[Player]) -> None:
        """Render the current game state & player information"""

    @abc.abstractmethod
    def render_error(self, exc: Exception) -> None:
        """Render an exception"""


class ConsoleRenderer(Renderer):
    def render(self, gs: LostCities, players: list[Player]) -> None:
        if not gs.is_round_over and not gs.is_round_over:
            print('Their Expeditions:', gs.players[1].expeditions)
            print('Discard:', gs.discard.cards[-1] if gs.discard.cards else '[]', 'Deck:',
                  '*' * len(gs.deck.cards))
            print('Your Expeditions: ', gs.players[0].expeditions)
            print('Your Hand:', gs.players[0].hand.cards)

        if gs.is_round_over:
            print('Round is over')
            [print(f'{p.name} has {p.points} {"points" if p.points != 1 else "point"}') for p in gs.players]

        if gs.is_game_over:
            print('Game is over')
            if isinstance(gs.winner, tuple):
                winner_idx, points = gs.winner
                print(f"The winner is {gs.players[winner_idx].name} with"
                      f"{points} {'point' if points == 1 else 'points'}")
            else:
                winner_names = 'and '.join([p.name for i, p in enumerate(gs.players) for idx in gs.winner if i == idx])
                points = gs.winner[0][1]
                print(f"{winner_names} tied with {points} {'points' if p.points != 1 else 'point'}")
                print('Thank you for playing.  Goodbye!')
                time.sleep(2)

    def render_error(self, exc: Exception) -> None:
        print(f"Something's gone wrong: {exc}")

