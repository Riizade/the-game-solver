from game_state import PlayerTurn, GameState


def greedy(state: GameState) -> PlayerTurn:

    return state.greediest_turn
