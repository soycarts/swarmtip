import React, { useEffect, useState } from 'react';

// Seeding configuration for Round of 32 fixtures as defined by FIFA 2026 World Cup slots.
const r32Matches = [
  { id: 'M74', t1: { type: 'winner', val: 'E' }, t2: { type: 'best_third', val: 0 }, venue: 'Boston' },
  { id: 'M77', t1: { type: 'winner', val: 'I' }, t2: { type: 'best_third', val: 1 }, venue: 'Philadelphia' },
  { id: 'M73', t1: { type: 'runner_up', val: 'A' }, t2: { type: 'runner_up', val: 'B' }, venue: 'Los Angeles' },
  { id: 'M75', t1: { type: 'winner', val: 'F' }, t2: { type: 'runner_up', val: 'C' }, venue: 'Boston' },
  { id: 'M76', t1: { type: 'winner', val: 'C' }, t2: { type: 'runner_up', val: 'F' }, venue: 'Vancouver' },
  { id: 'M78', t1: { type: 'runner_up', val: 'E' }, t2: { type: 'runner_up', val: 'I' }, venue: 'Monterrey' },
  { id: 'M79', t1: { type: 'winner', val: 'A' }, t2: { type: 'best_third', val: 2 }, venue: 'Miami' },
  { id: 'M80', t1: { type: 'winner', val: 'L' }, t2: { type: 'best_third', val: 3 }, venue: 'Atlanta' },
  { id: 'M83', t1: { type: 'runner_up', val: 'K' }, t2: { type: 'runner_up', val: 'L' }, venue: 'New York/NJ' },
  { id: 'M84', t1: { type: 'winner', val: 'H' }, t2: { type: 'runner_up', val: 'J' }, venue: 'Houston' },
  { id: 'M81', t1: { type: 'winner', val: 'D' }, t2: { type: 'best_third', val: 4 }, venue: 'San Francisco' },
  { id: 'M82', t1: { type: 'winner', val: 'G' }, t2: { type: 'best_third', val: 5 }, venue: 'Seattle' },
  { id: 'M86', t1: { type: 'winner', val: 'J' }, t2: { type: 'runner_up', val: 'H' }, venue: 'Kansas City' },
  { id: 'M88', t1: { type: 'runner_up', val: 'D' }, t2: { type: 'runner_up', val: 'G' }, venue: 'Dallas' },
  { id: 'M85', t1: { type: 'winner', val: 'B' }, t2: { type: 'best_third', val: 6 }, venue: 'Los Angeles' },
  { id: 'M87', t1: { type: 'winner', val: 'K' }, t2: { type: 'best_third', val: 7 }, venue: 'Toronto' },
];

