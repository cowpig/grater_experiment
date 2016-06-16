import rankings
import copy

from collections import deque

from utils import rotate_iter
from cards import Card, Deck
from game_models import Events, Table, Player, HandHistory
from random import randint

def is_playing(player):
	if player is None:
		return False
	else:
		return not player.sitting_out

def filter_folds(players):
	return [p for p in players if p.last_action != Events.FOLD]

def determine_blinds(table):
	def find_active_player(idx):
		owes = set()
		idx = idx % len(table.players)
		while not table.players[idx] or table.players[idx].sitting_out:
			if table.players[idx]:
				owes.add(table.players[idx].id)
			idx = (idx + 1) % len(table.players)
		return (idx, owes)

	if table.get_bb_idx() is None:
		sb_idx, owes = find_active_player(randint(0, len(table.players)-1))
		bb_idx, also_owes = find_active_player(sb_idx+1)
		owes.update(also_owes)
	else:
		bb_idx, owes = find_active_player(table.get_bb_idx() + 1)
		sb_idx = table.get_bb_idx()

	events = [(p.id, Events.OWE, table.bb) for p in owes]
	events.append((table.id, Events.SET_GAME_STATE, ("sb_idx", sb_idx)))
	events.append((table.id, Events.SET_GAME_STATE, ("bb_idx", bb_idx)))

	return events

def post_blinds(table):
	events = []
	for player in table.get_active_players():
		if player.id in table.owes_bb and player != players[table.get_bb_idx()]:
			events.append(player, Events.POST, table.bb)
		if player.id in table.owes_sb:
			events.append(player, Events.POST_DEAD, table.sb)

	if is_playing(players[table.get_sb_idx()]):
		events.append((players[table.get_sb_idx()].id, Events.POST, table.sb))

	events.append((players[table.get_bb_idx()].id, Events.POST, table.bb))
	
	return events

def sit_out_inactives(table):
	events = []

	# set correct states
	for player in players:
		if not player:
			continue
		if player.stack == 0 or (player.id in table.owes_bb and player.stack < BB):
			log("{} needs more chips to play".format(player.name))
			events.append((player.id, Events.SIT_OUT, None))

	return events

def deal_starting_hands(table, first):
	# NOTE: this function doesn't follow the pure functional pattern: deck is mutated.
	players = copy.deepcopy(table.players)
	events = []
	for _ in range(2):
		for player in rotate_iter(players, first):
			if is_playing(player):
				events.append((player.id, Events.DEAL, 1))
	
	return events

def log_hands(table, first):
	events = []
	for player in rotate_iter(table.players, first):
		msg = "{} ({}) dealt: {}".format(player.name, player.stack, player.cards)
		events.append(table.id, Events.LOG, msg)
	return events

def get_next_to_act(table, first):
	# players who are all-in or who folded don't take actions
	players = [p for p in filter_folds(table.get_active_players(first)) if p.stack]
	players = deque(players)

	if not players:
		return None

	last_to_raise = None
	stop_at = None

	while True:
		player = players.popleft()
		print "checking", player

		if player.last_action in (Events.NONE, Events.POST):
			return player

		if last_to_raise is not None:
			if player.uncollected_bets < last_to_raise.uncollected_bets:
				return player
			if last_to_raise == player:
				return None
		elif stop_at == player:
			return None

		if player.last_action in (Events.RAISE_TO, Events.BET):
			last_to_raise = player

		stop_at = stop_at or player
		players.append(player)

def get_last_raise_size(table):
	return max([p.uncollected_bets for p in table.get_active_players()])

def get_last_raise_diff(table):
	raises = set([p.uncollected_bets for p in table.get_active_players()])
	if raises:
		raise_size = max(raises)
		raises.remove(raise_size)
		if raises:
			before_that = max(raises)
			return raise_size - before_that
		else:
			return raise_size

	return 0

def get_available_actions(table, player):
	actions = [Events.FOLD]
	last_raise_size = get_last_raise_size(table)

	if last_raise_size > player.uncollected_bets:
		actions.append(Events.CALL)
	else:
		actions.append(Events.CHECK)

	if player.stack + player.uncollected_bets > last_raise_size:
		if last_raise_size == 0:
			actions.append(Events.BET)
		else:
			actions.append(Events.RAISE_TO)

	return actions

def is_legal_betsize(table, player, amt):
	if amt == player.stack:
		return True
	elif amt > player.stack:
		return False

	if amt - get_last_raise_size(table) >= get_last_raise_diff(table):
		return True

	return False


