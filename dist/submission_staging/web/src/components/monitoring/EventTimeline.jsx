export function EventTimeline({ events = [] }) {
  return (
    <section className="monitor-card event-card">
      <h3>● LIVE EVENT TIMELINE</h3>
      <div className="event-list">
        {events.map((event, index) => (
          <div className={`event-item event-${String(event.severity ?? 'INFO').toLowerCase()}`} key={`${event.time}-${event.message}-${index}`}>
            <div className="event-marker" />
            <div className="event-content">
              <div className="event-meta">
                <span className="event-time">TICK {String(event.tick ?? 0).padStart(5, '0')}</span>
                <span className="event-code">{event.code ?? event.type ?? 'SYSTEM'}</span>
              </div>
              <span className="event-text">{event.message}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}