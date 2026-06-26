import json
import os
import time

def yield_events(timeline_path="feeds/timelines/group_g.json", delay=2):
    """
    Yields events from the timeline, simulating the progression of a match.
    """
    with open(timeline_path, "r") as f:
        data = json.load(f)
        
    match_id = data["match_id"]
    for event in data["events"]:
        yield {
            "fixture_id": match_id,
            "minute": event["t"],
            "score": event["score"],
            "other_match_scores": event["other"],
            "draw_odds": event["draw_odds"]
        }
        time.sleep(delay)
