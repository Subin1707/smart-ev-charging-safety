import { ShieldCheck, Siren, Zap } from 'lucide-react'

export function Header({
  tick = 0,
  totalPower: reportedPower = 0,
  vehicles = [],
  emergencyStop = false,
  onEmergencyStop,
  onEmergencyRelease,
  backendMode = false,
  backendConnected = false,
  backendError = null,
  telemetryLive = false,
}) {
  const activePorts = vehicles.filter((vehicle) => vehicle.state === 'CHARGING').length
  const totalPower = reportedPower

  return (
    <header className="app-header">
      <div className="brand-area">
        <div className="logo-icon"><Zap size={20} /></div>
        <div>
          <div className="brand-name">SMART EV</div>
          <div className="brand-subtitle">CHARGING SAFETY SIM</div>
        </div>
      </div>

      <div className="header-divider" />

      <HeaderMetric label="STATION" value="STATION-01" />

      <div className="power-header">
        <div className="metric-label">TOTAL POWER</div>
        <div className="power-value">{totalPower.toFixed(1)} / 100 kW</div>
        <div className="header-power-bar">
          <div className="header-power-fill" style={{ width: `${Math.min((totalPower / 100) * 100, 100)}%` }} />
        </div>
      </div>

      <HeaderMetric label="ACTIVE PORTS" value={`${activePorts} / 5`} />
      <HeaderMetric label="TICK" value={String(tick).padStart(3, '0')} />
      <HeaderMetric label="SIMULATION" value="00:00:00" />

      <div className="header-spacer" />
      <div className={`bridge-status ${backendMode ? (backendConnected ? 'connected' : 'disconnected') : 'mock'}`}>
        {backendMode ? (backendConnected ? 'C BRIDGE ONLINE' : 'C BRIDGE OFFLINE') : 'MOCK MODE'}
      </div>
      {backendMode && backendConnected && (
        <div className={`telemetry-status ${telemetryLive ? 'live' : 'stale'}`}>
          {telemetryLive ? 'TELEMETRY LIVE' : 'TELEMETRY STALE'}
        </div>
      )}
      <div className={`safe-status ${emergencyStop ? 'emergency-status' : ''}`}>
        {emergencyStop ? <><Siren size={14} /> EMERGENCY STOP</> : <><ShieldCheck size={14} /> SAFE</>}
      </div>
      <button className="estop-button" type="button" onClick={onEmergencyStop} disabled={emergencyStop}>
        <Siren size={14} /> E-STOP
      </button>
      {emergencyStop && (
        <button className="release-button" type="button" onClick={onEmergencyRelease}>
          RELEASE
        </button>
      )}
      {backendMode && backendError && (
        <div className="bridge-error" title={backendError}>
          BRIDGE ERROR
        </div>
      )}
    </header>
  )
}

function HeaderMetric({ label, value }) {
  return (
    <div className="header-metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  )
}