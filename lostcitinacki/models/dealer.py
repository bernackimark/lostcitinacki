import random

from lostcitinacki.models.stack import Stack


class Dealer:
    """A grouping of commonly-used Dealer methods, such as dealing and worrying about turns"""
    @staticmethod
    def select_random_p_idx(player_cnt: int):
        return random.randint(0, player_cnt - 1)

    @staticmethod
    def deal(source_pile: Stack, dest_piles: list[Stack], dealer_idx: int, card_cnt: int) -> None:
        ordered_dest_piles = dest_piles[dealer_idx + 1 % len(dest_piles):] + dest_piles[:dealer_idx + 1]
        [p.push(source_pile.pop()) for _ in range(card_cnt) for p in ordered_dest_piles]

    @staticmethod
    def next_player_idx(current_idx: int, player_cnt: int) -> int:
        return (current_idx + 1) % player_cnt
