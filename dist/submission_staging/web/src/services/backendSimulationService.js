import { BRIDGE_BASE_URL } from '../config/simulationMode'

export async function getBackendState() {
  const response = await fetch(`${BRIDGE_BASE_URL}/api/state`)

  if (!response.ok) {
    throw new Error(`Bridge returned ${response.status}`)
  }

  return response.json()
}

export async function emergencyStop() {
  const response = await fetch(`${BRIDGE_BASE_URL}/api/emergency-stop`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error(`E-STOP failed: ${response.status}`)
  }

  return response.json()
}

async function sendSimulationCommand(path, label) {
  const response = await fetch(`${BRIDGE_BASE_URL}${path}`, { method: 'POST' })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(`${label}: ${error.detail ?? response.status}`)
  }

  return response.json()
}

export function startBackendSimulation() {
  return sendSimulationCommand('/api/start', 'START')
}

export function pauseBackendSimulation() {
  return sendSimulationCommand('/api/pause', 'PAUSE')
}

export function nextBackendTick() {
  return sendSimulationCommand('/api/tick', 'NEXT TICK')
}

export async function emergencyRelease() {
  const response = await fetch(`${BRIDGE_BASE_URL}/api/emergency-release`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error(`E-STOP release failed: ${response.status}`)
  }

  return response.json()
}

export async function injectBackendFault(vehicleId, faultType) {
  const response = await fetch(`${BRIDGE_BASE_URL}/api/fault`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vehicleId, faultType }),
  })

  if (!response.ok) {
    throw new Error(`Fault injection failed: ${response.status}`)
  }

  return response.json()
}

export async function vehicleArrived(vehicleId, portId) {
  const response = await fetch(`${BRIDGE_BASE_URL}/api/vehicle-arrived`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vehicleId, portId }),
  })

  if (!response.ok) {
    throw new Error(`Vehicle arrival failed: ${response.status}`)
  }

  return response.json()
}

export async function loadScenario(scenario, vehicleId) {
  const response = await fetch(`${BRIDGE_BASE_URL}/api/scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario, vehicleId }),
  })

  if (!response.ok) {
    throw new Error(`Scenario load failed: ${response.status}`)
  }

  return response.json()
}

export async function resetBackendSimulation() {
  const response = await fetch(`${BRIDGE_BASE_URL}/api/reset`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error(`Reset failed: ${response.status}`)
  }

  return response.json()
}


export async function setBackendSpeed(speed) {
  const response = await fetch(`${BRIDGE_BASE_URL}/api/speed`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ speed }),
  })
  if (!response.ok) throw new Error(`SPEED failed: ${response.status}`)
  return response.json()
}
