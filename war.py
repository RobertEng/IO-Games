from deck import Deck

class War:
    def __init__(self, num_players=2):
        self.players = {}
        self.max_players = num_players
        self.num_players = 0
        self.started = False  # has the game started
        self.drawn_cards = {}
        self.pot_cards = []  # to store cards during a war
        self.war_in_progress = False
        self.reinforcement = False
        self.battling_players = set()  # players at war
        self.continue_in_progress = False
        self.clicked_continue = set()

        self.current_state = 'unstarted'
        self.click_in_progress = False


    def setup_game(self):
        if self.num_players != self.max_players:
            return self.get_game_state()

        self.started = True
        deck = Deck()

        # Throw away every player's deck. Needed if restarting the game.
        for pid, player in self.players.iteritems():
            player.deck.discard_deck()

        # Deal the cards to the players
        cur_player = 0
        player_list = [player for pid, player in self.players.iteritems()]
        while True:
            card = deck.draw_card()
            if card is None:
                break
            player_list[cur_player].deck.add_card_to_bottom(card)
            cur_player += 1
            cur_player %= self.num_players

        # keep track of players who have drawn a card already in a round
        self.drawn_cards = {}
        self.battling_players = set(self.players.keys())
        return self.get_game_state()

    def add_player(self, player_id):
        if self.num_players >= self.max_players:
            return False
        self.players[player_id] = Player(player_id)
        self.num_players += 1
        return True

    def remove_player(self, player_id):
        del self.players[player_id]
        self.num_players -= 1

    def play_round(self, sid, message):
        # If player sid hasn't drawn a card, then draw one
        if sid not in self.drawn_cards.keys():
            self.drawn_cards[sid] = self.players[sid].deck.draw_card()
            if self.drawn_cards[sid] is None:
                print "RAN OUT OF CARDS!"
        
        # All battling players must draw a card.
        if any(pid not in self.drawn_cards for pid in self.battling_players):
            return self.get_game_state()

        # Reinforcement cards aka the ones you throw away in a war
        if self.war_in_progress and not self.reinforcement:
            self.reinforcement = True
            # dump reinforcement cards into the pot
            for pid, card in self.drawn_cards.iteritems():
                self.pot_cards.append(card)
            self.drawn_cards = {}
            return self.get_game_state()

        # Return this game state before the war. Let the war play out on client
        # side as well as server side.
        states = [self.get_game_state()]

        # Play out battle and find a winner
        battle_winners = []
        winner_cards = []
        for pid in self.battling_players:
            if not battle_winners:
                battle_winners.append(pid)
                winner_cards.append(self.drawn_cards[pid])
            elif winner_cards[0] < self.drawn_cards[pid]:
                battle_winners = [pid]
                winner_cards = [self.drawn_cards[pid]]
            elif winner_cards[0] == self.drawn_cards[pid]:
                # possible war
                battle_winners.append(pid)
                winner_cards.append(self.drawn_cards[pid])

        assert (len(battle_winners) > 0), "no winner in battle?"

        # If there's a winner, give all cards to them
        if len(battle_winners) == 1:
            self.war_in_progress = False
            self.reinforcement = False
            for pid, card in self.drawn_cards.iteritems():
                self.players[battle_winners[0]].deck.add_card_to_bottom(card)
            for card in self.pot_cards:
                self.players[battle_winners[0]].deck.add_card_to_bottom(card)

            # Reset for next battle
            self.battling_players = set(self.players.keys())
            self.pot_cards = []
        else: # Otherwise, there is a war
            self.war_in_progress = True
            self.reinforcement = False
            self.battling_players = set(battle_winners)
            
            # Put all drawn cards into the pot
            for pid, card in self.drawn_cards.iteritems():
                self.pot_cards.append(card)

        self.drawn_cards = {}
        states.append(self.get_game_state())
        return states

    def continue_cleanup(self, sid):
        '''Called after a battle has been played, and you're cleaning up the
        card for the next battle'''
        self.clicked_continue.add(sid)
        self.continue_in_progress = True

        if any(pid not in self.clicked_continue for pid in self.battling_players):
            return self.get_game_state()
        
        # if everyone who battled has clicked continue, then continue
        self.continue_in_progress = False
        self.clicked_continue = set()

    def handle_message(self, sid, message):
        '''routes messages from the server to the correct game function'''
        print [pid for pid, player in self.players.iteritems()]
        data = message['data']
        if 'action' in data:
            if data['action'] == 'start_game':
                return self.setup_game()
            elif data['action'] == 'draw_card':
                return self.play_round(sid, message)
            elif data['action'] == 'continue':
                return self.continue_cleanup(sid)

    def get_game_state(self):
        state = {}
        state['started'] = self.started
        state['pot_size'] = len(self.pot_cards)
        state['war_in_progress'] = self.war_in_progress
        state['continue_in_progress'] = self.war_in_progress
        state['players'] = {}

        for pid, player in self.players.iteritems():
            state['players'][pid] = {}
            state['players'][pid]['deck_size'] = len(player.deck)
            state['players'][pid]['drawn_card'] = str(self.drawn_cards[pid]) if pid in self.drawn_cards else None
        return state


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.deck = Deck(empty=True)