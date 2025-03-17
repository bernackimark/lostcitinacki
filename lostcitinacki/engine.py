from dataclasses import dataclass, field

from lostcitinacki.models.constants import Color, DrawFromStack, Action
from lostcitinacki.models.game_state import GameState
from lostcitinacki.models.logs import GameLog, Event
from lostcitinacki.models.piles import Discard
from lostcitinacki.players import Player
from lostcitinacki.renderers import Renderer


@dataclass
class LostCities:
    players: list[Player]
    renderer: Renderer
    max_rounds: int = 3
    game_log: GameLog = field(default_factory=GameLog)

    @property
    def player_cnt(self) -> int:
        return len(self.players)

    def play(self) -> None:
        gs = GameState(self.player_cnt, self.max_rounds, current_round_number=3)
        self.game_log.push(Event(gs, Action.BEGIN_GAME))

        while True:
            while True:
                self.renderer.render(gs, self.players)
                turn_idx = gs.player_turn_idx
                player = self.players[turn_idx]
                try:
                    selected_card, play_to_stack = player.play_card(gs.hands[turn_idx], gs.board_playable_cards)
                    color_or_discard: Color | Discard = gs.play_card_to(turn_idx, selected_card, play_to_stack)
                    self.game_log.push(Event(gs, Action.PLAY_CARD, turn_idx))
                    can_pick_up_discard: bool = not isinstance(color_or_discard, Discard) and len(gs.discard) > 0
                    drawing_from: DrawFromStack = player.pick_up_from(can_pick_up_discard, gs.is_discard_card_playable)
                    gs.draw_from(turn_idx, drawing_from)
                    self.game_log.push(Event(gs, Action.PICKUP_CARD, turn_idx))

                except Exception as ex:
                    self.renderer.render_error(ex)

                if gs.is_round_over:
                    gs.assign_points()
                    self.game_log.push(Event(gs, Action.END_ROUND))
                    gs.current_round_number += 1
                    break

            if gs.is_game_over:
                break

            self.renderer.render(gs, self.players)
            gs.create_new_round()
            self.game_log.push(Event(gs, Action.BEGIN_ROUND))

        self.renderer.render(gs, self.players)
        self.game_log.push(Event(gs, Action.END_GAME))
        self.renderer.render_log(self.game_log)
