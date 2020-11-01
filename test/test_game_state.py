
from game_state import initial_deck, initial_piles, take_action, take_turn, CardPile, GameState, PlayerAction, PlayerTurn


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


def test_initial_piles():
    piles = initial_piles()
    assert(len(piles) == 4)
    ascending = CardPile(cards=[1], ascending=True)
    descending = CardPile(cards=[100], ascending=False)
    assert(piles[0] == ascending)
    assert(piles[1] == ascending)
    assert(piles[2] == descending)
    assert(piles[3] == descending)


def test_take_turn():
    initial_state = GameState(deck=[10, 11, 12, 13, 14, 15, 16, 17, 18], hand=[2, 3, 4, 5, 6, 7, 89, 99], piles=initial_piles())
    initial_state_copy = GameState(deck=[10, 11, 12, 13, 14, 15, 16, 17, 18], hand=[2, 3, 4, 5, 6, 7, 89, 99], piles=initial_piles())

    actions = [
        PlayerAction(2, 0),
        PlayerAction(3, 1),
        PlayerAction(6, 1),
        PlayerAction(99, 2),
        PlayerAction(89, 2),
    ]

    turn = PlayerTurn(actions=actions)

    expected_piles = [
        CardPile(cards=[1, 2], ascending=True),
        CardPile(cards=[1, 3, 6], ascending=True),
        CardPile(cards=[100, 99, 89], ascending=False),
        CardPile(cards=[100], ascending=False),
    ]
    expected_result = GameState(deck=[10, 11, 12, 13], hand=[4, 5, 7, 14, 15, 16, 17, 18], piles=expected_piles)

    actual_result = take_turn(initial_state, turn)

    # assert expected result
    assert(actual_result == expected_result)

    # assert not mutated
    assert(initial_state == initial_state_copy)


def test_take_action():
    initial_state = GameState(deck=[4, 5, 6], hand=[2, 3], piles=initial_piles())
    initial_state_copy = GameState(deck=[4, 5, 6], hand=[2, 3], piles=initial_piles())

    action = PlayerAction(2, 0)

    expected_piles = [
        CardPile(cards=[1, 2], ascending=True),
        CardPile(cards=[1], ascending=True),
        CardPile(cards=[100], ascending=False),
        CardPile(cards=[100], ascending=False),
    ]

    expected_result = GameState(deck=[4, 5, 6], hand=[3], piles=expected_piles)

    actual_result = take_action(initial_state, action)

    # assert expected result
    assert(actual_result == expected_result)

    # assert not mutated
    assert(initial_state == initial_state_copy)
