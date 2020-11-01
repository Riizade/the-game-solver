from random import choice as random_choice
from typing import Callable, Dict, List
from functools import cmp_to_key

from game_state import Card, PlayerAction, PlayerTurn, GameState, take_action, take_turn


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


backtrack_solver_cache: Dict[GameState, PlayerTurn] = {}


# this solver cheats by "looking into the future" and knowing which cards it will draw after playing
def backtrack_solver(state: GameState) -> PlayerTurn:
    # if the cache has been populated with a winning strategy
    if state in backtrack_solver_cache:
        return backtrack_solver_cache[state]

    valid_turns_stack = [state.all_valid_turns]
    turn_index_stack = [0]
    state_stack = [state]
    while not state_stack[-1].has_won and len(state_stack) > 0:
        print(f"action stack: {valid_turns_stack}")
        print(f"index stack: {turn_index_stack}")
        # if we can evaluate the currently selected turn index
        if turn_index_stack[-1] < len(valid_turns_stack[-1]):
            # select the turn
            turn = valid_turns_stack[-1][turn_index_stack[-1]]
            # evaluate new state
            new_state = take_turn(state_stack[-1], turn)
            # mark the turn as evaluated (select next turn)
            turn_index_stack[-1] += 1

            # increment the stacks
            turn_index_stack.append(0)
            state_stack.append(new_state)
            valid_turns_stack.append(new_state.all_valid_turns)
        else:  # if we've run out of turns to evaluate on this frame
            # pop the stacks to backtrack
            turn_index_stack.pop()
            valid_turns_stack.pop()
            state_stack.pop()

    # when we exit the loop, either we've found a winning strategy, or we've evaluated all strategies and not found a winner
    if len(state_stack) == 0:  # indicates we did not find a strategy, just return any turn and expect to lose
        return state.all_valid_turns[0]
    elif state_stack[-1].has_won:  # indicates we've won
        # populate the cache with the winning strategy
        for i in range(len(state_stack)):
            backtrack_solver_cache[state_stack[i]] = valid_turns_stack[i][turn_index_stack[i]]
        # return the first turn from the winning strategy
        return backtrack_solver_cache[state]
    else:
        raise Exception("unexpectedly finished backtracking without winning")
