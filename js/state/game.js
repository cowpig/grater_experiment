import {Map} from 'immutable'
import {combineReducers} from 'redux'

// Global State
window.state = {
	// players: new Map({
	// 	1: {
	// 		id: 1,
	// 		avatar: 'cowpig',
	// 		stack: 1000000,
	// 		name: 'cowpig',
	// 	},
	// }),
	// board: new Map({
	// 	type: 'holdem',
	// 	cards: [],
	// 	pot: 0,
	// 	actionAt: 0,
	// 	holecards: {
	// 		1: ['Ts', 'Js'],
	// 	},
	// }),
	ball: new Map({
		x: 0,
		y: 200,
	}),
}
// animation transforms that should be merged with the state on every draw tick
window.animations = {
	// ball: {
	// 	start_time: new Date(),
	// 	step: (state, delta) => ({x: window.mouseX, y: window.mouseY}),
	// },
}

// Reducers
// const players = (state = new Map(), action) => {
// 	switch (action.type) {
// 		case 'ADD_PLAYER':
// 			const p = action.player;
// 			return state.set(p.id, p)
// 		case 'REMOVE_PLAYER':
// 			return state.delete(action.id)
// 		case 'SET_STACK':
// 			return state.set(action.id, action.stack)
// 		default:
// 			return state
// 	}
// }

// const board = (state = new Map(), action) => {
// 	switch (action.type) {
// 		case 'DEAL_TO_BOARD':
// 			return state.cards.concat(action.cards)
// 		default:
// 			return state
// 	}
// }

const ball = (state = new Map(), action) => {
	switch (action.type) {
		case 'MOVE':
			// instantaneously update the ball position to mouse's position on click
			return new Map({
				x: window.mouseX - 50,
				y: window.mouseY - 50,
			})

		case 'BOUNCE':
			return new Map({
				x: window.innerWidth * 0.5 - 50,
				y: window.innerHeight - 100,
			})
	}
	return state
}

function elastic(progress, x) {
  	const result = Math.pow(2, 10 * (progress-1)) * Math.cos(20*Math.PI*x/3*progress)
  	return result % 88
}


const ballAnimations = (animation = new Map(), action) => {
	switch (action.type) {
		case 'FOLLOW_MOUSE':
			return animation.start_time ? {} : {
				start_time: window.timestamp,
				step: (state, delta) => ({
					x: window.mouseX - 50,
					y: window.mouseY - 50,
				}),
			}
		case 'BOUNCE':
			return {
				start_time: window.timestamp,
				step: (state, delta) => ({
					x: elastic(delta / 1000, window.state.ball.x || 0),
					y: delta / 100 + window.state.ball.y || 0,
				})
			}
	}
	return animation
}

const stateReducers = combineReducers({
	// players,
	// board,
	ball,
})
const animationReducers = combineReducers({
	// players: playerAnimations,
	// board: boardAnimations,
	ball: ballAnimations,
})

// Actions are atomic and synchronous
const dispatch = (action) => {
	console.log(`[${action.type}] ${JSON.stringify(action)}`)
	window.state = stateReducers(window.state, action)
	window.animations = animationReducers(window.animations, action)
}

// Animations are computed functionally on each draw tick based on delta from a start-time
const computeAnimations = (state, animations, timestamp) => {
	// compute animations using step function based on state and start time

	const next_step = (new Map(animations)).filter(animation => animation.step).map((animation, scope) => {
		const current = state[scope]
		const delta = timestamp - animation.start_time
		return new Map(animation.step(current, delta))
	})

	// merge animation results into state tree
	return (new Map(state)).mergeDeep(next_step).toJS()
}

const drawing_runloop = (timestamp) => {
	window.timestamp = timestamp
    const current_tick = computeAnimations(window.state, window.animations, timestamp)
	render(current_tick)
	window.requestAnimationFrame(drawing_runloop)
}

const getDOM = (id) => document.getElementById(id)

// Take a state tree and render it to the DOM
const render = (state) => {
	getDOM('test').innerHTML = JSON.stringify(state, null, ' ')

	getDOM('ball').style.left = state.ball.x
	getDOM('ball').style.top = state.ball.y
}


// Event Listeners
const onClickText = (event) => {
	console.log('clicked text!', event)
	// thrash test
	// for (let i=0; i<100000; i++)
		// dispatch({type:'SET_HASH', hash: new Date()})
}
const onClickBall = (event) => {
	console.log('clicked ball!', event)
	// dispatch({type: 'BOUNCE'})
	dispatch({type: 'MOVE'})
	dispatch({type: 'FOLLOW_MOUSE'})
}

const onLoad = () => {
	getDOM('test').addEventListener('click', onClickText)
	getDOM('ball').addEventListener('click', onClickBall)
	drawing_runloop()
}
window.addEventListener('load', onLoad)
document.onmousemove = (event) => {
    window.mouseX = event.pageX
    window.mouseY = event.pageY
}
