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

def determine_blinds(table, last_bb_idx=None):
	def find_active_player(players, idx, diff=1):
		owes = set()
		while not table.players[idx] or table.players[idx].sitting_out:
			if table.players[idx]:
				owes.add(table.players[idx].id)
			idx = (idx + 1) % len(players)
		return (idx, owes)

	if last_bb_idx is None:
		sb_idx, owes = find_active_player(table.players, randint(0, len(table.players)-1))
		bb_idx, also_owes = find_active_player(table.players, sb_idx)
		owes.update(also_owes)
	else:
		idx = (last_bb_idx + 1) % len(table.players)
		bb_idx, owes = find_active_player(players, idx)
		sb_idx = last_bb_idx

	events = [(p.id, Events.OWE, table.bb) for p in owes]
	events.append((table.id, Events.SET_SB, sb_idx))
	events.append((table.id, Events.SET_BB, bb_idx))

	return events

def post_blinds(table, sb_idx, bb_idx):
	events = []
	for player in players:
		if is_playing(player):
			if player.id in table.owes_bb and player != players[bb_idx]:
				events.append(player, Events.POST, table.bb)
			if player.id in table.owes_sb:
				events.append(player, Events.POST_DEAD, table.sb)

	events.append(players[bb_idx].post(table.bb))

	if is_playing(players[sb_idx]):
		events.append(players[sb_idx].post(table.sb))
	else:
		return events

def prep_new_hand(table):
	players = copy.deepcopy(table.players)

	# set in/out states
	for player in players:
		if not player:
			continue
		if player.stack == 0 or (player.id in table.owes_bb and player.stack < BB):
			player.sitting_out = True
			log("{} needs more chips; sitting out".format(player.name))
		player.last_bet_size = 0
		player.last_action = Events.NONE

	return players

def deal_starting_hands(table, first, deck):
	# NOTE: this function doesn't follow the pure functional pattern: deck is mutated.
	players = copy.deepcopy(table.players)
	events = []
	for _ in range(2):
		for player in rotate_iter(players, first):
			if is_playing(player):
				events.append(player.deal([deck.deal()]))
	
	return (players, events)

def log_hands(table, first):
	for player in rotate_iter(table.players, first):
		table.log("{} ({}) dealt: {}".format(player.name, player.stack, player.cards))

def ordered_active_players(table, first):
	return deque([p for p in rotate_iter(table.players, first) if is_playing(p)])

def get_player_action(table, player, available_actions):
	print "pot is {}".format(sum([player.uncollected_bets + player.wagers for player in tabe.players]))
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
		if len(action) == 1:
			if action not in (Events.CALL, Events.FOLD):
				print "Must specify an amount."
				continue
			else:
				return (player, action, None)
		else:
			try:
				amt = int(action_in[1])
			except ValueError as e:
				print "second argument must be a number of chips"
				continue
			if not player.can_bet(amt, table.last_raise_size):
				print "Invalid amount."
			return (player, action, amt)

def betting_round(table, first):
	players = copy.deepcopy(table.players)
	n = len(players)
	next_to_act = first

	while next_to_act != last_raise:
		to_act = players[next_to_act]

		if not table.last_raise_size:
			available_actions = [Events.BET, Events.FOLD]
		elif to_act.stack <= (table.last_raise_size - to_act.uncollected_bets):
			available_actions = [Events.CALL, Events.FOLD]
		else:
			available_actions = [Events.RAISE_TO, Events.CALL, Events.FOLD]

		player, action, amt = get_player_action(table, to_act, available_actions)
		if action == Events.CALL:
			amt = table.last_raise_size
		player.take_action(action, amt)
		
		if action == Events.RAISE or action == Events.BET:
			table.last_raise = amt

		next_to_act = (next_to_act + 1) % n
		# close round on first to act if no bet/raises occur
		last_raise = last_raise or first 

	return players

def showdown(table):
	raise Exception("TODO")

def update_buyins(table):
	raise Exception("TODO")

if __name__ == '__main__':
	players = [
		Player(1,'cowpig',200,False),
		Player(10,'AJFenix',200,False),
		Player(11,'magicninja',200,False),
	]
	SB, BB = (1,2)
	table = Table("Hopper", SB, BB, players=players)
	bb_idx = None

	while True:
		deck = Deck(shuffled=True)

		# before hand starts
		table.players = prep_new_hand(table)
		# This isn't following the pattern of only changing state within
		#	the current block of code. How do we feel about that?
		table.new_hand()

		if len(active_players(table.players)) < 2:
			table.log("Not enough players to deal a new hand.")
		else:
			table.log("===Starting hand {}===".format(len(table.games)))

			# post blinds
			blind_location_events = determine_blinds(table, bb_idx)
			table.handle_events(blind_location_events)

			table.players, post_events, sb_owers = post_blinds(table, sb_idx, bb_idx)
			table.owes_sb.update(sb_owers)
			for post_event in post_events:
				table.log(post_event)

			# deal hole cards
			first = (bb_idx+1) % len(table.players)
			table.players, deal_events = deal_starting_hands(table, first, deck)
			for deal_event in deal_events:
				table.log(post_event)
			log_hands(table, first)

			# preflop betting
			table.last_raise_size = table.bb
			table.players, player_events = betting_round(table, first)
			for deal_event in deal_events:
				table.log(post_event)

			if len(active_players) > 1:
				# deal flop; flop betting
				table.board = [deck.deal(), deck.deal(), deck.deal()]
				table.log("===FLOP=== DEALT: {}".format(table.board))
				table.last_raise_size = None
				table.players, player_events = betting_round(table, sb_idx)
				for deal_event in deal_events:
					table.log(post_event)

			if len(active_players) > 1:
				# deal flop; flop betting
				turn = [deck.deal()]
				table.board += turn
				table.log("===TURN=== DEALT: {}".format(turn))
				table.last_raise_size = None
				table.players, player_events = betting_round(table, sb_idx)
				for deal_event in deal_events:
					table.log(post_event)

			if len(active_players) > 1:
				# deal flop; flop betting
				river = [deck.deal()]
				table.board += river
				table.log("===RIVER=== DEALT: {}".format(river))
				table.players, player_events = betting_round(table, sb_idx)
				for deal_event in deal_events:
					table.log(post_event)

			# showdown, stack updates:
			table.players = showdown(table)

		table.players = update_buyins(table)

