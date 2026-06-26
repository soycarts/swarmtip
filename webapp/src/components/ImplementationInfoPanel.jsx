import React from 'react';

export default function ImplementationInfoPanel() {
  return (
    <div className="panel" style={{ marginTop: '20px' }}>
      <div className="board-header-row" style={{ marginBottom: '14px' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
          Swarm System Architecture
        </h2>
        <span className="news-match-badge" style={{ background: 'rgba(57, 255, 20, 0.1)', color: 'var(--accent)', border: '1px solid rgba(57, 255, 20, 0.2)' }}>
          Active Engine
        </span>
      </div>

      <p style={{ color: 'var(--muted)', fontSize: '13px', marginBottom: '16px', lineHeight: '1.5' }}>
        Key details of our production-grade agentic coordination architecture, running on ClickHouse Cloud ledger events, Tavily advanced searches, and dynamic Gemini routing:
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Core Detail 1: NewsAgent */}
        <div style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '6px', padding: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ color: 'var(--accent)' }}>●</span> NewsAgent (Hourly Crawl)
            </span>
            <span style={{ fontSize: '11px', background: 'rgba(56, 189, 248, 0.15)', color: 'var(--human)', padding: '2px 6px', borderRadius: '4px', border: '1px solid rgba(56, 189, 248, 0.25)', fontWeight: 600 }}>
              Tavily + ClickHouse
            </span>
          </div>
          <p style={{ color: 'var(--muted)', fontSize: '12px', lineHeight: '1.4' }}>
            Autonomously executes every hour via orchestrator triggers. Scrapes match-specific lineup previews, tactical statements, and injury details across active fixtures. Updates the <code>match_news</code> table and injects the latest live context into the <code>StrategyAgent</code> prompts.
          </p>
        </div>

        {/* Core Detail 2: KickoffAgent */}
        <div style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '6px', padding: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ color: 'var(--accent)' }}>●</span> KickoffAgent (UTC Schedule)
            </span>
            <span style={{ fontSize: '11px', background: 'rgba(167, 139, 250, 0.15)', color: 'var(--claude)', padding: '2px 6px', borderRadius: '4px', border: '1px solid rgba(167, 139, 250, 0.25)', fontWeight: 600 }}>
              Gemini Verify
            </span>
          </div>
          <p style={{ color: 'var(--muted)', fontSize: '12px', lineHeight: '1.4' }}>
            Queries external schedules via Tavily search and uses Gemini to verify and extract official World Cup kickoff times in a strict <code>YYYY-MM-DD HH:MM:00</code> UTC format, updating our central fixtures database.
          </p>
        </div>

        {/* Core Detail 3: Timezone-Aware UTC Orchestrator */}
        <div style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '6px', padding: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ color: 'var(--accent)' }}>●</span> Timezone-Aware Orchestrator
            </span>
            <span style={{ fontSize: '11px', background: 'rgba(251, 146, 60, 0.15)', color: 'var(--cursor)', padding: '2px 6px', borderRadius: '4px', border: '1px solid rgba(251, 146, 60, 0.25)', fontWeight: 600 }}>
              UTC Sync
            </span>
          </div>
          <p style={{ color: 'var(--muted)', fontSize: '12px', lineHeight: '1.4' }}>
            Calculates match loop transitions dynamically. Uses tz-aware UTC timestamps (<code>datetime.now(timezone.utc)</code>) to track states (<code>scheduled</code> &rarr; <code>live</code> &rarr; <code>finished</code>). Translates current in-play times into actual elapsed minutes and injects them into regular live assessments.
          </p>
        </div>

        {/* Core Detail 4: ReplacingMergeTree & argMax */}
        <div style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '6px', padding: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ color: 'var(--accent)' }}>●</span> ClickHouse ReplacingMergeTree
            </span>
            <span style={{ fontSize: '11px', background: 'rgba(57, 255, 20, 0.15)', color: 'var(--accent)', padding: '2px 6px', borderRadius: '4px', border: '1px solid rgba(57, 255, 20, 0.25)', fontWeight: 600 }}>
              argMax Resolve
            </span>
          </div>
          <p style={{ color: 'var(--muted)', fontSize: '12px', lineHeight: '1.4' }}>
            Maintains absolute ledger consistency across asynchronous updates. Resolves the latest version of team fixtures and kickoff times on-demand using high-performance <code>argMax(field, updated_at)</code> aggregations grouped by <code>fixture_id</code>.
          </p>
        </div>
      </div>
    </div>
  );
}
