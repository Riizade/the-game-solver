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
    direction_ascending: bool = True
    face_card: int = 1


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


def initialize_deck(seed: Optional[int] = None) -> List[int]:
    if seed is None:
        seed = random.randint(0, sys.maxsize)
    random.seed(seed)
    # tuple[random_index, card_value]
    ordered_tuples: List[Tuple[int, int]] = [(random.randint(0, sys.maxsize), n) for n in range(2, 100)]
    ordered_tuples.sort()
    return [t[1] for t in ordered_tuples]


def draw_card(state: GameState) -> GameState:
    # copy mutable data to prevent modifying the original input
    deck = state.deck.copy()
    hand = state.hand.copy()

    # draw card and add to hand
    drawn_card = deck.pop()
    hand.append(drawn_card)

    # create new immutable data for return
    return GameState(piles=state.piles, hand=hand, deck=deck)


def take_turn(state: GameState, turn: PlayerTurn) -> GameState:
    # place cards from hand
    for action in turn.actions:
        state = take_action(state, action)

    # draw new cards
    while len(state.hand) < 8:
        state = draw_card(state)

    return state


def take_action(state: GameState, action: PlayerAction) -> GameState:
    pass


def simulate(strategy: Callable[[VisibleGameState], PlayerTurn], num_games: int = 1, print_level: PrintLevel = PrintLevel.WIN_LOSS) -> None:
    pass
