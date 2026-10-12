import { useState } from 'react'

const SCENARIOS = [
	['NORMAL', 'Sạc bình thường'],
	['OVERHEAT', 'Quá nhiệt'],
	['CRITICAL_TEMPERATURE', 'Nhiệt độ nguy hiểm'],
	['THERMAL_RUNAWAY', 'Nguy cơ mất kiểm soát nhiệt'],
	['FIRE_RISK', 'Nguy cơ cháy'],
	['AUTH_FAILURE', 'Lỗi xác thực'],
	['UNEXPECTED_DISCONNECT', 'Mất kết nối đột ngột'],
	['POWER_OVERLOAD', 'Quá tải công suất'],
	['EMERGENCY_STOP', 'Dừng khẩn cấp'],
	['MIXED', 'Kết hợp nhiều sự cố'],
]

const scenarioLabel = (value) => SCENARIOS.find(([code]) => code === value)?.[1] ?? value

export function ScenarioSelector({ vehicles = [], scenario, loadScenario }) {
	const [selectedScenario, setSelectedScenario] = useState('NORMAL')
	const [vehicleId, setVehicleId] = useState(vehicles[0]?.id ?? 'EV01')
	const [message, setMessage] = useState('')

	const selectedVehicleId = vehicles.some((vehicle) => vehicle.id === vehicleId) ? vehicleId : vehicles[0]?.id ?? ''
    const [pending, setPending] = useState(false)
    const submit = async () => {
        setPending(true)
        try {
            await loadScenario(selectedScenario, selectedVehicleId)
            setMessage(`Scenario applied: ${scenarioLabel(selectedScenario)} / ${selectedVehicleId}`)
        } catch (error) {
            setMessage(`Error: ${error.message}`)
        } finally { setPending(false) }
    }

	return (
		<section className="monitor-card">
			<h3>NẠP KỊCH BẢN KIỂM THỬ</h3>
			<label className="form-label" htmlFor="scenario-select">KỊCH BẢN</label>
			<select id="scenario-select" className="control-select" value={selectedScenario} onChange={(event) => setSelectedScenario(event.target.value)}>
				{SCENARIOS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
			</select>
			<label className="form-label" htmlFor="scenario-vehicle">XE ĐIỆN</label>
			<select id="scenario-vehicle" className="control-select" value={vehicles.some((vehicle) => vehicle.id === vehicleId) ? vehicleId : vehicles[0]?.id ?? ''} onChange={(event) => setVehicleId(event.target.value)}>
				{vehicles.map((vehicle) => <option key={vehicle.id} value={vehicle.id}>{vehicle.id}</option>)}
			</select>
			<button className="inject-button" type="button" disabled={pending || !selectedVehicleId} onClick={submit}>
				NẠP KỊCH BẢN
			</button>
			{message && <p className="scenario-status">{message}</p>}
			{scenario?.status === 'LOADED' && <p className="scenario-status">{scenarioLabel(scenario.name)} / {scenario.vehicleId} — Sẵn sàng</p>}
			{scenario?.status === 'TRIGGERED' && <p className="scenario-status">{scenarioLabel(scenario.name)} — Đã kích hoạt</p>}
		</section>
	)
}
