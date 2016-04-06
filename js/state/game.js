import {Map} from "immutable"
import {combineReducers} from "redux"

window.next_actions = []
window.state = {
	players: new Map({
		1: {
			id: 1, 
			avatar: 'cowpig',
			stack: 1000000,
			name: 'cowpig',
		}
	}),
	board: new Map({
		type: "holdem",
		cards: [],
		pot: 0,
		actionAt: 0,
		holecards: {
			1: ['Ts', 'Js']
		},
	}),
	ball: new Map({
		x: 0,
		y: 200,
		animation: {
			x: 0,
			y: 200,
			start_time: 0,
			f: (state, timestamp) => (state)
		}
	}),
	lasthash: null,
	timestamp: 0
}
animations = {
	ball: {
		x: 0,
		x: 200,
		start_time: 0,
		f: (state, current_state, timestamp) => state
	}
}


const players = (state = new Map(), action) => {
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

const board = (state = new Map(), action) => {
	switch (action.type) {
		case "DEAL_TO_BOARD":
			return state.cards.concat(action.cards)
		default:
			return state
	}
}

const lasthash = (state = new Map(), action) => {
	switch (action.type) {
		case "SET_HASH":
			return action.hash
		default:
			return state
	}
}


const ball = (state = new Map(), action) => {
	switch (action.type) {
		case "MOVE":
			const old_pos = state.toJS()
			const new_pos = {x: old_pos.x + action.x, y: old_pos.y + action.y}

			setTimeout(animateBall.bind(this, old_pos, new_pos), 10)

			return new Map(new_pos)
		default:
			return state
	}
}

const timestamp = (state = new Map(), action) => {
	if (action.type === "SET_TIMESTAMP") 
		return action.timestamp
	return state
}

const run_reducers = combineReducers({players, board, lasthash, timestamp, ball})

const dispatch = (action) => {
	console.log(action)
	window.state = run_reducers(window.state, action)
}

const computeAnimations = (state, timestamp) => {
	return (new Map(state)).map(values =>)
}

const draw = (timestamp) => {
	// console.log(timestamp)
	// apply the redux composed function

	// decide how to deal with animation

	// call all the appropriate view functions...
	// for (let action of window.next_actions) {
	// 	window.state = run_reducers(window.state, action)
	// }
	// window.next_actions = []

	// dispatch({type: "SET_TIMESTAMP", timestamp})
    window.state = computeAnimations(window.state, timestamp)
	render(window.state)
	window.requestAnimationFrame(draw)
}

const render = (state) => {
	// console.log(state)
	window.document.getElementById("test").innerHTML = JSON.stringify(
					state, null, " ")

	window.document.getElementById("ball").style.left = state.ball.get('x')
	window.document.getElementById("ball").style.top = state.ball.get('y')
}


const onClickTest = (event) => {
	console.log("click!")
	for (let i=0; i<100000; i++){
		dispatch({type:"SET_HASH", hash:new Date()})
	}
}


const onClickBall = (event) => {
	dispatch({type:"MOVE", x:100, y:100})
}

const ready = () => {
	window.document.getElementById("test").addEventListener("click", onClickTest)

	window.document.getElementById("ball").addEventListener("click", onClickBall)

	// setInterval(onClickTest, 1000)
	draw(0)
}


window.addEventListener("load", ready)
