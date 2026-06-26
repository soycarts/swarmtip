import React, { useEffect, useState } from 'react';
import { queryClickHouse } from '../clickhouse';

export default function SwarmBoard() {
  const [tasks, setTasks] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 8; // 8 rows per page looks very balanced

  const fetchTasks = async (currentPage) => {
    try {
      const res = await fetch(`/api/tasks?page=${currentPage}&limit=${limit}`);
      const data = await res.json();
      setTasks(data.tasks);
      setTotal(data.total);
    } catch (e) {
      console.error("Failed to fetch tasks", e);
    }
  };

  useEffect(() => {
    fetchTasks(page);
    const interval = setInterval(() => fetchTasks(page), 4000);
    return () => clearInterval(interval);
  }, [page]);

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

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="panel">
      <h2>Live Swarm Board</h2>
      
      <div className="tb-summary">
        <span className="tb-sum st-todo">todo</span>
        <span className="tb-sum st-doing">doing</span>
        <span className="tb-sum st-done">done</span>
      </div>

      <div className="taskboard">
        {tasks.map(task => {
          let statusClass = 'todo';
          if (task.status === 'completed') statusClass = 'done';
          else if (task.status === 'started' || task.status === 'claimed') statusClass = 'doing';
          else if (task.status === 'created') statusClass = 'todo';
          else if (task.status === 'failed') statusClass = 'failed';
          else if (task.status === 'cancelled') statusClass = 'cancelled';
          
          return (
          <div key={task.id} className={`task-row ${statusClass}`}>
            <div className={`st st-${statusClass}`}>
              {statusClass === 'todo' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" strokeDasharray="4 4"></circle></svg>}
              {statusClass === 'doing' && <svg className="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>}
              {statusClass === 'done' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>}
              {(statusClass === 'failed' || statusClass === 'cancelled') && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>}
            </div>
            
            <div className="task-main">
              <div className="task-title" style={{ fontSize: '13px', fontWeight: 500 }}>
                {task.title}
              </div>
              <div className="task-sub">
                {task.assigned && (
                  <span className="chip" style={{ color: 'var(--human)', borderColor: 'var(--human)' }}>
                    {task.assigned}
                  </span>
                )}
                <span className="chip" style={{ color: 'var(--muted)', borderColor: 'var(--border)' }}>
                  {task.type}
                </span>
                <span style={{ fontSize: '11px', color: 'var(--muted)' }}>{task.id}</span>
              </div>
              
              <div className="task-meta-info">
                <span className="meta-time">
                  Created: <strong style={{ color: 'var(--human)' }}>{formatTime(task.created_at)}</strong> by <span className="meta-actor">{task.created_by}</span>
                </span>
                {task.resolved_at && (
                  <span className="meta-time" style={{ marginLeft: '12px' }}>
                    Resolved: <strong style={{ color: 'var(--accent)' }}>{formatTime(task.resolved_at)}</strong> by <span className="meta-actor">{task.resolved_by || 'system'}</span>
                  </span>
                )}
              </div>
            </div>
          </div>
          );
        })}
      </div>

      <div className="pagination-ctrl">
        <button 
          onClick={() => setPage(p => Math.max(1, p - 1))} 
          disabled={page === 1} 
          className="pag-btn"
        >
          &larr; Prev
        </button>
        <span className="pag-info">
          Page {page} of {totalPages} <span className="total-badge">({total} total)</span>
        </span>
        <button 
          onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
          disabled={page >= totalPages} 
          className="pag-btn"
        >
          Next &rarr;
        </button>
      </div>
    </div>
  );
}
