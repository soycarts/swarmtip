import React, { useEffect, useState } from 'react';

export default function LiveStandings() {
  const [standings, setStandings] = useState([]);

  const fetchStandings = async () => {
    try {
      const res = await fetch('/api/standings');
      const data = await res.json();
      setStandings(data);
    } catch (e) {
      console.error("Failed to fetch standings", e);
    }
  };

  useEffect(() => {
    fetchStandings();
    const interval = setInterval(fetchStandings, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="panel" style={{ position: 'relative', overflow: 'hidden' }}>
      <h2>
        <span>Live Standings</span>
        <span style={{ fontSize: '11px', textTransform: 'lowercase', color: 'var(--accent)', fontWeight: 600 }}>
          as it stands
        </span>
      </h2>
      <div style={{ overflowX: 'auto', marginTop: '12px' }}>
        <table style={{ width: '100%', minWidth: '400px' }}>
          <thead>
            <tr>
              <th style={{ width: '40px', textAlign: 'center' }}>Pos</th>
              <th>Team</th>
              <th className="num">P</th>
              <th className="num">W</th>
              <th className="num">D</th>
              <th className="num">L</th>
              <th className="num">GD</th>
              <th className="num" style={{ fontWeight: 700, color: 'var(--text)' }}>Pts</th>
            </tr>
          </thead>
          <tbody>
            {standings.map(t => {
              // Highlight based on qualification position
              let indicatorColor = 'var(--muted)';
              let statusLabel = '';
              let rowBg = 'transparent';
              
              if (t.position <= 2) {
                indicatorColor = 'var(--accent)';
                statusLabel = 'Top 2 (Q)';
                rowBg = 'rgba(57, 255, 20, 0.02)';
              } else if (t.position === 3) {
                indicatorColor = 'var(--cursor)';
                statusLabel = 'Best Third';
                rowBg = 'rgba(251, 146, 60, 0.02)';
              } else {
                indicatorColor = 'var(--bad)';
                statusLabel = 'Eliminated';
                rowBg = 'rgba(239, 68, 110, 0.01)';
              }

              return (
                <tr 
                  key={t.team} 
                  style={{ 
                    background: rowBg,
                    transition: 'background-color 0.3s ease',
                  }}
                >
                  <td style={{ textAlign: 'center', padding: '10px 6px' }}>
                    <span 
                      className="rankpill" 
                      style={{ 
                        background: indicatorColor === 'var(--accent)' ? 'rgba(57, 255, 20, 0.15)' : 
                                    indicatorColor === 'var(--cursor)' ? 'rgba(251, 146, 60, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                        color: indicatorColor,
                        width: '24px',
                        height: '24px',
                        fontSize: '11px',
                        fontWeight: 700,
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: '6px'
                      }}
                    >
                      {t.position}
                    </span>
                  </td>
                  <td style={{ padding: '10px 6px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontWeight: 600, color: 'var(--text)' }}>{t.team}</span>
                      <span style={{ fontSize: '10px', color: indicatorColor, fontWeight: 500, letterSpacing: '0.3px', marginTop: '1px' }}>
                        {statusLabel}
                      </span>
                    </div>
                  </td>
                  <td className="num" style={{ fontWeight: 500 }}>{t.played}</td>
                  <td className="num">{t.won}</td>
                  <td className="num">{t.drawn}</td>
                  <td className="num">{t.lost}</td>
                  <td className="num" style={{ fontWeight: 600, color: t.goal_diff > 0 ? 'var(--accent)' : t.goal_diff < 0 ? 'var(--bad)' : 'var(--text)' }}>
                    {t.goal_diff > 0 ? `+${t.goal_diff}` : t.goal_diff}
                  </td>
                  <td className="num" style={{ fontWeight: 800, color: 'var(--text)', fontSize: '14px' }}>{t.points}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {standings.length === 0 && (
          <div style={{ color: 'var(--muted)', textAlign: 'center', padding: '16px', fontSize: '13px' }}>
            Loading standings...
          </div>
        )}
      </div>
    </div>
  );
}
