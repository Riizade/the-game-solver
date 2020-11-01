from game_state import simulate, PrintLevel
from strategies import greedy, random


def main():
    print("evaluating greedy strategy")
    simulate(greedy, 1000, PrintLevel.AGGREGATE)

    print("evaluating random strategy")
    simulate(random, 1000, PrintLevel.AGGREGATE)


if __name__ == "__main__":
    main()
