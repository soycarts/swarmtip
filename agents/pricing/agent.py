from core.db import client
import core.tasks
import config

def handle(task: dict):
    fixture_id = task["fixture_id"]
    payload = task.get("payload", {})
    model_draw_prob = float(payload.get("model_draw_prob", 0.0))
    match_class = payload.get("match_class", "")
    
    ch = client()
    existing = ch.query("SELECT count() FROM value_signals WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows[0][0]
    if existing > 0:
        return {"status": "already priced"}
    
    row = ch.query(
        "SELECT draw_odds FROM odds WHERE fixture_id = %(f)s "
        "ORDER BY fetched_at DESC LIMIT 1",
        parameters={"f": fixture_id},
    ).result_rows
    market = (1.0 / row[0][0]) if row else 0.0
    edge = model_draw_prob - market
    if match_class == "both_must_win":
        rec = "AVOID"
    elif edge > config.EDGE_MIN:
        rec = "BET_DRAW"
    else:
        rec = "NO_EDGE"
        
    signal = {"fixture_id": fixture_id, "match_class": match_class,
              "model_draw_prob": model_draw_prob, "market_draw_prob": market,
              "edge": edge, "recommendation": rec, "brief_url": ""}
    ch.insert("value_signals", [list(signal.values())],
              column_names=list(signal.keys()))
              
    if edge >= config.EDGE_MIN:
        core.tasks.spawn(task["task_id"], "agent", "publish", fixture_id=fixture_id, actor="pricing", assignee="publisher", title=f"Publish value signal for {fixture_id}")
        
    return {"edge": edge, "recommendation": rec}
