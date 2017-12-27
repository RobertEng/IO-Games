from deck import Deck
import sys
import copy

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.deck = Deck(empty=True)

class StateMachine:
    def __init__(self, initialState):
        self.currentState = initialState
        # self.currentState.run()
    # Template method:
    def runAll(self, inputs):
        for i in inputs:
            print(i)
            self.currentState = self.currentState.next(i)
            self.currentState.run()

class State:
    def start_run(self):
        assert 0, "start_run not implemented"
    def end_run(self):
        assert 0, "end_run not implemented"
    def next(self, input_, data, war_state):
        # actions to be run by default on certain inputs
        if input_ == WarAction.remove_player:
            del war_state['players'][data['pid']]
            return War.lobby
        sys.exit("Unknown input {} action for this state {}".format(input_, self.__class__.__name__))
    def __repr__(self):
        return self.__class__.__name__


class WarAction:
    def __init__(self, action):
        self.action = action
    def __str__(self): return self.action
    def __cmp__(self, other):
        return cmp(self.action, other.action)
    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self):
        return hash(self.action)

# Static fields; an enumeration of instances:
WarAction.add_player = WarAction("add_player")
WarAction.start_game = WarAction("start_game")
WarAction.draw_card = WarAction("draw_card")
WarAction.continue_game = WarAction("continue_game")
WarAction.reinforce_battle = WarAction("reinforce_battle")
WarAction.remove_player = WarAction("remove_player")
WarAction.restart = WarAction("restart")

WarAction.str2action = {
    "add_player": WarAction.add_player,
    "start_game": WarAction.start_game,
    "draw_card": WarAction.draw_card,
    "continue_game": WarAction.continue_game,
    "reinforce_battle": WarAction.reinforce_battle,
    "remove_player": WarAction.remove_player,
    "restart": WarAction.restart
}

class War(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, War.lobby)
        self.war_state = {'players': {}, 'pot': []}

    # Template method:
    def run(self, input_, data):
        print(input_)
        print self.war_state
        input_ = WarAction.str2action[input_]

        self.currentState = self.currentState.next(input_, data, self.war_state)
        self.war_state['state'] = self.currentState.__class__.__name__
        return self.serialize_war_state(self.war_state)

    def serialize_war_state(self, war_state):
        '''Need to make war_state 1) serializable and 2) hide important info'''
        war_state = copy.deepcopy(war_state)
        for pid in war_state['players']:
            war_state['players'][pid] = len(war_state['players'][pid].deck)
        if 'drawn_cards' in war_state:
            for pid in war_state['drawn_cards']:
                war_state['drawn_cards'][pid] = str(war_state['drawn_cards'][pid])
        for i in range(len(war_state['pot'])):
            war_state['pot'][i] = str(war_state['pot'][i])
        if 'continue_game' in war_state:
            war_state['continue_game'] = list(war_state['continue_game'])
        return war_state

class Lobby(State):
    def __init__(self):
        # self.action_in_progress = False
        self.req_players = 2

    def next(self, input_, data, war_state):
        num_players = len(war_state['players'])
        if input_ == WarAction.add_player and num_players >= self.req_players:
            return War.lobby
        if input_ == WarAction.add_player:
            if 'pid' in data and data['pid'] not in war_state['players']:
                war_state['players'][data['pid']] = Player(data['pid'])
            return War.lobby
        if input_ == WarAction.start_game and num_players < self.req_players:
            return War.lobby
        if input_ == WarAction.start_game:
            deck = Deck()
            # Throw away every player's deck. Needed if restarting the game.
            for pid, player in war_state['players'].iteritems():
                player.deck.discard_deck()

            # Deal the cards to the players
            cur_player = 0
            player_list = [player for pid, player in war_state['players'].iteritems()]
            while True:
                card = deck.draw_card()
                if card is None:
                    break
                player_list[cur_player].deck.add_card_to_bottom(card)
                cur_player += 1
                cur_player %= num_players

            war_state['drawn_cards'] = {}
            war_state['continue_game'] = set()
            war_state['pot'] = []

            return War.preparation
        
        
        return State.next(self, input_, data, war_state)

