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
        # Разбор символа
        if symbol.endswith("USDT"):
            fsym = symbol[:-4]
            tsym = "USDT"
        else:
            fsym = symbol[:-3]
            tsym = symbol[-3:]

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
            raise ValueError(f"Unsupported interval: {interval}")

        params = {
            "fsym": fsym,
            "tsym": tsym,
            "limit": limit - 1,
            "aggregate": aggregate,
            "api_key": self.api_key,
        }
        url = f"{self.BASE_URL}/{endpoint}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json().get("Data", [])

        if not data:
            logger.warning("CryptoCompare вернул пустой список Data")
            return pd.DataFrame()

        # Преобразование в DataFrame
        df = pd.DataFrame(data)
        df["Open Time"] = pd.to_datetime(df["time"], unit="s")
        df["Open"]   = df["open"]
        df["High"]   = df["high"]
        df["Low"]    = df["low"]
        df["Close"]  = df["close"]
        df["Volume"] = df["volumefrom"]
        df["Quote Asset Volume"] = df["volumeto"]

        # Возвращаем только нужные колонки
        return df[["Open Time","Open","High","Low","Close","Volume","Quote Asset Volume"]]
