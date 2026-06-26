import React, { useEffect, useState } from 'react';

const formatKickoff = (isoString) => {
  if (!isoString) return "";
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' }) + " at " + 
           date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    return isoString;
  }
};

export default function ResultsTable() {
  const [matches, setMatches] = useState([]);
  const [showTipsOnly, setShowTipsOnly] = useState(false);

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

  const filteredMatches = showTipsOnly 
    ? matches.filter(m => m.recommendation === 'BET_DRAW') 
    : matches;

  return (
    <div className="panel" style={{ position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: '14px' }}>
        <h2 style={{ margin: 0 }}>
          <span>Live Match Results</span>
          <span style={{ fontSize: '11px', textTransform: 'lowercase', color: 'var(--muted)', fontWeight: 'normal', marginLeft: '6px' }}>
            dynamic overlay
          </span>
        </h2>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button 
            onClick={() => setShowTipsOnly(false)}
            style={{
              background: !showTipsOnly ? 'rgba(56, 189, 248, 0.15)' : 'rgba(30, 41, 59, 0.4)',
              color: !showTipsOnly ? 'rgb(56, 189, 248)' : 'var(--muted)',
              border: !showTipsOnly ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid var(--border)',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            All Matches
          </button>
          <button 
            onClick={() => setShowTipsOnly(true)}
            style={{
              background: showTipsOnly ? 'rgba(251, 146, 60, 0.15)' : 'rgba(30, 41, 59, 0.4)',
              color: showTipsOnly ? 'var(--cursor)' : 'var(--muted)',
              border: showTipsOnly ? '1px solid rgba(251, 146, 60, 0.3)' : '1px solid var(--border)',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            🔥 Draw Tips
          </button>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filteredMatches.map(m => {
          const isLive = m.status === 'live';
          const isFinished = m.status === 'finished';
          const isBetDraw = m.recommendation === 'BET_DRAW' && !isFinished;
          
          return (
            <div 
              key={m.fixture_id} 
              style={{
                background: isBetDraw ? 'rgba(251, 146, 60, 0.03)' : 'rgba(30, 41, 59, 0.4)',
                border: isLive ? '1.5px solid var(--accent)' : isBetDraw ? '1.5px solid var(--cursor)' : '1px solid var(--border)',
                boxShadow: isLive ? '0 0 15px rgba(57, 255, 20, 0.15)' : isBetDraw ? '0 0 15px rgba(251, 146, 60, 0.12)' : 'none',
                borderRadius: '8px',
                padding: '14px 16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              }}
            >
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '2px' }}>
                  <span style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--muted)', letterSpacing: '0.8px' }}>
                    World Cup 2026 · Group {m.group_id}
                  </span>
                  {isBetDraw && (
                    <span style={{
                      background: 'rgba(251, 146, 60, 0.12)',
                      color: 'var(--cursor)',
                      fontSize: '9px',
                      fontWeight: 800,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      letterSpacing: '0.5px',
                      textTransform: 'uppercase',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      border: '1px solid rgba(251, 146, 60, 0.25)',
                      boxShadow: '0 0 10px rgba(251, 146, 60, 0.05)'
                    }}>
                      🔥 DRAW VALUE ({m.edge > 0 ? '+' : ''}{(m.edge * 100).toFixed(0)}% EDGE)
                    </span>
                  )}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text)', fontSize: '14px' }}>{m.home_team}</span>
                  <span style={{ color: 'var(--muted)', fontSize: '12px', fontWeight: 500 }}>vs</span>
                  <span style={{ fontWeight: 600, color: 'var(--text)', fontSize: '14px' }}>{m.away_team}</span>
                </div>
                {m.kickoff && (
                  <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px', fontWeight: 500 }}>
                    {formatKickoff(m.kickoff)}
                  </div>
                )}
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
                    <span style={{ 
                      background: 'rgba(56, 189, 248, 0.1)', 
                      color: 'rgb(56, 189, 248)', 
                      fontSize: '10px', 
                      fontWeight: 700, 
                      padding: '2px 8px', 
                      borderRadius: '4px', 
                      letterSpacing: '0.5px',
                      textTransform: 'uppercase'
                    }}>
                      {m.kickoff ? new Date(m.kickoff).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Scheduled'}
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
        {filteredMatches.length === 0 && (
          <div style={{ color: 'var(--muted)', textAlign: 'center', padding: '24px 16px', fontSize: '13px' }}>
            {showTipsOnly ? "No draw value recommendations found." : "No matches scheduled or in-play."}
          </div>
        )}
      </div>
    </div>
  );
}
