var Immutable = require("immutable")

window.initial_state = Immutable.Map({
	players: {
		1: {
			id: 1, 
			avatar: 'cowpig',
			stack: 1000000,
			name: 'cowpig',
		}
	},
	board: {
		type: "holdem",
		cards: [],
		pot: 0,
		actionAt: 0,
		holecards: {
			1: ['Ts', 'Js']
		},
	},
	lasthash: null,
})

const players = (state = {}, action) => {
	switch (action.type) {
		case "ADD_PLAYER":
			const p = action.player;
			return state.set(p.id, p)
		case "REMOVE_PLAYER":
			return state.delete(action.id)
		case "SET_STACK":
			return state.set(action.id, action.stack)
		default:
			return state
	}
}

const game = (state = {}, action) => {
	switch (action.type) {
		case "DEAL_TO_BOARD":
			return state.board.concat(action.cards)
		case "SET_HASH":
			return state.set("lasthash", action.hash)
		default:
			return state
	}
}
