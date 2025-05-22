# services/analysis_service.py

import json
from pathlib import Path
from jinja2 import Template
from services.crypto_compare_provider import CryptoCompareProvider
from services.openai_client     import ask
from services.snapshot_manager  import save_snapshot

PROMPT_PATH = Path("prompt.txt")
provider = CryptoCompareProvider()

async def analyze_data(user_id: str, symbol: str, interval: str, limit: int = 144) -> dict:
    """
    Собирает OHLCV через CryptoCompare, формирует промпт, сохраняет снепшот (если включён)
    и отправляет промпт в ChatGPT, возвращая результат.
    """
    # 1) Получаем данные
    df = await provider.fetch_ohlcv(symbol, interval, limit)
    if df.empty:
        return {"error": "Нет данных для анализа"}

    # 2) Готовим промпт
    records = df.to_dict(orient="records")
    tpl = Template(PROMPT_PATH.read_text(encoding="utf-8"))
    prompt_str = tpl.render(ohlc_data=json.dumps(records, ensure_ascii=False))

    # 3) Сохраняем снепшот для отладки
    save_snapshot(user_id, records, prompt_str)

    # 4) Отправляем в OpenAI
    return await ask(prompt_str)
