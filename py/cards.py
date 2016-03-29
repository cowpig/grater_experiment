import random

def to_cards(handstr):
	return [Card(s) for s in handstr.split(" ")]

def pluralize(card_or_rank):
	if type(card_or_rank) is str:
		rankname = card_or_rank
	else:
		rankname = card_or_rank.rank
	if rankname == "six":
		return "sixes"
	else:
		return rankname + "s"

class Card(object):
	ranks = ["2", "3", "4", "5", "6", "7", 
	          "8", "9", "T", "J", "Q", "K", "A"]
	suits = ["s", "c", "d", "h"]

	suitnames = {
		"s" : "spades",
		"c" : "clubs",
		"d" : "diamonds",
		"h" : "hearts"
	}

	ranknames = {
		"2": "two",
		"3": "three",
		"4": "four",
		"5": "five",
		"6": "six",
		"7": "seven",
		"8": "eight",
		"9": "nine",
		"T": "ten",
		"J": "jack",
		"Q": "queen",
		"K": "king",
		"A": "ace"
	}

	def __init__(self, rank, suit=None):
		# so that Card("Th") works
		if suit == None:
			suit = rank[1]
			rank = rank[0]

		if rank not in Card.ranks or suit not in Card.suits:
			raise Exception("Bad suit or rank")

		self.rank = rank
		self.suit = suit


	def __str__(self):
		return "{}{}".format(self.rank, self.suit)

	def __repr__(self):
		return self.__str__()

class Deck(object):
	def __init__(self, shuffled=True):
		self.cards = []

		for suit in Card.suits:
			for rank in Card.ranks:
				self.cards.append(Card(rank, suit))

		if shuffled:
			self.shuffle()

	def shuffle(self):
		new_cards = []

		while self.cards:
			new_cards.append(self.cards.pop(random.randrange(len(self.cards))))
		
		self.cards = new_cards

	def deal(self):
		return self.cards.pop(0)


# class Game(object):
# 	def __init__(self, players):