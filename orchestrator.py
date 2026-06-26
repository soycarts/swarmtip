import asyncio
from core.db import client
import core.tasks
from agents.context import agent as context_agent
from agents.strategy import agent as strategy_agent
from agents.pricing import agent as pricing_agent
from agents.publisher import agent as publisher_agent
from core import qualification

HANDLERS = {
    "ground": context_agent.handle,
    "qualify": qualification.handle,
    "strategy": strategy_agent.handle,
    "price": pricing_agent.handle,
    "publish": publisher_agent.handle,
}

ACTORS = {
    "ground": "context",
    "qualify": "QualificationEngine",
    "strategy": "strategy",
    "price": "pricing",
    "publish": "publisher",
}

async def run_loop():
    print("Orchestrator loop started.")
    ch = client()
    fx_rows = ch.query("SELECT fixture_id FROM fixtures WHERE status = 'scheduled'").result_rows
    
    for (fx,) in fx_rows:
        existing = core.tasks.current()
        if not any(t["task_type"] == "assess" and t["fixture_id"] == fx for t in existing):
            assess_id = core.tasks.create("agent", "assess", fixture_id=fx, actor="orchestrator", title=f"Assess fixture {fx}")
            core.tasks.claim(assess_id, "orchestrator")
            core.tasks.complete(assess_id, "orchestrator")
            
            ground_id = core.tasks.spawn(assess_id, "agent", "ground", fixture_id=fx, actor="context", title=f"Ground context for {fx}")
            qualify_id = core.tasks.spawn(assess_id, "agent", "qualify", fixture_id=fx, actor="QualificationEngine", title=f"Derive qualification for {fx}")
            
            core.tasks.create("agent", "strategy", fixture_id=fx, actor="strategy", depends_on=[ground_id, qualify_id], title=f"Evaluate strategy for {fx}")

    while True:
        claimable = core.tasks.claimable("agent")
        if not claimable:
            current = core.tasks.current()
            agent_tasks = [t for t in current if t["kind"] == "agent" and t["task_type"] != "assess"]
            if agent_tasks and all(t["status"] in ("completed", "failed") for t in agent_tasks):
                print("All tasks completed.")
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
