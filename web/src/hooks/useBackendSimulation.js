import { useEffect, useState } from 'react'
import { getBackendState } from '../services/backendSimulationService'
import { adaptBackendState } from '../services/backendStateAdapter'

export function useBackendSimulation(enabled) {
  const [state, setState] = useState(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!enabled) {
      return undefined
    }

    let cancelled = false

    async function loadState() {
      try {
        const data = await getBackendState()

        if (cancelled) {
          return
        }

        setState(adaptBackendState(data))
        setConnected(true)
        setError(null)
      } catch (requestError) {
        if (cancelled) {
          return
        }

        setConnected(false)
        setError(requestError.message)
      }
    }

    loadState()
    const timer = setInterval(loadState, 750)

    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [enabled])

  return { state, connected, error }
}
