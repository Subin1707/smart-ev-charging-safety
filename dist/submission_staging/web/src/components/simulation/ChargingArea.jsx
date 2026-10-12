import { ChargingPort } from './ChargingPort'

export function ChargingArea({ vehicles = [], ports = [] }) {
	const dockedVehicles = vehicles.filter((vehicle) => vehicle.connected && vehicle.state !== 'DEPARTED')

	return (
		<section className="charging-area">
			<div className="charging-area-title">CHARGING AREA</div>
			<div className="charging-grid">
				{[1, 2, 3, 4, 5].map((port) => (
					<ChargingPort
						key={port}
						port={port}
						vehicle={dockedVehicles.find((item) => (item.assignedPort ?? item.port) === port)}
						portData={ports.find((item) => item.id === port)}
					/>
				))}
			</div>
		</section>
	)
}
