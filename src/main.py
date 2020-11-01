from game_state import simulate, PrintLevel
from strategies import greedy


def main():
    simulate(greedy, 100, PrintLevel.EACH_TURN)


if __name__ == "__main__":
    main()