export default function ProjectedR32() {
  const [qualifiers, setQualifiers] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('bracket'); // 'bracket' | 'teams'
  const [userPicks, setUserPicks] = useState({});
  const [hoveredTeam, setHoveredTeam] = useState(null);

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

  // Split qualifiers into Top 2 and Best Third
  const direct = qualifiers.filter(q => q.path === 'top2');
  const wildcard = qualifiers.filter(q => q.path === 'best_third');

  // Build maps of standing values for lookup
  const teamMap = {};
  const bestThirds = [];
  qualifiers.forEach(q => {
    if (q.path === 'best_third') {
      bestThirds.push(q);
    } else {
      const key = `${q.group_id}${q.position}`; // e.g. "A1", "A2"
      teamMap[key] = q;
    }
  });

  // Helper to fetch standing details
  const getTeamStatsRaw = (slotType, index) => {
    if (slotType === 'winner') {
      return teamMap[`${index}1`] || null;
    }
    if (slotType === 'runner_up') {
      return teamMap[`${index}2`] || null;
    }
    if (slotType === 'best_third') {
      return bestThirds[index] || null;
    }
    return null;
  };

  // Recursive team resolver for the bracket tree
  const getMatchTeam = (matchId, slotNum) => {
    const r32 = r32Matches.find(m => m.id === matchId);
    if (r32) {
      const slotDef = slotNum === 1 ? r32.t1 : r32.t2;
      const raw = getTeamStatsRaw(slotDef.type, slotDef.val);
      if (raw) {
        return {
          name: raw.team,
          group: raw.group_id,
          points: raw.points,
          goalDiff: raw.goal_diff,
          position: slotDef.type === 'winner' ? 1 : slotDef.type === 'runner_up' ? 2 : 3,
          stats: `Group ${raw.group_id} · ${raw.points} pts`,
          matchId: matchId,
          isPlaceholder: false
        };
      } else {
        const label = slotDef.type === 'winner' 
          ? `Winner ${slotDef.val}` 
          : slotDef.type === 'runner_up' 
            ? `Runner-up ${slotDef.val}` 
            : `Best 3rd #${slotDef.val + 1}`;
        return {
          name: label,
          group: slotDef.type !== 'best_third' ? slotDef.val : '',
          points: 0,
          goalDiff: 0,
          position: slotDef.type === 'winner' ? 1 : slotDef.type === 'runner_up' ? 2 : 3,
          stats: slotDef.type === 'best_third' ? 'Best 3rd seed' : `Group ${slotDef.val} Pos ${slotDef.type === 'winner' ? '1' : '2'}`,
          matchId: matchId,
          isPlaceholder: true
        };
      }
    }

    // Round of 16 (resolves from preceding Round of 32 winners)
    if (matchId === 'M89') return slotNum === 1 ? resolveMatch('M74').winner : resolveMatch('M77').winner;
    if (matchId === 'M90') return slotNum === 1 ? resolveMatch('M73').winner : resolveMatch('M75').winner;
    if (matchId === 'M91') return slotNum === 1 ? resolveMatch('M76').winner : resolveMatch('M78').winner;
    if (matchId === 'M92') return slotNum === 1 ? resolveMatch('M79').winner : resolveMatch('M80').winner;
    if (matchId === 'M93') return slotNum === 1 ? resolveMatch('M83').winner : resolveMatch('M84').winner;
    if (matchId === 'M94') return slotNum === 1 ? resolveMatch('M81').winner : resolveMatch('M82').winner;
    if (matchId === 'M95') return slotNum === 1 ? resolveMatch('M86').winner : resolveMatch('M88').winner;
    if (matchId === 'M96') return slotNum === 1 ? resolveMatch('M85').winner : resolveMatch('M87').winner;

    // Quarterfinals (resolves from preceding Round of 16 winners)
    if (matchId === 'M97') return slotNum === 1 ? resolveMatch('M89').winner : resolveMatch('M90').winner;
    if (matchId === 'M99') return slotNum === 1 ? resolveMatch('M91').winner : resolveMatch('M92').winner;
    if (matchId === 'M98') return slotNum === 1 ? resolveMatch('M93').winner : resolveMatch('M94').winner;
    if (matchId === 'M100') return slotNum === 1 ? resolveMatch('M95').winner : resolveMatch('M96').winner;

    // Semifinals (resolves from Quarterfinal winners)
    if (matchId === 'M101') return slotNum === 1 ? resolveMatch('M97').winner : resolveMatch('M99').winner;
    if (matchId === 'M102') return slotNum === 1 ? resolveMatch('M98').winner : resolveMatch('M100').winner;

    // Final (resolves from Semifinal winners)
    if (matchId === 'M104') return slotNum === 1 ? resolveMatch('M101').winner : resolveMatch('M102').winner;

    return { name: 'TBD', stats: '', position: 4, points: 0, isPlaceholder: true };
  };

  // Helper to resolve the winner of a match, backing up with seed logic
  const resolveMatch = (matchId) => {
    const t1 = getMatchTeam(matchId, 1);
    const t2 = getMatchTeam(matchId, 2);

    if (t1.isPlaceholder && t2.isPlaceholder) {
      return { t1, t2, winner: { name: 'TBD', stats: '', position: 4, points: 0, isPlaceholder: true } };
    }

    // Check if the user has custom-clicked a winner for this match card
    const userPick = userPicks[matchId];
    if (userPick) {
      if (userPick === t1.name && !t1.isPlaceholder) return { t1, t2, winner: t1 };
      if (userPick === t2.name && !t2.isPlaceholder) return { t1, t2, winner: t2 };
    }

    // Seeding algorithms when no user override exists:
    if (t1.isPlaceholder) return { t1, t2, winner: t2 };
    if (t2.isPlaceholder) return { t1, t2, winner: t1 };

    // Position in group: 1st place > 2nd place > 3rd place
    if (t1.position < t2.position) return { t1, t2, winner: t1 };
    if (t2.position < t1.position) return { t1, t2, winner: t2 };

    // Group stage points
    if (t1.points > t2.points) return { t1, t2, winner: t1 };
    if (t2.points > t1.points) return { t1, t2, winner: t2 };

    // Goal difference
    if (t1.goalDiff > t2.goalDiff) return { t1, t2, winner: t1 };
    if (t2.goalDiff > t1.goalDiff) return { t1, t2, winner: t2 };

    // Fallback default
    return { t1, t2, winner: t1 };
  };

  // Render a single match card component
  const MatchCard = ({ matchId, label }) => {
    const { t1, t2, winner } = resolveMatch(matchId);

    const handleTeamClick = (teamName, isPlaceholder) => {
      if (isPlaceholder || teamName === 'TBD') return;
      setUserPicks(prev => ({
        ...prev,
        [matchId]: teamName,
      }));
    };

    const isT1Hovered = hoveredTeam && t1.name === hoveredTeam && !t1.isPlaceholder;
    const isT2Hovered = hoveredTeam && t2.name === hoveredTeam && !t2.isPlaceholder;
    
    const isT1Winner = winner && winner.name === t1.name && winner.name !== 'TBD';
    const isT2Winner = winner && winner.name === t2.name && winner.name !== 'TBD';

    return (
      <div className="match-card-wrapper" style={{
        background: 'var(--panel)',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        width: '185px',
        padding: '6px 10px',
        display: 'flex',
        flexDirection: 'column',
        gap: '2px',
        boxShadow: '0 4px 10px rgba(0, 0, 0, 0.2)',
        position: 'relative',
        transition: 'border-color 0.2s, box-shadow 0.2s',
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '9px',
          color: 'var(--muted)',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
          paddingBottom: '3px',
          marginBottom: '3px',
          fontWeight: 600,
        }}>
          <span style={{ color: 'var(--accent)' }}>{label}</span>
          <span style={{ fontSize: '8px', opacity: 0.8 }}>
            {r32Matches.find(m => m.id === matchId)?.venue || 'TBD Venue'}
          </span>
        </div>

        {/* Team 1 */}
        <div
          onClick={() => handleTeamClick(t1.name, t1.isPlaceholder)}
          onMouseEnter={() => !t1.isPlaceholder && setHoveredTeam(t1.name)}
          onMouseLeave={() => setHoveredTeam(null)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '4px 6px',
            borderRadius: '4px',
            cursor: t1.isPlaceholder ? 'default' : 'pointer',
            background: isT1Winner ? 'rgba(57, 255, 20, 0.06)' : 'transparent',
            border: isT1Hovered ? '1px solid var(--accent)' : '1px solid transparent',
            boxShadow: isT1Hovered ? '0 0 10px rgba(57, 255, 20, 0.3)' : 'none',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <span style={{
              fontSize: '11px',
              fontWeight: isT1Winner ? 700 : 500,
              color: isT1Winner ? 'var(--text)' : (isT2Winner ? 'var(--muted)' : 'var(--text)'),
              opacity: isT2Winner ? 0.45 : 1,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}>
              {t1.name}
            </span>
            <span style={{ fontSize: '8px', color: 'var(--muted)', opacity: isT2Winner ? 0.45 : 0.8 }}>
              {t1.stats}
            </span>
          </div>
          {isT1Winner && (
            <span style={{ color: 'var(--accent)', fontSize: '10px', marginLeft: '4px' }}>✓</span>
          )}
        </div>

        {/* Team 2 */}
        <div
          onClick={() => handleTeamClick(t2.name, t2.isPlaceholder)}
          onMouseEnter={() => !t2.isPlaceholder && setHoveredTeam(t2.name)}
          onMouseLeave={() => setHoveredTeam(null)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '4px 6px',
            borderRadius: '4px',
            cursor: t2.isPlaceholder ? 'default' : 'pointer',
            background: isT2Winner ? 'rgba(57, 255, 20, 0.06)' : 'transparent',
            border: isT2Hovered ? '1px solid var(--accent)' : '1px solid transparent',
            boxShadow: isT2Hovered ? '0 0 10px rgba(57, 255, 20, 0.3)' : 'none',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <span style={{
              fontSize: '11px',
              fontWeight: isT2Winner ? 700 : 500,
              color: isT2Winner ? 'var(--text)' : (isT1Winner ? 'var(--muted)' : 'var(--text)'),
              opacity: isT1Winner ? 0.45 : 1,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}>
              {t2.name}
            </span>
            <span style={{ fontSize: '8px', color: 'var(--muted)', opacity: isT1Winner ? 0.45 : 0.8 }}>
              {t2.stats}
            </span>
          </div>
          {isT2Winner && (
            <span style={{ color: 'var(--accent)', fontSize: '10px', marginLeft: '4px' }}>✓</span>
          )}
        </div>
      </div>
    );
  };

  const champion = resolveMatch('M104').winner;

  // Render original list of Top-2/Wildcards
  const renderQualifiedLists = () => (
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
  );

  return (
    <div className="panel" style={{ position: 'relative', overflow: 'hidden', padding: '16px' }}>
      
      {/* LOCAL STYLES FOR THE GLOWING PATH HIGHLIGHTS & BRACKET TREE */}
      <style>{`
        .bracket-scroll-container::-webkit-scrollbar {
          height: 6px;
          width: 6px;
        }
        .bracket-scroll-container::-webkit-scrollbar-track {
          background: rgba(255,255,255,0.02);
          border-radius: 4px;
        }
        .bracket-scroll-container::-webkit-scrollbar-thumb {
          background: var(--border);
          border-radius: 4px;
        }
        .bracket-scroll-container::-webkit-scrollbar-thumb:hover {
          background: var(--muted);
        }
        @keyframes goldenPulse {
          0% { box-shadow: 0 0 10px rgba(250, 204, 21, 0.15); border-color: rgba(250, 204, 21, 0.3); }
          50% { box-shadow: 0 0 25px rgba(250, 204, 21, 0.4); border-color: rgba(250, 204, 21, 0.7); }
          100% { box-shadow: 0 0 10px rgba(250, 204, 21, 0.15); border-color: rgba(250, 204, 21, 0.3); }
        }
        .champion-card {
          animation: goldenPulse 3s infinite ease-in-out;
        }
      `}</style>

      {/* Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h2>
          <span>Projected Round of 32</span>
          <span style={{ fontSize: '11px', textTransform: 'lowercase', color: 'var(--muted)', fontWeight: 'normal', marginLeft: '6px' }}>
            {isExpanded ? 'interactive bracket tree simulator' : 'as it stands'}
          </span>
        </h2>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {isExpanded && Object.keys(userPicks).length > 0 && (
            <button
              onClick={() => setUserPicks({})}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border)',
                borderRadius: '6px',
                padding: '4px 10px',
                color: 'var(--muted)',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--text)'; e.currentTarget.style.background = 'rgba(255,255,255,0.08)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--muted)'; e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; }}
            >
              ↺ Reset Picks
            </button>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            style={{
              background: 'rgba(57, 255, 20, 0.08)',
              border: '1px solid rgba(57, 255, 20, 0.3)',
              borderRadius: '6px',
              padding: '4px 12px',
              color: 'var(--accent)',
              fontSize: '11px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(57, 255, 20, 0.15)'; e.currentTarget.style.borderColor = 'var(--accent)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(57, 255, 20, 0.08)'; e.currentTarget.style.borderColor = 'rgba(57, 255, 20, 0.3)'; }}
          >
            {isExpanded ? '▲ Collapse Tree' : '⚡ Open Bracket Simulator'}
          </button>
        </div>
      </div>

      {/* Tabs and Content inside Expanded State */}
      {isExpanded ? (
        <div>
          {/* Internal Navigation Tabs */}
          <div style={{
            display: 'flex',
            gap: '8px',
            borderBottom: '1px solid var(--border)',
            paddingBottom: '8px',
            marginBottom: '14px',
          }}>
            <button
              onClick={() => setActiveTab('bracket')}
              style={{
                background: activeTab === 'bracket' ? 'rgba(255,255,255,0.06)' : 'transparent',
                border: 'none',
                color: activeTab === 'bracket' ? 'var(--text)' : 'var(--muted)',
                fontWeight: activeTab === 'bracket' ? 700 : 500,
                fontSize: '11px',
                textTransform: 'uppercase',
                padding: '6px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                letterSpacing: '0.6px',
              }}
            >
              🏆 Tournament Tree
            </button>
            <button
              onClick={() => setActiveTab('teams')}
              style={{
                background: activeTab === 'teams' ? 'rgba(255,255,255,0.06)' : 'transparent',
                border: 'none',
                color: activeTab === 'teams' ? 'var(--text)' : 'var(--muted)',
                fontWeight: activeTab === 'teams' ? 700 : 500,
                fontSize: '11px',
                textTransform: 'uppercase',
                padding: '6px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                letterSpacing: '0.6px',
              }}
            >
              📋 Qualified Teams
            </button>
          </div>

          {activeTab === 'teams' ? (
            renderQualifiedLists()
          ) : (
            /* TOURNAMENT TREE BRACKET GRAPHIC CONTAINER */
            <div 
              className="bracket-scroll-container"
              style={{
                maxHeight: '660px',
                overflow: 'auto',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                borderRadius: '10px',
                background: 'rgba(15, 23, 42, 0.4)',
                padding: '16px 20px',
              }}
            >
              {/* Symmetrical/Hierarchical Columns Header */}
              <div style={{
                display: 'flex',
                gap: '24px',
                borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
                paddingBottom: '8px',
                marginBottom: '16px',
                alignItems: 'center'
              }}>
                <div style={{ minWidth: '185px', fontSize: '10px', textTransform: 'uppercase', fontWeight: 800, color: 'var(--accent)', letterSpacing: '1px' }}>Round of 32</div>
                <div style={{ minWidth: '185px', fontSize: '10px', textTransform: 'uppercase', fontWeight: 800, color: 'var(--accent)', letterSpacing: '1px' }}>Round of 16</div>
                <div style={{ minWidth: '185px', fontSize: '10px', textTransform: 'uppercase', fontWeight: 800, color: 'var(--accent)', letterSpacing: '1px' }}>Quarterfinals</div>
                <div style={{ minWidth: '185px', fontSize: '10px', textTransform: 'uppercase', fontWeight: 800, color: 'var(--accent)', letterSpacing: '1px' }}>Semifinals</div>
                <div style={{ minWidth: '185px', fontSize: '10px', textTransform: 'uppercase', fontWeight: 800, color: 'var(--accent)', letterSpacing: '1px' }}>Final</div>
                <div style={{ minWidth: '210px', fontSize: '10px', textTransform: 'uppercase', fontWeight: 800, color: 'var(--warn)', letterSpacing: '1px' }}>🏆 Champion</div>
              </div>

              {/* Flex columns for the Tree */}
              <div style={{
                display: 'flex',
                gap: '24px',
                height: '1100px', // Standard container height to space everything beautifully
              }}>
                
                {/* 1. Round of 32 Column */}
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  minWidth: '185px',
                  height: '100%',
                }}>
                  <MatchCard matchId="M74" label="Match 74" />
                  <MatchCard matchId="M77" label="Match 77" />
                  <MatchCard matchId="M73" label="Match 73" />
                  <MatchCard matchId="M75" label="Match 75" />
                  <MatchCard matchId="M76" label="Match 76" />
                  <MatchCard matchId="M78" label="Match 78" />
                  <MatchCard matchId="M79" label="Match 79" />
                  <MatchCard matchId="M80" label="Match 80" />
                  <MatchCard matchId="M83" label="Match 83" />
                  <MatchCard matchId="M84" label="Match 84" />
                  <MatchCard matchId="M81" label="Match 81" />
                  <MatchCard matchId="M82" label="Match 82" />
                  <MatchCard matchId="M86" label="Match 86" />
                  <MatchCard matchId="M88" label="Match 88" />
                  <MatchCard matchId="M85" label="Match 85" />
                  <MatchCard matchId="M87" label="Match 87" />
                </div>

                {/* 2. Round of 16 Column */}
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-around',
                  minWidth: '185px',
                  height: '100%',
                }}>
                  <MatchCard matchId="M89" label="Match 89" />
                  <MatchCard matchId="M90" label="Match 90" />
                  <MatchCard matchId="M91" label="Match 91" />
                  <MatchCard matchId="M92" label="Match 92" />
                  <MatchCard matchId="M93" label="Match 93" />
                  <MatchCard matchId="M94" label="Match 94" />
                  <MatchCard matchId="M95" label="Match 95" />
                  <MatchCard matchId="M96" label="Match 96" />
                </div>

                {/* 3. Quarterfinals Column */}
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-around',
                  minWidth: '185px',
                  height: '100%',
                }}>
                  <MatchCard matchId="M97" label="Match 97" />
                  <MatchCard matchId="M99" label="Match 99" />
                  <MatchCard matchId="M98" label="Match 98" />
                  <MatchCard matchId="M100" label="Match 100" />
                </div>

                {/* 4. Semifinals Column */}
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-around',
                  minWidth: '185px',
                  height: '100%',
                }}>
                  <MatchCard matchId="M101" label="Match 101" />
                  <MatchCard matchId="M102" label="Match 102" />
                </div>

                {/* 5. Final Column */}
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-around',
                  minWidth: '185px',
                  height: '100%',
                }}>
                  <MatchCard matchId="M104" label="Match 104" />
                </div>

                {/* 6. Glowing Champion Column */}
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-around',
                  minWidth: '210px',
                  height: '100%',
                }}>
                  <div 
                    className="champion-card"
                    style={{
                      background: 'linear-gradient(135deg, rgba(250, 204, 21, 0.12) 0%, rgba(250, 204, 21, 0.02) 100%)',
                      border: '2px solid rgba(250, 204, 21, 0.35)',
                      borderRadius: '12px',
                      padding: '24px 16px',
                      textAlign: 'center',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                  >
                    <span style={{ fontSize: '32px' }}>🏆</span>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontSize: '9px', textTransform: 'uppercase', color: 'var(--warn)', fontWeight: 800, letterSpacing: '1px' }}>
                        Projected Champion
                      </span>
                      <span style={{ 
                        fontSize: '16px', 
                        fontWeight: 900, 
                        color: '#fef08a',
                        textShadow: '0 0 10px rgba(250, 204, 21, 0.3)',
                        marginTop: '4px',
                      }}>
                        {champion && champion.name !== 'TBD' ? champion.name : 'Simulating...'}
                      </span>
                      {champion && champion.stats && champion.name !== 'TBD' && (
                        <span style={{ fontSize: '10px', color: 'var(--muted)', marginTop: '2px' }}>
                          {champion.stats}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

              </div>
            </div>
          )}
        </div>
      ) : (
        /* COLLAPSED DEFAULT STATE (ORIGINAL QUALIFIERS GRID LIST) */
        renderQualifiedLists()
      )}
    </div>
  );
}
