import os
import sys
import json

# Ensure workspace is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from api.index import compute_live_standings, get_live_match_data, get_matches, get_round_of_32

print("=== TESTING GET LIVE MATCH DATA ===")
live_data = get_live_match_data()
print("Live Match Data Overlay:")
print(json.dumps(live_data, indent=2))

print("\n=== TESTING COMPUTE LIVE STANDINGS ===")
standings = compute_live_standings()
print(f"Computed Standings ({len(standings)} teams):")
for t in standings:
    print(f"Group {t['group_id']} | Pos {t['position']} | {t['team']:<12} | P: {t['played']} | W: {t['won']} | D: {t['drawn']} | L: {t['lost']} | GF: {t['goals_for']} | GA: {t['goals_against']} | GD: {t['goal_diff']:+d} | Pts: {t['points']}")

print("\n=== TESTING GET MATCHES ===")
matches = get_matches()
print(f"Matches ({len(matches)} matches):")
for m in matches:
    print(f"Fixture: {m['fixture_id']} ({m['group_id']}) | {m['home_team']} vs {m['away_team']} | Status: {m['status']:<10} | Score: {m['score']:<5} | Minute: {m['minute']}'")

print("\n=== TESTING GET ROUND OF 32 ===")
r32 = get_round_of_32()
print(f"Projected R32 Qualifiers ({len(r32)} teams):")
for t in r32:
    print(f"Group {t['group_id']} | Pos {t['position']} | {t['team']:<12} | Path: {t['path']:<12} | Pts: {t['points']} | GD: {t['goal_diff']:+d}")
