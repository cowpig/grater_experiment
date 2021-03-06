from enum import Enum
from cards import Deck, Card
from utils import rotate_iter
import json

class Events(Enum):
	NONE, DEAL, POST, POST_DEAD, ANTE, BET, RAISE_TO, \
	CALL, CHECK, FOLD, BUY, SIT_IN, SIT_OUT, DEAL, WIN, LOSE, ADD_CHIPS, \
	OWE, SET_GAME_STATE, NEW_HAND, NEW_STREET, LOG = range(22)

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name

# deals with keeping track of players & missing blinds
class Table(object):	
	def __init__(self, name, sb=1, bb=2, ante=0, max_players=6, players=None, 
											min_buyin=None, max_buyin=None):
		self.id = name
		self.name = name

		self.sb = sb
		self.bb = bb
		self.ante = ante

		self.min_buyin = min_buyin or 50*bb
		self.max_buyin = max_buyin or 200*bb

		self.players = [None] * max_players
		if players:
			for i, p in enumerate(players):
				self.players[i] = p

		# http://www.learn-texas-holdem.com/questions/blind-rules-when-players-bust-out.htm
		self.owes_bb = set()
		self.owes_sb = set()

		# individual hand state
		self.deck = Deck()
		self.game_state = {
			"sb_idx": None,
			"bb_idx": None,
			"board": []
		}

		self.games = [HandHistory()]

	def get_bb_idx(self):
		return self.game_state['bb_idx']

	def get_sb_idx(self):
		return self.game_state['sb_idx']

	def get_board(self):
		return self.game_state['board']

	def get_active_players(self, rotate=0):
		return [p for p in rotate_iter(self.players, rotate) 
						if p is not None and not p.sitting_out]

	def get_players_still_in(self, rotate=0):
		return [p for p in self.get_active_players(rotate)
						if p.last_action != Events.FOLD]

	def current_pot(self):
		return sum([player.wagers for player in self.get_active_players()])

	def hand_in_progress(self):
		# TODO: there might be an edge case where this becomes incorrect?
		return len(self.deck.cards) < 52

	def to_json(self, indent=None):
		out = {
			"id": self.id,
			"sb" : self.sb,
			"bb" : self.bb,
			"ante" : self.ante,
			"players" : {i : p.summary_for_json() if p else None 
							for i, p in enumerate(self.players)}
		}

		if self.hand_in_progress():
			game_state = {k:v for k,v in self.game_state.iteritems()}
			game_state['board'] = [c.__str__() for c in self.game_state['board']]
			game_state['pot'] = self.current_pot()
			out['game_state'] = game_state

		return json.dumps(out, indent=indent)

	def sit(self, player, seat_number):
		if self.players[seat_number]:
			raise Exception("Seat already taken")
		else:
			self.players[seat_number] = player
			self.owes_bb.add(player.id)

	def stand(self, player):
		self.players[self.index(player)] = None

	def new_hand(self):
		self.log("===Starting hand {}===".format(len(self.games)))
		self.games.append(HandHistory())
		self.game_state['board'] = []
		self.deck = Deck()
		self.new_street()
		for player in self.get_active_players():
			player.new_hand()

	def new_street(self):
		for player in self.get_active_players():
			player.last_action = Events.NONE
			player.uncollected_bets = 0

	def is_player(self, x):
		return x in [p.id for p in self.players if p]

	def get_player(self, id):
		for player in self.players:
			if player.id == id:
				return player
		return None

	def deal(self, n_cards):
		self.game_state.board.extend([self.deck.deal() for _ in xrange(n_cards)])

	def handle_event(self, subj, event, obj):
		if isinstance(subj, Player):
			raise Exception("Passed Player instance into handle_event. You probably meant to pass in the ID.")
		elif isinstance(subj, Table):
			raise Exception("Passed Table instance into handle_event. You probably meant to pass in the ID.")
		
		self.log((subj, event, obj))
		if self.is_player(subj):
			player = self.get_player(subj)
			if event == Events.NEW_HAND:
				player.new_hand()
			elif event in (Events.POST, Events.POST_DEAD):
				if obj == self.sb and player.id in self.owes_sb:
					self.owes_sb.remove(player.id)
				elif obj == self.bb and player.id in self.owes_bb:
					self.owes_bb.remove(player.id)
				player.post(obj)
			elif event == Events.BET:
				player.bet(obj)
			elif event == Events.RAISE_TO:
				player.raise_to(obj)
			elif event == Events.CALL:
				player.call(obj)
			elif event == Events.FOLD:
				player.fold()
			elif event == Events.CHECK:
				player.check()
			elif event == Events.DEAL:
				player.deal([self.deck.deal() for _ in xrange(obj)])
			elif event == Events.SIT_IN:
				player.sit_out()
			elif event == Events.SIT_OUT:
				player.sit_in()
			elif event == Events.LOSE:
				player.lose(obj)
			elif event == Events.WIN:
				player.win(obj)
			elif event == Events.BUY:
				player.buy(obj)
			else:
				raise Exception("Unknown event {} for {} with {}".format(event, subj, obj))
		elif subj == self.id:
			if event == Events.OWE:
				if obj == self.bb:
					self.owes_bb.add(subj)
				elif obj == self.sb:
					self.owes_sb.add(subj)
				else:
					raise Exception("Can't owe a non-blind amt")
			elif event == Events.SET_GAME_STATE:
				key, val = obj
				if not key in self.game_state:
					raise Exception("Unknown game state parameter")
				self.game_state[key] = val
			elif event == Events.DEAL:
				self.game_state['board'].extend([self.deck.deal() for _ in xrange(obj)])
			elif event == Events.NEW_HAND:
				self.new_hand()
			elif event == Events.NEW_STREET:
				self.new_street()
			elif event == Events.LOG:
				pass
			else:
				raise Exception("Unknown event {} for {} with {}".format(event, subj, obj))

	def handle_events(self, events):
		for event in events:
			self.handle_event(*event)

	def log(self, event):
		print event
		self.games[-1].log(event)



