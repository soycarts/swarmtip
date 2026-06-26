from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.db import client
import re
from datetime import datetime
import json

app = FastAPI()

def to_utc_iso(dt: datetime) -> str:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.isoformat() + "Z"
    return dt.isoformat()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/board")
def get_board():
    ch = client()
    # swarm_board view columns: status, kind, task_type, assigned_to, fixture_id, title, updated_at
    res = ch.query("SELECT * FROM swarm_board LIMIT 50")
    tasks = []
    # In ClickHouse driver, rows are returned as tuples. Column names are in res.column_names
    # Let's map them carefully.
    cols = res.column_names
    for row in res.result_rows:
        d = dict(zip(cols, row))
        # webapp expects: id, kind, type, status, assigned, title
        tasks.append({
            "id": d["task_id"] if "task_id" in d else f"{d.get('task_type')}_{d.get('fixture_id')}", # tasks_current has task_id, swarm_board doesn't have task_id! Wait, swarm_board view does not have task_id.
            # let's just query tasks_current directly
            "status": d.get("status"),
            "kind": d.get("kind"),
            "type": d.get("task_type"),
            "assigned": d.get("assigned_to"),
            "title": d.get("title"),
        })
    return tasks

@app.get("/api/tasks")
def get_tasks(page: int = 1, limit: int = 10, resolver: str = None):
    ch = client()
    offset = (page - 1) * limit
    
    where_clause = ""
    if resolver:
        # Sanitize parameter to prevent SQL injection
        resolver_clean = re.sub(r'[^a-zA-Z0-9_\-]', '', resolver)
        if resolver_clean:
            where_clause = f"WHERE resolved_by = '{resolver_clean}'"
            
    # Get total count
    count_query = f"SELECT count() FROM tasks_current {where_clause}"
    count_res = ch.query(count_query)
    total_count = count_res.result_rows[0][0]
    
    # Query tasks
    query = f"""
        SELECT task_id, status, kind, task_type, assigned_to, title, 
               created_by, resolved_by, created_at, resolved_at, updated_at 
        FROM tasks_current 
        {where_clause}
        ORDER BY created_at DESC 
        LIMIT {limit} OFFSET {offset}
    """
    res = ch.query(query)
    tasks = []
    cols = res.column_names
    for row in res.result_rows:
        d = dict(zip(cols, row))
        
        # Clean up default epoch DateTime values from ClickHouse (e.g., 1970-01-01)
        resolved_at_val = d.get("resolved_at")
        if resolved_at_val and resolved_at_val.year <= 1970:
            resolved_at_val = None
            
        tasks.append({
            "id": d["task_id"],
            "status": d["status"],
            "kind": d["kind"],
            "type": d["task_type"],
            "assigned": d["assigned_to"],
            "title": d["title"],
            "created_by": d.get("created_by") or "unknown",
            "resolved_by": d.get("resolved_by") if d.get("resolved_by") else None,
            "created_at": to_utc_iso(d.get("created_at")),
            "resolved_at": to_utc_iso(resolved_at_val),
            "updated_at": to_utc_iso(d.get("updated_at"))
        })
        
    return {
        "tasks": tasks,
        "total": total_count,
        "page": page,
        "limit": limit
    }

@app.get("/api/signals")
def get_signals():
    ch = client()
    # Support sorting by created_at or ts depending on schema
    res = ch.query("SELECT fixture_id, match_class, recommendation, model_draw_prob, edge FROM value_signals ORDER BY created_at DESC LIMIT 10")
    signals = []
    for r in res.result_rows:
        signals.append({
            "fixture_id": r[0],
            "match_class": r[1],
            "recommendation": r[2],
            "model_draw_prob": r[3],
            "edge": r[4],
        })
    return signals

@app.get("/api/stats")
def get_stats():
    ch = client()
    
    # 1. Total BET_DRAW recommendations
    bet_draw_res = ch.query("SELECT count() FROM value_signals WHERE recommendation = 'BET_DRAW'")
    total_recommendations = bet_draw_res.result_rows[0][0] if bet_draw_res.result_rows else 0
    
    # 2. Total checked fixtures
    checked_res = ch.query("SELECT count() FROM value_signals")
    total_checked = checked_res.result_rows[0][0] if checked_res.result_rows else 0
    
    # 3. Active recommendations (where fixture status is live or scheduled)
    active_res = ch.query("""
        SELECT count() 
        FROM value_signals v
        JOIN fixtures f ON v.fixture_id = f.fixture_id
        WHERE v.recommendation = 'BET_DRAW' AND f.status IN ('scheduled', 'live')
    """)
    active_recommendations = active_res.result_rows[0][0] if active_res.result_rows else 0
    
    return {
        "active_recommendations": active_recommendations,
        "total_recommendations": total_recommendations,
        "total_checked": total_checked
    }


