from cards import Card, pluralize, to_cards
from itertools import combinations

CARD_ORDER = ["2", "3", "4", "5", "6", "7", 
          "8", "9", "T", "J", "Q", "K", "A"]

def best_hand_from_cards(cards):
	if len(cards) < 5:
		raise Exception("Need 5 cards to make a poker hand")
	return best_hand(combinations(cards, 5))

def best_hand(hands):
	return sorted(hands, cmp=compare_hands, reverse=True)[0]

def compare_hands(hand1, hand2):
	h1 = handrank_encoding(hand1)
	h2 = handrank_encoding(hand2)
	return compare_encoded_hands(h1, h2)

def compare_ranks(this, that):
	if type(this) is Card:
		return CARD_ORDER.index(this.rank) - CARD_ORDER.index(that.rank)

	return CARD_ORDER.index(this) - CARD_ORDER.index(that)

def compare_encoded_hands(hand1, hand2):
	if hand1[0] != hand2[0]:
		return hand1[0] - hand2[0]

	for r1, r2 in zip(hand1[1:], hand2[1:]):
		if r1 != r2:
			return compare_ranks(r1, r2)

	return 0

def handrank_encoding(hand):
	''' Encodes a 5-card hand as:
				N K K K K K
		where each K represents a kicker, (a flush has 5, a straight has one, 
		full house has two) and N represents a numerical value (0 is High Card
		and 9 is Straight Flush). See def handrank_encoding_to_name for a more 
		precise explanation.
	'''
	hand = to_cards(hand)
	if len(hand) != 5:
		raise Exception("Need 5 cards to encode")

	# first look for pairs
	rankset = set([card.rank for card in hand])
	buckets = [(rank, sum([card.rank == rank for card in hand])) for rank in rankset]
	def ranker(a, b):
		if a[1] != b[1]:
			return b[1] - a[1]
		return compare_ranks(b[0], a[0])

	buckets.sort(ranker)

	# four of a kind
	if [size for rank, size in buckets] == [4, 1]:
		return [7, buckets[0][0], buckets[1][0], None, None, None]
	# full house
	elif [size for rank, size in buckets] == [3, 2]:
		return [6, buckets[0][0], buckets[1][0], None, None, None]
	# three of a kind
	elif [size for rank, size in buckets] == [3, 1, 1]:
		return [3, buckets[0][0], buckets[1][0], buckets[2][0], None, None]
	# two pair
	elif [size for rank, size in buckets] == [2, 2, 1]:
		return [2, buckets[0][0], buckets[1][0], buckets[2][0], None, None]
	# one pair
	elif [size for rank, size in buckets] == [2, 1, 1, 1]:
		return [1, buckets[0][0], buckets[1][0], buckets[2][0], buckets[3][0], None]
	else:
		flush = len(set([card.suit for card in hand])) == 1
		nums = sorted([CARD_ORDER.index(card.rank) for card in hand])
		# print nums
		straight = max(nums) - min(nums) == 4
		wheel = nums == [0,1,2,3,12]

		if flush:
			# straight flush
			if straight:
				return [8, buckets[0][0], buckets[1][0], buckets[2][0], buckets[3][0], buckets[4][0]]
			if wheel:
				return [8, buckets[1][0], buckets[2][0], buckets[3][0], buckets[4][0], buckets[0][0]]
			
			# flush
			return [5, buckets[0][0], buckets[1][0], buckets[2][0], buckets[3][0], buckets[4][0]]

		# straight
		if straight:
			return [4, buckets[0][0], buckets[1][0], buckets[2][0], buckets[3][0], buckets[4][0]]
		if wheel:
			return [4, buckets[1][0], buckets[2][0], buckets[3][0], buckets[4][0], buckets[0][0]]

		# high card
		return [0, buckets[0][0], buckets[1][0], buckets[2][0], buckets[3][0], buckets[4][0]]

def handrank_encoding_to_name(handrank_encoding):
	N, K1, K2, K3, K4, K5 = handrank_encoding
	if N == 0:
		return "High Card {}, {} kicker".format(Card.ranknames[K1], Card.ranknames[K2])
	elif N == 1:
		return "Pair of {}, {} kicker".format(pluralize(Card.ranknames[K1]), Card.ranknames[K2])
	elif N == 2:
		return "Two Pair, {} and {}".format(
				pluralize(Card.ranknames[K1]), pluralize(Card.ranknames[K2]))
	elif N == 3:
		return "Three of a Kind {}".format(pluralize(Card.ranknames[K1]))
	elif N == 4:
		return "Straight, {} to {}".format(Card.ranknames[K5], Card.ranknames[K1])
	elif N == 5:
		return "Flush, {} high".format(Card.ranknames[K1])
	elif N == 6:
		return "Full House, {} full of {}".format(
				pluralize(Card.ranknames[K1]), pluralize(Card.ranknames[K2]))
	elif N == 7:
		return "Four of a Kind, {}".format(pluralize(Card.ranknames[K1]))
	elif N == 8:
		if K1 == "A":
			return "Royal Flush"
		return "Straight Flush, {} to {}".format(Card.ranknames[K5], Card.ranknames[K1])

def hand_to_name(hand):
	return handrank_encoding_to_name(handrank_encoding(hand))
