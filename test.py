import rankings
from cards import Card, to_cards

def encode_hand(hand):
	return rankings.handrank_encoding(to_cards(hand))

def compare_hands(hand1, hand2):
	h1 = encode_hand(hand1)
	h2 = encode_hand(hand2)
	return rankings.compare_encoded_hands(h1, h2)

examples = [
	("Th Kh Qh Ah Jh", "Royal Flush"),
	("Ts 9s 7s 8s 6s", "Straight Flush, six to ten"),
	("4c 3c 2c Ac 5c", "Straight Flush, ace to five"),
	("Ah Ac Ad As 9d", "Four of a Kind, aces"),
	("Ah Ac Ad As 3d", "Four of a Kind, aces"),
	("7h 7c 3d 3s 7d", "Full House, sevens full of threes"),
	("7h 7c 2d 2s 7d", "Full House, sevens full of twos"),
	("Ts 9s 3s 8s 6s", "Flush, ten high"),
	("Ts 9s 2s 8s 6s", "Flush, ten high"),
	("5s 6s 7s 8s 4c", "Straight, four to eight"),
	("5s 3s 2s As 4c", "Straight, ace to five"),
	("9h 8c 8d Ks Kd", "Two Pair, kings and eights"),
	("3h 8c 8d Ks Kd", "Two Pair, kings and eights"),
	("3h 6c 6d Ks Kd", "Two Pair, kings and sixes"),
	("6h 6c 2s Ks 2d", "Two Pair, sixes and twos"),
	("Jh Ac 3d 2s Jd", "Pair of jacks, ace kicker"),
	("Jh Kc 3d 2s Jd", "Pair of jacks, king kicker"),
	("9h Kc 3d 2s 9d", "Pair of nines, king kicker"),
	("6h 5c 7d Ks Ad", "High Card ace, king kicker"),
	("6h 2c 7d Ks Ad", "High Card ace, king kicker"),
	("4h 2c 7d Ks Ad", "High Card ace, king kicker"),
	("6h 2c 3d Ks Ad", "High Card ace, king kicker"),
	("5h 2c 3d 4s 7d", "High Card seven, five kicker"),
]
for hand, name in examples:
	print hand, " -> ", rankings.handrank_encoding_to_name(encode_hand(hand))
	try:
		assert(name == rankings.handrank_encoding_to_name(encode_hand(hand)))
	except:
		import pdb; pdb.set_trace()

examples2 = [
	("Td Kd Qd Ad Jd", "Royal Flush"),
	("Td 9d 7d 8d 6d", "Straight Flush, six to ten"),
	("4d 3d 2d Ad 5d", "Straight Flush, ace to five"),
	("Ah Ac Ad As 9c", "Four of a Kind, aces"),
	("Ah Ac Ad As 3c", "Four of a Kind, aces"),
	("7h 7c 3d 3s 7s", "Full House, sevens full of threes"),
	("7h 7c 2h 2c 7d", "Full House, sevens full of twos"),
	("Th 9h 3h 8h 6h", "Flush, ten high"),
	("Th 9h 2h 8h 6h", "Flush, ten high"),
	("5c 6s 7s 8s 4c", "Straight, four to eight"),
	("5c 3s 2s As 4c", "Straight, ace to five"),
	("9c 8c 8d Ks Kd", "Two Pair, kings and eights"),
	("3c 8c 8d Ks Kd", "Two Pair, kings and eights"),
	("3c 6c 6d Ks Kd", "Two Pair, kings and sixes"),
	("6c 6c 2s Ks 2d", "Two Pair, sixes and twos"),
	("Jc Ac 3d 2s Jd", "Pair of jacks, ace kicker"),
	("Jc Kc 3d 2s Jd", "Pair of jacks, king kicker"),
	("9c Kc 3d 2s 9d", "Pair of nines, king kicker"),
	("6c 5c 7d Ks Ad", "High Card ace, king kicker"),
	("6c 2c 7d Ks Ad", "High Card ace, king kicker"),
	("4c 2c 7d Ks Ad", "High Card ace, king kicker"),
	("6c 2c 3d Ks Ad", "High Card ace, king kicker"),
	("5c 2c 3d 4s 7d", "High Card seven, five kicker"),
]
for i, (hand1, _) in enumerate(examples):
	for j, (hand2, _) in enumerate(examples2):
		print hand1, " - ", hand2, " = ", compare_hands(hand1, hand2)
		if (i==j):
			assert(compare_hands(hand1, hand2) == 0)
		elif (i>j):
			assert(compare_hands(hand1, hand2) < 0)
			assert(compare_hands(hand2, hand1) > 0)
		else:
			assert(compare_hands(hand1, hand2) > 0)
			assert(compare_hands(hand2, hand1) < 0)

print "tests pass"
