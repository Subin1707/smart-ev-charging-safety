export function VehicleInspector({ vehicle, onClose }) {
	if (!vehicle) {
		return (
			<section className="monitor-card vehicle-inspector vehicle-inspector-empty">
				<div className="vehicle-inspector-heading">
					<span className="vehicle-inspector-eyebrow">VEHICLE INSPECTOR</span>
					<h3>NO VEHICLE SELECTED</h3>
				</div>
				<p>Click a vehicle on the station map to inspect its live state.</p>
			</section>
		)
	}

	const assignedPort = vehicle.assignedPort ?? vehicle.targetPort
	const thermalState = vehicle.thermalState ?? 'NORMAL'
	const showChargingData = vehicle.showChargingData ?? vehicle.connected
	const isFault = Boolean(
		vehicle.fault || vehicle.safetyTrip || vehicle.fireRisk ||
		['CRITICAL', 'CRITICAL_TEMPERATURE', 'THERMAL_RUNAWAY_RISK', 'FIRE_RISK'].includes(thermalState),
	)
	const displayState = isFault ? 'FAULT' : (vehicle.state ?? 'UNKNOWN')

	return (
		<section className={`monitor-card vehicle-inspector ${isFault ? 'vehicle-inspector-fault' : ''}`}>
			<div className="vehicle-inspector-header">
				<div>
					<span className="vehicle-inspector-eyebrow">VEHICLE INSPECTOR</span>
					<h3>{vehicle.id}</h3>
				</div>
				<button className="vehicle-inspector-close" type="button" onClick={onClose} aria-label="Close vehicle inspector">×</button>
			</div>

			<div className="vehicle-inspector-state">{displayState}</div>

			{showChargingData ? (
				<>
			<InspectorSection title="BATTERY">
				<DetailRow label="SOC" value={`${vehicle.soc ?? 0}%`} />
				<DetailRow label="Temperature" value={`${vehicle.temperature ?? 0} °C`} />
				<DetailRow label="Thermal State" value={thermalState.replaceAll('_', ' ')} />
			</InspectorSection>

			<InspectorSection title="CHARGING">
				<DetailRow label="Assigned Port" value={assignedPort != null ? `P${assignedPort}` : '--'} />
				<DetailRow label="Requested Power" value={`${vehicle.requestedPower ?? 0} kW`} />
				<DetailRow label="Allocated Power" value={`${isFault ? 0 : vehicle.allocatedPower ?? 0} kW`} />
			</InspectorSection>
				</>
			) : (
				<div className="vehicle-inspector-alert">
					<strong>NOT CONNECTED</strong>
					<span>Charging data is hidden until the vehicle connects to a station port.</span>
				</div>
			)}

			<InspectorSection title="CONNECTION">
				<DetailRow label="Connected" value={vehicle.connected ? 'YES' : 'NO'} />
				<DetailRow label="Authenticated" value={vehicle.authenticated ? 'YES' : 'NO'} />
			</InspectorSection>

			<InspectorSection title="SAFETY">
				<DetailRow label="Fault" value={vehicle.fault ?? 'NONE'} />
				<DetailRow label="Isolation" value={vehicle.isolated ? 'ACTIVE' : 'NONE'} />
				<DetailRow label="Fire Risk" value={vehicle.fireRisk ? 'ACTIVE' : 'NONE'} />
			</InspectorSection>

			{isFault && (
				<div className="vehicle-inspector-alert">
					<strong>⚠ {thermalState.replaceAll('_', ' ')}</strong>
					<span>✓ Charging stopped</span>
					<span>{vehicle.isolated ? '✓ Port isolated' : '✓ Charging power disabled'}</span>
				</div>
			)}
		</section>
	)
}

function InspectorSection({ title, children }) {
	return (
		<div className="vehicle-inspector-section">
			<h4>{title}</h4>
			{children}
		</div>
	)
}

function DetailRow({ label, value }) {
	return (
		<div className="vehicle-detail-row">
			<span>{label}</span>
			<strong>{value}</strong>
		</div>
	)
}
