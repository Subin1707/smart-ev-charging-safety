export function MainRoad() {
	return (
		<div className="main-road">
			<div className="road-header">
				<span className="road-label">MAIN ROAD</span>
				<span className="road-status">ACCESS ROUTE <i /></span>
			</div>
			<div className="road-lane road-lane-top" />
			<div className="road-center-line" />
			<div className="road-lane road-lane-bottom" />
			<div className="road-reflector reflector-one" />
			<div className="road-reflector reflector-two" />
			<div className="road-reflector reflector-three" />
			<div className="road-direction">→ → → → → → →</div>
		</div>
	)
}
