import rankings
import copy
from enum import Enum
from collections import deque

from utils import rotate_iter
from cards import Card, Deck
from game_models import Events, Table, Player, HandHistory


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
				events.append(player.post(table.bb))
				table.owes_bb.remove(player.id)
			if player.id in table.owes_sb:
				events.append(player.post_dead(table.sb))
				table.owes_sb.remove(player.id)

	events.append(players[bb_idx].post(table.bb))
	if is_playing(players[sb_idx]):
		events.append(players[sb_idx.post(table.sb)])
		return (players, events, set())
	else:
		return (players, events, set(players[sb_idx].id))

def prep_new_hand(table):
	players = copy.deepcopy(table.players)

	# set in/out states
	for player in players:
		if player.stack == 0 or (player.id in table.owes_bb and player.stack < BB):
			player.sitting_out = True
			log("{} needs more chips; sitting out".format(player.name))
		player.last_bet_size = 0
		player.last_action = Events.NONE

	return table

def deal_starting_hands(table, first):
	players = copy.deepcopy(table.players)
	events = []
	for player in rotate_iter(players, first):
		if is_playing(player):
			events.append(player.deal())

def ordered_active_players(table, first):
	return deque([p for p in rotate_iter(table.players, first) if is_playing(p)])

def get_player_action(table, player):
	raise Exception("TODO")
	return (player, action)

def betting_round(table, first):
	players = copy.deepcopy(table.players)
	n = len(players)
	last_raise = None
	next_to_act = first

	while next_to_act != last_raise:
		player, action = get_player_action(table, players[next_to_act])
		
		if action == Events.RAISE or action == Events.BET:
			last_raise = next_to_act

		next_to_act = (next_to_act + 1) % n
		# close round on first to act if no bet/raises occur
		last_raise = last_raise or first 

	raise Exception("TODO")

def showdown(table):
	raise Exception("TODO")

def update_buyins(table):
	raise Exception("TODO")

if __name__ == '__main__':
	players = [
		Player(1,'cowpig',200),
		Player(10,'AJFenix',200),
		Player(11,'magicninja',200),
	]
	SB, BB = (1,2)
	t = Table("Hopper", SB, BB, players=players)

	while True:
		deck = Deck(shuffled=True)

		# before hand starts
		table.players = prep_new_hand(table.players)
		# This isn't following the pattern of only changing state within
		#	the current block of code. How do we feel about that?
		table.new_hand()

		actives = active_players(table.players)
		if len(actives) < 2:
			table.log("\nNot enough players to deal a new hand.")
		else:
			table.log("===Starting hand {}===".format(hand_num))

		# post blinds
		sb_idx, bb_idx, bb_owers = determine_blinds(table, bb_idx)
		table.owes_bb.update(bb_owers)

		table.players, post_events, sb_owers = post_blinds(table, sb_idx, bb_idx)
		table.owes_sb.update(sb_owers)
		for post_event in post_events:
			table.log(post_event)

		# deal hole cards
		first = (bb_idx+1) % len(table.players)
		table.players, deal_events = deal_starting_hands(table, first)
		for deal_event in deal_events:
			table.log(post_event)

		# preflop betting
		table.players, player_events = betting_round(table, first)
		for deal_event in deal_events:
			table.log(post_event)

		if len(active_players) > 1:
			# deal flop; flop betting
			table.board = [deck.deal(), deck.deal(), deck.deal()]
			table.log("===FLOP=== DEALT: {}".format(table.board))
			table.players, player_events = betting_round(table, sb_idx)
			for deal_event in deal_events:
				table.log(post_event)

		if len(active_players) > 1:
			# deal flop; flop betting
			turn = [deck.deal()]
			table.board += turn
			table.log("===TURN=== DEALT: {}".format(turn))
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

