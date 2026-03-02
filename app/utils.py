from __future__ import annotations
from datetime import datetime
import logging
from typing import Optional

log = logging.getLogger("orders_case")

def parse_dt(s: str) -> Optional[datetime]:
    if not s:
        return None
    # Accept ISO + a common dd/mm/YYYY HH:MM format
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None
