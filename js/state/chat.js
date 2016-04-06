var Immutable = require("immutable")

window.initial_state = Immutable.Map({
	users: {
		0: {
			id: 0,
			name: "dealer",
			status: "dealer",
			muted: false
		},
	},
	messages: [
		// userID, verbosity, message
		[0, 0, "Welcome to the Grater!"],
	],
	settings: {
		verbosity: 0,
		observers: true,
		announcements: true,
		chat: true,
	}
})

const users = (state = {}, action) => {
	switch (action.type) {
		case "ADD_USER":
			const u = action.user;
			return state.set(u.id, u)
		case "REMOVE_USER":
			return state.delete(action.id)
		case "TOGGLE_MUTE":
			return state.set(action.id, !state.muted)
		default:
			return state
	}
}