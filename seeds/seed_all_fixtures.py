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
        ("A_USA_MEX", "A", "USA", "Mexico", datetime.datetime(2026, 6, 25, 15, 0), "finished"),
        ("A_CAN_JAM", "A", "Canada", "Jamaica", datetime.datetime(2026, 6, 25, 15, 0), "finished"),

        # Group B (Completed)
        ("B_ENG_WAL", "B", "England", "Wales", datetime.datetime(2026, 6, 25, 15, 0), "finished"),
        ("B_SCO_UKR", "B", "Scotland", "Ukraine", datetime.datetime(2026, 6, 25, 15, 0), "finished"),

        # Group C (Completed)
        ("C_ARG_POL", "C", "Argentina", "Poland", datetime.datetime(2026, 6, 25, 18, 0), "finished"),
        ("C_SAU_AUS", "C", "Saudi Arabia", "Australia", datetime.datetime(2026, 6, 25, 18, 0), "finished"),

        # Group D (Completed)
        ("D_FRA_DEN", "D", "France", "Denmark", datetime.datetime(2026, 6, 25, 18, 0), "finished"),
        ("D_TUN_PER", "D", "Tunisia", "Peru", datetime.datetime(2026, 6, 25, 18, 0), "finished"),

        # Group E (Completed)
        ("E_ESP_GER", "E", "Spain", "Germany", datetime.datetime(2026, 6, 25, 21, 0), "finished"),
        ("E_JPN_CRC", "E", "Japan", "Costa Rica", datetime.datetime(2026, 6, 25, 21, 0), "finished"),

        # Group F (Completed)
        ("F_BRA_SUI", "F", "Brazil", "Switzerland", datetime.datetime(2026, 6, 25, 21, 0), "finished"),
        ("F_SRB_CMR", "F", "Serbia", "Cameroon", datetime.datetime(2026, 6, 25, 21, 0), "finished"),

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
        ("A_USA_MEX", "Bet365", 1.90, 3.30, 4.20),
        ("A_CAN_JAM", "Bet365", 1.50, 4.00, 6.50),

        # Group B
        ("B_ENG_WAL", "Bet365", 1.60, 3.80, 5.50),
        ("B_SCO_UKR", "Bet365", 2.40, 3.10, 3.10),

        # Group C
        ("C_ARG_POL", "Bet365", 1.45, 4.20, 7.50),
        ("C_SAU_AUS", "Bet365", 2.20, 3.20, 3.35),

        # Group D
        ("D_FRA_DEN", "Bet365", 1.85, 3.40, 4.50),
        ("D_TUN_PER", "Bet365", 2.10, 3.20, 3.60),

        # Group E
        ("E_ESP_GER", "Bet365", 2.15, 3.30, 3.30),
        ("E_JPN_CRC", "Bet365", 2.00, 3.20, 4.00),

        # Group F
        ("F_BRA_SUI", "Bet365", 1.55, 3.90, 6.00),
        ("F_SRB_CMR", "Bet365", 1.90, 3.40, 4.10),

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
