import { useEffect, useRef } from 'react'

const LIFECYCLE_STEPS = {
  PARKED: {
    delay: 700,
    changes: { state: 'CONNECTING', connected: true },
    event: (vehicle) => `${vehicle.id} connecting to P${vehicle.targetPort}`,
  },
  CONNECTING: {
    delay: 700,
    changes: { state: 'AUTHENTICATING' },
    event: (vehicle) => `Authenticating ${vehicle.id}`,
  },
  AUTHENTICATING: {
    delay: 800,
    changes: { state: 'READY', authenticated: true },
    event: (vehicle) => `${vehicle.id} authentication passed`,
  },
  READY: {
    delay: 500,
    changes: { state: 'CHARGING', charging: true },
    event: (vehicle) => `${vehicle.id} charging started`,
  },
}

export function useChargingLifecycle({ vehicle, running, speedMultiplier = 1, updateVehicle, addEvent }) {
  const timerRef = useRef(null)

  useEffect(() => {
    const step = LIFECYCLE_STEPS[vehicle.state]

    if (!running || !step) {
      return undefined
    }

    timerRef.current = setTimeout(() => {
    if (vehicle.state === 'AUTHENTICATING' && vehicle.injectedFault === 'AUTH_FAILURE') {
      updateVehicle(vehicle.id, {
        state: 'FAULT',
        authenticated: false,
        charging: false,
        allocatedPower: 0,
        fault: 'AUTH_FAILURE',
        safetyTrip: true,
      })
      addEvent(`AUTH FAILURE: ${vehicle.id} rejected - charging prohibited`, 'SAFETY')
      return
    }

      updateVehicle(vehicle.id, step.changes)
      addEvent(step.event(vehicle), 'CHARGING')
    }, step.delay / speedMultiplier)

    return () => clearTimeout(timerRef.current)
  }, [vehicle, running, speedMultiplier, updateVehicle, addEvent])
}