import React from 'react';

export default function SwarmBoard() {
  const mockTasks = [
    { id: 'assess_G_EGY_IRN', kind: 'agent', type: 'assess', status: 'done', assigned: 'orchestrator', title: 'Assess G_EGY_IRN' },
    { id: 'ground_G_EGY_IRN', kind: 'agent', type: 'ground', status: 'done', assigned: 'ContextAgent', title: 'Ground G_EGY_IRN' },
    { id: 'qualify_G_EGY_IRN', kind: 'agent', type: 'qualify', status: 'done', assigned: 'QualificationEngine', title: 'Qualify G_EGY_IRN' },
    { id: 'strategy_G_EGY_IRN', kind: 'agent', type: 'strategy', status: 'doing', assigned: 'StrategyAgent', title: 'Determine Strategy' },
    { id: 'price_G_EGY_IRN', kind: 'agent', type: 'price', status: 'todo', assigned: 'PricingAgent', title: 'Price Draw Odds' },
  ];

  return (
    <div className="panel">
      <h2>Live Swarm Board</h2>
      
      <div className="tb-summary">
        <span className="tb-sum st-todo">todo</span>
        <span className="tb-sum st-doing">doing</span>
        <span className="tb-sum st-done">done</span>
      </div>

      <div className="taskboard">
        {mockTasks.map(task => (
          <div key={task.id} className={`task-row ${task.status}`}>
            <div className={`st st-${task.status}`}>
              {task.status === 'todo' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" strokeDasharray="4 4"></circle></svg>}
              {task.status === 'doing' && <svg className="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>}
              {task.status === 'done' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>}
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
