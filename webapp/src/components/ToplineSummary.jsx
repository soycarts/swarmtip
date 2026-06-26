import React, { useEffect, useState } from 'react';

export default function ToplineSummary() {
  const [stats, setStats] = useState({
    active_recommendations: 0,
    total_recommendations: 0,
    total_checked: 0
  });
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();
      setStats(data);
      setLoading(false);
    } catch (e) {
      console.error("Failed to fetch stats", e);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div 
      className="panel" 
      style={{
        display: 'grid',
        gridTemplateColumns: '1.2fr 2fr',
        gap: '24px',
        padding: '24px',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)',
        border: '1.5px solid rgba(71, 85, 105, 0.5)',
        boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        borderRadius: '12px',
        marginBottom: '24px',
        alignItems: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Decorative background glow */}
      <div 
        style={{
          position: 'absolute',
          top: '-50%',
          left: '-10%',
          width: '300px',
          height: '300px',
          background: 'radial-gradient(circle, rgba(57, 255, 20, 0.08) 0%, rgba(57, 255, 20, 0) 70%)',
          pointerEvents: 'none',
          zIndex: 0
        }}
      />
      <div 
        style={{
          position: 'absolute',
          bottom: '-50%',
          right: '-10%',
          width: '300px',
          height: '300px',
          background: 'radial-gradient(circle, rgba(56, 189, 248, 0.05) 0%, rgba(56, 189, 248, 0) 70%)',
          pointerEvents: 'none',
          zIndex: 0
        }}
      />

      {/* Metric Column */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', borderRight: '1px solid rgba(71, 85, 105, 0.4)', paddingRight: '20px' }}>
        <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600, letterSpacing: '1px', marginBottom: '16px', textAlign: 'center' }}>
          Active Draw Recommendations
        </div>
        
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div 
            style={{
              width: '120px',
              height: '120px',
              borderRadius: '50%',
              background: 'rgba(15, 23, 42, 0.8)',
              border: stats.active_recommendations > 0 ? '3px solid var(--accent)' : '2.5px solid var(--border)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: stats.active_recommendations > 0 ? '0 0 25px rgba(57, 255, 20, 0.25)' : 'none',
              transition: 'all 0.4s ease-in-out',
            }}
          >
            <span style={{ 
              fontSize: '48px', 
              fontWeight: 800, 
              color: stats.active_recommendations > 0 ? 'var(--accent)' : 'var(--text)',
              fontFamily: 'Montserrat, sans-serif',
              lineHeight: 1
            }}>
              {loading ? '...' : stats.active_recommendations}
            </span>
            <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--muted)', fontWeight: 600, marginTop: '2px' }}>
              Tips Live
            </span>
          </div>
          
          {stats.active_recommendations > 0 && (
            <span 
              className="pulse" 
              style={{ 
                position: 'absolute', 
                top: '6px', 
                right: '6px', 
                width: '14px', 
                height: '14px', 
                borderRadius: '50%', 
                background: 'var(--accent)',
                boxShadow: '0 0 10px var(--accent)'
              }} 
            />
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', width: '100%', marginTop: '20px', textAlign: 'center' }}>
          <div>
            <div style={{ fontSize: '10px', color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.5px' }}>Total Tips Logged</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text)', fontFamily: 'Montserrat, sans-serif', marginTop: '2px' }}>{loading ? '...' : stats.total_recommendations}</div>
          </div>
          <div>
            <div style={{ fontSize: '10px', color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.5px' }}>Fixtures Checked</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--human)', fontFamily: 'Montserrat, sans-serif', marginTop: '2px' }}>{loading ? '...' : stats.total_checked}</div>
          </div>
        </div>
      </div>

      {/* Explainer Column */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <h3 style={{ 
          fontFamily: 'Montserrat, sans-serif', 
          fontWeight: 700, 
          fontSize: '16px', 
          color: 'var(--text)', 
          marginBottom: '10px',
          letterSpacing: '-0.3px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ color: 'var(--accent)' }}>★</span> Play-For-A-Draw Strategy
        </h3>
        <p style={{ 
          color: 'rgba(248, 250, 252, 0.85)', 
          fontSize: '13.5px', 
          lineHeight: '1.6', 
          fontWeight: 400,
          margin: 0
        }}>
          Since the best 8 third place ranked teams qualify, some teams will be incentivised to play out a draw depending on other results. swarmtip's betting agents seek out opportunities for you to bet on this happening.
        </p>

        <div style={{ display: 'flex', gap: '16px', marginTop: '16px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(56, 189, 248, 0.1)', padding: '4px 10px', borderRadius: '6px', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--human)' }} />
            <span style={{ fontSize: '11px', color: 'var(--human)', fontWeight: 500 }}>Deterministic Standing calculations</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(57, 255, 20, 0.08)', padding: '4px 10px', borderRadius: '6px', border: '1px solid rgba(57, 255, 20, 0.15)' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent)' }} />
            <span style={{ fontSize: '11px', color: 'var(--accent)', fontWeight: 500 }}>Heterogeneous model routing</span>
          </div>
        </div>
      </div>
    </div>
  );
}
