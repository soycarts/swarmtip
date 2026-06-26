"""
Verification script for Prometheux Qualification Reasoning engine.
Runs the logic solver over the Group G matchday fixtures and asserts the expected outcomes.
"""
import sys
import os

# Add parent directory to path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.qualification import derive_qualification

def main():
    print("==========================================================")
    print("VERIFYING PROMETHEUX QUALIFICATION REASONING ENGINE")
    print("==========================================================\n")
    
    # 1. Verify Egypt vs Iran
    print("--- Evaluating Fixture: G_EGY_IRN (Egypt vs Iran) ---")
    fixture_egy_irn = {
        "fixture_id": "G_EGY_IRN",
        "group_id": "G",
        "home_team": "Egypt",
        "away_team": "Iran"
    }
    
    res_egy_irn = derive_qualification(fixture_egy_irn)
    
    # Assertions and details for Egypt
    egy_res = res_egy_irn["Egypt"]
    print(f"\n[EGYPT]")
    print(f"Projected Draw Points: {egy_res['draw_points']}")
    print(f"Draw Sufficient: {egy_res['draw_sufficient']}")
    print(f"Path: '{egy_res['path']}'")
    print(f"Reasoning summary:\n{egy_res['reasoning'].split('--- PROMETHEUX')[0].strip()}")
    print("-" * 40)
    print(f"Detailed Prometheux Trace:\n{egy_res['reasoning']}")
    print("-" * 60)
    
    # Assertions and details for Iran
    irn_res = res_egy_irn["Iran"]
    print(f"\n[IRAN]")
    print(f"Projected Draw Points: {irn_res['draw_points']}")
    print(f"Draw Sufficient: {irn_res['draw_sufficient']}")
    print(f"Path: '{irn_res['path']}'")
    print(f"Reasoning summary:\n{irn_res['reasoning'].split('--- PROMETHEUX')[0].strip()}")
    print("-" * 40)
    print(f"Detailed Prometheux Trace:\n{irn_res['reasoning']}")
    print("-" * 60)
    
    # 2. Verify New Zealand vs Belgium
    print("\n--- Evaluating Fixture: G_NZL_BEL (New Zealand vs Belgium) ---")
    fixture_nzl_bel = {
        "fixture_id": "G_NZL_BEL",
        "group_id": "G",
        "home_team": "New Zealand",
        "away_team": "Belgium"
    }
    
    res_nzl_bel = derive_qualification(fixture_nzl_bel)
    
    # Assertions and details for Belgium
    bel_res = res_nzl_bel["Belgium"]
    print(f"\n[BELGIUM]")
    print(f"Projected Draw Points: {bel_res['draw_points']}")
    print(f"Draw Sufficient: {bel_res['draw_sufficient']}")
    print(f"Path: '{bel_res['path']}'")
    print(f"Reasoning summary:\n{bel_res['reasoning'].split('--- PROMETHEUX')[0].strip()}")
    print("-" * 40)
    print(f"Detailed Prometheux Trace:\n{bel_res['reasoning']}")
    print("-" * 60)
    
    # Assertions and details for New Zealand
    nzl_res = res_nzl_bel["New Zealand"]
    print(f"\n[NEW ZEALAND]")
    print(f"Projected Draw Points: {nzl_res['draw_points']}")
    print(f"Draw Sufficient: {nzl_res['draw_sufficient']}")
    print(f"Path: '{nzl_res['path']}'")
    print(f"Reasoning summary:\n{nzl_res['reasoning'].split('--- PROMETHEUX')[0].strip()}")
    print("-" * 40)
    print(f"Detailed Prometheux Trace:\n{nzl_res['reasoning']}")
    print("-" * 60)
    
    # Perform analytical checks
    print("\n================ RUNNING ASSERTIONS ================")
    
    # Egypt Check
    assert egy_res["draw_sufficient"] == 1, "Egypt should qualify under a draw."
    assert egy_res["path"] == "top2", "Egypt's qualification path should be top2."
    print("✔ Egypt assertion passed (qualifies via top2).")
    
    # Iran Check
    assert irn_res["draw_sufficient"] == 1, "Iran should qualify under a draw."
    assert irn_res["path"] == "best_third", "Iran's qualification path should be best_third."
    print("✔ Iran assertion passed (qualifies via best_third with GD 0).")
    
    # Belgium Check
    assert bel_res["draw_sufficient"] == 0, "Belgium should NOT qualify under a draw (GD -1)."
    assert bel_res["path"] == "none", "Belgium's qualification path should be none."
    print("✔ Belgium assertion passed (does NOT qualify, GD -1 < 0 threshold).")
    
    # New Zealand Check
    assert nzl_res["draw_sufficient"] == 0, "New Zealand should NOT qualify under a draw (2 pts)."
    assert nzl_res["path"] == "none", "New Zealand's qualification path should be none."
    print("✔ New Zealand assertion passed (does NOT qualify with 2 pts).")
    
    print("\n==========================================================")
    print("VERIFICATION COMPLETE: ALL ASSERTIONS PASSED SUCCESSFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    main()
