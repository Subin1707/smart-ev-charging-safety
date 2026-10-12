export function SafetyMonitor({ vehicles = [], emergencyStop = false, safetyChecks = null, totalPower = null }) {
  const activeVehicles = vehicles.filter((vehicle) => vehicle.connected).length
  const calculatedTotalPower = vehicles.reduce((sum, vehicle) => sum + (vehicle.allocatedPower || 0), 0)
  const rules = [
    { name: 'Authentication Safety', pass: vehicles.every((vehicle) => !vehicle.connected || vehicle.authenticated || ['PARKED', 'CONNECTING'].includes(vehicle.state)) },
    { name: 'Connection Safety', pass: vehicles.every((vehicle) => !vehicle.connected || vehicle.targetPort) },
    { name: 'SOC Bounds [0-100%]', pass: vehicles.every((vehicle) => vehicle.soc >= 0 && vehicle.soc <= 100) },
    { name: 'Station Power <= 100 kW', pass: (totalPower ?? calculatedTotalPower) <= 100.001 },
    { name: 'Fault -> Power = 0', pass: vehicles.every((vehicle) => !vehicle.fault || vehicle.allocatedPower === 0) },
    { name: 'Safety Trip -> Power = 0', pass: vehicles.every((vehicle) => !vehicle.safetyTrip || vehicle.allocatedPower === 0) },
    { name: 'Overheat -> Power = 0', pass: vehicles.every((vehicle) => !['OVERHEAT', 'CRITICAL_TEMPERATURE', 'THERMAL_RUNAWAY_RISK', 'FIRE_RISK'].includes(vehicle.thermalState) || vehicle.allocatedPower === 0) },
    { name: 'Thermal Runaway -> Isolated', pass: vehicles.every((vehicle) => vehicle.thermalState !== 'THERMAL_RUNAWAY_RISK' || vehicle.isolated) },
    { name: 'Fire Risk -> Emergency Stop', pass: vehicles.every((vehicle) => !vehicle.fireRisk) || emergencyStop },
    { name: 'Emergency -> Total Power = 0', pass: !emergencyStop || totalPower === 0 },
  ]
  const backendRules = safetyChecks?.map((check) => ({
    name: check.id,
    pass: check.status === 'PASS',
  }))
  const displayedRules = backendRules ?? rules
  const passedRules = displayedRules.filter((rule) => rule.pass).length

  return (
    <section className="monitor-card">
      <h3>✓ SAFETY MONITOR</h3>
      <div className="monitor-summary">
        <span>{passedRules}/{displayedRules.length} CHECKS PASS</span>
        <span>{activeVehicles} / 5 PORTS ACTIVE</span>
      </div>
      <div className="safety-rule-list">
        {displayedRules.map((rule) => (
          <div key={rule.name} className={`safety-rule ${rule.pass ? 'pass' : 'fail'}`}>
            {rule.pass ? '✓' : '✕'} {rule.name}
          </div>
        ))}
      </div>
    </section>
  )
}