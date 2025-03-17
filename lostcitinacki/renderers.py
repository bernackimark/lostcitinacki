import abc
import time

from lostcitinacki.players import Player
from lostcitinacki.models.game_state import GameState


class Renderer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def render(self, game_state: GameState, players: list[Player]) -> None:
        """Render the current game state & player information"""

    @abc.abstractmethod
    def render_error(self, exc: Exception) -> None:
        """Render an exception"""


class ConsoleRenderer(Renderer):
    def render(self, gs: GameState, players: list[Player]) -> None:
        if not gs.has_round_started:
            print(f"This is round #{gs.current_round_number} of {gs.max_rounds}")
            print(f"{players[gs.dealer_idx].name} is the dealer; {players[gs.player_turn_idx].name} plays first")
            print()

        if not gs.is_round_over and not gs.is_round_over:
            print('Their Expeditions:', gs.exp_boards[1].expeditions)
            print('Discard:', gs.discard.cards[-1] if gs.discard.cards else '[]', 'Deck:',
                  '*' * len(gs.deck.cards))
            print('Your Expeditions: ', gs.exp_boards[0].expeditions)
            print('Your Hand:', gs.hands[0].cards)
            print()

        if gs.is_round_over:
            print('Round is over')
            for p, ledger in zip(players, gs.scorer.ledgers):
                print(f'{p.name} has {ledger.total} {"points" if ledger.total != 1 else "point"}')

        if gs.is_game_over:
            print('Game is over')
            if isinstance(gs.winner, tuple):
                winner_idx, points = gs.winner
                print(f"The winner is {players[winner_idx].name} with "
                      f"{points} {'point' if points == 1 else 'points'}")
            else:
                winner_names = 'and '.join([p.name for i, p in enumerate(players) for idx in gs.winner if i == idx])
                points = gs.winner[0][1]
                print(f"{winner_names} tied with {points} {'points' if gs.scorer.ledgers[0].total != 1 else 'point'}")
            print('Thank you for playing.  Goodbye!')
            time.sleep(2)

    def render_error(self, exc: Exception) -> None:
        print(f"Something's gone wrong: {exc}")
        print()

