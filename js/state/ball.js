import {Map} from 'immutable'
import {combineReducers} from 'redux'
import m from 'mithril'

// Global State
window.state = {

	ball: new Map({
		x: 0,
		y: 200,
		flipped: true
	}),
}

const ball = (state = new Map(), action) => {
	switch (action.type) {
		case 'MOVE':
			// instantaneously update the ball position to mouse's position on click
			return state.merge(new Map({
				x: window.mouseX - 50,
				y: window.mouseY - 50,
			}))

		case 'BOUNCE':
			return state.merge(new Map({
				x: window.innerWidth * 0.5 - 50,
				y: window.innerHeight - 100,
			}))
		case 'FLIP':
			return state.set('flipped', !state.get('flipped'))
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

const getDOM = (id) => document.getElementById(id)

const mount_point = getDOM('mount_point')

const drawing_runloop = (timestamp) => {
	window.timestamp = timestamp
	const current_state = computeAnimations(window.state, window.animations, timestamp)
	m.render(mount_point, view(current_state))
	window.requestAnimationFrame(drawing_runloop)
}



const view = (state) => {
	return view_funcs.wrapper(state, [
		view_funcs.ball(state)
	]);
}

// view functions
const view_funcs = {
	wrapper: (state, children) => {
		return m('div', {id: 'wrapper'}, children)
	},
	ball: (state, children) => {
		const me = state.ball
		const attrs = {
			id: 'ball',
			onclick: onClickBall,
			style: {
				top: me.flipped ? me.x : me.y ,
				left: me.flipped ? me.y : me.x,
			}
		}
		return m('div', attrs, children)
	},
}

// Take a state tree and render it to the DOM
// const render = (state) => {
// 	getDOM('test').innerHTML = JSON.stringify(state, null, ' ')

// 	getDOM('ball').style.left = state.ball.x
// 	getDOM('ball').style.top = state.ball.y
// }


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
	// dispatch({type: 'FOLLOW_MOUSE'})
	dispatch({type: 'FLIP'})
}

const onLoad = () => {
	// getDOM('test').addEventListener('click', onClickText)
	// getDOM('ball').addEventListener('click', onClickBall)
	dispatch({type: 'FOLLOW_MOUSE'})
	drawing_runloop()
}
window.addEventListener('load', onLoad)

document.onmousemove = (event) => {
    window.mouseX = event.pageX
    window.mouseY = event.pageY
}
