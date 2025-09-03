import json, os
from datetime import datetime
RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

def run_big():
    with open(f"{RAW_DIR}/bigdata.jsonl", "w") as f:
        for i in range(5_000):
            f.write(json.dumps({
                "player_id": 100+i,
                "event": "score",
                "value": 2,
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n")
    print("Big JSONL file created")
