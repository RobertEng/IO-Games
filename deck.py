import random

class Card:
    '''
    suits: H, S, C, D
    A => 1
    2 => 2
    ...
    J => 11
    Q => 12
    K => 13
    '''
    def __init__(self, suit, rank):
        assert (isinstance(rank, int)), "rank must be an integer"
        assert (0 < int(rank) <= 13), "rank must be an integer between 1 and 13"
        assert (suit in ['H', 'S', 'C', 'D']), "suit must be H, S, C, or D"
        self.suit = suit
        self.rank = rank

    def __str__(self):
        if self.rank == 1:
            val = 'A'
        elif self.rank == 11:
            val = 'J'
        elif self.rank == 12:
            val = 'Q'
        elif self.rank == 13:
            val = 'K'
        else:
            val = str(self.rank)

        return self.suit + ' ' + val

    def __gt__(self, card2):
        return self.rank > card2.rank

    def __eq__(self, card2):
        return self.rank == card2.rank

    def __lt__(self, card2):
        return self.rank < card2.rank

    def __ne__(self, card2):
        return not self.__eq__(card2)

    def __ge__(self, card2):
        return self.rank >= card2.rank

    def __le__(self, card2):
        return self.rank <= card2.rank


class Deck:
    '''
    front of self.deck is the top of the deck
    end of self.deck is the bottom of the deck
    '''
    def __init__(self, empty=False, shuffle=True):
        self.deck = []
        if empty:
            return

        for suit in ['H', 'S', 'C', 'D']:
            for rank in range(1, 14):
                self.deck.append(Card(suit, rank))

        if shuffle:
            random.shuffle(self.deck)

    def draw_card(self):
        if len(self.deck) == 0:
            return None
        return self.deck.pop(0)

    def add_card(self, pos, card):
        self.deck.insert(pos, card)

    def add_cards_to_bottom(self, cards):
        for c in cards:
            self.add_card_to_bottom(c)

    def add_card_to_bottom(self, card):
        self.add_card(len(self.deck), card)

    def add_card_to_top(self, card):
        self.add_card(0, card)

    def shuffle(self):
        random.shuffle(self.deck)

    def discard_deck(self):
        self.deck = []

    def is_empty(self):
        return len(self.deck) == 0

    def __len__(self):
        return len(self.deck)
