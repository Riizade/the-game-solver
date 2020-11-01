from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple
import random
from enum import Enum
import sys
from functools import cached_property

from tqdm import tqdm
from frozenlist import FrozenList as FrozenList


class PrintLevel(Enum):
    NOTHING = 0
    AGGREGATE = 1
    WIN_LOSS = 2
    EACH_TURN = 3


@dataclass(frozen=True)
class Card:
    value: int

    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __lt__(self, other: Card) -> bool:
        return self.value < other.value

    def has_valid_play(self, state: GameState) -> bool:
        for pile in state.piles:
            if self in pile.valid_cards(state.hand):
                return True

        return False


@dataclass(frozen=True)
class CardPile:
    cards: FrozenList[Card]
    ascending: bool = True

    @cached_property
    def face_card(self) -> Card:
        return self.cards[-1]

    @cached_property
    def descending(self) -> bool:
        return not self.ascending

    @cached_property
    def visual(self) -> str:
        glyph = "^" if self.ascending else "v"
        return f"[ {self.face_card} {glyph} ]"

    # returns a map of card in hand to the change in value if that card is placed on the pile
    def change_if_placed(self, hand: FrozenList[Card]) -> Dict[Card, int]:
        result: Dict[Card, int] = {}
        for card in self.valid_cards(hand):
            result[card] = card.value - self.face_card.value
        return result

    def valid_cards(self, hand: FrozenList[Card]) -> FrozenList[Card]:
        result = FrozenList([x for x in filter(lambda c: self.placement_is_valid(c), hand)])
        result.freeze()
        return result

    def placement_is_valid(self, card: Card) -> bool:
        if card.value > self.face_card.value and self.ascending:
            return True
        elif card.value < self.face_card.value and self.descending:
            return True
        elif card.value == self.face_card.value + 10 or card.value == self.face_card.value - 10:
            return True
        else:
            return False


@dataclass(frozen=True)
class PlayerAction:
    chosen_card: Card
    chosen_pile_index: int

    # returns the change in value of the face card as a result of this action
    def change(self, state: GameState) -> int:
        return self.chosen_card.value - state.piles[self.chosen_pile_index].face_card.value

    def change_normalized(self, state: GameState) -> int:
        if state.piles[self.chosen_pile_index].descending:
            return -1 * self.change(state)
        else:
            return self.change(state)


@dataclass(frozen=True)
class PlayerTurn:
    actions: FrozenList[PlayerAction]


@dataclass(frozen=True)
class GameState:
    piles: FrozenList[CardPile]
    hand: FrozenList[Card]
    deck: FrozenList[Card]

    @cached_property
    def all_valid_actions(self) -> FrozenList[PlayerAction]:
        result: FrozenList[PlayerAction] = FrozenList([])
        for card in self.hand:
            for pile_index, pile in enumerate(self.piles):
                if card in pile.valid_cards(self.hand):
                    result.append(PlayerAction(card, pile_index))

        result.freeze()
        return result

    @cached_property
    def all_valid_turns(self) -> FrozenList[PlayerTurn]:
        return enumerate_valid_turns(self)

    @cached_property
    def has_one_valid_action(self) -> bool:
        return len(self.all_valid_actions) > 0

    @cached_property
    def has_one_valid_turn(self) -> bool:
        # can't have a valid turn if there are no valid actions
        if not self.has_one_valid_action:
            return False

        # for there to be a valid turn, there must be two actions that can be taken consecutively
        for action in self.all_valid_actions:
            next_state = take_action(self, action)
            if next_state.has_one_valid_action:
                return True

        return False

    @cached_property
    def has_won(self) -> bool:
        if len(self.hand) == 0 and len(self.deck) == 0:
            return True
        else:
            return False

    # list of change if placed where list index corresponds to pile index
    @cached_property
    def change_if_placed_on_pile(self) -> FrozenList[Dict[Card, int]]:
        result = FrozenList([p.change_if_placed(self.hand) for p in self.piles])
        result.freeze()
        return result

    # dict from card in hand to pile_index -> change
    @cached_property
    def change_if_placed_from_hand(self) -> Dict[Card, Dict[int, int]]:
        result: Dict[Card, Dict[int, int]] = {}
        for card in self.hand:
            result[card] = {}
            for pile_index, pile_change in enumerate(self.change_if_placed_on_pile):
                if card in self.piles[pile_index].valid_cards(self.hand):
                    result[card][pile_index] = pile_change[card]
        return result

    @cached_property
    def visual(self) -> str:
        return "\n".join([
            f"hand: | {' | '.join([str(c) for c in self.hand])} |",
            f"piles: | {' | '.join([p.visual for p in self.piles])} |",
            f"deck: {' -> '.join([str(c) for c in self.deck[::-1][:8]])}"
        ])

    def is_valid_action(self, action: PlayerAction) -> bool:
        return action.chosen_card in self.hand and self.piles[action.chosen_pile_index].placement_is_valid(action.chosen_card)


@dataclass(frozen=True)
class AggregateStats:
    end_states: FrozenList[GameState]

    @cached_property
    def total_games(self) -> int:
        return len(self.end_states)

    @cached_property
    def total_wins(self) -> int:
        return len([x for x in filter(lambda s: s.has_won, self.end_states)])

    @cached_property
    def total_losses(self) -> int:
        return self.total_games - self.total_wins

    @cached_property
    def win_ratio(self) -> float:
        return float(self.total_wins) / float(self.total_games)

    @cached_property
    def visual(self) -> str:
        return "\n".join([
            f"total games: {self.total_games}",
            f"wins: {self.total_wins}",
            f"losses: {self.total_losses}",
            f"win ratio: {self.win_ratio}",
            ])


