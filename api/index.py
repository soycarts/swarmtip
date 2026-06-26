from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.db import client
import re

app = FastAPI()

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
            "created_at": d["created_at"].isoformat() if d.get("created_at") else None,
            "resolved_at": resolved_at_val.isoformat() if resolved_at_val else None,
            "updated_at": d["updated_at"].isoformat() if d.get("updated_at") else None
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
    res = ch.query("SELECT fixture_id, match_class, recommendation, model_draw_prob, edge FROM value_signals ORDER BY ts DESC LIMIT 10")
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
