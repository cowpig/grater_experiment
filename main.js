

window.initial_state = {
	players: {
		0: {
			id: 0, 
			avatar: 'cowpig',
			stack: 1000000,
			name: 'cowpig',
		}
	},
	game: {
		board: null,
		pot: 0,
		actionAt: 0,
	}
}

const players = (state = {}, action) => {
	switch (action.type) {
		case "ADD_PLAYER":
			const p = action.player;
			let new_state = {...state}
			new_state[p.id] = p
			return new_state
		default:
			return state
	}
}
window.players = players