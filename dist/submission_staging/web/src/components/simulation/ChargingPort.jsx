export function ChargingPort({ port, vehicle, portData }) {
	const portState = portData?.state ?? getPortState(vehicle)
	const power = portData?.power ?? vehicle?.allocatedPower ?? 0
	const soc = Number(vehicle?.soc)
	const hasSoc = Number.isFinite(soc)
	const connected = Boolean(vehicle?.connected) && portState !== 'IDLE'
	const vehicleVisible = connected

	return (
		<div className={`charging-port port-${port} port-state-${portState.toLowerCase()} ${connected ? 'port-connected' : ''} ${vehicle?.state === 'FAULT' ? 'port-fault' : ''}`}>
			<div className="port-top">
				<span className="port-name">P{port}</span>
				<span className="port-state">{portState}</span>
			</div>

			<div className="charger-unit">⚡</div>
			{portState === 'CHARGING' && (
				<div className="energy-flow" aria-label="Energy flowing">
					<span />
					<span />
					<span />
				</div>
			)}

			<div className="parking-slot">
				<div className="parking-line top" />
				<div className="parking-line left" />
				<div className="parking-line right" />
				{vehicleVisible ? (
					<>
						<div className="port-vehicle-data">
							<strong>{vehicle?.id ?? portData.vehicleId}</strong>
							<div className="soc-row"><span>SOC</span><span>{connected && hasSoc ? `${soc.toFixed(1)}%` : '--'}</span></div>
							<div className="soc-bar"><div className="soc-fill" style={{ width: `${connected && hasSoc ? Math.max(0, Math.min(100, soc)) : 0}%` }} /></div>
							<div className="power-row"><span>REQUEST</span><strong>{connected ? (vehicle?.requestedPower ?? 0) : '--'} kW</strong></div>
							<div className="power-row"><span>ALLOCATED</span><strong>{connected ? power.toFixed(1) : '--'} kW</strong></div>
							<div className="temperature-row"><span>TEMP</span><strong>{Number.isFinite(Number(vehicle?.temperature)) ? Number(vehicle.temperature).toFixed(1) : '--'} °C</strong></div>
							{connected && vehicle?.thermalState && vehicle.thermalState !== 'NORMAL' && (
								<div className="thermal-state-row">{vehicle.thermalState.replaceAll('_', ' ')}</div>
							)}
						</div>
					</>
				) : (portState === 'RESERVED' ? 'RESERVED' : 'AVAILABLE')}
			</div>
		</div>
	)
}

function getPortState(vehicle) {
	if (!vehicle) return 'IDLE'

	switch (vehicle.state) {
		case 'PARKED':
		case 'CONNECTING':
		case 'AUTHENTICATING':
			return 'CONNECTED'
		case 'READY':
			return 'READY'
		case 'CHARGING':
			return 'CHARGING'
		case 'FAULT':
			return 'FAULT'
		case 'STOPPED':
			return 'STOPPED'
		default:
			return 'CONNECTED'
	}
}
