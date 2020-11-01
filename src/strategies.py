from game_state import PlayerTurn, VisibleGameState


def greedy(state: VisibleGameState) -> PlayerTurn:

    return state.greediest_turn
