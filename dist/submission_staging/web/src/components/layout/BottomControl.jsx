import { CirclePause, CirclePlay, RotateCcw, SkipForward } from 'lucide-react'

export function BottomControl({ running, speedMultiplier, onSpeedChange, onStart, onPause, onNextTick, onReset, controlError }) {
  return (
    <footer className="bottom-control">
      {controlError && <span className="control-error" role="alert">{controlError}</span>}
      <span className="sim-control-title">SIM CONTROL</span>
      <button
        className={`start-btn ${running ? 'control-active' : ''}`}
        type="button"
        aria-pressed={running}
        onClick={onStart}
      >
        <CirclePlay size={15} /> START
      </button>
      <button type="button" onClick={onPause}><CirclePause size={15} /> PAUSE</button>
      <button type="button" onClick={onNextTick}><SkipForward size={15} /> NEXT TICK</button>
      <button type="button" onClick={onReset}><RotateCcw size={15} /> RESET</button>

      <div className="speed-group">
        SPEED
        {[0.5, 1, 2, 5].map((speed) => (
          <button
            key={speed}
            className={speedMultiplier === speed ? 'speed-active' : ''}
            type="button"
            aria-pressed={speedMultiplier === speed}
            onClick={() => onSpeedChange(speed)}
          >
            ×{speed}
          </button>
        ))}
      </div>
    </footer>
  )
}