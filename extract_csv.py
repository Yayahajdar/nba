import pandas as pd, os
RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

def run_csv():
    df = pd.DataFrame([{"player_id": 237, "season": 2023, "pts": 29.8, "reb": 8.2, "ast": 6.4}])
    df.to_csv(f"{RAW_DIR}/extra_stats.csv", index=False)
    print("Extra CSV stats saved")
