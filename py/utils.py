def rotate_to_idx(lst, idx):
	indices = range(idx, len(lst))
	indices += range(0, idx)
	return [lst[i] for i in indices]
	
def rotate_iter(seq, idx):
	n = len(seq)
	for i in xrange(n):
		yield seq[(idx + i) % n]
