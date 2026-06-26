from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.db import client

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
def get_tasks():
    ch = client()
    # Query tasks_current so we have task_id
    res = ch.query("SELECT task_id, status, kind, task_type, assigned_to, title, updated_at FROM tasks_current ORDER BY updated_at DESC LIMIT 50")
    tasks = []
    cols = res.column_names
    for row in res.result_rows:
        d = dict(zip(cols, row))
        tasks.append({
            "id": d["task_id"],
            "status": d["status"],
            "kind": d["kind"],
            "type": d["task_type"],
            "assigned": d["assigned_to"],
            "title": d["title"],
            "updated_at": d["updated_at"].isoformat() if d.get("updated_at") else None
        })
    return tasks

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
