import datetime
import os
import json
from google import genai
from google.genai import types
from tavily import TavilyClient
import config
from core.db import client
import core.tasks

gemini = genai.Client(api_key=config.GEMINI_API_KEY)
tavily = TavilyClient(api_key=config.TAVILY_API_KEY)

def handle(task: dict):
    fixture_id = task["fixture_id"]
    ch = client()
    
    # 1. Fetch fixture information
    fx_rows = ch.query(
        "SELECT home_team, away_team FROM fixtures WHERE fixture_id = %(f)s",
        parameters={"f": fixture_id}
    ).result_rows
    
    if not fx_rows:
        return {"error": f"Fixture {fixture_id} not found."}
        
    home, away = fx_rows[0]
    print(f"[OddsAgent] Fetching odds for {home} vs {away} ({fixture_id})")
    
    # 2. Query Tavily for match odds
    query = f"{home} vs {away} match 1X2 betting odds draw 2026"
    sources = []
    try:
        res = tavily.search(query=query, max_results=5, search_depth="advanced")
        for r in res.get("results", []):
            sources.append({
                "title": r.get("title", ""),
                "snippet": r.get("content", ""),
                "url": r.get("url", "")
            })
    except Exception as e:
        print(f"[OddsAgent] Tavily search failed: {e}")
        
    if not sources:
        print(f"[OddsAgent] No search results found. Using fallback odds.")
        # Fallback odds
        fallback = {
            "bookmaker": "Fallback Bookmaker",
            "home_odds": 2.50,
            "draw_odds": 3.20,
            "away_odds": 2.80,
            "rationale": "No search results returned by Tavily; using standard default soccer draw odds."
        }
        ch.insert("odds", [[
            fixture_id, fallback["bookmaker"],
            fallback["home_odds"], fallback["draw_odds"], fallback["away_odds"],
            datetime.datetime.now()
        ]], column_names=["fixture_id", "bookmaker", "home_odds", "draw_odds", "away_odds", "fetched_at"])
        return fallback

    # 3. Construct prompt for Gemini
    context = "\n".join(f"- {s['title']}: {s['snippet']} ({s['url']})" for s in sources)
    prompt = f"""You are a betting odds extractor. You MUST extract the standard 1X2 full-time match betting odds for this fixture.
Fixture: {home} vs {away}

Search Results context:
{context}

Extract:
1. One representative bookmaker name or 'Market Average' if a list or range is found.
2. Home team win odds (home_odds)
3. Draw odds (draw_odds)
4. Away team win odds (away_odds)

IMPORTANT RULES:
- You MUST convert any fractional odds (e.g. 5/1 becomes 6.0, 1/2 becomes 1.5) or American moneyline odds (e.g. +450 becomes 5.5, -200 becomes 1.5) into standard decimal format (as a float).
- Decimal odds are always positive floats >= 1.0.
- If multiple bookmakers/sportsbooks are listed, pick one reputable bookmaker or compute/extract a market average.
- If odds cannot be found or parsed from the text, return fallback values: home_odds=2.5, draw_odds=3.2, away_odds=2.8, and explain why in rationale.

Return ONLY a JSON object:
{{
  "bookmaker": "<Bookmaker Name>",
  "home_odds": <float>,
  "draw_odds": <float>,
  "away_odds": <float>,
  "rationale": "<Detailed conversion and extraction rationale, citing specific sources/URLs from context>"
}}"""

    # 4. Load soul.md as system instruction
    soul_path = os.path.join(os.path.dirname(__file__), "soul.md")
    system_instruction = None
    if os.path.exists(soul_path):
        with open(soul_path, "r") as f:
            system_instruction = f.read().strip()
            
    config_params = {}
    if system_instruction:
        config_params["system_instruction"] = system_instruction
    config_params["response_mime_type"] = "application/json"
    
    # 5. Generate content using Gemini
    resp = gemini.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(**config_params)
    )
    
    text = resp.text.strip()
    if text.startswith("```json"):
        text = text.removeprefix("```json").removesuffix("```").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").removesuffix("```").strip()
        
    data = json.loads(text)
    print(f"[OddsAgent] Parsed odds for {fixture_id}: {data}")
    
    # 6. Insert into ClickHouse odds table
    ch.insert("odds", [[
        fixture_id,
        data.get("bookmaker", "Market Average"),
        float(data.get("home_odds", 2.50)),
        float(data.get("draw_odds", 3.20)),
        float(data.get("away_odds", 2.80)),
        datetime.datetime.now()
    ]], column_names=["fixture_id", "bookmaker", "home_odds", "draw_odds", "away_odds", "fetched_at"])
    
    return data
