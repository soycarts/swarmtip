import datetime
from core.db import client

def seed():
    ch = client()
    print("Seeding all 12 groups for 2026 World Cup standings...")

    # Define the 48 teams (12 groups * 4 teams)
    # group_id, team, played, won, drawn, lost, goals_for, goals_against, goal_diff, points, position
    data = [
        # Group A
        ("A", "USA", 3, 2, 1, 0, 6, 2, 4, 7, 1),
        ("A", "Mexico", 3, 1, 2, 0, 4, 3, 1, 5, 2),
        ("A", "Canada", 3, 1, 1, 1, 4, 3, 1, 4, 3),
        ("A", "Jamaica", 3, 0, 0, 3, 1, 10, -9, 0, 4),
        
        # Group B
        ("B", "England", 3, 2, 1, 0, 5, 1, 4, 7, 1),
        ("B", "Wales", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("B", "Scotland", 3, 1, 0, 2, 3, 3, 0, 3, 3),
        ("B", "Ukraine", 3, 0, 2, 1, 2, 6, -4, 2, 4),
        
        # Group C
        ("C", "Argentina", 3, 3, 0, 0, 8, 1, 7, 9, 1),
        ("C", "Poland", 3, 1, 1, 1, 3, 4, -1, 4, 2),
        ("C", "Saudi Arabia", 3, 1, 1, 1, 3, 3, 0, 4, 3),
        ("C", "Australia", 3, 0, 0, 3, 1, 7, -6, 0, 4),
        
        # Group D
        ("D", "France", 3, 2, 1, 0, 6, 1, 5, 7, 1),
        ("D", "Denmark", 3, 1, 2, 0, 4, 2, 2, 5, 2),
        ("D", "Tunisia", 3, 1, 2, 0, 5, 3, 2, 5, 3),
        ("D", "Peru", 3, 0, 0, 3, 0, 9, -9, 0, 4),
        
        # Group E
        ("E", "Spain", 3, 2, 1, 0, 7, 2, 5, 7, 1),
        ("E", "Germany", 3, 1, 1, 1, 4, 4, 0, 4, 2),
        ("E", "Japan", 3, 0, 2, 1, 2, 4, -2, 2, 3),
        ("E", "Costa Rica", 3, 0, 2, 1, 1, 4, -3, 2, 4),
        
        # Group F
        ("F", "Brazil", 3, 2, 1, 0, 5, 1, 4, 7, 1),
        ("F", "Switzerland", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("F", "Serbia", 3, 1, 1, 1, 3, 4, -1, 4, 3),
        ("F", "Cameroon", 3, 0, 1, 2, 2, 5, -3, 1, 4),
        
        # Group G (Live group, base state before matchday 3 final whistles)
        ("G", "Egypt", 2, 1, 1, 0, 3, 1, 2, 4, 1),
        ("G", "Iran", 2, 0, 2, 0, 1, 1, 0, 2, 2),
        ("G", "Belgium", 2, 0, 2, 0, 1, 2, -1, 2, 3),
        ("G", "New Zealand", 2, 0, 1, 1, 1, 2, -1, 1, 4),
        
        # Group H
        ("H", "Portugal", 3, 2, 1, 0, 6, 2, 4, 7, 1),
        ("H", "Uruguay", 3, 2, 0, 1, 5, 3, 2, 6, 2),
        ("H", "South Korea", 3, 0, 1, 2, 1, 5, -4, 1, 3),
        ("H", "Ghana", 3, 0, 1, 2, 2, 6, -4, 1, 4),
        
        # Group I
        ("I", "Italy", 3, 2, 1, 0, 5, 1, 4, 7, 1),
        ("I", "Sweden", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("I", "Turkey", 3, 1, 0, 2, 2, 3, -1, 3, 3),
        ("I", "Austria", 3, 0, 2, 1, 1, 4, -3, 2, 4),
        
        # Group J
        ("J", "Netherlands", 3, 2, 1, 0, 6, 2, 4, 7, 1),
        ("J", "Senegal", 3, 1, 2, 0, 4, 3, 1, 5, 2),
        ("J", "Ecuador", 3, 1, 1, 1, 3, 2, 1, 4, 3),
        ("J", "Qatar", 3, 0, 0, 3, 1, 8, -7, 0, 4),
        
        # Group K
        ("K", "Morocco", 3, 2, 1, 0, 5, 2, 3, 7, 1),
        ("K", "Croatia", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("K", "Colombia", 3, 1, 0, 2, 4, 3, 1, 3, 3),
        ("K", "Chile", 3, 0, 2, 1, 2, 6, -4, 2, 4),
        
        # Group L
        ("L", "Nigeria", 3, 2, 1, 0, 4, 2, 2, 7, 1),
        ("L", "Ivory Coast", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("L", "Algeria", 3, 0, 2, 1, 2, 3, -1, 2, 3),
        ("L", "South Africa", 3, 0, 2, 1, 1, 2, -1, 2, 4),
    ]

    # Clean old standings
    ch.query("TRUNCATE TABLE standings")
    
    # Insert new standings
    ch.insert(
        "standings",
        data,
        column_names=["group_id", "team", "played", "won", "drawn", "lost", "goals_for", "goals_against", "goal_diff", "points", "position"]
    )
    print("Standings seeded successfully! 48 teams in ClickHouse standings table.")

if __name__ == "__main__":
    seed()
