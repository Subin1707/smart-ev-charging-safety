export function ExitRoad() {
	return (
		<>
			<div className="exit-lane" aria-hidden="true" />
			<div className="exit-road" aria-label="Outbound exit lane">
				<div className="exit-road-edge top" />
				<div className="exit-road-edge bottom" />
				<div className="exit-road-center" />
				<div className="exit-road-label">OUTBOUND LANE</div>
				<div className="exit-road-arrows">→ → → → →</div>
			</div>
		</>
	)
}