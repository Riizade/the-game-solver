from game_state import PlayerTurn, VisibleGameState
from strategy_info import state_information


def greedy(state: VisibleGameState) -> PlayerTurn:
    info = state_information(state)

    return info.greediest_turn
