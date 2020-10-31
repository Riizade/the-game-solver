from dataclasses import dataclass, field
from typing import List, Optional
import random
from enum import Enum

class PrintLevel(Enum):
    NOTHING = 0
    AGGREGATE = 1
    WIN_LOSS = 2
    EACH_TURN = 3

def initialize_deck(seed: Optional[int] = None):
    if seed is None:
        seed = random.randint(0, 1e12)

def take_action(state: GameState, action: PlayerAction):
    pass

def simulate(num_games: int = 1, print_level: PrintLevel = PrintLevel.WIN_LOSS, strategy: Callable[[VisibleGameState], PlayerAction]) -> None:
    pass

@dataclass(frozen=True)
class CardPile:
    cards: List[int] = field(default_factory=list)
    direction_ascending: bool = True
    face_card: int = 1

@dataclass(frozen=True)
class VisibleGameState:
    piles: List[CardPile] = field(default_factory=list)
    hand: List[int]

@dataclass(frozen=True)
class PlayerAction:
    chosen_card: int
    chosen_pile_index: int

@dataclass(frozen=True)
class GameState:
    piles: List[CardPile] = field(default_factory=list)
    hand: List[int]
    deck: List[int]