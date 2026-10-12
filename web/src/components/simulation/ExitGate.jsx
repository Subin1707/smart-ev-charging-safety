export function ExitGate({ open = false }) {
	return (
		<div className={`exit-gate ${open ? 'exit-gate-open' : ''}`}>
			<div className="exit-gate-label">EXIT GATE</div>
			<div className="exit-gate-frame">
				<div className="exit-gate-post" />
				<div className="exit-barrier" />
				<div className="exit-gate-post" />
			</div>
			<div className="exit-direction">OUT →</div>
		</div>
	)
}
