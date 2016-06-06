
class Events(Enum):
	'NONE', 'DEAL', 'POST', 'POST_DEAD', 'ANTE', \
	'BET', 'RAISE', 'CALL', 'FOLD', 'BUY' = range(10)

# deals with keeping track of players & missing blinds
class Table(object):
	def __init__(self, id_, sb=1, bb=2, ante=0, max_players=6, players=None):
		self.id = id_
		self.name = name

		self.sb = sb
		self.bb = bb
		self.ante = ante

		self.players = [None] * max_players
		if players:
			for i, p in enumerate(players):
				self.players[i] = p

		self.btn_idx = None

		# figure out how to deal with these situations
		# http://www.learn-texas-holdem.com/questions/blind-rules-when-players-bust-out.htm
		self.owes_bb = set()
		self.owes_sb = set()

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

	def new_hand():
		self.games.append(HandHistory())
		self.board = []
		self.last_raise_size = bb

	def log(self, event):
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
		if not can_bet(amt, last_amt):
			return False

		self.wagers += amt
		self.stack -= amt
		return (self.name, "ANTE", amt)

	def post_dead(self, amt):
		if not can_bet(amt, last_amt):
			return False

		self.wagers += amt
		self.stack -= amt
		return (self.name, Events.POST_DEAD, amt)

	def bet(self, amt):
		if not can_bet(amt):
			return False
			
		if amt == self.stack:
			self.all_in = True

		self.last_action = Events.BET
		self.uncollected_bets = amt
		self.wagers += amt
		self.stack -= amt
		return (self.name, Events.BET, amt)

	def raise_to(self, amt, last_raise_size=0):
		if not can_bet(amt, last_raise_size):
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
		if not can_bet(amt, last_amt):
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

	def __repr__(self):
		return "{} ({})".format(self.name, self.stack)

class HandHistory(object):
	def __init__(self):
		self.log = []

	def log(self, to_log):
		self.log.append(to_log)

	def strlog(self):
		output = []
		def action_to_str(action):
			player, action, amt = action
			if action == Action.FOLD:
				return "{} folds".format(player)
			elif action in [Action.CALL, Action.BET, Action.POST, Action.ANTE]:

		
		for line in self.log:
			if type(line) == tuple:
				output.append(action_to_str(line))
			else:
				output.append(line)

		return "\n".join(output)
