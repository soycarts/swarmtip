from core.db import client
from tavily import TavilyClient
import config
import core.tasks
import traceback

tavily = TavilyClient(api_key=config.TAVILY_API_KEY)

def handle(task: dict):
    """
    Claims news_fetch task, finds all active (live or scheduled) fixtures,
    fetches recent match news from Tavily, and writes unique entries to match_news.
    """
    ch = client()
    
    # 1. Fetch active fixtures
    fx_rows = ch.query(
        "SELECT fixture_id, home_team, away_team FROM fixtures WHERE status IN ('live', 'scheduled')"
    ).result_rows
    
    if not fx_rows:
        return {"status": "no active fixtures to gather news for"}
        
    stats = {}
    for fx_id, home, away in fx_rows:
        try:
            print(f"[NewsAgent] Gathering news for {fx_id} ({home} vs {away})...")
            
            # 2. Query Tavily for match news
            q = f"{home} {away} World Cup 2026 team news lineup injuries"
            res = tavily.search(query=q, max_results=3, search_depth="advanced")
            
            inserted_count = 0
            for r in res.get("results", []):
                url = r["url"]
                title = r["title"]
                snippet = r["content"]
                
                # 3. Check for duplicates in match_news
                dup = ch.query(
                    "SELECT count() FROM match_news WHERE fixture_id = %(f)s AND url = %(u)s",
                    parameters={"f": fx_id, "u": url}
                ).result_rows[0][0]
                
                if dup == 0:
                    # 4. Insert news article into ClickHouse
                    ch.insert(
                        "match_news",
                        [[fx_id, title, url, snippet, "Tavily"]],
                        column_names=["fixture_id", "title", "url", "snippet", "source_name"]
                    )
                    inserted_count += 1
            
            stats[fx_id] = {"searched": True, "new_articles": inserted_count}
            
        except Exception as e:
            print(f"[NewsAgent] Error gathering news for {fx_id}: {e}")
            traceback.print_exc()
            stats[fx_id] = {"error": str(e)}
            
    return {"status": "news_gathered", "fixtures_processed": len(fx_rows), "details": stats}
