from game_state import simulate, PrintLevel
from strategies import greedy


def main():
    simulate(greedy, 1000, PrintLevel.AGGREGATE)


if __name__ == "__main__":
    main()
