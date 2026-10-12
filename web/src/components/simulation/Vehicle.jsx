import { useEffect, useRef } from 'react'
import { useVehicleMovement } from '../../hooks/useVehicleMovement'
import { useChargingLifecycle } from '../../hooks/useChargingLifecycle'

export function Vehicle({ vehicle, backendMode = false, running, speedMultiplier = 1, index, updateVehicle, onVehicleArrived, addEvent, dimensions, selected = false, onClick }) {
	const thermalState = vehicle.thermalState ?? 'NORMAL'
	const thermalClass = thermalState.toLowerCase()
	const departing = vehicle.state === 'DEPARTING'
	const docked = ['CONNECTED', 'AUTHENTICATED', 'FAULT', 'STOPPED', 'PARKED', 'CONNECTING', 'AUTHENTICATING', 'READY', 'CHARGING'].includes(vehicle.state)
	const { point, finished, pointIndex } = useVehicleMovement({
		targetPort: vehicle.assignedPort ?? vehicle.targetPort ?? vehicle.port,
		departing,
		running: running && !docked && vehicle.state !== 'DEPARTED',
		delay: departing || backendMode ? 0 : (index * 8000) / speedMultiplier,
		speed: departing ? 1700 / speedMultiplier : 1200 / speedMultiplier,
		dimensions,
	})
	const portPoint = dimensions.ports?.[(vehicle.assignedPort ?? vehicle.targetPort ?? vehicle.port) - 1]
	const displayPoint = docked && !departing && portPoint ? { ...portPoint, rotation: 0 } : point
	const completedRef = useRef(false)
	const previousStateRef = useRef(vehicle.state)

	useChargingLifecycle({ vehicle, running: running && !backendMode, speedMultiplier, updateVehicle, addEvent })

	useEffect(() => {
		if (!running || departing || !updateVehicle || finished) {
			return
		}

		let state = 'ARRIVING'
		if (pointIndex >= 2) state = 'AT_GATE'
		if (pointIndex >= 3) state = 'ENTERING'
		if (pointIndex >= 4) state = 'DRIVING_TO_PORT'
		if (pointIndex >= 5) state = 'PARKING'
		if (finished) state = 'PARKED'

		updateVehicle(vehicle.id, { state })

		if (state !== previousStateRef.current) {
			addEvent?.(`${vehicle.id} -> ${state}`, 'VEHICLE')
			previousStateRef.current = state
		}
	}, [pointIndex, finished, running, departing, vehicle.id, updateVehicle, addEvent])

	useEffect(() => {
		if (!departing || !finished || !updateVehicle) {
			return
		}

		updateVehicle(vehicle.id, {
			state: 'DEPARTED',
			connected: false,
			assignedPort: null,
			targetPort: null,
			charging: false,
			allocatedPower: 0,
		})
		addEvent?.(`${vehicle.id} exited after reaching target SOC`, 'VEHICLE')
	}, [departing, finished, vehicle.id, updateVehicle, addEvent])

	useEffect(() => {
		if (departing || docked || !finished || completedRef.current || (!updateVehicle && !onVehicleArrived)) {
			return
		}

		completedRef.current = true
		const arrivalPort = vehicle.assignedPort ?? vehicle.targetPort
		if (onVehicleArrived && arrivalPort != null && vehicle.state === 'WAITING') {
			onVehicleArrived(vehicle.id, arrivalPort)
		}
		updateVehicle?.(vehicle.id, { state: 'PARKED', connected: true })
		addEvent?.(`${vehicle.id} connected to P${vehicle.assignedPort ?? vehicle.targetPort}`, 'VEHICLE')
	}, [departing, docked, finished, vehicle.id, vehicle.assignedPort, vehicle.targetPort, vehicle.state, updateVehicle, onVehicleArrived, addEvent])

	if (vehicle.state === 'DEPARTED' || (!docked && !departing && pointIndex === 0)) {
		return null
	}

	return (
		<div
			className={`map-vehicle ${docked ? 'vehicle-docked' : ''} ${running ? 'vehicle-moving' : ''} ${selected ? 'vehicle-selected' : ''} thermal-${thermalClass}`}
			style={{
				transform: `translate(${displayPoint.x}px, ${displayPoint.y}px)`,
                transitionDuration: `${1200 / speedMultiplier}ms`,
			}}
			onClick={(event) => {
				event.stopPropagation()
				onClick?.()
			}}
			onKeyDown={(event) => {
				if (event.key === 'Enter' || event.key === ' ') {
					event.preventDefault()
					onClick?.()
				}
			}}
			role="button"
			tabIndex={0}
		>
			<div className="vehicle-shape">
				<svg className="vehicle-illustration" viewBox="0 0 96 54" role="img" aria-label={`${vehicle.id} electric vehicle`}>
					<defs>
						<linearGradient id={`body-${vehicle.id}`} x1="0" y1="0" x2="1" y2="1">
							<stop offset="0" stopColor="#f4f7fb" />
							<stop offset="0.3" stopColor="#aeb9c8" />
							<stop offset="0.65" stopColor="#596675" />
							<stop offset="1" stopColor="#1b242e" />
						</linearGradient>
						<linearGradient id={`glass-${vehicle.id}`} x1="0" y1="0" x2="0.8" y2="1">
							<stop offset="0" stopColor="#f8fcff" stopOpacity="0.98" />
							<stop offset="0.34" stopColor="#9fb9cc" stopOpacity="0.86" />
							<stop offset="1" stopColor="#192b3a" stopOpacity="0.99" />
						</linearGradient>
						<radialGradient id={`wheel-${vehicle.id}`} cx="35%" cy="28%">
							<stop offset="0" stopColor="#ffffff" />
							<stop offset="0.2" stopColor="#bbc6d2" />
							<stop offset="0.24" stopColor="#101b20" />
							<stop offset="1" stopColor="#050a0d" />
						</radialGradient>
					</defs>
					<ellipse cx="48" cy="48" rx="40" ry="4" fill="#020713" opacity="0.55" />
					<path d="M8 39l3-5 12-4 12-13c4-5 10-8 17-8h10c8 0 14 3 19 9l7 10 7 3 2 7-4 4H10z" fill="#071638" opacity="0.9" transform="translate(0 3)" />
					<path className="vehicle-svg-body" d="M6 35c2-5 8-8 19-10l10-10c5-5 12-7 20-7h7c7 0 13 2 18 7l4 7 10 3c4 1 6 4 7 8l-2 5H8z" fill={`url(#body-${vehicle.id})`} />
					<path d="M25 28l10-13c4-5 10-7 17-7h7c7 0 12 2 16 7l5 8-8 5z" fill={`url(#glass-${vehicle.id})`} stroke="#eef5fb" strokeOpacity="0.82" strokeWidth="0.8" />
					<path d="M51 9l-2 19M60 9l5 18M35 28h57" fill="none" stroke="#ffffff" strokeOpacity="0.55" strokeWidth="0.75" />
					<path d="M14 31h77M18 37h70" fill="none" stroke="#e9eef3" strokeOpacity="0.72" strokeWidth="0.9" />
					<path d="M19 34h67" fill="none" stroke="#f4f7fa" strokeWidth="1.3" />
					<path d="M38 30v7M66 29v8" fill="none" stroke="#3d4855" strokeWidth="0.9" />
					<rect x="47" y="31" width="6" height="1.2" rx="0.6" fill="#ffffff" />
					<path d="M79 26l10 2 3 4-2 4H78z" fill="#f9ffff" />
					<path d="M7 26l8-3 6 2-2 4-10 2z" fill="#d72f3c" />
					<path d="M85 20l6 3-2 3-6-1z" fill="#ffffff" />
					<path d="M11 20h15l-2 2H10z" fill="#e8f4ff" />
					<path d="M86 26h8v10h-8z" fill="#111b25" stroke="#e7edf2" strokeWidth="0.6" />
					<path d="M88 27v8M90 27v8M92 27v8" stroke="#c7d0d8" strokeWidth="0.65" />
					<circle cx="91" cy="23" r="2.2" fill="none" stroke="#f5f7f9" strokeWidth="0.75" />
					<path d="M25 29v7M43 29v7M66 28v8" fill="none" stroke="#3d4855" strokeWidth="0.7" />
					<rect x="31" y="30" width="5" height="1.1" rx="0.55" fill="#f4f7f9" />
					<rect x="49" y="30" width="5" height="1.1" rx="0.55" fill="#f4f7f9" />
					<path d="M14 28c5-2 10-3 16-3M70 25c7 0 13 1 19 4" fill="none" stroke="#ffffff" strokeOpacity="0.6" strokeWidth="0.7" />
					<path d="M76 36h16l-2 3H77z" fill="#26323e" stroke="#bfc9d2" strokeWidth="0.45" />
					<path d="M81 37h7" stroke="#f0f4f7" strokeWidth="0.55" />
					<path d="M91 31l4 1-1 3h-3z" fill="#f9ffff" />
					<path d="M8 33l5-2 4 1-1 2H8z" fill="#cfd9e2" opacity="0.8" />
					<path d="M13 35c2-5 6-7 12-7s10 2 12 7M63 35c2-5 6-7 12-7s10 2 12 7" fill="none" stroke="#151b22" strokeWidth="4.2" />
					<g className="vehicle-wheel-graphic">
						<circle cx="25" cy="40" r="8.2" fill={`url(#wheel-${vehicle.id})`} stroke="#f7f9fc" strokeWidth="1.3" />
						<path d="M25 33v14M18 40h14M20 35l10 10M30 35L20 45" stroke="#d5dbe2" strokeWidth="0.85" />
						<circle cx="25" cy="40" r="2.5" fill="#b7c0ca" stroke="#ffffff" strokeWidth="0.7" />
					</g>
					<g className="vehicle-wheel-graphic">
						<circle cx="75" cy="40" r="8.2" fill={`url(#wheel-${vehicle.id})`} stroke="#f7f9fc" strokeWidth="1.3" />
						<path d="M75 33v14M68 40h14M70 35l10 10M80 35L70 45" stroke="#d5dbe2" strokeWidth="0.85" />
						<circle cx="75" cy="40" r="2.5" fill="#b7c0ca" stroke="#ffffff" strokeWidth="0.7" />
					</g>
					<path d="M11 35h11M79 35h10" stroke="#ffffff" strokeOpacity="0.9" strokeWidth="1.3" strokeLinecap="round" />
				</svg>
			</div>
			{thermalState !== 'NORMAL' && (
				<div className={`vehicle-thermal-badge ${vehicle.fireRisk ? 'critical' : ''}`}>
					{vehicle.fireRisk ? 'FIRE RISK' : thermalState.replaceAll('_', ' ')}
				</div>
			)}
			<div className="vehicle-label">
				{vehicle.id}
				<span>{vehicle.state}</span>
			</div>
		</div>
	)
}
