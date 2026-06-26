from core.db import client

def seed():
    ch = client()
    print("Seeding official 2026 World Cup standings...")

    # Define the 48 teams (12 groups * 4 teams)
    # group_id, team, played, won, drawn, lost, goals_for, goals_against, goal_diff, points, position
    data = [
        # Group A - Completed
        ("A", "Mexico", 3, 3, 0, 0, 6, 0, 6, 9, 1),
        ("A", "South Africa", 3, 1, 1, 1, 2, 3, -1, 4, 2),
        ("A", "South Korea", 3, 1, 0, 2, 2, 3, -1, 3, 3),
        ("A", "Czech Republic", 3, 0, 1, 2, 2, 6, -4, 1, 4),
        
        # Group B - Completed
        ("B", "Switzerland", 3, 2, 1, 0, 7, 3, 4, 7, 1),
        ("B", "Canada", 3, 1, 1, 1, 8, 3, 5, 4, 2),
        ("B", "Bosnia & Herzegovina", 3, 1, 1, 1, 5, 6, -1, 4, 3),
        ("B", "Qatar", 3, 0, 1, 2, 2, 10, -8, 1, 4),
        
        # Group C - Completed
        ("C", "Brazil", 3, 2, 1, 0, 7, 1, 6, 7, 1),
        ("C", "Morocco", 3, 2, 1, 0, 6, 3, 3, 7, 2),
        ("C", "Scotland", 3, 1, 0, 2, 1, 4, -3, 3, 3),
        ("C", "Haiti", 3, 0, 0, 3, 2, 8, -6, 0, 4),
        
        # Group D - Completed
        ("D", "USA", 3, 2, 0, 1, 8, 4, 4, 6, 1),
        ("D", "Australia", 3, 1, 1, 1, 3, 3, 0, 4, 2),
        ("D", "Paraguay", 3, 1, 1, 1, 3, 5, -2, 4, 3),
        ("D", "Turkey", 3, 1, 0, 2, 3, 5, -2, 3, 4),
        
        # Group E - Completed
        ("E", "Germany", 3, 2, 0, 1, 10, 4, 6, 6, 1),
        ("E", "Ivory Coast", 3, 2, 0, 1, 4, 2, 2, 6, 2),
        ("E", "Ecuador", 3, 1, 1, 1, 2, 2, 0, 4, 3),
        ("E", "Curaçao", 3, 0, 1, 2, 1, 9, -8, 1, 4),
        
        # Group F - Completed
        ("F", "Netherlands", 3, 2, 1, 0, 10, 4, 6, 7, 1),
        ("F", "Japan", 3, 2, 1, 0, 8, 3, 5, 7, 2),
        ("F", "Sweden", 3, 1, 0, 2, 7, 8, -1, 3, 3),
        ("F", "Tunisia", 3, 0, 0, 3, 2, 12, -10, 0, 4),
        
        # Group G - 2 games played, 1 left
        ("G", "Egypt", 2, 1, 1, 0, 4, 2, 2, 4, 1),
        ("G", "Iran", 2, 0, 2, 0, 2, 2, 0, 2, 2),
        ("G", "Belgium", 2, 0, 2, 0, 1, 1, 0, 2, 3),
        ("G", "New Zealand", 2, 0, 1, 1, 3, 5, -2, 1, 4),
        
        # Group H - 2 games played, 1 left
        ("H", "Spain", 2, 1, 1, 0, 4, 0, 4, 4, 1),
        ("H", "Uruguay", 2, 0, 2, 0, 3, 3, 0, 2, 2),
        ("H", "Cape Verde", 2, 0, 2, 0, 2, 2, 0, 2, 3),
        ("H", "Saudi Arabia", 2, 0, 1, 1, 1, 5, -4, 1, 4),
        
        # Group I - 2 games played, 1 left
        ("I", "France", 2, 2, 0, 0, 6, 1, 5, 6, 1),
        ("I", "Norway", 2, 2, 0, 0, 7, 3, 4, 6, 2),
        ("I", "Senegal", 2, 0, 0, 2, 3, 6, -3, 0, 3),
        ("I", "Iraq", 2, 0, 0, 2, 1, 7, -6, 0, 4),
        
        # Group J - 2 games played, 1 left
        ("J", "Argentina", 2, 2, 0, 0, 5, 0, 5, 6, 1),
        ("J", "Austria", 2, 1, 0, 1, 2, 3, -1, 3, 2),
        ("J", "Algeria", 2, 1, 0, 1, 2, 4, -2, 3, 3),
        ("J", "Jordan", 2, 0, 0, 2, 2, 4, -2, 0, 4),
        
        # Group K - 2 games played, 1 left
        ("K", "Colombia", 2, 2, 0, 0, 4, 1, 3, 6, 1),
        ("K", "Portugal", 2, 1, 1, 0, 6, 1, 5, 4, 2),
        ("K", "Congo DR", 2, 0, 1, 1, 1, 2, -1, 1, 3),
        ("K", "Uzbekistan", 2, 0, 0, 2, 1, 8, -7, 0, 4),
        
        # Group L - 2 games played, 1 left
        ("L", "England", 2, 1, 1, 0, 4, 2, 2, 4, 1),
        ("L", "Ghana", 2, 1, 1, 0, 1, 0, 1, 4, 2),
        ("L", "Croatia", 2, 1, 0, 1, 3, 4, -1, 3, 3),
        ("L", "Panama", 2, 0, 0, 2, 0, 2, -2, 0, 4),
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
