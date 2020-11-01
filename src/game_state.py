from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
import random
from enum import Enum
import sys
from functools import cached_property


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
    cards: List[Card] = field(default_factory=list)
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
    def change_if_placed(self, hand: List[Card]) -> Dict[Card, int]:
        result: Dict[Card, int] = {}
        for card in self.valid_cards(hand):
            result[card] = card.value - self.face_card.value
        return result

    def valid_cards(self, hand: List[Card]) -> List[Card]:
        return [x for x in filter(lambda c: self.placement_is_valid(c), hand)]

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
    actions: List[PlayerAction] = field(default_factory=list)


@dataclass(frozen=True)
class GameState:
    piles: List[CardPile] = field(default_factory=list)
    hand: List[Card] = field(default_factory=list)
    deck: List[Card] = field(default_factory=list)

    @cached_property
    def has_valid_moves(self) -> bool:
        placement_validities = []
        for card in self.hand:
            for pile in self.piles:
                placement_validities.append(pile.placement_is_valid(card))

        return True in placement_validities

    @cached_property
    def has_won(self) -> bool:
        if len(self.hand) == 0 and len(self.deck) == 0:
            return True
        else:
            return False

    @cached_property
    def visible_state(self) -> GameState:
        # copies mutable objects to prevent cheating player strategies
        return GameState(piles=self.piles.copy(), hand=self.hand.copy())

        # list of change if placed where list index corresponds to pile index
    @cached_property
    def change_if_placed_on_pile(self) -> List[Dict[Card, int]]:
        return [p.change_if_placed(self.hand) for p in self.piles]

    # dict from card in hand to list of change if placed where list index corresponds to pile index
    @cached_property
    def change_if_placed_from_hand(self) -> Dict[Card, List[int]]:
        result: Dict[Card, List[int]] = {}
        for card in self.hand:
            result[card] = []
            for pile_index, pile_change in enumerate(self.change_if_placed_on_pile):
                if card in self.piles[pile_index].valid_cards(self.hand):
                    result[card].append(pile_change[card])
        return result

    @cached_property
    def any_card_with_valid_plays(self) -> Optional[Card]:
        for card in self.hand:
            if card.has_valid_play(self):
                return card

        return None

    # Dict from card in hand to greediest play for that card
    @cached_property
    def greedy_plays(self) -> Dict[Card, PlayerAction]:
        print("evaluating greedy plays")
        plays = {}
        for card, pile_changes in self.change_if_placed_from_hand.items():
            if pile_changes == []:
                continue
            best_change_normalized = pile_changes[0]
            best_index = 0
            for pile_index, change in enumerate(pile_changes):
                print(f"evaluating card {card} for pile {pile_index}")
                if card not in self.piles[pile_index].valid_cards(self.hand):  # do not check change for invalid pile placements
                    print("not valid")
                    continue
                print("valid")
                change_normalized = change
                if self.piles[pile_index].descending:
                    change_normalized = -1 * change
                if change_normalized < best_change_normalized:
                    best_change_normalized = change_normalized
                    best_index = pile_index
            plays[card] = PlayerAction(card, best_index)
        return plays

    @cached_property
    def greediest_action(self) -> PlayerAction:
        initial_card = self.any_card_with_valid_plays
        if initial_card is None:
            raise Exception("no valid actions for greediest action")
        best_change_normalized = self.greedy_plays[initial_card].change_normalized(self)
        best_card = initial_card
        print("-" * 80 + "\ngreedy plays:")
        print(self.greedy_plays)
        for card, play in self.greedy_plays.items():
            if play.change_normalized(self) < best_change_normalized:
                best_change_normalized = play.change_normalized(self)
                best_card = card

        return self.greedy_plays[best_card]

    # returns the two greediest plays in your hand
    @cached_property
    def greediest_turn(self) -> PlayerTurn:
        print(f"old state:\n{self}")
        greediest_first_play = self.greediest_action
        print(f"1st action: {greediest_first_play}")
        new_state = take_action(self, greediest_first_play)
        print(f"new state:\n{new_state}")
        greediest_second_play = new_state.greediest_action
        print(f"2nd action: {greediest_second_play}")
        return PlayerTurn([greediest_first_play, greediest_second_play])

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
    end_states: List[GameState] = field(default_factory=list)

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

    def __str__(self) -> str:
        return "\n".join([
            f"total games: {self.total_games}",
            f"wins: {self.total_wins}",
            f"losses: {self.total_losses}",
            f"win ratio: {self.win_ratio}",
            ])


def initial_deck(seed: Optional[int] = None) -> List[Card]:
    if seed is None:
        seed = random.randint(0, sys.maxsize)
    random.seed(seed)
    # tuple[random_index, card_value]
    ordered_tuples: List[Tuple[int, int]] = [(random.randint(0, sys.maxsize), n) for n in range(2, 100)]
    ordered_tuples.sort()
    return [Card(t[1]) for t in ordered_tuples]


def initial_piles() -> List[CardPile]:
    piles = []
    for i in range(2):
        piles.append(CardPile(cards=[Card(1)], ascending=True))

    for i in range(2):
        piles.append(CardPile(cards=[Card(100)], ascending=False))

    return piles


def initial_state(seed: Optional[int] = None) -> GameState:
    deck = initial_deck(seed)
    piles = initial_piles()
    state = GameState(piles=piles, hand=[], deck=deck)

    return draw_cards(state)


def draw_cards(state: GameState) -> GameState:
    while len(state.hand) < 8 and len(state.deck) > 0:
        state = draw_card(state)

    return state


def draw_card(state: GameState) -> GameState:
    # copy mutable data to prevent modifying the original input
    deck = state.deck.copy()
    hand = state.hand.copy()

    # draw card and add to hand
    drawn_card = deck.pop()
    hand.append(drawn_card)
    hand.sort()

    # create new immutable data for return
    return GameState(piles=state.piles, hand=hand, deck=deck)


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
    hand = state.hand.copy()
    hand.remove(action.chosen_card)

    piles = state.piles.copy()
    pile = state.piles[action.chosen_pile_index]
    cards = pile.cards.copy()
    cards.append(action.chosen_card)
    piles[action.chosen_pile_index] = CardPile(cards=cards, ascending=pile.ascending)

    return GameState(piles=piles, hand=hand, deck=state.deck)


def simulate(strategy: Callable[[GameState], PlayerTurn], num_games: int = 1, print_level: PrintLevel = PrintLevel.WIN_LOSS) -> None:
    end_states: List[GameState] = []

    for i in range(num_games):
        state = initial_state()

        while state.has_valid_moves:
            turn = strategy(state.visible_state)
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
            if state.has_won:
                print(f"won game #{i}")
            else:
                print(f"lost game #{i}")

        end_states.append(state)

    if print_level.value >= PrintLevel.AGGREGATE.value:
        print(AggregateStats(end_states=end_states).__repr__())
