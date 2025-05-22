# services/history_manager.py

import json
from pathlib import Path
from datetime import datetime

from config import ENV, db  # Импортируем ENV из модуля config

# Выбираем файловое хранилище в локальной среде
USE_FILE_STORAGE = ENV in ("development", "local")

# Директория для локального сохранения истории
HISTORY_DIR = Path("history")

# Firestore-коллекция для продакшен
FIRESTORE_COLLECTION = "histories"
MAX_HISTORY_ITEMS = 5

def _load_local_history(user_id: str):
    HISTORY_DIR.mkdir(exist_ok=True)
    path = HISTORY_DIR / f"{user_id}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))

def _save_local_history(user_id: str, history):
    HISTORY_DIR.mkdir(exist_ok=True)
    path = HISTORY_DIR / f"{user_id}.json"
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

def save_history(user_id: str, symbol: str, interval: str, result: dict):
    """
    Сохраняет историю запроса:
      - timestamp (UTC YYYY-MM-DD HH:MM:SS)
      - symbol, interval, result (словарь)
    Оставляет только последние MAX_HISTORY_ITEMS записей.
    """
    entry = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "interval": interval,
        "result": result
    }

    if USE_FILE_STORAGE:
        history = _load_local_history(user_id)
        history.append(entry)
        history = history[-MAX_HISTORY_ITEMS:]
        _save_local_history(user_id, history)
    else:
        if db is None:
            return
        doc_ref = db.collection(FIRESTORE_COLLECTION).document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({"history": [entry]})
        else:
            hist = doc.to_dict().get("history", [])
            hist.append(entry)
            hist = hist[-MAX_HISTORY_ITEMS:]
            doc_ref.update({"history": hist})

def get_history(user_id: str):
    """
    Возвращает список последних запросов пользователя (не более MAX_HISTORY_ITEMS).
    """
    if USE_FILE_STORAGE:
        return _load_local_history(user_id)
    if db is None:
        return []
    doc = db.collection(FIRESTORE_COLLECTION).document(user_id).get()
    if not doc.exists:
        return []
    return doc.to_dict().get("history", [])
