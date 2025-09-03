import os
import json
import time
import requests
from dotenv import load_dotenv

# تحميل API Key من .env
load_dotenv()
API_KEY = os.getenv("BALLDONTLIE_API_KEY")
if not API_KEY:
    raise ValueError("❌ BALLDONTLIE_API_KEY is not set in .env!")

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://api.balldontlie.io/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}


def fetch_all_players(per_page=100, max_players=200):
    
    players = []
    page = 1
    total_fetched = 0

    while total_fetched < max_players:
        try:
            response = requests.get(
                f"{BASE_URL}/players",
                params={"per_page": per_page, "page": page},
                headers=HEADERS,
                timeout=30
            )
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "10"))
                print(f"⏳ Rate limited on players page {page}. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue
            if not response.ok:
                response.raise_for_status()

            data = response.json()

            batch = data.get("data", [])
            if not batch:
                break

            players.extend(batch)
            total_fetched += len(batch)
            print(f"✅ Collected {total_fetched} players so far")

            page += 1
            time.sleep(1.5)  # small pacing between pages

        except requests.HTTPError as http_err:
            print(f"⚠️ HTTP error on players page {page}: {http_err}. Retrying in 10s...")
            time.sleep(10)
            continue
        except Exception as e:
            print(f"⚠️ Error fetching players on page {page}: {e}. Retrying in 10s...")
            time.sleep(10)
            continue

 
    with open(f"{RAW_DIR}/api_players.json", "w") as f:
        json.dump(players[:max_players], f, indent=2)

    print(f"🎉 Finished fetching {len(players[:max_players])} players")
    return players[:max_players]


def fetch_games(season=2023, per_page=100, max_games=200):
    """جلب مباريات NBA من API"""
    games = []
    page = 1
    total_fetched = 0

    while total_fetched < max_games:
        try:
            response = requests.get(
                f"{BASE_URL}/games",
                params={"per_page": per_page, "page": page, "seasons[]": season},
                headers=HEADERS,
                timeout=30
            )
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "10"))
                print(f"⏳ Rate limited on games page {page}. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue
            if not response.ok:
                response.raise_for_status()

            data = response.json()

            batch = data.get("data", [])
            if not batch:
                break

            games.extend(batch)
            total_fetched += len(batch)
            print(f"🏀 Collected {total_fetched} games so far")

            page += 1
            time.sleep(1.5)  # small pacing between pages

        except requests.HTTPError as http_err:
            print(f"⚠️ HTTP error on games page {page}: {http_err}. Retrying in 10s...")
            time.sleep(10)
            continue
        except Exception as e:
            print(f"⚠️ Error fetching games on page {page}: {e}. Retrying in 10s...")
            time.sleep(10)
            continue

  
    with open(f"{RAW_DIR}/api_games.json", "w") as f:
        json.dump(games[:max_games], f, indent=2)

    print(f"🎉 Finished fetching {len(games[:max_games])} games")
    return games[:max_games]


def run_api():
 
    players = fetch_all_players(per_page=100, max_players=200)
    games = fetch_games(season=2023, per_page=100, max_games=200)
    return players, games
