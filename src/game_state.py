from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple
import random
from enum import Enum
import sys


class PrintLevel(Enum):
    NOTHING = 0
    AGGREGATE = 1
    WIN_LOSS = 2
    EACH_TURN = 3


@dataclass(frozen=True)
class CardPile:
    cards: List[int] = field(default_factory=list)
    ascending: bool = True

    @property
    def face_card(self) -> int:
        return self.cards[-1]

    @property
    def descending(self) -> bool:
        return not self.ascending

    def placement_is_valid(self, card: int) -> bool:
        if card > self.face_card and self.ascending:
            return True
        elif card < self.face_card and self.descending:
            return True
        elif card == self.face_card + 10 or card == self.face_card - 10:
            return True
        else:
            return False


@dataclass(frozen=True)
class VisibleGameState:
    piles: List[CardPile] = field(default_factory=list)
    hand: List[int] = field(default_factory=list)


@dataclass(frozen=True)
class PlayerAction:
    chosen_card: int
    chosen_pile_index: int


@dataclass(frozen=True)
class PlayerTurn:
    actions: List[PlayerAction] = field(default_factory=list)


@dataclass(frozen=True)
class GameState:
    piles: List[CardPile] = field(default_factory=list)
    hand: List[int] = field(default_factory=list)
    deck: List[int] = field(default_factory=list)

    @property
    def has_valid_moves(self) -> bool:
        placement_validities = []
        for card in self.hand:
            for pile in self.piles:
                placement_validities.append(pile.placement_is_valid(card))

        return True in placement_validities

    @property
    def has_won(self) -> bool:
        if len(self.hand) == 0 and len(self.deck) == 0:
            return True
        else:
            return False

    @property
    def visible_state(self) -> VisibleGameState:
        # copies mutable objects to prevent cheating player strategies
        return VisibleGameState(piles=self.piles.copy(), hand=self.hand.copy())

    def is_valid_action(self, action: PlayerAction) -> bool:
        return action.chosen_card in self.hand and self.piles[action.chosen_pile_index].placement_is_valid(action.chosen_card)


@dataclass(frozen=True)
class AggregateStats:
    end_states: List[GameState] = field(default_factory=list)

    @property
    def total_games(self) -> int:
        return len(self.end_states)

    @property
    def total_wins(self) -> int:
        return len([x for x in filter(lambda s: s.has_won, self.end_states)])

    @property
    def total_losses(self) -> int:
        return self.total_games - self.total_wins

    @property
    def win_ratio(self) -> float:
        return float(self.total_wins) / float(self.total_games)

    def __str__(self) -> str:
        return "\n".join([
            f"total games: {self.total_games}",
            f"wins: {self.total_wins}",
            f"losses: {self.total_losses}",
            f"win ratio: {self.win_ratio}",
            ])


def initial_deck(seed: Optional[int] = None) -> List[int]:
    if seed is None:
        seed = random.randint(0, sys.maxsize)
    random.seed(seed)
    # tuple[random_index, card_value]
    ordered_tuples: List[Tuple[int, int]] = [(random.randint(0, sys.maxsize), n) for n in range(2, 100)]
    ordered_tuples.sort()
    return [t[1] for t in ordered_tuples]


def initial_piles() -> List[CardPile]:
    piles = []
    for i in range(2):
        piles.append(CardPile(cards=[1], ascending=True))

    for i in range(2):
        piles.append(CardPile(cards=[100], ascending=False))

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


def simulate(strategy: Callable[[VisibleGameState], PlayerTurn], num_games: int = 1, print_level: PrintLevel = PrintLevel.WIN_LOSS) -> None:
    end_states: List[GameState] = []

    for i in range(num_games):
        state = initial_state()

        while state.has_valid_moves:
            turn = strategy(state.visible_state)
            state = take_turn(state, turn)

            if print_level.value >= PrintLevel.EACH_TURN:
                for action in turn.actions:
                    print(f"player places {action.chosen_card} on pile {action.chosen_pile_index}")
                print("player ends their turn")
                print(state.__repr__)

        # end of game
        if print_level.value >= PrintLevel.WIN_LOSS:
            if state.has_won:
                print(f"won game #{i}")
            else:
                print(f"lost game #{i}")

        end_states.append(state)

    if print_level.value >= PrintLevel.AGGREGATE:
        print(AggregateStats(end_states=end_states).__repr__)
