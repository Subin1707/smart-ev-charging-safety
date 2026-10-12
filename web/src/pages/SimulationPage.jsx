import { useCallback, useEffect, useReducer, useState } from 'react'
import { Header } from '../components/layout/Header'
import { StationMap } from '../components/simulation/StationMap'
import { SafetyMonitor } from '../components/monitoring/SafetyMonitor'
import { VehicleInspector } from '../components/monitoring/VehicleInspector'
import { EventTimeline } from '../components/monitoring/EventTimeline'
import { FaultInjection } from '../components/testing/FaultInjection'
import { ScenarioSelector } from '../components/testing/ScenarioSelector'
import { BottomControl } from '../components/layout/BottomControl'
import {
  createInitialSimulationState,
  simulationReducer,
} from '../store/simulationReducer'
import { SIMULATION_MODE } from '../config/simulationMode'
import { useBackendSimulation } from '../hooks/useBackendSimulation'
import {
  emergencyRelease as sendEmergencyRelease,
  emergencyStop as sendEmergencyStop,
  injectBackendFault,
  nextBackendTick,
  pauseBackendSimulation,
  resetBackendSimulation,
  startBackendSimulation,
  setBackendSpeed,
  vehicleArrived,
  loadScenario,
} from '../services/backendSimulationService'

