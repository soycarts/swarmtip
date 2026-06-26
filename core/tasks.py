"""
swarmtip: the canonical task ledger over ClickHouse.

Every actor (coding tools, the orchestrator, and the runtime agents) logs work here:
open a task, close it, or assign it to another actor. The append-only table
`task_events` is the source of truth; current state is computed with argMax, so there
is one live view of everything moving in the project.

API (runtime swarm):  create, claim, complete, spawn
Extras:               open_task, start, fail, cancel, current, claimable
CLI (coding tools):   python -m core.tasks start | done | assign | list

Env: CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD,
     CLICKHOUSE_SECURE (true for ClickHouse Cloud), CLICKHOUSE_DATABASE
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from typing import Any

import clickhouse_connect

TABLE = "task_events"
TERMINAL = {"completed", "failed", "cancelled"}

from core.db import client


_COLUMNS = ["task_id", "event_type", "kind", "task_type", "actor", "assignee",
            "fixture_id", "depends_on", "parent_task", "title", "payload", "result"]


def _emit(task_id: str, event_type: str, *, kind: str = "agent", task_type: str = "",
          actor: str = "", assignee: str = "", fixture_id: str = "", depends_on: list[str] | None = None,
          parent_task: str = "", title: str = "",
          payload: Any = None, result: Any = None) -> str:
    """Append one event to the ledger. event_id and ts use their column defaults."""
    row = [task_id, event_type, kind, task_type, actor, assignee,
           fixture_id, depends_on or [], parent_task, title,
           json.dumps(payload or {}), json.dumps(result or {})]
    client().insert(TABLE, [row], column_names=_COLUMNS)
    return task_id


def _new_id(task_type: str) -> str:
    return f"{task_type or 'task'}-{uuid.uuid4().hex[:8]}"


# --- documented API -------------------------------------------------------------------

def create(kind: str, task_type: str, *, title: str = "", fixture_id: str = "",
           depends_on: list[str] | None = None, parent: str = "",
           actor: str = "", assignee: str = "", payload: Any = None) -> str:
    """Create a claimable task (status 'created'). Returns the task_id."""
    tid = _new_id(task_type)
    return _emit(tid, "created", kind=kind, task_type=task_type, actor=actor, assignee=assignee,
                 fixture_id=fixture_id, depends_on=depends_on, parent_task=parent,
                 title=title, payload=payload)


def claim(task_id: str, actor: str) -> str:
    """Mark a task claimed by an actor."""
    return _emit(task_id, "claimed", actor=actor)


def complete(task_id: str, actor: str, result: Any = None) -> str:
    """Close a task as completed."""
    return _emit(task_id, "completed", actor=actor, result=result)


def spawn(parent: str, kind: str, task_type: str, *, fixture_id: str = "",
          title: str = "", actor: str = "", assignee: str = "", payload: Any = None) -> str:
    """Create a child task that depends on `parent`. Returns the new task_id."""
    return create(kind, task_type, title=title, fixture_id=fixture_id,
                  depends_on=[parent], parent=parent, actor=actor, assignee=assignee, payload=payload)


# --- extras ---------------------------------------------------------------------------

def open_task(kind: str, task_type: str, *, title: str = "", actor: str = "", assignee: str = "",
              fixture_id: str = "", depends_on: list[str] | None = None) -> str:
    """Create a task already in progress ('started'). For an actor beginning work now."""
    tid = _new_id(task_type)
    return _emit(tid, "started", kind=kind, task_type=task_type, actor=actor, assignee=assignee,
                 fixture_id=fixture_id, depends_on=depends_on, title=title)


def start(task_id: str, actor: str) -> str:
    return _emit(task_id, "started", actor=actor)


def fail(task_id: str, actor: str, result: Any = None) -> str:
    return _emit(task_id, "failed", actor=actor, result=result)


def cancel(task_id: str, actor: str = "") -> str:
    return _emit(task_id, "cancelled", actor=actor)


_CURRENT_SQL = f"""
SELECT task_id,
       argMax(event_type, ts) AS status,
       argMax(kind, ts)       AS kind,
       argMaxIf(task_type, ts, task_type != '')  AS task_type,
       argMaxIf(assignee, ts, assignee != '')      AS assigned_to,
       argMinIf(actor, ts, event_type IN ('created', 'started')) AS created_by,
       argMaxIf(actor, ts, event_type = 'completed')             AS completed_by,
       argMaxIf(fixture_id, ts, fixture_id != '') AS fixture_id,
       argMaxIf(depends_on, ts, notEmpty(depends_on)) AS depends_on,
       argMaxIf(title, ts, title != '')      AS title,
       argMaxIf(payload, ts, payload != '{{}}' AND payload != '') AS payload,
       argMaxIf(result, ts, result != '{{}}' AND result != '')  AS result,
       min(ts)                AS created_at,
       max(ts)                AS updated_at
