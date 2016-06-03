# relationships:
#	player - hole cards
#	player - chips
# 	player - last action taken
#	hand(game) - pot
#	hand(game) - board cards
#	hand(game) - players
#	hand(game) - player to act
import rankings
from utils import enum

Actions = enum('NONE', 'BET', 'CALL', 'FOLD')
States = enum('OUT', 'IN', 'ALL_IN')

class Player(object):
	def __init__(self, id_, cards=None, stack=0):
		self.id = id_

		if cards:
			self.cards = cards
		else:
			self.cards = []

		self.stack = stack
		self.wagers = 0
		self.last_action = Actions.NONE
		self.state = States.OUT
		
		# self.stack_pending = 0

	# not sure if this should be in the Player object
	# def add_chips(self, amt):
	# 	if self.state:
	# 		self.stack_pending += amt
	# 	else:
	# 		self.stack += amt


class Game(object):
	def __init__(self, players):
		pass

