from dataclasses import dataclass, field

from lostcitinacki.models.cards import Card
from lostcitinacki.models.constants import Color, PlayToStack, DrawFromStack
from lostcitinacki.models.dealer import Dealer
from lostcitinacki.models.piles import Hand, ExpeditionBoard, Deck, Discard
from lostcitinacki.models.scorer import Ledger, Scorer, WinCondition


@dataclass
class GameState:
    player_cnt: int
    max_rounds: int
    hands: list[Hand] = field(default_factory=list)
    exp_boards: list[ExpeditionBoard] = field(default_factory=list)
    scorer: Scorer = None
    deck: Deck = field(default_factory=Deck)
    discard: Discard = field(default_factory=Discard)
    dealer_idx: int = None
    player_turn_idx: int = None
    current_round_number: int = 1

    def __post_init__(self):
        ledgers = []
        for _ in range(self.player_cnt):
            self.hands.append(Hand())
            self.exp_boards.append(ExpeditionBoard())
            ledgers.append(Ledger())
        self.scorer = Scorer(ledgers, WinCondition.HIGHEST_SCORE_W_TIES)
        self.dealer_idx = Dealer.select_random_p_idx(self.player_cnt) if self.dealer_idx is None else self.dealer_idx
        self.player_turn_idx = Dealer.next_player_idx(self.dealer_idx, self.player_cnt)
        self.deal()

    @property
    def has_round_started(self) -> bool:
        return self.discard.cards or any([exp.cards for exp_board in self.exp_boards for exp in exp_board])

    @property
    def is_game_over(self) -> bool:
        return self.is_round_over and self.current_round_number >= self.max_rounds

    @property
    def is_round_over(self) -> bool:
        return len(self.deck.cards) == 0 or set(self.color_maxes.values()) == {10}

    @property
    def winner(self) -> None | tuple[int, int] | list[tuple[int, int]]:
        """Returns None if game not over; tuple[player_idx, points] if solo winner else list[tuple[]] for ties"""
        if not self.is_game_over:
            return None
        return self.scorer.get_winner(self.is_game_over)

    @property
    def color_maxes(self) -> dict[Color: int]:
        return {c: max([p.get_max_card_in_color(c) for p in self.exp_boards]) for c in list(Color)}

    @property
    def board_playable_cards(self) -> list[Card]:
        fresh_deck = Deck()
        return [c for c in fresh_deck if c.value > self.color_maxes[c.color] or self.color_maxes[c.color] == 0]

    @property
    def is_discard_card_playable(self) -> bool:
        return self.discard.peek() in self.board_playable_cards

    def create_new_round(self):
        [h.clear() for h in self.hands]
        [e.clear() for e in self.exp_boards]
        self.deck = Deck()
        self.discard = Discard()
        self.dealer_idx = Dealer.next_player_idx(self.dealer_idx, self.player_cnt)
        self.player_turn_idx = Dealer.next_player_idx(self.dealer_idx, self.player_cnt)
        self.deal()

    def deal(self, card_cnt: int = 8):
        Dealer.deal(self.deck, [_ for _ in self.hands], self.dealer_idx, card_cnt)

    def play_card_to(self, p_idx: int, c: Card, dest_pile: PlayToStack) -> Color | Discard:
        hand = self.hands[p_idx]
        exp_board = self.exp_boards[p_idx]
        if c not in hand.cards:
            raise ValueError(f"{c} is not in the hand")
        if dest_pile == PlayToStack.DISCARD:
            return self._play_to_discard(hand, c)
        else:
            return self._play_to_exp_pile(hand, c, exp_board)

    def draw_from(self, p_idx: int, source_pile: DrawFromStack):
        hand = self.hands[p_idx]
        returned_card = self.deck.pop() if source_pile == DrawFromStack.DECK else self.discard.pop()
        if not returned_card:
            raise ValueError("There are no cards here")
        hand.push(returned_card)
        self.player_turn_idx = Dealer.next_player_idx(self.player_turn_idx, self.player_cnt)

    def _play_to_discard(self, h: Hand, c: Card) -> Discard:
        # before_state = self
        # move = Move(self.player_turn_idx, c, PlayToStack.DISCARD, None, self, None)
        h.remove(c)
        self.discard.push(c)
        return self.discard

    def _play_to_exp_pile(self, h: Hand, c: Card, exp_board: ExpeditionBoard) -> Color:
        dest_pile = next(pile for pile in exp_board.expeditions if pile.color == c.color)
        max_number_in_color = max([p.get_max_card_in_color(c.color) for p in self.exp_boards])
        if max_number_in_color > c.value > 0:
            raise ValueError(f"You must play higher than a {max_number_in_color}")
        h.remove(c)
        dest_pile.push(c)
        return dest_pile.color

    def assign_points(self) -> None:
        for pl, exp_board in zip(self.scorer.ledgers, self.exp_boards):
            pl.add_a_value(exp_board.points)
