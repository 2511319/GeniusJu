# models/data_models.py

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel

class OhlcRecord(BaseModel):
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class HistoryEntry(BaseModel):
    timestamp: datetime
    symbol: str
    interval: str
    result: Dict[str, Any]
