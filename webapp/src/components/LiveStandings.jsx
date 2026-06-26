import React, { useEffect, useState } from 'react';

export default function LiveStandings() {
  const [standings, setStandings] = useState([]);
  const [qualifiers, setQualifiers] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('G');

  const fetchStandings = async () => {
    try {
      const res = await fetch('/api/standings');
      const data = await res.json();
      setStandings(data);
    } catch (e) {
      console.error("Failed to fetch standings", e);
    }
  };

  const fetchQualifiers = async () => {
    try {
      const res = await fetch('/api/round_of_32');
      const data = await res.json();
      setQualifiers(data);
    } catch (e) {
      console.error("Failed to fetch projected qualifiers", e);
    }
  };

  useEffect(() => {
    fetchStandings();
    fetchQualifiers();
    const interval = setInterval(() => {
      fetchStandings();
      fetchQualifiers();
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  // Get unique group IDs in sorted order
  const groups = Array.from(new Set(standings.map(t => t.group_id))).sort();

  // Filter standings to the selected group
  const filteredStandings = standings.filter(t => t.group_id === selectedGroup);

  return (
    <div className="panel" style={{ position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
        <h2>
          <span>Live Standings</span>
          <span style={{ fontSize: '11px', textTransform: 'lowercase', color: 'var(--accent)', fontWeight: 600, marginLeft: '6px' }}>
            as it stands
          </span>
        </h2>
        {/* Status Legends */}
        <div style={{ display: 'flex', gap: '10px', fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
          <span style={{ color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: 'var(--accent)' }} /> Q (Top 2)
          </span>
          <span style={{ color: 'var(--cursor)', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: 'var(--cursor)' }} /> Q (Best 3rd)
          </span>
          <span style={{ color: 'var(--bad)', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: 'var(--bad)' }} /> Eliminated
          </span>
        </div>
      </div>

      {/* Beautiful Premium Tab Selector */}
      {groups.length > 1 && (
        <div style={{ 
          display: 'flex', 
          gap: '6px', 
          overflowX: 'auto', 
          paddingBottom: '8px', 
          marginBottom: '14px',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        }}>
          {groups.map(g => {
            const isSelected = selectedGroup === g;
            const isLiveGroup = g === 'G'; // Highlight Group G specifically as live
            return (
              <button
                key={g}
                onClick={() => setSelectedGroup(g)}
                style={{
                  background: isSelected ? 'var(--accent)' : 'rgba(30, 41, 59, 0.4)',
                  color: isSelected ? 'var(--panel)' : 'var(--text)',
                  border: isSelected 
                    ? '1.5px solid var(--accent)' 
                    : isLiveGroup 
                      ? '1px dashed var(--accent)' 
                      : '1px solid var(--border)',
                  fontWeight: 700,
                  fontSize: '11px',
                  padding: '5px 10px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  minWidth: '40px',
                  textAlign: 'center',
                  boxShadow: isSelected ? '0 0 10px rgba(57, 255, 20, 0.3)' : 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px'
                }}
              >
                {isLiveGroup && !isSelected && (
                  <span className="pulse" style={{ display: 'inline-block', width: '5px', height: '5px', borderRadius: '50%', background: 'var(--accent)' }} />
                )}
                {g}
              </button>
            );
          })}
        </div>
      )}

      <div style={{ overflowX: 'auto' }}>
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
            {filteredStandings.map(t => {
              // Check if team is projected to qualify in Round of 32
              const isQualified = qualifiers.some(q => q.team === t.team);
              
              let indicatorColor = 'var(--muted)';
              let statusLabel = '';
              let rowBg = 'transparent';
              
              if (t.position <= 2) {
                indicatorColor = 'var(--accent)';
                statusLabel = 'Top 2 (Qualified)';
                rowBg = 'rgba(57, 255, 20, 0.02)';
              } else if (t.position === 3) {
                if (isQualified) {
                  indicatorColor = 'var(--cursor)';
                  statusLabel = 'Best Third (Qualified)';
                  rowBg = 'rgba(251, 146, 60, 0.02)';
                } else {
                  indicatorColor = 'var(--bad)';
                  statusLabel = 'Eliminated (3rd Place)';
                  rowBg = 'rgba(239, 68, 110, 0.01)';
                }
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
