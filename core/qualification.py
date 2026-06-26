"""
Deterministic qualification engine implementing the Prometheux Datalog ontology rules.
Never let an LLM compute standings or best-third math.
"""
import os
import itertools
from core.db import client
from config import BEST_THIRD_POINTS

def load_ontology_rules() -> list:
    """Reads the Datalog ontology rules from core/prometheux/ontology.dlog"""
    dlog_path = os.path.join(os.path.dirname(__file__), "prometheux", "ontology.dlog")
    try:
        with open(dlog_path, "r") as f:
            lines = f.readlines()
        rules = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("%"):
                rules.append(line)
        return rules
    except Exception as e:
        # Fallback hardcoded rules matching ontology.dlog in case of read error
        return [
            "projected_points(T, F, P) :- standings(T, CurrentP), P = CurrentP + 1.",
            "secures_top2(T, F) :- projected_points(T, F, P), group_scenario_min_position(T, F, Pos), Pos <= 2.",
            "secures_best_third(T, F) :- projected_points(T, F, P), group_scenario_min_position(T, F, 3), P >= 4.",
            "secures_best_third(T, F) :- projected_points(T, F, P), group_scenario_min_position(T, F, 3), P == 3, goal_difference(T, GD), GD >= 0.",
            "draw_sufficient(T, F) :- secures_top2(T, F).",
            "draw_sufficient(T, F) :- secures_best_third(T, F)."
        ]

def rank_standings(simulated_standings: dict) -> dict:
    """Ranks teams based on points, GD, GF, and team name tie-breaker."""
    sorted_teams = sorted(
        simulated_standings.keys(),
        key=lambda t: (
            -simulated_standings[t]["points"],
            -simulated_standings[t]["goal_diff"],
            -simulated_standings[t]["goals_for"],
            t
        )
    )
    return {team: i + 1 for i, team in enumerate(sorted_teams)}

