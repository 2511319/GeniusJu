# services/snapshot_manager.py

import os, json
from datetime import datetime
from pathlib import Path

ENV = os.getenv("APP_ENV","production").lower()
SNAPSHOT_ENABLED = os.getenv("SNAPSHOT_ENABLED","false").lower()=="true" or ENV in ("development","local")

def save_snapshot(user_id: str, data: list, prompt: str):
    if not SNAPSHOT_ENABLED:
        return
    base = Path("snapshots")/user_id
    base.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    with open(base/f"data_{ts}.json","w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(base/f"prompt_{ts}.txt","w",encoding="utf-8") as f:
        f.write(prompt)
