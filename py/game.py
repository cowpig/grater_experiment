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
import copy
from enum import Enum

class Actions(Enum):
	'NONE', 'POST', 'POST_DEAD', 'ANTE', \
	'BET', 'RAISE', 'CALL', 'FOLD', 'BUY' = range(9)

# deals with keeping track of players & missing blinds
class Table(object):
	def __init__(self, id_, sb=1, bb=2, ante=0, max_players=6, players=None):
		self.id = id_

		self.sb = sb
		self.bb = bb
		self.ante = ante

		self.players = [None] * max_players
		if players:
			for i, p in enumerate(players):
				self.players[i] = p

		self.games = []

		self.btn_idx = None

		# figure out how to deal with these situations
		# http://www.learn-texas-holdem.com/questions/blind-rules-when-players-bust-out.htm
		self.owes_bb = set()
		self.owes_sb = set()

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
		self.last_action = Actions.NONE

		self.stack = stack
		self.wagers = 0
		self.last_wager_size = 0

		self.pending_buyin = 0

	def deal(self, card):
		self.cards.append(card)

	def can_bet(self, amt, last_amt=0):
		if amt > self.stack:
			return False
		if amt < (last_amt*2) and amt != self.stack:
			False
		return True

	def ante(self, amt):
		if not can_bet(amt, last_amt):
			return False

		self.wagers += amt
		self.stack -= amt
		return (self.name, "ANTE", amt)

	def bet(self, amt, last_amt=0):
		if not can_bet(amt, last_amt):
			return False
			
		if amt == self.stack:
			self.all_in = True

		self.last_action = Actions.BET
		self.last_bet_size = amt - last_amt
		self.wagers += amt
		self.stack -= amt
		if (last_amt == 0):
			return (self.name, Actions.BET, amt)
		else:
			return (self.name, Actions.RAISE, (last_amt, amt))

	def post(self, amt):
		if not can_bet(amt, last_amt):
			return False

		self.wagers += amt
		self.stack -= amt
		self.last_action = Actions.POST
		return (self.name, Actions.POST, amt)

	def post(self, amt):
		if not can_bet(amt, last_amt):
			return False

		self.wagers += amt
		self.stack -= amt
		self.last_action = Actions.POST_DEAD
		return (self.name, Actions.POST_DEAD, amt)

	def fold(self):
		self.last_action = Actions.FOLD
		return (self.name, Actions.FOLD, None)

	def can_buy(self, amt, max_buyin):
		return self.wagers + self.stack + amt <= max_buyin

	def buy(self, amt):
		self.stack_pending += amt
		return (self.name, Actions.BUY, amt)

	def __repr__(self):
		return "{} ({})".format(self.name, self.stack)

class Hand(object):
	def __init__(self, table):
		self.log = []
		self.table = table

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

#####
# game logic

def log(s):
	print s
	log.transcript.append(s)
log.transcript = []

def is_playing(player):
	if player is None:
		return False
	else:
		return not player.sitting_out

def active_players(players):
	return [p for p in players if not p.sitting_out]

def determine_blinds(table, last_bb_idx=None):
	def find_active_player(players, idx, diff=1):
		owes = set()
		while table.players[idx].sitting_out:
			owes.add(table.players[idx].id)
			idx = (idx + 1) % len(players)
		return (idx, owes)

	if last_bb_idx is None:
		sb_idx, owes = find_active_player(table.players, 
										random.randint(len(table.players)))
		bb_idx, also_owes = find_active_player(table.players, sb_idx)
		owes.update(also_owes)
	else:
		idx = (last_bb_idx + 1) % len(table.players)
		bb_idx, owes = find_active_player(players, idx)
		sb_idx = last_bb_idx

	return (sb_idx, bb_idx, owes)

def post_blinds(table, sb_idx, bb_idx):
	events = []
	players = copy.deepcopy(table.players)
	for player in players:
		if is_playing(player):
			if player.id in table.owes_bb and player != players[bb_idx]:
				player.post(table.bb)
				table.owes_bb.remove(player.id)
			if player.id in table.owes_sb:
				player.ante(table.sb)
				table.owes_sb.remove(player.id)

	players[bb_idx].post(table.bb)
	if is_playing(players[sb_idx]):
		players[sb_idx.post(table.sb)]
		return (players, set())
	else:
		return (players, set(players[sb_idx].id))



def sit_out_inactives(table):
	players = copy.deepcopy(table.players)

	# set in/out states
	for player in players:
		if player.stack == 0 or (player.id in table.owes_bb and player.stack < BB):
			player.sitting_out = True
			log("{} needs more chips; sitting out".format(player.name))
		
	return players

if __name__ == '__main__':
	players = [
		Player(1,'cowpig',200),
		Player(10,'AJFenix',200),
		Player(11,'magicninja',200),
	]
	SB, BB = (1,2)
	t = Table(0, SB, BB, players=players)

	hand = []

	while True:
		table.players = sit_out_inactives(table)

		actives = active_players(table.players)
		if len(actives) < 2:
			log("\nNot enough players to deal a new hand.")
		else:
			log("===Starting hand {}===".format(hand_num))

		sb_idx, bb_idx, bb_owers = determine_blinds(table, bb_idx)
		
		table.owes_bb.update(bb_owers)

		table.players, sb_owers = post_blinds(table, sb_idx, bb_idx)
		table.owes_sb.update(sb_owers)



		# update everyones' stacks
		deck = cards.Deck()
		board = []
		log("Dealing hand {}")
