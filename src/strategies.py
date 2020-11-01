from random import shuffle
from game_state import PlayerTurn, GameState, take_action


def greedy(state: GameState) -> PlayerTurn:
    return state.greediest_turn


def random(state: GameState) -> PlayerTurn:
    valid_actions = state.all_valid_actions.copy()
    shuffle(valid_actions)

    for action in valid_actions:
        new_state = take_action(state, action)
        if new_state.has_one_valid_action:
            new_valid_actions = new_state.all_valid_actions.copy()
            shuffle(new_valid_actions)
            second_action = new_valid_actions[0]
            return PlayerTurn([action, second_action])
