
from typing import List

from game_state import initial_deck, initial_piles, take_action, take_turn, Card, CardPile, GameState, PlayerAction, PlayerTurn


def card_list(ints: List[int]) -> List[Card]:
    return [Card(i) for i in ints]


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
        for num in range(2, 100):
            assert(Card(num) in deck)


def test_initial_piles():
    piles = initial_piles()
    assert(len(piles) == 4)
    ascending = CardPile(cards=card_list([1]), ascending=True)
    descending = CardPile(cards=card_list([100]), ascending=False)
    assert(piles[0] == ascending)
    assert(piles[1] == ascending)
    assert(piles[2] == descending)
    assert(piles[3] == descending)


def test_take_turn():
    initial_state = GameState(deck=card_list([10, 11, 12, 13, 14, 15, 16, 17, 18]), hand=card_list([2, 3, 4, 5, 6, 7, 89, 99]), piles=initial_piles())
    initial_state_copy = GameState(deck=card_list([10, 11, 12, 13, 14, 15, 16, 17, 18]), hand=card_list([2, 3, 4, 5, 6, 7, 89, 99]), piles=initial_piles())

    actions = [
        PlayerAction(Card(2), 0),
        PlayerAction(Card(3), 1),
        PlayerAction(Card(6), 1),
        PlayerAction(Card(99), 2),
        PlayerAction(Card(89), 2),
    ]

    turn = PlayerTurn(actions=actions)

    expected_piles = [
        CardPile(cards=card_list([1, 2]), ascending=True),
        CardPile(cards=card_list([1, 3, 6]), ascending=True),
        CardPile(cards=card_list([100, 99, 89]), ascending=False),
        CardPile(cards=card_list([100]), ascending=False),
    ]
    expected_result = GameState(deck=card_list([10, 11, 12, 13]), hand=card_list([4, 5, 7, 14, 15, 16, 17, 18]), piles=expected_piles)

    actual_result = take_turn(initial_state, turn)

    # assert expected result
    assert(actual_result == expected_result)

    # assert not mutated
    assert(initial_state == initial_state_copy)


def test_take_action():
    initial_state = GameState(deck=card_list([4, 5, 6]), hand=card_list([2, 3]), piles=initial_piles())
    initial_state_copy = GameState(deck=card_list([4, 5, 6]), hand=card_list([2, 3]), piles=initial_piles())

    action = PlayerAction(Card(2), 0)

    expected_piles = [
        CardPile(cards=card_list([1, 2]), ascending=True),
        CardPile(cards=card_list([1]), ascending=True),
        CardPile(cards=card_list([100]), ascending=False),
        CardPile(cards=card_list([100]), ascending=False),
    ]

    expected_result = GameState(deck=card_list([4, 5, 6]), hand=card_list([3]), piles=expected_piles)

    actual_result = take_action(initial_state, action)

    # assert expected result
    assert(actual_result == expected_result)

    # assert not mutated
    assert(initial_state == initial_state_copy)
