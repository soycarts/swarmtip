from core.db import client

def seed():
    ch = client()
    print("Seeding official 2026 World Cup standings...")

    # Define the 48 teams (12 groups * 4 teams)
    # group_id, team, played, won, drawn, lost, goals_for, goals_against, goal_diff, points, position
    data = [
        # Group A - Completed
        ("A", "USA", 3, 2, 1, 0, 6, 2, 4, 7, 1),
        ("A", "Mexico", 3, 1, 2, 0, 4, 3, 1, 5, 2),
        ("A", "Canada", 3, 1, 1, 1, 4, 3, 1, 4, 3),
        ("A", "Jamaica", 3, 0, 0, 3, 1, 10, -9, 0, 4),
        
        # Group B - Completed
        ("B", "England", 3, 2, 1, 0, 5, 1, 4, 7, 1),
        ("B", "Wales", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("B", "Scotland", 3, 1, 0, 2, 3, 3, 0, 3, 3),
        ("B", "Ukraine", 3, 0, 2, 1, 2, 6, -4, 2, 4),
        
        # Group C - Completed
        ("C", "Argentina", 3, 3, 0, 0, 8, 1, 7, 9, 1),
        ("C", "Poland", 3, 1, 1, 1, 3, 4, -1, 4, 2),
        ("C", "Saudi Arabia", 3, 1, 1, 1, 3, 3, 0, 4, 3),
        ("C", "Australia", 3, 0, 0, 3, 1, 7, -6, 0, 4),
        
        # Group D - Completed
        ("D", "France", 3, 2, 1, 0, 6, 1, 5, 7, 1),
        ("D", "Denmark", 3, 1, 2, 0, 4, 2, 2, 5, 2),
        ("D", "Tunisia", 3, 1, 2, 0, 5, 3, 2, 5, 3),
        ("D", "Peru", 3, 0, 0, 3, 0, 9, -9, 0, 4),
        
        # Group E - Completed
        ("E", "Spain", 3, 2, 1, 0, 7, 2, 5, 7, 1),
        ("E", "Germany", 3, 1, 1, 1, 4, 4, 0, 4, 2),
        ("E", "Japan", 3, 0, 2, 1, 2, 4, -2, 2, 3),
        ("E", "Costa Rica", 3, 0, 2, 1, 1, 4, -3, 2, 4),
        
        # Group F - Completed
        ("F", "Brazil", 3, 2, 1, 0, 5, 1, 4, 7, 1),
        ("F", "Switzerland", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("F", "Serbia", 3, 1, 1, 1, 3, 4, -1, 4, 3),
        ("F", "Cameroon", 3, 0, 1, 2, 2, 5, -3, 1, 4),
        
        # Group G - 2 games played, 1 left
        ("G", "Belgium", 2, 1, 1, 0, 3, 1, 2, 4, 1),
        ("G", "Egypt", 2, 1, 0, 1, 2, 2, 0, 3, 2),
        ("G", "Iran", 2, 0, 2, 0, 2, 2, 0, 2, 3),
        ("G", "New Zealand", 2, 0, 1, 1, 1, 3, -2, 1, 4),
        
        # Group H - 2 games played, 1 left
        ("H", "Spain", 2, 1, 1, 0, 4, 2, 2, 4, 1),
        ("H", "Uruguay", 2, 1, 0, 1, 3, 3, 0, 3, 2),
        ("H", "Saudi Arabia", 2, 0, 2, 0, 2, 2, 0, 2, 3),
        ("H", "Cape Verde", 2, 0, 1, 1, 1, 3, -2, 1, 4),
        
        # Group I - 2 games played, 1 left
        ("I", "France", 2, 1, 1, 0, 3, 1, 2, 4, 1),
        ("I", "Senegal", 2, 1, 0, 1, 3, 3, 0, 3, 2),
        ("I", "Norway", 2, 0, 2, 0, 2, 2, 0, 2, 3),
        ("I", "Iraq", 2, 0, 1, 1, 1, 3, -2, 1, 4),
        
        # Group J - 2 games played, 1 left
        ("J", "Argentina", 2, 1, 1, 0, 4, 2, 2, 4, 1),
        ("J", "Algeria", 2, 1, 0, 1, 3, 3, 0, 3, 2),
        ("J", "Austria", 2, 0, 2, 0, 2, 2, 0, 2, 3),
        ("J", "Jordan", 2, 0, 1, 1, 1, 3, -2, 1, 4),
        
        # Group K - 2 games played, 1 left
        ("K", "Portugal", 2, 1, 1, 0, 3, 1, 2, 4, 1),
        ("K", "Colombia", 2, 1, 0, 1, 2, 2, 0, 3, 2),
        ("K", "Uzbekistan", 2, 0, 2, 0, 2, 2, 0, 2, 3),
        ("K", "Congo DR", 2, 0, 1, 1, 1, 3, -2, 1, 4),
        
        # Group L - 2 games played, 1 left
        ("L", "England", 2, 1, 1, 0, 3, 1, 2, 4, 1),
        ("L", "Croatia", 2, 1, 0, 1, 2, 2, 0, 3, 2),
        ("L", "Ghana", 2, 0, 2, 0, 2, 2, 0, 2, 3),
        ("L", "Panama", 2, 0, 1, 1, 1, 3, -2, 1, 4),
    ]

    # Clean old standings
    ch.query("TRUNCATE TABLE standings")
    
    # Insert new standings
    ch.insert(
        "standings",
        data,
        column_names=["group_id", "team", "played", "won", "drawn", "lost", "goals_for", "goals_against", "goal_diff", "points", "position"]
    )
    print("Standings seeded successfully!")

if __name__ == "__main__":
    seed()
