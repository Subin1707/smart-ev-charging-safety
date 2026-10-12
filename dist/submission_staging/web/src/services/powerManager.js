export const STATION_MAX_POWER = 100

export function allocatePower(vehicles, emergencyStop = false) {
  if (emergencyStop) {
    return vehicles.map((vehicle) => ({
      ...vehicle,
      allocatedPower: 0,
      charging: false,
    }))
  }

  const chargingVehicles = vehicles.filter((vehicle) => (
    vehicle.state === 'CHARGING'
    && vehicle.authenticated
    && vehicle.connected
    && !vehicle.fault
    && !vehicle.safetyTrip
  ))

  const totalRequested = chargingVehicles.reduce(
    (sum, vehicle) => sum + vehicle.requestedPower,
    0,
  )
  const ratio = totalRequested > STATION_MAX_POWER
    ? STATION_MAX_POWER / totalRequested
    : 1

  return vehicles.map((vehicle) => {
    const isCharging = chargingVehicles.some((item) => item.id === vehicle.id)

    return {
      ...vehicle,
      allocatedPower: isCharging
        ? Number((vehicle.requestedPower * ratio).toFixed(2))
        : 0,
    }
  })
}

export function getTotalPower(vehicles) {
  return Number(
    vehicles.reduce((sum, vehicle) => sum + (vehicle.allocatedPower || 0), 0).toFixed(2),
  )
}