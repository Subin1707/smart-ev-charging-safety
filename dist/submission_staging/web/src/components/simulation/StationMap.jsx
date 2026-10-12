import { useEffect, useState } from 'react'
import { MainRoad } from './MainRoad'
import { EntranceGate } from './EntranceGate'
import { InternalRoad } from './InternalRoad'
import { ChargingArea } from './ChargingArea'
import { WaitingArea } from './WaitingArea'
import { ExitGate } from './ExitGate'
import { ExitRoad } from './ExitRoad'
import { Vehicle } from './Vehicle'

export function StationMap({ running = false, speedMultiplier = 1, vehicles = [], backendVehicles = [], backendPorts = [], backendQueue = [], backendMode = false, updateVehicle, onVehicleArrived, addEvent, simulationKey, emergencyStop = false, selectedVehicleId, onSelectVehicle }) {
  const [mapElement, setMapElement] = useState(null)
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })
  const displayedVehicles = backendMode ? backendVehicles : vehicles
  const arrivingVehicle = displayedVehicles.find((vehicle) => vehicle.state === 'WAITING' && (vehicle.assignedPort ?? vehicle.targetPort) > 0)
  const gateOpen = (backendMode && running && Boolean(arrivingVehicle)) || displayedVehicles.some((vehicle) => ['AT_GATE', 'ENTERING', 'DRIVING_TO_PORT', 'PARKING'].includes(vehicle.state))
  const exitGateOpen = displayedVehicles.some((vehicle) => vehicle.state === 'DEPARTING')

  useEffect(() => {
    if (!mapElement) {
      return undefined
    }

    const updateDimensions = () => {
      const mapRect = mapElement.getBoundingClientRect()
      const ports = Array.from(mapElement.querySelectorAll('.charging-port')).map((port) => {
        const rect = port.getBoundingClientRect()
        return { x: rect.left - mapRect.left - mapElement.clientLeft + rect.width / 2 - 36,
          y: rect.top - mapRect.top - mapElement.clientTop + 30 }
      })
      setDimensions({ width: mapElement.clientWidth, height: mapElement.clientHeight, ports })
    }

    updateDimensions()
    const observer = new ResizeObserver(updateDimensions)
    observer.observe(mapElement)

    return () => observer.disconnect()
  }, [mapElement])

  return (
    <div className="station-map" ref={setMapElement}>
      <div className="station-title">SMART EV CHARGING STATION</div>
      <MainRoad />
      <EntranceGate open={gateOpen} />
      <InternalRoad />
      <ChargingArea vehicles={displayedVehicles} ports={backendMode ? backendPorts : []} />
      <WaitingArea queue={backendMode ? backendQueue : []} />
      <ExitRoad />
      <ExitGate open={exitGateOpen} />

      {displayedVehicles.filter((vehicle) => vehicle.state !== 'DEPARTED').map((vehicle, index) => (
        <Vehicle
          key={`${vehicle.id}-${simulationKey}-${vehicle.assignedPort}-${vehicle.state === 'DEPARTING' ? 'departure' : 'arrival'}`}
          vehicle={vehicle}
          backendMode={backendMode}
          index={index}
          running={running && (!backendMode || vehicle.state !== 'WAITING' || vehicle.id === arrivingVehicle?.id)}
          speedMultiplier={speedMultiplier}
          updateVehicle={backendMode ? undefined : updateVehicle}
          onVehicleArrived={backendMode ? onVehicleArrived : undefined}
          addEvent={addEvent}
          dimensions={dimensions}
          selected={selectedVehicleId === vehicle.id}
          onClick={() => onSelectVehicle?.(vehicle.id)}
        />
      ))}

      {emergencyStop && (
        <div className="emergency-overlay">
          <div>
            EMERGENCY STOP
            <span>ALL CHARGING POWER DISABLED</span>
          </div>
        </div>
      )}
    </div>
  )
}
