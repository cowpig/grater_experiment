
data = {
	"game_hashes" : []
}

const request_missed_messages = (lasthash) =>
	// it was just a late (duplicate) message
	if (data.game_hashes.indexOf(lasthash) > -1) return null;

	// socket call to server with last hash
	// 