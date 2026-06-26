import datetime
from core.db import client

def seed():
    ch = client()
    print("Seeding official 2026 World Cup fixtures and odds (A-F finished, G-L scheduled)...")

    # Define the 24 fixtures (2 per group)
    # Groups A to F are completed (status: 'finished')
    # Groups G to L are upcoming/scheduled (status: 'scheduled')
    # fixture_id, group_id, home_team, away_team, kickoff, status
    fixtures_data = [
        # Group A (Completed)
        ("A_MEX_RSA", "A", "Mexico", "South Africa", datetime.datetime(2026, 6, 25, 15, 0), "finished"),
        ("A_KOR_IRL", "A", "South Korea", "Ireland", datetime.datetime(2026, 6, 25, 15, 0), "finished"),

        # Group B (Completed)
        ("B_CAN_SUI", "B", "Canada", "Switzerland", datetime.datetime(2026, 6, 25, 15, 0), "finished"),
        ("B_ITA_QAT", "B", "Italy", "Qatar", datetime.datetime(2026, 6, 25, 15, 0), "finished"),

        # Group C (Completed)
        ("C_BRA_SCO", "C", "Brazil", "Scotland", datetime.datetime(2026, 6, 25, 18, 0), "finished"),
        ("C_MAR_HAI", "C", "Morocco", "Haiti", datetime.datetime(2026, 6, 25, 18, 0), "finished"),

        # Group D (Completed)
        ("D_USA_PAR", "D", "USA", "Paraguay", datetime.datetime(2026, 6, 25, 18, 0), "finished"),
        ("D_AUS_TUR", "D", "Australia", "Turkey", datetime.datetime(2026, 6, 25, 18, 0), "finished"),

        # Group E (Completed)
        ("E_GER_ECU", "E", "Germany", "Ecuador", datetime.datetime(2026, 6, 25, 21, 0), "finished"),
        ("E_CIV_CUW", "E", "Ivory Coast", "Curacao", datetime.datetime(2026, 6, 25, 21, 0), "finished"),

        # Group F (Completed)
        ("F_NED_JPN", "F", "Netherlands", "Japan", datetime.datetime(2026, 6, 25, 21, 0), "finished"),
        ("F_POL_TUN", "F", "Poland", "Tunisia", datetime.datetime(2026, 6, 25, 21, 0), "finished"),

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
        ("A_MEX_RSA", "Bet365", 1.80, 3.40, 4.50),
        ("A_KOR_IRL", "Bet365", 2.20, 3.10, 3.40),

        # Group B
        ("B_CAN_SUI", "Bet365", 2.60, 3.00, 2.90),
        ("B_ITA_QAT", "Bet365", 1.30, 5.00, 11.00),

        # Group C
        ("C_BRA_SCO", "Bet365", 1.40, 4.50, 8.00),
        ("C_MAR_HAI", "Bet365", 1.50, 4.00, 6.50),

        # Group D
        ("D_USA_PAR", "Bet365", 1.75, 3.50, 4.80),
        ("D_AUS_TUR", "Bet365", 2.50, 3.10, 3.00),

        # Group E
        ("E_GER_ECU", "Bet365", 1.65, 3.75, 5.50),
        ("E_CIV_CUW", "Bet365", 1.45, 4.20, 7.50),

        # Group F
        ("F_NED_JPN", "Bet365", 2.10, 3.30, 3.50),
        ("F_POL_TUN", "Bet365", 1.95, 3.25, 4.20),

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