FROM {TABLE}
GROUP BY task_id
"""


def current() -> list[dict]:
    """Current state of every task (latest event wins). Self-contained, no view needed."""
    res = client().query(_CURRENT_SQL)
    out = []
    for row in res.result_rows:
        d = dict(zip(res.column_names, row))
        if "payload" in d and d["payload"]:
            try: d["payload"] = json.loads(d["payload"])
            except: d["payload"] = {}
        if "result" in d and d["result"]:
            try: d["result"] = json.loads(d["result"])
            except: d["result"] = {}
        out.append(d)
    return out


def claimable(kind: str | None = None, task_type: str | None = None) -> list[dict]:
    """Tasks that are 'created' and whose dependencies are all 'completed'."""
    rows = current()
    status = {r["task_id"]: r["status"] for r in rows}
    out = []
    for r in rows:
        if r["status"] != "created":
            continue
        if kind and r["kind"] != kind:
            continue
        if task_type and r["task_type"] != task_type:
            continue
        if all(status.get(d) == "completed" for d in r["depends_on"]):
            out.append(r)
    return out


# --- CLI ------------------------------------------------------------------------------

def _print_rows(rows: list[dict]) -> None:
    if not rows:
        print("(no tasks)")
        return
    for r in sorted(rows, key=lambda x: str(x.get("updated_at")), reverse=True):
        dep = f"  deps={list(r['depends_on'])}" if r.get("depends_on") else ""
        print(f"{r['status']:<9} {r['kind']:<6} {r['task_type']:<9} "
              f"{(r.get('assigned_to') or '-'):<12} {r['task_id']:<16} "
              f"{r.get('title', '')}{dep}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="core.tasks", description="swarmtip task ledger")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="open a new task already in progress")
    s.add_argument("--actor", required=True)
    s.add_argument("--kind", default="coding", choices=["coding", "agent"])
    s.add_argument("--type", required=True, dest="task_type")
    s.add_argument("--title", required=True)
    s.add_argument("--fixture", default="")
    s.add_argument("--depends", default="", help="comma-separated task_ids")

    d = sub.add_parser("done", help="close a task as completed")
    d.add_argument("task_id")
    d.add_argument("--actor", required=True)
    d.add_argument("--result", default="{}", help="JSON string")

    a = sub.add_parser("assign", help="create a task for another actor")
    a.add_argument("--actor", required=True, help="who is assigning this task")
    a.add_argument("--to", required=True)
    a.add_argument("--kind", default="coding", choices=["coding", "agent"])
    a.add_argument("--type", required=True, dest="task_type")
    a.add_argument("--title", required=True)
    a.add_argument("--after", default="", help="task_id this one depends on")

    li = sub.add_parser("list", help="show tasks")
    g = li.add_mutually_exclusive_group()
    g.add_argument("--open", action="store_true", help="open tasks (default)")
    g.add_argument("--mine", default="", help="open tasks for this actor")
    g.add_argument("--board", action="store_true", help="every task, most recent first")

    args = p.parse_args(argv)

    if args.cmd == "start":
        deps = [x for x in args.depends.split(",") if x]
        print(open_task(args.kind, args.task_type, title=args.title,
                        actor=args.actor, assignee=args.actor, fixture_id=args.fixture, depends_on=deps))
    elif args.cmd == "done":
        complete(args.task_id, args.actor, result=json.loads(args.result))
        print(f"closed {args.task_id}")
    elif args.cmd == "assign":
        deps = [args.after] if args.after else None
        print(create(args.kind, args.task_type, title=args.title,
                     actor=args.actor, assignee=args.to, depends_on=deps, parent=args.after))
    elif args.cmd == "list":
        rows = current()
        if args.mine:
            rows = [r for r in rows if r.get("assigned_to") == args.mine
                    and r["status"] not in TERMINAL]
        elif not args.board:
            rows = [r for r in rows if r["status"] not in TERMINAL]
        _print_rows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())