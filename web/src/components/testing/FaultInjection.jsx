import { useState } from 'react'

export function FaultInjection({ vehicles = [], injectFault, backendMode = false, injectBackendFault }) {
  const [vehicleId, setVehicleId] = useState(vehicles[0]?.id ?? 'EV01')
  const [message, setMessage] = useState('')
  const [pending, setPending] = useState(false)
  const selectedVehicleId = vehicles.some((vehicle) => vehicle.id === vehicleId) ? vehicleId : vehicles[0]?.id ?? ''
  const [faultType, setFaultType] = useState('OVERHEAT')

  return (
    <section className="monitor-card">
      <h3>🧪 MÔ PHỎNG SỰ CỐ</h3>

      <label className="form-label" htmlFor="target-vehicle">XE CẦN KIỂM THỬ</label>
      <select id="target-vehicle" className="control-select" value={selectedVehicleId} onChange={(event) => setVehicleId(event.target.value)}>
        {vehicles.map((vehicle) => <option key={vehicle.id} value={vehicle.id}>{vehicle.id}</option>)}
      </select>

      <label className="form-label" htmlFor="fault-type">LOẠI SỰ CỐ</label>
      <select id="fault-type" className="control-select" value={faultType} onChange={(event) => setFaultType(event.target.value)}>
        <option value="OVERHEAT">Quá nhiệt</option>
        <option value="AUTH_FAILURE">Lỗi xác thực</option>
        <option value="UNEXPECTED_DISCONNECT">Mất kết nối đột ngột</option>
      </select>

      <button
        className="inject-button"
        type="button"
        disabled={pending || !selectedVehicleId}
        onClick={async () => {
          setPending(true)
          try {
            await injectFault(selectedVehicleId, faultType, backendMode, injectBackendFault)
            setMessage(`Fault injected: ${faultType} / ${selectedVehicleId}`)
          } catch (error) { setMessage(`Error: ${error.message}`) }
          finally { setPending(false) }
        }}
      >
        KÍCH HOẠT SỰ CỐ
      </button>
      {message && <p role="status">{message}</p>}
    </section>
  )
}
