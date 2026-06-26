import React, { useEffect, useState } from 'react';
import SwarmBoard from './components/SwarmBoard';
import ResultsTable from './components/ResultsTable';
import LiveStandings from './components/LiveStandings';
import ProjectedR32 from './components/ProjectedR32';
import ToplineSummary from './components/ToplineSummary';
import TavilyNewsFeed from './components/TavilyNewsFeed';
import ReasoningTraces from './components/ReasoningTraces';
import PrometheuxOntologyPanel from './components/PrometheuxOntologyPanel';
import ImplementationInfoPanel from './components/ImplementationInfoPanel';
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
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <polygon points="12 9 14.9 11.1 13.8 14.4 10.2 14.4 9.1 11.1" fill="var(--accent)" />
            <path d="M12 9L12 2M14.9 11.1L21.5 8.9M13.8 14.4L17.9 20.1M10.2 14.4L6.1 20.1M9.1 11.1L2.5 8.9" />
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

      <ToplineSummary />

      <div className="grid">
        <div>
          <ResultsTable />
          <LiveStandings />
          <ProjectedR32 />
          <TavilyNewsFeed />
        </div>
        <div>
          <SwarmBoard />
          <ReasoningTraces />
          <PrometheuxOntologyPanel />
          <ImplementationInfoPanel />
          
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
