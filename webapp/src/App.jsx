import React from 'react';
import SwarmBoard from './components/SwarmBoard';
import CitedBrief from './components/CitedBrief';
import AudioPlayer from './components/AudioPlayer';

function App() {
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
              <div className="bigpct" style={{ color: 'var(--accent)' }}>
                BET_DRAW
              </div>
              <div className="slider-hint" style={{ marginTop: '12px', fontSize: '13px' }}>
                Computed Edge: <span style={{ color: 'var(--human)', fontWeight: 600 }}>+0.18</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
