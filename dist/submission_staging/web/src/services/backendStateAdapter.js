export function adaptBackendState(data) {
  return {
    tick: data?.tick ?? 0,
    simulation: {
      status: data?.simulation?.status ?? 'PAUSED',
    },
    station: {
      totalPower: data?.station?.totalPower ?? 0,
      maxPower: data?.station?.maxPower ?? 100,
      emergency: data?.station?.emergency ?? false,
    },
    vehicles: Array.isArray(data?.vehicles)
      ? data.vehicles.map((vehicle) => {
        const connected = Boolean(vehicle.connected)
        const showChargingData = connected
        const targetPort = vehicle.assignedPort ?? vehicle.port ?? null
        return {
          ...vehicle,
          connected,
          port: connected ? (vehicle.port ?? null) : null,
          assignedPort: connected ? (vehicle.assignedPort ?? null) : null,
          targetPort,
          requestedPower: showChargingData ? (vehicle.requestedPower ?? vehicle.maxChargingPower ?? 0) : 0,
          allocatedPower: showChargingData ? (vehicle.allocatedPower ?? 0) : 0,
          showChargingData,
          thermalState: showChargingData ? (vehicle.thermalState ?? (vehicle.temperature >= 90 ? 'FIRE_RISK' : vehicle.temperature >= 80 ? 'THERMAL_RUNAWAY_RISK' : vehicle.temperature >= 70 ? 'CRITICAL_TEMPERATURE' : vehicle.temperature >= 60 ? 'OVERHEAT' : 'NORMAL')) : 'NOT_CONNECTED',
          fireRisk: showChargingData ? (vehicle.fireRisk ?? false) : false,
          isolated: showChargingData ? (vehicle.isolated ?? false) : false,
        }
      })
      : [],
    ports: Array.isArray(data?.ports) ? data.ports : [],
    queue: {
      count: data?.queue?.count ?? 0,
      vehicles: Array.isArray(data?.queue?.vehicles) ? data.queue.vehicles : [],
    },
    scenario: data?.scenario ?? {
      name: 'NORMAL', vehicleId: '', status: 'IDLE', triggered: false,
    },
    events: Array.isArray(data?.events) ? data.events : [],
    safetyChecks: Array.isArray(data?.safetyChecks) ? data.safetyChecks : [],
    telemetry: {
      generatedAtMs: data?.generatedAtMs ?? null,
      ageMs: data?.telemetryAgeMs ?? null,
    },
  }
}

export function mapCStateToVisualState(cState) {
  switch (cState) {
    case 'WAITING':
      return 'ARRIVING'
    case 'CONNECTED':
    case 'AUTHENTICATED':
    case 'READY':
    case 'CHARGING':
    case 'STOPPED':
    case 'FAULT':
      return 'PARKED'
    default:
      return 'WAITING'
  }
}