class Preparation(State):
    def next(self, input_, data, war_state):
        if input_ == WarAction.draw_card:
            if data['pid'] in war_state['drawn_cards']:
                return War.preparation

            pid = data['pid']
            war_state['drawn_cards'][pid] = war_state['players'][pid].deck.draw_card()
            if war_state['drawn_cards'][pid] is None:
                return War.conclusion

            if len(war_state['drawn_cards']) == 2:
                return War.afterbattle
            else:
                return War.preparation
        if input_ == WarAction.add_player:
            return War.preparation
        return State.next(self, input_, data, war_state)

class Afterbattle(State):
    def next(self, input_, data, war_state):
        if input_ == WarAction.continue_game:
            war_state['continue_game'].add(data['pid'])

            if len(war_state['continue_game']) < 2:
                return War.afterbattle
            else:
                war_state['continue_game'].clear()

                # Play out battle and find a winner
                battle_winner = None
                winner_card = None
                is_war = False
                for pid in war_state['drawn_cards']:
                    if battle_winner is None:
                        battle_winner = pid
                        winner_card = war_state['drawn_cards'][pid]
                        continue

                    if winner_card < war_state['drawn_cards'][pid]:
                        battle_winner = pid
                    if winner_card == war_state['drawn_cards'][pid]:
                        is_war = True

                drawn_cards = [card for pid, card in war_state['drawn_cards'].iteritems()]
                war_state['drawn_cards'] = {}

                if is_war:
                    # A war! Move all cards in battle to the pot.
                    war_state['pot'].extend(drawn_cards)
                    return War.reinforcements
                else:
                    # battle_winner has won the battle. Give them all the cards
                    # from the pot and currently in battle.
                    war_state['players'][battle_winner].deck.add_cards_to_bottom(war_state['pot'])
                    war_state['players'][battle_winner].deck.add_cards_to_bottom(drawn_cards)
                    war_state['pot'] = []
                    return War.preparation
        return State.next(self, input_, data, war_state)

class Reinforcements(State):
    def next(self, input_, data, war_state):
        if input_ == WarAction.reinforce_battle:
            pid = data['pid']
            if pid in war_state['drawn_cards']:
                return War.reinforcements

            war_state['drawn_cards'][pid] = war_state['players'][pid].deck.draw_card()
            if war_state['drawn_cards'][pid] is None:
                return War.conclusion

            if len(war_state['drawn_cards']) == 2:
                # Both players reinforced. So add both reinforcement cards to
                # the pot.
                drawn_cards = [card for pid, card in war_state['drawn_cards'].iteritems()]
                war_state['pot'].extend(drawn_cards)
                
                war_state['drawn_cards'] = {}
                return War.preparation
            else:
                return War.reinforcements
        return State.next(self, input_, data, war_state)

class Conclusion(State):
    def next(self, input_, data, war_state):
        if input_ == WarAction.restart:
            return War.lobby
        return State.next(self, input_, data, war_state)




# Static variable initialization:
War.lobby = Lobby()
War.preparation = Preparation()
War.afterbattle = Afterbattle()
War.reinforcements = Reinforcements()
War.conclusion = Conclusion()


# war = War()
# war.run(WarAction.add_player, {'pid': '12345'})
# war.run(WarAction.start_game, {})
# war.run(WarAction.add_player, {'pid': '67890'})
# war.run(WarAction.start_game, {})
# war.run(WarAction.draw_card, {'pid': '12345'})
# war.run(WarAction.draw_card, {'pid': '67890'})
# war.run(WarAction.continue_game, {'pid': '67890'})
# war.run(WarAction.continue_game, {'pid': '12345'})
# war.run(WarAction.reinforce_battle, {'pid': '67890'})
# war.run(WarAction.reinforce_battle, {'pid': '12345'})



