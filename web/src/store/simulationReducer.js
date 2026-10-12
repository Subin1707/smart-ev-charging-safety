import { mockVehicles } from '../data/mockVehicles'
import { getTotalPower } from '../services/powerManager'
import { processSimulationTick } from '../services/simulationEngine'

export function createInitialSimulationState() {
  return {
    running: false,
    emergencyStop: false,
    tick: 0,
    totalPower: 0,
    thermalScenario: null,
    vehicles: mockVehicles.map((vehicle) => ({ ...vehicle })),
    events: [{ tick: 0, type: 'SYSTEM', message: 'Simulation ready' }],
    simulationKey: 0,
  }
}

export function simulationReducer(state, action) {
  switch (action.type) {
    case 'START':
      return state.emergencyStop ? state : { ...state, running: true }

    case 'PAUSE':
      return { ...state, running: false }

    case 'TICK':
      return processSimulationTick(state)

    case 'RESET':
      return {
        ...createInitialSimulationState(),
        simulationKey: state.simulationKey + 1,
      }

    case 'UPDATE_VEHICLE': {
      const vehicles = state.vehicles.map((vehicle) => (
        vehicle.id === action.vehicleId
          ? { ...vehicle, ...action.changes }
          : vehicle
      ))

      return { ...state, vehicles, totalPower: getTotalPower(vehicles) }
    }

    case 'INJECT_FAULT':
      return {
        ...state,
        vehicles: state.vehicles.map((vehicle) => (
          vehicle.id === action.vehicleId
            ? { ...vehicle, injectedFault: action.faultType }
            : vehicle
        )),
        events: [
          ...state.events,
          {
            tick: state.tick,
            type: 'FAULT',
            message: `${action.faultType} injected into ${action.vehicleId}`,
          },
        ],
      }

    case 'LOAD_THERMAL_SCENARIO': {
      const vehicle = state.vehicles.find((item) => item.id === action.vehicleId)
      const startTemperature = action.scenario === 'FIRE_RISK'
        ? 85
        : action.scenario === 'CRITICAL_TEMPERATURE'
          ? 65
          : 45

      return {
        ...state,
        thermalScenario: {
          type: action.scenario,
          vehicleId: action.vehicleId,
          startTick: state.tick + 1,
          temperatureStep: action.scenario === 'FIRE_RISK' ? 5 : 8,
        },
        vehicles: state.vehicles.map((item) => (
          item.id === action.vehicleId
            ? {
              ...item,
              temperature: startTemperature,
              thermalState: 'NORMAL',
              fireRisk: false,
              isolated: false,
              fault: null,
              safetyTrip: false,
            }
            : item
        )),
        events: [
          ...state.events,
          {
            tick: state.tick,
            type: 'SYSTEM',
            message: `${action.scenario} thermal scenario loaded for ${vehicle?.id ?? action.vehicleId}`,
          },
        ],
      }
    }

    case 'ADD_EVENT':
      return {
        ...state,
        events: [...state.events, { tick: state.tick, ...action.event }],
      }

    case 'E_STOP':
      return activateEmergencyStop(state)

    case 'RELEASE_E_STOP':
      return {
        ...state,
        emergencyStop: false,
        events: [
          ...state.events,
          { tick: state.tick, type: 'SYSTEM', message: 'Emergency stop released' },
        ],
      }

    default:
      return state
  }
}

function activateEmergencyStop(state) {
  const vehicles = state.vehicles.map((vehicle) => {
    const active = vehicle.state === 'CHARGING' || vehicle.state === 'READY'

    return {
      ...vehicle,
      charging: false,
      allocatedPower: 0,
      state: active ? 'STOPPED' : vehicle.state,
    }
  })

  return {
    ...state,
    running: false,
    emergencyStop: true,
    totalPower: 0,
    vehicles,
    events: [
      ...state.events,
      {
        tick: state.tick,
        type: 'EMERGENCY',
        message: 'EMERGENCY STOP ACTIVATED - all charging power cut',
      },
    ],
  }
}