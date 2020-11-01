
from game_state import initial_deck


def test_seeded_deck_randomizes_order():
    for seed1 in range(0, 10):
        for seed2 in range(101, 110):
            assert(initial_deck(seed1) != initial_deck(seed2))


def test_seeded_deck_generates_equivalent_results_from_same_seed():
    for seed in range(0, 10):
        assert(initial_deck(seed) == initial_deck(seed))


def test_generated_deck_contains_all_cards():
    for seed in range(0, 10):
        deck = initial_deck(seed)
        for card in range(2, 100):
            assert(card in deck)


def test_take_turn():
    assert(False)


def test_take_action():
    assert(False)
