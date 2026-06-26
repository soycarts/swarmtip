from google import genai
import config
from core.db import client
from core.qualification import classify_match
import json
import core.tasks

gemini = genai.Client(api_key=config.GEMINI_API_KEY)

def handle(task: dict):
    fixture_id = task["fixture_id"]
    ch = client()
    
    fx_rows = ch.query("SELECT group_id, home_team, away_team FROM fixtures WHERE fixture_id = %(f)s", 
                       parameters={"f": fixture_id}).result_rows
    group_id, home, away = fx_rows[0]
    
    # Query latest group standings from the new view
    standings_rows = ch.query(
        "SELECT team, played, won, drawn, lost, goals_for, goals_against, goal_diff, points, position "
        "FROM group_standings_view WHERE group_id = %(g)s ORDER BY position ASC",
        parameters={"g": group_id}
    ).result_rows
    
    standings_md = "| Pos | Team | P | W | D | L | GF | GA | GD | Pts |\n|---|---|---|---|---|---|---|---|---|---|\n"
    for r in standings_rows:
        standings_md += f"| {r[9]} | {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]:+d} | {r[8]} |\n"
    
    q_rows = ch.query("SELECT team, draw_points, draw_sufficient, path, reasoning FROM qualification_signals WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows
    qual = {}
    for team, dp, ds, path, r in q_rows:
        qual[team] = {"draw_points": dp, "draw_sufficient": ds, "path": path, "reasoning": r}
    
    match_class = classify_match(qual, home, away)
    
    s_rows = ch.query("SELECT title, snippet, url FROM sources WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows
    sources = [{"title": r[0], "snippet": r[1], "url": r[2]} for r in s_rows]
    
    context = "\n".join(f"- {s['title']}: {s['snippet'][:300]} ({s['url']})" for s in sources)
    prompt = f"""You estimate the probability of a DRAW in a World Cup match.
Match: {home} vs {away} (Group {group_id}).

Current Group Standings:
{standings_md}

Qualification context (authoritative, from a rules engine):
- {home}: {qual[home]['reasoning']}
- {away}: {qual[away]['reasoning']}
- Incentive class: {match_class}

Grounded sources:
{context}

Weigh team strength from the sources, then adjust for incentive: a mutual_draw
class raises draw probability, both_must_win lowers it. Return ONLY a JSON
object: {{"draw_prob": <0..1>, "rationale": "<one sentence>", "play_for_draw": true}}."""

    from google.genai import types
    import os

    # Load soul.md as system instruction
    soul_path = os.path.join(os.path.dirname(__file__), "soul.md")
    system_instruction = None
    if os.path.exists(soul_path):
        with open(soul_path, "r") as f:
            system_instruction = f.read().strip()

    # Route model dynamically: Pro tier on a detected flip (mutual_draw), Flash otherwise
    if match_class == "mutual_draw":
        model_name = config.GEMINI_PRO_MODEL
        print(f"[StrategyAgent] FLIP detected! Escalated to Pro model: {model_name}")
    else:
        model_name = config.GEMINI_MODEL
        print(f"[StrategyAgent] Using standard model: {model_name}")

    # Build types.GenerateContentConfig
    config_params = {}
    if system_instruction:
        config_params["system_instruction"] = system_instruction
    config_params["response_mime_type"] = "application/json"

    resp = gemini.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(**config_params)
    )
    
    # Strip markdown code blocks if any
    text = resp.text.strip()
    if text.startswith("```json"):
        text = text.removeprefix("```json").removesuffix("```").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").removesuffix("```").strip()
        
    data = json.loads(text)
    
    # spawn price task
    core.tasks.spawn(task["task_id"], "agent", "price", fixture_id=fixture_id, actor="strategy", assignee="pricing", payload={
        "model_draw_prob": data["draw_prob"],
        "play_for_draw": data["play_for_draw"],
        "match_class": match_class
    }, title=f"Price draw odds for {fixture_id}")
    
    return data
