import argparse
import sys
import datetime

from core.db import client
import core.tasks
from feeds import sim, live

def run(mode="sim"):
    print(f"FeedAgent started in mode: {mode}")
    ch = client()
    
    if mode == "sim":
        feed_generator = sim.yield_events()
    else:
        feed_generator = live.yield_events()
        
    for event in feed_generator:
        fixture_id = event["fixture_id"]
        minute = event["minute"]
        score = event["score"]
        other_scores = event["other_match_scores"]
        draw_odds = event.get("draw_odds")
        
        print(f"[{minute}'] {fixture_id} score {score}, other {other_scores}, draw_odds {draw_odds}")
        
        if draw_odds:
            ch.insert("odds", [[
                fixture_id, "sim_bookmaker", 
                0.0, float(draw_odds), 0.0, 
                datetime.datetime.now()
            ]], column_names=["fixture_id", "bookmaker", "home_odds", "draw_odds", "away_odds", "fetched_at"])
            
        payload = {
            "minute": minute,
            "score": score,
            "other_scores": other_scores
        }
        
        task_id = core.tasks.create(
            kind="agent",
            task_type="assess",
            fixture_id=fixture_id,
            actor="feed",
            assignee="orchestrator",
            title=f"Assess fixture {fixture_id} at {minute}'",
            payload=payload
        )
        print(f"Spawned root assess task: {task_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FeedAgent")
    parser.add_argument("--mode", choices=["sim", "live"], default="sim", help="Run mode")
    args = parser.parse_args()
    run(mode=args.mode)