export function SimulationPage() {
  const [simulation, dispatch] = useReducer(
    simulationReducer,
    undefined,
    createInitialSimulationState,
  )
  const [controlError, setControlError] = useState(null)
  const [speedMultiplier, setSpeedMultiplier] = useState(1)
  const [selectedVehicleId, setSelectedVehicleId] = useState(null)
  const {
    running,
    emergencyStop,
    tick,
    totalPower,
    vehicles,
    events,
    simulationKey,
  } = simulation
  const backendMode = SIMULATION_MODE === 'backend'
  const {
    state: backendState,
    connected: backendConnected,
    error: backendError,
  } = useBackendSimulation(backendMode)

  const displayTick = backendMode ? backendState?.tick ?? 0 : tick
  const displayRunning = backendMode
    ? backendState?.simulation?.status === 'RUNNING'
    : running
  const displayTotalPower = backendMode ? backendState?.station?.totalPower ?? 0 : totalPower
  const displayEmergency = backendMode
    ? backendState?.station?.emergency ?? false
    : emergencyStop
  const displayVehicles = backendMode && backendState ? backendState.vehicles : vehicles
  const selectedVehicle = displayVehicles.find((vehicle) => vehicle.id === selectedVehicleId)
  const displayPorts = backendMode && backendState ? backendState.ports : []
  const displayQueue = backendMode && backendState ? backendState.queue.vehicles : []
  const displayScenario = backendMode && backendState ? backendState.scenario : null
  const displayEvents = backendMode && backendState ? [...backendState.events, ...events.filter((event) => event.type === 'ERROR')] : events
  const displaySafetyChecks = backendMode && backendState ? backendState.safetyChecks : null
  const telemetryAgeMs = backendState?.telemetry?.ageMs
  const telemetryLive = backendConnected && (telemetryAgeMs == null || telemetryAgeMs <= 3000)

  const addEvent = useCallback((message, type = 'INFO') => {
    dispatch({ type: 'ADD_EVENT', event: { type, message } })
  }, [])

  const updateVehicle = useCallback((vehicleId, changes) => {
    dispatch({ type: 'UPDATE_VEHICLE', vehicleId, changes })
  }, [])

  const injectFault = useCallback(async (vehicleId, faultType, useBackend, backendFault) => {
    if (useBackend) {
      try {
        await backendFault(vehicleId, faultType)
        if (!displayRunning) await nextBackendTick()
      } catch (error) {
      setControlError(error.message)
        dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
        throw error
      }
      return
    }

    dispatch({ type: 'INJECT_FAULT', vehicleId, faultType })
  }, [displayRunning])

  useEffect(() => {
    if (backendMode || !running) {
      return undefined
    }

    const interval = setInterval(() => {
      dispatch({ type: 'TICK' })
    }, 1000 / speedMultiplier)

    return () => clearInterval(interval)
  }, [backendMode, running, speedMultiplier])

  const activateEmergencyStop = useCallback(async () => {
    if (!backendMode) {
      dispatch({ type: 'E_STOP' })
      return
    }

    try {
      await sendEmergencyStop()
    } catch (error) {
      setControlError(error.message)
      dispatch({
        type: 'ADD_EVENT',
        event: { type: 'ERROR', message: error.message },
      })
    }
  }, [backendMode])

  const releaseEmergencyStop = useCallback(async () => {
    if (!backendMode) {
      dispatch({ type: 'RELEASE_E_STOP' })
      return
    }

    try {
      await sendEmergencyRelease()
    } catch (error) {
      setControlError(error.message)
      dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
    }
  }, [backendMode])

  const resetSimulation = useCallback(async () => {
    if (!backendMode) {
      dispatch({ type: 'RESET' })
      return
    }

    try {
      await resetBackendSimulation()
      dispatch({ type: 'RESET' })
      setControlError(null)
    } catch (error) {
      setControlError(error.message)
      dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
    }
  }, [backendMode])

  const changeSpeed = useCallback(async (speed) => {
    try {
      if (backendMode) await setBackendSpeed(speed)
      setControlError(null)
      setSpeedMultiplier(speed)
    } catch (error) {
      setControlError(error.message)
      dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
    }
  }, [backendMode])

  const sendStart = useCallback(async () => {
    if (!backendMode) {
      dispatch({ type: 'START' })
      return
    }

    try {
      await startBackendSimulation()
      setControlError(null)
    } catch (error) {
      setControlError(error.message)
      dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
    }
  }, [backendMode])

  const sendPause = useCallback(async () => {
    if (!backendMode) {
      dispatch({ type: 'PAUSE' })
      return
    }

    try {
      await pauseBackendSimulation()
      setControlError(null)
    } catch (error) {
      setControlError(error.message)
      dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
    }
  }, [backendMode])

  const sendNextTick = useCallback(async () => {
    if (!backendMode) {
      dispatch({ type: 'TICK' })
      return
    }

    try {
      await nextBackendTick()
      setControlError(null)
    } catch (error) {
      setControlError(error.message)
      dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
    }
  }, [backendMode])

  const sendVehicleArrived = useCallback(async (vehicleId, portId) => {
    try {
      await vehicleArrived(vehicleId, portId)
    } catch (error) {
      setControlError(error.message)
      dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
    }
  }, [])

  const sendLoadScenario = useCallback(async (scenario, vehicleId) => {
    if (!backendMode) {
      if (scenario === 'NORMAL') {
        dispatch({ type: 'ADD_EVENT', event: { type: 'SYSTEM', message: `Normal scenario selected for ${vehicleId}` } })
        return
      }

      if (scenario === 'EMERGENCY_STOP') {
        dispatch({ type: 'E_STOP' })
        return
      }

      if (['OVERHEAT', 'CRITICAL_TEMPERATURE', 'THERMAL_RUNAWAY', 'FIRE_RISK'].includes(scenario)) {
        dispatch({
          type: 'LOAD_THERMAL_SCENARIO',
          scenario,
          vehicleId,
        })
        return
      }

      if (scenario === 'POWER_OVERLOAD') {
        vehicles.forEach((vehicle) => {
          dispatch({ type: 'UPDATE_VEHICLE', vehicleId: vehicle.id, changes: { requestedPower: 30 } })
        })
        dispatch({ type: 'ADD_EVENT', event: { type: 'SAFETY', message: 'POWER OVERLOAD scenario loaded - requests raised to 30 kW' } })
        return
      }

      if (scenario === 'MIXED') {
        dispatch({ type: 'INJECT_FAULT', vehicleId, faultType: 'OVERHEAT' })
        const secondVehicle = vehicles.find((vehicle) => vehicle.id !== vehicleId)
        if (secondVehicle) {
          dispatch({ type: 'INJECT_FAULT', vehicleId: secondVehicle.id, faultType: 'AUTH_FAILURE' })
        }
        return
      }

      dispatch({ type: 'INJECT_FAULT', vehicleId, faultType: scenario })
      return
    }

    try {
      await loadScenario(scenario, vehicleId)
    } catch (error) {
      setControlError(error.message)
      dispatch({ type: 'ADD_EVENT', event: { type: 'ERROR', message: error.message } })
      throw error
    }
  }, [backendMode, vehicles, displayRunning])

  return (
    <div className="simulation-page">
      <Header
        tick={displayTick}
        totalPower={displayTotalPower}
        vehicles={displayVehicles}
        emergencyStop={displayEmergency}
        onEmergencyStop={activateEmergencyStop}
        onEmergencyRelease={releaseEmergencyStop}
        backendMode={backendMode}
        backendConnected={backendConnected}
        backendError={backendError}
        telemetryLive={telemetryLive}
      />

      <main className="simulation-main">
        <section className="station-section">
          <StationMap
            running={displayRunning}
            speedMultiplier={speedMultiplier}
            vehicles={vehicles}
            backendVehicles={displayVehicles}
            backendPorts={displayPorts}
            backendQueue={displayQueue}
            backendMode={backendMode}
            updateVehicle={updateVehicle}
            onVehicleArrived={sendVehicleArrived}
            addEvent={addEvent}
            simulationKey={simulationKey}
            emergencyStop={emergencyStop}
            selectedVehicleId={selectedVehicleId}
            onSelectVehicle={setSelectedVehicleId}
          />
        </section>

        <aside className="monitor-panel">
          <SafetyMonitor
            vehicles={displayVehicles}
            emergencyStop={displayEmergency}
            safetyChecks={displaySafetyChecks}
            totalPower={displayTotalPower}
          />
          <VehicleInspector
            vehicle={selectedVehicle}
            onClose={() => setSelectedVehicleId(null)}
          />
          <EventTimeline events={displayEvents} />
          <FaultInjection
            vehicles={displayVehicles}
            injectFault={injectFault}
            backendMode={backendMode}
            injectBackendFault={injectBackendFault}
          />
          <ScenarioSelector
            vehicles={displayVehicles}
            scenario={displayScenario}
            backendMode={backendMode}
            loadScenario={sendLoadScenario}
          />
        </aside>
      </main>

      <BottomControl
        running={displayRunning}
        speedMultiplier={speedMultiplier}
        controlError={controlError}
        onSpeedChange={changeSpeed}
        onStart={sendStart}
        onPause={sendPause}
        onNextTick={sendNextTick}
        onReset={resetSimulation}
      />
    </div>
  )
}