import React from 'react';

export default function PrometheuxOntologyPanel() {
  const measures = [
    {
      id: "projected_points",
      predicate: "projected_points(T, F, P)",
      name: "Draw Points Projection",
      logic: "standings(T, CurrentP), P = CurrentP + 1",
      description: "Computes the team's hypothetical points if the match under analysis ends in a draw.",
      badge: "Rule 1",
      badgeColor: "rgba(56, 189, 248, 0.15)",
      badgeTextColor: "#38bdf8"
    },
    {
      id: "secures_top2",
      predicate: "secures_top2(T, F)",
      name: "Guaranteed Top-2 Finish",
      logic: "projected_points(T, F, P), group_scenario_min_position(T, F, Pos), Pos <= 2",
      description: "Deterministically evaluates all 3^N permutation outcomes of the group sibling fixtures to guarantee the team finishes 1st or 2nd under a draw.",
      badge: "Rule 2",
      badgeColor: "rgba(57, 255, 20, 0.15)",
      badgeTextColor: "#39ff14"
    },
    {
      id: "secures_best_third",
      predicate: "secures_best_third(T, F)",
      name: "Best-Third Qualification",
      logic: "group_scenario_min_position(T, F, 3), (P >= 4 || (P == 3, goal_difference(T, GD), GD >= 0))",
      description: "Evaluates if a 3rd-place finish secures progression, requiring either >= 4 points or exactly 3 points with a non-negative goal difference.",
      badge: "Rule 3",
      badgeColor: "rgba(251, 191, 36, 0.15)",
      badgeTextColor: "#fbbf24"
    },
    {
      id: "draw_sufficient",
      predicate: "draw_sufficient(T, F)",
      name: "Draw Sufficiency Indicator",
      logic: "secures_top2(T, F) || secures_best_third(T, F)",
      description: "Aggregates rules to flag if a draw is mathematically sufficient for World Cup round-of-32 qualification.",
      badge: "Rule 4",
      badgeColor: "rgba(168, 85, 247, 0.15)",
      badgeTextColor: "#a855f7"
    }
  ];

  return (
    <div className="panel" style={{ marginTop: '16px' }}>
      <div className="board-header-row" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2.5">
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
            <line x1="4" y1="22" x2="4" y2="15" />
          </svg>
          Prometheux Logic Ontology
        </h2>
        <span className="live" style={{ fontSize: '10px', background: 'rgba(57, 255, 20, 0.1)', color: 'var(--accent)', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>
          Active Solver
        </span>
      </div>

      <p style={{ fontSize: '13px', color: 'var(--muted)', margin: '10px 0 16px 0', lineHeight: 1.4 }}>
        The deterministic engine executes these declarative Datalog ontology rules over ClickHouse standings data, generating fully verifiable lineage traces for every match.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {measures.map((m) => (
          <div 
            key={m.id} 
            style={{ 
              background: 'var(--panel-2)', 
              border: '1px solid var(--border)', 
              borderRadius: '8px', 
              padding: '12px',
              transition: 'all 0.15s ease'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: 600, color: 'var(--human)' }}>
                {m.predicate}
              </span>
              <span style={{ 
                fontSize: '10px', 
                fontWeight: 700, 
                background: m.badgeColor, 
                color: m.badgeTextColor, 
                padding: '1px 6px', 
                borderRadius: '4px' 
              }}>
                {m.badge}
              </span>
            </div>

            <h3 style={{ fontSize: '13px', margin: '0 0 4px 0', fontWeight: 600, color: 'var(--text)' }}>
              {m.name}
            </h3>

            <p style={{ fontSize: '12px', color: 'var(--muted)', margin: '0 0 10px 0', lineHeight: 1.4 }}>
              {m.description}
            </p>

            <div style={{ 
              background: 'rgba(0, 0, 0, 0.15)', 
              borderRadius: '4px', 
              padding: '6px 8px', 
              borderLeft: '2px solid var(--accent)',
              display: 'flex',
              alignItems: 'center'
            }}>
              <code style={{ fontSize: '11px', color: 'var(--text)', fontFamily: 'monospace', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                :- {m.logic}.
              </code>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
