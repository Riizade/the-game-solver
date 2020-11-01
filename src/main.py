from game_state import simulate, PrintLevel
from strategies import greedy, greedy_tracks_tens, random


def main():
    num_runs = 100
    strats = [greedy, random, greedy_tracks_tens]

    for strat in strats:
        print(f"evaluating strategy {strat.__name__}")
        simulate(strat, num_runs, PrintLevel.AGGREGATE)


if __name__ == "__main__":
    main()
