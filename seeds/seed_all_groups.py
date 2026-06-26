from core.db import client

def seed():
    ch = client()
    print("Seeding official 2026 World Cup standings...")

    # Define the 48 teams (12 groups * 4 teams)
    # group_id, team, played, won, drawn, lost, goals_for, goals_against, goal_diff, points, position
    data = [
        # Group A - Completed
        ("A", "Mexico", 3, 2, 1, 0, 6, 3, 3, 7, 1),
        ("A", "South Korea", 3, 1, 2, 0, 4, 3, 1, 5, 2),
        ("A", "Ireland", 3, 1, 1, 1, 4, 4, 0, 4, 3),
        ("A", "South Africa", 3, 0, 0, 3, 2, 6, -4, 0, 4),
        
        # Group B - Completed
        ("B", "Italy", 3, 2, 1, 0, 6, 1, 5, 7, 1),
        ("B", "Canada", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("B", "Switzerland", 3, 1, 1, 1, 3, 3, 0, 4, 3),
        ("B", "Qatar", 3, 0, 1, 2, 1, 6, -5, 1, 4),
        
        # Group C - Completed
        ("C", "Brazil", 3, 3, 0, 0, 7, 1, 6, 9, 1),
        ("C", "Morocco", 3, 2, 0, 1, 6, 4, 2, 6, 2),
        ("C", "Scotland", 3, 1, 0, 2, 3, 5, -2, 3, 3),
        ("C", "Haiti", 3, 0, 0, 3, 2, 8, -6, 0, 4),
        
        # Group D - Completed
        ("D", "USA", 3, 2, 1, 0, 5, 2, 3, 7, 1),
        ("D", "Australia", 3, 1, 2, 0, 4, 3, 1, 5, 2),
        ("D", "Turkey", 3, 1, 1, 1, 3, 3, 0, 4, 3),
        ("D", "Paraguay", 3, 0, 0, 3, 2, 6, -4, 0, 4),
        
        # Group E - Completed
        ("E", "Germany", 3, 2, 1, 0, 6, 2, 4, 7, 1),
        ("E", "Ivory Coast", 3, 1, 2, 0, 4, 2, 2, 5, 2),
        ("E", "Ecuador", 3, 1, 1, 1, 3, 4, -1, 4, 3),
        ("E", "Curacao", 3, 0, 0, 3, 1, 6, -5, 0, 4),
        
        # Group F - Completed
        ("F", "Netherlands", 3, 2, 1, 0, 6, 3, 3, 7, 1),
        ("F", "Japan", 3, 1, 2, 0, 4, 3, 1, 5, 2),
        ("F", "Poland", 3, 1, 0, 2, 3, 4, -1, 3, 3),
        ("F", "Tunisia", 3, 0, 1, 2, 1, 4, -3, 1, 4),
        
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
