import {store} from redux
import {request_missed_messages} from io.game

const game_controller = (msg) => {
	const state = store.getState()
	if (msg.lasthash != store.game.lasthash) {
		return request_missed_messages("game", store.game.lasthash)
	}

	state.game.lasthash = hash(msg)

	switch (msg.type) {
		case "deal":
			deal_cards(msg.cards)
		default:
			msg_error()
	}
}

const deal_cards = (cards) => {
	store.dispatch("DEAL_TO_BOARD", cards)
	if game.
}

