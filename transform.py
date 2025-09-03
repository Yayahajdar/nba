import os
import pandas as pd

def run_transform():
    os.makedirs("data/raw", exist_ok=True)
    players_path = "data/raw/api_players.json"
    games_path = "data/raw/api_games.json"

    if not (os.path.exists(players_path) and os.path.exists(games_path)):
        print("⚠️ Transform skipped: raw API files not found.")
        return

   
    players = pd.read_json(players_path)
    games = pd.read_json(games_path)

    
    players_norm = pd.json_normalize(players.to_dict(orient="records"))
    games_norm = pd.json_normalize(games.to_dict(orient="records"))

  
    if "team.id" in players_norm.columns:
        players_norm["team.id"] = players_norm["team.id"].fillna(-1).astype(int)

     
    if "id" in players_norm.columns:
        players_norm = players_norm.drop_duplicates(subset=["id"])
    if "id" in games_norm.columns:
        games_norm = games_norm.drop_duplicates(subset=["id"])

   
    players_out = players_norm.rename(columns={
        "first_name": "first",
        "last_name": "last",
        "position": "pos",
        "team.id": "team_id"
    })
    keep_players = [c for c in ["id", "first", "last", "pos", "team_id"] if c in players_out.columns]
    players_out = players_out[keep_players]

    games_out = games_norm.rename(columns={
        "home_team.id": "home_team_id",
        "visitor_team.id": "visitor_team_id",
        "home_team_score": "home_score",
        "visitor_team_score": "visitor_score"
    })
    keep_games = [c for c in ["id", "season", "date", "home_team_id", "visitor_team_id", "home_score", "visitor_score"] if c in games_out.columns]
    games_out = games_out[keep_games]

    
    players_out.to_csv("data/raw/players_norm.csv", index=False)
    games_out.to_csv("data/raw/games_norm.csv", index=False)

    print("✅ Transform complete: wrote players_norm.csv and games_norm.csv")