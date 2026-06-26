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
       argMaxIf(actor, ts, event_type IN ('completed', 'failed', 'cancelled')) AS resolved_by,
       argMaxIf(fixture_id, ts, fixture_id != '') AS fixture_id,
       argMaxIf(depends_on, ts, notEmpty(depends_on)) AS depends_on,
       argMaxIf(title, ts, title != '')      AS title,
       argMaxIf(result, ts, result != '{}')     AS result,
       min(ts)                AS created_at,
       argMaxIf(ts, ts, event_type IN ('completed', 'failed', 'cancelled')) AS resolved_at,
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

-- ============================================================
-- BBC-Style Visualization Views
-- ============================================================

-- 1. Group Standings View (Latest row per team)
CREATE VIEW IF NOT EXISTS group_standings_view AS
SELECT 
    group_id,
    team,
    argMax(played, updated_at) AS played,
    argMax(won, updated_at) AS won,
    argMax(drawn, updated_at) AS drawn,
    argMax(lost, updated_at) AS lost,
    argMax(goals_for, updated_at) AS goals_for,
    argMax(goals_against, updated_at) AS goals_against,
    argMax(goal_diff, updated_at) AS goal_diff,
    argMax(points, updated_at) AS points,
    argMax(position, updated_at) AS position
FROM standings
GROUP BY group_id, team
ORDER BY group_id, points DESC, goal_diff DESC, goals_for DESC;

-- 2. Best Third-Placed Teams
CREATE VIEW IF NOT EXISTS best_third_placed_teams AS
SELECT 
    group_id,
    team,
    played,
    won,
    drawn,
    lost,
    goals_for,
    goals_against,
    goal_diff,
    points
FROM group_standings_view
WHERE position = 3
ORDER BY points DESC, goal_diff DESC, goals_for DESC;

-- 3. Draw Incentive Fixtures
CREATE VIEW IF NOT EXISTS draw_incentive_fixtures AS
SELECT 
    f.fixture_id,
    f.group_id,
    f.home_team,
    f.away_team,
    f.kickoff,
    f.status,
    qs.team AS incentive_team,
    qs.draw_points,
    qs.path,
    qs.reasoning
FROM fixtures f
JOIN qualification_signals qs ON f.fixture_id = qs.fixture_id
WHERE f.status IN ('scheduled', 'live') AND qs.draw_sufficient = 1
ORDER BY f.kickoff ASC;

-- 4. Projected Round of 32
CREATE VIEW IF NOT EXISTS projected_round_of_32 AS
SELECT 
    group_id,
    team,
    position,
    points,
    goal_diff,
    goals_for
FROM group_standings_view
WHERE position <= 2
UNION ALL
SELECT 
    group_id,
    team,
    3 AS position,
    points,
    goal_diff,
    goals_for
FROM best_third_placed_teams
LIMIT 8;
