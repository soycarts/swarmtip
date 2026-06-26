import asyncio
import datetime
from core.db import client
import core.tasks
from agents.context import agent as context_agent
from agents.strategy import agent as strategy_agent
from agents.pricing import agent as pricing_agent
from agents.publisher import agent as publisher_agent
from agents.kickoff import agent as kickoff_agent
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
    "research_kickoff": kickoff_agent.handle,
}

ACTORS = {
    "assess": "orchestrator",
    "ground": "context",
    "qualify": "QualificationEngine",
    "strategy": "strategy",
    "price": "pricing",
    "publish": "publisher",
    "research_kickoff": "kickoff",
}

async def check_and_trigger_fixtures():
    """
    Dual-frequency triggering mechanism:
    - Pre-match (scheduled): Checks once per hour.
    - In-play (live): Checks regularly (every minute via the Modal cron heartbeat).
    - Kickoff Research (Tavily): Autonomous kickoff verification.
    """
    print("Checking fixtures for scheduled (hourly) and live (regular) assessments...")
    try:
        ch = client()
        # Query utilizing ReplacingMergeTree properties to get the latest row per fixture
        fixtures = [dict(zip(["fixture_id", "group_id", "home_team", "away_team", "status", "kickoff"], r))
                    for r in ch.query("""
                        SELECT fixture_id,
                               argMax(group_id, updated_at) AS group_id,
                               argMax(home_team, updated_at) AS home_team,
                               argMax(away_team, updated_at) AS away_team,
                               argMax(status, updated_at) AS status,
                               argMax(kickoff, updated_at) AS kickoff
                        FROM fixtures
                        GROUP BY fixture_id
                    """).result_rows]
                    
        current_tasks = core.tasks.current()
        now = datetime.datetime.now(datetime.timezone.utc)

        for fixture in fixtures:
            fx_id = fixture["fixture_id"]
            status = fixture["status"]
            kickoff = fixture["kickoff"]
            group_id = fixture["group_id"]
            home = fixture["home_team"]
            away = fixture["away_team"]
            
            # Ensure kickoff is timezone-aware UTC for direct comparison with datetime.now(timezone.utc)
            if kickoff.tzinfo is None:
                kickoff = kickoff.replace(tzinfo=datetime.timezone.utc)

            # 1. Trigger kickoff research if not already started or completed
            kickoff_tasks = [t for t in current_tasks if t["fixture_id"] == fx_id and t["task_type"] == "research_kickoff"]
            if not kickoff_tasks:
                print(f"[Orchestrator] Triggering kickoff research task for {fx_id}")
                core.tasks.create(
                    kind="agent",
                    task_type="research_kickoff",
                    fixture_id=fx_id,
                    actor="orchestrator",
                    assignee="kickoff",
                    title=f"Research kickoff time for {fx_id}"
                )
                
            # 2. Dynamic Match Status Transition
            determined_status = "scheduled"
            if now >= kickoff:
                if now <= kickoff + datetime.timedelta(minutes=110):
                    determined_status = "live"
                else:
                    determined_status = "finished"
                    
            if status != determined_status:
                print(f"[Orchestrator] Transitioning {fx_id} status from '{status}' to '{determined_status}'")
                ch.insert(
                    "fixtures",
                    [[
                        fx_id, group_id, home, away, kickoff,
                        determined_status, datetime.datetime.now(datetime.timezone.utc)
                    ]],
                    column_names=["fixture_id", "group_id", "home_team", "away_team", "kickoff", "status", "updated_at"]
                )
                status = determined_status  # update local status reference for downstream checks

            # 3. Assessment Scheduling
            fx_assess = [t for t in current_tasks if t["fixture_id"] == fx_id and t["task_type"] == "assess"]
            active_fx_tasks = [t for t in current_tasks if t["fixture_id"] == fx_id and t["status"] not in ("completed", "failed", "cancelled")]
            
            if fx_assess:
                last_assess_time = max(t["updated_at"] for t in fx_assess)
                if last_assess_time.tzinfo is None:
                    last_assess_time = last_assess_time.replace(tzinfo=datetime.timezone.utc)
                seconds_since_last = (now - last_assess_time).total_seconds()
            else:
                last_assess_time = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
                seconds_since_last = 999999.0

            if status == "live":
                # Regular live checks: if there is no active task chain for this fixture,
                # and it's been more than 60 seconds since the last check, trigger a new one.
                if not active_fx_tasks and seconds_since_last > 60.0:
                    current_minute = int((now - kickoff).total_seconds() / 60)
                    current_minute = max(0, min(110, current_minute))
                    print(f"[Orchestrator] Triggering live in-play assessment for {fx_id} at {current_minute}'")
                    core.tasks.create(
                        kind="agent",
                        task_type="assess",
                        fixture_id=fx_id,
                        actor="orchestrator",
                        assignee="orchestrator",
                        title=f"Assess fixture {fx_id} at {current_minute}'",
                        payload={"minute": current_minute, "score": "0-0", "other_scores": {}}
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

async def check_and_trigger_news_fetch():
    """
    Checks if an hourly news_fetch task has already been created for the current hour start.
    If not, creates a news_fetch task on the ledger.
    """
    print("Checking if hourly news fetch needs to be triggered...")
    try:
        current_tasks = core.tasks.current()
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        current_hour_start = now.replace(minute=0, second=0, microsecond=0)
        
        # Check if there is any news_fetch task created in the current hour
        recent_news_fetches = []
        for t in current_tasks:
            if t["task_type"] == "news_fetch":
                created_at = t["created_at"]
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=datetime.timezone.utc)
                if created_at >= current_hour_start:
                    recent_news_fetches.append(t)
                    
        if not recent_news_fetches:
            print(f"[Orchestrator] Spawning hourly news_fetch task for hour start {current_hour_start}")
            core.tasks.create(
                kind="agent",
                task_type="news_fetch",
                actor="orchestrator",
                assignee="news_gatherer",
                title=f"Hourly World Cup news feed update ({current_hour_start.strftime('%Y-%m-%d %H:00')} UTC)"
            )
        else:
            print("[Orchestrator] Hourly news_fetch task already exists for this hour.")
    except Exception as e:
        print(f"Error in check_and_trigger_news_fetch: {e}")

async def run_loop():
    print("Orchestrator loop started.")
    
    # 1. Trigger any necessary assessments based on match status and timing
    await check_and_trigger_fixtures()
    
    # 2. Trigger hourly news fetch if needed
    await check_and_trigger_news_fetch()

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
