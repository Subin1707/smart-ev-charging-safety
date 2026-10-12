import { useState } from 'react'
import { SimulationPage } from './pages/SimulationPage'
import { VerificationPage } from './pages/VerificationPage'
import './styles/global.css'
import './styles/layout.css'
import './styles/simulation.css'
import './styles/monitoring.css'
import './styles/controls.css'

function App() {
  const [view, setView] = useState('simulation')

  return (
    <>
      <nav className="app-nav">
        <button type="button" onClick={() => setView('simulation')}>Simulation</button>
        <button type="button" onClick={() => setView('verification')}>Verification</button>
      </nav>
      {view === 'verification' ? <VerificationPage /> : <SimulationPage />}
    </>
  )
}

export default App
