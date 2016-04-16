import {Map} from 'immutable'
import {combineReducers} from 'redux'
import m from 'mithril'

///////////
// STATE //

window.state = {
	players: {
		1: {
			id: 1,
			avatar: 'cowpig',
			stack: 10866,
			name: 'cowpig',
		},
		10: {
			id: 10,
			avatar: 'clown',
			stack: 100,
			name: 'AJFenix',
		},
		11: {
			id: 11,
			avatar: 'ninja',
			stack: 120,
			name: 'MagicNinja',
		},
	},
	board: {
		type: 'holdem',
		top: "10%",
		left: 0,
		height: window.innerWidth * 0.5,
		width: window.innerWidth,
		sitting: [1, null, 10, null, null, null, null, 11],
		button_idx: 0,
		pot: 0,
		actionAt: 0,
		cards: {
			community: [],
			1: ['Ts', 'Js'],
			10: ['X', 'X'],
			11: ['X', 'X']
		},
		cards_dealing: {},
	},
}

window.animations = {}


//////////////
// DISPATCH //

// animation transforms that should be merged with the state on every draw tick
// window.animations = {
// 	switch (action.type) {
// 		// case 'DEAL_CARDS':
// 		// 	for (target of state.action.cards_dealing) {

// 		// 	}
// 		default: 
// 			return state
// 	}
// }


const players = (state = new Map(), action) => {
	switch (action.type) {
		case 'ADD_PLAYER':
			const p = action.player;
			return state.set(p.id, p)
		case 'REMOVE_PLAYER':
			return state.delete(action.id)
		case 'SET_STACK':
			return state.set(action.id, action.stack)
		default:
			return state
	}
}

const board = (state = new Map(), action) => {
	switch (action.type) {
		case 'DEAL_CARDS':
			return state.cards.concat(action.cards)
		default:
			return state
	}
}

///////////
// VIEWS //

const view = (state) => {	
	return view_funcs.wrapper(state, [
		view_funcs.table(state)
	]);
}

// view functions
const view_funcs = {
	wrapper: (state, children) => {
		return m('div', {id: 'wrapper'}, children)
	},
	table: (state, children) => {
		const SEATBOX_SIZE_RATIO = 0.135

		const table = {
			class: 'table',
			style: {
				top: state.board.top,
				left: state.board.left,
				height: state.board.height,
				width: state.board.width,
				position: 'absolute',
			}
		}
		const felt = {class: 'felt'}
		const positions = player_positions(state)
		
		const seatbox_width = state.board.width * SEATBOX_SIZE_RATIO
		const seatbox_height = seatbox_width * 2/3
		const section_height = seatbox_height / 4

		let seatboxes = []

		positions.map((pt, i) => {
			const seatbox = {
				class: "seatbox",
				style: {
					height: seatbox_height,
					width: seatbox_width,
					top : pt.y - 0.5*seatbox_height,
					left: pt.x - 0.5*seatbox_width,
				},
			}
			const pid = state.board.sitting[i]
			const plyr = state.players[pid]

			const fontsize = section_height / 2
			const seat = {
				class : 'seat' + (plyr ? '' : ' hoveropacity'),
				style : {
					top : section_height*2,
					left: 0,
					height: section_height*2,
					width: seatbox_width,
					'font-size': fontsize, 					
				}
			}
			let label = null
			if (plyr) {
				label = [
					m('div', {class:'white opaque'}, plyr.name), 
					m('div', {class:'white opaque'}, plyr.stack)
				]
			} else {
				label = [m('div', {
						class:'white opaque', 
						style: {
							'position' : 'relative',
							'font-size' : fontsize*1.5,
							top: (section_height*2 - fontsize*1.5)/2.2
						}
					}, 'SIT HERE')]
			}

			// TODO: div that holds cards held by players
			const cardbox = {}
			const cards = null

			seatboxes.push(m('div', seatbox, [
					m('div', seat, label),
					m('div', cardbox, cards)
			]))
		})
		seatboxes.push(m('div', felt))
		if (children) seatboxes += children
		return m('div', table, seatboxes)
	},
}
// view helper functions
const player_positions = (state) => {
	const n_players = state.board.sitting.length
	const angle = 2 * Math.PI / n_players
	const center = {
		x: state.board.width / 2,
		y: state.board.height / 2
	}
	return state.board.sitting.map((item, i) => {
		let theta;
		if (n_players%2) {
			theta = angle * (i + 0.5)
		} else {
			theta = angle * i
		}
		theta = angle * i + Math.PI / 2 // player 1 at bottom
		return add_pts(scale_pt(
			ellipse(center.y, center.x, theta), 0.82), center)
	})
} 

const ellipse = (height, width, angle) => {
	return {x: width * Math.cos(angle),
			y: height * Math.sin(angle)}
}
const add_pts = (pt1, pt2) => {
	return {x:pt1.x + pt2.x, y:pt1.y + pt2.y}
}
const scale_pt = (pt, scalar) => {
	return {x: pt.x * scalar, y: pt.y*scalar}
}

/////////////
// GENERIC //

const stateReducers = combineReducers({
	players,
	board,
})
const animationReducers = combineReducers({
	// players: playerAnimations,
	// board: boardAnimations,
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

const draw_loop = (timestamp) => {
	window.timestamp = timestamp
	const current_state = computeAnimations(window.state, window.animations, timestamp)
	m.render(mount_point, view(current_state))
	window.requestAnimationFrame(draw_loop)
}

const onLoad = () => {
	draw_loop()
}
window.addEventListener('load', onLoad)
