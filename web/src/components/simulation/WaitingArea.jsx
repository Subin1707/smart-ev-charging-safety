export function WaitingArea({ queue = [] }) {
	return (
		<div className="waiting-area">
			<div className="waiting-title">WAITING AREA</div>
			<div className="waiting-slots">
				{queue.length > 0 ? queue.map((vehicleId, index) => (
					<div className="waiting-slot" key={vehicleId}>
						{index + 1}. {vehicleId}
					</div>
				)) : <div className="waiting-slot">EMPTY</div>}
			</div>
		</div>
	)
}
