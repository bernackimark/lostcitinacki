from dataclasses import dataclass
import random
from typing import Self

from players import Player, ConsolePlayer, BotPlayer
from models import Card, Color, Deck, Discard, DrawFromStack, Hand, PlayToStack, Stack
from renderers import Renderer


class Game:
    @staticmethod
    def deal(source_pile: Stack, dest_piles: list[Stack], dealer_idx: int, card_cnt: int) -> None:
        ordered_dest_piles = dest_piles[dealer_idx + 1 % len(dest_piles):] + dest_piles[:dealer_idx + 1]
        [p.add_card(source_pile.pop()) for _ in range(card_cnt) for p in ordered_dest_piles]

    @staticmethod
    def next_player_idx(current_idx: int, player_cnt: int) -> int:
        return (current_idx + 1) % player_cnt


@dataclass
class LostCities:
    players: list[Player]
    renderer: Renderer
    max_rounds: int
    deck: Deck
    discard: Discard
    dealer_idx: int = None
    player_turn_idx: int = None
    current_round_number: int = 1

    def __post_init__(self):
        self.dealer_idx = random.randint(0, self.player_cnt - 1) if self.dealer_idx is None else self.dealer_idx
        self.player_turn_idx = Game.next_player_idx(self.dealer_idx, self.player_cnt)

    @classmethod
    def create_new_game(cls, players: list[Player], renderer: Renderer, max_rounds) -> Self:
        new_game = cls(players, renderer, max_rounds, Deck(), Discard())
        new_game.deal()
        return new_game

    @property
    def player_cnt(self) -> int:
        return len(self.players)

    @property
    def is_game_over(self) -> bool:
        return self.is_round_over and self.current_round_number >= self.max_rounds

    @property
    def is_round_over(self) -> bool:
        return len(self.deck.cards) == 0 or set(self.color_maxes.values()) == {10}

    @property
    def winner(self) -> None | tuple[int, int] | list[tuple[int, int]]:
        """Returns None is game not over; tuple[player_idx, points] if solo winner else list[tuple[]] for ties"""
        if not self.is_game_over:
            return None
        p_idx_points: list[tuple[int, int]] = [(i, p.points) for i, p in enumerate(self.players)]
        max_points = max(t[1] for t in p_idx_points)
        winners = [e for e in p_idx_points if e[1] == max_points]
        return winners[0] if len(winners) == 1 else winners

    @property
    def color_maxes(self) -> dict[Color: int]:
        return {c: max([p.expeditions.get_max_card_in_color(c) for p in self.players]) for c in list(Color)}

    @property
    def board_playable_cards(self) -> list[Card]:
        # TODO: this belongs in the Hand class, but it needs access to game_state, and i'll need to re-org the code
        fresh_deck = Deck()
        return [c for c in fresh_deck if c.value > self.color_maxes[c.color] or self.color_maxes[c.color] == 0]

    def create_new_round(self):
        [p.hand.clear() for p in self.players]
        [p.expeditions.clear() for p in self.players]
        self.deck = Deck()
        self.discard = Discard()
        self.dealer_idx = Game.next_player_idx(self.dealer_idx, self.player_cnt)
        self.player_turn_idx = Game.next_player_idx(self.dealer_idx, self.player_cnt)
        self.deal()

    def deal(self, card_cnt: int = 8):
        Game.deal(self.deck, [p.hand for p in self.players], self.dealer_idx, card_cnt)

    def play_to(self, p: Player, c: Card, dest_pile: PlayToStack) -> Color | Discard:
        if c not in p.hand.cards:
            raise ValueError(f"{c} is not in {p.name}'s hand")
        if dest_pile == PlayToStack.DISCARD:
            return self._play_to_discard(p.hand, c)
        else:
            return self._play_to_exp_pile(p, c)

    def draw_from(self, p: Player, source_pile: DrawFromStack):
        returned_card = self.deck.pop() if source_pile == DrawFromStack.DECK else self.discard.pop()
        if not returned_card:
            raise ValueError("There are no cards here")
        p.hand.add_card(returned_card)
        self.player_turn_idx = Game.next_player_idx(self.player_turn_idx, self.player_cnt)

    def _play_to_discard(self, h: Hand, c: Card) -> Discard:
        h.remove_card(c)
        self.discard.add_card(c)
        return self.discard

    def _play_to_exp_pile(self, p: Player, c: Card) -> Color:
        dest_pile = next(pile for pile in p.expeditions if pile.color == c.color)
        max_number_in_color = max([p.expeditions.get_max_card_in_color(c.color) for p in self.players])
        if max_number_in_color > c.value > 0:
            raise ValueError(f"You must play higher than a {max_number_in_color}")
        p.hand.remove_card(c)
        dest_pile.add_card(c)
        return dest_pile.color

    def assign_points(self) -> None:
        for p in self.players:
            p.round_scores.append(p.expeditions.points)

    def play(self, players: list[Player], renderer: Renderer, max_rounds: int = 3) -> None:
        game_state = self.create_new_game(players, renderer, max_rounds)

        while True:
            while True:
                self.renderer.render(game_state, self.players)
                if game_state.is_round_over:
                    game_state.assign_points()
                    break
                player = game_state.players[game_state.player_turn_idx]
                try:
                    selected_card, play_to_stack = player.play_card(self.board_playable_cards)
                    color_or_discard: Color | Discard = self.play_to(player, selected_card, play_to_stack)
                    draw_from: DrawFromStack = player.pick_up_from(color_or_discard, len(self.discard) > 0)
                    self.draw_from(player, draw_from)
                except Exception as ex:
                    self.renderer.render_error(ex)

            if game_state.is_game_over:
                break

            self.renderer.render(game_state, self.players)
            self.create_new_round()

        self.renderer.render(game_state, self.players)
