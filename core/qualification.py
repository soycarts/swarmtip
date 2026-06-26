"""
Deterministic qualification engine.
Never let an LLM compute standings or best-third math.
"""
from core.db import client
from config import BEST_THIRD_POINTS

def derive_qualification(fixture: dict) -> dict:
    """
    Coarse Python stand-in for the Prometheux ontology.
    Swap point: Call Prometheux here once wired.
    """
    out = {}
    ch = client()
    rows = ch.query(
        "SELECT team, points FROM standings WHERE group_id = %(g)s",
        parameters={"g": fixture["group_id"]},
    ).result_rows
    pts = {team: p for team, p in rows}

    for team in (fixture["home_team"], fixture["away_team"]):
        draw_points = pts.get(team, 0) + 1
        if draw_points >= BEST_THIRD_POINTS:
            sufficient, path = 1, "best_third"
            reason = f"{draw_points} pts on a draw clears the ~{BEST_THIRD_POINTS}-pt third-place bar."
        else:
            sufficient, path = 0, "none"
            reason = f"{draw_points} pts on a draw is below the third-place bar; needs a win."
        out[team] = {"draw_points": draw_points, "draw_sufficient": sufficient,
                     "path": path, "reasoning": reason}
        ch.insert("qualification_signals",
                  [[fixture["fixture_id"], team, draw_points, sufficient,
                    path, reason, "fallback"]],
                  column_names=["fixture_id", "team", "draw_points",
                                "draw_sufficient", "path", "reasoning", "source"])
    return out

def classify_match(qual: dict, home: str, away: str) -> str:
    h, a = qual[home]["draw_sufficient"], qual[away]["draw_sufficient"]
    if h and a:
        return "mutual_draw"
    if not h and not a:
        return "both_must_win"
    return "one_sided"

import core.tasks

def handle(task: dict):
    fixture_id = task["fixture_id"]
    ch = client()
    
    existing = ch.query("SELECT count() FROM qualification_signals WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows[0][0]
    if existing > 0:
        return {"status": "already qualified"}
        
    fx_rows = ch.query("SELECT group_id, home_team, away_team FROM fixtures WHERE fixture_id = %(f)s", 
                       parameters={"f": fixture_id}).result_rows
    fixture = {"fixture_id": fixture_id, "group_id": fx_rows[0][0], "home_team": fx_rows[0][1], "away_team": fx_rows[0][2]}
    out = derive_qualification(fixture)
    return {"status": "qualified", "teams": list(out.keys())}
