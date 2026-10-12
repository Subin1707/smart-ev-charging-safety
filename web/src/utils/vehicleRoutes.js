const STATION_LAYOUT = {
	roadTop: 62,
	roadHeight: 112,
	entranceTop: 181,
	chargingTop: 345,
	chargingInset: 0.05,
	chargingPaddingX: 32,
	chargingGap: 14,
	vehicleWidth: 46,
	vehicleHeight: 24,
}

export function getVehicleRoute(targetPort, { width, height, ports }) {
	if (!targetPort || !width || !height) {
		return [{ x: -80, y: 110, rotation: 0 }]
	}

	const chargingWidth = width * (1 - STATION_LAYOUT.chargingInset * 2)
	const gridWidth = chargingWidth - STATION_LAYOUT.chargingPaddingX * 2
	const portWidth = (gridWidth - STATION_LAYOUT.chargingGap * 4) / 5
	const portCenter = width * STATION_LAYOUT.chargingInset
		+ STATION_LAYOUT.chargingPaddingX
		+ (targetPort - 0.5) * portWidth
		+ (targetPort - 1) * STATION_LAYOUT.chargingGap

	const vehicleX = ports?.[targetPort - 1]?.x ?? portCenter - 36
	const roadY = height * 0.145 - 21
	const entranceX = width / 2 - STATION_LAYOUT.vehicleWidth / 2
	const entranceY = height * 0.32
	const chargingEntryY = height * 0.39 - 42
	const parkingY = ports?.[targetPort - 1]?.y ?? height * 0.4788 + 30
	const horizontalRotation = vehicleX >= entranceX ? 0 : 180

	return [
		{ x: -STATION_LAYOUT.vehicleWidth * 2, y: roadY, rotation: 0 },
		{ x: width * 0.25, y: roadY, rotation: 0 },
		{ x: entranceX, y: roadY, rotation: 0 },
		{ x: entranceX, y: entranceY, rotation: 90 },
		{ x: entranceX, y: chargingEntryY, rotation: 90 },
		{ x: vehicleX, y: chargingEntryY, rotation: horizontalRotation },
		{ x: vehicleX, y: parkingY, rotation: 0 },
	]
}

export function getVehicleDepartureRoute(targetPort, { width, height, ports }) {
	if (!targetPort || !width || !height) {
		return [{ x: width / 2, y: height + 80, rotation: 90 }]
	}

	const chargingWidth = width * (1 - STATION_LAYOUT.chargingInset * 2)
	const gridWidth = chargingWidth - STATION_LAYOUT.chargingPaddingX * 2
	const portWidth = (gridWidth - STATION_LAYOUT.chargingGap * 4) / 5
	const portCenter = width * STATION_LAYOUT.chargingInset
		+ STATION_LAYOUT.chargingPaddingX
		+ (targetPort - 0.5) * portWidth
		+ (targetPort - 1) * STATION_LAYOUT.chargingGap
	const vehicleX = ports?.[targetPort - 1]?.x ?? portCenter - 36
	const parkingY = ports?.[targetPort - 1]?.y ?? height * 0.4788 + 30
	const exitLaneY = Math.min(height - 66, parkingY + 120)
	const exitLaneX = width * 0.82

	return [
		{ x: vehicleX, y: parkingY, rotation: 0 },
		{ x: vehicleX, y: exitLaneY, rotation: 90 },
		{ x: exitLaneX, y: exitLaneY, rotation: 0 },
		{ x: width + 100, y: exitLaneY, rotation: 0 },
	]
}

