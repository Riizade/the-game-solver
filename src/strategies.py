from random import choice as random_choice
from typing import Callable, Dict, List, Tuple
from functools import cmp_to_key
from dataclasses import dataclass

from game_state import Card, CardPile, PlayerAction, PlayerTurn, GameState, take_action


def greedy(state: GameState) -> PlayerTurn:
    def normalized_change_compare(a: PlayerAction, b: PlayerAction) -> bool:
        a_val = a.change_normalized(state)
        b_val = b.change_normalized(state)
        return a_val < b_val

    return prioritization(state, normalized_change_compare)


def random(state: GameState) -> PlayerTurn:
    def random_compare(a: PlayerAction, b: PlayerAction) -> bool:
        return random_choice([True, False])

    return prioritization(state, random_compare)


def prioritize_jumps(state: GameState) -> PlayerTurn:
    @dataclass(frozen=True)
    class JumpPlay:
        setup_card: Card
        jump_card: Card
        # normalized change value for given pile (less is better)
        normalized_change_values: Dict[int, int]

    # define all possible jump plays
    jump_plays: List[JumpPlay] = []
    for card in state.hand:
        for other in state.hand:
            if card.value + 10 == other.value or card.value - 10 == other.value:
                normalized_change_values: Dict[int, int] = {}
                for index, pile in enumerate(state.piles):
                    if card.can_be_placed_on_pile(pile):
                        change = other.value - pile.face_card.value
                        normalized_change = change
                        if pile.descending:
                            normalized_change = -1 * change
                        normalized_change_values[index] = normalized_change
                jump_plays.append(JumpPlay(card, other, normalized_change_values))

    def part_of_good_jump_play(action: PlayerAction) -> bool:
        for play in jump_plays:
            if action.chosen_card == play.setup_card:
                for normalized_value in play.normalized_change_values.values():
                    if normalized_value <= 0:
                        return True

        return False

    def jump_play_compare(a: PlayerAction, b: PlayerAction) -> bool:
        a_val = a.change_normalized(state)
        b_val = b.change_normalized(state)

        if part_of_good_jump_play(a):
            a_val -= 100
        if part_of_good_jump_play(b):
            b_val -= 100

        return a_val < b_val

    return prioritization(state, jump_play_compare)


# same as the greedy strategy but will deprioritize playing a card that would shift a pile from displaying a card for which the -10 still remains in the deck
def greedy_tracks_tens(state: GameState) -> PlayerTurn:
    def tracks_tens_compare(a: PlayerAction, b: PlayerAction) -> bool:
        a_val = a.change_normalized(state)
        b_val = b.change_normalized(state)

        if get_ten_value(a) in state.deck:
            a_val - 1000

        if get_ten_value(b) in state.deck:
            b_val - 1000
        return a_val < b_val

    def get_ten_value(action: PlayerAction) -> Card:
        pile = state.piles[action.chosen_pile_index]
        if pile.ascending:
            return Card(pile.face_card.value - 10)
        elif pile.descending:
            return Card(pile.face_card.value + 10)

    return prioritization(state, tracks_tens_compare)


# generic strategy function that takes a less_than function that compares two PlayerActions (less is better when comparing)
# less_than()'s signature looks like: def less_than(a: PlayerAction, b: PlayerAction) -> bool
# less_than() returns True if a < b, False otherwise
def prioritization(state: GameState, less_than: Callable[[PlayerAction, PlayerAction], bool]) -> PlayerTurn:
    # define full comparator function from less_than
    def compare(a: PlayerAction, b: PlayerAction):
        if less_than(a, b):
            return -1
        elif less_than(b, a):
            return 1
        else:
            return 0

    # transform old style comparator function to new style key function
    key = cmp_to_key(compare)

    # sort all valid actions
    valid_actions: List[PlayerAction] = state.all_valid_actions.copy()
    sorted_actions = sorted(valid_actions, key=key)

    # pick the best action that allows us to take a second action, then pick the best second action
    for action in sorted_actions:
        new_state = take_action(state, action)
        if new_state.has_one_valid_action:
            new_valid_actions = new_state.all_valid_actions.copy()
            new_sorted_actions = sorted(new_valid_actions, key=key)
            second_action = new_sorted_actions[0]
            return PlayerTurn([action, second_action])
