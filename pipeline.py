"""
swarmtip: pipeline skeleton.

Flow per fixture:
  ground (Tavily) -> qualify (Prometheux, fallback here) -> analyse (Gemini)
  -> value signal -> cited.md

This runs end to end with the Python fallback before Prometheux is wired.
Swap derive_qualification() for the Prometheux call once the mentor pairing
is done; everything downstream stays the same.

Env vars expected:
  CLICKHOUSE_HOST / CLICKHOUSE_USER / CLICKHOUSE_PASSWORD
  TAVILY_API_KEY
  GEMINI_API_KEY
"""

import os
import json
import clickhouse_connect          # pip install clickhouse-connect
from tavily import TavilyClient    # pip install tavily-python
from google import genai           # pip install google-genai

# --- config ---------------------------------------------------------------
GEMINI_MODEL = "gemini-3.5-flash"  # confirm exact string against current SDK docs
BEST_THIRD_POINTS = 4              # historical heuristic; Prometheux does this properly

ch = clickhouse_connect.get_client(
    host=os.environ["CLICKHOUSE_HOST"],
    username=os.environ.get("CLICKHOUSE_USER", "default"),
    password=os.environ.get("CLICKHOUSE_PASSWORD", ""),
)
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


# --- 1. ground ------------------------------------------------------------
def ground_fixture(fixture: dict) -> list[dict]:
    """Pull current squad news, form, and qualification context for a fixture."""
    sources = []
    for q in [
        f"{fixture['home_team']} {fixture['away_team']} World Cup 2026 team news lineup",
        f"{fixture['home_team']} {fixture['away_team']} qualification scenario draw",
    ]:
        res = tavily.search(query=q, max_results=4, search_depth="advanced")
        for r in res["results"]:
            sources.append({
                "fixture_id": fixture["fixture_id"], "query": q,
                "url": r["url"], "title": r["title"], "snippet": r["content"],
            })
    if sources:
        ch.insert("sources", [list(s.values()) for s in sources],
                  column_names=list(sources[0].keys()))
    return sources


# --- 2. qualify (Prometheux replaces this; fallback keeps the spine alive) -
def derive_qualification(fixture: dict) -> dict:
    """
    Coarse Python stand-in for the Prometheux ontology.
    For each team: projected points on a draw, and whether that likely
    qualifies. Prometheux replaces this with proper cross-group ranking
    (top-2 logic + best-third comparison on points/GD/goals) AND lineage.
    """
    out = {}
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
        return "mutual_draw"        # both qualify on a draw -> draw prob elevated
    if not h and not a:
        return "both_must_win"      # NZ vs Belgium lands here -> avoid the draw
    return "one_sided"


# --- 3. analyse -----------------------------------------------------------
def estimate_draw_prob(fixture: dict, sources: list[dict],
                       qual: dict, match_class: str) -> float:
    """Gemini turns grounded facts + the qualification signal into a draw prob."""
    context = "\n".join(f"- {s['title']}: {s['snippet'][:300]} ({s['url']})"
                        for s in sources)
    prompt = f"""You estimate the probability of a DRAW in a World Cup match.
Match: {fixture['home_team']} vs {fixture['away_team']}.
Qualification context (authoritative, from a rules engine):
- {fixture['home_team']}: {qual[fixture['home_team']]['reasoning']}
- {fixture['away_team']}: {qual[fixture['away_team']]['reasoning']}
- Incentive class: {match_class}
Grounded sources:
{context}

Weigh team strength from the sources, then adjust for incentive: a mutual_draw
class raises draw probability, both_must_win lowers it. Return ONLY a JSON
object: {{"draw_prob": <0..1>, "rationale": "<one sentence>"}}."""
    resp = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    data = json.loads(resp.text.strip().removeprefix("```json").removesuffix("```").strip())
    return float(data["draw_prob"])


# --- 4. value signal ------------------------------------------------------
def compute_value(fixture: dict, model_draw_prob: float, match_class: str) -> dict:
    row = ch.query(
        "SELECT draw_odds FROM odds WHERE fixture_id = %(f)s "
        "ORDER BY fetched_at DESC LIMIT 1",
        parameters={"f": fixture["fixture_id"]},
    ).result_rows
    market = (1.0 / row[0][0]) if row else 0.0   # de-vig properly for production
    edge = model_draw_prob - market
    if match_class == "both_must_win":
        rec = "AVOID"
    elif edge > 0.03:
        rec = "BET_DRAW"
    else:
        rec = "NO_EDGE"
    signal = {"fixture_id": fixture["fixture_id"], "match_class": match_class,
              "model_draw_prob": model_draw_prob, "market_draw_prob": market,
              "edge": edge, "recommendation": rec, "brief_url": ""}
    ch.insert("value_signals", [list(signal.values())],
              column_names=list(signal.keys()))
    return signal


# --- 5. cited.md (stub, wire to Senso once confirmed) --------------------
def write_cited_md(fixture, sources, qual, signal):
    """Render an auditable brief: claim -> rule lineage -> sources -> edge."""
    # TODO: publish via Senso CLI so cited.md is satisfied properly + Senso prize.
    raise NotImplementedError


# --- main loop ------------------------------------------------------------
def run():
    fixtures = [dict(zip(["fixture_id", "group_id", "home_team", "away_team"], r))
                for r in ch.query(
                    "SELECT fixture_id, group_id, home_team, away_team "
                    "FROM fixtures WHERE status = 'scheduled'").result_rows]
    ranked = []
    for fx in fixtures:
        sources = ground_fixture(fx)
        qual = derive_qualification(fx)
        match_class = classify_match(qual, fx["home_team"], fx["away_team"])
        draw_prob = estimate_draw_prob(fx, sources, qual, match_class)
        signal = compute_value(fx, draw_prob, match_class)
        ranked.append(signal)
    ranked.sort(key=lambda s: s["edge"], reverse=True)
    for s in ranked:
        print(s["fixture_id"], s["match_class"], f"edge={s['edge']:+.3f}", s["recommendation"])


if __name__ == "__main__":
    run()