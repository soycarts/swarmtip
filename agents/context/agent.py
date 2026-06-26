from core.db import client
from tavily import TavilyClient
import config
import core.tasks

tavily = TavilyClient(api_key=config.TAVILY_API_KEY)

def handle(task: dict):
    fixture_id = task["fixture_id"]
    ch = client()
    
    fx_rows = ch.query("SELECT home_team, away_team FROM fixtures WHERE fixture_id = %(f)s", 
                       parameters={"f": fixture_id}).result_rows
    if not fx_rows:
        return {"error": "fixture not found"}
    home, away = fx_rows[0]

    existing = ch.query("SELECT count() FROM sources WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows[0][0]
    if existing > 0:
        rows = ch.query("SELECT query, url, title, snippet FROM sources WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows
        sources = [{"fixture_id": fixture_id, "query": r[0], "url": r[1], "title": r[2], "snippet": r[3]} for r in rows]
        return {
            "status": "already grounded",
            "sources_count": len(sources),
            "queries_run": list(set(s["query"] for s in sources)),
            "sources": sources
        }

    sources = []
    queries = [
        f"{home} {away} World Cup 2026 team news lineup",
        f"{home} {away} qualification scenario draw",
    ]
    for q in queries:
        res = tavily.search(query=q, max_results=4, search_depth="advanced")
        for r in res["results"]:
            sources.append({
                "fixture_id": fixture_id, "query": q,
                "url": r["url"], "title": r["title"], "snippet": r["content"],
            })
    if sources:
        ch.insert("sources", [list(s.values()) for s in sources],
                  column_names=list(sources[0].keys()))
    return {
        "status": "grounded",
        "sources_count": len(sources),
        "queries_run": queries,
        "sources": sources
    }
