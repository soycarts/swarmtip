import asyncio
from core.db import client
import core.tasks
from agents.context import agent as context_agent
from agents.strategy import agent as strategy_agent
from agents.pricing import agent as pricing_agent
from agents.publisher import agent as publisher_agent
from core import qualification

def handle_assess(task: dict):
    fx = task["fixture_id"]
    assess_id = task["task_id"]
    ground_id = core.tasks.spawn(assess_id, "agent", "ground", fixture_id=fx, actor="orchestrator", assignee="context", title=f"Ground context for {fx}")
    qualify_id = core.tasks.spawn(assess_id, "agent", "qualify", fixture_id=fx, actor="orchestrator", assignee="QualificationEngine", title=f"Derive qualification for {fx}")
    core.tasks.create("agent", "strategy", fixture_id=fx, actor="orchestrator", assignee="strategy", depends_on=[ground_id, qualify_id], title=f"Evaluate strategy for {fx}")
    return {"status": "spawned_children"}

HANDLERS = {
    "assess": handle_assess,
    "ground": context_agent.handle,
    "qualify": qualification.handle,
    "strategy": strategy_agent.handle,
    "price": pricing_agent.handle,
    "publish": publisher_agent.handle,
}

ACTORS = {
    "assess": "orchestrator",
    "ground": "context",
    "qualify": "QualificationEngine",
    "strategy": "strategy",
    "price": "pricing",
    "publish": "publisher",
}

async def check_and_trigger_fixtures():
    """
    Dual-frequency triggering mechanism:
    - Pre-match (scheduled): Checks once per hour.
    - In-play (live): Checks regularly (every minute via the Modal cron heartbeat).
    """
    print("Checking fixtures for scheduled (hourly) and live (regular) assessments...")
    try:
        ch = client()
        fixtures = [dict(zip(["fixture_id", "group_id", "home_team", "away_team", "status"], r))
                    for r in ch.query("SELECT fixture_id, group_id, home_team, away_team, status FROM fixtures").result_rows]
        current_tasks = core.tasks.current()
        import datetime
        now = datetime.datetime.utcnow()

        for fixture in fixtures:
            fx_id = fixture["fixture_id"]
            status = fixture["status"]
            
            fx_assess = [t for t in current_tasks if t["fixture_id"] == fx_id and t["task_type"] == "assess"]
            active_fx_tasks = [t for t in current_tasks if t["fixture_id"] == fx_id and t["status"] not in ("completed", "failed", "cancelled")]
            
            if fx_assess:
                last_assess_time = max(t["updated_at"] for t in fx_assess)
                if last_assess_time.tzinfo is not None:
                    last_assess_time = last_assess_time.replace(tzinfo=None)
                seconds_since_last = (now - last_assess_time).total_seconds()
            else:
                seconds_since_last = 999999.0

            if status == "live":
                # Regular live checks: if there is no active task chain for this fixture,
                # and it's been more than 60 seconds since the last check, trigger a new one.
                if not active_fx_tasks and seconds_since_last > 60.0:
                    print(f"[Orchestrator] Triggering regular live assessment for {fx_id}")
                    core.tasks.create(
                        kind="agent",
                        task_type="assess",
                        fixture_id=fx_id,
                        actor="orchestrator",
                        assignee="orchestrator",
                        title=f"Live in-play assess for {fx_id}",
                        payload={"minute": 0, "score": "0-0", "other_scores": {}}
                    )
            elif status == "scheduled":
                # Pre-match hourly assessments aligned to run at XX:45 each hour
                target_45 = now.replace(minute=45, second=0, microsecond=0)
                if now.minute < 45:
                    target_45 = target_45 - datetime.timedelta(hours=1)
                
                if not active_fx_tasks and last_assess_time < target_45:
                    print(f"[Orchestrator] Triggering pre-match hourly assessment for {fx_id} (target XX:45)")
                    core.tasks.create(
                        kind="agent",
                        task_type="assess",
                        fixture_id=fx_id,
                        actor="orchestrator",
                        assignee="orchestrator",
                        title=f"Hourly pre-match assess for {fx_id}",
                        payload={"minute": 0, "score": "0-0", "other_scores": {}}
                    )
    except Exception as e:
        print(f"Error in check_and_trigger_fixtures: {e}")

async def run_loop():
    print("Orchestrator loop started.")
    
    # 1. Trigger any necessary assessments based on match status and timing
    await check_and_trigger_fixtures()

    # 2. Main processing loop
    while True:
        claimable = core.tasks.claimable("agent")
        if not claimable:
            current = core.tasks.current()
            active_agent_tasks = [t for t in current if t["kind"] == "agent" and t["status"] not in ("completed", "failed", "cancelled")]
            if not active_agent_tasks:
                print("No active agent tasks. Exiting orchestrator loop gracefully.")
                break
            await asyncio.sleep(1)
            continue
            
        for task in claimable:
            ttype = task["task_type"]
            actor = ACTORS.get(ttype)
            if not actor:
                continue
                
            print(f"Claiming {ttype} for {task['fixture_id']}")
            core.tasks.claim(task["task_id"], actor)
            
            handler = HANDLERS[ttype]
            try:
                res = handler(task)
                core.tasks.complete(task["task_id"], actor, result=res)
            except Exception as e:
                print(f"Task {task['task_id']} failed: {e}")
                core.tasks.fail(task["task_id"], actor, result={"error": str(e)})
                
if __name__ == "__main__":
    asyncio.run(run_loop())
