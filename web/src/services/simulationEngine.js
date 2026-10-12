import { allocatePower, getTotalPower } from './powerManager'

export const OVERHEAT_LIMIT = 60
export const THERMAL_THRESHOLDS = {
  WARNING: 50,
  OVERHEAT: 60,
  CRITICAL: 70,
  THERMAL_RUNAWAY: 80,
  FIRE_RISK: 90,
}
const SOC_SIMULATION_FACTOR = 0.35

export function processSimulationTick(state) {
  if (!state.running || state.emergencyStop) {
    return state
  }

  const nextTick = state.tick + 1
  const generatedEvents = []
  let vehicles = state.vehicles.map((vehicle) => ({ ...vehicle }))

  vehicles = processFaults(vehicles, generatedEvents, nextTick)
  vehicles = progressThermalScenario(vehicles, state.thermalScenario, nextTick)
  const thermalResult = processThermalSafety(vehicles, generatedEvents, nextTick)
  vehicles = thermalResult.vehicles
  const emergencyStop = state.emergencyStop || thermalResult.fireRisk
  vehicles = allocatePower(vehicles, emergencyStop)
  vehicles = processCharging(vehicles, generatedEvents, nextTick)

  return {
    ...state,
    tick: nextTick,
    running: emergencyStop ? false : state.running,
    emergencyStop,
    vehicles,
    totalPower: getTotalPower(vehicles),
    events: [...state.events, ...generatedEvents],
  }
}

function processFaults(vehicles, generatedEvents, tick) {
  return vehicles.map((vehicle) => {
    if (vehicle.injectedFault === 'OVERHEAT' && vehicle.state === 'CHARGING') {
      const temperature = vehicle.temperature + 8

      if (temperature >= OVERHEAT_LIMIT) {
        generatedEvents.push({
          tick,
          type: 'SAFETY',
          message: `SAFETY TRIP: ${vehicle.id} overheat detected - power cut to 0 kW`,
        })

        return {
          ...vehicle,
          temperature,
          state: 'FAULT',
          fault: 'OVERHEAT',
          injectedFault: null,
          safetyTrip: true,
          charging: false,
          allocatedPower: 0,
        }
      }

      return { ...vehicle, temperature }
    }

    if (vehicle.injectedFault === 'UNEXPECTED_DISCONNECT' && vehicle.state === 'CHARGING') {
      generatedEvents.push({
        tick,
        type: 'SAFETY',
        message: `SAFETY TRIP: ${vehicle.id} unexpected disconnect - power cut to 0 kW`,
      })

      return {
        ...vehicle,
        state: 'FAULT',
        fault: 'UNEXPECTED_DISCONNECT',
        injectedFault: null,
        safetyTrip: true,
        connected: false,
        charging: false,
        allocatedPower: 0,
      }
    }

    return vehicle
  })
}

function processCharging(vehicles, generatedEvents, tick) {
  return vehicles.map((vehicle) => {
    if (
      vehicle.state !== 'CHARGING'
      || vehicle.allocatedPower <= 0
      || vehicle.fault
      || !vehicle.connected
      || !vehicle.authenticated
    ) {
      return vehicle
    }

    const socIncrease = (vehicle.allocatedPower / 22) * SOC_SIMULATION_FACTOR
    const newSoc = Math.min(vehicle.targetSoc, vehicle.soc + socIncrease)

    if (newSoc >= vehicle.targetSoc) {
      generatedEvents.push({
        tick,
        type: 'CHARGING',
        message: `${vehicle.id} reached target SOC ${vehicle.targetSoc}%`,
      })

      return {
        ...vehicle,
        soc: vehicle.targetSoc,
        state: 'DEPARTING',
        charging: false,
        allocatedPower: 0,
      }
    }

    return {
      ...vehicle,
      soc: Number(newSoc.toFixed(2)),
      charging: true,
    }
  })
}

function progressThermalScenario(vehicles, scenario, tick) {
  if (!scenario || tick < scenario.startTick) {
    return vehicles
  }

  return vehicles.map((vehicle) => {
    if (vehicle.id !== scenario.vehicleId || vehicle.fireRisk || vehicle.isolated) {
      return vehicle
    }

    return {
      ...vehicle,
      temperature: Number((vehicle.temperature + scenario.temperatureStep).toFixed(1)),
    }
  })
}

function getThermalState(temperature) {
  if (temperature >= THERMAL_THRESHOLDS.FIRE_RISK) return 'FIRE_RISK'
  if (temperature >= THERMAL_THRESHOLDS.THERMAL_RUNAWAY) return 'THERMAL_RUNAWAY_RISK'
  if (temperature >= THERMAL_THRESHOLDS.CRITICAL) return 'CRITICAL_TEMPERATURE'
  if (temperature >= THERMAL_THRESHOLDS.OVERHEAT) return 'OVERHEAT'
  if (temperature >= THERMAL_THRESHOLDS.WARNING) return 'TEMP_WARNING'
  return 'NORMAL'
}

function processThermalSafety(vehicles, generatedEvents, tick) {
  let fireRisk = false
  const nextVehicles = vehicles.map((vehicle) => {
    const thermalState = getThermalState(vehicle.temperature)
    const previousState = vehicle.thermalState ?? 'NORMAL'

    if (thermalState === previousState) {
      return { ...vehicle, thermalState }
    }

    if (thermalState !== 'NORMAL') {
      generatedEvents.push({
        tick,
        type: thermalState === 'TEMP_WARNING' ? 'WARNING' : 'SAFETY',
        message: `${vehicle.id} ${thermalState} at ${vehicle.temperature.toFixed(1)} C`,
      })
    }

    if (thermalState === 'OVERHEAT') {
      return {
        ...vehicle,
        thermalState,
        charging: false,
        allocatedPower: 0,
        fault: vehicle.fault ?? 'OVERHEAT',
      }
    }

    if (thermalState === 'CRITICAL_TEMPERATURE' || thermalState === 'THERMAL_RUNAWAY_RISK') {
      return {
        ...vehicle,
        thermalState,
        state: 'FAULT',
        charging: false,
        allocatedPower: 0,
        fault: 'THERMAL_SAFETY',
        safetyTrip: true,
        isolated: thermalState === 'THERMAL_RUNAWAY_RISK',
      }
    }

    if (thermalState === 'FIRE_RISK') {
      fireRisk = true
      return {
        ...vehicle,
        thermalState,
        fireRisk: true,
        isolated: true,
        state: 'FAULT',
        charging: false,
        allocatedPower: 0,
        fault: 'FIRE_RISK',
        safetyTrip: true,
      }
    }

    return { ...vehicle, thermalState }
  })

  if (fireRisk) {
    generatedEvents.push({
      tick,
      type: 'EMERGENCY',
      message: 'FIRE_RISK detected - station emergency stop activated',
    })
  }

  return { vehicles: nextVehicles, fireRisk }
}