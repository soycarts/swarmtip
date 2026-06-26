import React, { useEffect, useState } from 'react';

export default function OddsComparison() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMatches = async () => {
    try {
      const res = await fetch('/api/matches');
      const data = await res.json();
      // Only keep upcoming/scheduled matches for odds comparison
      const upcoming = data.filter(m => m.status === 'scheduled');
      setMatches(upcoming);
      setLoading(false);
    } catch (e) {
      console.error("Failed to fetch matches for comparison", e);
    }
  };

  useEffect(() => {
    fetchMatches();
    const interval = setInterval(fetchMatches, 4000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="panel" style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>
        Loading odds comparison data...
      </div>
    );
  }

  return (
    <div className="panel" style={{ position: 'relative', overflow: 'hidden', marginBottom: '24px' }}>
      <div 
        style={{
          position: 'absolute',
          top: '-50%',
          right: '-20%',
          width: '250px',
          height: '250px',
          background: 'radial-gradient(circle, rgba(251, 146, 60, 0.05) 0%, rgba(251, 146, 60, 0) 70%)',
          pointerEvents: 'none',
          zIndex: 0
        }}
      />
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', position: 'relative', zIndex: 1 }}>
        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>Market vs Model Odds Comparison</span>
          <span style={{ fontSize: '11px', textTransform: 'lowercase', color: 'var(--muted)', fontWeight: 'normal' }}>
            value analysis
          </span>
        </h2>
      </div>

      <p style={{ color: 'var(--muted)', fontSize: '12.5px', lineHeight: '1.5', marginBottom: '20px', position: 'relative', zIndex: 1 }}>
        Below is the real-time comparison between the bookmaker's implied draw probabilities (derived from current market odds) and our heterogeneous AI swarm's calculated draw incentives. High-edge matches flag the <strong>BET_DRAW</strong> strategy.
      </p>

      <div style={{ overflowX: 'auto', position: 'relative', zIndex: 1 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <th style={{ textAlign: 'left', padding: '12px 16px', fontSize: '11px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600 }}>Matchup</th>
              <th style={{ textAlign: 'center', padding: '12px 16px', fontSize: '11px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600 }}>Group</th>
              <th style={{ textAlign: 'center', padding: '12px 16px', fontSize: '11px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600 }}>Draw Odds</th>
              <th style={{ textAlign: 'center', padding: '12px 16px', fontSize: '11px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600 }}>Market Prob</th>
              <th style={{ textAlign: 'center', padding: '12px 16px', fontSize: '11px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600 }}>Model Prob</th>
              <th style={{ textAlign: 'center', padding: '12px 16px', fontSize: '11px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600 }}>Edge</th>
              <th style={{ textAlign: 'center', padding: '12px 16px', fontSize: '11px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600 }}>Strategy</th>
            </tr>
          </thead>
          <tbody>
            {matches.map(m => {
              const isValue = m.recommendation === 'BET_DRAW';
              const marketProb = m.draw_odds ? (1 / m.draw_odds) : 0;
              const edgeVal = m.edge !== undefined ? m.edge : (m.model_draw_prob - marketProb);
              
              return (
                <tr 
                  key={m.fixture_id}
                  style={{
                    borderBottom: '1px solid var(--border)',
                    background: isValue ? 'rgba(251, 146, 60, 0.04)' : 'transparent',
                    transition: 'all 0.2s ease',
                  }}
                  className="odds-row"
                >
                  <td style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '13.5px' }}>{m.home_team}</span>
                      <span style={{ color: 'var(--muted)', fontSize: '11px' }}>vs</span>
                      <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '13.5px' }}>{m.away_team}</span>
                    </div>
                    {isValue && (
                      <span style={{ fontSize: '10px', color: 'var(--cursor)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                        🔥 Positive Edge Opportunity
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '16px', textAlign: 'center', color: 'var(--muted)', fontSize: '13px', fontWeight: 600 }}>
                    {m.group_id}
                  </td>
                  <td style={{ padding: '16px', textAlign: 'center', fontFamily: 'Montserrat, sans-serif', fontWeight: 700, fontSize: '13.5px', color: 'var(--text)' }}>
                    {m.draw_odds ? m.draw_odds.toFixed(2) : '-'}
                  </td>
                  <td style={{ padding: '16px', textAlign: 'center', fontFamily: 'Montserrat, sans-serif', color: 'var(--muted)', fontSize: '13px' }}>
                    {m.draw_odds ? `${(marketProb * 100).toFixed(1)}%` : '-'}
                  </td>
                  <td style={{ padding: '16px', textAlign: 'center', fontFamily: 'Montserrat, sans-serif', fontWeight: 700, color: isValue ? 'var(--accent)' : 'var(--text)', fontSize: '13.5px' }}>
                    {m.model_draw_prob ? `${(m.model_draw_prob * 100).toFixed(1)}%` : '-'}
                  </td>
                  <td style={{ 
                    padding: '16px', 
                    textAlign: 'center', 
                    fontFamily: 'Montserrat, sans-serif', 
                    fontWeight: 800,
                    fontSize: '13.5px',
                    color: edgeVal > 0.03 ? 'var(--accent)' : edgeVal < 0 ? '#ef4444' : 'var(--muted)'
                  }}>
                    {edgeVal !== undefined ? `${edgeVal > 0 ? '+' : ''}${(edgeVal * 100).toFixed(1)}%` : '-'}
                  </td>
                  <td style={{ padding: '16px', textAlign: 'center' }}>
                    <span style={{
                      background: isValue ? 'rgba(251, 146, 60, 0.15)' : m.recommendation === 'AVOID' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(148, 163, 184, 0.1)',
                      color: isValue ? 'var(--cursor)' : m.recommendation === 'AVOID' ? '#f87171' : 'var(--muted)',
                      border: isValue ? '1px solid rgba(251, 146, 60, 0.3)' : m.recommendation === 'AVOID' ? '1px solid rgba(239, 68, 68, 0.2)' : '1px solid var(--border)',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '10px',
                      fontWeight: 800,
                      letterSpacing: '0.5px',
                      textTransform: 'uppercase',
                      display: 'inline-block'
                    }}>
                      {m.recommendation || 'PENDING'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
