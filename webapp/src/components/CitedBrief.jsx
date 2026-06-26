import React from 'react';

export default function CitedBrief() {
  return (
    <div className="panel" style={{ display: 'flex', flexDirection: 'column' }}>
      <h2>Cited Brief</h2>
      
      <div className="report-headline">
        <p style={{ fontFamily: 'serif', fontSize: '15px', fontStyle: 'italic', marginBottom: '12px', color: 'var(--text)' }}>
          "With Egypt securing qualification after 38 minutes, Iran's optimal path shifts to playing for a point to secure the final Best Third place slot over New Zealand."
        </p>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <span className="tag done">Source: Prometheux Engine</span>
          <span className="tag done">Source: Tavily Squad News</span>
        </div>
      </div>
    </div>
  );
}
