"""
Zależności FastAPI (dependency injection)
"""

import logging
from functools import lru_cache


@lru_cache()
def get_logger(name: str) -> logging.Logger:
    """Zwraca logger dla danego modułu"""
    return logging.getLogger(name)