@app.get("/api/news")
def get_news(fixture_id: str = None, limit: int = 15):
    ch = client()
    
    where_clause = ""
    if fixture_id:
        fixture_id_clean = re.sub(r'[^a-zA-Z0-9_\-]', '', fixture_id)
        where_clause = f"WHERE s.fixture_id = '{fixture_id_clean}'"
        
    # 1. Fetch from the dedicated match_news table first
    query_match_news = f"""
        SELECT s.fixture_id, s.title, s.url, s.snippet, s.fetched_at, f.home_team, f.away_team
        FROM match_news s
        LEFT JOIN fixtures f ON s.fixture_id = f.fixture_id
        {where_clause}
        ORDER BY s.fetched_at DESC
        LIMIT {limit}
    """
    
    res = ch.query(query_match_news)
    news = []
    seen_urls = set()
    
    cols = res.column_names
    for row in res.result_rows:
        d = dict(zip(cols, row))
        url = d.get("url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        news.append({
            "fixture_id": d.get("fixture_id"),
            "url": url,
            "title": d.get("title") or "Match News",
            "snippet": d.get("snippet") or "",
            "source_name": "Tavily News Feed",
            "fetched_at": to_utc_iso(d.get("fetched_at")),
            "home_team": d.get("home_team") or "",
            "away_team": d.get("away_team") or ""
        })
        
    # 2. Fall back to / supplement with grounding sources
    if len(news) < limit:
        query_sources = f"""
            SELECT s.fixture_id, s.title, s.url, s.snippet, s.fetched_at, f.home_team, f.away_team
            FROM sources s
            LEFT JOIN fixtures f ON s.fixture_id = f.fixture_id
            {where_clause}
            ORDER BY s.fetched_at DESC
        """
        res_sources = ch.query(query_sources)
        cols_s = res_sources.column_names
        for row in res_sources.result_rows:
            if len(news) >= limit:
                break
            d = dict(zip(cols_s, row))
            url = d.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            news.append({
                "fixture_id": d.get("fixture_id"),
                "url": url,
                "title": d.get("title") or "Match News",
                "snippet": d.get("snippet") or "",
                "source_name": "Grounding Evidence",
                "fetched_at": to_utc_iso(d.get("fetched_at")),
                "home_team": d.get("home_team") or "",
                "away_team": d.get("away_team") or ""
            })
            
    return news



def get_live_match_data() -> dict:
    ch = client()
    # Get the latest assess task created event
    res = ch.query("""
        SELECT fixture_id, payload, ts 
        FROM task_events 
        WHERE task_type = 'assess' AND event_type = 'created' 
        ORDER BY ts DESC 
        LIMIT 1
    """)
    if not res.result_rows:
        return {}
    
    main_fixture_id, payload_str, ts = res.result_rows[0]
    
    # Avoid stale live states from completed or offline simulations.
    # Discard live score overlay if the last tick was more than 120 seconds ago.
    from datetime import timezone
    ts_aware = ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts
    now_utc = datetime.now(timezone.utc)
    if (now_utc - ts_aware).total_seconds() > 120:
        return {}
        
    try:
        payload = json.loads(payload_str)
    except Exception:
        return {}
    
    minute = payload.get("minute", 0)
    score = payload.get("score", "0-0")
    other_scores = payload.get("other_scores", {})
    
    match_data = {}
    
    # Determine main fixture status
    if minute >= 90:
        main_status = "finished"
    elif minute > 0:
        main_status = "live"
    else:
        main_status = "scheduled"
        
    match_data[main_fixture_id] = {
        "minute": minute,
        "score": score,
        "status": main_status
    }
    
    # Map other fixtures
    for other_id, other_score in other_scores.items():
        if minute >= 90:
            other_status = "finished"
        elif minute > 0:
            other_status = "live"
        else:
            other_status = "scheduled"
            
        match_data[other_id] = {
            "minute": minute,
            "score": other_score,
            "status": other_status
        }
        
    return match_data


