-- views.sql

-- Current state of every task: latest event wins. The close-to-live board.
CREATE VIEW IF NOT EXISTS tasks_current AS
SELECT task_id,
       argMax(kind, ts)       AS kind,
       argMaxIf(task_type, ts, task_type != '')  AS task_type,
       argMax(event_type, ts) AS status,
       argMaxIf(assignee, ts, assignee != '')    AS assigned_to,
       argMinIf(actor, ts, event_type IN ('created', 'started')) AS created_by,
       argMaxIf(actor, ts, event_type = 'completed')             AS completed_by,
       argMaxIf(fixture_id, ts, fixture_id != '') AS fixture_id,
       argMaxIf(depends_on, ts, notEmpty(depends_on)) AS depends_on,
       argMaxIf(title, ts, title != '')      AS title,
       argMaxIf(result, ts, result != '{}')     AS result,
       min(ts)                AS created_at,
       max(ts)                AS updated_at
FROM task_events
GROUP BY task_id;

-- Demo board: live moves and who is doing what.
CREATE VIEW IF NOT EXISTS swarm_board AS
SELECT status, kind, task_type, assigned_to, fixture_id, title, updated_at
FROM tasks_current
ORDER BY updated_at DESC;

CREATE VIEW IF NOT EXISTS agent_status AS
SELECT agent, argMax(status, ts) AS status, max(ts) AS last_seen
FROM heartbeats GROUP BY agent;
