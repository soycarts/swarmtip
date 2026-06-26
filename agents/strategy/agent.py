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
    
    fx_rows = ch.query("SELECT home_team, away_team FROM fixtures WHERE fixture_id = %(f)s", 
                       parameters={"f": fixture_id}).result_rows
    home, away = fx_rows[0]
    
    q_rows = ch.query("SELECT team, draw_points, draw_sufficient, path, reasoning FROM qualification_signals WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows
    qual = {}
    for team, dp, ds, path, r in q_rows:
        qual[team] = {"draw_points": dp, "draw_sufficient": ds, "path": path, "reasoning": r}
    
    match_class = classify_match(qual, home, away)
    
    s_rows = ch.query("SELECT title, snippet, url FROM sources WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows
    sources = [{"title": r[0], "snippet": r[1], "url": r[2]} for r in s_rows]
    
    context = "\n".join(f"- {s['title']}: {s['snippet'][:300]} ({s['url']})" for s in sources)
    prompt = f"""You estimate the probability of a DRAW in a World Cup match.
Match: {home} vs {away}.
Qualification context (authoritative, from a rules engine):
- {home}: {qual[home]['reasoning']}
- {away}: {qual[away]['reasoning']}
- Incentive class: {match_class}
Grounded sources:
{context}

Weigh team strength from the sources, then adjust for incentive: a mutual_draw
class raises draw probability, both_must_win lowers it. Return ONLY a JSON
object: {{"draw_prob": <0..1>, "rationale": "<one sentence>", "play_for_draw": true}}."""

    resp = gemini.models.generate_content(model=config.GEMINI_MODEL, contents=prompt)
    
    # Strip markdown code blocks
    text = resp.text.strip()
    if text.startswith("```json"):
        text = text.removeprefix("```json").removesuffix("```").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").removesuffix("```").strip()
        
    data = json.loads(text)
    
    # spawn price task
    core.tasks.spawn(task["task_id"], "agent", "price", fixture_id=fixture_id, actor="strategy", assignee="pricing", payload={
        "model_draw_prob": data["draw_prob"],
        "play_for_draw": data["play_for_draw"]
    }, title=f"Price draw odds for {fixture_id}")
    
    return data