def compute_live_standings():
    ch = client()
    # Fetch standings from db
    std_res = ch.query("SELECT group_id, team, played, won, drawn, lost, goals_for, goals_against, goal_diff, points, position FROM standings")
    cols = std_res.column_names
    
    standings_map = {}
    for row in std_res.result_rows:
        d = dict(zip(cols, row))
        standings_map[d["team"]] = {
            "group_id": d["group_id"],
            "team": d["team"],
            "played": int(d["played"]),
            "won": int(d["won"]),
            "drawn": int(d["drawn"]),
            "lost": int(d["lost"]),
            "goals_for": int(d["goals_for"]),
            "goals_against": int(d["goals_against"]),
            "goal_diff": int(d["goal_diff"]),
            "points": int(d["points"]),
            "position": int(d["position"])
        }
        
    live_data = get_live_match_data()
    
    fx_res = ch.query("""
        SELECT fixture_id,
               argMax(home_team, updated_at) AS home_team,
               argMax(away_team, updated_at) AS away_team
        FROM fixtures
        GROUP BY fixture_id
    """)
    fixtures_map = {r[0]: (r[1], r[2]) for r in fx_res.result_rows}
    
    for fid, match_info in live_data.items():
        if match_info["minute"] == 0:
            continue
            
        if fid not in fixtures_map:
            continue
            
        home_team, away_team = fixtures_map[fid]
        score_str = match_info["score"]
        try:
            home_goals, away_goals = map(int, score_str.split("-"))
        except Exception:
            continue
            
        if home_team in standings_map and away_team in standings_map:
            h = standings_map[home_team]
            a = standings_map[away_team]
            
            h["played"] += 1
            a["played"] += 1
            
            h["goals_for"] += home_goals
            h["goals_against"] += away_goals
            h["goal_diff"] += (home_goals - away_goals)
            
            a["goals_for"] += away_goals
            a["goals_against"] += home_goals
            a["goal_diff"] += (away_goals - home_goals)
            
            if home_goals > away_goals:
                h["won"] += 1
                h["points"] += 3
                a["lost"] += 1
            elif home_goals < away_goals:
                a["won"] += 1
                a["points"] += 3
                h["lost"] += 1
            else:
                h["drawn"] += 1
                h["points"] += 1
                a["drawn"] += 1
                a["points"] += 1
                
    groups = {}
    for team, stats in standings_map.items():
        gid = stats["group_id"]
        if gid not in groups:
            groups[gid] = []
        groups[gid].append(stats)
        
    for gid, teams_list in groups.items():
        teams_list.sort(key=lambda t: (t["points"], t["goal_diff"], t["goals_for"]), reverse=True)
        for idx, team_stats in enumerate(teams_list):
            team_stats["position"] = idx + 1
            
    all_teams = []
    for gid in sorted(groups.keys()):
        all_teams.extend(groups[gid])
        
    return all_teams


@app.get("/api/matches")
def get_matches():
    ch = client()
    fx_res = ch.query("""
        SELECT fixture_id,
               argMax(group_id, updated_at) AS group_id,
               argMax(home_team, updated_at) AS home_team,
               argMax(away_team, updated_at) AS away_team,
               argMax(kickoff, updated_at) AS kickoff,
               argMax(status, updated_at) AS status
        FROM fixtures
        GROUP BY fixture_id
        ORDER BY kickoff ASC
    """)
    cols = fx_res.column_names
    
    live_data = get_live_match_data()
    
    matches = []
    for row in fx_res.result_rows:
        d = dict(zip(cols, row))
        fid = d["fixture_id"]
        
        score = "0-0"
        minute = 0
        status = d["status"]
        
        if fid in live_data:
            score = live_data[fid]["score"]
            minute = live_data[fid]["minute"]
            status = live_data[fid]["status"]
            
        matches.append({
            "fixture_id": fid,
            "group_id": d["group_id"],
            "home_team": d["home_team"],
            "away_team": d["away_team"],
            "kickoff": to_utc_iso(d["kickoff"]),
            "status": status,
            "score": score,
            "minute": minute
        })
    return matches


@app.get("/api/standings")
def get_standings():
    return compute_live_standings()


@app.get("/api/round_of_32")
def get_round_of_32():
    live_standings = compute_live_standings()
    
    top2_teams = []
    third_placed_teams = []
    
    for team in live_standings:
        pos = team["position"]
        if pos <= 2:
            top2_teams.append(team)
        elif pos == 3:
            third_placed_teams.append(team)
            
    third_placed_teams.sort(key=lambda t: (t["points"], t["goal_diff"], t["goals_for"]), reverse=True)
    best_thirds = third_placed_teams[:8]
    
    projected = []
    for t in top2_teams:
        projected.append({
            "group_id": t["group_id"],
            "team": t["team"],
            "position": t["position"],
            "points": t["points"],
            "goal_diff": t["goal_diff"],
            "goals_for": t["goals_for"],
            "path": "top2"
        })
    for t in best_thirds:
        projected.append({
            "group_id": t["group_id"],
            "team": t["team"],
            "position": 3,
            "points": t["points"],
            "goal_diff": t["goal_diff"],
            "goals_for": t["goals_for"],
            "path": "best_third"
        })
        
    return projected


@app.get("/api/traces")
def get_traces():
    import json
    ch = client()
    query = """
        SELECT task_id, task_type, fixture_id, result, updated_at
        FROM tasks_current
        WHERE status = 'completed' AND task_type IN ('ground', 'strategy')
        ORDER BY updated_at DESC
        LIMIT 15
    """
    res = ch.query(query)
    traces = []
    cols = res.column_names
    for row in res.result_rows:
        d = dict(zip(cols, row))
        try:
            result_parsed = json.loads(d["result"]) if d["result"] else {}
        except Exception:
            result_parsed = {}
            
        traces.append({
            "task_id": d["task_id"],
            "task_type": d["task_type"],
            "fixture_id": d["fixture_id"],
            "result": result_parsed,
            "updated_at": to_utc_iso(d.get("updated_at"))
        })
    return traces