def initial_deck(seed: Optional[int] = None) -> FrozenList[Card]:
    if seed is None:
        seed = random.randint(0, sys.maxsize)
    random.seed(seed)
    # tuple[random_index, card_value]
    ordered_tuples: List[Tuple[int, int]] = [(random.randint(0, sys.maxsize), n) for n in range(2, 100)]
    ordered_tuples.sort()
    deck = FrozenList([Card(t[1]) for t in ordered_tuples])
    deck.freeze()
    return deck


def initial_piles() -> FrozenList[CardPile]:
    piles: FrozenList[CardPile] = FrozenList([])
    for i in range(2):
        cards = FrozenList([Card(1)])
        cards.freeze()
        piles.append(CardPile(cards=cards, ascending=True))

    for i in range(2):
        cards = FrozenList([Card(100)])
        cards.freeze()
        piles.append(CardPile(cards=cards, ascending=False))

    piles.freeze()

    return piles


def initial_state(seed: Optional[int] = None) -> GameState:
    deck = initial_deck(seed)
    piles = initial_piles()
    hand: FrozenList[Card] = FrozenList([])
    hand.freeze()
    state = GameState(piles=piles, hand=hand, deck=deck)

    return draw_cards(state)


def draw_cards(state: GameState) -> GameState:
    while len(state.hand) < 8 and len(state.deck) > 0:
        state = draw_card(state)

    return state


def draw_card(state: GameState) -> GameState:
    # copy mutable data to prevent modifying the original input
    deck = FrozenList([x for x in state.deck])
    hand = [x for x in state.hand]

    # draw card and add to hand
    drawn_card = deck.pop()
    hand.append(drawn_card)
    hand.sort()
    sorted_hand = FrozenList(hand)

    deck.freeze()
    sorted_hand.freeze()

    # create new immutable data for return
    return GameState(piles=state.piles, hand=sorted_hand, deck=deck)


def take_turn(state: GameState, turn: PlayerTurn) -> GameState:
    # place cards from hand
    for action in turn.actions:
        state = take_action(state, action)

    # draw new cards
    state = draw_cards(state)

    return state


def take_action(state: GameState, action: PlayerAction) -> GameState:
    # check if action is valid
    if not state.is_valid_action(action):
        raise Exception(f"player cheated, action {action} is not valid at state {state}")

    # copy mutable variables to prevent mutation of previous state, then modify
    hand = FrozenList([x for x in state.hand])
    hand.remove(action.chosen_card)

    piles = FrozenList([x for x in state.piles])
    pile = state.piles[action.chosen_pile_index]
    cards = FrozenList([x for x in pile.cards])
    cards.append(action.chosen_card)
    piles[action.chosen_pile_index] = CardPile(cards=cards, ascending=pile.ascending)

    cards.freeze()
    piles.freeze()
    hand.freeze()

    return GameState(piles=piles, hand=hand, deck=state.deck)


def enumerate_valid_turns(state: GameState) -> FrozenList[PlayerTurn]:
    result: FrozenList[PlayerTurn] = FrozenList([])

    for action in state.all_valid_actions:
        for turn in enumerate_valid_turns_recursive([action], [take_action(state, action)]):
            result.append(turn)

    result.freeze()
    return result


def enumerate_valid_turns_recursive(action_stack: List[PlayerAction], state_stack: List[GameState]) -> FrozenList[PlayerTurn]:
    state = state_stack[-1]
    result: FrozenList[PlayerTurn] = FrozenList([])

    for new_action in state.all_valid_actions:
        new_action_stack = action_stack.copy()
        new_action_stack.append(new_action)
        new_state = take_action(state, new_action)
        new_state_stack = state_stack.copy()
        new_state_stack.append(new_state)

        if len(new_action_stack) >= 2:
            actions = FrozenList(new_action_stack.copy())
            actions.freeze()
            result.append(PlayerTurn(actions))

        for turn in enumerate_valid_turns_recursive(new_action_stack, new_state_stack):
            result.append(turn)

    result.freeze()
    return result


def simulate(strategy: Callable[[GameState], PlayerTurn], num_games: int = 1, print_level: PrintLevel = PrintLevel.WIN_LOSS) -> None:
    end_states: FrozenList[GameState] = FrozenList([])

    if print_level.value <= PrintLevel.EACH_TURN.value:
        print("running simulations...")

    it = range(num_games) if print_level.value >= PrintLevel.EACH_TURN.value else tqdm(range(num_games))
    for i in it:
        state = initial_state()

        while state.has_one_valid_turn:
            turn = strategy(state)
            state = take_turn(state, turn)

            if print_level.value >= PrintLevel.EACH_TURN.value:
                print('-' * 80)
                print('player takes their turn')
                for action in turn.actions:
                    print(f"player places {action.chosen_card} on pile {action.chosen_pile_index}")
                print("player ends their turn")
                print(state.visual)
                print('-' * 80)

        # end of game
        if print_level.value >= PrintLevel.WIN_LOSS.value:
            print('=' * 80)
            if state.has_won:
                print(f"won game #{i}")
            else:
                print(f"lost game #{i}")
            print('=' * 80)

        end_states.append(state)

    end_states.freeze()
    if print_level.value >= PrintLevel.AGGREGATE.value:
        print("#" * 80)
        print(AggregateStats(end_states=end_states).visual)
