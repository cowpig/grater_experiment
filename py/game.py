# relationships:
#	player - hole cards
#	player - chips
# 	player - last action taken
#	hand(game) - pot
#	hand(game) - board cards
#	hand(game) - players
#	hand(game) - player to act
import rankings
import cards
from utils import enum

Actions = enum('NONE', 'BET', 'CALL', 'FOLD')
States = enum('OUT', 'IN', 'ALL_IN')
Blinds = enum('SB', 'BB', 'STRADDLE')

# deals with keeping track of players & hands played
class Table(object):
	def __init__(self, id_, sb=1, bb=2, ante=0, max_players=6):
		self.id = id_

		self.sb = sb
		self.bb = bb
		self.ante = ante
		self.players = [None] * max_players

		self.games = []

		# figure out how to deal with these situations
		# http://www.learn-texas-holdem.com/questions/blind-rules-when-players-bust-out.htm
		# self.missed_bb = set()
		# self.missed_sb = set()

	def add_player(self, player, seat_number):
		if self.players[seat_number]:
			raise Exception("Seat already taken")
		else:
			self.players[seat_number] = player

	def remove_player(self, player):
		self.players[self.index(player)] = None

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

		self.stack = stack
		self.wagers = 0
		self.last_action = Actions.NONE
		self.last_bet_size = 0
		self.state = States.OUT

		self.blinds_owed = []
		# self.stack_pending = 0

	def deal(self, card):
		self.cards.append(card)

	def can_bet(self, amt, last_amt=0):
		if amt > self.stack:
			return False
		if amt < (last_amt*2) and amt < self.stack:
			False
		return True

	def bet(self, amt, last_amt=0):
		if not can_bet(amt, last_amt):
			raise Exception("illegal bet")
			
		if amt == self.stack:
			self.state = States.ALL_IN

		self.last_action = Actions.BET
		self.last_bet_size = amt - last_amt
		self.wagers += amt
		self.stack -= amt

	def fold(self):
		self.last_action = Actions.FOLD
		self.state = Sates.OUT

	# not sure if this should be in the Player object
	# def add_chips(self, amt):
	# 	if self.state:
	# 		self.stack_pending += amt
	# 	else:
	# 		self.stack += amt

