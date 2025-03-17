from dataclasses import dataclass

from lostcitinacki.models.constants import Color, DrawFromStack
from lostcitinacki.models.game_state import GameState
from lostcitinacki.models.piles import Discard
from lostcitinacki.players import Player
from lostcitinacki.renderers import Renderer


@dataclass
class LostCities:
    players: list[Player]
    renderer: Renderer
    max_rounds: int = 3

    @property
    def player_cnt(self) -> int:
        return len(self.players)

    def play(self) -> None:
        gs = GameState(self.player_cnt, self.max_rounds, current_round_number=3)

        while True:
            while True:
                self.renderer.render(gs, self.players)
                turn_idx = gs.player_turn_idx
                player = self.players[turn_idx]
                try:
                    selected_card, play_to_stack = player.play_card(gs.hands[turn_idx], gs.board_playable_cards)
                    color_or_discard: Color | Discard = gs.play_card_to(turn_idx, selected_card, play_to_stack)
                    can_pick_up_discard: bool = not isinstance(color_or_discard, Discard) and len(gs.discard) > 0
                    drawing_from: DrawFromStack = player.pick_up_from(can_pick_up_discard, gs.is_discard_card_playable)
                    print('Drawing From', drawing_from)
                    gs.draw_from(turn_idx, drawing_from)

                except Exception as ex:
                    self.renderer.render_error(ex)

                if gs.is_round_over:
                    gs.assign_points()
                    gs.current_round_number += 1
                    break

            if gs.is_game_over:
                break

            self.renderer.render(gs, self.players)
            gs.create_new_round()

        self.renderer.render(gs, self.players)
