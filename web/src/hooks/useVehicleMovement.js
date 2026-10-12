import { useEffect, useMemo, useState } from 'react'
import { getVehicleDepartureRoute, getVehicleRoute } from '../utils/vehicleRoutes'

export function useVehicleMovement({
	targetPort,
	departing = false,
	running,
	delay = 0,
	speed = 1200,
	dimensions = { width: 0, height: 0 },
}) {
	const { width, height, ports } = dimensions
	const arrivalRoute = useMemo(
		() => getVehicleRoute(targetPort, { width, height, ports }),
		[targetPort, width, height, ports],
	)
	const departureRoute = useMemo(
		() => getVehicleDepartureRoute(targetPort, { width, height, ports }),
		[targetPort, width, height, ports],
	)
	const route = departing ? departureRoute : arrivalRoute
	const ready = width > 0 && height > 0
	const [pointIndex, setPointIndex] = useState(0)

	useEffect(() => {
		setPointIndex(0)
	}, [departing, targetPort, width, height])

	useEffect(() => {
		if (!ready || !running || departing || pointIndex !== 0) {
			return
		}

		const startTimer = setTimeout(() => {
			setPointIndex(1)
		}, delay)

		return () => clearTimeout(startTimer)
	}, [ready, running, departing, delay, pointIndex])

	useEffect(() => {
		if (!ready || !running || !departing || pointIndex !== 0 || route.length < 2) {
			return undefined
		}

		const departureTimer = setTimeout(() => {
			setPointIndex((current) => (current >= route.length - 1 ? 1 : current + 1))
		}, 250)

		return () => clearTimeout(departureTimer)
	}, [ready, running, departing, pointIndex, route])

	useEffect(() => {
		if (!ready || !running || pointIndex === 0 || pointIndex >= route.length - 1) {
			return undefined
		}

		const timer = setTimeout(() => {
			setPointIndex((current) => current + 1)
		}, speed)

		return () => clearTimeout(timer)
	}, [ready, pointIndex, running, route, speed])

	const point = route[pointIndex] ?? { x: -100, y: 100, rotation: 0 }
	const finished = ready && pointIndex === route.length - 1

	return { point, finished, pointIndex }
}
