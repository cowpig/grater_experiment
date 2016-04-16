class Player(object):
	def __init__(self, web_conn, db_conn):
		self.web_conn = web_conn
		self.db_conn = db_conn
		self.cards = []
		self.stack = 0

	def add_chips(self, amt):
		pass


class Game(object):
	def __init__(self, players):
		pass 