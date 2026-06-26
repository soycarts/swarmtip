import React, { useEffect, useState } from 'react';

export default function ResultsTable() {
  const [matches, setMatches] = useState([]);

  const fetchMatches = async () => {
    try {
      const res = await fetch('/api/matches');
      const data = await res.json();
      setMatches(data);
    } catch (e) {
      console.error("Failed to fetch matches", e);
    }
  };

  useEffect(() => {
    fetchMatches();
    const interval = setInterval(fetchMatches, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="panel" style={{ position: 'relative', overflow: 'hidden' }}>
      <h2>
        <span>Live Match Results</span>
        <span style={{ fontSize: '11px', textTransform: 'lowercase', color: 'var(--muted)', fontWeight: 'normal' }}>
          dynamic overlay
        </span>
      </h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
        {matches.map(m => {
          const isLive = m.status === 'live';
          const isFinished = m.status === 'finished';
          return (
            <div 
              key={m.fixture_id} 
              style={{
                background: 'rgba(30, 41, 59, 0.4)',
                border: isLive ? '1.5px solid var(--accent)' : '1px solid var(--border)',
                boxShadow: isLive ? '0 0 15px rgba(57, 255, 20, 0.15)' : 'none',
                borderRadius: '8px',
                padding: '14px 16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              }}
            >
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--muted)', letterSpacing: '0.8px' }}>
                  World Cup 2026 · Group {m.group_id}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text)', fontSize: '14px' }}>{m.home_team}</span>
                  <span style={{ color: 'var(--muted)', fontSize: '12px', fontWeight: 500 }}>vs</span>
                  <span style={{ fontWeight: 600, color: 'var(--text)', fontSize: '14px' }}>{m.away_team}</span>
                </div>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  {isLive && (
                    <span style={{ 
                      display: 'inline-flex', 
                      alignItems: 'center', 
                      gap: '4px', 
                      background: 'rgba(57, 255, 20, 0.1)', 
                      color: 'var(--accent)', 
                      fontSize: '10px', 
                      fontWeight: 700, 
                      padding: '2px 8px', 
                      borderRadius: '4px', 
                      letterSpacing: '0.5px' 
                    }}>
                      <span className="pulse" style={{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent)' }} />
                      LIVE {m.minute}'
                    </span>
                  )}
                  {isFinished && (
                    <span style={{ 
                      background: 'rgba(148, 163, 184, 0.15)', 
                      color: 'var(--muted)', 
                      fontSize: '10px', 
                      fontWeight: 700, 
                      padding: '2px 6px', 
                      borderRadius: '4px' 
                    }}>
                      FT
                    </span>
                  )}
                  {!isLive && !isFinished && (
                    <span style={{ color: 'var(--muted)', fontSize: '11px', fontWeight: 500 }}>
                      Scheduled
                    </span>
                  )}
                </div>
                
                <span style={{ 
                  fontFamily: 'Montserrat, sans-serif', 
                  fontWeight: 800, 
                  fontSize: '18px', 
                  color: isLive ? 'var(--accent)' : 'var(--text)',
                  letterSpacing: '2px',
                  background: 'var(--panel)',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: isLive ? '1px solid var(--accent)' : '1px solid var(--border)',
                  boxShadow: isLive ? '0 0 10px rgba(57, 255, 20, 0.1)' : 'none',
                }}>
                  {m.score}
                </span>
              </div>
            </div>
          );
        })}
        {matches.length === 0 && (
          <div style={{ color: 'var(--muted)', textAlign: 'center', padding: '16px', fontSize: '13px' }}>
            No matches scheduled or in-play.
          </div>
        )}
      </div>
    </div>
  );
}