def get_player_action(table, player):
	available_actions = get_available_actions(table, player)

	print "BOARD:", table.get_board()
	print "YOUR HAND:", player.cards
	print "pot is {}".format(table.current_pot())
	stack_msg = "your stack is {}".format(player.stack)
	if player.uncollected_bets:
		stack_msg += " (+ {} in front)".format(player.uncollected_bets)
	print "it is", get_last_raise_size(table), "to you"
	print "available_actions are:"
	print available_actions

	while True:
		action_in = raw_input("\t{}> ".format(player.name)).split()
		print action_in
		if not action_in:
			continue
		try:
			if action_in[0].upper() == "RAISE":
				action_in[0] = "RAISE_TO"
			action = Events[action_in[0].upper()]
		except KeyError as e:
			print "{} is not a valid action".format(e)
			continue
		if action not in available_actions:
			print "{} is not a valid action".format(action)
			continue
		if len(action_in) == 1:
			if action not in (Events.CALL, Events.FOLD, Events.CHECK):
				print "Must specify an amount."
				continue
			else:
				amt = get_last_raise_size(table)
				return (player.id, action, amt)
		else:
			try:
				amt = int(action_in[1])
			except ValueError as e:
				print "second argument must be a number of chips"
				continue
			if not is_legal_betsize(table, player, amt):
				print "Invalid bet/raise size."
				continue
			return (player.id, action, amt)

def showdown(table, first):
	events = []

	players = table.get_active_players()
	showdown_players = [p for p in players if p.last_action != Events.FOLD]

	if len(showdown_players) == 1:
		p = showdown_players[0]
		pot = table.current_pot()
		events.append((table.id, Events.LOG, "{} wins {} without showdown.".format(p, pot)))
		events.append((showdown_players[0].id, Events.WIN_POT, pot))

	else:
		# iterate over players in order, showing hands
		# order players by their hand strength
		# while there's money in the pot, take the strongest hand(s) and give
		#	those players other players' money


def update_buyins(table):
	raise Exception("TODO")

if __name__ == '__main__':
	players = [
		Player('cowpig',200,False),
		Player('AJFenix',200,False),
		Player('magicninja',200,False),
	]
	SB, BB = (1,2)
	table = Table("Hopper", SB, BB, players=players)
	print "SB:", table.sb
	bb_idx = None

	while True:
		deck = Deck(shuffled=True)

		table.handle_events(sit_out_inactives(table))
		table.handle_event(table.id, Events.NEW_HAND, None)

		if len(table.get_active_players()) < 2:
			table.handle_event(table.id, Events.LOG, 
								"Not enough players to deal a new hand.")
		else:
			# print "starting hand game state:"
			# print table.to_json(4)

			# post blinds
			table.handle_events(determine_blinds(table))
			table.handle_events(post_blinds(table))

			# deal hole cards
			first = (table.get_bb_idx()+1) % len(table.players)
			table.handle_events(deal_starting_hands(table, first))

			# preflop betting
			player = get_next_to_act(table, first)
			while player is not None:
				table.handle_event(*get_player_action(table, player))
				player = get_next_to_act(table, first)

			# sb is first to act for the rest of the rounds
			first = table.get_sb_idx()
			
			# FLOP
			if len(filter_folds(table.get_active_players())) > 1:
				table.handle_event(table.id, Events.NEW_STREET, None)
				table.handle_event(table.id, Events.DEAL, 3)
				msg = "===FLOP=== DEALT: {}".format(table.get_board())
				table.handle_event(table.id, Events.LOG, msg)

				player = get_next_to_act(table, first)
				while player is not None:
					table.handle_event(*get_player_action(table, player))
					player = get_next_to_act(table, first)

			# TURN
			if len(filter_folds(table.get_active_players())) > 1:
				table.handle_event(table.id, Events.NEW_STREET, None)
				table.handle_event(table.id, Events.DEAL, 1)
				msg = "===TURN=== DEALT: {} {}".format(table.get_board()[:3], 
															table.get_board()[3:])
				table.handle_event(table.id, Events.LOG, msg)

				player = get_next_to_act(table, first)
				while player is not None:
					table.handle_event(*get_player_action(table, player))
					player = get_next_to_act(table, first)

			# RIVER
			if len(filter_folds(table.get_active_players())) > 1:
				table.handle_event(table.id, Events.NEW_STREET, None)
				table.handle_event(table.id, Events.DEAL, 1)
				msg = "===RIVER=== DEALT: {} {}".format(table.get_board()[:4], 
															table.get_board()[4:])
				table.handle_event(table.id, Events.LOG, msg)

				player = get_next_to_act(table, first)
				while player is not None:
					table.handle_event(*get_player_action(table, player))
					player = get_next_to_act(table, first)

			# showdown, stack updates:
			showdown(table)

		table.players = update_buyins(table)