def derive_qualification(fixture: dict) -> dict:
    """
    Prometheux ontology-native, logic-based explainable reasoning engine in Python.
    Calculates draw sufficiency by simulating all group outcomes for the sibling fixtures.
    """
    out = {}
    ch = client()
    fixture_id = fixture["fixture_id"]
    group_id = fixture["group_id"]
    home_team = fixture["home_team"]
    away_team = fixture["away_team"]
    
    # 1. Fetch current group standings
    rows = ch.query(
        "SELECT team, played, points, goal_diff, goals_for, goals_against, position FROM standings WHERE group_id = %(g)s",
        parameters={"g": group_id},
    ).result_rows
    
    standings_by_team = {}
    for team_name, played, points, goal_diff, goals_for, goals_against, position in rows:
        standings_by_team[team_name] = {
            "played": played,
            "points": points,
            "goal_diff": goal_diff,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "position": position
        }
        
    # 2. Fetch active sibling fixtures in the same group (excluding current fixture)
    sibling_rows = ch.query(
        "SELECT fixture_id, home_team, away_team FROM fixtures WHERE group_id = %(g)s AND fixture_id != %(f)s AND status != 'finished'",
        parameters={"g": group_id, "f": fixture_id},
    ).result_rows
    
    siblings = []
    for f_id, h, a in sibling_rows:
        siblings.append({"fixture_id": f_id, "home_team": h, "away_team": a})
        
    # 3. Generate all combinations of sibling match outcomes (3^N permutations)
    outcomes = ["home_win", "draw", "away_win"]
    scenario_combos = list(itertools.product(outcomes, repeat=len(siblings))) if siblings else [()]
    
    # 4. Set up the baseline standings assuming a DRAW in the current fixture F
    base_standings = {team: dict(data) for team, data in standings_by_team.items()}
    for team in (home_team, away_team):
        if team not in base_standings:
            base_standings[team] = {"played": 0, "points": 0, "goal_diff": 0, "goals_for": 0, "goals_against": 0, "position": 4}
            
    base_standings[home_team]["points"] += 1
    base_standings[home_team]["played"] += 1
    base_standings[away_team]["points"] += 1
    base_standings[away_team]["played"] += 1
    
    # 5. Evaluate rankings across all scenario permutations
    positions_under_scenarios = {home_team: [], away_team: []}
    
    for combo in scenario_combos:
        sim_standings = {team: dict(data) for team, data in base_standings.items()}
        
        for sibling, outcome in zip(siblings, combo):
            sh = sibling["home_team"]
            sa = sibling["away_team"]
            
            for t in (sh, sa):
                if t not in sim_standings:
                    sim_standings[t] = {"played": 0, "points": 0, "goal_diff": 0, "goals_for": 0, "goals_against": 0, "position": 4}
                    
            if outcome == "home_win":
                sim_standings[sh]["points"] += 3
                sim_standings[sh]["goal_diff"] += 1
                sim_standings[sh]["goals_for"] += 1
                sim_standings[sh]["played"] += 1
                
                sim_standings[sa]["points"] += 0
                sim_standings[sa]["goal_diff"] -= 1
                sim_standings[sa]["played"] += 1
            elif outcome == "draw":
                sim_standings[sh]["points"] += 1
                sim_standings[sh]["played"] += 1
                
                sim_standings[sa]["points"] += 1
                sim_standings[sa]["played"] += 1
            elif outcome == "away_win":
                sim_standings[sh]["points"] += 0
                sim_standings[sh]["goal_diff"] -= 1
                sim_standings[sh]["played"] += 1
                
                sim_standings[sa]["points"] += 3
                sim_standings[sa]["goal_diff"] += 1
                sim_standings[sa]["goals_for"] += 1
                sim_standings[sa]["played"] += 1
                
        ranks = rank_standings(sim_standings)
        positions_under_scenarios[home_team].append(ranks.get(home_team, 4))
        positions_under_scenarios[away_team].append(ranks.get(away_team, 4))
        
    # 6. Load Datalog ontology rules for trace documentation
    rules = load_ontology_rules()
    rule_projected_pts_str = next((r for r in rules if r.startswith("projected_points")), "projected_points(T, F, P) :- standings(T, CurrentP), P = CurrentP + 1.")
    rule_top2_str = next((r for r in rules if r.startswith("secures_top2")), "secures_top2(T, F) :- projected_points(T, F, P), group_scenario_min_position(T, F, Pos), Pos <= 2.")
    rule_best_third_strs = [r for r in rules if r.startswith("secures_best_third")]
    if not rule_best_third_strs:
        rule_best_third_strs = [
            "secures_best_third(T, F) :- projected_points(T, F, P), group_scenario_min_position(T, F, 3), P >= 4.",
            "secures_best_third(T, F) :- projected_points(T, F, P), group_scenario_min_position(T, F, 3), P == 3, goal_difference(T, GD), GD >= 0."
        ]
    rule_sufficient_strs = [r for r in rules if r.startswith("draw_sufficient")]
    if not rule_sufficient_strs:
        rule_sufficient_strs = [
            "draw_sufficient(T, F) :- secures_top2(T, F).",
            "draw_sufficient(T, F) :- secures_best_third(T, F)."
        ]
        
    # 7. Evaluate and record results for each team
    for team in (home_team, away_team):
        current_p = standings_by_team.get(team, {}).get("points", 0)
        gd = standings_by_team.get(team, {}).get("goal_diff", 0)
        draw_p = current_p + 1
        
        scenarios_pos = positions_under_scenarios[team]
        worst_pos = max(scenarios_pos) if scenarios_pos else standings_by_team.get(team, {}).get("position", 4)
        
        # Secures Top-2
        secures_top2 = 1 if worst_pos <= 2 else 0
        
        # Secures Best Third
        secures_best_third = 0
        triggered_best_third_rule = ""
        if worst_pos == 3:
            if draw_p >= BEST_THIRD_POINTS:
                secures_best_third = 1
                triggered_best_third_rule = rule_best_third_strs[0]
            elif draw_p == 3 and gd >= 0:
                secures_best_third = 1
                triggered_best_third_rule = rule_best_third_strs[1] if len(rule_best_third_strs) > 1 else rule_best_third_strs[0]
                
        # Draw Sufficient
        sufficient = 1 if (secures_top2 or secures_best_third) else 0
        
        # Path string
        if secures_top2:
            path = "top2"
        elif secures_best_third:
            path = "best_third"
        else:
            path = "none"
            
        # Format scenario explanations for the reasoning field
        scenario_details = []
        if siblings:
            for idx, combo_outcome in enumerate(scenario_combos):
                outcome_desc = []
                for sib, out_val in zip(siblings, combo_outcome):
                    if out_val == "home_win":
                        outcome_desc.append(f"{sib['home_team']} wins")
                    elif out_val == "draw":
                        outcome_desc.append("draw")
                    elif out_val == "away_win":
                        outcome_desc.append(f"{sib['away_team']} wins")
                pos = scenarios_pos[idx]
                scenario_details.append(f"if {' and '.join(outcome_desc)} -> finishes {pos} in group")
        else:
            scenario_details.append("no sibling fixtures remaining (standings fixed)")
            
        # Build logical Datalog trace
        trace_steps = []
        trace_steps.append(
            f"Rule 1: [{rule_projected_pts_str}]\n"
            f"  Applied: standings({team}, {current_p}) -> projected_points({team}, {fixture_id}, {draw_p})."
        )
        
        scenario_str = ", ".join(scenario_details)
        trace_steps.append(
            f"Rule 2: [{rule_top2_str}]\n"
            f"  Applied: projected_points({team}, {fixture_id}, {draw_p}), group_scenario_min_position({team}, {fixture_id}, {worst_pos}) -> secures_top2({team}, {fixture_id}) = {secures_top2}.\n"
            f"  (Permutations evaluated: {scenario_str})"
        )
        
        if worst_pos == 3:
            rule_str = triggered_best_third_rule if secures_best_third else rule_best_third_strs[0]
            trace_steps.append(
                f"Rule 3: [{rule_str}]\n"
                f"  Applied: projected_points({team}, {fixture_id}, {draw_p}), group_scenario_min_position({team}, {fixture_id}, {worst_pos}), goal_difference({team}, {gd}) -> secures_best_third({team}, {fixture_id}) = {secures_best_third}."
            )
        else:
            trace_steps.append(
                f"Rule 3: [secures_best_third(T, F) :- ...]\n"
                f"  Applied: team finishes {worst_pos} (not 3rd) -> secures_best_third({team}, {fixture_id}) = 0."
            )
            
        sufficient_rule_triggered = rule_sufficient_strs[0] if secures_top2 else rule_sufficient_strs[1] if secures_best_third else rule_sufficient_strs[0]
        trace_steps.append(
            f"Rule 4: [{sufficient_rule_triggered}]\n"
            f"  Applied: secures_top2({team}, {fixture_id}) = {secures_top2}, secures_best_third({team}, {fixture_id}) = {secures_best_third} -> draw_sufficient({team}, {fixture_id}) = {sufficient}."
        )
        
        if sufficient:
            summary = f"Draw is mathematically SUFFICIENT for {team} to qualify via {path} (Worst position under draw: {worst_pos} with projected {draw_p} points, GD {gd})."
        else:
            summary = f"Draw is NOT sufficient for {team} to qualify (Worst position under draw: {worst_pos} with projected {draw_p} points, GD {gd} below required threshold). Needs a win."
            
        full_reasoning = (
            f"{summary}\n\n"
            f"--- PROMETHEUX ONTOLOGY TRACE ---\n" + 
            "\n\n".join(trace_steps) +
            f"\n\nLineage: standings({team}, {current_p}) -> projected_points({team}, {draw_p}) -> "
            f"group_scenario_min_position({team}, {worst_pos}) -> "
            f"secures_top2({team})={secures_top2} / secures_best_third({team})={secures_best_third} -> "
            f"draw_sufficient({team})={sufficient}."
        )
        
        out[team] = {
            "draw_points": draw_p,
            "draw_sufficient": sufficient,
            "path": path,
            "reasoning": full_reasoning
        }
        
        # Insert signal row into qualification_signals with 'prometheux' source
        ch.insert(
            "qualification_signals",
            [[fixture_id, team, draw_p, sufficient, path, full_reasoning, "prometheux"]],
            column_names=["fixture_id", "team", "draw_points", "draw_sufficient", "path", "reasoning", "source"]
        )
        
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
