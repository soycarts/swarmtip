import React, { useEffect, useState } from 'react';
import SwarmBoard from './components/SwarmBoard';
import CitedBrief from './components/CitedBrief';
import AudioPlayer from './components/AudioPlayer';
import { queryClickHouse } from './clickhouse';

function App() {
  const [signal, setSignal] = useState(null);

  useEffect(() => {
    const fetchSignals = async () => {
      try {
        const res = await fetch('/api/signals');
        const data = await res.json();
        if (data.length > 0) {
          setSignal(data[0]); // just show the most recent signal
        }
      } catch (e) {
        console.error("Failed to fetch signals", e);
      }
    };
    fetchSignals();
    const interval = setInterval(fetchSignals, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="wrap">
      <div className="topbar">
        <div className="brand" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="var(--accent)" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
          </svg>
          SWARMTIP
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div className="live">
            <span className="pulse" />
            live · refreshes every 4s
          </div>
        </div>
      </div>

      <div className="grid">
        <div>
          <SwarmBoard />
        </div>
        <div>
          <CitedBrief />
          <AudioPlayer />
          
          <div className="panel">
            <h2>Signal Output</h2>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px 0' }}>
              {signal ? (
                <>
                  <div className="bigpct" style={{ color: signal.recommendation === 'BET_DRAW' ? 'var(--accent)' : 'var(--human)' }}>
                    {signal.recommendation}
                  </div>
                  <div className="slider-hint" style={{ marginTop: '12px', fontSize: '13px' }}>
                    Fixture: <span style={{ color: 'var(--human)', fontWeight: 600 }}>{signal.fixture_id}</span> | 
                    Computed Edge: <span style={{ color: 'var(--human)', fontWeight: 600 }}>{signal.edge > 0 ? '+' : ''}{signal.edge.toFixed(3)}</span>
                  </div>
                </>
              ) : (
                <div style={{ color: 'var(--muted)' }}>Waiting for signals...</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