# A player has cards, stack and can take actions, which change states
class Player(object):
	def __init__(self, name, stack=0, sitting_out=True, cards=None):
		self.id = name
		self.name = name

		if cards:
			self.cards = cards
		else:
			self.cards = []

		self.sitting_out = sitting_out
		self.all_in = False
		self.last_action = Events.NONE

		self.stack = stack
		# wagers represents the total chips put into the pot during a hand
		self.wagers = 0
		# uncollected_bets represents the total chips put into the pot for one street
		self.uncollected_bets = 0

	def new_hand(self):
		self.cards = []
		self.last_action = Events.NONE
		if not self.wagers == 0:
			raise Exception("Money seems to be unaccounted for here...")
		self.uncollected_bets = 0

	def clone(self):
		p = Player(self.name, self.stack, self.sitting_out, [c.clone() for c in self.cards])
		p.all_in = self.all_in
		p.last_action = self.last_action
		p.wagers = self.wagers
		p.uncollected_bets = self.uncollected_bets
		return p

	def summary_for_json(self):
		out = {
			'name' : self.name,
			'stack' : self.stack
		}
		if self.sitting_out:
			out['sitting_out'] = True
		
		if self.last_action:
			out['last_action'] = self.last_action.__str__()

		if self.wagers != 0:
			out['wagers'] = self.wagers
		if self.uncollected_bets != 0:
			out['uncollected_bets'] = self.uncollected_bets
		
		return out

	def to_json(self, indent=None):
		return json.dumps(summary_for_json(), indent=indent)

	def clear_state(self):
		self.wagers = 0
		self.uncollected_bets = 0
		self.last_action = Events.NONE
		self.all_in = False
		self.cards = []

	def sit_out(self):
		if self.uncollected_bets != 0 and self.last_action != Events.FOLD:
			raise Exception("Cannot sit out in the middle of a hand!")
		self.sitting_out = True
		self.last_action = Events.SIT_OUT

	def sit_out(self):
		self.sitting_out = False
		self.last_action = Events.SIT_IN

	def deal(self, cards):
		self.cards.extend(cards)

	def check_amt(self, amt):
		if amt > self.stack:
			raise Exception("trying to bet more than stack")

	def ante(self, amt):
		self.check_amt(amt)
		self.wagers += amt
		self.stack -= amt

	def post_dead(self, amt):
		self.check_amt(amt)

		self.wagers += amt
		self.stack -= amt

	def bet(self, amt):
		self.check_amt(amt)

		if amt == self.stack:
			self.all_in = True

		self.last_action = Events.BET
		self.uncollected_bets = amt
		self.wagers += amt
		self.stack -= amt

		self.last_action = Events.BET

	def call(self, amt):
		amt_adjusted = amt - self.uncollected_bets

		if amt_adjusted >= self.stack:
			self.all_in = True
			amt_adjusted = self.stack

		self.wagers += amt_adjusted
		self.stack -= amt_adjusted
		self.uncollected_bets = amt

		self.last_action = Events.CALL

	def raise_to(self, amt, last_raise_size=0):
		self.check_amt(amt)

		diff = amt - self.uncollected_bets
		self.uncollected_bets = amt

		self.wagers += diff
		self.stack -= diff

		if amt == self.stack:
			self.all_in = True

		self.last_action = Events.RAISE_TO

	def post(self, amt):
		self.check_amt(amt)

		self.wagers += amt
		self.stack -= amt
		self.uncollected_bets = amt

		self.last_action = Events.POST
		
	def fold(self):
		self.last_action = Events.FOLD

	def check(self):
		self.last_action = Events.CHECK

	def can_buy(self, amt, max_buyin):
		return self.wagers + self.stack + amt <= max_buyin

	def buy(self, amt):
		self.stack += amt

	def lose(self, amt):
		self.wagers -= amt

	def win(self, amt):
		self.stack += amt

	def take_action(self, action, amt=None):
		if action == Events.Bet:
			self.bet(amt)
		elif action == Events.RAISE_TO:
			self.raise_to(amt)
		elif action == Events.FOLD:
			self.fold()
		elif action == Events.CALL:
			self.call(amt)
		else:
			raise Exception("Don't know how to handle event '{}' for {}".format(action, self.name))

	def __str__(self):
		return "{} ({})".format(self.name, self.stack)

	def __repr__(self):
		return self.__str__()

class HandHistory(object):
	def __init__(self):
		self.log_ = []

	def log(self, to_log):
		self.log_.append(to_log)

	def strlog(self):
		output = []
		def action_to_str(action):
			player, action, amt = action
			if action == Action.FOLD:
				return "{} folds".format(player)
			elif action in [Action.CALL, Action.BET, Action.POST, Action.ANTE]:
				raise Exception("TODO")

		
		for line in self.log:
			if type(line) == tuple:
				output.append(action_to_str(line))
			else:
				output.append(line)

		return "\n".join(output)
