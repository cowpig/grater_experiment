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

def active_players(players):
	return [p for p in players if p and not p.sitting_out]

def determine_blinds(table):
	def find_active_player(idx):
		owes = set()
		idx = idx % len(table.players)
		while not table.players[idx] or table.players[idx].sitting_out:
			if table.players[idx]:
				owes.add(table.players[idx].id)
			idx = (idx + 1) % len(table.players)
		return (idx, owes)

	if table.game_state['bb_idx'] is None:
		sb_idx, owes = find_active_player(randint(0, len(table.players)-1))
		bb_idx, also_owes = find_active_player(sb_idx+1)
		owes.update(also_owes)
	else:
		bb_idx, owes = find_active_player(table.game_state['bb_idx'] + 1)
		sb_idx = table.game_state['bb_idx']

	events = [(p.id, Events.OWE, table.bb) for p in owes]
	events.append((table.id, Events.SET_GAME_STATE, ("sb_idx", sb_idx)))
	events.append((table.id, Events.SET_GAME_STATE, ("bb_idx", bb_idx)))

	return events

def post_blinds(table):
	events = []
	for player in players:
		if is_playing(player):
			if player.id in table.owes_bb and player != players[table.game_state['bb_idx']]:
				events.append(player, Events.POST, table.bb)
			if player.id in table.owes_sb:
				events.append(player, Events.POST_DEAD, table.sb)

	if is_playing(players[table.game_state['sb_idx']]):
		events.append((players[table.game_state['sb_idx']].id, Events.POST, table.sb))

	events.append((players[table.game_state['bb_idx']].id, Events.POST, table.bb))
	
	return events

def prep_new_hand(table):
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
	for player in rotate_iter(table.players, first):
		table.log("{} ({}) dealt: {}".format(player.name, player.stack, player.cards))

def ordered_active_players(table, first):
	return deque([p for p in rotate_iter(table.players, first) if is_playing(p)])

def get_potsize(table):
	print "calculating sum of:"
	print [(player.name, player.wagers) 
			for player in table.players if is_playing(player)]
	return 

def get_available_actions(table):
	to_act = table.get_next_to_act()

	if not to_act:
		return None

	if not table.game_state['last_raise_size']:
		return (Events.BET, Events.CHECK, Events.FOLD)
	elif to_act.stack <= (table.game_state['last_raise_size'] - to_act.uncollected_bets):
		return (Events.CALL, Events.FOLD)
	else:
		return (Events.RAISE_TO, Events.CALL, Events.FOLD)

def get_player_action(table, player):
	available_actions = get_available_actions(table)

	print "pot is {}".format(table.current_pot())
	print "your stack is {}".format(player.stack)
	print "available_actions are:"
	print available_actions

	while True:
		action_in = raw_input("{}> ".format(player.name)).split()
		try:
			action = Events[action_in[0].upper()]
		except KeyError as e:
			print "{} is not a valid action".format(e)
			continue
		if action not in available_actions:
			print "{} is not a valid action".format(e)
			continue
		if len(action_in) == 1:
			if action not in (Events.CALL, Events.FOLD):
				print "Must specify an amount."
				continue
			else:
				amt = table.game_state['last_raise_size']
				return (player.id, action, amt)
		else:
			try:
				amt = int(action_in[1])
			except ValueError as e:
				print "second argument must be a number of chips"
				continue
			if not player.can_bet(amt, table.last_raise_size):
				print "Invalid amount."
			return (player.id, action, amt)

def betting_round(table, first):
	# TODO: in keeping with the rest of the code, I'd like to pull all table.handle_event
	# 	calls out to the main loop
	n = len(table.players)
	print "action starts at {}: {}".format(first, table.players[first])
	table.handle_event(table.id, Events.SET_GAME_STATE, ("next_to_act", first))
	table.handle_event(table.id, Events.SET_GAME_STATE, ("last_to_raise", None))

	while table.game_state['next_to_act'] != table.game_state['last_to_raise']:
		to_act = table.get_next_to_act()
		print "game status:"
		print table.to_json(indent=4)
		print "to_act", to_act
		if to_act:
			available_actions = get_available_actions(table)
			# returned action should be a valid action
			action = get_player_action(table, to_act)

			table.handle_event(*action)

			if action == Events.CALL:
				amt = table.game_state['last_raise_size']
			elif action == Events.RAISE_TO or action == Events.BET:
				 table.handle_event(table.id, Events.SET_GAME_STATE, ("last_raise_size", amt))

		table.handle_event(table.id, Events.SET_GAME_STATE, ("next_to_act", (table.game_state['next_to_act'] + 1) % n))
		# close round on first to act if no bet/raises occur
		table.handle_event(table.id, Events.SET_GAME_STATE, ("last_to_raise", table.game_state['last_to_raise'] or first))

def showdown(table):
	raise Exception("TODO")

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

		table.handle_events(prep_new_hand(table))
		table.handle_event(table.id, Events.NEW_HAND, None)

		if len(active_players(table.players)) < 2:
			table.log("Not enough players to deal a new hand.")
		else:
			# print "starting hand game state:"
			# print table.to_json(4)

			# post blinds
			table.handle_events(determine_blinds(table))
			table.handle_events(post_blinds(table))

			# deal hole cards
			first = (table.game_state['bb_idx']+1) % len(table.players)
			table.handle_events(deal_starting_hands(table, first))

			# preflop betting
			table.handle_event(table.id, Events.SET_GAME_STATE, ("last_raise_size", table.bb))
			betting_round(table, first)

			for deal_event in deal_events:
				table.log(post_event)

			if len(active_players) > 1:
				# deal flop; flop betting
				table.board = [deck.deal(), deck.deal(), deck.deal()]
				table.log("===FLOP=== DEALT: {}".format(table.board))
				table.last_raise_size = None
				table.players, player_events = betting_round(table, table.game_state['sb_idx'])
				for deal_event in deal_events:
					table.log(post_event)

			if len(active_players) > 1:
				# deal flop; flop betting
				turn = [deck.deal()]
				table.board += turn
				table.log("===TURN=== DEALT: {}".format(turn))
				table.last_raise_size = None
				table.players, player_events = betting_round(table, table.game_state['sb_idx'])
				for deal_event in deal_events:
					table.log(post_event)

			if len(active_players) > 1:
				# deal flop; flop betting
				river = [deck.deal()]
				table.board += river
				table.log("===RIVER=== DEALT: {}".format(river))
				table.players, player_events = betting_round(table, table.game_state['sb_idx'])
				for deal_event in deal_events:
					table.log(post_event)

			# showdown, stack updates:
			table.players = showdown(table)

		table.players = update_buyins(table)

