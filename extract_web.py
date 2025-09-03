import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

# -------------------------------
# إعداد المجلد
# -------------------------------
RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

def run_web():
    url = "https://en.wikipedia.org/wiki/NBA_Most_Valuable_Player_Award"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://en.wikipedia.org/",
    }
    response = None
    for attempt in range(3):
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            response = resp
            break
        print(f"⚠️ Wikipedia fetch attempt {attempt+1}/3 failed with {resp.status_code}. Retrying...")
        time.sleep(2 ** attempt * 2)

    if response is None or response.status_code != 200:
        print("⚠️ Could not fetch Wikipedia page after retries. Skipping web extraction.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # جميع الجداول
    tables = soup.find_all("table", {"class": "wikitable"})
    print(f"🔍 Found {len(tables)} wikitable tables on the page")

    # حفظ كل جدول
    for idx, table in enumerate(tables):
        # تحويل HTML إلى DataFrame
        df = pd.read_html(str(table))[0]

        # تنظيف الأعمدة الفارغة
        df = df.dropna(how="all")
        df.to_csv(f"{RAW_DIR}/mvp_wiki_table_{idx+1}.csv", index=False)
        print(f"✅ Table {idx+1} saved: {len(df)} rows, columns: {list(df.columns)}")
    
    print("🎉 All tables saved successfully!")
    return tables

if __name__ == "__main__":
    run_web()
