from core.db import client
import os

def handle(task: dict):
    fixture_id = task["fixture_id"]
    ch = client()
    
    sig = ch.query("SELECT match_class, model_draw_prob, edge, recommendation FROM value_signals WHERE fixture_id = %(f)s", parameters={"f": fixture_id}).result_rows
    if not sig:
        return {"error": "no signal found"}
        
    with open("cited.md", "a") as f:
        f.write(f"# Cited Brief: {fixture_id}\n\n")
        f.write(f"Class: {sig[0][0]}\n")
        f.write(f"Model Prob: {sig[0][1]}\n")
        f.write(f"Edge: {sig[0][2]}\n")
        f.write(f"Rec: {sig[0][3]}\n\n")
        
    ch.command("ALTER TABLE value_signals UPDATE brief_url = 'cited.md' WHERE fixture_id = %(f)s", parameters={"f": fixture_id})
    return {"status": "published to cited.md"}
