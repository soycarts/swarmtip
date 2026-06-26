import datetime
from core.db import client

def seed():
    ch = client()
    print("Seeding official 2026 World Cup fixtures and odds (A-F finished, G-L scheduled)...")

    # Define the 48 fixtures (6 per group for Groups A-F finished, 2 per group for Groups G-L scheduled)
    # Groups A to F are completed (status: 'finished')
    # Groups G to L are upcoming/scheduled (status: 'scheduled')
    # fixture_id, group_id, home_team, away_team, kickoff, status
    fixtures_data = [
        # Group A (Completed)
        ("A_MEX_RSA", "A", "Mexico", "South Africa", datetime.datetime(2026, 6, 11, 13, 0), "finished"),
        ("A_KOR_CZE", "A", "South Korea", "Czech Republic", datetime.datetime(2026, 6, 11, 16, 0), "finished"),
        ("A_CZE_RSA", "A", "Czech Republic", "South Africa", datetime.datetime(2026, 6, 16, 14, 0), "finished"),
        ("A_MEX_KOR", "A", "Mexico", "South Korea", datetime.datetime(2026, 6, 16, 17, 0), "finished"),
        ("A_MEX_CZE", "A", "Mexico", "Czech Republic", datetime.datetime(2026, 6, 25, 15, 0), "finished"),
        ("A_RSA_KOR", "A", "South Africa", "South Korea", datetime.datetime(2026, 6, 25, 15, 0), "finished"),

        # Group B (Completed)
        ("B_CAN_BIH", "B", "Canada", "Bosnia & Herzegovina", datetime.datetime(2026, 6, 12, 13, 0), "finished"),
        ("B_QAT_SUI", "B", "Qatar", "Switzerland", datetime.datetime(2026, 6, 12, 16, 0), "finished"),
        ("B_CAN_QAT", "B", "Canada", "Qatar", datetime.datetime(2026, 6, 17, 14, 0), "finished"),
        ("B_SUI_BIH", "B", "Switzerland", "Bosnia & Herzegovina", datetime.datetime(2026, 6, 17, 17, 0), "finished"),
        ("B_SUI_CAN", "B", "Switzerland", "Canada", datetime.datetime(2026, 6, 25, 15, 0), "finished"),
        ("B_BIH_QAT", "B", "Bosnia & Herzegovina", "Qatar", datetime.datetime(2026, 6, 25, 15, 0), "finished"),

        # Group C (Completed)
        ("C_BRA_MAR", "C", "Brazil", "Morocco", datetime.datetime(2026, 6, 13, 13, 0), "finished"),
        ("C_SCO_HAI", "C", "Scotland", "Haiti", datetime.datetime(2026, 6, 13, 16, 0), "finished"),
        ("C_SCO_MAR", "C", "Scotland", "Morocco", datetime.datetime(2026, 6, 18, 14, 0), "finished"),
        ("C_BRA_HAI", "C", "Brazil", "Haiti", datetime.datetime(2026, 6, 18, 17, 0), "finished"),
        ("C_SCO_BRA", "C", "Scotland", "Brazil", datetime.datetime(2026, 6, 25, 18, 0), "finished"),
        ("C_MAR_HAI", "C", "Morocco", "Haiti", datetime.datetime(2026, 6, 25, 18, 0), "finished"),

        # Group D (Completed)
        ("D_USA_PAR", "D", "USA", "Paraguay", datetime.datetime(2026, 6, 14, 13, 0), "finished"),
        ("D_AUS_TUR", "D", "Australia", "Turkey", datetime.datetime(2026, 6, 14, 16, 0), "finished"),
        ("D_USA_AUS", "D", "USA", "Australia", datetime.datetime(2026, 6, 19, 14, 0), "finished"),
        ("D_PAR_TUR", "D", "Paraguay", "Turkey", datetime.datetime(2026, 6, 19, 17, 0), "finished"),
        ("D_TUR_USA", "D", "Turkey", "USA", datetime.datetime(2026, 6, 25, 18, 0), "finished"),
        ("D_AUS_PAR", "D", "Australia", "Paraguay", datetime.datetime(2026, 6, 25, 18, 0), "finished"),

        # Group E (Completed)
        ("E_GER_CUW", "E", "Germany", "Curaçao", datetime.datetime(2026, 6, 15, 13, 0), "finished"),
        ("E_CIV_ECU", "E", "Ivory Coast", "Ecuador", datetime.datetime(2026, 6, 15, 16, 0), "finished"),
        ("E_GER_CIV", "E", "Germany", "Ivory Coast", datetime.datetime(2026, 6, 20, 14, 0), "finished"),
        ("E_ECU_CUW", "E", "Ecuador", "Curaçao", datetime.datetime(2026, 6, 20, 17, 0), "finished"),
        ("E_CIV_CUW", "E", "Ivory Coast", "Curaçao", datetime.datetime(2026, 6, 25, 21, 0), "finished"),
        ("E_ECU_GER", "E", "Ecuador", "Germany", datetime.datetime(2026, 6, 25, 21, 0), "finished"),

        # Group F (Completed)
        ("F_NED_JPN", "F", "Netherlands", "Japan", datetime.datetime(2026, 6, 16, 13, 0), "finished"),
        ("F_SWE_TUN", "F", "Sweden", "Tunisia", datetime.datetime(2026, 6, 16, 16, 0), "finished"),
        ("F_NED_SWE", "F", "Netherlands", "Sweden", datetime.datetime(2026, 6, 21, 14, 0), "finished"),
        ("F_TUN_JPN", "F", "Tunisia", "Japan", datetime.datetime(2026, 6, 21, 17, 0), "finished"),
        ("F_TUN_NED", "F", "Tunisia", "Netherlands", datetime.datetime(2026, 6, 25, 21, 0), "finished"),
        ("F_JPN_SWE", "F", "Japan", "Sweden", datetime.datetime(2026, 6, 25, 21, 0), "finished"),

        # Group G (Scheduled)
        ("G_EGY_IRN", "G", "Egypt", "Iran", datetime.datetime(2026, 6, 27, 4, 0), "scheduled"),
        ("G_NZL_BEL", "G", "New Zealand", "Belgium", datetime.datetime(2026, 6, 27, 4, 0), "scheduled"),

        # Group H (Scheduled)
        ("H_CPV_KSA", "H", "Cape Verde", "Saudi Arabia", datetime.datetime(2026, 6, 27, 1, 0), "scheduled"),
        ("H_URU_ESP", "H", "Uruguay", "Spain", datetime.datetime(2026, 6, 27, 1, 0), "scheduled"),

        # Group I (Scheduled)
        ("I_FRA_NOR", "I", "France", "Norway", datetime.datetime(2026, 6, 27, 18, 0), "scheduled"),
        ("I_SEN_IRQ", "I", "Senegal", "Iraq", datetime.datetime(2026, 6, 27, 18, 0), "scheduled"),

        # Group J (Scheduled)
        ("J_ALG_AUT", "J", "Algeria", "Austria", datetime.datetime(2026, 6, 28, 3, 0), "scheduled"),
        ("J_JOR_ARG", "J", "Jordan", "Argentina", datetime.datetime(2026, 6, 28, 3, 0), "scheduled"),

        # Group K (Scheduled)
        ("K_COL_POR", "K", "Colombia", "Portugal", datetime.datetime(2026, 6, 28, 0, 30), "scheduled"),
        ("K_COD_UZB", "K", "Congo DR", "Uzbekistan", datetime.datetime(2026, 6, 28, 0, 30), "scheduled"),

        # Group L (Scheduled)
        ("L_CRO_GHA", "L", "Croatia", "Ghana", datetime.datetime(2026, 6, 27, 22, 0), "scheduled"),
        ("L_PAN_ENG", "L", "Panama", "England", datetime.datetime(2026, 6, 27, 22, 0), "scheduled"),
    ]

    # Market odds per fixture
    odds_data = [
        # Group A
        ("A_MEX_RSA", "Bet365", 1.80, 3.40, 4.80),
        ("A_KOR_CZE", "Bet365", 2.20, 3.20, 3.40),
        ("A_CZE_RSA", "Bet365", 2.30, 3.20, 3.20),
        ("A_MEX_KOR", "Bet365", 1.70, 3.50, 5.25),
        ("A_MEX_CZE", "Bet365", 1.60, 3.80, 5.50),
        ("A_RSA_KOR", "Bet365", 2.60, 3.10, 2.80),

        # Group B
        ("B_CAN_BIH", "Bet365", 2.10, 3.25, 3.60),
        ("B_QAT_SUI", "Bet365", 5.50, 3.80, 1.62),
        ("B_CAN_QAT", "Bet365", 1.40, 4.50, 8.00),
        ("B_SUI_BIH", "Bet365", 1.80, 3.40, 4.75),
        ("B_SUI_CAN", "Bet365", 2.15, 3.30, 3.40),
        ("B_BIH_QAT", "Bet365", 1.75, 3.60, 4.60),

        # Group C
        ("C_BRA_MAR", "Bet365", 1.65, 3.75, 5.25),
        ("C_SCO_HAI", "Bet365", 1.50, 4.00, 7.00),
        ("C_SCO_MAR", "Bet365", 3.25, 3.20, 2.25),
        ("C_BRA_HAI", "Bet365", 1.15, 7.50, 17.00),
        ("C_SCO_BRA", "Bet365", 6.50, 4.20, 1.50),
        ("C_MAR_HAI", "Bet365", 1.40, 4.60, 7.50),

        # Group D
        ("D_USA_PAR", "Bet365", 1.85, 3.40, 4.33),
        ("D_AUS_TUR", "Bet365", 2.40, 3.20, 3.00),
        ("D_USA_AUS", "Bet365", 1.95, 3.30, 4.00),
        ("D_PAR_TUR", "Bet365", 2.50, 3.10, 3.00),
        ("D_TUR_USA", "Bet365", 3.10, 3.30, 2.30),
        ("D_AUS_PAR", "Bet365", 2.35, 3.10, 3.20),

        # Group E
        ("E_GER_CUW", "Bet365", 1.10, 9.00, 21.00),
        ("E_CIV_ECU", "Bet365", 2.40, 3.10, 3.10),
        ("E_GER_CIV", "Bet365", 1.75, 3.60, 4.75),
        ("E_ECU_CUW", "Bet365", 1.45, 4.20, 7.50),
        ("E_CIV_CUW", "Bet365", 1.30, 5.00, 10.00),
        ("E_ECU_GER", "Bet365", 4.50, 3.75, 1.75),

        # Group F
        ("F_NED_JPN", "Bet365", 1.90, 3.40, 4.00),
        ("F_SWE_TUN", "Bet365", 1.65, 3.75, 5.25),
        ("F_NED_SWE", "Bet365", 1.85, 3.50, 4.20),
        ("F_TUN_JPN", "Bet365", 5.50, 3.80, 1.62),
        ("F_TUN_NED", "Bet365", 7.00, 4.00, 1.45),
        ("F_JPN_SWE", "Bet365", 2.20, 3.25, 3.30),

        # Group G
        ("G_EGY_IRN", "Bet365", 2.45, 2.65, 3.75),
        ("G_NZL_BEL", "Bet365", 4.50, 3.25, 1.90),

        # Group H
        ("H_CPV_KSA", "Bet365", 2.80, 2.90, 2.70),
        ("H_URU_ESP", "Bet365", 3.20, 3.10, 2.30),

        # Group I
        ("I_FRA_NOR", "Bet365", 1.85, 3.40, 4.50),
        ("I_SEN_IRQ", "Bet365", 2.10, 3.10, 3.80),

        # Group J
        ("J_ALG_AUT", "Bet365", 3.10, 2.85, 2.60),
        ("J_JOR_ARG", "Bet365", 13.00, 6.00, 1.20),

        # Group K
        ("K_COL_POR", "Bet365", 3.20, 3.10, 2.35),
        ("K_COD_UZB", "Bet365", 2.90, 3.00, 2.65),

        # Group L
        ("L_CRO_GHA", "Bet365", 2.20, 3.10, 3.50),
        ("L_PAN_ENG", "Bet365", 8.00, 5.00, 1.40),
    ]

    # Truncate tables first to avoid any duplicates
    ch.query("TRUNCATE TABLE fixtures")
    ch.query("TRUNCATE TABLE odds")

    # Insert fixtures
    ch.insert(
        "fixtures",
        fixtures_data,
        column_names=["fixture_id", "group_id", "home_team", "away_team", "kickoff", "status"]
    )
    print(f"Successfully seeded {len(fixtures_data)} official fixtures.")

    # Insert odds
    ch.insert(
        "odds",
        odds_data,
        column_names=["fixture_id", "bookmaker", "home_odds", "draw_odds", "away_odds"]
    )
    print(f"Successfully seeded {len(odds_data)} official odds.")

if __name__ == "__main__":
    seed()
