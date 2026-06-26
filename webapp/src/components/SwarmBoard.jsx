import React, { useEffect, useState } from 'react';
import { queryClickHouse } from '../clickhouse';

export default function SwarmBoard() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const query = `
          SELECT task_id as id, status, kind, task_type as type, assigned_to as assigned, title 
          FROM tasks_current 
          ORDER BY updated_at DESC 
          LIMIT 50
        `;
        const data = await queryClickHouse(query);
        setTasks(data.data);
      } catch (e) {
        console.error("Failed to fetch tasks", e);
      }
    };
    fetchTasks();
    const interval = setInterval(fetchTasks, 4000);
    return () => clearInterval(interval);
  }, []);

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
          
          return (
          <div key={task.id} className={`task-row ${statusClass}`}>
            <div className={`st st-${statusClass}`}>
              {statusClass === 'todo' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" strokeDasharray="4 4"></circle></svg>}
              {statusClass === 'doing' && <svg className="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>}
              {statusClass === 'done' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>}
            </div>
            
            <div className="task-main">
              <div className="task-title" style={{ fontSize: '13px', fontWeight: 500 }}>
                {task.title}
              </div>
              <div className="task-sub">
                <span className="chip" style={{ color: 'var(--human)', borderColor: 'var(--human)' }}>
                  {task.assigned}
                </span>
                <span className="chip" style={{ color: 'var(--muted)', borderColor: 'var(--border)' }}>
                  {task.type}
                </span>
                <span>{task.id}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
