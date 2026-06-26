import React, { useEffect, useState } from 'react';

export default function ReasoningTraces() {
  const [traces, setTraces] = useState([]);
  const [expandedTraceId, setExpandedTraceId] = useState(null);

  const fetchTraces = async () => {
    try {
      const res = await fetch('/api/traces');
      const data = await res.json();
      setTraces(data);
    } catch (e) {
      console.error("Failed to fetch reasoning traces", e);
    }
  };

  useEffect(() => {
    fetchTraces();
    const interval = setInterval(fetchTraces, 4000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (isoString) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      const seconds = date.getSeconds().toString().padStart(2, '0');
      return `${hours}:${minutes}:${seconds}`;
    } catch (e) {
      return isoString;
    }
  };

  const toggleExpand = (id) => {
    if (expandedTraceId === id) {
      setExpandedTraceId(null);
    } else {
      setExpandedTraceId(id);
    }
  };

  return (
    <div className="panel" style={{ marginTop: '16px' }}>
      <div className="board-header-row">
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          Agent Reasoning Traces
        </h2>
        <div className="live" style={{ fontSize: '11px' }}>
          <span className="pulse" style={{ width: '6px', height: '6px' }} />
          live audit
        </div>
      </div>

      <div className="traces-container" style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
        {traces.length === 0 ? (
          <div style={{ color: 'var(--muted)', textAlign: 'center', padding: '24px 0' }}>
            No agent traces available yet.
          </div>
        ) : (
          traces.map((trace) => {
            const isExpanded = expandedTraceId === trace.task_id;
            const resData = trace.result || {};
            const isStrategy = trace.task_type === 'strategy';

            return (
              <div 
                key={trace.task_id} 
                className={`trace-card ${isExpanded ? 'expanded' : ''}`}
                style={{
                  background: 'var(--panel-2)',
                  border: isExpanded ? '1px solid var(--border)' : '1px solid transparent',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  transition: 'all 0.2s ease-in-out'
                }}
              >
                {/* Header row, clickable to toggle */}
                <div 
                  className="trace-header" 
                  onClick={() => toggleExpand(trace.task_id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    {isStrategy ? (
                      <span className="tag done" style={{ background: 'rgba(57, 255, 20, 0.1)', fontSize: '10px', textTransform: 'uppercase', fontWeight: 600 }}>
                        🤖 Gemini Strategy
                      </span>
                    ) : (
                      <span className="tag in_progress" style={{ background: 'rgba(56, 189, 248, 0.1)', fontSize: '10px', textTransform: 'uppercase', fontWeight: 600, color: 'var(--human)', borderColor: 'var(--human)' }}>
                        🔍 Tavily Grounding
                      </span>
                    )}

                    <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text)' }}>
                      {trace.fixture_id}
                    </span>

                    {isStrategy && resData.model_used && (
                      <span style={{ fontSize: '11px', color: resData.model_used.includes('pro') ? 'var(--warn)' : 'var(--muted)', fontWeight: 500 }}>
                        ({resData.model_used})
                      </span>
                    )}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--muted)', fontVariantNumeric: 'tabular-nums' }}>
                      {formatTime(trace.updated_at)}
                    </span>
                    <svg 
                      width="16" 
                      height="16" 
                      viewBox="0 0 24 24" 
                      fill="none" 
                      stroke="currentColor" 
                      strokeWidth="2.5"
                      style={{ 
                        transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                        transition: 'transform 0.2s ease',
                        color: 'var(--muted)'
                      }}
                    >
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </div>
                </div>

                {/* Expanded content */}
                {isExpanded && (
                  <div className="trace-body" style={{ padding: '12px', borderTop: '1px solid var(--border)', background: 'var(--panel)', fontSize: '13px' }}>
                    
                    {isStrategy ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        
                        {/* Summary metrics */}
                        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                          <div className="trace-metric">
                            <span style={{ color: 'var(--muted)', fontSize: '11px', display: 'block' }}>Incentive Class</span>
                            <strong style={{ 
                              color: resData.match_class === 'mutual_draw' ? 'var(--accent)' : 'var(--text)', 
                              fontSize: '13px',
                              fontFamily: 'monospace'
                            }}>
                              {resData.match_class || 'unknown'}
                            </strong>
                          </div>

                          <div className="trace-metric">
                            <span style={{ color: 'var(--muted)', fontSize: '11px', display: 'block' }}>Draw Probability</span>
                            <strong style={{ color: 'var(--human)', fontSize: '14px' }}>
                              {resData.draw_prob !== undefined ? `${(resData.draw_prob * 100).toFixed(0)}%` : 'N/A'}
                            </strong>
                          </div>

                          <div className="trace-metric">
                            <span style={{ color: 'var(--muted)', fontSize: '11px', display: 'block' }}>Play for Draw</span>
                            <strong style={{ color: resData.play_for_draw ? 'var(--accent)' : 'var(--bad)', fontSize: '13px' }}>
                              {resData.play_for_draw ? 'YES' : 'NO'}
                            </strong>
                          </div>
                        </div>

                        {/* Rationale block */}
                        <div>
                          <span style={{ color: 'var(--muted)', fontSize: '11px', display: 'block', marginBottom: '4px' }}>Model Rationale</span>
                          <blockquote style={{ 
                            borderLeft: '2px solid var(--accent)', 
                            paddingLeft: '10px', 
                            margin: 0, 
                            fontStyle: 'italic', 
                            color: 'var(--text)',
                            lineHeight: 1.5,
                            fontFamily: 'serif',
                            fontSize: '14px'
                          }}>
                            "{resData.rationale || 'No rationale sentence generated.'}"
                          </blockquote>
                        </div>

                        {/* Authoritative scenarios */}
                        {resData.qualification_scenarios && (
                          <div>
                            <span style={{ color: 'var(--muted)', fontSize: '11px', display: 'block', marginBottom: '6px' }}>Authoritative Scenarios (QualificationEngine)</span>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                              {Object.entries(resData.qualification_scenarios).map(([team, scenario]) => (
                                <div key={team} style={{ background: 'var(--panel-2)', padding: '8px', borderRadius: '6px', border: '1px solid var(--border)' }}>
                                  <span style={{ fontWeight: 600, color: 'var(--human)', fontSize: '12px', display: 'block', marginBottom: '2px' }}>{team}</span>
                                  <span style={{ color: 'var(--text)', fontSize: '12.5px' }}>{scenario || 'Loading...'}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                      </div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        
                        {/* Queries Run */}
                        {resData.queries_run && (
                          <div>
                            <span style={{ color: 'var(--muted)', fontSize: '11px', display: 'block', marginBottom: '4px' }}>Tavily API Queries</span>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                              {resData.queries_run.map((q, idx) => (
                                <code key={idx} style={{ background: 'var(--panel-2)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', color: 'var(--human)' }}>
                                  GET /search?query="{q}"
                                </code>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Grounded Sources */}
                        {resData.sources && resData.sources.length > 0 ? (
                          <div>
                            <span style={{ color: 'var(--muted)', fontSize: '11px', display: 'block', marginBottom: '6px' }}>Retrieved Grounding Sources ({resData.sources.length})</span>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '280px', overflowY: 'auto', paddingRight: '4px' }}>
                              {resData.sources.map((src, sIdx) => (
                                <div key={sIdx} style={{ background: 'var(--panel-2)', border: '1px solid var(--border)', borderRadius: '6px', padding: '8px' }}>
                                  <a 
                                    href={src.url} 
                                    target="_blank" 
                                    rel="noreferrer" 
                                    style={{ 
                                      color: 'var(--human)', 
                                      fontWeight: 600, 
                                      textDecoration: 'none', 
                                      fontSize: '12px',
                                      display: 'inline-block',
                                      marginBottom: '4px'
                                    }}
                                    className="source-link"
                                  >
                                    {src.title || 'Untitled Source'} ↗
                                  </a>
                                  <p style={{ color: 'var(--muted)', fontSize: '12px', margin: 0, lineHeight: 1.4 }}>
                                    {src.snippet}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div style={{ color: 'var(--muted)', fontStyle: 'italic' }}>
                            No raw sources attached to this grounding task result.
                          </div>
                        )}

                      </div>
                    )}

                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
