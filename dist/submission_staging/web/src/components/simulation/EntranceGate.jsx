export function EntranceGate({ open = false }) {
	return (
		<div className="entrance-zone">
			<div className="gate-label">ENTRANCE</div>
			<div className={`gate ${open ? 'gate-open' : ''}`}>
				<div className="gate-post" />
				<div className="barrier-arm" />
				<div className="gate-post" />
			</div>
			<div className="entrance-arrow">↓</div>
		</div>
	)
}
