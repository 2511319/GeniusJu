# services/analysis_service.py

import json
import pandas as pd
from pathlib import Path
from jinja2 import Template, Environment, select_autoescape
from services.crypto_compare_provider import CryptoCompareProvider
from services.openai_client     import ask
from services.snapshot_manager  import save_snapshot
from config import logger
from .technical_indicators import calculate_all_indicators

PROMPT_PATH = Path("prompt.txt")
provider = CryptoCompareProvider()

# Setup Jinja2 environment
jinja_env = Environment(
    loader=Path(__file__).parent.parent, # Assuming prompt.txt is in the root
    autoescape=select_autoescape(['html', 'xml', 'jinja'])
)

def to_json_custom(value, indent=None, default_handler=str):
    """Custom Jinja2 filter for to_json to handle NaNs and other non-serializable types."""
    if isinstance(value, pd.DataFrame):
        # Handle NaN/NaT by converting to None (null in JSON) or string representations
        # Convert NaT to string 'NaT' or None
        df_prepared = value.astype(object).where(pd.notnull(value), None) 
        # If there are still issues, consider df_prepared = value.fillna('N/A')
        # or more specific handlers for dates/times if needed
        records = df_prepared.to_dict(orient='records')
        return json.dumps(records, indent=indent, default=default_handler, ensure_ascii=False)
    return json.dumps(value, indent=indent, default=default_handler, ensure_ascii=False)

jinja_env.filters['tojson'] = to_json_custom


async def analyze_data(user_id: str, symbol: str, interval: str, limit: int = 144, indicator_params: dict = None) -> dict:
    """
    Собирает OHLCV через CryptoCompare, рассчитывает индикаторы, формирует промпт, 
    сохраняет снепшот (если включён) и отправляет промпт в ChatGPT, возвращая результат.
    """
    logger.info(f"analyze_data called with user_id: {user_id}, symbol: {symbol}, interval: {interval}, limit: {limit}, indicator_params: {indicator_params}")
    try:
        # 1) Получаем данные OHLCV
        logger.info(f"Fetching OHLCV data for symbol: {symbol}, interval: {interval}, limit: {limit}")
        df_ohlcv = await provider.fetch_ohlcv(symbol, interval, limit)
        if df_ohlcv.empty:
            logger.warning("No data received from provider.fetch_ohlcv")
            return {"error": "Нет данных для анализа (OHLCV)"}
        logger.info(f"Received {len(df_ohlcv)} OHLCV rows from provider.fetch_ohlcv")

        # 2) Рассчитываем индикаторы
        logger.info(f"Calculating technical indicators with params: {indicator_params}")
        df_with_indicators = calculate_all_indicators(df_ohlcv, indicator_params)
        if df_with_indicators.empty: # Could happen if TA calculation fails badly
             logger.warning("Technical indicator calculation resulted in an empty DataFrame.")
             return {"error": "Ошибка при расчете технических индикаторов."}
        logger.info(f"Calculated indicators. DataFrame shape: {df_with_indicators.shape}. Columns: {df_with_indicators.columns.tolist()}")
        
        # 3) Готовим контекст для промпта
        # Convert DataFrame to list of dicts, handling NaN/NaT
        # Using .astype(object).where(pd.notnull(df_with_indicators), None) to convert NaNs to None for JSON
        ohlc_data_for_prompt = df_with_indicators # Jinja filter will handle conversion
        
        prompt_context = {
            "ohlc_data_with_indicators": ohlc_data_for_prompt,
            "user_indicator_params": indicator_params or {} # Ensure it's a dict
        }
        
        try:
            template = jinja_env.get_template(str(PROMPT_PATH))
            prompt_str = template.render(prompt_context)
            logger.info(f"Generated prompt (first 300 chars): {prompt_str[:300]}")
        except Exception as e:
            logger.error(f"Error rendering Jinja2 template: {e}", exc_info=True)
            return {"error": "Ошибка формирования запроса для анализа (Jinja2)."}


        # 4) Сохраняем снепшот для отладки
        # For snapshot, it's better to save the dict version of ohlc_data_for_prompt
        # as it was passed to the template (after NaN handling)
        snapshot_records = df_with_indicators.astype(object).where(pd.notnull(df_with_indicators), None).to_dict(orient='records')
        logger.info(f"Saving snapshot for user_id: {user_id}")
        save_snapshot(user_id, snapshot_records, prompt_str) # Pass the records used for prompt

        # 5) Отправляем в OpenAI
        logger.info("Sending prompt to OpenAI")
        analysis_results_str = await ask(prompt_str) # ask expects a string
        logger.info(f"Received response from OpenAI (first 200 chars): {analysis_results_str[:200]}")

        try:
            analysis_results = json.loads(analysis_results_str)
            logger.info(f"Successfully parsed JSON response from OpenAI.")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response from OpenAI: {e}", exc_info=True)
            logger.error(f"Problematic JSON string (first 500 chars): {analysis_results_str[:500]}")
            return {"error": f"Ошибка парсинга ответа от OpenAI: {e}"}

        logger.info(f"analyze_data returning successfully.")
        return analysis_results
    except Exception as e:
        logger.error(f"Exception in analyze_data: {e}", exc_info=True)
        return {"error": f"Внутренняя ошибка в сервисе анализа: {e}"}
