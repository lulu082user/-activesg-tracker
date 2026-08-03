"""
ActiveSG Gym Crowd Scraper
Runs on GitHub Actions every 30 min. Fetches crowd data for all gyms,
focuses on Jurong Lake Gardens. Appends to data.jsonl.
"""
import urllib.request
import json
import re
from datetime import datetime, timezone
from pathlib import Path

JINA_URL = "https://r.jina.ai/https://activesg.gov.sg/gym-pool-crowd"
DATA_FILE = Path(__file__).parent / "data.jsonl"

def fetch():
    req = urllib.request.Request(JINA_URL, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/markdown",
        "X-Timeout": "45"
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode()

def parse(text):
    ts_match = re.search(r'Last updated at (.+?)(?:\n|<)', text)
    timestamp = ts_match.group(1).strip() if ts_match else "unknown"
    gyms = re.findall(r'(.+?)\n\n(\d+)% full', text)
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "page_updated": timestamp,
        "gyms": {name.strip(): int(pct) for name, pct in gyms},
        "num_gyms": len(gyms)
    }

def main():
    try:
        result = parse(fetch())
    except Exception as e:
        result = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "error": str(e)[:200]
        }

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    jlg = result.get("gyms", {}).get("Jurong Lake Gardens ActiveSG Gym", "N/A")
    print(f"OK | page_updated={result.get('page_updated','?')} | Jurong Lake Gardens: {jlg}%")

if __name__ == "__main__":
    main()
