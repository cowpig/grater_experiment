from enum import Enum
from cards import Deck, Card

class Events(Enum):
	NONE, DEAL, POST, POST_DEAD, ANTE, BET, RAISE_TO, \
	CALL, FOLD, BUY, OWE, SET_BB, SET_SB = range(13)

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name

# deals with keeping track of players & missing blinds
class Table(object):
	def __init__(self, id_, name, sb=1, bb=2, ante=0, max_players=6, players=None):
		self.id = id_
		self.name = name

		self.sb = sb
		self.bb = bb
		self.ante = ante

		self.players = [None] * max_players
		if players:
			for i, p in enumerate(players):
				self.players[i] = p

		# figure out how to deal with these situations
		# http://www.learn-texas-holdem.com/questions/blind-rules-when-players-bust-out.htm
		self.owes_bb = set()
		self.owes_sb = set()

		self.deck = Deck()
		self.sb_idx = None
		self.bb_idx = None
		self.board = []
		self.last_raise_size = bb

		self.games = []

	def sit(self, player, seat_number):
		if self.players[seat_number]:
			raise Exception("Seat already taken")
		else:
			self.players[seat_number] = player
			self.post_bb.add(player.id)

	def stand(self, player):
		self.players[self.index(player)] = None

	def forgive_debts(self, player):
		if player in self.owes_bb:
			owes_bb.remove(player)
		if player in self.owes_sb:
			owes_sb.remove(player)

	def new_hand(self):
		self.games.append(HandHistory())
		self.board = []
		self.last_raise_size = self.bb

	def is_player(self, x):
		return x in [p.id for p in self.players if p]

	def get_player(self, id):
		for player in self.players:
			if player.id == id:
				return player
		return None

	def handle_event(self, subj, event, obj):
		self.log((subj, event, obj))
		if self.is_player(subj):
			player = get_player(subj)
			player.take_action(event)
			if event in (Events.POST, Events.POST_DEAD):
				if obj == self.sb and player.id in self.owes_sb:
					self.owes_sb.remove(player.id)
				elif obj == self.bb and player.id in self.owes_bb:
					self.owes_bb.remove(player.id)
		elif subj == self.id:
			if event == Events.OWE:
				if obj == self.bb:
					self.owes_bb.add(subj)
				elif obj == self.sb:
					self.owes_sb.add(subj)
				else:
					raise Exception("Can't owe a non-blind amt")
			elif event == Events.SET_BB:
				self.bb_idx = obj
			elif event == Events.SET_SB:
				self.sb_idx = obj

	def handle_events(self, events):
		for event in events:
			self.handle_event(*event)


	def log(self, event):
		print event
		self.games[-1].log(event)


# A player has cards, stack and can take actions, which change states
class Player(object):
	def __init__(self, id_, name, stack=0, sitting_out=True, cards=None):
		self.id = id_
		self.name = name

		if cards:
			self.cards = cards
		else:
			self.cards = []

		self.sitting_out = sitting_out
		self.all_in = False
		self.last_action = Events.NONE

		self.stack = stack
		self.wagers = 0
		self.uncollected_bets = 0

		self.pending_buyin = 0

	def deal(self, cards):
		self.cards.extend(cards)
		return (self.name, Events.DEAL, cards)

	def can_bet(self, amt, last_raise_size=0):
		if amt > self.stack:
			return False
		if amt < (last_raise_size*2) and amt != self.stack:
			False
		return True

	def ante(self, amt):
		if not self.can_bet(amt, last_amt):
			return False

		self.wagers += amt
		self.stack -= amt
		return (self.name, "ANTE", amt)

	def post_dead(self, amt):
		if not self.can_bet(amt, last_amt):
			return False

		self.wagers += amt
		self.stack -= amt
		return (self.name, Events.POST_DEAD, amt)

	def bet(self, amt):
		if not self.can_bet(amt):
			return False
			
		if amt == self.stack:
			self.all_in = True

		self.last_action = Events.BET
		self.uncollected_bets = amt
		self.wagers += amt
		self.stack -= amt
		return (self.name, Events.BET, amt)

	def call(self, amt):
		amt_adjusted = amt - self.uncollected_bets
		if amt_adjusted >= self.stack:
			self.all_in = True
			amt_adjusted = self.stack

		self.wagers += amt_adjusted
		self.stack -= amt_adjusted

		return (self.name, Events.CALL, amt_adjusted)

	def raise_to(self, amt, last_raise_size=0):
		if not self.can_bet(amt, last_raise_size):
			return False
				
		if amt == self.stack:
			self.all_in = True

		diff = amt - self.uncollected_bets

		self.last_action = Events.BET
		self.uncollected_bets = amt
		self.wagers += amt
		self.stack -= amt

		if amt == self.stack:
			self.all_in = True

		return (self.name, Events.RAISE, (last_amt, amt))

	def post(self, amt):
		if not self.can_bet(amt):
			return False

		self.wagers += amt
		self.stack -= amt
		self.uncollected_bets = amt
		self.last_action = Events.POST
		return (self.name, Events.POST, amt)

	def fold(self):
		self.last_action = Events.FOLD
		return (self.name, Events.FOLD, None)

	def can_buy(self, amt, max_buyin):
		return self.wagers + self.stack + amt <= max_buyin

	def buy(self, amt):
		self.stack_pending += amt
		return (self.name, Events.BUY, amt)

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

	def __repr__(self):
		return "{} ({})".format(self.name, self.stack)

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
