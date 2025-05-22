# services/openai_client.py

import os
import json
import openai
import logging
from config import config

logger = logging.getLogger(__name__)

# Настраиваем API-ключ и модель
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = config.get("openai", "model", "gpt-4o-mini")

async def ask(prompt: str) -> dict:
    """
    Отправляет prompt в OpenAI ChatCompletion и пытается вернуть распарсенный JSON.
    В случае ошибки парсинга вернёт {'error': ..., 'raw': <строка ответа>}.
    """
    if not openai.api_key:
        logger.error("OPENAI_API_KEY не установлен")
        raise ValueError("OPENAI_API_KEY не установлен")

    try:
        response = await openai.ChatCompletion.acreate(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an experienced trader and top-tier expert."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.1,
            max_tokens=15000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.1,
        )
        content = response.choices[0].message.content.strip()
        logger.info("Ответ от OpenAI получен, пытаемся распарсить JSON")

        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Не удалось распарсить JSON: {e}")
            return {"error": "Invalid JSON from OpenAI", "raw": content}

    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return {"error": str(e)}
