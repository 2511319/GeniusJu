# services/crypto_compare_provider.py

import os
import httpx
import pandas as pd
from config import logger

class CryptoCompareProvider:
    BASE_URL = "https://min-api.cryptocompare.com/data"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("CRYPTOCOMPARE_API_KEY")
        if not self.api_key:
            logger.error("CRYPTOCOMPARE_API_KEY не установлен")
            raise ValueError("CRYPTOCOMPARE_API_KEY не установлен")

    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """
        Загружает OHLCV данные из CryptoCompare.
        `symbol` — строка вида 'BTCUSDT' или 'BTCUSD'.
        `interval` — '1m', '15m', '1h', '4h', '1d' и т.д.
        `limit` — количество свечей.
        """
        logger.info(f"fetch_ohlcv called with symbol: {symbol}, interval: {interval}, limit: {limit}")
        try:
            # Разбор символа
            if symbol.endswith("USDT"):
                fsym = symbol[:-4]
                tsym = "USDT"
            else:
                fsym = symbol[:-3]
                tsym = symbol[-3:]
            logger.debug(f"Parsed symbol: fsym={fsym}, tsym={tsym}")

            # Выбираем endpoint
            unit = interval[-1]
            value = int(interval[:-1])
            if unit == "m":
                endpoint = "histominute"
                aggregate = value
            elif unit == "h":
                endpoint = "histohour"
                aggregate = value
            elif unit == "d":
                endpoint = "histoday"
                aggregate = value
            else:
                logger.error(f"Unsupported interval: {interval}")
                raise ValueError(f"Unsupported interval: {interval}")
            logger.debug(f"Selected endpoint: {endpoint}, aggregate: {aggregate}")

            params = {
                "fsym": fsym,
                "tsym": tsym,
                "limit": limit - 1, # CryptoCompare API returns 'limit + 1' data points
                "aggregate": aggregate,
                # "api_key": self.api_key, # Removed for logging url
            }
            url = f"{self.BASE_URL}/{endpoint}"
            logger.info(f"Requesting URL: {url} with params: {params}")
            params["api_key"] = self.api_key # Add api_key back for actual request

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params)
                logger.info(f"CryptoCompare API response status code: {resp.status_code}")
                resp.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
                response_json = resp.json()

            data = response_json.get("Data", {}).get("Data", []) # Adjusted to new response structure
            
            if not data:
                logger.warning(f"CryptoCompare returned no data in 'Data.Data'. Full response: {response_json}")
                return pd.DataFrame()
            
            logger.info(f"Received {len(data)} records from CryptoCompare. First record: {data[0] if data else 'N/A'}")

            # Преобразование в DataFrame
            df = pd.DataFrame(data)
            df["Open Time"] = pd.to_datetime(df["time"], unit="s")
            df["Open"]   = df["open"]
            df["High"]   = df["high"]
            df["Low"]    = df["low"]
            df["Close"]  = df["close"]
            df["Volume"] = df["volumefrom"]
            df["Quote Asset Volume"] = df["volumeto"] # volumeto is the quote asset volume

            # Возвращаем только нужные колонки
            result_df = df[["Open Time","Open","High","Low","Close","Volume","Quote Asset Volume"]]
            logger.info(f"Returning DataFrame with {len(result_df)} rows. Columns: {result_df.columns.tolist()}")
            return result_df
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.request.url} - {e.response.status_code} - {e.response.text}", exc_info=True)
            return pd.DataFrame() # Return empty DataFrame on HTTP error
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while requesting {e.request.url!r}: {e}", exc_info=True)
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"An unexpected error occurred in fetch_ohlcv: {e}", exc_info=True)
            return pd.DataFrame()
