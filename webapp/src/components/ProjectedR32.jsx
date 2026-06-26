import React, { useEffect, useState } from 'react';

export default function ProjectedR32() {
  const [qualifiers, setQualifiers] = useState([]);

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
    fetchQualifiers();
    const interval = setInterval(fetchQualifiers, 4000);
    return () => clearInterval(interval);
  }, []);

  // Split into Top 2 and Best Third
  const direct = qualifiers.filter(q => q.path === 'top2');
  const wildcard = qualifiers.filter(q => q.path === 'best_third');

  return (
    <div className="panel" style={{ position: 'relative', overflow: 'hidden' }}>
      <h2>
        <span>Projected Round of 32</span>
        <span style={{ fontSize: '11px', textTransform: 'lowercase', color: 'var(--muted)', fontWeight: 'normal' }}>
          as it stands
        </span>
      </h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '12px' }}>
        
        {/* Direct Qualifiers */}
        <div>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--accent)', fontWeight: 700, letterSpacing: '0.8px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent)' }} />
            Direct Qualifiers (Top 2)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '8px' }}>
            {direct.map(q => (
              <div 
                key={q.team} 
                style={{
                  background: 'rgba(57, 255, 20, 0.04)',
                  border: '1px solid rgba(57, 255, 20, 0.25)',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '2px',
                }}
              >
                <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '13px' }}>{q.team}</span>
                <span style={{ fontSize: '10px', color: 'var(--muted)' }}>
                  Group {q.group_id} · {q.points} pts
                </span>
              </div>
            ))}
            {direct.length === 0 && (
              <div style={{ color: 'var(--muted)', fontSize: '12px', fontStyle: 'italic' }}>Calculating...</div>
            )}
          </div>
        </div>

        {/* Wildcard Qualifiers */}
        <div>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--cursor)', fontWeight: 700, letterSpacing: '0.8px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--cursor)' }} />
            Best 3rd-Place Wildcards
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '8px' }}>
            {wildcard.map(q => (
              <div 
                key={q.team} 
                style={{
                  background: 'rgba(251, 146, 60, 0.04)',
                  border: '1px solid rgba(251, 146, 60, 0.25)',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '2px',
                }}
              >
                <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '13px' }}>{q.team}</span>
                <span style={{ fontSize: '10px', color: 'var(--muted)' }}>
                  Group {q.group_id} · {q.points} pts
                </span>
              </div>
            ))}
            {wildcard.length === 0 && (
              <div style={{ color: 'var(--muted)', fontSize: '12px', fontStyle: 'italic', padding: '4px' }}>
                No wildcards currently qualified.
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
