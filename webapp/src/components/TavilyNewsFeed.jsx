import React, { useEffect, useState } from 'react';

export default function TavilyNewsFeed() {
  const [news, setNews] = useState([]);
  const [selectedMatch, setSelectedMatch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchNews = async () => {
    try {
      const res = await fetch('/api/news?limit=25');
      const data = await res.json();
      setNews(data);
    } catch (e) {
      console.error("Failed to fetch news", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 4000);
    return () => clearInterval(interval);
  }, []);

  const getDomain = (url) => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return 'News Link';
    }
  };

  const getRelativeTime = (isoString) => {
    if (!isoString) return '';
    try {
      const normalized = (isoString.endsWith('Z') || isoString.includes('+') || (isoString.includes('-') && isoString.lastIndexOf('-') > 7)) 
        ? isoString 
        : `${isoString}Z`;
      const date = new Date(normalized);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  // Get list of unique matches in the current news feed for the dropdown filter
  const matches = [];
  const seenMatches = new Set();
  
  news.forEach(item => {
    if (item.home_team && item.away_team) {
      const matchLabel = `${item.home_team} vs ${item.away_team}`;
      if (!seenMatches.has(item.fixture_id)) {
        seenMatches.add(item.fixture_id);
        matches.push({ id: item.fixture_id, label: matchLabel });
      }
    }
  });

  const filteredNews = selectedMatch 
    ? news.filter(item => item.fixture_id === selectedMatch)
    : news;

  return (
    <div className="panel news-panel">
      <div className="board-header-row" style={{ marginBottom: '14px' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent)' }}>
            <path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 4a2 2 0 0 0-2-2h-3a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h3a2 2 0 0 0 2-2V11z" />
            <path d="M7 8h4" />
            <path d="M7 12h4" />
            <path d="M7 16h8" />
          </svg>
          Upcoming Match News Feed
        </h2>
        
        {matches.length > 0 && (
          <div className="filter-group">
            <label htmlFor="match-select" className="filter-label">Filter Match:</label>
            <select 
              id="match-select"
              value={selectedMatch} 
              onChange={(e) => setSelectedMatch(e.target.value)}
              className="filter-select"
              style={{ padding: '4px 8px', fontSize: '12px' }}
            >
              <option value="">All Matches</option>
              {matches.map(m => (
                <option key={m.id} value={m.id}>{m.label}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading && news.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '30px', color: 'var(--muted)' }}>
          <svg className="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
          </svg>
        </div>
      ) : filteredNews.length === 0 ? (
        <div className="empty" style={{ textAlign: 'center', padding: '20px 0' }}>
          No grounding squad news or form updates found.
        </div>
      ) : (
        <div className="feed" style={{ maxHeight: '420px', overflowY: 'auto', paddingRight: '4px' }}>
          {filteredNews.map((item, idx) => {
            const domain = getDomain(item.url);
            const timeAgo = getRelativeTime(item.fetched_at);
            return (
              <div key={idx} className="feed-item news-item">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '4px', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                    <span className="news-domain">{domain}</span>
                    {item.home_team && item.away_team && (
                      <span className="news-match-badge">
                        {item.home_team} v {item.away_team}
                      </span>
                    )}
                  </div>
                  {timeAgo && <span className="news-time">{timeAgo}</span>}
                </div>
                
                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="news-link-title"
                >
                  {item.title}
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: '4px', display: 'inline-block', verticalAlign: 'middle' }}>
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                </a>
                
                {item.snippet && (
                  <p className="news-snippet">
                    {item.snippet.length > 180 ? `${item.snippet.slice(0, 180)}...` : item.snippet}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
