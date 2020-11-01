from dataclasses import dataclass
from typing import Dict, List

from game_state import CardPile, PlayerAction, PlayerTurn, VisibleGameState


@dataclass(frozen=True)
class PlayerActionInfo:
    action: PlayerAction
    change: int
    change_normalized: int


@dataclass(frozen=True)
class PileInformation:
    pile: CardPile
    valid_cards: List[int]

    # returns a map of card in hand to the change in value if that card is placed on the pile
    @property
    def change_if_placed(self) -> Dict[int, int]:
        result: Dict[int, int] = {}
        for card in self.valid_cards:
            result[card] = result - self.pile.face_card
        return result


@dataclass(frozen=True)
class StateInformation:
    piles: List[PileInformation]
    hand: List[int]

    # list of change if placed where list index corresponds to pile index
    @property
    def change_if_placed_on_pile(self) -> List[Dict[int, int]]:
        return [p.change_if_placed for p in self.piles]

    # dict from card in hand to list of change if placed where list index corresponds to pile index
    @property
    def change_if_placed_from_hand(self) -> Dict[int, List[int]]:
        result: Dict[int, List[int]] = {}
        for card in self.hand:
            result[card] = []
            for pile_change in self.change_if_placed_on_pile:
                result[card].append(pile_change[card])
        return result

    # Dict from card in hand to greediest play for that card
    @property
    def greedy_plays(self) -> Dict[int, PlayerActionInfo]:
        plays = {}
        for card, l in self.change_if_placed_from_hand.items():
            best_change_normalized = l[0]
            best_change = l[0]
            best_index = 0
            for pile_index, change in enumerate(l):
                change_normalized = change
                if self.piles[pile_index].pile.descending:
                    change_normalized = -1 * change
                if change_normalized < best_change_normalized:
                    best_change_normalized = change_normalized
                    best_change = change
                    best_index = pile_index
            plays[card] = PlayerActionInfo(PlayerAction(card, best_index), best_change, best_change_normalized)
        return plays

    @property
    def greediest_action(self) -> PlayerAction:
        best_change_normalized = self.greedy_plays[self.hand[0]].change_normalized
        best_card = self.hand[0]
        for card, play_info in self.greedy_plays.items():
            if play_info.change_normalized < best_change_normalized:
                best_change_normalized = play_info.change_normalized
                best_card = card

        return self.greedy_plays[best_card]

    # returns the two greediest plays in your hand
    @property
    def greediest_turn(self) -> PlayerTurn:
        greediest_first_play = self.greediest_action
        new_state = self.predict_action(greediest_first_play)
        greediest_second_play = new_state.greediest_action
        return PlayerTurn([greediest_first_play, greediest_second_play])

    def predict_action(self, action: PlayerAction) -> VisibleGameState:
        piles = self.piles.copy()
        cards = self.piles[action.chosen_pile_index].pile.cards.copy()
        cards.append(action.chosen_card)
        piles[action.chosen_pile_index] = CardPile(cards, self.piles[action.chosen_pile_index].ascending)

        hand = self.hand.copy()
        hand.remove(action.chosen_card)

        return VisibleGameState(piles, hand)


def valid_cards(pile: CardPile, hand: List[int]) -> List[int]:
    return [x for x in filter(lambda c: pile.placement_is_valid(c), hand)]


def pile_information(pile: CardPile, hand: List[int]) -> PileInformation:
    return PileInformation(pile, valid_cards(pile, hand))


def state_information(state: VisibleGameState) -> StateInformation:
    pile_infos = []
    for pile in state.piles:
        pile_infos.append(pile_information(pile, state.hand))

    return StateInformation(piles=pile_infos, hand=state.hand)
